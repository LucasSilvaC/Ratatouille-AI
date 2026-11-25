"use server";

import { z } from "zod";

import {
  type OpenFoodFactsProduct,
  searchOpenFoodFacts,
} from "@/server/product-search-composition";

export type ProductSearchState =
  | { status: "idle" }
  | { status: "invalid" | "error" }
  | {
      status: "success";
      query: string;
      page: number;
      pageCount: number;
      products: OpenFoodFactsProduct[];
    };

const querySchema = z.string().trim().min(2).max(100);
const pageSchema = z
  .string()
  .regex(/^[1-9]\d*$/)
  .transform(Number)
  .pipe(z.number().int().positive());

export async function searchProductsAction(
  _: ProductSearchState,
  formData: FormData,
): Promise<ProductSearchState> {
  const query = querySchema.safeParse(formData.get("query"));
  const page = pageSchema.safeParse(formData.get("page") ?? "1");
  if (!query.success || !page.success) return { status: "invalid" };

  try {
    return {
      status: "success",
      query: query.data,
      ...(await searchOpenFoodFacts(query.data, page.data)),
    };
  } catch {
    return { status: "error" };
  }
}
