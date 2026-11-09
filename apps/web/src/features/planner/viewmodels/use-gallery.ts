"use client";

import { useEffect, useState } from "react";

import { emptyProfile, isChoiceBlocked } from "../model/rules";
import type { WeeklyPlan } from "../model/types";

import type { PlannerSession } from "./use-session";

export function useGallery(session: PlannerSession) {
  const [draft, setDraft] = useState(emptyProfile);
  const [plan, setPlan] = useState<WeeklyPlan | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    void session.repository
      .generateWeek(
        {
          ...emptyProfile(),
          name: "Perfil fictício",
          country: "Brasil",
          region: "Sudeste",
          restrictionsReviewed: true,
        },
        { scenario: "success" },
      )
      .then((proposal) => {
        if (active) setPlan(proposal?.plan ?? null);
      })
      .catch((cause) => {
        if (active) setError(cause instanceof Error ? cause.message : "Exemplo indisponível.");
      });
    return () => {
      active = false;
    };
  }, [session.repository]);
  const blockedReasons = Object.fromEntries(
    (session.catalog?.preferences.flatMap((group) => group.choices) ?? [])
      .filter((choice) => isChoiceBlocked(choice, draft.restrictions))
      .map((choice) => [choice.id, "Indisponível pelas restrições informadas."]),
  );
  return {
    draft,
    setDraft,
    meal: (session.snapshot.plan ?? plan)?.days[0]?.meals[0],
    error,
    blockedReasons,
  };
}
