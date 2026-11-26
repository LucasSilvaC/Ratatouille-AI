import { afterEach, expect, it, vi } from "vitest";

import { getProductDetailsAction } from "@/features/products/actions/get-product-details.action";

afterEach(() => vi.unstubAllGlobals());

it("looks up the exact barcode and preserves zero values while omitting missing nutrients", async () => {
  vi.stubGlobal("fetch", async (url: URL) => {
    expect(url.origin + url.pathname).toBe(
      "https://world.openfoodfacts.org/api/v3/product/01234567",
    );
    expect(url.searchParams.get("fields")?.split(",")).toContain("nova_group");
    return Response.json({
      status: "success",
      product: {
        ingredients_text_pt: "Aveia integral",
        ingredients_text: "Whole oats",
        serving_size: "30 g",
        nova_group: 4,
        nutriments: { "energy-kcal_100g": 370, sugars_100g: 0, fiber_serving: 3 },
      },
    });
  });

  await expect(getProductDetailsAction("01234567")).resolves.toEqual({
    status: "success",
    details: {
      ingredients: "Aveia integral",
      servingSize: "30 g",
      novaGroup: 4,
      nutrients: [
        { label: "Valor energético", value: 370, unit: "kcal" },
        { label: "Açúcares totais", value: 0, unit: "g" },
      ],
    },
  });
});

it.each([undefined, 0, 5])(
  "keeps details available for an unknown NOVA group (%s)",
  async (novaGroup) => {
    vi.stubGlobal("fetch", async () =>
      Response.json({
        status: "success",
        product: { nova_group: novaGroup },
      }),
    );

    await expect(getProductDetailsAction("01234567")).resolves.toMatchObject({
      status: "success",
      details: { novaGroup: null },
    });
  },
);
