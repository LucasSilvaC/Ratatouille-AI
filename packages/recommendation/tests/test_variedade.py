"""
Testes do sorteio de alimentos do Montador (variedade) e da opção reservada para a novidade.

    python -m pytest tests/test_variedade.py -q
"""
from datetime import date

import numpy as np
import pytest

from ratatouille_recommendation.avaliador import AvaliadorIngredientes
from ratatouille_recommendation.planejador import Planejador
from ratatouille_recommendation.montador import MontadorIngredientes

MULHER = {"sexo": "F", "idade": 30, "altura_cm": 163, "peso_kg": 62, "atividade": "pouco_ativo"}


@pytest.fixture(scope="module")
def m():
    return MontadorIngredientes(regiao="Sudeste")


def test_sem_sorteio_sao_os_mais_comidos(m):
    t = m.itens("almoco", "proteina")
    assert len(t) == 8 and not t.novidade.any()
    assert list(t["rank"]) == sorted(t["rank"])


def test_populares_fixos_e_sorteados_por_semente(m):
    a = m.itens("almoco", "proteina", rng=np.random.default_rng(1))
    b = m.itens("almoco", "proteina", rng=np.random.default_rng(1))
    c = m.itens("almoco", "proteina", rng=np.random.default_rng(2))
    assert len(a) == 8 and a.novidade.sum() == 4
    assert list(a.codigo) == list(b.codigo)                          # mesma semente, mesmos sorteados
    assert list(a.codigo[:4]) == list(c.codigo[:4])                  # os populares não mudam
    assert set(a.codigo[4:]) != set(c.codigo[4:])                    # os sorteados mudam
    assert a.codigo.is_unique


def test_sorteio_cobre_subtipos_diferentes(m):
    sub = m.itens("almoco", "proteina", rng=np.random.default_rng(3)).query("novidade").subtipo
    assert sub.nunique() >= 3


def test_vetados_sao_repostos(m):
    """Vetados saem ANTES de escolher: o grupo é completado com os seguintes e com a diversidade."""
    av = AvaliadorIngredientes(["sem_porco", "vegetariano"])
    sem = m.itens("almoco", "proteina", av._veto_item)               # só o núcleo: o que houver (até 8)
    com = m.itens("almoco", "proteina", av._veto_item, np.random.default_rng(5))
    assert 0 < len(sem) <= 8 and len(com) == 8
    for t in (sem, com):
        assert not any(av._veto_item(r) for _, r in t.iterrows())


def test_cronograma_varia_por_dia_e_repete_no_mesmo_dia():
    c = Planejador(MULHER, regiao="Sudeste", data=date(2026, 11, 24))
    hoje = [o["itens"] for o in c.opcoes("almoco")["opcoes"]]
    assert c.opcoes("almoco")["opcoes"][0]["itens"] == hoje[0]      # recarregar não muda
    c.novo_dia()
    assert c.data == date(2026, 11, 25)
    amanha = [o["itens"] for o in c.opcoes("almoco")["opcoes"]]
    assert amanha != hoje
    fixo = Planejador(MULHER, regiao="Sudeste", variar=False)
    assert not any(o["novidade"] for o in fixo.opcoes("almoco")["opcoes"])


def test_uma_opcao_traz_novidade():
    c = Planejador(MULHER, regiao="Sudeste", data=date(2026, 11, 24))
    for ref in c.refeicoes:
        ops = c.opcoes(ref)
        if ops["avaliacao"].get("novidades_disponiveis"):
            assert any(o["novidade"] for o in ops["opcoes"]), ref


def test_sorteio_permite_aprender_o_que_nao_e_popular():
    """Sem sorteio, peixe nunca aparece no almoço do Sudeste; com sorteio aparece e o bandit aprende."""
    vistos = {}
    for variar in (False, True):
        c = Planejador(MULHER, regiao="Sudeste", variar=variar, data=date(2026, 11, 1))
        n = 0
        for _ in range(12):
            c.opcoes("almoco")
            sub = [next(i["subtipo"] for i in it if i["grupo"] == "proteina") for it in c.mostradas["almoco"].itens]
            n += sub.count("peixe")
            c.escolher("almoco", sub.index("peixe") if "peixe" in sub else 0)
            c.novo_dia()
        vistos[variar] = n
    assert vistos[False] == 0 and vistos[True] > 0
