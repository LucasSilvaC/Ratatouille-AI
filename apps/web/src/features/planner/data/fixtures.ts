import { PlannerError } from "../model/rules";
import type { Catalog, Choice, Meal, MealPeriod, Profile, WeeklyPlan } from "../model/types";

export const catalog: Catalog = {
  countries: ["Brasil", "Portugal", "Estados Unidos", "Argentina", "Outro"].map((label) => ({
    id: label,
    label,
  })),
  regions: [
    {
      id: "Sudeste",
      label: "Sudeste",
      description: "Arroz, feijão, couve, inhame e frutas tropicais.",
    },
    {
      id: "Sul",
      label: "Sul",
      description: "Polenta, batata-doce, maçã, moranga e folhas verdes.",
    },
    {
      id: "Nordeste",
      label: "Nordeste",
      description: "Cuscuz de milho, tapioca, macaxeira e jerimum.",
    },
    { id: "Norte", label: "Norte", description: "Mandioca, banana-da-terra e frutas regionais." },
    {
      id: "Centro-Oeste",
      label: "Centro-Oeste",
      description: "Milho, mandioca, abóbora e arroz com legumes.",
    },
  ],
  restrictions: [
    {
      id: "allergies",
      label: "Alergias",
      description: "O catálogo é ilustrativo e não avalia contaminação cruzada.",
      choices: [{ id: "seafood", label: "Alergia a frutos do mar" }],
    },
    {
      id: "intolerances",
      label: "Intolerâncias",
      description: "Registre as restrições que já conhece.",
      choices: [{ id: "lactose", label: "Intolerância à lactose" }],
    },
    {
      id: "health",
      label: "Condições de saúde",
      description:
        "Não há avaliação clínica. Estas condições não têm cobertura de cardápio nesta demonstração.",
      choices: [
        { id: "gluten", label: "Doença celíaca / restrição a glúten" },
        { id: "diabetes", label: "Diabetes / controle glicêmico" },
        { id: "hypertension", label: "Hipertensão / baixo sódio" },
        { id: "cholesterol", label: "Colesterol alto" },
        { id: "reflux", label: "Gastrite / refluxo" },
      ],
    },
    {
      id: "diet",
      label: "Escolhas alimentares",
      description: "Estas escolhas têm prioridade sobre os alimentos favoritos.",
      choices: [
        { id: "vegetarian", label: "Vegetariano" },
        { id: "vegan", label: "Vegano" },
      ],
    },
  ],
  preferences: [
    {
      id: "white-proteins",
      label: "Proteínas brancas",
      description: "Selecione quantas gostar.",
      choices: [
        { id: "chicken", label: "Frango grelhado", blockedBy: ["vegetarian", "vegan"] },
        { id: "tilapia", label: "Filé de tilápia", blockedBy: ["vegetarian", "vegan", "seafood"] },
        { id: "turkey", label: "Peito de peru", blockedBy: ["vegetarian", "vegan"] },
        { id: "eggs", label: "Ovos / omelete", blockedBy: ["vegan"] },
        { id: "fish", label: "Peixe assado", blockedBy: ["vegetarian", "vegan", "seafood"] },
      ],
    },
    {
      id: "alternative-proteins",
      label: "Proteínas alternativas",
      description: "Carnes, grãos e leguminosas.",
      choices: [
        { id: "beef", label: "Patinho grelhado", blockedBy: ["vegetarian", "vegan"] },
        { id: "beans", label: "Feijão tradicional" },
        { id: "chickpeas", label: "Grão-de-bico" },
        { id: "lentils", label: "Lentilha" },
        { id: "tofu", label: "Tofu grelhado" },
      ],
    },
    {
      id: "carbohydrates",
      label: "Carboidratos",
      description: "Bases para almoço e jantar.",
      choices: [
        { id: "rice", label: "Arroz branco" },
        { id: "brown-rice", label: "Arroz integral" },
        { id: "sweet-potato", label: "Batata-doce" },
        { id: "cassava", label: "Mandioquinha / mandioca" },
        { id: "quinoa", label: "Quinoa" },
      ],
    },
    {
      id: "vegetables",
      label: "Vegetais",
      description: "Legumes, folhas e acompanhamentos.",
      choices: [
        { id: "carrot", label: "Cenoura" },
        { id: "broccoli", label: "Brócolis" },
        { id: "zucchini", label: "Abobrinha" },
        { id: "pumpkin", label: "Abóbora" },
        { id: "salad", label: "Folhas verdes e tomate" },
      ],
    },
    {
      id: "breakfast",
      label: "Café da manhã",
      description: "Favoritos para começar o dia.",
      choices: [
        { id: "tapioca", label: "Tapioca" },
        { id: "couscous", label: "Cuscuz" },
        { id: "bread", label: "Pão integral", blockedBy: ["gluten"] },
        { id: "oats", label: "Aveia com frutas", blockedBy: ["gluten"] },
        { id: "yogurt", label: "Iogurte e frutas", blockedBy: ["lactose", "vegan", "gluten"] },
      ],
    },
  ],
};

const regional: Record<string, string> = {
  Sudeste: "Couve refogada",
  Sul: "Moranga assada",
  Nordeste: "Jerimum assado",
  Norte: "Banana-da-terra assada",
  "Centro-Oeste": "Milho cozido",
};
const weekdays = [
  "Segunda-feira",
  "Terça-feira",
  "Quarta-feira",
  "Quinta-feira",
  "Sexta-feira",
  "Sábado",
  "Domingo",
];

function rankedChoices(profile: Profile, groups: string[]): Choice[] {
  return catalog.preferences
    .filter((group) => groups.includes(group.id))
    .flatMap((group) => group.choices)
    .filter(
      (choice) =>
        !choice.blockedBy?.some((restriction) => profile.restrictions.includes(restriction)),
    )
    .sort(
      (left, right) =>
        Number(profile.preferences.includes(right.id)) -
        Number(profile.preferences.includes(left.id)),
    );
}

export function hasCandidateCoverage(profile: Profile): boolean {
  // Even the illustrated gluten exclusion is not clinical celiac coverage.
  return !profile.restrictions.some((id) =>
    ["gluten", "diabetes", "hypertension", "cholesterol", "reflux"].includes(id),
  );
}

export function makeMeal(profile: Profile, period: MealPeriod, index: number, id: string): Meal {
  const breakfast = rankedChoices(profile, ["breakfast"]);
  const proteins = rankedChoices(profile, ["white-proteins", "alternative-proteins"]);
  const bases = rankedChoices(profile, ["carbohydrates"]);
  const vegetables = rankedChoices(profile, ["vegetables"]);
  const at = (choices: Choice[], offset: number): Choice => {
    const choice = choices[offset % choices.length];
    if (!choice)
      throw new PlannerError("empty", "Não há candidatos neste grupo alimentar demonstrativo.");
    return choice;
  };
  const regionalIngredient = regional[profile.region];
  if (!regionalIngredient)
    throw new PlannerError("validation", "A região não tem cobertura demonstrativa.");
  let choices: Choice[];
  let ingredients: string[];
  let name: string;
  if (period === "breakfast") {
    const base = at(breakfast, index);
    choices = [base];
    ingredients = [base.label, "Banana", "Mamão", "Café sem açúcar"];
    name = `${base.label} com frutas da estação`;
  } else {
    const protein = at(proteins, index);
    const base = at(bases, index);
    const vegetable = at(vegetables, index);
    choices = [protein, base, vegetable];
    ingredients = [protein.label, base.label, vegetable.label, regionalIngredient];
    name = `${protein.label} com ${base.label.toLocaleLowerCase("pt-BR")}`;
  }
  return {
    id,
    period,
    name,
    ingredients,
    portions: 1,
    kcal: period === "breakfast" ? 310 + (index % 3) * 20 : 460 + (index % 5) * 25,
    excludes: [...new Set(choices.flatMap((choice) => choice.blockedBy ?? []))],
  };
}

export function makeWeek(profile: Profile, sequence: number, version: number): WeeklyPlan {
  return {
    id: "week-2026-11-09",
    version,
    profileVersion: profile.version,
    region: profile.region,
    needsRevalidation: false,
    days: weekdays.map((label, index) => ({
      id: `day-${index + 1}`,
      date: `2026-11-${String(index + 9).padStart(2, "0")}`,
      label,
      meals: (["breakfast", "lunch", "dinner"] as MealPeriod[]).map((period, slot) =>
        makeMeal(
          profile,
          period,
          index + sequence + slot,
          `day-${index + 1}-${period}-v${sequence}`,
        ),
      ),
    })),
  };
}
