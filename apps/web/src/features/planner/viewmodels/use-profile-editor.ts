"use client";

import { useState } from "react";

import { isChoiceBlocked, validateProfile } from "../model/rules";
import type { Scenario } from "../model/types";

import type { PlannerSession } from "./use-session";

export function useProfileEditor(session: PlannerSession) {
  const { draft, catalog, snapshot, repository, setSnapshot, setDraft, setScreen } = session;
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [scenario, setScenario] = useState<Scenario>("success");
  const [discardOpen, setDiscardOpen] = useState(false);
  const [conflict, setConflict] = useState(false);
  const dirty = snapshot.profile
    ? JSON.stringify(draft) !== JSON.stringify(snapshot.profile)
    : false;
  const blockedReasons = Object.fromEntries(
    (catalog?.preferences.flatMap((group) => group.choices) ?? [])
      .filter((choice) => isChoiceBlocked(choice, draft.restrictions))
      .map((choice) => [choice.id, "Indisponível pelas restrições informadas."]),
  );
  function cancel() {
    if (dirty) setDiscardOpen(true);
    else setScreen("calendar");
  }
  function discard() {
    if (snapshot.profile) setDraft(snapshot.profile);
    setDiscardOpen(false);
    setError("");
    setConflict(false);
    setScreen("calendar");
  }
  async function approve() {
    if (busy || conflict || !snapshot.profile) return;
    const found = validateProfile(draft, "all");
    setErrors(found);
    if (Object.keys(found).length) {
      setError("Revise os campos indicados antes de aprovar.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const saved = await repository.updateProfile(snapshot.profile.id, draft.version, draft, {
        scenario,
      });
      setSnapshot(saved);
      if (saved.profile) setDraft(saved.profile);
      setScreen("calendar");
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Não foi possível salvar. O rascunho continua aqui.",
      );
      if (cause instanceof Error && "code" in cause && cause.code === "conflict") setConflict(true);
    } finally {
      setBusy(false);
    }
  }
  async function refresh() {
    setBusy(true);
    try {
      const latest = await repository.getSnapshot({ scenario: "success" });
      setSnapshot(latest);
      if (latest.profile) setDraft({ ...draft, version: latest.profile.version });
      setConflict(false);
      setScenario("success");
      setError(
        "Versão atual recarregada. Seu rascunho foi preservado; revise os dados antes de aprovar novamente.",
      );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Não foi possível recarregar.");
    } finally {
      setBusy(false);
    }
  }
  return {
    errors,
    busy,
    error,
    scenario,
    setScenario,
    discardOpen,
    setDiscardOpen,
    dirty,
    conflict,
    blockedReasons,
    cancel,
    discard,
    approve,
    refresh,
  };
}
