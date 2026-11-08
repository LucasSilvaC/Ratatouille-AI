# RatatouilleAI

Monorepo com o web-app Next.js existente e estrutura documentada para agentes LLM,
recomendação alimentar e rede neural em Python.

## Estrutura

| Pasta                     | Responsabilidade                              | Estado               |
| ------------------------- | --------------------------------------------- | -------------------- |
| `apps/web`                | Interface e backend Next.js, Drizzle e testes | Implementado         |
| `apps/ai-api`             | API Python/FastAPI                            | Somente documentação |
| `apps/ai-worker`          | Execução assíncrona e jobs                    | Somente documentação |
| `packages/agents`         | NutriGuard, Chef Regional e integração LLM    | Somente documentação |
| `packages/recommendation` | Políticas, busca, ranking e validação         | Somente documentação |
| `packages/neural`         | Treinamento e inferência de afinidade         | Somente documentação |
| `packages/ai-client`      | Cliente TypeScript gerado da API              | Somente documentação |
| `contracts`               | Contratos OpenAPI e eventos                   | Somente documentação |

Consulte [a arquitetura](docs/architecture.md) e os README.md de cada pasta.
As telas e integrações do wireframe ainda não foram implementadas neste repositório.

## Desenvolvimento

Requisitos: Node 24, pnpm 11 e Docker para PostgreSQL local. Na raiz:

```powershell
pnpm install
Copy-Item .env.example .env
Copy-Item apps/web/.env.example apps/web/.env.local
docker compose up -d postgres
$env:DATABASE_URL = "postgres://acrux:acrux@localhost:5432/acrux_template"
pnpm db:migrate
pnpm dev
```

`.env` da raiz configura o Compose. `apps/web/.env.local` configura o Next.js.
Se alterar as credenciais do banco, mantenha os dois arquivos consistentes.
Nunca commite segredos. O web-app abre em http://localhost:3000 e tem health check
em http://localhost:3000/api/health.

## Comandos

Execute pela raiz: `pnpm dev`, `pnpm build`, `pnpm start`, `pnpm lint`,
`pnpm typecheck`, `pnpm test:unit`, `pnpm test:coverage`, `pnpm test:e2e`,
`pnpm format` e `pnpm check`. Os comandos do web-app são delegados ao workspace
`@ratatouille/web`; a formatação verifica o monorepo inteiro.

Para E2E, instale o Chromium com
`pnpm --filter @ratatouille/web exec playwright install chromium`.

Banco: `pnpm db:generate`, `pnpm db:migrate`, `pnpm db:studio` e `pnpm db:seed`.
O Drizzle CLI e o seed precisam de `DATABASE_URL` no ambiente do processo; os comandos
Next.js carregam `apps/web/.env.local`. `db:push` é apenas para bancos descartáveis.
Schemas e migrações ficam em `apps/web/src/server/infrastructure/database/drizzle`
e `apps/web/drizzle`, respectivamente.

## Deploy

`docker compose up -d --build` aplica migrações e inicia o web-app. A imagem final
usa o servidor standalone em `apps/web/server.js`. Os serviços Python ainda não
fazem parte do Compose. Consulte [deploy e CI/CD](docs/deployment.md).

Na Vercel, configure Root Directory como `apps/web` e permita arquivos externos ao
Root Directory para acessar o workspace. A instalação usa o lockfile da raiz.

## Evolução

Primeiro implementar API e um fluxo de geração/troca com regras e contratos.
Depois conectar os agentes, jobs demorados e o preditor neural conforme existirem
dados e avaliações. Cada pasta reservada descreve seu objetivo e seus limites.

A base existente mantém Atomic Design na interface e Clean Architecture no backend.
Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para contribuição e commits.
