"""Prompt, geração com o Gemini e resposta com fontes."""

import re
import time
from dataclasses import dataclass

from .busca import K, Nutripedia, Resultado

FRASE_RECUSA = "a bibliografia consultada não cobre o assunto"

# Ordem de tentativa. Se um modelo falhar, o próximo é usado.
MODELOS = ("gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite")


def montar_prompt(pergunta: str, resultados: list[Resultado]) -> str:
    contexto = "\n\n".join(
        f"[{numero}] ({r.trecho.arquivo}, página {r.trecho.pagina})\n{r.trecho.texto}"
        for numero, r in enumerate(resultados, start=1)
    )
    return f"""Você é um assistente de nutrição. Responda à pergunta usando APENAS os trechos abaixo.

Regras:
- Se os trechos não trouxerem a resposta, diga que {FRASE_RECUSA}. Não use conhecimento de fora.
- Cite os trechos que usou pelo número entre colchetes, por exemplo [1] ou [2][4].
- Responda em português, de forma clara e direta.

TRECHOS:
{contexto}

PERGUNTA: {pergunta}

RESPOSTA:"""


def eh_recusa(texto: str) -> bool:
    """O modelo disse que a bibliografia não tem a resposta?

    O modelo às vezes varia a frase pedida ("não traz", "não aborda"), por isso
    procuramos só o começo dela.
    """
    texto = texto.lower()
    return "bibliografia consultada não" in texto or "não cobre" in texto


def citou_fonte(texto: str) -> bool:
    return re.search(r"\[\d+\]", texto) is not None


class GeradorGemini:
    """Chama o Gemini tentando os modelos em ordem.

    Um modelo que estoura a cota (erro 429) sai da fila desta instância, desde que
    sobre outro para tentar.
    """

    def __init__(self, chave: str | None = None, modelos=MODELOS, tentativas: int = 3, pausa: float = 5, cliente=None):
        if cliente is None:
            if not chave:
                raise ValueError("Defina GEMINI_API_KEY em infra/.env ou no ambiente.")
            from google import genai

            cliente = genai.Client(api_key=chave, http_options={"timeout": 30000})
        self.cliente = cliente
        self.modelos = list(modelos)
        self.tentativas = tentativas
        self.pausa = pausa

    def gerar(self, prompt: str) -> tuple[str, str]:
        """Devolve (texto, modelo usado)."""
        for _ in range(self.tentativas):
            for modelo in list(self.modelos):
                try:
                    resposta = self.cliente.models.generate_content(model=modelo, contents=prompt)
                    if resposta.text:
                        return resposta.text, modelo
                except Exception as erro:  # o SDK lança tipos variados para rede, cota e timeout
                    if "429" in str(erro) and len(self.modelos) > 1:
                        self.modelos.remove(modelo)
                    print(f"   ({modelo} não respondeu: {str(erro)[:60]})")
            time.sleep(self.pausa)
        raise RuntimeError("Nenhum modelo respondeu. Tente de novo em alguns minutos.")


@dataclass(frozen=True)
class Resposta:
    texto: str
    modelo: str
    fontes: list[Resultado]

    @property
    def recusou(self) -> bool:
        return eh_recusa(self.texto)

    @property
    def citou_fonte(self) -> bool:
        return citou_fonte(self.texto)


def responder(nutripedia: Nutripedia, gerador: GeradorGemini, pergunta: str, k: int = K, busca: str = "hibrida") -> Resposta:
    """Busca os trechos, pede a resposta ao modelo e devolve o texto com as fontes usadas.

    `busca` é "hibrida" (padrão, a melhor na avaliação), "vetorial" ou "palavras".
    Não envie dados pessoais na pergunta: ela vai para o provedor do modelo.
    """
    buscar = {
        "hibrida": nutripedia.buscar_hibrida,
        "vetorial": nutripedia.buscar_vetorial,
        "palavras": nutripedia.buscar_palavras,
    }[busca]
    fontes = buscar(pergunta, k)
    texto, modelo = gerador.gerar(montar_prompt(pergunta, fontes))
    return Resposta(texto.strip(), modelo, fontes)
