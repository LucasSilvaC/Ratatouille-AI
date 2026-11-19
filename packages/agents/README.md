# Agentes

Biblioteca Python para os agentes do RatatouilleAI (Guardião/NutriGuard, Planejador/Chef
Regional). API e worker importarão esta biblioteca. Workflows coordenam ferramentas, contexto
e respostas estruturadas. Restrições obrigatórias são aplicadas em código no pacote
recommendation; um parecer do LLM não substitui essa validação.

Status: **a Nutripédia (RAG sobre a bibliografia) está implementada** em
`src/ratatouille_agents/tools/nutripedia`, com testes e avaliação. Agentes, workflows e a
integração com a API ainda são planejados.

## Nutripédia

Busca trechos dos PDFs da bibliografia de nutrição e pede ao Gemini uma resposta que use
**apenas** esses trechos, citando a fonte (`[1]`, `[2]`...). Quando a bibliografia não cobre o
assunto, o modelo recusa responder. A saída traz o texto, o modelo usado e as fontes
(arquivo, página e similaridade com a pergunta).

1. Os PDFs são divididos em trechos de 500 caracteres, com 100 de sobreposição.
2. Os embeddings vêm de `paraphrase-multilingual-MiniLM-L12-v2` e ficam salvos em disco.
3. A busca é **híbrida**: vetorial + palavra-chave (BM25), combinadas por _Reciprocal Rank
   Fusion_. Os 5 melhores trechos vão para o modelo.
4. O Gemini responde, tentando `gemini-3.5-flash`, `gemini-3.5-flash-lite` e
   `gemini-3.1-flash-lite`, nessa ordem.

É a base de conhecimento prevista para o Guardião consultar doenças e alergias. Hoje a
resposta é texto livre: para o Guardião usá-la, falta uma saída estruturada (o que excluir,
o que limitar, fontes) e a lista de restrições críticas tratada em código.

### Instalar

Requer Python 3.11+. Na pasta `packages/agents`:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[rag,dev]"
```

O extra `rag` instala o PyTorch (via sentence-transformers) e é pesado. Os testes unitários
precisam só de `.[dev]`. Ainda não há lockfile do uv (ver `docs/architecture.md`).

### Configurar

1. Copie os PDFs da pasta do Drive do grupo para `data/nutripedia/pdfs/` (veja
   [a lista](data/nutripedia/README.md)). Eles não vão para o Git.
2. Coloque a chave do Google AI Studio em `infra/.env`, como `GEMINI_API_KEY=...` (o exemplo
   está em `infra/.env.example`). A variável de ambiente `GEMINI_API_KEY` tem prioridade.

Na primeira execução o índice é criado em `data/nutripedia/indice/` (cerca de 1 minuto).
Ao trocar os PDFs, apague essa pasta.

### Usar

```powershell
.venv\Scripts\nutripedia.exe                           # conversa no terminal
.venv\Scripts\nutripedia.exe "A aveia contém glúten?"  # uma pergunta
```

```python
from ratatouille_agents.tools.nutripedia import GeradorGemini, criar_nutripedia, responder
from ratatouille_agents.tools.nutripedia.config import obter_chave_gemini

nutripedia = criar_nutripedia()
resposta = responder(nutripedia, GeradorGemini(obter_chave_gemini()), "A aveia contém glúten?")
print(resposta.texto, resposta.recusou, [f.trecho.arquivo for f in resposta.fontes])
```

A pergunta e os trechos vão para o Google. Não coloque dados pessoais na pergunta.

### Testar e avaliar

```powershell
.venv\Scripts\python.exe -m pytest                                # unitários, sem rede
.venv\Scripts\python.exe evals\nutripedia\avaliar.py --so-busca   # acerto da busca, sem Gemini
.venv\Scripts\python.exe evals\nutripedia\avaliar.py              # avaliação completa
```

A avaliação usa as 36 perguntas de `evals/nutripedia/perguntas.json` (30 cobertas pela
bibliografia e 6 de fora) e gera relatório HTML, CSV e JSON em `evals/nutripedia/resultados/`.
Resultado da última execução completa:

| Verificação                            | Vetorial | Híbrida  |
| -------------------------------------- | -------- | -------- |
| Busca acerta o trecho (top 5)          | 77%      | **83%**  |
| Perguntas cobertas respondidas         | 23 de 30 | 26 de 30 |
| Respostas fiéis aos trechos (juiz LLM) | 22       | 23       |
| Perguntas de fora recusadas            | 6 de 6   | 6 de 6   |

Limitações conhecidas: o PDF de alimentos funcionais é escaneado e fica fora do índice; o
início de um trecho pode cair no meio de uma palavra (o fim nunca); e a bibliografia não cobre
suplementos, vitamina D nem fatores de risco do diabetes tipo 2.
