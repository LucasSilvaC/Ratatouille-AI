"""
Testes do contrato de entrada (dados/entrada_planejador.schema.json): o schema é válido, os exemplos passam nele
e o planejador monta o dia com cada um.

    uv run pytest
"""
import json
from pathlib import Path

import jsonschema
import pytest

from ratatouille_recommendation import EntradaInvalida, ForaDoEscopo, Planejador
from ratatouille_recommendation.restricoes import RESTRICAO, TIPOS

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "src" / "ratatouille_recommendation" / "dados"
                     / "entrada_planejador.schema.json").read_text(encoding="utf-8"))


def test_schema_e_valido_e_bate_com_o_codigo():
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    assert SCHEMA["properties"]["restricoes"]["items"]["enum"] == list(RESTRICAO)
    assert SCHEMA["properties"]["nao_misturar"]["items"]["items"]["enum"] == list(TIPOS)


@pytest.mark.parametrize("entrada", SCHEMA["examples"])
def test_exemplos_passam_no_schema_e_montam_o_dia(entrada):
    jsonschema.validate(entrada, SCHEMA)
    dia = Planejador.da_entrada(entrada, variar=False).dia()
    assert all(len(r["opcoes"]) == 3 for r in dia["refeicoes"].values())
    assert dia["avisos"] == entrada.get("avisos", [])


def test_entradas_invalidas():
    base = SCHEMA["examples"][0]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**base, "restricoes": ["kosher"]}, SCHEMA)
    with pytest.raises(EntradaInvalida):
        Planejador.da_entrada({**base, "restricoes": ["kosher"]})
    with pytest.raises(ValueError, match="campos desconhecidos"):
        Planejador.da_entrada({**base, "gosta_de": ["peixe"]})
    with pytest.raises(ValueError, match="dados_dri"):
        Planejador.da_entrada({"regiao": "Sul"})
    with pytest.raises(ForaDoEscopo):
        Planejador.da_entrada({"dados_dri": {**base["dados_dri"], "idade": 16}})


def test_estado_do_bandit_volta():
    entrada = SCHEMA["examples"][0]
    p = Planejador.da_entrada(entrada)
    p.opcoes("almoco")
    p.escolher("almoco", 1)
    estado = json.loads(json.dumps(p.estado()))
    q = Planejador.da_entrada(entrada, estado_bandit=estado)
    assert q.explicar("almoco")[0].round(6).equals(p.explicar("almoco")[0].round(6))
