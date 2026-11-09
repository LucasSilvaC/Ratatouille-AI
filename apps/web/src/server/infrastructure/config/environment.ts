import "server-only";

import { z } from "zod";

const serverEnvironmentSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  DATABASE_URL: z.string().url().optional(),
});
const publicEnvironmentSchema = z.object({
  NEXT_PUBLIC_APP_URL: z.string().url().default("http://localhost:3000"),
});

export const environment = {
  server: serverEnvironmentSchema.parse({
    NODE_ENV: process.env.NODE_ENV,
    DATABASE_URL: process.env.DATABASE_URL,
  }),
  public: publicEnvironmentSchema.parse({ NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL }),
};

export function requireDatabaseUrl(): string {
  const databaseUrl = environment.server.DATABASE_URL;
  if (!databaseUrl)
    throw new Error(
      "DATABASE_URL is required for database operations. Set PostgreSQL values in infra/.env and use root workspace commands.",
    );
  return databaseUrl;
}
