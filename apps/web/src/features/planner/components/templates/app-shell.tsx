"use client";

import { Leaf } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

import { Button } from "@/components/atoms/button";
import { usePlannerSession } from "@/features/planner/providers/planner-provider";

export function AppShell({
  children,
  gallery = false,
}: {
  children: React.ReactNode;
  gallery?: boolean;
}) {
  const session = usePlannerSession();
  return (
    <>
      <a className="skip-link" href="#conteudo">
        Pular para o conteúdo
      </a>
      <header className="app-topbar">
        <div className="app-topbar-inner">
          <Link className="brand" href="/" aria-label="RatatouilleAI, início">
            <Image
              className="brand-symbol"
              src="/brand/ratatouille-ai.svg"
              alt=""
              width={48}
              height={48}
              preload
            />
            <span>
              ratatouille<span className="text-primary">ai</span>
              <small>COMIDA DE VERDADE. DO SEU JEITO.</small>
            </span>
          </Link>
          <nav aria-label="Navegação principal" className="flex flex-wrap items-center gap-2">
            {session.snapshot.profile && (
              <>
                <Link
                  href="/"
                  onClick={() => session.setScreen("calendar")}
                  className="nav-link"
                  aria-current={!gallery && session.screen === "calendar" ? "page" : undefined}
                >
                  Meu cardápio
                </Link>
                <Link
                  href="/"
                  onClick={session.editProfile}
                  className="nav-link"
                  aria-current={!gallery && session.screen === "profile" ? "page" : undefined}
                >
                  Meu perfil
                </Link>
              </>
            )}
            <span className="demo-badge">
              <Leaf size={14} /> Demonstração local
            </span>
          </nav>
        </div>
      </header>
      <main id="conteudo" className="app-main" tabIndex={-1}>
        {children}
      </main>
      <footer className="app-footer">
        <p>Dados fictícios e valores demonstrativos. Sem validação nutricional ou clínica.</p>
        <div className="flex flex-wrap items-center gap-4">
          <Link href="/componentes">Galeria de componentes</Link>
          <Button size="sm" variant="ghost" onClick={() => void session.reset()}>
            Restaurar demonstração
          </Button>
        </div>
        <p className="text-xs">
          As alterações ficam em memória nesta aba e são perdidas ao recarregar.
        </p>
      </footer>
    </>
  );
}
