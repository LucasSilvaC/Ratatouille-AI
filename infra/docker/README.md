# Imagens Docker

As imagens são definidas em `Dockerfile`, com etapas `migrator`, `builder` e
`runner`. O contexto de build é a raiz do monorepo; a orquestração e a configuração
de ambiente ficam em [`infra/`](../README.md).

Adicione novas imagens e etapas neste diretório e conecte cada serviço em
`infra/compose.yaml`. Consulte o [guia de infraestrutura](../README.md) antes de
adicionar outro ponto de inicialização.
