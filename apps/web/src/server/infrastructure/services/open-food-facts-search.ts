import { z } from "zod";

const productSchema = z.object({
  code: z.string().regex(/^\d{1,32}$/),
  product_name: z.string().nullish(),
  product_name_pt: z.string().nullish(),
  brands: z.array(z.string()).nullish(),
  quantity: z.string().nullish(),
  image_front_small_url: z
    .string()
    .regex(/^https:\/\/images\.openfoodfacts\.org\/images\/products\/[\w/.-]+\.jpg$/i)
    .nullish()
    .catch(null),
});

const searchResponseSchema = z.object({
  hits: z.array(z.unknown()),
  page: z.number().int().positive(),
  page_count: z.number().int().nonnegative(),
  timed_out: z.boolean().optional(),
});

export interface OpenFoodFactsProduct {
  code: string;
  name: string;
  brands: string;
  quantity: string;
  imageUrl: string | null;
}

export async function searchOpenFoodFacts(query: string, page: number) {
  const url = new URL("https://search.openfoodfacts.org/search");
  url.searchParams.set("q", query);
  url.searchParams.set("langs", "pt,en");
  url.searchParams.set("page_size", "20");
  url.searchParams.set("page", String(page));
  url.searchParams.set(
    "fields",
    "code,product_name,product_name_pt,brands,quantity,image_front_small_url",
  );

  const response = await fetch(url, {
    headers: { "User-Agent": "RatatouilleAI/0.1 (https://github.com/LucasSilvaC/Ratatouille-AI)" },
    next: { revalidate: 300 },
    signal: AbortSignal.timeout(8000),
  });
  if (!response.ok) throw new Error(`Open Food Facts returned HTTP ${response.status}`);

  const {
    hits,
    page: currentPage,
    page_count: pageCount,
    timed_out: timedOut,
  } = searchResponseSchema.parse(await response.json());
  if (timedOut) throw new Error("Open Food Facts search timed out");

  const products = new Map<string, OpenFoodFactsProduct>();
  for (const hit of hits) {
    const parsed = productSchema.safeParse(hit);
    if (!parsed.success || products.has(parsed.data.code)) continue;

    const product = parsed.data;
    products.set(product.code, {
      code: product.code,
      name: product.product_name_pt?.trim() || product.product_name?.trim() || "Produto sem nome",
      brands:
        product.brands
          ?.map((brand) => brand.replace(/^[a-z]{2}:/, "").trim())
          .filter(Boolean)
          .join(", ") ?? "",
      quantity: product.quantity?.trim() ?? "",
      imageUrl: product.image_front_small_url ?? null,
    });
  }
  return { page: currentPage, pageCount, products: [...products.values()] };
}
