import { expect, test } from "@playwright/test";

test("shows the template and health check", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Acrux Project Template" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Create record" })).toBeVisible();
  await expect(page.getByRole("link", { name: "/api/health" })).toHaveAttribute(
    "href",
    "/api/health",
  );
});
