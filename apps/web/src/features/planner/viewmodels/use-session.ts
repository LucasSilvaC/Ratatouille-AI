"use client";

import { useCallback, useEffect, useState } from "react";

import { plannerRepository } from "../composition";
import { emptyProfile } from "../model/rules";
import type { Catalog, Profile, Snapshot } from "../model/types";

export function useSession() {
  const [snapshot, setSnapshot] = useState<Snapshot>({ profile: null, plan: null });
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [draft, setDraft] = useState<Profile>(emptyProfile);
  const [screen, setScreen] = useState<"onboarding" | "calendar" | "profile">("onboarding");
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = useCallback(() => {
    return Promise.all([
      plannerRepository.getCatalog(),
      plannerRepository.getSnapshot({ scenario: "success" }),
    ])
      .then(([nextCatalog, nextSnapshot]) => {
        setCatalog(nextCatalog);
        setError("");
        setSnapshot(nextSnapshot);
        if (nextSnapshot.profile) setDraft(nextSnapshot.profile);
        setScreen(nextSnapshot.plan ? "calendar" : "onboarding");
      })
      .catch((cause: unknown) => {
        setError(cause instanceof Error ? cause.message : "Não foi possível abrir a demonstração.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);
  useEffect(() => {
    void load();
  }, [load]);
  function editProfile() {
    // A draft is preserved while visiting the calendar and the component gallery.
    setScreen("profile");
  }
  function applySnapshot(next: Snapshot) {
    // Follow newer approved versions only when there are no unsaved edits.
    setDraft((current) =>
      snapshot.profile &&
      JSON.stringify(current) === JSON.stringify(snapshot.profile) &&
      next.profile
        ? next.profile
        : current,
    );
    setSnapshot(next);
  }
  async function reset() {
    setLoading(true);
    await plannerRepository.reset();
    setDraft(emptyProfile());
    setStep(0);
    await load();
  }
  async function reload() {
    setLoading(true);
    setError("");
    await load();
  }
  return {
    repository: plannerRepository,
    snapshot,
    setSnapshot: applySnapshot,
    catalog,
    draft,
    setDraft,
    screen,
    setScreen,
    step,
    setStep,
    loading,
    error,
    load: reload,
    editProfile,
    reset,
  };
}
export type PlannerSession = ReturnType<typeof useSession>;
