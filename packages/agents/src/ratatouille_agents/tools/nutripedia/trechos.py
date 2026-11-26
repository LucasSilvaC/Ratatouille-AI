"""Leitura dos PDFs, divisão em trechos e índice de embeddings guardado em disco."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

TAMANHO = 500
SOBREPOSICAO = 100
MINIMO = 50  # páginas e trechos com menos caracteres são descartados


@dataclass(frozen=True)
class Trecho:
    arquivo: str
    pagina: int
    texto: str


def dividir_em_trechos(texto: str, tamanho: int = TAMANHO, sobreposicao: int = SOBREPOSICAO) -> list[str]:
    """Divide o texto em trechos de até `tamanho` caracteres que se sobrepõem.

    O corte é feito no último espaço da segunda metade do trecho, para não partir palavras.
    """
    trechos = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        if fim < len(texto):
            espaco = texto.rfind(" ", inicio + tamanho // 2, fim)
            if espaco != -1:
                fim = espaco
        trechos.append(texto[inicio:fim].strip())
        if fim >= len(texto):
            break
        inicio = fim - sobreposicao
    return trechos


def ler_pdfs(pasta: Path) -> list[Trecho]:
    """Lê todos os PDFs da pasta. PDFs escaneados (sem texto) ficam de fora, com aviso."""
    from pypdf import PdfReader

    arquivos = sorted(pasta.glob("*.pdf"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum PDF encontrado em {pasta}")
    trechos = []
    for caminho in arquivos:
        com_texto = 0
        for numero, pagina in enumerate(PdfReader(caminho).pages, start=1):
            texto = " ".join((pagina.extract_text() or "").split())
            if len(texto) < MINIMO:
                continue
            com_texto += 1
            trechos.extend(
                Trecho(caminho.name, numero, pedaco)
                for pedaco in dividir_em_trechos(texto)
                if len(pedaco) >= MINIMO
            )
        aviso = "  (sem texto: PDF escaneado, ficou de fora)" if com_texto == 0 else ""
        print(f"  {com_texto:4d} páginas | {caminho.name}{aviso}")
    return trechos


def salvar_indice(pasta: Path, trechos: list[Trecho], vetores: np.ndarray) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    np.save(pasta / "vetores.npy", vetores)
    with open(pasta / "trechos.json", "w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in trechos], f, ensure_ascii=False)


def carregar_indice(pasta: Path) -> tuple[list[Trecho], np.ndarray] | None:
    arq_vetores, arq_trechos = pasta / "vetores.npy", pasta / "trechos.json"
    if not (arq_vetores.exists() and arq_trechos.exists()):
        return None
    with open(arq_trechos, encoding="utf-8") as f:
        trechos = [Trecho(**t) for t in json.load(f)]
    return trechos, np.load(arq_vetores)


def carregar_ou_criar_indice(pasta_pdfs: Path, pasta_indice: Path, modelo) -> tuple[list[Trecho], np.ndarray]:
    """Usa o índice salvo; se não existir, lê os PDFs, calcula os embeddings e salva.

    Ao trocar os PDFs, apague a pasta do índice para que ele seja recriado.
    """
    salvo = carregar_indice(pasta_indice)
    if salvo is not None:
        return salvo
    print("Primeira execução: lendo os PDFs e criando o índice (leva cerca de 1 minuto)...")
    trechos = ler_pdfs(pasta_pdfs)
    vetores = modelo.encode([t.texto for t in trechos], normalize_embeddings=True, show_progress_bar=True)
    salvar_indice(pasta_indice, trechos, vetores)
    return trechos, vetores
