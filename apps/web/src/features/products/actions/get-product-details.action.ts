"use server";

import { z } from "zod";

import {
  getOpenFoodFactsProductDetails,
  type OpenFoodFactsProductDetails,
} from "@/server/product-search-composition";

export type ProductDetailsResult =
  { status: "success"; details: OpenFoodFactsProductDetails } | { status: "not-found" | "error" };

const barcodeSchema = z.string().regex(/^\d{1,32}$/);

export async function getProductDetailsAction(code: string): Promise<ProductDetailsResult> {
  const barcode = barcodeSchema.safeParse(code);
  if (!barcode.success) return { status: "not-found" };

  try {
    const details = await getOpenFoodFactsProductDetails(barcode.data);
    return details ? { status: "success", details } : { status: "not-found" };
  } catch {
    return { status: "error" };
  }
}
