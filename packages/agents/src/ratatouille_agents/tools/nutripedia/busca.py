"""Busca vetorial, por palavra-chave (BM25) e híbrida (fusão de rankings) sobre os trechos."""

import math
import re
from collections import Counter
from dataclasses import dataclass

import numpy as np

from .trechos import Trecho

K = 5  # trechos enviados ao modelo; foi a melhor configuração na avaliação
CANDIDATOS = 20  # quantos resultados de cada busca entram na fusão
CONSTANTE_RRF = 60


@dataclass(frozen=True)
class Resultado:
    trecho: Trecho
    indice: int
    pontuacao: float  # pontuação da busca que produziu o resultado
    similaridade: float  # cosseno entre a pergunta e o trecho, de 0 a 1


def tokenizar(texto: str) -> list[str]:
    return [p for p in re.findall(r"\w+", texto.lower()) if len(p) >= 3]


def melhores(pontuacoes: np.ndarray, k: int) -> list[int]:
    """Índices das k maiores pontuações, da maior para a menor (empates mantêm a ordem original)."""
    return [int(i) for i in np.argsort(-pontuacoes, kind="stable")[:k]]


class IndiceDePalavras:
    """BM25: pontua os trechos pelas palavras da pergunta, valorizando as palavras raras."""

    def __init__(self, textos: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.contagens = [Counter(tokenizar(t)) for t in textos]
        self.tamanhos = [sum(c.values()) for c in self.contagens]
        self.tamanho_medio = (sum(self.tamanhos) / len(self.tamanhos)) if self.tamanhos else 0.0
        self.trechos_com_a_palavra: Counter[str] = Counter()
        for contagem in self.contagens:
            self.trechos_com_a_palavra.update(contagem.keys())

    def pontuar(self, consulta: str) -> np.ndarray:
        total = len(self.contagens)
        pontuacoes = np.zeros(total)
        for palavra in set(tokenizar(consulta)):
            n = self.trechos_com_a_palavra.get(palavra, 0)
            if n == 0:
                continue
            idf = math.log(1 + (total - n + 0.5) / (n + 0.5))
            for i, contagem in enumerate(self.contagens):
                f = contagem.get(palavra, 0)
                if f == 0:
                    continue
                ajuste_tamanho = 1 - self.b + self.b * self.tamanhos[i] / self.tamanho_medio
                pontuacoes[i] += idf * f * (self.k1 + 1) / (f + self.k1 * ajuste_tamanho)
        return pontuacoes


def fundir_rankings(*rankings: list[int], constante: int = CONSTANTE_RRF) -> dict[int, float]:
    """Reciprocal Rank Fusion: cada ranking soma 1 / (constante + posição) ao trecho."""
    pontos: dict[int, float] = {}
    for ranking in rankings:
        for posicao, indice in enumerate(ranking, start=1):
            pontos[indice] = pontos.get(indice, 0.0) + 1 / (constante + posicao)
    return pontos


class Nutripedia:
    """Busca na bibliografia de nutrição.

    `modelo` é qualquer objeto com `encode(texto, normalize_embeddings=True)`, como um
    SentenceTransformer. `vetores` são os embeddings normalizados dos trechos, na mesma ordem.
    """

    def __init__(self, trechos: list[Trecho], vetores: np.ndarray, modelo):
        if len(trechos) != len(vetores):
            raise ValueError("O número de trechos e de vetores precisa ser o mesmo.")
        self.trechos = trechos
        self.vetores = vetores
        self.modelo = modelo
        self.palavras = IndiceDePalavras([t.texto for t in trechos])

    def _vetor(self, consulta: str) -> np.ndarray:
        return self.modelo.encode(consulta, normalize_embeddings=True)

    def _resultados(self, indices: list[int], pontuacoes, vetor: np.ndarray) -> list[Resultado]:
        return [
            Resultado(self.trechos[i], i, float(pontuacoes[i]), float(self.vetores[i] @ vetor))
            for i in indices
        ]

    def buscar_vetorial(self, consulta: str, k: int = K) -> list[Resultado]:
        vetor = self._vetor(consulta)
        pontuacoes = self.vetores @ vetor
        return self._resultados(melhores(pontuacoes, k), pontuacoes, vetor)

    def buscar_palavras(self, consulta: str, k: int = K) -> list[Resultado]:
        pontuacoes = self.palavras.pontuar(consulta)
        return self._resultados(melhores(pontuacoes, k), pontuacoes, self._vetor(consulta))

    def buscar_hibrida(self, consulta: str, k: int = K, candidatos: int = CANDIDATOS) -> list[Resultado]:
        vetor = self._vetor(consulta)
        por_vetor = melhores(self.vetores @ vetor, candidatos)
        por_palavra = melhores(self.palavras.pontuar(consulta), candidatos)
        pontos = fundir_rankings(por_vetor, por_palavra)
        escolhidos = sorted(pontos, key=pontos.get, reverse=True)[:k]
        return self._resultados(escolhidos, pontos, vetor)
