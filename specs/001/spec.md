# Specification: Acrux project template

## Goal

Provide a private, reproducible Next.js fullstack template that demonstrates the approved frontend and backend boundaries without requiring a database to render the home page.

## Requirements

- R1: App Router, TypeScript, Tailwind, pnpm, and standalone Docker execution are configured.
- R2: The example mutation flows through Server Action, controller, service, repository interface, and Drizzle repository.
- R3: Environment validation keeps server values private and database operations fail clearly if unconfigured.
- R4: Quality tooling, hooks, CI, unit/component/E2E tests, and documentation are supplied.
- R5: The home page shows the template, theme control, stack, example form, and health link.

## Acceptance criteria

- `GET /api/health` returns `{ "status": "ok" }`.
- `pnpm check` succeeds without a database.
- Chromium E2E loads the home page and finds its primary heading and example action.
- Database migrations generate into `drizzle/` when `DATABASE_URL` is configured.
