"""
Restrições alimentares que o planejador aceita (o contrato com o roteador/chatbot).

O roteador traduz o que a pessoa escreve ("sigo kosher") para nomes destas listas; o planejador não interpreta
texto livre. Um nome fora das listas levanta EntradaInvalida.

  RESTRICAO : restrição -> (coluna da TBCA, valor exigido, palavras proibidas no nome)
  TIPOS     : tipos de alimento usados em "não misturar no mesmo prato" (ex.: carne e laticínio)
"""
from __future__ import annotations

import re
import unicodedata

# ----------------------------------------------------------------------------------------------------------
# ENTRADA DE RESTRIÇÕES (o contrato com o roteador). O roteador/formulário só pode mandar nomes destas listas;
# um nome desconhecido levanta EntradaInvalida (antes, era ignorado em silêncio).
#
# restricoes: restrição -> (coluna da TBCA, valor exigido, palavras proibidas no nome). O alimento sai se a
#   coluna não tiver o valor exigido OU se o nome (com a lista de ingredientes, nas receitas) tiver uma das
#   palavras. As colunas de alérgeno da TBCA foram detectadas pelo nome e 0 quer dizer "não detectado"; as
#   palavras são a segunda rede de segurança.
_PORCO = (r"porco|suin|bacon|toucinho|torresmo|banha|presunto|apresuntado|mortadela|salame|\bcopa\b|\blombo(?! de (bacalhau|peixe|atum|salmao))|pernil|"
          r"linguica|calabresa|paio|pepperoni|chouri|salsicha")
_FRUTOS_DO_MAR = (r"camar|lagost|caranguej|\bsiri\b|marisco|mexilh|ostra|\blula|polvo|vieira|sururu|lambreta|"
                  r"molusco|frutos do mar|\bkani")
_PEIXE = (r"peixe|pescad|atum|sardinha|bacalhau|salmao|tilapia|merluza|corvina|robalo|badejo|abadejo|linguado|"
          r"tainha|anchova|cavala|truta|pirarucu|tambaqui|pacu|surubim|pintado|cacao\b|bagre|namorado|sushi")
RESTRICAO = {
    "vegetariano": ("dieta_vegetariano", 1, None),
    "vegano": ("dieta_vegano", 1, None),
    "pescetariano": (None, None, r"\bboi\b|bovin|carneiro|cordeiro|ovino|cabrito|caprino|vitela|frango|galinha|"
                                 r"\bperu\b|\bpato\b|chester|figado|charque|carne seca|" + _PORCO),
    "sem_lactose": ("alergeno_leite", 0, r"\bleite|queijo|manteiga|iogurte|requeijao|creme de leite"),
    "alergia_ovo": ("alergeno_ovos", 0, r"\bovo|maionese|omelete"),
    "celiaco": ("alergeno_gluten", 0, r"trigo|\bpao\b|macarrao|biscoito|aveia|cevada|centeio"),
    "alergia_amendoim": ("alergeno_amendoim", 0, r"amendoim|pacoca|pe de moleque"),
    "alergia_castanhas": ("alergeno_castanhas_nozes", 0, r"castanha|\bnoz|nozes|amendoa|avela|pistache|macadamia|"
                                                         r"pecan"),
    "alergia_soja": ("alergeno_soja", 0, r"\bsoja|tofu|shoyu|misso|edamame|tempeh"),
    "alergia_peixe": ("alergeno_peixes", 0, _PEIXE),
    "alergia_crustaceos": ("alergeno_crustaceos", 0, r"camar|lagost|caranguej|\bsiri\b|\bkani"),
    "sem_carne_vermelha": (None, None, r"\bboi\b|bovin|porco|suin|carneiro|cordeiro|cabrito|linguica|bacon|"
                                       r"mortadela|presunto|salame|figado|charque|carne seca|toucinho"),
    "sem_carne_bovina": (None, None, r"\bboi\b|bovin|vitela|charque|carne seca|carne de sol|figado bovino"),
    "sem_porco": (None, None, _PORCO),
    "sem_frutos_do_mar": ("alergeno_crustaceos", 0, _FRUTOS_DO_MAR),
    "sem_peixe_sem_escama": (None, None, r"cacao\b|bagre|enguia|moreia|tubarao|arraia|\braia\b|pintado|surubim|"
                                         r"\bjau\b|mandi\b|piraiba|filhote|pirarara|cachara"),
    "sem_sangue": (None, None, r"molho pardo|cabidela|chouri|morcela|sarapatel|sangue"),
    "sem_alcool": (None, None, r"(?<!vinagre de )vinho|cerveja|cachaca|conhaque|\brum\b|licor|vodka|whisky|"
                               r"\bsaque\b|\bsake\b|marsala|flambad"),
}

# nao_misturar: pares de TIPOS que não podem estar no mesmo prato (por exemplo, carne e laticínio). Tipo ->
#   (coluna da TBCA que marca o tipo, palavras no nome). O par vale para a combinação inteira e também dentro de
#   um prato pronto (um strogonoff com creme de leite já junta ave e laticínio).
TIPOS = {
    "carne": (None, r"\bboi\b|bovin|carneiro|cordeiro|ovino|cabrito|caprino|vitela|figado|charque|carne seca|"
                    r"\bcarne\b(?!,? (de )?(soja|frango|peru|pato|galinha|chester|peixe))|" + _PORCO),
    "ave": (None, r"frango|galinha|\bperu\b|\bpato\b|chester|codorna"),
    "peixe": ("alergeno_peixes", _PEIXE),
    "frutos_do_mar": ("alergeno_crustaceos", _FRUTOS_DO_MAR),
    # só pelas palavras: a coluna de leite da TBCA marca a couve-manteiga
    "laticinio": (None, r"\bleite\b(?! de (coco|soja|amendoa|castanha|arroz|aveia))|queijo|(?<!couve-)(?<!couve, )"
                        r"manteiga|iogurte|requeijao|creme de leite|\bnata\b|coalhada|ricota|mucarela|parmesao|"
                        r"catupiry|chantilly"),
}


class EntradaInvalida(ValueError):
    """Restrição ou tipo que o Montador não conhece (o roteador mandou um nome fora das listas)."""


def validar_entrada(restricoes=(), nao_misturar=()):
    """Confere a entrada e devolve (restricoes, nao_misturar) normalizados. Levanta EntradaInvalida."""
    restricoes = list(restricoes)
    desconhecidas = [r for r in restricoes if r not in RESTRICAO]
    if desconhecidas:
        raise EntradaInvalida(f"restrição desconhecida: {', '.join(desconhecidas)}; "
                              f"as aceitas são: {', '.join(RESTRICAO)}")
    pares = []
    for par in nao_misturar:
        par = tuple(par)
        if len(par) != 2 or any(t not in TIPOS for t in par) or par[0] == par[1]:
            raise EntradaInvalida(f"par de não misturar inválido: {list(par)}; "
                                  f"use dois tipos diferentes entre: {', '.join(TIPOS)}")
        pares.append(par)
    return restricoes, pares


def tipos_do_alimento(nome_norm, item=None):
    """Conjunto de TIPOS do alimento (ou prato) pelo nome sem acento e, se houver, pelas colunas da TBCA.
    Ovo de galinha não é ave."""
    nome_norm = re.sub(r"ovos?,? (de )?(galinha|codorna)", "ovo", nome_norm)
    achados = set()
    for t, (col, rx) in TIPOS.items():
        if (col and item is not None and col in item.index and int(item[col]) == 1) or re.search(rx, nome_norm):
            achados.add(t)
    return achados


def par_proibido(tipos, nao_misturar):
    """O primeiro par de nao_misturar coberto pelo conjunto de tipos, ou None."""
    return next((p for p in nao_misturar if p[0] in tipos and p[1] in tipos), None)


def _norm(t):
    """Minúsculas e sem acento."""
    t = unicodedata.normalize("NFKD", str(t).lower())
    return "".join(c for c in t if not unicodedata.combining(c))
