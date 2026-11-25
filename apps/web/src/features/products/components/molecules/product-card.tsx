"use client";

import Image from "next/image";
import { useState, useTransition } from "react";

import { Button } from "@/components/atoms/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/atoms/card";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/atoms/dialog";
import {
  getProductDetailsAction,
  type ProductDetailsResult,
} from "@/features/products/actions/get-product-details.action";
import type { OpenFoodFactsProduct } from "@/server/product-search-composition";

const nutritionNumber = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 6 });
const novaLabels = {
  1: "Alimentos in natura ou minimamente processados",
  2: "Ingredientes culinários processados",
  3: "Alimentos processados",
  4: "Alimentos ultraprocessados",
};

export function ProductCard({ product }: { product: OpenFoodFactsProduct }) {
  const [result, setResult] = useState<ProductDetailsResult>();
  const [isPending, startTransition] = useTransition();
  const details = result?.status === "success" ? result.details : undefined;

  function loadDetails() {
    startTransition(async () => {
      try {
        setResult(await getProductDetailsAction(product.code));
      } catch {
        setResult({ status: "error" });
      }
    });
  }

  return (
    <Dialog
      onOpenChange={(isOpen) => {
        if (isOpen && !result && !isPending) loadDetails();
      }}
    >
      <Card className="relative h-full">
        <CardHeader>
          {product.imageUrl && (
            <Image
              src={product.imageUrl}
              alt=""
              width={200}
              height={200}
              unoptimized
              className="h-32 w-full object-contain"
            />
          )}
          <CardTitle className="break-words">
            <DialogTrigger asChild>
              <button
                type="button"
                className="focus-visible:after:ring-ring cursor-pointer text-left after:absolute after:inset-0 after:rounded-2xl hover:underline focus-visible:after:ring-2"
              >
                {product.name}
              </button>
            </DialogTrigger>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-muted-foreground space-y-1 text-sm break-words">
          {product.brands && <p>{product.brands}</p>}
          {product.quantity && <p>{product.quantity}</p>}
          <p>Código de barras {product.code}</p>
        </CardContent>
      </Card>
      <DialogContent>
        <DialogHeader>
          <div className="flex items-start justify-between gap-3">
            <DialogTitle className="min-w-0 break-words">{product.name}</DialogTitle>
            <DialogClose asChild>
              <Button variant="outline" size="sm">
                Fechar
              </Button>
            </DialogClose>
          </div>
          <DialogDescription>
            {[product.brands, product.quantity, `Código de barras ${product.code}`]
              .filter(Boolean)
              .join(" · ")}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          {(isPending || !result) && <p role="status">Carregando dados do produto…</p>}
          {!isPending && result?.status === "not-found" && (
            <p role="status">Produto indisponível no catálogo do Open Food Facts.</p>
          )}
          {!isPending && result?.status === "error" && (
            <>
              <p role="alert">Não foi possível carregar os dados do produto.</p>
              <Button type="button" variant="outline" onClick={loadDetails}>
                Tentar novamente
              </Button>
            </>
          )}
          {details && (
            <>
              <section className="space-y-2">
                <h3 className="font-semibold">Classificação NOVA</h3>
                <p className="text-sm">
                  {details.novaGroup === null
                    ? "Classificação indisponível no Open Food Facts."
                    : `NOVA ${details.novaGroup} · ${novaLabels[details.novaGroup]}`}
                </p>
              </section>
              {details.servingSize && (
                <p className="text-sm">Porção cadastrada: {details.servingSize}</p>
              )}
              <section className="space-y-2">
                <h3 className="font-semibold">Ingredientes</h3>
                <p className="text-sm">{details.ingredients || "Ingredientes não cadastrados."}</p>
              </section>
              <section className="space-y-2">
                <h3 className="font-semibold">Informação nutricional por 100 g ou 100 ml</h3>
                {details.nutrients.length > 0 ? (
                  <dl className="divide-y text-sm">
                    {details.nutrients.map(({ label, value, unit }) => (
                      <div key={label} className="flex justify-between gap-4 py-2">
                        <dt>{label}</dt>
                        <dd className="shrink-0 tabular-nums">
                          {nutritionNumber.format(value)} {unit}
                        </dd>
                      </div>
                    ))}
                  </dl>
                ) : (
                  <p className="text-sm">Valores nutricionais não cadastrados.</p>
                )}
              </section>
            </>
          )}
          <a
            href={`https://world.openfoodfacts.org/product/${product.code}`}
            className="text-primary inline-block text-sm underline"
            target="_blank"
            rel="noreferrer"
          >
            Ver no Open Food Facts (nova aba)
          </a>
        </div>
      </DialogContent>
    </Dialog>
  );
}
