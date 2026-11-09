import type { Metadata } from "next";

import { PlannerProvider } from "@/features/planner/providers/planner-provider";

import "./globals.css";

export const metadata: Metadata = {
  title: "RatatouilleAI — Sua semana, do seu jeito",
  description: "Planejamento alimentar regional. Demonstração local com dados fictícios.",
};

interface IRootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: IRootLayoutProps): React.ReactElement {
  return (
    <html lang="pt-BR">
      <body>
        <PlannerProvider>{children}</PlannerProvider>
      </body>
    </html>
  );
}
