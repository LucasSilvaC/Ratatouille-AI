import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { createMockPlannerRepository } from "@/features/planner/data/mock-planner-repository";
import type { PlannerRepository } from "@/features/planner/model/contracts";
import { emptyProfile } from "@/features/planner/model/rules";
import type { Profile } from "@/features/planner/model/types";
import { useOnboarding } from "@/features/planner/viewmodels/use-onboarding";
import { useProfileEditor } from "@/features/planner/viewmodels/use-profile-editor";
import { useSession } from "@/features/planner/viewmodels/use-session";

const injected = vi.hoisted(() => ({ repository: null as PlannerRepository | null }));
vi.mock("@/features/planner/composition", () => ({
  get plannerRepository() {
    return injected.repository;
  },
}));

const success = { scenario: "success" } as const;
const validDraft = (): Profile => ({
  ...emptyProfile(),
  name: "Pessoa Exemplo",
  country: "Brasil",
  region: "Sudeste",
  restrictionsReviewed: true,
});

function useFlow() {
  const session = useSession();
  return { session, onboarding: useOnboarding(session), editor: useProfileEditor(session) };
}

async function openFlow() {
  const hook = renderHook(useFlow);
  await waitFor(() => expect(hook.result.current.session.loading).toBe(false));
  return hook;
}

async function seedApproved() {
  const proposal = (await injected.repository!.generateWeek(validDraft(), success))!;
  return injected.repository!.approveWeek(proposal.id, proposal.baseVersion, success);
}

beforeEach(() => {
  injected.repository = createMockPlannerRepository({ latencyMs: 0 });
});

describe("planner ViewModel transitions", () => {
  it("regenerates a proposal after returning to edit onboarding fields", async () => {
    const { result } = await openFlow();
    act(() => result.current.session.setDraft(validDraft()));
    act(() => result.current.onboarding.navigate(3));
    await waitFor(() => expect(result.current.onboarding.busy).toBe(false));
    const firstProposal = result.current.onboarding.proposal;
    expect(firstProposal).not.toBeNull();
    act(() => result.current.onboarding.navigate(0));
    expect(result.current.onboarding.proposal).toBeNull();
    act(() =>
      result.current.session.setDraft({
        ...result.current.session.draft,
        name: "Novo nome fictício",
        restrictions: ["vegan"],
      }),
    );
    act(() => result.current.onboarding.navigate(3));
    await waitFor(() => expect(result.current.onboarding.busy).toBe(false));
    expect(result.current.onboarding.proposal?.id).not.toBe(firstProposal?.id);
    expect(result.current.onboarding.proposal?.profile.name).toBe("Novo nome fictício");
    expect(result.current.onboarding.proposal?.profile.restrictions).toEqual(["vegan"]);
    await act(async () => result.current.onboarding.approve());
    expect(result.current.session.snapshot.profile?.name).toBe("Novo nome fictício");
  });

  it("keeps the draft while moving forward and back and validates required fields", async () => {
    const { result } = await openFlow();
    act(() => result.current.onboarding.navigate(1));
    expect(result.current.session.step).toBe(0);
    expect(result.current.onboarding.errors).toHaveProperty("name");
    const draft = { ...validDraft(), restrictions: ["vegan"], preferences: ["beans", "rice"] };
    act(() => result.current.session.setDraft(draft));
    act(() => result.current.onboarding.navigate(1));
    expect(result.current.session.step).toBe(1);
    act(() => result.current.onboarding.navigate(2));
    act(() => result.current.onboarding.navigate(0));
    expect(result.current.session.draft).toEqual(draft);
    act(() => result.current.onboarding.navigate(1));
    expect(result.current.session.draft.restrictions).toEqual(["vegan"]);
  });

  it("skips preferences without losing restrictions or approving the draft prematurely", async () => {
    const { result } = await openFlow();
    act(() =>
      result.current.session.setDraft({
        ...validDraft(),
        restrictions: ["vegan"],
        preferences: ["beans", "rice"],
      }),
    );
    await act(async () => result.current.onboarding.generate(true));
    expect(result.current.session.draft.preferences).toEqual([]);
    expect(result.current.session.draft.restrictions).toEqual(["vegan"]);
    expect(result.current.onboarding.proposal?.profile.restrictions).toEqual(["vegan"]);
    expect(result.current.session.snapshot).toEqual({ profile: null, plan: null });
    act(() => result.current.onboarding.cancel());
    expect(result.current.session.step).toBe(2);
    expect(result.current.onboarding.proposal).toBeNull();
    expect(result.current.session.draft.restrictions).toEqual(["vegan"]);
  });

  it("keeps the initial proposal after failed approval and requires explicit conflict refresh", async () => {
    const { result } = await openFlow();
    act(() => result.current.session.setDraft(validDraft()));
    await act(async () => result.current.onboarding.generate());
    const proposal = result.current.onboarding.proposal;
    act(() => result.current.onboarding.setScenario("error"));
    await act(async () => result.current.onboarding.approve());
    expect(result.current.onboarding.proposal).toEqual(proposal);
    expect(result.current.session.screen).toBe("onboarding");
    act(() => result.current.onboarding.setScenario("conflict"));
    await act(async () => result.current.onboarding.approve());
    expect(result.current.onboarding.conflict).toBe(true);
    expect(result.current.onboarding.proposal).toEqual(proposal);
    act(() => result.current.onboarding.setScenario("success"));
    await act(async () => result.current.onboarding.approve());
    expect(result.current.session.snapshot.plan).toBeNull();
    await act(async () => result.current.onboarding.refresh());
    expect(result.current.onboarding.conflict).toBe(false);
    expect(result.current.onboarding.proposal?.baseVersion).toBeGreaterThan(proposal!.baseVersion);
    await act(async () => result.current.onboarding.approve());
    expect(result.current.session.screen).toBe("calendar");
    expect(result.current.session.snapshot.plan?.days).toHaveLength(7);
  });

  it("preserves profile edits while visiting the calendar and confirms discard", async () => {
    const approved = await seedApproved();
    const { result } = await openFlow();
    act(() => result.current.session.editProfile());
    const draft = { ...approved.profile!, name: "Outro nome fictício", preferences: ["lentils"] };
    act(() => result.current.session.setDraft(draft));
    expect(result.current.editor.dirty).toBe(true);
    act(() => result.current.session.setScreen("calendar"));
    act(() => result.current.session.editProfile());
    expect(result.current.session.draft).toEqual(draft);
    expect(result.current.session.snapshot.profile).toEqual(approved.profile);
    act(() => result.current.editor.cancel());
    expect(result.current.editor.discardOpen).toBe(true);
    act(() => result.current.editor.setDiscardOpen(false));
    expect(result.current.session.draft).toEqual(draft);
    act(() => result.current.editor.cancel());
    act(() => result.current.editor.discard());
    expect(result.current.session.draft).toEqual(approved.profile);
    expect(result.current.editor.dirty).toBe(false);
    expect(result.current.session.screen).toBe("calendar");
  });

  it("preserves an existing dirty draft when the calendar reloads a newer approved version", async () => {
    const approved = await seedApproved();
    const { result } = await openFlow();
    const draft = { ...approved.profile!, name: "Rascunho preservado" };
    act(() => result.current.session.editProfile());
    act(() => result.current.session.setDraft(draft));
    act(() => result.current.session.setScreen("calendar"));
    const newer = await injected.repository!.updateProfile(
      approved.profile!.id,
      approved.profile!.version,
      { ...approved.profile!, preferences: ["rice"] },
      success,
    );
    act(() => result.current.session.setSnapshot(newer));
    act(() => result.current.session.editProfile());
    expect(result.current.session.draft).toEqual(draft);
    await act(async () => result.current.editor.approve());
    expect(result.current.editor.conflict).toBe(true);
    expect(result.current.session.draft.name).toBe("Rascunho preservado");
  });

  it("keeps profile drafts after save failures and conflicts then marks changed restrictions for revalidation", async () => {
    const approved = await seedApproved();
    const { result } = await openFlow();
    act(() => result.current.session.editProfile());
    const draft = { ...approved.profile!, name: "Nome de demonstração", restrictions: ["vegan"] };
    act(() => result.current.session.setDraft(draft));
    act(() => result.current.editor.setScenario("error"));
    await act(async () => result.current.editor.approve());
    expect(result.current.session.draft).toEqual(draft);
    expect(result.current.session.snapshot).toEqual(approved);
    act(() => result.current.editor.setScenario("conflict"));
    await act(async () => result.current.editor.approve());
    expect(result.current.editor.conflict).toBe(true);
    expect(result.current.session.draft).toEqual(draft);
    await act(async () => result.current.editor.refresh());
    expect(result.current.session.draft.name).toBe(draft.name);
    expect(result.current.session.draft.restrictions).toEqual(["vegan"]);
    expect(result.current.session.draft.version).toBeGreaterThan(draft.version);
    await act(async () => result.current.editor.approve());
    expect(result.current.session.snapshot.profile?.name).toBe(draft.name);
    expect(result.current.session.snapshot.plan?.needsRevalidation).toBe(true);
    expect(result.current.session.snapshot.plan?.days).toEqual(approved.plan?.days);
    expect(result.current.session.screen).toBe("calendar");
  });
});
