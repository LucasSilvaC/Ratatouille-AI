"""
Testes da despensa (dados/despensa.csv).

    python -m pytest tests/test_despensa.py -q
"""
import pandas as pd
import pytest

from ratatouille_recommendation.montador import ARQ_DESPENSA, GRUPOS_REFEICAO, NUTRIENTES, MontadorIngredientes

ARQ = ARQ_DESPENSA


@pytest.fixture(scope="module")
def desp():
    return pd.read_csv(ARQ, dtype={"nutriscore": str, "id_base": str}).fillna({"nutriscore": "", "id_base": ""})


def test_duas_camadas(desp):
    assert set(desp.camada) == {"nucleo", "diversidade"}
    nucleo, div = desp[desp.camada == "nucleo"], desp[desp.camada == "diversidade"]
    assert nucleo["rank"].notna().all() and (nucleo.vezes >= 20).all()
    assert div["rank"].isna().all() and (div.regiao == "Brasil").all()
    assert not set(div.codigo) & set(nucleo[nucleo.regiao == "Brasil"].codigo)


def test_grupos_porcoes_e_nutrientes(desp):
    for r in desp.drop_duplicates(["refeicao", "grupo"]).itertuples():
        assert r.grupo in GRUPOS_REFEICAO[r.refeicao]
    assert (desp.porcao_g > 0).all() and (desp.porcao_g % 5 == 0).all()
    assert desp[NUTRIENTES].notna().all().all()
    assert not desp.duplicated(["regiao", "refeicao", "grupo", "codigo"]).any()


def test_diversidade_tem_pratos_de_outras_culturas(desp):
    div = desp[desp.camada == "diversidade"].descricao
    for prato in ("Hómus", "Falafel", "Tabule", "Espetinho de kafta", "Soja, tofu"):
        assert div.str.startswith(prato).any(), prato


def test_diversidade_sem_sobremesas_nem_lanches_completos(desp):
    nomes = desp[desp.camada == "diversidade"].descricao.str.lower().str.split(r",\s*\(").str[0]
    assert not nomes.str.contains(r"chocolate|^mousse|^pudim|^pizza|^sanduíche|^sopa|em pó").any()


def test_montador_usa_so_o_nucleo(desp):
    m = MontadorIngredientes(desp, regiao="Brasil")
    assert set(m.d.codigo) <= set(desp[desp.camada == "nucleo"].codigo)


def test_sem_carne_de_caca_nem_especies_protegidas(desp):
    """Carne de caça e quelônios (tracajá, jabuti) foram tirados: caça sem autorização é proibida no Brasil."""
    assert not desp.descricao.str.contains(r"quelônio|tracajá|tartaruga|jabuti|carne, caça", case=False).any()
