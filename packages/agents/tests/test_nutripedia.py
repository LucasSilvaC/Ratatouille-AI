"""Testes da Nutripédia que não precisam de rede, PDFs nem do modelo de embeddings."""

import numpy as np
import pytest

from ratatouille_agents.tools.nutripedia.busca import (
    IndiceDePalavras,
    Nutripedia,
    fundir_rankings,
    melhores,
    tokenizar,
)
from ratatouille_agents.tools.nutripedia.config import ler_env, obter_chave_gemini
from ratatouille_agents.tools.nutripedia.resposta import (
    FRASE_RECUSA,
    GeradorGemini,
    citou_fonte,
    eh_recusa,
    montar_prompt,
    responder,
)
from ratatouille_agents.tools.nutripedia.trechos import (
    Trecho,
    carregar_indice,
    dividir_em_trechos,
    salvar_indice,
)


class ModeloFalso:
    """Embedding de mentira: conta palavras de um vocabulário fixo e normaliza."""

    VOCABULARIO = ["gluten", "aveia", "diabetes", "insulina", "alergia", "amendoim"]

    def encode(self, texto, normalize_embeddings=True):
        palavras = tokenizar(texto)
        vetor = np.array([palavras.count(p) for p in self.VOCABULARIO], dtype=float) + 1e-6
        return vetor / np.linalg.norm(vetor)


TRECHOS = [
    Trecho("celiaca.pdf", 1, "A aveia pode conter gluten por contaminação cruzada no processamento."),
    Trecho("diabetes.pdf", 2, "O diabetes envolve a insulina e o controle da glicemia ao longo do dia."),
    Trecho("alergia.pdf", 3, "A alergia ao amendoim costuma persistir na vida adulta."),
    Trecho("guia.pdf", 4, "Prefira alimentos in natura e minimamente processados."),
]


@pytest.fixture
def nutripedia():
    modelo = ModeloFalso()
    vetores = np.array([modelo.encode(t.texto) for t in TRECHOS])
    return Nutripedia(TRECHOS, vetores, modelo)


# ---------- trechos ----------


def test_texto_curto_vira_um_trecho():
    assert dividir_em_trechos("arroz e feijão") == ["arroz e feijão"]


def test_trechos_respeitam_tamanho_e_se_sobrepoem():
    texto = " ".join(f"palavra{i}" for i in range(300))
    trechos = dividir_em_trechos(texto, tamanho=100, sobreposicao=20)
    assert len(trechos) > 1
    assert all(len(t) <= 100 for t in trechos)
    assert trechos[0].split()[-1] in trechos[1]  # a sobreposição repete o fim do trecho anterior
    assert trechos[-1].endswith("palavra299")


def test_fim_do_trecho_nao_parte_palavras():
    # Só o fim é cortado num espaço; o início do trecho seguinte (fim - sobreposição)
    # pode cair no meio de uma palavra. É o comportamento avaliado e usado no índice atual.
    texto = " ".join(["nutricao"] * 200)
    for trecho in dividir_em_trechos(texto, tamanho=100, sobreposicao=20):
        assert trecho.endswith("nutricao")


def test_indice_salvo_e_carregado(tmp_path):
    vetores = np.eye(len(TRECHOS))
    salvar_indice(tmp_path, TRECHOS, vetores)
    trechos, carregados = carregar_indice(tmp_path)
    assert trechos == TRECHOS
    assert np.array_equal(carregados, vetores)


def test_indice_ausente_devolve_none(tmp_path):
    assert carregar_indice(tmp_path / "nao-existe") is None


# ---------- busca ----------


def test_tokenizar_ignora_palavras_curtas_e_caixa():
    assert tokenizar("A Aveia é de 2 tipos") == ["aveia", "tipos"]


def test_melhores_ordena_e_desempata_pela_ordem_original():
    assert melhores(np.array([0.1, 0.9, 0.9, 0.5]), 3) == [1, 2, 3]


def test_bm25_prefere_o_trecho_com_a_palavra_rara():
    indice = IndiceDePalavras([t.texto for t in TRECHOS])
    pontuacoes = indice.pontuar("amendoim")
    assert int(np.argmax(pontuacoes)) == 2
    assert pontuacoes[0] == 0


def test_bm25_sem_palavras_conhecidas_da_zero():
    indice = IndiceDePalavras([t.texto for t in TRECHOS])
    assert not indice.pontuar("xyz qwerty").any()


def test_fusao_premia_quem_aparece_nos_dois_rankings():
    pontos = fundir_rankings([0, 1, 2], [2, 3, 0])
    assert max(pontos, key=pontos.get) in (0, 2)
    assert pontos[0] > pontos[1] and pontos[2] > pontos[3]


def test_buscas_encontram_o_trecho_certo(nutripedia):
    for buscar in (nutripedia.buscar_vetorial, nutripedia.buscar_palavras, nutripedia.buscar_hibrida):
        resultados = buscar("A aveia tem gluten?", 2)
        assert resultados[0].trecho.arquivo == "celiaca.pdf"
        assert 0.0 <= resultados[0].similaridade <= 1.0 + 1e-9


def test_hibrida_devolve_k_resultados_sem_repetir(nutripedia):
    resultados = nutripedia.buscar_hibrida("insulina e diabetes", k=3)
    assert len(resultados) == 3
    assert len({r.indice for r in resultados}) == 3


def test_trechos_e_vetores_precisam_combinar():
    with pytest.raises(ValueError):
        Nutripedia(TRECHOS, np.zeros((2, 6)), ModeloFalso())


# ---------- resposta ----------


def test_prompt_numera_trechos_com_fonte(nutripedia):
    prompt = montar_prompt("A aveia tem gluten?", nutripedia.buscar_hibrida("aveia gluten", 2))
    assert "[1] (celiaca.pdf, página 1)" in prompt
    assert "[2] (" in prompt
    assert FRASE_RECUSA in prompt
    assert prompt.rstrip().endswith("RESPOSTA:")


@pytest.mark.parametrize(
    "texto, esperado",
    [
        (f"Desculpe, {FRASE_RECUSA}.", True),
        ("A bibliografia consultada não traz essa informação.", True),
        ("A aveia pode conter glúten [1].", False),
    ],
)
def test_detecta_recusa(texto, esperado):
    assert eh_recusa(texto) is esperado


def test_detecta_citacao():
    assert citou_fonte("Sim, contém [2][4].")
    assert not citou_fonte("Sim, contém.")


class _Resposta:
    def __init__(self, text):
        self.text = text


class ClienteFalso:
    """Imita genai.Client: falha nos modelos indicados e responde no primeiro que sobrar."""

    def __init__(self, falhas):
        self.falhas = falhas
        self.chamados = []
        self.models = self

    def generate_content(self, model, contents):
        self.chamados.append(model)
        if model in self.falhas:
            raise RuntimeError(self.falhas[model])
        return _Resposta(f"Resposta de {model} [1]")


def test_gerador_usa_o_proximo_modelo_e_tira_o_que_estourou_a_cota():
    cliente = ClienteFalso({"a": "429 RESOURCE_EXHAUSTED"})
    gerador = GeradorGemini(cliente=cliente, modelos=["a", "b"], pausa=0)
    texto, modelo = gerador.gerar("oi")
    assert modelo == "b" and "b" in texto
    assert gerador.modelos == ["b"]


def test_gerador_desiste_depois_das_tentativas():
    cliente = ClienteFalso({"a": "500", "b": "timeout"})
    gerador = GeradorGemini(cliente=cliente, modelos=["a", "b"], tentativas=2, pausa=0)
    with pytest.raises(RuntimeError):
        gerador.gerar("oi")
    assert cliente.chamados == ["a", "b", "a", "b"]


def test_gerador_sem_chave_avisa():
    with pytest.raises(ValueError):
        GeradorGemini(chave=None)


def test_responder_devolve_texto_modelo_e_fontes(nutripedia):
    gerador = GeradorGemini(cliente=ClienteFalso({}), modelos=["m"], pausa=0)
    resposta = responder(nutripedia, gerador, "A aveia tem gluten?", k=2)
    assert resposta.modelo == "m"
    assert resposta.citou_fonte and not resposta.recusou
    assert len(resposta.fontes) == 2
    assert resposta.fontes[0].trecho.arquivo == "celiaca.pdf"


# ---------- configuração ----------


def test_ler_env_ignora_comentarios_e_aspas(tmp_path):
    arquivo = tmp_path / ".env"
    arquivo.write_text('# comentário\n\nPOSTGRES_DB=x\nGEMINI_API_KEY="abc"\n', encoding="utf-8")
    assert ler_env(arquivo) == {"POSTGRES_DB": "x", "GEMINI_API_KEY": "abc"}


def test_chave_do_ambiente_tem_prioridade(tmp_path, monkeypatch):
    arquivo = tmp_path / ".env"
    arquivo.write_text("GEMINI_API_KEY=do-arquivo\n", encoding="utf-8")
    monkeypatch.setenv("GEMINI_API_KEY", "do-ambiente")
    assert obter_chave_gemini(arquivo) == "do-ambiente"
    monkeypatch.delenv("GEMINI_API_KEY")
    assert obter_chave_gemini(arquivo) == "do-arquivo"
    assert obter_chave_gemini(tmp_path / "nao-existe") is None
