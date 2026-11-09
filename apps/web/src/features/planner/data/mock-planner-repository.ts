import type { PlannerRepository } from "../model/contracts";
import { PlannerError, sameRestrictions, validateProfile } from "../model/rules";
import type {
  MealProposal,
  OperationContext,
  Profile,
  Snapshot,
  WeekProposal,
  WeeklyPlan,
} from "../model/types";

import { catalog, hasCandidateCoverage, makeMeal, makeWeek } from "./fixtures";

const copy = <T>(value: T): T => structuredClone(value);
const success: OperationContext = { scenario: "success" };

/** One instance owns all approved data and proposals; never instantiate this inside a hook. */
export function createMockPlannerRepository({
  latencyMs = 650,
}: { latencyMs?: number } = {}): PlannerRepository {
  let state: Snapshot = { profile: null, plan: null };
  let revision = 0;
  let sequence = 0;
  const weekProposals = new Map<string, WeekProposal>();
  const mealProposals = new Map<string, MealProposal>();
  const wait = () => new Promise<void>((resolve) => setTimeout(resolve, latencyMs));

  async function prepare(context: OperationContext = success): Promise<void> {
    await wait();
    if (context.scenario === "error")
      throw new PlannerError(
        "error",
        "Não foi possível concluir a operação demonstrativa. Seus dados e propostas foram preservados.",
      );
  }

  function assertProfile(profile: Profile): void {
    const errors = validateProfile(profile);
    if (Object.keys(errors).length)
      throw new PlannerError("validation", Object.values(errors).join(" "));
    const knownRestrictions = catalog.restrictions.flatMap((group) =>
      group.choices.map((choice) => choice.id),
    );
    if (profile.restrictions.some((id) => !knownRestrictions.includes(id)))
      throw new PlannerError(
        "validation",
        "Há uma restrição sem cobertura no catálogo demonstrativo.",
      );
  }

  function simulateConflict(context: OperationContext): void {
    if (context.scenario !== "conflict") return;
    revision += 1;
    if (state.profile) state.profile.version += 1;
    if (state.plan) state.plan.version = revision;
    throw new PlannerError(
      "conflict",
      "Conflito de versão simulado. Recarregue os dados atuais e revise a proposta antes de aprovar novamente.",
    );
  }

  function assertRevision(expected: number): void {
    if (expected !== revision)
      throw new PlannerError(
        "conflict",
        "A versão atual mudou. Recarregue e revise a proposta preservada.",
      );
  }

  function requirePlan(planId: string): WeeklyPlan {
    if (!state.plan || state.plan.id !== planId)
      throw new PlannerError("validation", "O plano solicitado não está disponível.");
    return state.plan;
  }

  function requireWeekProposal(proposalId: string): WeekProposal {
    const proposal = weekProposals.get(proposalId);
    if (!proposal)
      throw new PlannerError(
        "validation",
        "A proposta semanal não está mais disponível. Gere uma nova proposta.",
      );
    return proposal;
  }

  function requireMealProposal(proposalId: string): MealProposal {
    const proposal = mealProposals.get(proposalId);
    if (!proposal)
      throw new PlannerError(
        "validation",
        "A proposta de troca não está mais disponível. Gere uma nova alternativa.",
      );
    return proposal;
  }

  return {
    async getCatalog() {
      await wait();
      return copy(catalog);
    },
    async getSnapshot(context) {
      await prepare(context);
      return copy(context.scenario === "empty" ? { profile: state.profile, plan: null } : state);
    },
    async updateProfile(profileId, expectedVersion, draft, context) {
      await prepare(context);
      if (!state.profile || state.profile.id !== profileId)
        throw new PlannerError("validation", "Perfil aprovado não encontrado.");
      assertProfile(draft);
      simulateConflict(context);
      if (state.profile.version !== expectedVersion)
        throw new PlannerError(
          "conflict",
          "O perfil mudou. Recarregue a versão atual e revise seu rascunho.",
        );
      const changed =
        !sameRestrictions(state.profile.restrictions, draft.restrictions) ||
        state.profile.region !== draft.region;
      state.profile = {
        ...copy(draft),
        id: profileId,
        version: expectedVersion + 1,
        name: draft.name.trim(),
      };
      revision += 1;
      if (state.plan) {
        state.plan.version = revision;
        state.plan.needsRevalidation = state.plan.needsRevalidation || changed;
        if (!state.plan.needsRevalidation) state.plan.profileVersion = state.profile.version;
      }
      return copy(state);
    },
    async generateWeek(profile, context) {
      await prepare(context);
      assertProfile(profile);
      if (context.scenario === "empty" || !hasCandidateCoverage(profile)) return null;
      sequence += 1;
      const proposal: WeekProposal = {
        id: `week-proposal-${sequence}`,
        baseVersion: revision,
        profile: copy(profile),
        plan: makeWeek(profile, sequence, revision + 1),
      };
      weekProposals.set(proposal.id, proposal);
      return copy(proposal);
    },
    async approveWeek(proposalId, expectedVersion, context) {
      await prepare(context);
      const proposal = requireWeekProposal(proposalId);
      simulateConflict(context);
      assertRevision(expectedVersion);
      assertRevision(proposal.baseVersion);
      if (state.profile && proposal.profile.version !== state.profile.version)
        throw new PlannerError(
          "conflict",
          "O perfil mudou desde a geração. Recarregue e revise a proposta.",
        );
      assertProfile(proposal.profile);
      if (!hasCandidateCoverage(proposal.profile))
        throw new PlannerError(
          "empty",
          "Não há cobertura demonstrativa para as condições informadas.",
        );
      const profile = {
        ...copy(proposal.profile),
        name: proposal.profile.name.trim(),
        version: state.profile?.version ?? 1,
      };
      revision += 1;
      state = {
        profile,
        plan: { ...copy(proposal.plan), version: revision, profileVersion: profile.version },
      };
      weekProposals.delete(proposalId);
      return copy(state);
    },
    async generateMeal(planId, dayId, mealId, context) {
      await prepare(context);
      const plan = requirePlan(planId);
      const current = plan.days
        .find((day) => day.id === dayId)
        ?.meals.find((meal) => meal.id === mealId);
      if (!current || !state.profile)
        throw new PlannerError("validation", "Refeição não encontrada no plano aprovado.");
      if (plan.needsRevalidation)
        throw new PlannerError(
          "validation",
          "O plano precisa de revalidação. Gere uma nova proposta com as restrições atuais.",
        );
      if (context.scenario === "empty" || !hasCandidateCoverage(state.profile)) return null;
      sequence += 1;
      let alternative = makeMeal(
        state.profile,
        current.period,
        sequence,
        `meal-alternative-${sequence}`,
      );
      for (let index = 1; alternative.name === current.name && index < 12; index += 1)
        alternative = makeMeal(
          state.profile,
          current.period,
          sequence + index,
          `meal-alternative-${sequence}`,
        );
      if (alternative.name === current.name) return null;
      const proposal: MealProposal = {
        id: `meal-proposal-${sequence}`,
        planId,
        baseVersion: revision,
        dayId,
        currentMealId: mealId,
        current: copy(current),
        proposed: alternative,
      };
      mealProposals.set(proposal.id, proposal);
      return copy(proposal);
    },
    async approveMeal(proposalId, expectedVersion, context) {
      await prepare(context);
      const proposal = requireMealProposal(proposalId);
      simulateConflict(context);
      assertRevision(expectedVersion);
      assertRevision(proposal.baseVersion);
      const plan = requirePlan(proposal.planId);
      if (plan.needsRevalidation)
        throw new PlannerError(
          "conflict",
          "As restrições mudaram. Revalide o plano ou gere uma nova semana antes desta troca.",
        );
      const day = plan.days.find((item) => item.id === proposal.dayId);
      const mealIndex = day?.meals.findIndex((meal) => meal.id === proposal.currentMealId) ?? -1;
      if (!day || mealIndex < 0)
        throw new PlannerError(
          "conflict",
          "A refeição atual mudou. Recarregue a proposta para revisar a diferença.",
        );
      day.meals[mealIndex] = copy(proposal.proposed);
      revision += 1;
      plan.version = revision;
      mealProposals.delete(proposalId);
      return copy(state);
    },
    async refreshWeekProposal(proposalId) {
      await wait();
      const proposal = requireWeekProposal(proposalId);
      // A profile change requires regenerating the content against those restrictions.
      if (state.profile && proposal.profile.version !== state.profile.version) {
        if (!hasCandidateCoverage(state.profile))
          throw new PlannerError(
            "empty",
            "O perfil atual não tem cobertura demonstrativa. Sua proposta anterior foi preservada.",
          );
        proposal.profile = copy(state.profile);
        proposal.plan = makeWeek(state.profile, ++sequence, revision + 1);
      }
      proposal.baseVersion = revision;
      return copy(proposal);
    },
    async refreshMealProposal(proposalId) {
      await wait();
      const proposal = requireMealProposal(proposalId);
      const plan = requirePlan(proposal.planId);
      if (plan.needsRevalidation)
        throw new PlannerError(
          "conflict",
          "O plano precisa de revalidação por mudança de restrições. Sua proposta foi preservada.",
        );
      const current = plan.days
        .find((day) => day.id === proposal.dayId)
        ?.meals.find((meal) => meal.period === proposal.current.period);
      if (!current)
        throw new PlannerError(
          "conflict",
          "A refeição atual não foi encontrada. Sua proposta foi preservada.",
        );
      proposal.current = copy(current);
      proposal.currentMealId = current.id;
      proposal.baseVersion = revision;
      return copy(proposal);
    },
    async revalidatePlan(planId, expectedVersion, context) {
      await prepare(context);
      const plan = requirePlan(planId);
      simulateConflict(context);
      assertRevision(expectedVersion);
      if (
        !state.profile ||
        context.scenario === "empty" ||
        !hasCandidateCoverage(state.profile) ||
        plan.days.some((day) =>
          day.meals.some((meal) =>
            meal.excludes.some((restriction) => state.profile!.restrictions.includes(restriction)),
          ),
        )
      ) {
        throw new PlannerError(
          "empty",
          "Este plano não atende aos filtros demonstrativos atuais. Gere uma nova proposta; nenhuma restrição será removida.",
        );
      }
      if (plan.region !== state.profile.region)
        throw new PlannerError(
          "empty",
          "A região mudou. Gere uma nova proposta para o catálogo da região atual.",
        );
      revision += 1;
      plan.version = revision;
      plan.profileVersion = state.profile.version;
      plan.needsRevalidation = false;
      return copy(plan);
    },
    async reset() {
      await wait();
      state = { profile: null, plan: null };
      revision = 0;
      sequence = 0;
      weekProposals.clear();
      mealProposals.clear();
    },
  };
}
