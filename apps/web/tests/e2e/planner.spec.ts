import { expect, test, type Locator, type Page } from "@playwright/test";

test.setTimeout(90000);

async function selectOption(page: Page, label: string, option: string) {
  await page.getByRole("combobox", { name: label, exact: true }).click();
  await page.getByRole("option", { name: option, exact: true }).click();
}

async function profileAndRegion(page: Page, restriction = false) {
  await page.goto("/");
  await page.getByLabel("Nome (obrigatório)", { exact: true }).fill("Ana Demo");
  if (restriction)
    await page.getByRole("checkbox", { name: "Intolerância à lactose", exact: true }).check();
  await page.getByRole("checkbox", { name: /Revisei os grupos/ }).check();
  await page.getByRole("button", { name: "Continuar", exact: true }).click();
  await selectOption(page, "País (obrigatório)", "Brasil");
  await page.getByRole("radio", { name: /Sudeste/ }).check();
  await page.getByRole("button", { name: "Continuar", exact: true }).click();
}

async function approveInitialWeek(page: Page) {
  await profileAndRegion(page);
  await page.getByRole("button", { name: "Pular por enquanto", exact: true }).click();
  await expect(page.getByRole("region", { name: "Proposta inicial", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Aprovar", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Sua semana, do seu jeito.", exact: true }),
  ).toBeVisible();
}

function approvedPlan(page: Page) {
  return page.getByRole("region", { name: "Plano semanal aprovado", exact: true });
}

async function names(plan: Locator) {
  return plan.getByRole("heading", { level: 3 }).allTextContents();
}

test("onboarding preserves drafts, blocks unsupported country and skips preferences without removing restrictions", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await profileAndRegion(page, true);
  await expect(
    page.getByRole("checkbox", { name: "Iogurte e frutas", exact: true }),
  ).toBeDisabled();
  await page.getByRole("checkbox", { name: "Arroz integral", exact: true }).check();
  await page.getByRole("button", { name: "Voltar", exact: true }).click();
  await expect(page.getByRole("radio", { name: /Sudeste/ })).toBeChecked();
  await selectOption(page, "País (obrigatório)", "Portugal");
  await expect(
    page.getByText("Localidade sem cobertura demonstrativa.", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Continuar", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Sabores de perto de você.", exact: true }),
  ).toBeVisible();
  await selectOption(page, "País (obrigatório)", "Brasil");
  await expect(page.getByRole("radio", { name: /Sudeste/ })).not.toBeChecked();
  await page.getByRole("radio", { name: /Sudeste/ }).check();
  await page.getByRole("button", { name: "Voltar", exact: true }).click();
  await expect(page.getByLabel("Nome (obrigatório)", { exact: true })).toHaveValue("Ana Demo");
  await expect(
    page.getByRole("checkbox", { name: "Intolerância à lactose", exact: true }),
  ).toBeChecked();
  await page.getByRole("button", { name: "Continuar", exact: true }).click();
  await page.getByRole("button", { name: "Continuar", exact: true }).click();
  await expect(page.getByRole("checkbox", { name: "Arroz integral", exact: true })).toBeChecked();
  await page.getByRole("button", { name: "Pular por enquanto", exact: true }).click();
  await page.getByRole("button", { name: "Aprovar", exact: true }).click();
  await expect(approvedPlan(page)).toBeVisible();
  await page.getByRole("button", { name: "Editar perfil e preferências", exact: true }).click();
  await expect(
    page.getByRole("checkbox", { name: "Intolerância à lactose", exact: true }),
  ).toBeChecked();
  await expect(
    page.getByRole("checkbox", { name: "Arroz integral", exact: true }),
  ).not.toBeChecked();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
});

test("calendar exposes 21 meals, cancelling preserves all and approval changes exactly one", async ({
  page,
}) => {
  await approveInitialWeek(page);
  const plan = approvedPlan(page);
  await plan.getByRole("tab", { name: "Semana", exact: true }).click();
  await expect(plan.getByRole("button", { name: /^Ver detalhes:/ })).toHaveCount(21);
  const before = await names(plan);
  await plan
    .getByRole("button", { name: /^Trocar refeição:/ })
    .first()
    .click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByRole("heading", { name: "Proposta", exact: true })).toBeVisible();
  await dialog.getByRole("button", { name: "Cancelar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(plan.getByRole("button", { name: /^Trocar refeição:/ }).first()).toBeFocused();
  expect(await names(plan)).toEqual(before);
  await plan
    .getByRole("button", { name: /^Trocar refeição:/ })
    .first()
    .click();
  await dialog.getByRole("button", { name: "Aprovar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  const after = await names(plan);
  expect(after.filter((name, index) => name !== before[index])).toHaveLength(1);
  expect(after[1]).not.toEqual(before[1]);
  expect(after.slice(2)).toEqual(before.slice(2));
  await plan.getByRole("tab", { name: "Por dia", exact: true }).click();
  await expect(plan.getByRole("button", { name: /^Ver detalhes:/ })).toHaveCount(3);
});

test("new weekly proposal never replaces the approved week before approval", async ({ page }) => {
  await approveInitialWeek(page);
  const plan = approvedPlan(page);
  await plan.getByRole("tab", { name: "Semana", exact: true }).click();
  const before = await names(plan);
  await page.getByRole("button", { name: "Gerar nova proposta", exact: true }).click();
  const review = page.getByRole("region", {
    name: "Revisão da nova proposta semanal",
    exact: true,
  });
  await expect(review).toBeVisible();
  expect(await names(plan)).toEqual(before);
  await review.getByRole("button", { name: "Cancelar", exact: true }).click();
  await expect(review).not.toBeVisible();
  expect(await names(plan)).toEqual(before);
});

test("meal error and conflict preserve proposal, require refreshed review and allow recovery", async ({
  page,
}) => {
  await approveInitialWeek(page);
  const plan = approvedPlan(page);
  await plan
    .getByRole("button", { name: /^Trocar refeição:/ })
    .first()
    .click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByRole("heading", { name: "Proposta", exact: true })).toBeVisible();
  const proposed = await dialog
    .locator("section")
    .filter({ has: page.getByRole("heading", { name: "Proposta", exact: true }) })
    .getByRole("heading", { level: 3 })
    .last()
    .textContent();
  await selectOption(page, "Cenário demonstrativo da troca", "Erro simulado");
  await dialog.getByRole("button", { name: "Aprovar", exact: true }).click();
  await expect(dialog.getByRole("alert")).toContainText("preservados");
  await expect(dialog.getByRole("heading", { name: proposed!, exact: true })).toBeVisible();
  await selectOption(page, "Cenário demonstrativo da troca", "Conflito ao aprovar");
  await dialog.getByRole("button", { name: "Aprovar", exact: true }).click();
  await expect(
    dialog.getByRole("button", { name: "Recarregar e revisar diferenças", exact: true }),
  ).toBeVisible();
  await expect(dialog.getByRole("heading", { name: proposed!, exact: true })).toBeVisible();
  await expect(dialog.getByRole("button", { name: "Aprovar", exact: true })).toBeDisabled();
  await dialog
    .getByRole("button", { name: "Recarregar e revisar diferenças", exact: true })
    .click();
  await expect(dialog.getByRole("button", { name: "Aprovar", exact: true })).toBeEnabled();
  await dialog.getByRole("button", { name: "Aprovar", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(plan.getByRole("heading", { name: proposed!, exact: true })).toBeVisible();
});

test("profile draft survives navigation, cancel confirms discard and restrictions flag revalidation", async ({
  page,
}) => {
  await approveInitialWeek(page);
  await page.getByRole("button", { name: "Editar perfil e preferências", exact: true }).click();
  await page.getByLabel("Nome (obrigatório)", { exact: true }).fill("Nome em rascunho");
  await page.getByRole("button", { name: "Ver cardápio e manter rascunho", exact: true }).click();
  await page.getByRole("button", { name: "Editar perfil e preferências", exact: true }).click();
  await expect(page.getByLabel("Nome (obrigatório)", { exact: true })).toHaveValue(
    "Nome em rascunho",
  );
  await page.getByRole("button", { name: "Cancelar", exact: true }).click();
  const discard = page.getByRole("dialog", { name: "Descartar alterações?", exact: true });
  await discard.getByRole("button", { name: "Cancelar", exact: true }).click();
  await expect(page.getByLabel("Nome (obrigatório)", { exact: true })).toHaveValue(
    "Nome em rascunho",
  );
  await page.getByRole("button", { name: "Cancelar", exact: true }).click();
  await discard.getByRole("button", { name: "Aprovar", exact: true }).click();
  await page.getByRole("button", { name: "Editar perfil e preferências", exact: true }).click();
  await expect(page.getByLabel("Nome (obrigatório)", { exact: true })).toHaveValue("Ana Demo");
  await page.getByRole("checkbox", { name: "Intolerância à lactose", exact: true }).check();
  await page.getByRole("button", { name: "Aprovar", exact: true }).click();
  await expect(
    page.getByText("Seu plano precisa de uma nova revisão.", { exact: true }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Revalidar plano", exact: true })).toBeVisible();
});

test("generation empty and error recover without losing onboarding data", async ({ page }) => {
  await profileAndRegion(page);
  await page.getByText("Cenários da demonstração", { exact: true }).click();
  await selectOption(page, "Resultado da próxima operação", "Sem candidatos");
  await page.getByRole("button", { name: "Gerar cardápio", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Nenhum candidato disponível", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Voltar às preferências", exact: true }).click();
  await page.getByText("Cenários da demonstração", { exact: true }).click();
  await selectOption(page, "Resultado da próxima operação", "Erro");
  await page.getByRole("button", { name: "Gerar cardápio", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: "preservados" })).toBeVisible();
  await page.getByText("Cenários da demonstração", { exact: true }).click();
  await selectOption(page, "Resultado da próxima operação", "Sucesso");
  await page.getByRole("button", { name: "Tentar novamente", exact: true }).click();
  await expect(page.getByRole("region", { name: "Proposta inicial", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Cancelar", exact: true }).click();
  await page.getByRole("button", { name: "Voltar", exact: true }).click();
  await page.getByRole("button", { name: "Voltar", exact: true }).click();
  await expect(page.getByLabel("Nome (obrigatório)", { exact: true })).toHaveValue("Ana Demo");
});

test("calendar loading error preserves the plan and empty state can restore approved data", async ({
  page,
}) => {
  await approveInitialWeek(page);
  const before = await names(approvedPlan(page));
  await page.getByText("Cenários da demonstração", { exact: true }).click();
  await selectOption(page, "Resultado das próximas operações", "Erro simulado");
  await page.getByRole("button", { name: "Recarregar calendário", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: "preservados" })).toBeVisible();
  expect(await names(approvedPlan(page))).toEqual(before);
  await selectOption(page, "Resultado das próximas operações", "Sem candidatos");
  await page.getByRole("button", { name: "Recarregar calendário", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Sua semana ainda está em branco", exact: true }),
  ).toBeVisible();
  await expect(approvedPlan(page)).not.toBeVisible();
  await selectOption(page, "Resultado das próximas operações", "Sucesso");
  await page.getByRole("button", { name: "Recarregar calendário", exact: true }).click();
  await expect(approvedPlan(page)).toBeVisible();
  expect(await names(approvedPlan(page))).toEqual(before);
});

test("visual QA covers responsive layouts, gallery, keyboard dialog focus and console", async ({
  page,
}) => {
  const browserErrors: string[] = [];
  page.on("pageerror", (error) => browserErrors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") browserErrors.push(message.text());
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByLabel("Nome (obrigatório)", { exact: true })).toBeVisible();
  await expect(page.getByLabel("Nome (obrigatório)", { exact: true })).toHaveCSS(
    "border-color",
    "rgb(133, 138, 130)",
  );
  await expect(page.getByRole("button", { name: "Continuar", exact: true })).toHaveCSS(
    "font-size",
    "14px",
  );
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: "test-results/qa-onboarding-mobile.png", fullPage: true });
  await approveInitialWeek(page);
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: "test-results/qa-calendar-desktop.png", fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: "test-results/qa-calendar-mobile.png", fullPage: true });
  for (const width of [320, 390, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
      `Calendar overflow at ${width}px`,
    ).toBe(true);
  }
  await page.setViewportSize({ width: 390, height: 844 });
  const details = approvedPlan(page)
    .getByRole("button", { name: /^Ver detalhes:/ })
    .first();
  await details.click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await page.screenshot({ path: "test-results/qa-dialog-mobile.png" });
  for (let index = 0; index < 12; index += 1) {
    await page.keyboard.press("Tab");
    expect(
      await page.evaluate(() => Boolean(document.activeElement?.closest('[role="dialog"]'))),
    ).toBe(true);
  }
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(details).toBeFocused();
  await page.getByRole("link", { name: "Galeria de componentes", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Ingredientes da interface.", exact: true }),
  ).toBeVisible();
  await expect(page.getByLabel("Campo com erro", { exact: true })).toHaveCSS(
    "border-color",
    "rgb(180, 35, 24)",
  );
  await expect(page.getByRole("button", { name: "Revisar exemplo", exact: true })).toHaveCSS(
    "font-size",
    "14px",
  );
  await page.getByRole("button", { name: "Revisar exemplo", exact: true }).click();
  await page.getByRole("dialog").getByRole("button", { name: "Aprovar", exact: true }).click();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  for (const width of [320, 390, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
      `Gallery overflow at ${width}px`,
    ).toBe(true);
  }
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.screenshot({ path: "test-results/qa-gallery-desktop.png", fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: "test-results/qa-gallery-mobile.png", fullPage: true });
  expect(browserErrors).toEqual([]);
});
