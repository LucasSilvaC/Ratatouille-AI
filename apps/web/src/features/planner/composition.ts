import { createMockPlannerRepository } from "./data/mock-planner-repository";
import type { PlannerRepository } from "./model/contracts";

// Replace this single adapter with an implementation of PlannerRepository to use an API.
export const plannerRepository: PlannerRepository = createMockPlannerRepository({ latencyMs: 650 });
