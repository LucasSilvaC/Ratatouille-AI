"""
Montador por ingredientes (sem receitas): monta as combinações de cada refeição do cronograma.

Para cada refeição, cada combinação tem um alimento de cada grupo:
    almoço e jantar       : proteína + carboidrato + leguminosa (feijão) + legumes + fruta
    café da manhã, lanche : carboidrato + proteína + fruta
(O feijão tem grupo próprio no almoço e no jantar porque é assim que se come no Brasil: arroz E feijão E a
carne. Com o feijão no lugar da carne, o prato não chega à energia da refeição. Para tirar, é só remover
"leguminosa" de GRUPOS_REFEICAO.)
Os alimentos vêm da despensa (dados/despensa.csv). Em cada grupo, metade são os mais comidos naquela refeição e
região na POF 2017–2018 (camada "nucleo", com a porção típica de quem come aquilo) e metade é sorteada entre o
resto do núcleo e a camada "diversidade" (pratos e alimentos que a POF quase não registra: homus, falafel,
tofu...). Os nutrientes são os da TBCA.

AS GRAMAS BATEM AS METAS DA DRI E RESPEITAM AS RESTRIÇÕES DO PRATO. Cada alimento começa na porção típica
da POF multiplicada pela ESCALA da pessoa (energia do dia / 2.000 kcal, entre 0,75 e 1,6). Depois:
  * frutas e legumes: se o prato tiver menos que a parte da refeição nos 400 g/dia da OMS (400 g × fração
    da refeição), essas porções crescem até atingir o mínimo (no máximo 1,75 vez);
  * proteína e carboidrato são multiplicados por fatores f_p e f_c (entre 0,5 e 1,75). A energia tem de
    ser exatamente a meta, e isso amarra f_p a f_c (uma reta). Cada restrição deixa só um intervalo de f_c:
      - f_p e f_c entre 0,5 e 1,75;
      - proteína entre o mínimo da DRI (o maior entre 0,8 g/kg e 10% da energia, na parte da refeição) e
        35% da energia. A META de proteína (15% da energia) não é obrigatória aqui: ela entra na nota do
        Avaliador;
      - carboidrato entre 45% e 65% da energia;
      - gordura entre 20% e 35% da energia (faixas AMDR da DRI, aplicadas a cada refeição);
      - sódio até 1,25 × o limite da refeição (o mesmo limite da trava do Avaliador);
    Dentro do intervalo que sobra, f_c é escolhido para deixar f_p o mais perto possível de 1 (a proteína
    muda o mínimo possível). Se o intervalo é vazio, a combinação não serve e sai da lista.
As gramas são arredondadas de 5 em 5, e o prato é conferido de novo depois do arredondamento.
Se sobrarem menos de 20 combinações, o Montador relaxa em dois níveis e avisa no log: primeiro tira as faixas de
macronutrientes; se ainda nada couber, mantém só os limites das porções (a energia pode não fechar, e o
Avaliador ainda veta pelo sódio).
Restrições e "não gosta" da pessoa (vetar_item) são aplicados antes, para as contas valerem só para o que a
pessoa pode comer.

O Montador não escolhe nada: entrega TODAS as combinações com gramas e nutrientes. Quem veta, dá nota e
escolhe as 3 opções é o Avaliador (avaliador.py). A notação e a dedução das equações estão no README do pacote.
"""
from __future__ import annotations

import itertools
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

from .restricoes import tipos_do_alimento

ARQ_DESPENSA = Path(__file__).resolve().parent / "dados" / "despensa.csv"

GRUPOS_REFEICAO = {
    "cafe_da_manha": ["carboidrato", "proteina", "fruta"],
    "almoco": ["proteina", "carboidrato", "leguminosa", "legumes", "fruta"],
    "lanche": ["carboidrato", "proteina", "fruta"],
    "jantar": ["proteina", "carboidrato", "leguminosa", "legumes", "fruta"],
}
TOP_POR_GRUPO = {"leguminosa": 3}          # itens por grupo em cada refeição; os outros grupos usam top_por_grupo
# desses itens, quantos são os mais comidos (fixos); o resto é sorteado da cauda do núcleo e da diversidade
POPULARES = {"leguminosa": 2}              # os outros grupos usam metade de top_por_grupo
NOMES_REFEICAO = {"cafe_da_manha": "Café da manhã", "almoco": "Almoço", "lanche": "Lanche", "jantar": "Jantar"}
FATOR_MIN, FATOR_MAX = 0.5, 1.75
KCAL_REFERENCIA = 2000                     # as porções típicas da POF são de um adulto médio
ESCALA_MIN, ESCALA_MAX = 0.75, 1.6
NUTRIENTES = ["energia_kcal", "proteina_g", "carboidrato_total_g", "lipidios_g", "fibra_g", "sodio_mg"]
# faixas aceitáveis de macronutrientes (AMDR da DRI), em fração da energia, e kcal por grama
FAIXAS_MACRO = {"proteina_g": (0.10, 0.35, 4), "carboidrato_total_g": (0.45, 0.65, 4), "lipidios_g": (0.20, 0.35, 9)}
FLV_DIA_G = 400                            # OMS: pelo menos 400 g de frutas e hortaliças por dia
GRUPOS_FLV = ("legumes", "fruta")
TOLERANCIA = 0.02                          # folga ao conferir um prato pronto (arredondamento de 5 g, trocas)
SODIO_VETO = 1.25                          # sódio até 1,25 × o limite da refeição (o Avaliador usa o mesmo)
MIN_COMBINACOES = 20                       # com menos que isso, o Montador relaxa um nível

# subtipos: o que a pessoa pode gostar ou não (são as características que o bandit do Avaliador aprende)
SUBTIPOS = {
    "proteina": [("leguminosa", r"^feijao|lentilha|grao.de.bico|ervilha|(?<!oleo de )(?<!oleo )soja"),
                 ("aves", r"frango|galinha|peru"),
                 ("boi", r"\bboi\b|bovin|carne seca|charque|bife"), ("porco", r"porco|suin|pernil|lombo"),
                 ("peixe", r"peixe|sardinha|atum|camarao|pescad|tilapia|merluza"), ("ovo", r"^ovo"),
                 ("embutido", r"linguica|salsicha|presunto|mortadela|calabresa|salame"),
                 ("leite", r"^leite|bebida lactea|bebida vegetal"), ("queijo", r"queijo|requeijao"),
                 ("iogurte", r"iogurte|coalhada")],
    "carboidrato": [("arroz", r"^arroz"), ("massa", r"macarrao|massa"),
                    ("raiz", r"mandioca|aipim|macaxeira|inhame|cara\b|tapioca|farofa|beiju"),
                    ("batata", r"^batata"), ("pao", r"^pao|torrada|biscoito|bolo"),
                    ("milho", r"milho|cuscuz|polenta|fuba|pipoca"), ("aveia", r"aveia|granola|cereais")],
    "leguminosa": [("carioca", r"carioca"), ("preto", r"preto"), ("fradinho", r"fradinho|corda|macassar")],
    "legumes": [("folha_crua", r"alface|rucula|agriao|couve, crua|repolho, cru|acelga|chicoria"),
                ("cru", r"crua?\b|crua?,"), ("cozido", r"cozid|vapor|refogad|assad|drenad")],
    "fruta": [("banana", r"^banana"), ("citrica", r"laranja|tangerina|mexerica|limao|abacaxi|acerola|ponka"),
              ("tropical", r"mamao|manga|melao|melancia|acai|goiaba|caju"), ("temperada", r"^maca|^pera|^uva|morango")],
}


# o que NÃO é um item do prato: sucos, doces, farinhas e amidos crus, molhos, pastas e temperos
FORA_DO_PRATO = re.compile(
    r"^suco|nectar|refresco|doce|compota|calda|geleia|cristalizad|desidratad|"
    r"^farinha, (trigo|milho)|^amido|^fecula|^polvilho|^fermento|cru(a)?, |\bcrua?$|in natura, cru|"
    r"^tempero|^molho|shoyu|^misso|^pasta|^extrato|^caldo|^creme de leite|^leite condensado|^manteiga|^margarina")
# cru vale para salada e fruta
CRU_OK = re.compile(r"^(alface|tomate|pepino|cenoura|repolho|rucula|agriao|cebola|pimentao|beterraba|"
                    r"couve|acelga|chicoria|almeirao|banana|maca|mamao|laranja|tangerina|manga|uva|pera|"
                    r"abacaxi|melancia|melao|goiaba|abacate|kiwi|morango|caju|acerola|ameixa|pessego|"
                    r"caqui|carambola|pitanga|jabuticaba|graviola|pinha|cupuacu|maracuja|limao|mexerica|acai|"
                    r"nabo|berinjela|abobrinha|cereja|abiu)")


def serve_no_prato(descricao):
    """Alimento que pode ser um item do prato (fruta e salada cruas valem; farinha crua e molho não)."""
    n = sem_acento(descricao)
    if CRU_OK.match(n):
        return not re.search(r"suco|doce|compota|calda|geleia|cristalizad|desidratad|frit", n)
    return not FORA_DO_PRATO.search(n)


def proteina_minima(metas):
    """Mínimo de proteína da refeição pela DRI. Metas antigas (sem proteina_g_min) usam a meta."""
    return metas.get("proteina_g_min", metas["proteina_g"])


def sem_acento(t):
    return "".join(c for c in unicodedata.normalize("NFKD", str(t).lower()) if not unicodedata.combining(c))


# subtipos conferidos antes dos outros ("Ovo, galinha" é ovo, não ave). A ORDEM de SUBTIPOS não muda: ela é a
# ordem das características do bandit, e mudá-la embaralharia o que já foi aprendido e salvo.
PRIMEIRO = {"proteina": ["ovo"]}


def subtipo(grupo, descricao):
    n = sem_acento(descricao)
    lista = SUBTIPOS.get(grupo, [])
    lista = sorted(lista, key=lambda st: st[0] not in PRIMEIRO.get(grupo, []))
    for nome, rx in lista:
        if re.search(rx, n):
            return nome
    return "outro"


class MontadorIngredientes:
    def __init__(self, despensa: pd.DataFrame | None = None, regiao: str = "Brasil", top_por_grupo: int = 8):
        d = despensa if despensa is not None else pd.read_csv(
            ARQ_DESPENSA, dtype={"nutriscore": str, "id_base": str}).fillna({"nutriscore": "", "id_base": ""})
        if regiao not in set(d.regiao):
            regiao = "Brasil"                                   # região desconhecida: usa o Brasil inteiro
        self.regiao, self.top_por_grupo = regiao, top_por_grupo
        camada = d.camada if "camada" in d else pd.Series("nucleo", index=d.index)
        # núcleo da região, do mais comido ao menos comido
        self.d = d[(camada == "nucleo") & (d.regiao == regiao)].sort_values("rank").copy()
        # diversidade (Brasil): vem junto ou, se a despensa veio da API só com o núcleo, do arquivo local
        div = d[camada == "diversidade"]
        if div.empty and ARQ_DESPENSA.exists():
            local = pd.read_csv(ARQ_DESPENSA, dtype={"nutriscore": str, "id_base": str}) \
                .fillna({"nutriscore": "", "id_base": ""})
            div = local[local.camada == "diversidade"] if "camada" in local else local.iloc[:0]
        self.diversidade = div[[c for c in self.d.columns if c in div.columns]].copy()
        for t in (self.d, self.diversidade):
            t["subtipo"] = [subtipo(g, n) for g, n in zip(t.grupo, t.descricao)]
        self.log: list[str] = []

    def _n(self, grupo):
        """(itens por grupo, quantos são populares)."""
        total = TOP_POR_GRUPO.get(grupo, self.top_por_grupo)
        return total, POPULARES.get(grupo, total // 2)

    def itens(self, refeicao, grupo, vetar_item=None, rng=None):
        """Os alimentos do grupo que o Montador combina nesta refeição.

        1. Tira o que a pessoa não pode (vetar_item), da lista INTEIRA, antes de escolher: os vetados são
           repostos pelos seguintes, e o grupo continua cheio.
        2. Sem rng: os mais comidos da região (como antes).
           Com rng: os POPULARES mais comidos (fixos) e o resto SORTEADO entre a cauda do núcleo e a camada de
           diversidade (homus, falafel, tofu...), por subtipo: passa pelos subtipos (aves, peixe, leguminosa...)
           em ordem sorteada, um alimento de cada, para os sorteados cobrirem tipos diferentes.
           Coluna novidade = sorteado.
        Se as regras esvaziam o grupo, devolve os mais comidos sem filtro: o Avaliador veta e explica."""
        total, n_pop = self._n(grupo)
        nucleo = self.d[(self.d.refeicao == refeicao) & (self.d.grupo == grupo)]
        if vetar_item is not None:
            ok = nucleo[[not vetar_item(r) for _, r in nucleo.iterrows()]]
            if ok.empty:
                return nucleo.head(total).assign(novidade=False).reset_index(drop=True)
            nucleo = ok
        if rng is None:
            return nucleo.head(total).assign(novidade=False).reset_index(drop=True)
        populares = nucleo.head(n_pop)
        div = self.diversidade[(self.diversidade.refeicao == refeicao) & (self.diversidade.grupo == grupo)]
        if vetar_item is not None and len(div):
            div = div[[not vetar_item(r) for _, r in div.iterrows()]]
        resto = pd.concat([nucleo.iloc[n_pop:], div]).drop_duplicates("codigo")
        resto = resto[~resto.codigo.isin(populares.codigo)].reset_index(drop=True)
        livre = np.ones(len(resto), bool)
        sorteados, fila = [], []
        while len(sorteados) < total - n_pop and livre.any():
            if not fila:            # uma rodada por todos os subtipos que restam, em ordem sorteada
                fila = list(rng.permutation(sorted(resto.subtipo[livre].unique())))
            st = fila.pop()                                              # primeiro o subtipo...
            cand = np.flatnonzero(livre & (resto.subtipo == st).to_numpy())
            if not len(cand):
                continue
            k = int(cand[rng.integers(len(cand))])                       # ...depois um alimento dele
            sorteados.append(k)
            livre[k] = False
        t = pd.concat([populares.assign(novidade=False), resto.iloc[sorteados].assign(novidade=True)])
        return t.reset_index(drop=True)

    # ---------------------------------------------------------------- combinações com gramas ajustadas
    def combinacoes(self, refeicao: str, metas: dict, vetar_item=None, nao_misturar=(), semente=None) -> pd.DataFrame:
        """metas: as da refeição vindas da calculadora DRI (energia_kcal, proteina_g, fibra_g, sodio_mg_max...).
        vetar_item: função (linha da despensa) -> motivo ou None, com as restrições e o "não gosta" da pessoa
        (o Cronograma passa a do Avaliador). Os alimentos vetados saem ANTES das contas, para que as
        restrições do prato sejam aplicadas só ao que a pessoa pode comer.
        nao_misturar: pares de tipos (TIPOS de restricoes.py, ex. ("carne", "laticinio")) que não podem estar no
        mesmo prato; as combinações que juntam um par saem antes das contas.
        semente: com um número, cada grupo leva os mais comidos e alguns alimentos sorteados (itens); a mesma
        semente dá os mesmos sorteados (o Cronograma usa pessoa, data e refeição).
        Devolve uma linha por combinação, com as gramas de cada item e os totais de nutrientes."""
        grupos = GRUPOS_REFEICAO[refeicao]
        rng = np.random.default_rng(semente) if semente is not None else None
        tabelas = [self.itens(refeicao, g, vetar_item, rng) for g in grupos]
        if any(t.empty for t in tabelas):
            raise ValueError(f"despensa sem itens para {refeicao} em {self.regiao}")
        idx = np.array(list(itertools.product(*[range(len(t)) for t in tabelas])))      # (n, grupos)
        codigos = np.column_stack([t.codigo.to_numpy()[idx[:, k]] for k, t in enumerate(tabelas)])
        distintos = np.array([len(set(c)) == len(c) for c in codigos])   # o mesmo alimento em 2 grupos: fora
        idx = idx[distintos]
        n_misturar = 0
        if nao_misturar:                                 # pares proibidos no mesmo prato (ex.: carne e laticínio)
            tipos = [[tipos_do_alimento(sem_acento(r["descricao"]), r) for _, r in t.iterrows()] for t in tabelas]
            junta = np.zeros(len(idx), bool)
            for u, w in nao_misturar:
                tem = {x: np.zeros(len(idx), bool) for x in (u, w)}
                for k, tk in enumerate(tipos):
                    for x in (u, w):
                        tem[x] |= np.array([x in s_ for s_ in tk], bool)[idx[:, k]]
                junta |= tem[u] & tem[w]
            n_misturar, idx = int(junta.sum()), idx[~junta]
            if not len(idx):
                raise ValueError(f"nenhuma combinação para {refeicao} sem juntar {list(nao_misturar)}")
        escala = float(np.clip(metas["energia_kcal"] / (metas.get("fracao", 0.3) * KCAL_REFERENCIA),
                               ESCALA_MIN, ESCALA_MAX))
        porcao = escala * np.column_stack([t.porcao_g.to_numpy()[idx[:, k]] for k, t in enumerate(tabelas)])
        por100 = {c: np.column_stack([t[c].to_numpy()[idx[:, k]] for k, t in enumerate(tabelas)]) / 100
                  for c in NUTRIENTES}

        n_total = len(idx)
        ip, ic = grupos.index("proteina"), grupos.index("carboidrato")
        fixos = [k for k in range(len(grupos)) if k not in (ip, ic)]
        # frutas e legumes: no mínimo a parte da refeição nos 400 g/dia da OMS
        iflv = [k for k, g in enumerate(grupos) if g in GRUPOS_FLV]
        f_v = np.ones(n_total)
        if iflv:
            g_flv = porcao[:, iflv].sum(1)
            f_v = np.maximum(1, FLV_DIA_G * metas.get("fracao", 0.3) / np.maximum(g_flv, 1e-6))
            porcao[:, iflv] *= np.minimum(f_v, FATOR_MAX)[:, None]
        ok_flv = f_v <= FATOR_MAX + 1e-9

        # nível 1: todas as restrições; 2: sem as faixas de macronutrientes (o resto vale);
        # 3: só os limites dos fatores
        nivel = 0
        for nivel, macros in ((1, True), (2, False)):
            lo, hi, alvo = self._intervalo_fc(grupos, porcao, por100, metas, macros=macros)
            viavel = ok_flv & (lo <= hi)
            if viavel.sum() >= min(MIN_COMBINACOES, n_total):
                break
        else:
            nivel = 3
            lo, hi = np.full(n_total, FATOR_MIN), np.full(n_total, FATOR_MAX)
            viavel = np.ones(n_total, bool)
        fc = np.clip(alvo, lo, hi)                       # f_p o mais perto possível de 1
        kcal = por100["energia_kcal"] * porcao
        resto = metas["energia_kcal"] - kcal[:, fixos].sum(1)
        fp = (resto - fc * kcal[:, ic]) / np.maximum(kcal[:, ip], 1e-6)
        if nivel == 3:
            fp = np.clip(fp, FATOR_MIN, FATOR_MAX)      # aqui a energia pode não fechar
        fator = np.ones_like(porcao)
        fator[:, ip], fator[:, ic] = fp, fc
        gramas = np.maximum(np.round(porcao * fator / 5) * 5, 5)

        descartadas = {"nao_misturar": n_misturar,
                       "frutas_e_legumes": int((~ok_flv).sum()) if nivel < 3 else 0,
                       "faixas": int((ok_flv & ~(lo <= hi)).sum()) if nivel < 3 else 0}
        idx, gramas = idx[viavel], gramas[viavel]
        por100 = {c: v[viavel] for c, v in por100.items()}
        # confere de novo depois do arredondamento de 5 g (em porções pequenas ele pode tirar o prato da faixa)
        passa = np.ones(len(idx), bool)
        if nivel < 3:
            tot = {c: (por100[c] * gramas).sum(1) for c in NUTRIENTES}
            g_flv = gramas[:, iflv].sum(1) if iflv else None
            passa = self._respeita(tot, g_flv, metas, macros=(nivel == 1))
            if not passa.any():                          # o arredondamento derrubou todas: mantém
                passa[:] = True
        descartadas["arredondamento"] = int((~passa).sum())
        idx, gramas = idx[passa], gramas[passa]
        por100 = {c: v[passa] for c, v in por100.items()}
        totais = {c: (por100[c] * gramas).sum(1) for c in NUTRIENTES}
        registros = [t.to_dict("records") for t in tabelas]
        linhas = []
        for n, combo in enumerate(idx):
            itens = []
            for k, g in enumerate(grupos):
                r = registros[k][combo[k]]
                itens.append({"grupo": g, "codigo": r["codigo"], "alimento": r["descricao"],
                              "gramas": float(gramas[n, k]), "porcao_tipica_g": float(r["porcao_g"]),
                              "subtipo": r["subtipo"], "id_base": r["id_base"],
                              "novidade": bool(r.get("novidade", False))})
            linhas.append(itens)
        df = pd.DataFrame({"itens": linhas})
        for c in NUTRIENTES:
            df[c] = totais[c].round(1)
        df["desvio_energia"] = (df.energia_kcal / metas["energia_kcal"] - 1).round(3)
        df["codigos"] = [frozenset(i["codigo"] for i in it) for it in linhas]
        df["codigos_ordem"] = [tuple(i["codigo"] for i in it) for it in linhas]
        # tabela dos itens desta refeição (um por alimento): o Avaliador usa para a trava
        df.attrs["itens"] = pd.concat(tabelas).drop_duplicates("codigo").set_index("codigo")
        # atributos por item que o Avaliador usa (trava e qualidade)
        for col in [c for c in self.d.columns if c.startswith(("alergeno_", "dieta_"))] + ["nova"]:
            df[col] = list(np.column_stack([t[col].to_numpy()[idx[:, k]] for k, t in enumerate(tabelas)]))
        df["nutriscore"] = list(np.column_stack([t.nutriscore.to_numpy()[idx[:, k]] for k, t in enumerate(tabelas)]))
        df.attrs["escala"] = round(escala, 2)
        df.attrs["descartadas"] = descartadas
        df.attrs["nivel_restricoes"] = nivel
        aviso = {2: " — AVISO: poucas cabiam nas faixas de macronutrientes; faixas relaxadas",
                 3: " — AVISO: poucas fechavam a energia com proteína e sódio; só os limites das porções valem"}
        self.log.append(f"{refeicao}: {len(df)} de {n_total} combinações respeitam as restrições "
                        f"({' × '.join(str(len(t)) for t in tabelas)}), porções × {escala:.2f}"
                        + aviso.get(nivel, ""))
        return df

    @staticmethod
    def _intervalo_fc(grupos, porcao, por100, metas, macros=True):
        """Intervalo [lo, hi] de f_c em que todas as restrições valem, com a energia exatamente na meta.
        Com energia fixa, f_p = (resto − f_c·e_c) / e_p; então cada nutriente do prato é a + b·f_c, e cada
        faixa [L, U] vira um intervalo de f_c. Devolve também o f_c que deixaria f_p = 1."""
        ip, ic = grupos.index("proteina"), grupos.index("carboidrato")
        fixos = [k for k in range(len(grupos)) if k not in (ip, ic)]
        eps = 1e-6
        E = metas["energia_kcal"]
        kcal = por100["energia_kcal"] * porcao
        e_p, e_c = np.maximum(kcal[:, ip], eps), np.maximum(kcal[:, ic], eps)
        resto = E - kcal[:, fixos].sum(1)
        n = len(resto)
        lo = np.full(n, FATOR_MIN)
        hi = np.full(n, FATOR_MAX)
        lo = np.maximum(lo, (resto - FATOR_MAX * e_p) / e_c)          # f_p <= 1,75
        hi = np.minimum(hi, (resto - FATOR_MIN * e_p) / e_c)          # f_p >= 0,5
        p_min = proteina_minima(metas)
        faixas = {"proteina_g": (p_min, np.inf)}
        if "sodio_mg_max" in metas:
            faixas["sodio_mg"] = (-np.inf, SODIO_VETO * metas["sodio_mg_max"])
        if macros:
            faixas.update({c: (mn * E / kc, mx * E / kc) for c, (mn, mx, kc) in FAIXAS_MACRO.items()})
            faixas["proteina_g"] = (max(p_min, faixas["proteina_g"][0]), faixas["proteina_g"][1])
        for c, (L, U) in faixas.items():
            nut = por100[c] * porcao
            a = nut[:, fixos].sum(1) + nut[:, ip] * resto / e_p
            b = nut[:, ic] - nut[:, ip] * e_c / e_p
            with np.errstate(divide="ignore", invalid="ignore"):
                b_seguro = np.where(b == 0, 1, b)
                l1 = np.where(b > 0, (L - a) / b_seguro, np.where(b < 0, (U - a) / b_seguro, -np.inf))
                h1 = np.where(b > 0, (U - a) / b_seguro, np.where(b < 0, (L - a) / b_seguro, np.inf))
            fora = (b == 0) & ((a < L) | (a > U))
            lo, hi = np.maximum(lo, l1), np.minimum(hi, h1)
            hi = np.where(fora, -np.inf, hi)
        return lo, hi, (resto - e_p) / e_c

    @staticmethod
    def _respeita(tot, g_flv, metas, macros=True):
        """Quais pratos prontos respeitam as restrições (com folga de 2% por causa do arredondamento)."""
        E = np.maximum(tot["energia_kcal"], 1e-6)
        ok = tot["proteina_g"] >= (1 - TOLERANCIA) * proteina_minima(metas)
        if macros:
            for c, (mn, mx, kc) in FAIXAS_MACRO.items():
                frac = kc * tot[c] / E
                ok &= (frac >= mn - TOLERANCIA) & (frac <= mx + TOLERANCIA)
        if g_flv is not None:
            ok &= g_flv >= (1 - TOLERANCIA) * FLV_DIA_G * metas.get("fracao", 0.3) - 5
        if "sodio_mg_max" in metas:                     # sem folga: acima disso o Avaliador veta
            ok &= tot["sodio_mg"] <= SODIO_VETO * metas["sodio_mg_max"]
        return ok

    @staticmethod
    def fora_das_restricoes(linha: pd.Series, metas: dict) -> str:
        """Confere um prato pronto (ex.: depois de uma troca pelo SOM). Devolve "" se respeita as
        restrições do Montador, ou o motivo. Usa uma folga de 2% por causa do arredondamento."""
        E = float(linha["energia_kcal"]) or 1.0
        # (os totais da tabela vêm arredondados a 0,1; a folga extra de 0,05 g / 0,1% evita falso alarme)
        if float(linha["proteina_g"]) < (1 - TOLERANCIA) * proteina_minima(metas) - 0.05:
            return "proteína abaixo do mínimo da DRI"
        for c, (mn, mx, kc) in FAIXAS_MACRO.items():
            frac = kc * float(linha[c]) / E
            if frac < mn - TOLERANCIA - 0.001 or frac > mx + TOLERANCIA + 0.001:
                nome = {"proteina_g": "proteína", "carboidrato_total_g": "carboidrato", "lipidios_g": "gordura"}[c]
                return f"{nome} fora da faixa ({100 * frac:.0f}% da energia; aceito {100 * mn:.0f}–{100 * mx:.0f}%)"
        flv = sum(i["gramas"] for i in linha["itens"] if i["grupo"] in GRUPOS_FLV)
        minimo = FLV_DIA_G * metas.get("fracao", 0.3)
        if any(i["grupo"] in GRUPOS_FLV for i in linha["itens"]) and flv < (1 - TOLERANCIA) * minimo - 5:
            return f"frutas e legumes abaixo do mínimo ({flv:.0f} g; mínimo {minimo:.0f} g)"
        return ""

    # ---------------------------------------------------------------- uma combinação montada à mão (troca pelo SOM)
    @staticmethod
    def montar_linha(itens: list[dict], tabela: pd.DataFrame, metas: dict) -> pd.DataFrame:
        """Uma combinação no mesmo formato de combinacoes(), a partir de itens já com gramas.
        tabela: alimentos da TBCA indexados pelo código (nutrientes por 100 g, alérgenos, dietas, NOVA...)."""
        cods = [i["codigo"] for i in itens]
        t = tabela.loc[cods]
        g = np.array([i["gramas"] for i in itens], dtype=float)
        linha = {"itens": [itens]}
        for c in NUTRIENTES:
            linha[c] = [round(float((t[c].fillna(0).to_numpy() / 100 * g).sum()), 1)]
        df = pd.DataFrame(linha)
        df["desvio_energia"] = (df.energia_kcal / metas["energia_kcal"] - 1).round(3)
        df["codigos"] = [frozenset(cods)]
        df["codigos_ordem"] = [tuple(cods)]
        for col in [c for c in t.columns if c.startswith(("alergeno_", "dieta_"))] + ["nova", "nutriscore"]:
            df[col] = [t[col].to_numpy()]
        df.attrs["itens"] = t
        return df
