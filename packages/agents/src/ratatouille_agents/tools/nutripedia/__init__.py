"""Nutripédia: RAG sobre a bibliografia de nutrição.

Busca trechos dos PDFs da bibliografia e pede ao Gemini uma resposta que use só esses
trechos, com as fontes citadas. É a base de conhecimento prevista para o Guardião
consultar doenças e alergias. A resposta é texto livre e não substitui as regras
obrigatórias de restrição alimentar, que precisam ficar em código.

Uso rápido:

    from ratatouille_agents.tools.nutripedia import criar_nutripedia, GeradorGemini, responder
    from ratatouille_agents.tools.nutripedia.config import obter_chave_gemini

    nutripedia = criar_nutripedia()
    resposta = responder(nutripedia, GeradorGemini(obter_chave_gemini()), "A aveia contém glúten?")
"""

from pathlib import Path

from . import config
from .busca import K, Nutripedia, Resultado
from .resposta import GeradorGemini, Resposta, responder
from .trechos import Trecho, carregar_ou_criar_indice

__all__ = [
    "K",
    "GeradorGemini",
    "Nutripedia",
    "Resposta",
    "Resultado",
    "Trecho",
    "carregar_modelo_embedding",
    "criar_nutripedia",
    "responder",
]


def carregar_modelo_embedding(nome: str = config.MODELO_EMBEDDING):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(nome)


def criar_nutripedia(pasta_pdfs: Path = config.PASTA_PDFS, pasta_indice: Path = config.PASTA_INDICE) -> Nutripedia:
    """Carrega o modelo de embeddings e o índice (criando-o a partir dos PDFs se preciso)."""
    modelo = carregar_modelo_embedding()
    trechos, vetores = carregar_ou_criar_indice(pasta_pdfs, pasta_indice, modelo)
    return Nutripedia(trechos, vetores, modelo)
