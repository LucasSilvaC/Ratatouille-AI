# Clientes de LLM

Futuros adaptadores dos provedores de LLM: configuração de modelo, saídas estruturadas, streaming, limites, timeout, métricas e tratamento de erros. Chaves ficam no ambiente do backend. Sem SDK ou provedor instalado nesta etapa.

Status: estrutura planejada. Por enquanto, o único cliente de LLM é o `GeradorGemini` da Nutripédia, em `tools/nutripedia/resposta.py`; ele deve migrar para cá quando outro agente precisar do Gemini.
