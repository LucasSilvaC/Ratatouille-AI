"""
Testes da entrada de restrições do Montador (o contrato com o roteador): nomes aceitos, filtro por alimento,
"não misturar" e "não gosta".

    python -m pytest tests/test_restricoes.py -q
"""
import pandas as pd
import pytest

from ratatouille_recommendation.avaliador import AvaliadorIngredientes
from ratatouille_recommendation.planejador import Planejador
from ratatouille_recommendation.montador import MontadorIngredientes
from ratatouille_recommendation.restricoes import RESTRICAO, TIPOS, EntradaInvalida, _norm, tipos_do_alimento, validar_entrada

MULHER = {"sexo": "F", "idade": 30, "altura_cm": 163, "peso_kg": 62, "atividade": "pouco_ativo"}
KOSHER = {"restricoes": ["sem_porco", "sem_frutos_do_mar", "sem_peixe_sem_escama", "sem_sangue"],
          "nao_misturar": [["carne", "laticinio"], ["ave", "laticinio"]]}


def item(descricao, **colunas):
    base = {c: 0 for c in ["alergeno_gluten", "alergeno_leite", "alergeno_ovos", "alergeno_peixes",
                           "alergeno_crustaceos", "alergeno_amendoim", "alergeno_soja", "alergeno_castanhas_nozes"]}
    base.update({"dieta_vegetariano": 0, "dieta_vegano": 0, "id_base": ""})
    base.update(colunas)
    return pd.Series({"descricao": descricao, **base})


# ---------------------------------------------------------------- nomes aceitos
def test_nome_desconhecido_e_erro():
    with pytest.raises(EntradaInvalida, match="kosher"):
        AvaliadorIngredientes(["kosher"])
    with pytest.raises(EntradaInvalida):
        validar_entrada(nao_misturar=[["carne", "doce"]])
    with pytest.raises(EntradaInvalida):
        validar_entrada(nao_misturar=[["carne", "carne"]])
    with pytest.raises(EntradaInvalida):
        Planejador(MULHER, restricoes=["sem_porco", "halal"])


def test_listas_aceitas():
    assert {"sem_porco", "sem_frutos_do_mar", "sem_peixe_sem_escama", "sem_sangue", "sem_alcool", "vegano",
            "pescetariano", "alergia_amendoim", "alergia_soja"} <= set(RESTRICAO)
    assert set(TIPOS) == {"carne", "ave", "peixe", "frutos_do_mar", "laticinio"}
    r, p = validar_entrada(KOSHER["restricoes"], KOSHER["nao_misturar"])
    assert p == [("carne", "laticinio"), ("ave", "laticinio")]


# ---------------------------------------------------------------- filtro por alimento
@pytest.mark.parametrize("restricao, vetado, permitido", [
    ("sem_porco", "Mortadela", "Arroz, farinha, Colombo"),
    ("sem_porco", "Carne, porco, lombo, assado", "Lombo de bacalhau, assado"),
    ("sem_frutos_do_mar", "Camarão, cozido", "Peixe, água salgada, corvina, assada"),
    ("sem_peixe_sem_escama", "Peixe, água salgada, cação, cozido", "Peixe, água salgada, corvina, assada"),
    ("sem_sangue", "Frango ao molho pardo, c/ sal", "Frango, assado"),
    ("sem_alcool", "Risoto, c/ sal, (arroz, vinho branco)", "Salada, c/ vinagre de vinho tinto"),
    ("alergia_amendoim", "Paçoca", "Banana, prata"),
    ("alergia_soja", "Soja, tofu", "Feijão, carioca"),
    ("pescetariano", "Carne, frango, peito, grelhado", "Peixe, água salgada, corvina, assada"),
])
def test_restricao_por_alimento(restricao, vetado, permitido):
    av = AvaliadorIngredientes([restricao])
    assert av._veto_item(item(vetado)) == f"restrição: {restricao}"
    assert av._veto_item(item(permitido)) is None


def test_coluna_da_tbca_tambem_veta():
    av = AvaliadorIngredientes(["alergia_soja"])
    assert av._veto_item(item("Molho especial", alergeno_soja=1)) == "restrição: alergia_soja"


def test_nao_gosta_por_palavra_inteira():
    av = AvaliadorIngredientes(nao_gosta=["ostra"])
    assert av._veto_item(item("Ostra, cozida")) == "não gosta: ostra"
    assert av._veto_item(item("Ostras, cruas")) == "não gosta: ostra"
    assert av._veto_item(item("Pão, média de amostras")) is None


# ---------------------------------------------------------------- tipos e "não misturar"
@pytest.mark.parametrize("nome, tipos", [
    ("Ovo, galinha, inteiro, cozido", set()),
    ("Carne, frango, peito, grelhado", {"ave"}),
    ("Carne, boi, acém, cozido", {"carne"}),
    ("Couve, manteiga, refogada", set()),
    ("Leite de coco", set()),
    ("Queijo, minas, frescal", {"laticinio"}),
    ("Strogonoff de frango, (frango, creme de leite)", {"ave", "laticinio"}),
])
def test_tipos_do_alimento(nome, tipos):
    assert tipos_do_alimento(_norm(nome)) == tipos


def test_prato_pronto_que_ja_mistura_e_vetado():
    av = AvaliadorIngredientes(nao_misturar=[["ave", "laticinio"]])
    assert av._veto_item(item("Strogonoff de frango, (frango, creme de leite)")) == "não misturar: ave e laticinio"
    assert av._veto_item(item("Carne, frango, peito, grelhado")) is None


def test_montador_nao_junta_par_proibido():
    metas = Planejador(MULHER).metas["refeicoes"]["cafe_da_manha"]
    m = MontadorIngredientes(regiao="Sudeste")
    livre = m.combinacoes("cafe_da_manha", metas)
    sem = m.combinacoes("cafe_da_manha", metas, nao_misturar=[("ave", "laticinio"), ("carne", "laticinio")])
    assert sem.attrs["descartadas"]["nao_misturar"] > 0
    for itens in sem.itens:
        tipos = set().union(*(tipos_do_alimento(_norm(i["alimento"])) for i in itens))
        assert not ({"carne", "laticinio"} <= tipos or {"ave", "laticinio"} <= tipos)
    assert len(livre) >= len(sem)


def test_cronograma_com_regras_kosher():
    c = Planejador(MULHER, regiao="Sudeste", avisos=["abate kosher não verificável"], **KOSHER)
    assert c.avisos == ["abate kosher não verificável"]
    for refeicao in c.refeicoes:
        ops = c.opcoes(refeicao)
        for o in ops["opcoes"]:
            nomes = [_norm(i["alimento"]) for i in o["itens"]]
            assert not any(n.startswith(("carne, porco", "mortadela", "bacon", "presunto", "camarao"))
                           for n in nomes)
            tipos = set().union(*(tipos_do_alimento(n) for n in nomes))
            assert not ({"carne", "laticinio"} <= tipos or {"ave", "laticinio"} <= tipos)
