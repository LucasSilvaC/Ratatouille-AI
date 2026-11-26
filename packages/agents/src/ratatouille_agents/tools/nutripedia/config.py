"""Caminhos e configuração da Nutripédia.

Os PDFs e o índice ficam fora do Git, em packages/agents/data/nutripedia/.
A chave do Gemini vem da variável de ambiente GEMINI_API_KEY ou de infra/.env,
o arquivo de ambiente único do monorepo.
"""

import os
from pathlib import Path

# .../packages/agents/src/ratatouille_agents/tools/nutripedia/config.py
_PACOTE = Path(__file__).resolve().parents[4]
_RAIZ = _PACOTE.parents[1]

PASTA_DADOS = Path(os.environ.get("NUTRIPEDIA_DADOS", _PACOTE / "data" / "nutripedia"))
PASTA_PDFS = PASTA_DADOS / "pdfs"
PASTA_INDICE = PASTA_DADOS / "indice"
ARQUIVO_ENV = _RAIZ / "infra" / ".env"

MODELO_EMBEDDING = "paraphrase-multilingual-MiniLM-L12-v2"


def ler_env(caminho: Path) -> dict[str, str]:
    """Lê linhas CHAVE=valor de um arquivo .env, ignorando comentários e linhas vazias."""
    valores: dict[str, str] = {}
    if not caminho.exists():
        return valores
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        valores[chave.strip()] = valor.strip().strip('"').strip("'")
    return valores


def obter_chave_gemini(arquivo_env: Path = ARQUIVO_ENV) -> str | None:
    """Devolve a chave do Gemini do ambiente ou de infra/.env, ou None se não houver."""
    return os.environ.get("GEMINI_API_KEY") or ler_env(arquivo_env).get("GEMINI_API_KEY") or None
