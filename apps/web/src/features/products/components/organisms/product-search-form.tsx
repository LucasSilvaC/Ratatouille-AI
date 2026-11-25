"use client";

import { useActionState, useState } from "react";

import { Button } from "@/components/atoms/button";
import { Input } from "@/components/atoms/input";
import { Label } from "@/components/atoms/label";
import { searchProductsAction } from "@/features/products/actions/search-products.action";
import { ProductCard } from "@/features/products/components/molecules/product-card";

export function ProductSearchForm() {
  const [query, setQuery] = useState("");
  const [state, action, isPending] = useActionState(searchProductsAction, { status: "idle" });
  const products = state.status === "success" ? state.products : [];

  return (
    <div className="space-y-6">
      <form action={action} role="search" className="space-y-2">
        <Label htmlFor="product-query">Nome ou marca</Label>
        <div className="flex flex-col gap-2 sm:flex-row">
          <Input
            id="product-query"
            name="query"
            type="search"
            placeholder="Ex.: aveia ou Nutella"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            required
            minLength={2}
            maxLength={100}
            readOnly={isPending}
            aria-invalid={state.status === "invalid"}
            aria-describedby={state.status === "invalid" ? "product-query-error" : undefined}
          />
          <Button type="submit" disabled={isPending}>
            {isPending ? "Buscando…" : "Buscar"}
          </Button>
        </div>
        {!isPending && state.status === "invalid" && (
          <p id="product-query-error" role="alert" className="text-destructive text-sm">
            Digite de 2 a 100 caracteres.
          </p>
        )}
      </form>
      <section aria-label="Resultados da busca" aria-busy={isPending} className="space-y-3">
        {!isPending && state.status === "error" && (
          <p role="alert" className="text-destructive">
            Não foi possível consultar o Open Food Facts. Tente buscar novamente em instantes.
          </p>
        )}
        {state.status === "success" && (
          <p role="status" className="text-muted-foreground text-sm">
            {state.pageCount === 0
              ? "Nenhum produto encontrado. Tente outro nome ou marca."
              : `Página ${state.page} de ${state.pageCount}`}
          </p>
        )}
        {state.status === "success" && state.pageCount > 1 && (
          <nav aria-label="Paginação dos produtos">
            <form action={action} className="flex flex-wrap gap-2">
              <input type="hidden" name="query" value={state.query} />
              <Button
                type="submit"
                name="page"
                value={state.page - 1}
                variant="outline"
                disabled={isPending || state.page <= 1}
              >
                Anterior
              </Button>
              <Button
                type="submit"
                name="page"
                value={state.page + 1}
                variant="outline"
                disabled={isPending || state.page >= state.pageCount}
              >
                Próxima
              </Button>
            </form>
          </nav>
        )}
        {products.length > 0 && (
          <ul className="grid gap-3 sm:grid-cols-2">
            {products.map((product) => (
              <li key={product.code}>
                <ProductCard product={product} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
