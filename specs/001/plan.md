# Plan: Acrux project template

1. Scaffold the official Next.js baseline with pnpm and initialize local Git on `main`.
2. Configure strict TypeScript, linting, formatting, commits, testing, Docker, CI, and dependency updates.
3. Implement Atomic Design primitives and a theme-aware home page.
4. Implement the removable example across Clean Architecture layers, Drizzle schema, and Server Action.
5. Document operations and validate the full local quality path.

Risks: database-dependent mutations cannot be exercised without PostgreSQL; the home page and all non-database checks remain independent.
