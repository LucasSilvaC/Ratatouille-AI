"""
Planejador do dia por ingredientes: junta a calculadora DRI, o Montador e o Avaliador.

    from ratatouille_recommendation import Planejador
    p = Planejador.da_entrada({
        "dados_dri": {"sexo": "F", "idade": 30, "altura_cm": 163, "peso_kg": 62, "atividade": "pouco_ativo"},
        "regiao": "Nordeste",
        "restricoes": ["sem_lactose"],
    })
    dia = p.dia()                 # metas + 3 opções para cada refeição
    p.escolher("almoco", 1)       # a pessoa escolheu a 2ª opção do almoço: o bandit aprende
    estado = p.estado()           # guardar por usuário; volta em Planejador.da_entrada(..., estado_bandit=estado)

Trocar um alimento de uma opção pelo mapa SOM (som.py):
    p.substitutos("almoco", 0, "proteina")            # alimentos parecidos com a proteína da 1ª opção
    p.trocar("almoco", 0, "proteina", "C0029F")       # troca, recalcula gramas, nutrientes e bem-estar

A entrada é o JSON descrito em dados/entrada_planejador.schema.json (o que o roteador/chatbot preenche).
Só "dados_dri" é obrigatório. Nomes de restrição fora das listas levantam EntradaInvalida; perfis fora do escopo
da calculadora (menores de 19 anos, gestantes, lactantes) levantam ForaDoEscopo.

Fluxo de cada refeição:
    calculadora DRI (metas da refeição) -> Montador (combinações seguras, gramas ajustadas às metas)
    -> Avaliador (trava, bem-estar, bandit) -> 3 opções
As restrições são aplicadas em código determinístico, antes e depois das contas; nenhum modelo de linguagem
participa dessas decisões.
"""
from __future__ import annotations

import json
import re
import zlib
from datetime import date, timedelta

import numpy as np
import pandas as pd

from .avaliador import AvaliadorIngredientes
from .dri import calcular_dri
from .montador import (ARQ_DESPENSA, GRUPOS_REFEICAO, NOMES_REFEICAO, MontadorIngredientes, sem_acento,
                       serve_no_prato, subtipo)

ROTULO_GRUPO = {"proteina": "Proteína", "carboidrato": "Carboidrato", "leguminosa": "Leguminosa", "legumes": "Legumes",
                "fruta": "Fruta"}
GENERICOS = {"carne", "peixe", "pao", "farinha", "biscoito", "queijo", "leite", "iogurte", "bebida", "oleo"}
CAMPOS_ENTRADA = {"nome", "dados_dri", "regiao", "restricoes", "nao_misturar", "nao_gosta", "avisos"}


def metas_do_perfil(dados_dri: dict) -> dict:
    """Metas do dia e de cada refeição pela calculadora DRI (EER 2023 ou Anjos)."""
    return calcular_dri(dados_dri["sexo"], float(dados_dri["idade"]), float(dados_dri["altura_cm"]),
                        float(dados_dri["peso_kg"]), dados_dri["atividade"],
                        gestante=bool(dados_dri.get("gestante")), amamentando=bool(dados_dri.get("amamentando")),
                        metodo=dados_dri.get("metodo") or "eer2023")


class Planejador:
    def __init__(self, dados_dri: dict, restricoes=(), nao_gosta=(), regiao: str = "Brasil",
                 nao_misturar=(), avisos=(), estado_bandit: dict | None = None, despensa: pd.DataFrame | None = None,
                 data: date | None = None, variar: bool = True, chave_pessoa: str | None = None):
        """restricoes  : nomes de RESTRICAO (restricoes.py), ex. ["sem_porco", "sem_frutos_do_mar"]
        nao_misturar : pares de TIPOS que não vão no mesmo prato, ex. [["carne", "laticinio"]]
        nao_gosta    : alimentos recusados (palavras do nome)
        avisos       : o que o roteador não conseguiu traduzir em regra; só é devolvido, não é usado
        variar       : em cada refeição o Montador usa os mais comidos e alguns alimentos sorteados. O sorteio
                       depende da pessoa (chave_pessoa), da data e da refeição: o mesmo dia dá as mesmas
                       opções; outro dia (novo_dia) traz outros. variar=False: só os mais comidos.
        chave_pessoa : identificador estável da pessoa para o sorteio (o ID do usuário); sem ele, usa o perfil."""
        self.avaliador = AvaliadorIngredientes(restricoes, nao_gosta, nao_misturar=nao_misturar)
        self.avisos = [str(a) for a in avisos]
        self.metas = metas_do_perfil(dados_dri)
        self.montador = MontadorIngredientes(despensa, regiao=regiao)
        self.avaliador.carregar(estado_bandit)
        self.data = data or date.today()
        self.variar = variar
        self.chave_pessoa = chave_pessoa or json.dumps(dados_dri, sort_keys=True, default=str)
        self._combinacoes: dict = {}
        self.mostradas: dict = {}
        self._som = None

    @classmethod
    def da_entrada(cls, entrada: dict, **kwargs) -> "Planejador":
        """Monta o planejador a partir do JSON de entrada (dados/entrada_planejador.schema.json)."""
        desconhecidos = set(entrada) - CAMPOS_ENTRADA
        if desconhecidos:
            raise ValueError(f"campos desconhecidos na entrada: {', '.join(sorted(desconhecidos))}")
        if "dados_dri" not in entrada:
            raise ValueError("a entrada precisa de dados_dri")
        return cls(entrada["dados_dri"], restricoes=entrada.get("restricoes", []),
                   nao_gosta=entrada.get("nao_gosta", []), regiao=entrada.get("regiao") or "Brasil",
                   nao_misturar=entrada.get("nao_misturar", []), avisos=entrada.get("avisos", []), **kwargs)

    @property
    def refeicoes(self):
        return [r for r in GRUPOS_REFEICAO if r in self.metas["refeicoes"]]

    def semente(self, refeicao: str) -> int | None:
        """Semente do sorteio de alimentos: pessoa + data + refeição (None se variar=False)."""
        if not self.variar:
            return None
        return zlib.crc32(f"{self.chave_pessoa}|{self.data.isoformat()}|{refeicao}".encode())

    def novo_dia(self, data: date | None = None):
        """Passa para o dia seguinte (ou para a data dada): novos alimentos sorteados; o aprendizado continua."""
        self.data = data or self.data + timedelta(days=1)
        self._combinacoes, self.mostradas = {}, {}

    def opcoes(self, refeicao: str, politica: str = "bandit") -> dict:
        """As 3 opções de uma refeição. politica: "bandit" (padrão), "fixa" (só bem-estar) ou "aleatoria"."""
        if refeicao not in self.refeicoes:
            raise ValueError(f"refeição desconhecida: {refeicao}; use uma de: {', '.join(self.refeicoes)}")
        metas = self.metas["refeicoes"][refeicao]
        if refeicao not in self._combinacoes:
            self._combinacoes[refeicao] = self.montador.combinacoes(
                refeicao, metas, vetar_item=self.avaliador._veto_item, nao_misturar=self.avaliador.nao_misturar,
                semente=self.semente(refeicao))
        ops, resumo = self.avaliador.tres_opcoes(self._combinacoes[refeicao], refeicao, metas, politica)
        self.mostradas[refeicao] = ops
        comb = self._combinacoes[refeicao]
        resumo = {**resumo, "nivel_restricoes": comb.attrs.get("nivel_restricoes"),
                  "descartadas": comb.attrs.get("descartadas", {})}
        return {"refeicao": NOMES_REFEICAO[refeicao], "metas": metas, "avaliacao": resumo,
                "opcoes": [self._formatar(r, metas) for _, r in ops.iterrows()]}

    def dia(self, politica: str = "bandit") -> dict:
        return {"data": self.data.isoformat(), "energia_dia_kcal": self.metas["dia"]["energia_kcal"],
                "avisos_metas": self.metas.get("avisos", []), "avisos": self.avisos,
                "refeicoes": {r: self.opcoes(r, politica) for r in self.refeicoes}}

    def escolher(self, refeicao: str, posicao: int):
        """posicao: 0, 1 ou 2 (opção escolhida entre as últimas mostradas para essa refeição)."""
        if refeicao not in self.mostradas:
            raise ValueError(f"nenhuma opção mostrada ainda para {refeicao}")
        self.avaliador.registrar_escolha(refeicao, self.mostradas[refeicao], posicao)

    def estado(self) -> dict:
        """O que o Avaliador aprendeu (A e b por refeição), em listas, para guardar por usuário."""
        return self.avaliador.estado()

    def explicar(self, refeicao: str, top: int = 5):
        """Os maiores e os menores pesos aprendidos pelo bandit (o que a pessoa prefere e o que evita)."""
        return self.avaliador.explicar(refeicao, top=top)

    # ---------------------------------------------------------------- troca de alimento pelo mapa SOM
    @property
    def som(self):
        if self._som is None:                       # carrega o mapa só na primeira troca pedida
            from .som import Substituidor
            self._som = Substituidor()
            # a tabela da troca: a TBCA do SOM e, para os pratos da despensa que não estão nela (diversidade),
            # as linhas da própria despensa, que têm os mesmos nutrientes, alérgenos e dietas
            tab = self._som.d.set_index("codigo")
            extra = pd.concat([self.montador.d, self.montador.diversidade]).drop_duplicates("codigo") \
                .set_index("codigo")
            extra = extra[~extra.index.isin(tab.index)]
            self._tabela = pd.concat([tab, extra[[c for c in tab.columns if c in extra.columns]]])
        return self._som

    @staticmethod
    def _mesmo_alimento(nome):
        """Chave do alimento sem corte nem preparo: 'Repolho, cru' e 'Repolho, branco, cozido' -> 'repolho'.
        Quando o primeiro termo da TBCA é genérico ('Carne, frango, peito'), usa os dois primeiros
        ('carne, frango'), para frango e boi continuarem diferentes."""
        termos = [t.strip() for t in sem_acento(nome).split(",")]
        return ", ".join(termos[:2]) if termos[0] in GENERICOS else termos[0]

    def _comuns(self, refeicao, grupo):
        """Códigos dos alimentos que as pessoas comem naquela refeição e grupo, em qualquer região (POF)."""
        if not hasattr(self, "_despensa_toda"):
            d = pd.read_csv(ARQ_DESPENSA, usecols=["refeicao", "grupo", "codigo", "camada"])
            self._despensa_toda = d[d.camada == "nucleo"]           # o que as pessoas comem (POF)
        d = self._despensa_toda
        return set(d[(d.refeicao == refeicao) & (d.grupo == grupo)].codigo)

    def substitutos(self, refeicao: str, posicao: int, grupo: str, n: int = 5) -> dict:
        """Alimentos com perfil nutricional parecido com o item `grupo` da opção `posicao`, pelo mapa SOM.

        Regras, nesta ordem:
          * restrições e "não gosta" da pessoa (o Substituidor já filtra);
          * só o que pode ser item do prato (sem molho, pasta, farinha crua; cru só em salada e fruta);
          * um por alimento: cortes e preparos do mesmo alimento contam como um só, e o próprio sai;
          * primeiro os alimentos que as pessoas comem nessa refeição (POF, qualquer região), na ordem do
            mapa; se faltar, completa com os outros. 'comum' diz de qual dos dois veio."""
        item = next(i for i in self.mostradas[refeicao].iloc[posicao].itens if i["grupo"] == grupo)
        res = self.som.substituir(item["alimento"], n=15 * n, restricoes=self.avaliador.restricoes,
                                  evitar=self.avaliador.nao_gosta, codigo=item["codigo"])
        comuns = self._comuns(refeicao, grupo)
        vistos, candidatos = {self._mesmo_alimento(item["alimento"])}, []
        for x in res.get("substitutos", []):
            chave = self._mesmo_alimento(x["nome"])
            if chave in vistos or not serve_no_prato(x["nome"]):
                continue
            if grupo not in ("legumes", "fruta") and re.search(r"\bcrua?\b|\bcrus\b", sem_acento(x["nome"])):
                continue
            vistos.add(chave)
            candidatos.append({**{k: x[k] for k in ("codigo", "nome", "motivo", "distancia_no_mapa", "por_100g")},
                               "comum": x["codigo"] in comuns})
        ordem = [c for c in candidatos if c["comum"]] + [c for c in candidatos if not c["comum"]]
        saida, barrados = [], 0
        for c in ordem:                     # só oferece o que passa na trava depois da troca (ex.: sódio)
            linha = self._linha_trocada(refeicao, posicao, grupo, c["codigo"])
            if linha.motivo_veto.iloc[0]:
                barrados += 1
                continue
            c["gramas"] = next(i["gramas"] for i in linha.itens.iloc[0] if i["grupo"] == grupo)
            c["bem_estar_depois"] = float(linha.bem_estar.iloc[0])
            saida.append(c)
            if len(saida) == n:
                break
        return {"original": item, "gaveta_no_mapa": res.get("gaveta_no_mapa"), "substitutos": saida,
                "barrados_pela_trava": barrados}

    def _linha_trocada(self, refeicao, posicao, grupo, codigo_novo):
        """A opção com o item trocado, já avaliada (trava, nutrientes, bem-estar), sem mudar nada ainda.
        O novo alimento fica com a MESMA energia do item antigo (gramas entre 0,5 e 1,75 vez as do
        original, de 5 em 5)."""
        tab = self._tabela
        metas = self.metas["refeicoes"][refeicao]
        antiga = self.mostradas[refeicao].iloc[posicao]
        itens = [dict(i) for i in antiga.itens]
        k = next(j for j, i in enumerate(itens) if i["grupo"] == grupo)
        velho, novo = itens[k], tab.loc[codigo_novo]
        kcal_item = float(tab.loc[velho["codigo"], "energia_kcal"]) * velho["gramas"] / 100
        gramas = kcal_item / max(float(novo.energia_kcal), 1) * 100
        gramas = float(np.clip(gramas, 0.5 * velho["gramas"], 1.75 * velho["gramas"]))
        gramas = max(round(gramas / 5) * 5, 5)
        itens[k] = {"grupo": grupo, "codigo": codigo_novo, "alimento": novo.descricao, "gramas": float(gramas),
                    "porcao_tipica_g": float(gramas), "subtipo": subtipo(grupo, novo.descricao),
                    "id_base": "" if pd.isna(novo.id_base) else str(novo.id_base), "novidade": False}
        linha = self.avaliador.avaliar(self.montador.montar_linha(itens, tab, metas), refeicao, metas)
        if not linha.motivo_veto.iloc[0]:           # as restrições do Montador valem também para a troca
            motivo = self.montador.fora_das_restricoes(linha.iloc[0], metas)
            if motivo:
                linha["motivo_veto"] = motivo
        linha["nota"] = antiga.nota
        linha["novidade"] = any(i.get("novidade", False) for i in itens)
        return linha

    def trocar(self, refeicao: str, posicao: int, grupo: str, codigo_novo: str) -> dict:
        """Troca o item `grupo` da opção `posicao` pelo alimento `codigo_novo` e reavalia a opção.
        A opção trocada substitui a antiga entre as mostradas, então escolher() registra a troca e o bandit
        aprende com a opção como ela ficou. Levanta ValueError se a troca não passar na trava."""
        self.som                                            # garante o mapa e a tabela carregados
        linha = self._linha_trocada(refeicao, posicao, grupo, codigo_novo)
        if linha.motivo_veto.iloc[0]:
            raise ValueError(f"essa troca não passa na trava: {linha.motivo_veto.iloc[0]}")
        ops = self.mostradas[refeicao]
        linha.index = [ops.index[posicao]]
        self.mostradas[refeicao] = pd.concat([ops.iloc[:posicao], linha[ops.columns], ops.iloc[posicao + 1:]])
        return self._formatar(self.mostradas[refeicao].iloc[posicao], self.metas["refeicoes"][refeicao])

    @staticmethod
    def _formatar(r, metas):
        pct = lambda v, m: round(100 * v / m) if m else None
        return {
            "itens": [{"grupo": ROTULO_GRUPO[i["grupo"]], "codigo": i["codigo"], "alimento": i["alimento"],
                       "gramas": i["gramas"], "porcao_tipica_g": i["porcao_tipica_g"], "subtipo": i["subtipo"],
                       "novidade": bool(i.get("novidade", False))} for i in r.itens],
            "totais": {"energia_kcal": r.energia_kcal, "proteina_g": r.proteina_g,
                       "carboidrato_g": r.carboidrato_total_g, "gordura_g": r.lipidios_g,
                       "fibra_g": r.fibra_g, "sodio_mg": r.sodio_mg},
            "percentual_da_meta": {"energia": pct(r.energia_kcal, metas["energia_kcal"]),
                                   "proteina": pct(r.proteina_g, metas["proteina_g"]),
                                   "fibra": pct(r.fibra_g, metas["fibra_g"]),
                                   "sodio_do_limite": pct(r.sodio_mg, metas["sodio_mg_max"])},
            "bem_estar": float(r.bem_estar), "nota": float(r.nota),
            "novidade": bool(r.get("novidade", False)),
        }
