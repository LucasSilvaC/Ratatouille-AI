"""
Calculadora DRI: metas de energia e macronutrientes do dia e de cada refeição, para adultos.

É a mesma base da calculadora do USDA (https://www.nal.usda.gov/human-nutrition-and-food-safety/dri-calculator):
as Dietary Reference Intakes das National Academies.

  * Energia, dois métodos (parâmetro `metodo`):
      - "eer2023" (padrão): equações de gasto energético total (EER) de 2023, uma por sexo e nível de
        atividade (National Academies, "Dietary Reference Intakes for Energy", 2023, Tabela S-1).
      - "anjos": método fatorial ajustado para brasileiros. Gasto do dia = TMB x NAF, com a TMB
        (taxa metabólica basal, o gasto em repouso) pela equação de Anjos, Wahrlich e Vasconcellos (2013),
        feita com adultos de Niterói, e o NAF (nível de atividade física) escolhido dentro das faixas
        do relatório FAO/OMS/UNU de 2004. As equações internacionais tendem a superestimar a TMB de
        brasileiros; esta dá valores menores.
    Idade em anos, altura em cm, peso em kg, resultado em kcal/dia. Os dois valores saem em
    dia["energia_por_metodo"], para comparar.
  * Proteína: RDA de 0,8 g/kg/dia; faixa aceitável (AMDR) de 10% a 35% da energia.
  * Carboidrato: RDA de 130 g/dia; AMDR de 45% a 65% da energia.
  * Gordura: AMDR de 20% a 35% da energia.
  * Fibra: AI de 14 g a cada 1.000 kcal.
  * Sódio: reduzir se passar de 2.300 mg/dia (CDRR, 2019).
  * Água total: AI de 3,7 L (homens) e 2,7 L (mulheres).
  * Gordura saturada e açúcar de adição abaixo de 10% da energia: vêm das Dietary Guidelines for Americans
    e do Guia Alimentar, não das DRI (a calculadora do USDA não traz esses limites).

Fora do escopo (devolve ForaDoEscopo, e o app deve encaminhar para um profissional):
  menores de 19 anos, gestantes e lactantes. Pessoas abaixo do peso ou com obesidade recebem as metas,
  mas com um aviso, porque as equações estimam a energia para MANTER o peso atual.

Uso:
    from ratatouille_recommendation.dri import calcular_dri
    calcular_dri(sexo="F", idade=30, altura_cm=165, peso_kg=62, atividade="pouco_ativo")
    calcular_dri(sexo="F", idade=30, altura_cm=165, peso_kg=62, atividade="pouco_ativo", metodo="anjos")
"""
from __future__ import annotations

# (constante, idade, altura_cm, peso_kg) — Tabela S-1, adultos de 19 anos ou mais
EER_2023 = {
    ("M", "inativo"):     (753.07, -10.83, 6.50, 14.10),
    ("M", "pouco_ativo"): (581.47, -10.83, 8.30, 14.94),
    ("M", "ativo"):       (1004.82, -10.83, 6.52, 15.91),
    ("M", "muito_ativo"): (-517.88, -10.83, 15.61, 19.11),
    ("F", "inativo"):     (584.90, -7.01, 5.72, 11.71),
    ("F", "pouco_ativo"): (575.77, -7.01, 6.60, 12.14),
    ("F", "ativo"):       (710.25, -7.01, 6.54, 12.34),
    ("F", "muito_ativo"): (511.83, -7.01, 9.07, 12.56),
}
ATIVIDADES = ("inativo", "pouco_ativo", "ativo", "muito_ativo")

# TMB de Anjos et al. (2013), em kcal/dia: (constante, peso_kg, altura_cm, idade).
# ATENÇÃO: o artigo original rotulou estes coeficientes como kJ/dia; a errata (Public Health Nutr 16(8):1526)
# corrigiu: estes são os valores em kcal/dia.
TMB_ANJOS = {
    "M": (-450.5, 9.99, 7.14, -2.79),
    "F": (-814.3, 8.95, 8.87, -0.70),
}
# NAF (quantas vezes a TMB a pessoa gasta no dia). Escolha nossa dentro das faixas do relatório
# FAO/OMS/UNU de 2004: sedentário 1,40-1,69; ativo 1,70-1,99; vigoroso 2,00-2,40.
NAF = {"inativo": 1.40, "pouco_ativo": 1.55, "ativo": 1.75, "muito_ativo": 2.00}
METODOS = ("eer2023", "anjos")

# como a energia do dia se divide entre as refeições do cronograma (soma 1)
REPARTICAO = {"cafe_da_manha": 0.20, "almoco": 0.35, "lanche": 0.15, "jantar": 0.30}

# metas usadas para PLANEJAR (dentro das faixas AMDR): 15% proteína, 55% carboidrato, 30% gordura
ALVO_PROTEINA, ALVO_CARBOIDRATO, ALVO_GORDURA = 0.15, 0.55, 0.30

REFERENCIAS = [
    "National Academies (2023). Dietary Reference Intakes for Energy — equações EER, Tabela S-1.",
    "Institute of Medicine (2005). DRI for Energy, Carbohydrate, Fiber, Fat, Fatty Acids, Cholesterol, "
    "Protein, and Amino Acids — RDA, AMDR e AI de fibra.",
    "National Academies (2019). DRI for Sodium and Potassium — CDRR de sódio.",
    "Institute of Medicine (2005). DRI for Water, Potassium, Sodium, Chloride, and Sulfate — AI de água.",
]
REFERENCIAS_ANJOS = [
    "Anjos LA, Wahrlich V, Vasconcellos MTL (2014). BMR in a Brazilian adult probability sample: the "
    "Nutrition, Physical Activity and Health Survey. Public Health Nutr 17:853-60 (errata: 16(8):1526) — TMB.",
    "FAO/WHO/UNU (2004). Human energy requirements — método fatorial e faixas de NAF.",
]


class ForaDoEscopo(ValueError):
    """Perfil para o qual a calculadora não dá metas (menor de 19 anos, gestante, lactante)."""


def eer_2023(sexo, idade, altura_cm, peso_kg, atividade):
    """Gasto energético do dia (kcal) pela equação EER de 2023."""
    a, b_idade, c_altura, d_peso = EER_2023[(sexo, atividade)]
    return a + b_idade * idade + c_altura * altura_cm + d_peso * peso_kg


def tmb_anjos(sexo, idade, altura_cm, peso_kg):
    """Taxa metabólica basal (kcal/dia, gasto em repouso) pela equação de Anjos et al. para brasileiros."""
    a, b_peso, c_altura, d_idade = TMB_ANJOS[sexo]
    return a + b_peso * peso_kg + c_altura * altura_cm + d_idade * idade


def _validar(sexo, idade, altura_cm, peso_kg, atividade, gestante, amamentando):
    if gestante or amamentando:
        raise ForaDoEscopo("Gestação e amamentação mudam muito as necessidades: procure um nutricionista "
                           "ou o pré-natal para ter metas individuais.")
    if sexo not in ("M", "F"):
        raise ValueError("sexo deve ser 'M' ou 'F'")
    if atividade not in ATIVIDADES:
        raise ValueError(f"atividade deve ser uma de: {', '.join(ATIVIDADES)}")
    if idade < 19:
        raise ForaDoEscopo("As metas para menores de 19 anos incluem a energia do crescimento e não são "
                           "calculadas aqui: procure um nutricionista ou pediatra.")
    if idade > 120 or not 100 <= altura_cm <= 250 or not 30 <= peso_kg <= 300:
        raise ValueError("idade, altura ou peso fora de uma faixa plausível")


def classificar_imc(imc):
    if imc < 18.5:
        return "baixo peso"
    if imc < 25:
        return "eutrofia"
    if imc < 30:
        return "sobrepeso"
    return "obesidade"


def calcular_dri(sexo: str, idade: float, altura_cm: float, peso_kg: float, atividade: str,
                 gestante: bool = False, amamentando: bool = False, reparticao: dict | None = None,
                 metodo: str = "eer2023") -> dict:
    """Metas do dia e por refeição. Levanta ForaDoEscopo ou ValueError se o perfil não serve.
    metodo: "eer2023" (DRI, padrão) ou "anjos" (TMB de Anjos x NAF, ajustado para brasileiros)."""
    sexo = str(sexo).upper()[:1]
    metodo = metodo or "eer2023"
    if metodo not in METODOS:
        raise ValueError(f"metodo deve ser um de: {', '.join(METODOS)}")
    _validar(sexo, idade, altura_cm, peso_kg, atividade, gestante, amamentando)
    kcal_eer = eer_2023(sexo, idade, altura_cm, peso_kg, atividade)
    tmb = tmb_anjos(sexo, idade, altura_cm, peso_kg)
    kcal_anjos = tmb * NAF[atividade]
    kcal = kcal_anjos if metodo == "anjos" else kcal_eer
    imc = peso_kg / (altura_cm / 100) ** 2

    proteina_rda = 0.8 * peso_kg
    dia = {
        "energia_kcal": round(kcal),
        "energia_por_metodo": {"eer2023": round(kcal_eer), "anjos": round(kcal_anjos)},
        "proteina_g": {"rda": round(proteina_rda, 1),
                       "min": round(max(proteina_rda, 0.10 * kcal / 4), 1), "max": round(0.35 * kcal / 4, 1),
                       "meta": round(max(proteina_rda, ALVO_PROTEINA * kcal / 4), 1)},
        "carboidrato_g": {"rda": 130, "min": round(max(130, 0.45 * kcal / 4), 1), "max": round(0.65 * kcal / 4, 1),
                          "meta": round(max(130, ALVO_CARBOIDRATO * kcal / 4), 1)},
        "gordura_g": {"min": round(0.20 * kcal / 9, 1), "max": round(0.35 * kcal / 9, 1),
                      "meta": round(ALVO_GORDURA * kcal / 9, 1)},
        "fibra_g": round(14 * kcal / 1000, 1),
        "sodio_mg_max": 2300,
        "gordura_saturada_g_max": round(0.10 * kcal / 9, 1),
        "acucar_adicao_g_max": round(0.10 * kcal / 4, 1),
        "agua_l": 3.7 if sexo == "M" else 2.7,
    }

    reparticao = reparticao or REPARTICAO
    refeicoes = {}
    for nome, fracao in reparticao.items():
        refeicoes[nome] = {
            "fracao": fracao,
            "energia_kcal": round(fracao * kcal),
            "proteina_g": round(fracao * dia["proteina_g"]["meta"], 1),
            "proteina_g_min": round(fracao * dia["proteina_g"]["min"], 1),
            "carboidrato_g": round(fracao * dia["carboidrato_g"]["meta"], 1),
            "gordura_g": round(fracao * dia["gordura_g"]["meta"], 1),
            "gordura_g_max": round(fracao * dia["gordura_g"]["max"], 1),
            "fibra_g": round(fracao * dia["fibra_g"], 1),
            "sodio_mg_max": round(fracao * dia["sodio_mg_max"]),
        }

    avisos = []
    classe = classificar_imc(imc)
    if classe in ("baixo peso", "obesidade"):
        avisos.append(f"IMC na faixa de {classe}: as equações estimam a energia para manter o peso atual. "
                      "Para ganhar ou perder peso, procure um nutricionista.")
    if metodo == "anjos":
        dia["tmb_kcal"] = round(tmb)
        dia["naf"] = NAF[atividade]
        fonte = "calculadora DRI (energia: TMB de Anjos x NAF, ajustada para brasileiros)"
        referencias = REFERENCIAS_ANJOS + REFERENCIAS
    else:
        fonte = "calculadora DRI (equações EER 2023)"
        referencias = REFERENCIAS
    return {
        "fonte": fonte,
        "metodo": metodo,
        "entrada": {"sexo": sexo, "idade": idade, "altura_cm": altura_cm, "peso_kg": peso_kg,
                    "atividade": atividade, "metodo": metodo},
        "imc": round(imc, 1),
        "classificacao_imc": classe,
        "dia": dia,
        "refeicoes": refeicoes,
        "avisos": avisos,
        "referencias": referencias,
    }
