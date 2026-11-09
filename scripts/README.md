# Automação do monorepo

Diretório reservado para automações de manutenção e geração, como exportar OpenAPI e
gerar o cliente TypeScript. Não coloque aqui configuração de ambiente, Compose, setup
ou inicialização de serviços; esse fluxo é centralizado em [`infra/`](../infra/README.md).

Os comandos de desenvolvimento, banco, testes e build são atalhos no `package.json`
da raiz. A lógica de ambiente e Compose fica em `infra/scripts/`.

Status: estrutura planejada; sem automações de geração nesta etapa.
