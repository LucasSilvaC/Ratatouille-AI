import { z } from "zod";

const productDetailsSchema = z.object({
  status: z.literal("success"),
  product: z.object({
    ingredients_text: z.string().nullish().catch(null),
    ingredients_text_pt: z.string().nullish().catch(null),
    serving_size: z.string().nullish().catch(null),
    nova_group: z.literal([1, 2, 3, 4]).nullish().catch(null),
    nutriments: z.record(z.string(), z.unknown()).nullish().catch(null),
  }),
});

const nutritionFields = [
  { key: "energy-kcal_100g", label: "Valor energético", unit: "kcal" },
  { key: "carbohydrates_100g", label: "Carboidratos", unit: "g" },
  { key: "sugars_100g", label: "Açúcares totais", unit: "g" },
  { key: "proteins_100g", label: "Proteínas", unit: "g" },
  { key: "fat_100g", label: "Gorduras totais", unit: "g" },
  { key: "saturated-fat_100g", label: "Gorduras saturadas", unit: "g" },
  { key: "fiber_100g", label: "Fibras alimentares", unit: "g" },
  { key: "salt_100g", label: "Sal", unit: "g" },
];

export interface OpenFoodFactsProductDetails {
  ingredients: string;
  servingSize: string;
  novaGroup: 1 | 2 | 3 | 4 | null;
  nutrients: { label: string; value: number; unit: string }[];
}

export async function getOpenFoodFactsProductDetails(
  code: string,
): Promise<OpenFoodFactsProductDetails | null> {
  const url = new URL(`https://world.openfoodfacts.org/api/v3/product/${code}`);
  url.searchParams.set(
    "fields",
    "ingredients_text,ingredients_text_pt,serving_size,nutriments,nova_group",
  );

  const response = await fetch(url, {
    headers: { "User-Agent": "RatatouilleAI/0.1 (https://github.com/LucasSilvaC/Ratatouille-AI)" },
    next: { revalidate: 300 },
    signal: AbortSignal.timeout(8000),
  });
  if (response.status === 404) return null;
  if (!response.ok) throw new Error(`Open Food Facts returned HTTP ${response.status}`);

  const { product } = productDetailsSchema.parse(await response.json());
  const nutrients = nutritionFields.flatMap(({ key, label, unit }) => {
    const value = product.nutriments?.[key];
    return typeof value === "number" && Number.isFinite(value) && value >= 0
      ? [{ label, value, unit }]
      : [];
  });

  return {
    ingredients: product.ingredients_text_pt?.trim() || product.ingredients_text?.trim() || "",
    servingSize: product.serving_size?.trim() ?? "",
    novaGroup: product.nova_group ?? null,
    nutrients,
  };
}
