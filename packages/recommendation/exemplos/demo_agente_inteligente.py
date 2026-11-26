"""
Demonstração: o Planejador (Montador) e o Avaliador são agentes inteligentes e autônomos, sem LLM.

    uv run python exemplos/demo_agente_inteligente.py      (dentro de packages/recommendation)

Roda sem internet. Quatro partes:
  1. GARANTIA E DECISÃO: uma pessoa que segue kosher (entrada já traduzida pelo roteador). O Montador tira o que
     é proibido, descarta as combinações inviáveis, relaxa as restrições do prato se precisar, e nenhuma opção
     mostrada viola as regras.
  2. AUTONOMIA: duas pessoas com o MESMO perfil. Uma sempre escolhe a opção com salada crua, a outra a opção com
     legumes cozidos (quando aparece). Ninguém programa isso: com os dias, o Avaliador passa a oferecer a cada uma
     o que ela escolhe.
  3. EXPLICAÇÃO: o que o Avaliador aprendeu de cada uma (os pesos do bandit).
  4. VARIEDADE: o Montador sorteia, a cada dia, parte dos alimentos (cauda da POF e diversidade). Comparação com
     usar sempre os mais comidos: quantos alimentos a pessoa vê e se o Avaliador consegue aprender que ela gosta
     de peixe, que quase nunca está entre os mais comidos.
"""
import re
import sys

from ratatouille_recommendation import Planejador                  # noqa: E402
from ratatouille_recommendation.montador import NOMES_REFEICAO     # noqa: E402
from ratatouille_recommendation.restricoes import _norm, tipos_do_alimento  # noqa: E402

PERFIL = {"sexo": "F", "idade": 30, "altura_cm": 163, "peso_kg": 62, "atividade": "pouco_ativo"}
KOSHER = {"restricoes": ["sem_porco", "sem_frutos_do_mar", "sem_peixe_sem_escama", "sem_sangue"],
          "nao_misturar": [["carne", "laticinio"], ["ave", "laticinio"]]}
PROIBIDO = ("carne, porco", "mortadela", "bacon", "presunto", "linguica", "camarao", "lula", "polvo")
DIAS = 15
ROTULO_LEGUME = {"folha_crua": "folha crua", "cru": "cru", "cozido": "cozido"}
NIVEIS = {1: "todas as restrições do prato", 2: "sem as faixas de macronutrientes", 3: "só os limites das porções"}


def linha():
    print("-" * 78)


PREPARO = re.compile(r"cozid|grelhad|assad|frit|refogad|ensopad|cru|inteir|s/ |c/ |drenad|vapor|milanesa")


def curto(nome):
    """Nome curto para mostrar, com o tipo e o corte das carnes:
    "Carne, boi, patinho, s/ gordura, grelhado" -> "Boi (patinho)"; "Carne, frango, peito..." -> "Frango (peito)";
    "Peixe, água salgada, merluza, cozido" -> "Peixe (merluza)"; "Feijão, carioca..." -> "Feijão"."""
    partes = [p.strip() for p in nome.split(" (")[0].split(",") if p.strip()]
    base = partes[0].lower()
    if base == "carne" and len(partes) > 1:
        corte = partes[2] if len(partes) > 2 and not PREPARO.search(partes[2].lower()) else ""
        return partes[1].capitalize() + (f" ({corte})" if corte else "")
    if base == "peixe" and len(partes) > 1:
        especie = partes[2] if partes[1].lower().startswith("água") and len(partes) > 2 else partes[1]
        return f"Peixe ({especie})" if not PREPARO.search(especie.lower()) else "Peixe"
    return partes[0]


def subtipo(opcao, grupo):
    return next(i["subtipo"] for i in opcao if i["grupo"] == grupo)


# ------------------------------------------------------------------ 1. garantia e decisão
linha()
print("1. GARANTIA E DECISÃO — pessoa que segue kosher")
linha()
c = Planejador(PERFIL, regiao="Sudeste", **KOSHER)
violacoes = 0
for ref in c.refeicoes:
    ops = c.opcoes(ref)
    comb = c._combinacoes[ref]
    desc = comb.attrs["descartadas"]
    print(f"\n{NOMES_REFEICAO[ref]}: {len(comb)} combinações viáveis "
          f"(descartadas: {desc['nao_misturar']} por misturar carne/ave com leite, "
          f"{desc['faixas']} fora das faixas, {desc['frutas_e_legumes']} sem frutas e legumes suficientes)")
    print(f"   nível de restrições usado: {comb.attrs['nivel_restricoes']} ({NIVEIS[comb.attrs['nivel_restricoes']]})")
    for k, o in enumerate(ops["opcoes"], 1):
        nomes = [_norm(i["alimento"]) for i in o["itens"]]
        tipos = set().union(*(tipos_do_alimento(n) for n in nomes))
        ruim = any(n.startswith(PROIBIDO) for n in nomes) or {"carne", "laticinio"} <= tipos \
            or {"ave", "laticinio"} <= tipos
        violacoes += ruim
        print(f"   opção {k}: " + " + ".join(f"{i['gramas']:.0f} g {curto(i['alimento'])}" for i in o["itens"]))
print(f"\n=> opções que violam a regra kosher: {violacoes}")

# ------------------------------------------------------------------ 2. autonomia
linha()
print(f"2. AUTONOMIA — duas pessoas com o mesmo perfil, {DIAS} dias de almoço e jantar")
linha()
pessoas = {"Ana (gosta de salada crua)": "folha_crua", "Bia (gosta de legumes cozidos)": "cozido"}
crons = {nome: Planejador(PERFIL, regiao="Sudeste") for nome in pessoas}
oferta = {nome: [] for nome in pessoas}            # por dia: quantas das 6 opções têm o que a pessoa prefere
for dia in range(DIAS):
    for nome, gosto in pessoas.items():
        cr, n_gosto = crons[nome], 0
        for ref in ("almoco", "jantar"):
            cr.opcoes(ref)
            subtipos = [subtipo(o, "legumes") for o in cr.mostradas[ref].itens]
            n_gosto += subtipos.count(gosto)
            cr.escolher(ref, subtipos.index(gosto) if gosto in subtipos else 0)
        oferta[nome].append(n_gosto)
        cr.novo_dia()

for nome in pessoas:
    o = oferta[nome]
    print(f"{nome}\n   opções com o que ela escolhe, por dia (de 6): {' '.join(map(str, o))}")
    print(f"   média nos 3 primeiros dias: {sum(o[:3]) / 3:.1f}   nos 3 últimos: {sum(o[-3:]) / 3:.1f}")
print("\nAlmoço do último dia de cada uma (mesmo perfil, mesmas metas, mesma despensa):")
for nome, cr in crons.items():
    cr.opcoes("almoco")
    print(f"  {nome}:")
    for itens in cr.mostradas["almoco"].itens:
        print("     " + " + ".join(curto(i["alimento"]) + (f" ({ROTULO_LEGUME.get(i['subtipo'], i['subtipo'])})"
                                    if i["grupo"] == "legumes" else "") for i in itens))

# ------------------------------------------------------------------ 3. explicação
linha()
print("3. EXPLICAÇÃO — o que o Avaliador aprendeu no almoço (pesos θ do bandit)")
linha()
for nome, cr in crons.items():
    gosta, _ = cr.avaliador.explicar("almoco", top=100)            # todos os pesos θ, do maior ao menor
    print(f"{nome}: peso de legumes crus {gosta['legumes:folha_crua']:+.2f}, "
          f"de legumes cozidos {gosta['legumes:cozido']:+.2f}")

# ------------------------------------------------------------------ 4. variedade
linha()
print(f"4. VARIEDADE — pessoa que gosta de peixe, {DIAS} dias de almoço e jantar, com e sem sorteio")
linha()
for variar, rotulo in ((False, "só os mais comidos"), (True, "mais comidos + sorteados")):
    cr = Planejador(PERFIL, regiao="Sudeste", variar=variar)
    vistos, com_peixe, novidades = set(), 0, 0
    for dia in range(DIAS):
        for ref in ("almoco", "jantar"):
            cr.opcoes(ref)
            mostradas = cr.mostradas[ref]
            vistos |= {i["codigo"] for it in mostradas.itens for i in it}
            novidades += int(mostradas.novidade.sum())
            subtipos = [subtipo(o, "proteina") for o in mostradas.itens]
            com_peixe += subtipos.count("peixe")
            cr.escolher(ref, subtipos.index("peixe") if "peixe" in subtipos else 0)
        cr.novo_dia()
    theta, _ = cr.avaliador.explicar("almoco", top=100)
    print(f"{rotulo:26s} alimentos diferentes vistos: {len(vistos):3d}   opções com peixe: {com_peixe:2d}   "
          f"opções com novidade: {novidades:2d}   peso aprendido de peixe: {theta['proteina:peixe']:+.2f}")
print("\n=> sem sorteio o peixe nunca aparece e o Avaliador não tem como aprender; com sorteio ele aparece e é aprendido.")
