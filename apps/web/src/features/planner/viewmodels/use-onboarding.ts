"use client";

import { useState } from "react";

import { isChoiceBlocked, validateProfile } from "../model/rules";
import type { Scenario, WeekProposal } from "../model/types";

import type { PlannerSession } from "./use-session";

export function useOnboarding(session: PlannerSession) {
  const { draft, setDraft, step, setStep, repository, setSnapshot, setScreen, catalog } = session;
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [proposal, setProposal] = useState<WeekProposal | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [empty, setEmpty] = useState(false);
  const [conflict, setConflict] = useState(false);
  const [scenario, setScenario] = useState<Scenario>("success");
  const blockedReasons = Object.fromEntries(
    (catalog?.preferences.flatMap((group) => group.choices) ?? [])
      .filter((choice) => isChoiceBlocked(choice, draft.restrictions))
      .map((choice) => [choice.id, "Indisponível pelas restrições informadas."]),
  );
  function navigate(next: number) {
    if (busy) return;
    if (next >= 3) {
      void generate();
      return;
    }
    if (next > step) {
      const found = validateProfile(draft, step === 0 ? "profile" : "all");
      setErrors(found);
      if (Object.keys(found).length) return;
    }
    setProposal(null);
    setConflict(false);
    setStep(next);
    setError("");
    setEmpty(false);
  }
  async function generate(skip = false) {
    if (busy) return;
    const found = validateProfile(draft, "all");
    setErrors(found);
    if (Object.keys(found).length) return;
    const input = skip ? { ...draft, preferences: [] } : draft;
    if (skip) setDraft(input);
    setStep(3);
    setBusy(true);
    setError("");
    setEmpty(false);
    setProposal(null);
    setConflict(false);
    try {
      const generated = await repository.generateWeek(input, { scenario });
      setProposal(generated);
      setEmpty(!generated);
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Não foi possível gerar. Seus dados foram preservados.",
      );
    } finally {
      setBusy(false);
    }
  }
  async function approve() {
    if (!proposal || busy || conflict) return;
    setBusy(true);
    setError("");
    try {
      const saved = await repository.approveWeek(proposal.id, proposal.baseVersion, { scenario });
      setSnapshot(saved);
      if (saved.profile) setDraft(saved.profile);
      setProposal(null);
      setScreen("calendar");
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Não foi possível aprovar. Sua proposta continua aqui.",
      );
      if (cause instanceof Error && "code" in cause && cause.code === "conflict") setConflict(true);
    } finally {
      setBusy(false);
    }
  }
  async function refresh() {
    if (!proposal || busy) return;
    setBusy(true);
    try {
      setProposal(await repository.refreshWeekProposal(proposal.id));
      setConflict(false);
      setScenario("success");
      setError("Versão recarregada. Revise a proposta preservada antes de aprovar novamente.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Não foi possível recarregar.");
    } finally {
      setBusy(false);
    }
  }
  function cancel() {
    if (busy) return;
    setProposal(null);
    setConflict(false);
    setStep(2);
    setError("");
    setEmpty(false);
  }
  return {
    errors,
    proposal,
    busy,
    error,
    empty,
    conflict,
    scenario,
    setScenario,
    blockedReasons,
    navigate,
    generate,
    approve,
    refresh,
    cancel,
  };
}
