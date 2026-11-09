import type {
  Catalog,
  MealProposal,
  OperationContext,
  Profile,
  Snapshot,
  WeekProposal,
  WeeklyPlan,
} from "./types";

export interface PlannerRepository {
  getCatalog(): Promise<Catalog>;
  getSnapshot(context: OperationContext): Promise<Snapshot>;
  updateProfile(
    profileId: string,
    expectedVersion: number,
    draft: Profile,
    context: OperationContext,
  ): Promise<Snapshot>;
  generateWeek(profile: Profile, context: OperationContext): Promise<WeekProposal | null>;
  approveWeek(
    proposalId: string,
    expectedVersion: number,
    context: OperationContext,
  ): Promise<Snapshot>;
  generateMeal(
    planId: string,
    dayId: string,
    mealId: string,
    context: OperationContext,
  ): Promise<MealProposal | null>;
  approveMeal(
    proposalId: string,
    expectedVersion: number,
    context: OperationContext,
  ): Promise<Snapshot>;
  refreshWeekProposal(proposalId: string): Promise<WeekProposal>;
  refreshMealProposal(proposalId: string): Promise<MealProposal>;
  revalidatePlan(
    planId: string,
    expectedVersion: number,
    context: OperationContext,
  ): Promise<WeeklyPlan>;
  reset(): Promise<void>;
}
