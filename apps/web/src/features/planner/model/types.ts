export type Scenario = "success" | "error" | "empty" | "conflict";
export type MealPeriod = "breakfast" | "lunch" | "dinner";
export interface Profile {
  id: string;
  version: number;
  name: string;
  height: string;
  weight: string;
  gender: string;
  country: string;
  region: string;
  restrictions: string[];
  restrictionsReviewed: boolean;
  preferences: string[];
}
export interface Choice {
  id: string;
  label: string;
  description?: string;
  blockedBy?: string[];
}
export interface ChoiceGroup {
  id: string;
  label: string;
  description: string;
  choices: Choice[];
}
export interface Catalog {
  countries: Choice[];
  regions: Choice[];
  restrictions: ChoiceGroup[];
  preferences: ChoiceGroup[];
}
export interface Meal {
  id: string;
  period: MealPeriod;
  name: string;
  ingredients: string[];
  portions: number;
  kcal: number;
  image?: string;
  excludes: string[];
}
export interface PlanDay {
  id: string;
  date: string;
  label: string;
  meals: Meal[];
}
export interface WeeklyPlan {
  id: string;
  version: number;
  profileVersion: number;
  region: string;
  needsRevalidation: boolean;
  days: PlanDay[];
}
export interface WeekProposal {
  id: string;
  baseVersion: number;
  profile: Profile;
  plan: WeeklyPlan;
}
export interface MealProposal {
  id: string;
  planId: string;
  baseVersion: number;
  dayId: string;
  currentMealId: string;
  current: Meal;
  proposed: Meal;
}
export interface Snapshot {
  profile: Profile | null;
  plan: WeeklyPlan | null;
}
export interface OperationContext {
  scenario: Scenario;
}
