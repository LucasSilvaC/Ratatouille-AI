import { existsSync } from "node:fs";
import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const infraDirectory = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = resolve(infraDirectory, "..");
const envFile = resolve(infraDirectory, ".env");

if (existsSync(envFile)) {
  process.loadEnvFile(envFile);
}

if (!process.env.DATABASE_URL) {
  const databaseUrl = new URL("postgresql://localhost");
  databaseUrl.username = process.env.POSTGRES_USER ?? "ratatouille";
  databaseUrl.password = process.env.POSTGRES_PASSWORD ?? "ratatouille";
  databaseUrl.port = process.env.POSTGRES_PORT ?? "5432";
  databaseUrl.pathname = `/${process.env.POSTGRES_DB ?? "ratatouille_ai"}`;
  process.env.DATABASE_URL = databaseUrl.toString();
}

const [command, ...args] = process.argv.slice(2);

if (!command) {
  console.error("Usage: node infra/scripts/with-env.mjs <command> [args...]");
  process.exit(2);
}

const child = spawn(command, args, {
  cwd: repositoryRoot,
  env: process.env,
  shell: process.platform === "win32",
  stdio: "inherit",
});

child.on("error", (error) => {
  console.error(error.message);
  process.exitCode = 1;
});

child.on("exit", (code, signal) => {
  process.exitCode = code ?? (signal ? 1 : 0);
});
