"""
Testes da troca de alimento pelo mapa SOM (som.py e Planejador.substitutos/trocar).

    uv run pytest
"""
import re

from ratatouille_recommendation import Planejador
from ratatouille_recommendation.som import Substituidor

MULHER = dict(sexo="F", idade=30, altura_cm=163, peso_kg=62, atividade="pouco_ativo")


def test_mapa_carrega_e_acha_vizinhos():
    s = Substituidor()
    res = s.substituir("frango", n=5)
    assert len(res["substitutos"]) == 5
    assert all(len(x["codigo"]) == 6 for x in res["substitutos"])


def test_substitutos_e_troca_pelo_som():
    c = Planejador(MULHER, restricoes=["sem_lactose"], regiao="Sudeste", variar=False)
    c.opcoes("almoco")
    res = c.substitutos("almoco", 0, "proteina")
    original = c._mesmo_alimento(res["original"]["alimento"])
    assert res["substitutos"], "o SOM deveria achar substitutos"
    chaves = [c._mesmo_alimento(x["nome"]) for x in res["substitutos"]]
    assert original not in chaves and len(set(chaves)) == len(chaves)     # nem o próprio, nem repetidos
    antes = c.mostradas["almoco"].iloc[0]
    nova = c.trocar("almoco", 0, "proteina", res["substitutos"][0]["codigo"])
    assert nova["itens"][0]["alimento"] != antes.itens[0]["alimento"]
    assert abs(nova["totais"]["energia_kcal"] - antes.energia_kcal) < 0.15 * antes.energia_kcal
    assert c.mostradas["almoco"].iloc[0].motivo_veto is None
    c.escolher("almoco", 0)                                    # o bandit aprende com a opção trocada


def test_troca_respeita_restricao():
    c = Planejador(MULHER, restricoes=["vegetariano"], regiao="Nordeste")
    c.opcoes("almoco")
    for x in c.substitutos("almoco", 0, "proteina")["substitutos"]:
        assert not re.search(r"carne|frango|peixe|boi|porco|linguica", x["nome"].lower())
