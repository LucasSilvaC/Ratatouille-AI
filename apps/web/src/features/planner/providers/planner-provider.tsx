"use client";

import { createContext, useContext } from "react";

import { useSession, type PlannerSession } from "@/features/planner/viewmodels/use-session";

const PlannerContext = createContext<PlannerSession | null>(null);
export function PlannerProvider({ children }: { children: React.ReactNode }) {
  const session = useSession();
  return <PlannerContext.Provider value={session}>{children}</PlannerContext.Provider>;
}
export function usePlannerSession() {
  const session = useContext(PlannerContext);
  if (!session) throw new Error("PlannerProvider ausente.");
  return session;
}
