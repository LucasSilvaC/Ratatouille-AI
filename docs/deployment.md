# Deployment and CI/CD

This repository validates changes with GitHub Actions and prepares the Next.js app for Vercel or Docker. GitHub Actions does not publish the app or push container images; delivery is configured through the hosting provider or an operator.

## GitHub workflows

| Workflow              | Trigger                                         | What it does                                                                                                                                    |
| --------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| CI                    | Pull requests and pushes to `main`              | Installs from the frozen lockfile, audits high severity dependency issues, runs `pnpm check`, installs Chromium, and runs Playwright E2E tests. |
| Automated Code Review | Opened, synchronized, or reopened pull requests | Posts ESLint findings on changed lines for same-repository branches, then runs typecheck and unit tests.                                        |
| CodeQL                | Pull requests, pushes to `main`, and weekly     | Scans JavaScript and TypeScript and uploads results to GitHub code security.                                                                    |
| Dependency Review     | Pull requests                                   | Rejects dependency changes with high or critical severity.                                                                                      |

Dependabot checks npm packages, Docker base images, and GitHub Actions weekly. Minor and patch npm updates are grouped; Dependabot opens update pull requests and does not merge them automatically. The workflows run independently. Require the desired checks in the GitHub ruleset or branch protection settings if merges to `main` must wait for them; that repository setting is not stored in these workflow files.

## Vercel

`apps/web/vercel.json` selects the Next.js framework and uses the frozen pnpm lockfile for installation and `pnpm build` for compilation. Configure the Vercel project to use `apps/web` as the Root Directory, with access to files outside that directory for the pnpm workspace and Node.js 24. Set a production `DATABASE_URL` and public `NEXT_PUBLIC_APP_URL`; do not copy the local PostgreSQL credentials from `infra/.env.example`. Store credentials in the provider, never in Git.

The Next.js config omits standalone output when Vercel sets `VERCEL=1`; Docker keeps standalone output. Apply database migrations separately before serving a release by running `pnpm db:migrate` with the production database connection. The CI and Vercel build do not migrate a production database. Git integration, production branch, domains, preview settings, and whether Vercel waits for GitHub checks are configured in the Vercel and GitHub settings, not by a deployment workflow in this repository.

## Docker Compose

The Compose file and Docker build configuration live under `infra/`. Compose builds the standalone runner and a migration image. It waits for PostgreSQL to become healthy, applies Drizzle migrations, and starts the app only after migration succeeds. See the [infrastructure guide](../infra/README.md) for the single entry point and configuration layout.

```sh
pnpm infra:up
pnpm infra:ps
pnpm infra:logs
```

The app is available on port 3000 by default; set `APP_PORT` in `infra/.env` to change the host port. The PostgreSQL data volume persists across container restarts. `pnpm infra:down` keeps that volume; `pnpm infra:down:volumes` removes it. For a standalone production image, build the `runner` target and supply production environment variables at runtime. Build and run the `migrator` target against the same database before starting the app:

```sh
docker build --file infra/docker/Dockerfile --target migrator -t ratatouille-ai-migrator:<commit> .
docker run --rm --env DATABASE_URL="$DATABASE_URL" ratatouille-ai-migrator:<commit>
docker build --file infra/docker/Dockerfile --target runner -t ratatouille-ai:<commit> .
```

## Release and rollback rules

- Commit versioned Drizzle migrations in `apps/web/drizzle` with the application change. Use `pnpm db:push` only for disposable local databases; deployed databases use `pnpm db:migrate`.
- Check that a migration is safe for the currently deployed application and document how to recover before release. Reverting application code does not reverse a database migration.
- Record the commit or image tag used for each release. There is no automated image publication, environment promotion, deployment, or rollback in this repository.
- After deployment, check `GET /api/health` and exercise the relevant application and database flows. The health route is an HTTP liveness check; it is not a substitute for validating integrations.
