# Specification: RatatouilleAI initial foundation

## Goal

Provide a private, reproducible Next.js foundation for RatatouilleAI that demonstrates the approved frontend and backend boundaries without requiring a database to render the home page.

This specification records the initial foundation. The current planning interface and mock flows are documented in [the frontend guide](../../docs/frontend-demo.md).

## Requirements

- R1: App Router, TypeScript, Tailwind, pnpm, and standalone Docker execution are configured.
- R2: The example mutation flows through Server Action, controller, service, repository interface, and Drizzle repository.
- R3: Environment validation keeps server values private and database operations fail clearly if unconfigured.
- R4: Quality tooling, hooks, CI, unit/component/E2E tests, and documentation are supplied.
- R5: The initial home page demonstrates the stack, theme control, example form, and health link; the RatatouilleAI planning interface supersedes that initial screen.

## Acceptance criteria

- `GET /api/health` returns `{ "status": "ok" }`.
- `pnpm check` succeeds without a database.
- Chromium E2E loads RatatouilleAI and exercises its primary user flow.
- Database migrations generate into `drizzle/` when `DATABASE_URL` is configured.
