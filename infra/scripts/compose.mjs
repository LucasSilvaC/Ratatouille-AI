import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const infraDirectory = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = resolve(infraDirectory, "..");
const actions = {
  up: ["up", "-d", "--build"],
  db: ["up", "-d", "postgres"],
  down: ["down"],
  "down:volumes": ["down", "--volumes"],
  ps: ["ps"],
  logs: ["logs", "--follow"],
};
const [action, ...extraArgs] = process.argv.slice(2);

if (!action || !actions[action]) {
  console.error(
    `Usage: node infra/scripts/compose.mjs <${Object.keys(actions).join("|")}> [args...]`,
  );
  process.exit(2);
}

const args = [
  "compose",
  "--project-directory",
  "infra",
  "--file",
  "infra/compose.yaml",
  ...actions[action],
  ...extraArgs,
];

const child = spawn("docker", args, {
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
