import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/atoms/card";
import { ThemeToggle } from "@/components/molecules/theme-toggle";
import { ExampleForm } from "@/features/example/components/example-form";

const technologies = [
  "Next.js",
  "TypeScript",
  "Tailwind CSS",
  "Shadcn UI",
  "Drizzle",
  "PostgreSQL",
  "Vitest",
  "Playwright",
];

export default function Home(): React.ReactElement {
  return (
    <main className="mx-auto min-h-screen max-w-5xl space-y-8 px-6 py-12">
      <header className="flex items-start justify-between gap-6">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Acrux Project Template</h1>
          <p className="text-muted-foreground mt-2">
            A reusable, fullstack baseline with explicit boundaries.
          </p>
        </div>
        <ThemeToggle />
      </header>
      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Included stack</CardTitle>
            <CardDescription>
              Production-minded tools with a small starting surface.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="grid grid-cols-2 gap-2 text-sm">
              {technologies.map((technology) => (
                <li key={technology} className="bg-muted rounded-md px-3 py-2">
                  {technology}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
        <ExampleForm />
      </section>
      <section className="rounded-lg border p-5">
        <h2 className="font-medium">Useful commands</h2>
        <p className="text-muted-foreground mt-2 text-sm">
          <code>pnpm dev</code> starts the app.{" "}
          <a className="underline underline-offset-4" href="/api/health">
            /api/health
          </a>{" "}
          exposes the health check.
        </p>
      </section>
    </main>
  );
}
