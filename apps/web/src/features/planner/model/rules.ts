import type { Choice, Profile } from "./types";

export function emptyProfile(): Profile {
  return {
    id: "profile-demo",
    version: 0,
    name: "",
    height: "",
    weight: "",
    gender: "",
    country: "",
    region: "",
    restrictions: [],
    restrictionsReviewed: false,
    preferences: [],
  };
}

export function validateProfile(
  profile: Profile,
  scope: "profile" | "all" = "all",
): Record<string, string> {
  const errors: Record<string, string> = {};
  if (profile.name.trim().length < 2 || profile.name.trim().length > 80)
    errors.name = "Informe um nome entre 2 e 80 caracteres.";
  for (const [key, label, min, max] of [
    ["height", "altura em cm", 50, 250],
    ["weight", "peso em kg", 10, 400],
  ] as const) {
    const value = profile[key];
    if (
      value !== "" &&
      (!Number.isFinite(Number(value)) || Number(value) < min || Number(value) > max)
    )
      errors[key] = `Informe ${label} entre ${min} e ${max}, ou deixe em branco.`;
  }
  if (!profile.restrictionsReviewed)
    errors.restrictionsReviewed = "Revise as restrições e confirme que concluiu esta seção.";
  if (scope === "all") {
    if (profile.country !== "Brasil")
      errors.country = "O catálogo demonstrativo está disponível apenas para o Brasil.";
    if (!["Sudeste", "Sul", "Nordeste", "Norte", "Centro-Oeste"].includes(profile.region))
      errors.region = "Selecione uma das cinco regiões brasileiras.";
  }
  return errors;
}

export function isChoiceBlocked(choice: Choice, restrictions: string[]): boolean {
  return Boolean(choice.blockedBy?.some((restriction) => restrictions.includes(restriction)));
}

export function sameRestrictions(left: string[], right: string[]): boolean {
  return [...left].sort().join("|") === [...right].sort().join("|");
}

export class PlannerError extends Error {
  constructor(
    public readonly code: "error" | "conflict" | "validation" | "empty",
    message: string,
  ) {
    super(message);
    this.name = "PlannerError";
  }
}
