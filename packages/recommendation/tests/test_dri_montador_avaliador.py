"""
Testes da calculadora DRI, do Montador e do Avaliador.

    uv run pytest
"""
import json

import numpy as np
import pytest

from ratatouille_recommendation.avaliador import AvaliadorIngredientes
from ratatouille_recommendation.dri import REPARTICAO, ForaDoEscopo, calcular_dri
from ratatouille_recommendation.montador import MontadorIngredientes

MULHER = dict(sexo="F", idade=30, altura_cm=163, peso_kg=62, atividade="pouco_ativo")
HOMEM = dict(sexo="M", idade=35, altura_cm=175, peso_kg=78, atividade="ativo")


# ---------------------------------------------------------------- calculadora DRI
def test_eer_confere_com_a_tabela_s1():
    # mulher, pouco ativa: 575,77 − 7,01·30 + 6,60·163 + 12,14·62
    assert calcular_dri(**MULHER)["dia"]["energia_kcal"] == round(575.77 - 7.01 * 30 + 6.60 * 163 + 12.14 * 62)
    # homem, ativo: 1004,82 − 10,83·35 + 6,52·175 + 15,91·78
    assert calcular_dri(**HOMEM)["dia"]["energia_kcal"] == round(1004.82 - 10.83 * 35 + 6.52 * 175 + 15.91 * 78)


def test_macros_dentro_das_faixas():
    m = calcular_dri(**MULHER)
    kcal, d = m["dia"]["energia_kcal"], m["dia"]
    assert d["proteina_g"]["meta"] >= d["proteina_g"]["rda"] == round(0.8 * 62, 1)
    assert d["proteina_g"]["min"] <= d["proteina_g"]["meta"] <= d["proteina_g"]["max"]
    assert d["carboidrato_g"]["min"] <= d["carboidrato_g"]["meta"] <= d["carboidrato_g"]["max"]
    assert d["fibra_g"] == round(14 * kcal / 1000, 1)
    assert abs(sum(REPARTICAO.values()) - 1) < 1e-9
    assert sum(r["energia_kcal"] for r in m["refeicoes"].values()) == pytest.approx(kcal, abs=3)


def test_anjos_tmb_vezes_naf():
    # mulher, pouco ativa: TMB = 8,95·62 + 8,87·163 − 0,70·30 − 814,3 ≈ 1165 kcal; × NAF 1,55 ≈ 1806 kcal
    m = calcular_dri(**MULHER, metodo="anjos")
    tmb = 8.95 * 62 + 8.87 * 163 - 0.70 * 30 - 814.3
    assert m["dia"]["tmb_kcal"] == round(tmb) == 1165
    assert m["dia"]["naf"] == 1.55
    assert m["dia"]["energia_kcal"] == round(tmb * 1.55) == 1806
    assert m["metodo"] == "anjos" and "Anjos" in m["fonte"]
    # homem, ativo: TMB = 9,99·78 + 7,14·175 − 2,79·35 − 450,5; × NAF 1,75
    assert calcular_dri(**HOMEM, metodo="anjos")["dia"]["energia_kcal"] == round(
        (9.99 * 78 + 7.14 * 175 - 2.79 * 35 - 450.5) * 1.75)


def test_anjos_da_menos_que_a_dri_e_mostra_os_dois():
    for perfil in (MULHER, HOMEM):
        dri, anjos = calcular_dri(**perfil), calcular_dri(**perfil, metodo="anjos")
        assert anjos["dia"]["energia_kcal"] < dri["dia"]["energia_kcal"]
        assert dri["dia"]["energia_por_metodo"] == anjos["dia"]["energia_por_metodo"]
        # macros e refeições continuam saindo da energia escolhida
        assert anjos["dia"]["fibra_g"] == round(14 * anjos["dia"]["energia_kcal"] / 1000, 1)
    with pytest.raises(ValueError):
        calcular_dri(**MULHER, metodo="outro")


@pytest.mark.parametrize("extra", [{"idade": 17}, {"gestante": True}, {"amamentando": True}])
def test_fora_do_escopo(extra):
    with pytest.raises(ForaDoEscopo):
        calcular_dri(**{**MULHER, **extra})


# ---------------------------------------------------------------- Montador e Avaliador
@pytest.fixture(scope="module")
def metas():
    return calcular_dri(**MULHER)["refeicoes"]


def test_montador_bate_a_energia_e_a_proteina(metas):
    df = MontadorIngredientes(regiao="Nordeste").combinacoes("almoco", metas["almoco"])
    assert len(df) > 100
    assert np.median(np.abs(df.desvio_energia)) < 0.10
    prot = df.proteina_g / metas["almoco"]["proteina_g"]
    assert (prot >= 0.95).mean() > 0.8                           # a meta de proteína é um mínimo
    assert all(len(it) == 5 and all(i["gramas"] % 5 == 0 for i in it) for it in df.itens)


def test_trava_vegetariano_e_nao_gosta(metas):
    m = MontadorIngredientes(regiao="Sudeste")
    av = AvaliadorIngredientes(restricoes=["vegetariano"], nao_gosta=["tomate"])
    # sem as restrições, o Montador monta para todos os alimentos e o Avaliador veta os proibidos
    df = m.combinacoes("almoco", metas["almoco"])
    _, resumo = av.tres_opcoes(df, "almoco", metas["almoco"])
    assert resumo["vetadas"] > 0
    # com as restrições, o Montador só monta com o que a pessoa pode comer (é o que o Cronograma faz)
    df = m.combinacoes("almoco", metas["almoco"], vetar_item=av._veto_item)
    ops, resumo = av.tres_opcoes(df, "almoco", metas["almoco"])
    assert len(ops) == 3
    for itens in ops.itens:
        for i in itens:
            assert "tomate" not in i["alimento"].lower()
            if i["grupo"] == "proteina":
                assert i["subtipo"] in ("leguminosa", "ovo", "leite", "queijo", "iogurte", "outro")


def test_tres_opcoes_variadas(metas):
    df = MontadorIngredientes(regiao="Nordeste").combinacoes("almoco", metas["almoco"])
    ops, _ = AvaliadorIngredientes().tres_opcoes(df, "almoco", metas["almoco"])
    cods = list(ops.codigos)
    assert all(len(cods[i] - cods[j]) >= 2 for i in range(3) for j in range(3) if i != j)


def test_bandit_aprende_o_gosto(metas):
    """Pessoa que sempre escolhe a opção com frango: o peso aprendido de aves fica positivo e acima de boi e porco.
    (Antes o teste usava leguminosa e passava por um erro: "óleo de soja" marcava carne frita como leguminosa.)"""
    df = MontadorIngredientes(regiao="Nordeste").combinacoes("almoco", metas["almoco"])
    av = AvaliadorIngredientes()
    for _ in range(15):
        ops, _ = av.tres_opcoes(df, "almoco", metas["almoco"])
        tem = [any(i["grupo"] == "proteina" and i["subtipo"] == "aves" for i in it) for it in ops.itens]
        av.registrar_escolha("almoco", ops, tem.index(True) if any(tem) else 0)
    theta, _ = av.explicar("almoco", top=100)
    assert theta["proteina:aves"] > 0
    assert theta["proteina:aves"] > max(theta["proteina:boi"], theta["proteina:porco"])
    estado = av.estado()
    novo = AvaliadorIngredientes()
    novo.carregar(json.loads(json.dumps(estado)))
    assert np.allclose(novo.modelos["almoco"][1], av.modelos["almoco"][1])


def test_montador_respeita_as_restricoes_do_prato(metas):
    """Energia na meta, proteína acima do mínimo da DRI, macronutrientes nas faixas e frutas e legumes
    acima do mínimo da OMS, depois do arredondamento (folga de 2%)."""
    from ratatouille_recommendation.montador import FAIXAS_MACRO, FLV_DIA_G, GRUPOS_FLV, proteina_minima
    m = MontadorIngredientes(regiao="Brasil")
    for refeicao, mt in metas.items():
        df = m.combinacoes(refeicao, mt)
        assert len(df) > 0 and df.attrs["nivel_restricoes"] == 1
        assert (df.desvio_energia.abs() <= 0.05).all()
        assert (df.proteina_g >= 0.98 * proteina_minima(mt) - 0.05).all()
        for c, (mn, mx, kc) in FAIXAS_MACRO.items():
            frac = kc * df[c] / df.energia_kcal
            assert frac.between(mn - 0.021, mx + 0.021).all(), c
        flv = df.itens.map(lambda it: sum(i["gramas"] for i in it if i["grupo"] in GRUPOS_FLV))
        assert (flv >= 0.98 * FLV_DIA_G * mt["fracao"] - 5).all()
        assert all(MontadorIngredientes.fora_das_restricoes(df.iloc[i], mt) == "" for i in range(0, len(df), 50))


def test_montador_relaxa_quando_nada_cabe(metas):
    mt = dict(metas["almoco"], proteina_g_min=500)           # mínimo impossível: nenhuma combinação cabe
    df = MontadorIngredientes(regiao="Brasil").combinacoes("almoco", mt)
    assert df.attrs["nivel_restricoes"] == 3 and len(df) > 0
