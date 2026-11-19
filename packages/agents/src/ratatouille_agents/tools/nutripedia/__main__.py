"""Conversa com a Nutripédia no terminal.

    nutripedia                       conversa interativa
    nutripedia "sua pergunta aqui"   responde uma pergunta e sai

(ou `python -m ratatouille_agents.tools.nutripedia`)
"""

import getpass
import logging
import os
import sys

from . import GeradorGemini, criar_nutripedia, responder
from .config import obter_chave_gemini


def _silenciar_avisos() -> None:
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    for nome in ("pypdf", "huggingface_hub", "sentence_transformers"):
        logging.getLogger(nome).setLevel(logging.ERROR)


def _mostrar(resposta) -> None:
    print(f"\nRESPOSTA ({resposta.modelo}):")
    print(resposta.texto)
    print("\nFONTES CONSULTADAS (similaridade com a pergunta, de 0 a 1):")
    for numero, r in enumerate(resposta.fontes, start=1):
        print(f"  [{numero}] similaridade {r.similaridade:.2f} | {r.trecho.arquivo} - pág. {r.trecho.pagina}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    _silenciar_avisos()

    print("Carregando o modelo de embeddings...")
    nutripedia = criar_nutripedia()
    arquivos = {t.arquivo for t in nutripedia.trechos}
    print(f"Índice pronto: {len(nutripedia.trechos)} trechos de {len(arquivos)} PDFs.")

    chave = obter_chave_gemini() or getpass.getpass(
        "Cole a sua chave do Gemini e aperte Enter (ela não aparece na tela): "
    ).strip()
    if not chave:
        sys.exit("Sem chave do Gemini não dá para gerar respostas.")
    gerador = GeradorGemini(chave)

    if len(sys.argv) > 1:
        _mostrar(responder(nutripedia, gerador, " ".join(sys.argv[1:])))
        return

    print("\nFaça perguntas sobre a bibliografia de nutrição. Digite sair para encerrar.")
    while True:
        try:
            pergunta = input("\nSua pergunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté mais!")
            break
        if pergunta.lower() in ("", "sair"):
            print("Até mais!")
            break
        try:
            _mostrar(responder(nutripedia, gerador, pergunta))
        except Exception as erro:
            print(f"Não consegui responder agora: {erro}")
        print("-" * 70)


if __name__ == "__main__":
    main()
