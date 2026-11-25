import { afterEach, expect, it, vi } from "vitest";

import { searchProductsAction } from "@/features/products/actions/search-products.action";

afterEach(() => vi.unstubAllGlobals());

it("treats a partial response from an upstream timeout as unavailable", async () => {
  vi.stubGlobal("fetch", async () => Response.json({ timed_out: true, hits: [] }));
  const form = new FormData();
  form.set("query", "aveia");

  await expect(searchProductsAction({ status: "idle" }, form)).resolves.toEqual({
    status: "error",
  });
});

it("loads the requested page with product details and available thumbnails", async () => {
  vi.stubGlobal("fetch", async (url: URL) => {
    expect(url.origin + url.pathname).toBe("https://search.openfoodfacts.org/search");
    expect(url.searchParams.get("q")).toBe("aveia");
    expect(url.searchParams.get("page")).toBe("2");
    expect(url.searchParams.get("fields")).toContain("image_front_small_url");
    return Response.json({
      page: 2,
      page_count: 3,
      hits: [
        {
          code: "01234567",
          product_name: "Oats",
          product_name_pt: "Aveia",
          brands: ["xx:Marca"],
          quantity: "400 g",
          image_front_small_url:
            "https://images.openfoodfacts.org/images/products/01234567/front_pt.2.200.jpg",
        },
        {
          code: "02345678",
          product_name: "Aveia em flocos",
          image_front_small_url: "https://untrusted.example/photo.jpg",
        },
      ],
    });
  });
  const form = new FormData();
  form.set("query", " aveia ");
  form.set("page", "2");

  await expect(searchProductsAction({ status: "idle" }, form)).resolves.toEqual({
    status: "success",
    query: "aveia",
    page: 2,
    pageCount: 3,
    products: [
      {
        code: "01234567",
        name: "Aveia",
        brands: "Marca",
        quantity: "400 g",
        imageUrl: "https://images.openfoodfacts.org/images/products/01234567/front_pt.2.200.jpg",
      },
      { code: "02345678", name: "Aveia em flocos", brands: "", quantity: "", imageUrl: null },
    ],
  });
});
