import type { Metadata } from "next";
import Link from "next/link";

import { ProductSearchForm } from "@/features/products/components/organisms/product-search-form";

export const metadata: Metadata = { title: "Buscar produtos | RatatouilleAI" };

export default function ProductsPage() {
  return (
    <main className="app-main mx-auto max-w-3xl space-y-6">
      <Link href="/" className="text-primary text-sm font-medium hover:underline">
        Voltar para o planejador
      </Link>
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">Buscar produtos</h1>
        <p className="text-muted-foreground">
          Consulte o catálogo do{" "}
          <a href="https://world.openfoodfacts.org/discover" className="underline">
            Open Food Facts
          </a>{" "}
          pelo nome ou pela marca do produto.
        </p>
      </header>
      <ProductSearchForm />
    </main>
  );
}
