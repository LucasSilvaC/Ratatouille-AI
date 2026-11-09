"use client";

import { useRef, useState } from "react";

import type { PlannerRepository } from "../model/contracts";
import type { MealProposal, Scenario, Snapshot, WeekProposal } from "../model/types";

type Scope = "week" | "meal" | "plan" | "calendar";
interface Feedback {
  scope: Scope;
  message: string;
  conflict: boolean;
}
interface UsePlanOptions {
  repository: PlannerRepository;
  snapshot: Snapshot;
  onSnapshot: (snapshot: Snapshot) => void;
}

function failure(error: unknown, scope: Scope): Feedback {
  const message =
    error instanceof Error ? error.message : "Não foi possível concluir. Tente novamente.";
  const code =
    typeof error === "object" && error !== null && "code" in error ? String(error.code) : "";
  return { scope, message, conflict: /conflict/i.test(code) || /conflit|versão/i.test(message) };
}

export function usePlan({ repository, snapshot, onSnapshot }: UsePlanOptions) {
  const [scenario, setScenario] = useState<Scenario>("success");
  const [pending, setPending] = useState<Scope | null>(null);
  const lock = useRef(false);
  const [weekProposal, setWeekProposal] = useState<WeekProposal | null>(null);
  const [mealProposal, setMealProposal] = useState<MealProposal | null>(null);
  const [selection, setSelection] = useState<{ dayId: string; mealId: string } | null>(null);
  const [error, setError] = useState<Feedback | null>(null);
  const [empty, setEmpty] = useState<Scope | null>(null);
  const [notice, setNotice] = useState("");

  async function run(scope: Scope, command: () => Promise<void>) {
    if (lock.current) return;
    lock.current = true;
    setPending(scope);
    setError(null);
    setEmpty(null);
    setNotice("");
    try {
      await command();
    } catch (cause) {
      setError(failure(cause, scope));
    } finally {
      lock.current = false;
      setPending(null);
    }
  }

  const selectedDay = snapshot.plan?.days.find((day) => day.id === selection?.dayId);
  const currentMeal = selectedDay?.meals.find((meal) => meal.id === selection?.mealId);

  function openMeal(dayId: string, mealId: string) {
    if (lock.current) return;
    setSelection({ dayId, mealId });
    setMealProposal(null);
    setError(null);
    setEmpty(null);
  }

  function cancelMeal() {
    if (lock.current) return;
    setSelection(null);
    setMealProposal(null);
    setError(null);
    setEmpty(null);
  }

  function cancelWeek() {
    if (lock.current) return;
    setWeekProposal(null);
    setError(null);
    setEmpty(null);
    setNotice("Proposta descartada. Sua semana atual foi mantida.");
  }

  async function generateWeek() {
    if (!snapshot.profile) return;
    await run("week", async () => {
      const proposal = await repository.generateWeek(snapshot.profile!, { scenario });
      if (proposal) setWeekProposal(proposal);
      else setEmpty("week");
    });
  }

  async function approveWeek() {
    if (!weekProposal || error?.conflict) return;
    await run("week", async () => {
      const next = await repository.approveWeek(weekProposal.id, weekProposal.baseVersion, {
        scenario,
      });
      onSnapshot(next);
      setWeekProposal(null);
      setNotice("Nova semana aprovada. Seu cardápio foi atualizado.");
    });
  }

  async function generateMeal(dayId = selection?.dayId, mealId = selection?.mealId) {
    if (!snapshot.plan || !dayId || !mealId) return;
    if (!selection || selection.dayId !== dayId || selection.mealId !== mealId)
      openMeal(dayId, mealId);
    await run("meal", async () => {
      const proposal = await repository.generateMeal(snapshot.plan!.id, dayId, mealId, {
        scenario,
      });
      if (proposal) setMealProposal(proposal);
      else setEmpty("meal");
    });
  }

  async function approveMeal() {
    if (!mealProposal || error?.conflict) return;
    await run("meal", async () => {
      const next = await repository.approveMeal(mealProposal.id, mealProposal.baseVersion, {
        scenario,
      });
      onSnapshot(next);
      setMealProposal(null);
      setSelection(null);
      setNotice("Troca aprovada. Somente a refeição selecionada foi atualizada.");
    });
  }

  async function refreshReview(scope: "meal" | "week") {
    await run(scope, async () => {
      if (scope === "meal" && mealProposal) {
        const next = await repository.refreshMealProposal(mealProposal.id);
        setMealProposal(next);
        setSelection({ dayId: next.dayId, mealId: next.currentMealId });
      }
      if (scope === "week" && weekProposal)
        setWeekProposal(await repository.refreshWeekProposal(weekProposal.id));
      onSnapshot(await repository.getSnapshot({ scenario: "success" }));
      setScenario("success");
      setNotice("Versão atual recarregada. Compare os dados novamente antes de aprovar.");
    });
  }

  async function revalidate() {
    if (!snapshot.plan) return;
    await run("plan", async () => {
      await repository.revalidatePlan(snapshot.plan!.id, snapshot.plan!.version, { scenario });
      onSnapshot(await repository.getSnapshot({ scenario: "success" }));
      setNotice(
        "Revisão demonstrativa concluída. Este cardápio não substitui orientação profissional.",
      );
    });
  }

  async function reloadPlan() {
    await run("plan", async () => {
      onSnapshot(await repository.getSnapshot({ scenario: "success" }));
      setScenario("success");
      setNotice("Plano atual recarregado. Revise o aviso e solicite a revalidação novamente.");
    });
  }

  async function reloadCalendar() {
    await run("calendar", async () => {
      onSnapshot(await repository.getSnapshot({ scenario }));
    });
  }

  return {
    scenario,
    setScenario,
    pending,
    weekProposal,
    mealProposal,
    selection,
    selectedDay,
    currentMeal,
    error,
    empty,
    notice,
    openMeal,
    cancelMeal,
    cancelWeek,
    generateWeek,
    approveWeek,
    generateMeal,
    approveMeal,
    refreshReview,
    revalidate,
    reloadPlan,
    reloadCalendar,
  };
}
