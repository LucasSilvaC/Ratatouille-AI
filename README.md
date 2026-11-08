# Acrux Project Template

A private, reusable fullstack baseline for Acrux web products. Create the official repository inside the Acrux GitHub organization; this template intentionally has no remote URL.

## Stack

Next.js App Router, React, TypeScript, Tailwind CSS, Shadcn-style primitives, Server Actions, Drizzle, PostgreSQL, Zod, Vitest, Playwright, Docker, pnpm, and GitHub Actions.

## Requirements and setup

Node 24 (see `.nvmrc`), pnpm 11, and Docker for local PostgreSQL.

```bash
pnpm install
cp .env.example .env.local
docker compose up -d postgres
pnpm db:generate
pnpm db:migrate
pnpm dev
```

Open `http://localhost:3000`; the health endpoint is `http://localhost:3000/api/health`.

## Database

`DATABASE_URL` is server-only. Use `pnpm db:generate` to create versioned migrations and `pnpm db:migrate` to apply them. `pnpm db:push` is only for disposable local development; production uses migrations. `pnpm db:studio` opens Drizzle Studio and `pnpm db:seed` adds the removable example record.

Docker commands: `docker compose up -d --build`, `docker compose down`, and `docker compose down -v` (the last removes local database data). Compose applies database migrations before starting the app. Build the production app image with `docker build --target runner -t acrux-project-template .`.

## Quality

`pnpm format`, `pnpm format:check`, `pnpm lint`, `pnpm typecheck`, `pnpm test:unit`, `pnpm test:coverage`, `pnpm build`, `pnpm test:e2e`, and `pnpm check` are available. CI runs format, lint, types, unit tests, build, and Chromium E2E.

See [deployment and CI/CD](docs/deployment.md) for the GitHub checks, Vercel setup, container deployment, and migration steps.

Commits use `type(scope): description`, lowercase, with a mandatory scope. Run `pnpm check` before every PR. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Structure

`src/app` is the Next framework layer; `src/components` contains atoms, molecules, and organisms; `src/features` owns product UI; `src/server` contains Clean Architecture layers. See [docs/architecture.md](docs/architecture.md).

To create a feature, add its UI, actions, schemas, and tests under `src/features/<name>`. Add a use case under `server/application/services`, a repository interface under `domain/repositories`, its implementation under `infrastructure`, and connect them in `composition-root.ts`. New Shadcn primitives belong in `src/components/atoms` as configured in `components.json`.

## Removing the example feature

Remove `src/features/example`, `src/server/domain/{entities,errors,repositories,value-objects}/example-*`, `src/server/application/{dtos,services}/create-example-record-*`, `src/server/infrastructure/database/drizzle/{repositories,schemas}/example-*`, `src/server/presentation/{controllers,mappers}/example-*`, the factory in `src/server/composition-root.ts`, its tests, and the example form import from `src/app/page.tsx`. Generate a migration to drop `example_records` when it has reached a deployed database.

## Production

Set `DATABASE_URL` and `NEXT_PUBLIC_APP_URL` in Vercel or another platform. Supabase PostgreSQL works through its PostgreSQL connection string; do not install the Supabase SDK unless a product needs it. Confirm migrations, environment variables, security headers, and an integration-specific CSP before deployment. The Docker Compose deployment applies migrations before starting the app.
