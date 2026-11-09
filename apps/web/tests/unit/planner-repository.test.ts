import { describe, expect, it } from "vitest";

import { createMockPlannerRepository } from "@/features/planner/data/mock-planner-repository";
import { emptyProfile, isChoiceBlocked, validateProfile } from "@/features/planner/model/rules";
import type { Profile } from "@/features/planner/model/types";

const success = { scenario: "success" } as const;
const error = { scenario: "error" } as const;
const conflict = { scenario: "conflict" } as const;
const empty = { scenario: "empty" } as const;
const profile = (): Profile => ({
  ...emptyProfile(),
  name: "Pessoa Exemplo",
  country: "Brasil",
  region: "Sudeste",
  restrictionsReviewed: true,
});
const repository = () => createMockPlannerRepository({ latencyMs: 0 });

async function approved() {
  const repo = repository();
  const proposal = (await repo.generateWeek(profile(), success))!;
  const snapshot = await repo.approveWeek(proposal.id, proposal.baseVersion, success);
  return { repo, snapshot, plan: snapshot.plan!, profile: snapshot.profile! };
}

describe("local planner domain", () => {
  it("validates an explicit restriction review, optional measurements and region coverage without diagnosing", () => {
    expect(validateProfile(emptyProfile())).toHaveProperty("restrictionsReviewed");
    expect(validateProfile(profile())).toEqual({});
    expect(validateProfile({ ...profile(), height: "invalid", weight: "0" })).toHaveProperty(
      "height",
    );
    expect(validateProfile({ ...profile(), country: "Portugal" })).toHaveProperty("country");
    expect(validateProfile({ ...profile(), region: "" })).toHaveProperty("region");
    expect(validateProfile({ ...profile(), region: "" }, "profile")).toEqual({});
  });

  it("keeps the onboarding profile as a draft until the complete proposal is approved", async () => {
    const repo = repository();
    const draft = { ...profile(), restrictions: ["vegan"], preferences: [] };
    const proposal = (await repo.generateWeek(draft, success))!;
    expect(await repo.getSnapshot(success)).toEqual({ profile: null, plan: null });
    expect(proposal.profile.restrictions).toEqual(["vegan"]);
    expect(proposal.plan.days).toHaveLength(7);
    expect(proposal.plan.days.every((day) => day.meals.length === 3)).toBe(true);
    expect(proposal.plan.days[0]!.date).toBe("2026-11-09");
    expect(proposal.plan.days[6]!.date).toBe("2026-11-15");
    const snapshot = await repo.approveWeek(proposal.id, proposal.baseVersion, success);
    expect(snapshot.profile?.restrictions).toEqual(["vegan"]);
    expect(snapshot.plan).not.toBeNull();
  });

  it("does not silently relax restrictions when favorites conflict or are skipped", async () => {
    const repo = repository();
    const proposal = (await repo.generateWeek(
      {
        ...profile(),
        restrictions: ["vegan", "lactose", "seafood"],
        preferences: ["chicken", "yogurt", "fish"],
      },
      success,
    ))!;
    expect(
      proposal.plan.days
        .flatMap((day) => day.meals)
        .every((meal) =>
          meal.excludes.every(
            (restriction) => !proposal.profile.restrictions.includes(restriction),
          ),
        ),
    ).toBe(true);
    expect(
      isChoiceBlocked({ id: "chicken", label: "Frango", blockedBy: ["vegan"] }, ["vegan"]),
    ).toBe(true);
  });

  it("returns no candidates for unsupported health conditions and rejects unsupported regions", async () => {
    const repo = repository();
    expect(
      await repo.generateWeek({ ...profile(), restrictions: ["diabetes"] }, success),
    ).toBeNull();
    expect(await repo.generateWeek({ ...profile(), restrictions: ["gluten"] }, success)).toBeNull();
    expect(await repo.generateWeek(profile(), empty)).toBeNull();
    await expect(
      repo.generateWeek({ ...profile(), country: "Portugal" }, success),
    ).rejects.toMatchObject({ code: "validation" });
    expect(await repo.getSnapshot(success)).toEqual({ profile: null, plan: null });
  });

  it("preserves the approved week when a new proposal is cancelled or generation fails", async () => {
    const { repo, snapshot } = await approved();
    const proposal = await repo.generateWeek(snapshot.profile!, success);
    expect(proposal).not.toBeNull();
    expect(await repo.getSnapshot(success)).toEqual(snapshot);
    await expect(repo.generateWeek(snapshot.profile!, error)).rejects.toMatchObject({
      code: "error",
    });
    expect(await repo.getSnapshot(success)).toEqual(snapshot);
  });

  it("preserves the current meal until approval and changes only the selected item", async () => {
    const { repo, plan, snapshot } = await approved();
    const day = plan.days[2]!;
    const meal = day.meals[1]!;
    const proposal = (await repo.generateMeal(plan.id, day.id, meal.id, success))!;
    expect(await repo.getSnapshot(success)).toEqual(snapshot);
    const result = await repo.approveMeal(proposal.id, proposal.baseVersion, success);
    expect(result.plan!.days[2]!.meals[1]!).toEqual(proposal.proposed);
    const unchangedBefore = plan.days
      .flatMap((item) => item.meals)
      .filter((item) => item.id !== meal.id);
    const unchangedAfter = result
      .plan!.days.flatMap((item) => item.meals)
      .filter((item) => item.id !== proposal.proposed.id);
    expect(unchangedAfter).toEqual(unchangedBefore);
  });

  it("retains a meal proposal on save failure and explicitly rebases after a simulated conflict", async () => {
    const { repo, plan } = await approved();
    const day = plan.days[0]!;
    const proposal = (await repo.generateMeal(plan.id, day.id, day.meals[0]!.id, success))!;
    await expect(repo.approveMeal(proposal.id, proposal.baseVersion, error)).rejects.toMatchObject({
      code: "error",
    });
    await expect(
      repo.approveMeal(proposal.id, proposal.baseVersion, conflict),
    ).rejects.toMatchObject({ code: "conflict" });
    await expect(
      repo.approveMeal(proposal.id, proposal.baseVersion, success),
    ).rejects.toMatchObject({ code: "conflict" });
    const refreshed = await repo.refreshMealProposal(proposal.id);
    expect(refreshed.proposed).toEqual(proposal.proposed);
    expect(refreshed.baseVersion).toBeGreaterThan(proposal.baseVersion);
    expect((await repo.getSnapshot(success)).plan!.days[0]!.meals[0]!).toEqual(proposal.current);
    const result = await repo.approveMeal(refreshed.id, refreshed.baseVersion, success);
    expect(result.plan!.days[0]!.meals[0]!).toEqual(proposal.proposed);
  });

  it("retains weekly proposals on failure and conflict until refreshed and approved", async () => {
    const { repo, snapshot } = await approved();
    const proposal = (await repo.generateWeek(snapshot.profile!, success))!;
    await expect(repo.approveWeek(proposal.id, proposal.baseVersion, error)).rejects.toMatchObject({
      code: "error",
    });
    expect(await repo.getSnapshot(success)).toEqual(snapshot);
    await expect(
      repo.approveWeek(proposal.id, proposal.baseVersion, conflict),
    ).rejects.toMatchObject({ code: "conflict" });
    const refreshed = await repo.refreshWeekProposal(proposal.id);
    const result = await repo.approveWeek(refreshed.id, refreshed.baseVersion, success);
    expect(result.plan!.days).toEqual(refreshed.plan.days);
  });

  it("requires revalidation when restrictions change and preserves pending plan on failed validation", async () => {
    const { repo, plan, profile: saved } = await approved();
    const snapshot = await repo.updateProfile(
      saved.id,
      saved.version,
      { ...saved, restrictions: ["vegan"] },
      success,
    );
    expect(snapshot.plan!.needsRevalidation).toBe(true);
    expect(snapshot.plan!.days).toEqual(plan.days);
    await expect(
      repo.revalidatePlan(plan.id, snapshot.plan!.version, success),
    ).rejects.toMatchObject({ code: "empty" });
    expect((await repo.getSnapshot(success)).plan!.needsRevalidation).toBe(true);
    await expect(
      repo.generateMeal(plan.id, plan.days[0]!.id, plan.days[0]!.meals[0]!.id, success),
    ).rejects.toMatchObject({ code: "validation" });
    const replacement = (await repo.generateWeek(snapshot.profile!, success))!;
    const approvedReplacement = await repo.approveWeek(
      replacement.id,
      replacement.baseVersion,
      success,
    );
    expect(approvedReplacement.plan!.needsRevalidation).toBe(false);
  });

  it("revalidates safely when a restriction is removed, without changing meals", async () => {
    const repo = repository();
    const proposal = (await repo.generateWeek({ ...profile(), restrictions: ["vegan"] }, success))!;
    const saved = await repo.approveWeek(proposal.id, proposal.baseVersion, success);
    const edited = await repo.updateProfile(
      saved.profile!.id,
      saved.profile!.version,
      { ...saved.profile!, restrictions: [] },
      success,
    );
    const plan = await repo.revalidatePlan(edited.plan!.id, edited.plan!.version, success);
    expect(plan.needsRevalidation).toBe(false);
    expect(plan.days).toEqual(saved.plan!.days);
  });

  it("returns copies and restores a deterministic empty demo", async () => {
    const { repo, snapshot } = await approved();
    snapshot.profile!.name = "Changed externally";
    expect((await repo.getSnapshot(success)).profile!.name).toBe("Pessoa Exemplo");
    const catalog = await repo.getCatalog();
    catalog.regions.length = 0;
    expect((await repo.getCatalog()).regions).toHaveLength(5);
    expect((await repo.getSnapshot(empty)).plan).toBeNull();
    expect((await repo.getSnapshot(success)).plan).not.toBeNull();
    await repo.reset();
    expect(await repo.getSnapshot(success)).toEqual({ profile: null, plan: null });
  });
});
