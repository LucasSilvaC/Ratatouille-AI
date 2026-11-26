# RatatouilleAI

<img src="apps/web/public/brand/ratatouille-ai.svg" alt="Logo do RatatouilleAI: silhueta de Remy com touca de chef" width="112" height="112" />

Monorepo com web-app Next.js, API Django, Nutripédia RAG para linha de comando e
módulos iniciais de recomendação alimentar, além de estruturas para capacidades futuras de IA.

## Estrutura

| Pasta                            | Responsabilidade                                                              | Estado                          |
| -------------------------------- | ----------------------------------------------------------------------------- | ------------------------------- |
| `apps/web`                       | Interface e backend Next.js, Drizzle e testes                                 | Implementado                    |
| [`apps/api`](apps/api/README.md) | API Django REST Framework para autenticação, alimentos, perguntas e respostas | Implementado                    |
| `apps/ai-api`                    | API Python/FastAPI                                                            | Somente documentação            |
| `apps/ai-worker`                 | Execução assíncrona e jobs                                                    | Somente documentação            |
| `packages/agents`                | Nutripédia RAG para CLI; demais agentes ainda planejados                         | Parcial                          |
| `packages/recommendation`        | Módulos Python de restrições, planejamento e avaliação de planos                 | Inicial, sem integração ao app   |
| `packages/neural`                | Treinamento e inferência de afinidade                                         | Somente documentação            |
| `packages/ai-client`             | Cliente TypeScript gerado da API                                              | Somente documentação            |
| `contracts`                      | Contratos OpenAPI e eventos                                                   | Somente documentação            |
| `infra`                          | Inicialização, Docker, Compose e configuração operacional                     | Implementado para o stack atual |

Consulte [a arquitetura](docs/architecture.md), o [guia de infraestrutura](infra/README.md)
e os README.md de cada pasta. Toda inicialização de serviços deve ser centralizada em
`infra/`; consulte o guia antes de adicionar novos componentes.
As telas do protótipo estão implementadas com dados locais demonstrativos: onboarding,
calendário, edição de perfil e revisões de propostas. Não há integração de IA ou
validação clínica. Veja [a arquitetura frontend e os cenários mockados](docs/frontend-demo.md).

Para abrir apenas a demonstração, execute `pnpm install` e `pnpm dev`, depois acesse
http://localhost:3000. A galeria fica em `/componentes`. Esse fluxo não exige banco
ou variáveis de ambiente. Os dados são mantidos em memória e reiniciam ao recarregar.

## Desenvolvimento

O código da API Django fica em `apps/api/apps/`. As views estão em
[`accounts/`](apps/api/apps/accounts/views.py), [`foods/`](apps/api/apps/foods/views.py)
e [`diagnosis/`](apps/api/apps/diagnosis/views.py). A API usa o ORM do Django com
uma base PostgreSQL dedicada. Siga o [README da API Django](apps/api/README.md)
para preparar as dependências e provisionar o banco. Depois, execute pela raiz:

```powershell
node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py migrate
node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py seed_catalog
node infra/scripts/with-env.mjs apps/api/env/Scripts/python.exe apps/api/manage.py runserver
```

`migrate` cria as tabelas no PostgreSQL e aplica as migrações pendentes. `seed_catalog`
carrega o catálogo inicial quando suas tabelas estão vazias. Veja a
[referência do banco Django](infra/database/README.md).

Requisitos: Node 24, pnpm 11 e Docker Compose. Para subir todo o stack implementado em um comando, execute pela raiz:

```powershell
pnpm infra:up
```

O Compose constrói as imagens, inicializa o banco, aplica migrações e inicia o app.
Essa etapa instala as dependências dentro da imagem, sem exigir `pnpm install` na
máquina. Os padrões funcionam sem arquivo de ambiente; copie `infra/.env.example`
para `infra/.env` se quiser ajustar portas ou credenciais.
Para desenvolver o Next.js diretamente na máquina, use:

```powershell
pnpm install
Copy-Item infra/.env.example infra/.env
pnpm infra:db
pnpm db:migrate
pnpm dev
```

`infra/.env` é a única configuração local compartilhada pelo Compose e pelos comandos
de desenvolvimento e banco da raiz. Nunca commite segredos. O web-app abre em
http://localhost:3000 e tem health check em http://localhost:3000/api/health.

## Comandos

Execute pela raiz:

- Infraestrutura: `pnpm infra:up`, `pnpm infra:db`, `pnpm infra:down`,
  `pnpm infra:down:volumes`, `pnpm infra:ps` e `pnpm infra:logs`.
- App: `pnpm dev`, `pnpm build` e `pnpm start`.
- Qualidade: `pnpm lint`, `pnpm typecheck`, `pnpm test:unit`,
  `pnpm test:coverage`, `pnpm test:e2e`, `pnpm format` e `pnpm check`.

Os comandos de execução, E2E e banco carregam `infra/.env`; lint e testes unitários
não precisam de variáveis locais. Os comandos do web-app são delegados ao workspace
`@ratatouille/web`, e a formatação verifica o monorepo inteiro.

Para E2E, instale o Chromium com
`pnpm --filter @ratatouille/web exec playwright install chromium`.

Banco: `pnpm db:generate`, `pnpm db:migrate`, `pnpm db:studio` e `pnpm db:seed`.
Os comandos da raiz carregam as variáveis centrais e montam `DATABASE_URL` local a partir
das configurações PostgreSQL. `db:push` é apenas para bancos descartáveis.
Schemas e migrações ficam em `apps/web/src/server/infrastructure/database/drizzle`
e `apps/web/drizzle`, respectivamente.

## Deploy

`pnpm infra:up` provisiona os bancos PostgreSQL, aplica as migrações, carrega o
catálogo inicial e inicia o web-app e a API Django. A imagem do web-app
usa o servidor standalone em `apps/web/server.js`.
Consulte o [guia de infraestrutura](infra/README.md) e [deploy e CI/CD](docs/deployment.md).

Na Vercel, configure Root Directory como `apps/web` e permita arquivos externos ao
Root Directory para acessar o workspace. A instalação usa o lockfile da raiz.

## Evolução

Evoluir os contratos frontend existentes para um adaptador de API e validação real.
Depois conectar os agentes, jobs demorados e o preditor neural conforme existirem
dados e avaliações. O repositório deve evoluir por incrementos pequenos e componíveis;
novos passos de inicialização e serviços entram em `infra/` sem duplicar a configuração.

A base existente mantém Atomic Design na interface e Clean Architecture no backend.
Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para contribuição e commits.
