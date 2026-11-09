"use client";

import { ArrowLeft, ArrowRight, Leaf, MapPin } from "lucide-react";

import { Alert } from "@/components/atoms/alert";
import { Button } from "@/components/atoms/button";
import { Card } from "@/components/atoms/card";
import { ReviewDialog } from "@/components/molecules/planner-dialog";
import {
  ApprovalActions,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from "@/components/molecules/planner-feedback";
import { OnboardingStepper } from "@/features/planner/components/molecules/onboarding-stepper";
import { ScenarioSelector } from "@/features/planner/components/molecules/scenario-selector";
import { CalendarScreen } from "@/features/planner/components/organisms/calendar-screen";
import { PreferenceSelector } from "@/features/planner/components/organisms/preference-selector";
import { ProfileFields } from "@/features/planner/components/organisms/profile-fields";
import { RegionSelector } from "@/features/planner/components/organisms/region-selector";
import { WeeklyPlan } from "@/features/planner/components/organisms/weekly-plan";
import { AppShell } from "@/features/planner/components/templates/app-shell";
import { usePlannerSession } from "@/features/planner/providers/planner-provider";
import { useOnboarding } from "@/features/planner/viewmodels/use-onboarding";
import { useProfileEditor } from "@/features/planner/viewmodels/use-profile-editor";

export function PlannerApp() {
  const session = usePlannerSession();
  const onboarding = useOnboarding(session);
  const editor = useProfileEditor(session);
  const { catalog, draft, setDraft, step } = session;
  if (session.loading)
    return (
      <AppShell>
        <LoadingState message="Abrindo sua cozinha…" />
      </AppShell>
    );
  if (session.error || !catalog)
    return (
      <AppShell>
        <ErrorState
          message={session.error || "Catálogo indisponível."}
          onRetry={() => void session.load()}
        />
      </AppShell>
    );
  if (session.screen === "calendar")
    return (
      <AppShell>
        <CalendarScreen
          repository={session.repository}
          snapshot={session.snapshot}
          onSnapshot={session.setSnapshot}
          onEdit={session.editProfile}
        />
      </AppShell>
    );
  if (session.screen === "profile")
    return (
      <AppShell>
        <PageHeader
          eyebrow="O CARDÁPIO COMEÇA COM VOCÊ"
          title="Seus gostos têm lugar à mesa."
          description="Revise seu perfil, suas restrições e suas preferências antes de aprovar."
        />
        <div className="profile-layout">
          <aside className="profile-aside">
            <Leaf size={34} />
            <h2>Seu perfil</h2>
            <p>Região, preferências e restrições merecem seu próprio espaço.</p>
            <p className="demo-badge">Rascunho em edição</p>
            <Button variant="outline" onClick={() => session.setScreen("calendar")}>
              Ver cardápio e manter rascunho
            </Button>
          </aside>
          <form
            className="space-y-6"
            onSubmit={(event) => {
              event.preventDefault();
              void editor.approve();
            }}
          >
            <fieldset disabled={editor.busy} className="min-w-0 space-y-6">
              <Card className="p-6">
                <ProfileFields
                  profile={draft}
                  catalog={catalog}
                  errors={editor.errors}
                  onChange={setDraft}
                />
              </Card>
              <Card className="p-6">
                <RegionSelector profile={draft} catalog={catalog} onChange={setDraft} />
                {editor.errors.region && (
                  <p role="alert" className="field-error">
                    {editor.errors.region}
                  </p>
                )}
              </Card>
              <Card className="p-6">
                <PreferenceSelector
                  profile={draft}
                  catalog={catalog}
                  onChange={setDraft}
                  blockedReasons={editor.blockedReasons}
                />
              </Card>
              <Alert>
                Alterar restrições sinaliza a necessidade de revalidar o plano atual. A demonstração
                não oferece avaliação clínica.
              </Alert>
              <ScenarioSelector value={editor.scenario} onChange={editor.setScenario} />
            </fieldset>
            {editor.error && <ErrorState message={editor.error} />}
            {editor.conflict && (
              <Button
                variant="outline"
                disabled={editor.busy}
                onClick={() => void editor.refresh()}
              >
                Recarregar versão e revisar
              </Button>
            )}
            <div>
              <p className="text-muted-foreground mb-3 text-sm">
                Ao aprovar, os dados acima substituem o perfil aprovado.{" "}
                {editor.dirty ? "Há alterações no rascunho." : "Nenhuma alteração pendente."}
              </p>
              <ApprovalActions
                onCancel={editor.cancel}
                onApprove={() => void editor.approve()}
                busy={editor.busy}
                disabled={!editor.dirty || editor.conflict}
              />
            </div>
          </form>
        </div>
        <ReviewDialog
          open={editor.discardOpen}
          onOpenChange={editor.setDiscardOpen}
          title="Descartar alterações?"
          description="Ao aprovar, o rascunho será descartado e o perfil aprovado será mantido."
        >
          <ApprovalActions
            onCancel={() => editor.setDiscardOpen(false)}
            onApprove={editor.discard}
          />
        </ReviewDialog>
      </AppShell>
    );
  const titles = [
    "Vamos preparar sua semana?",
    "Sabores de perto de você.",
    "O que você gosta de comer?",
    "Uma proposta para sua mesa.",
  ];
  const descriptions = [
    "Conte um pouco sobre você. Use apenas dados fictícios nesta demonstração.",
    "Escolha sua localização para explorar o catálogo regional demonstrativo.",
    "Selecione seus favoritos ou pule por enquanto. Suas restrições vêm primeiro.",
    "Revise os sete dias antes de confirmar seu primeiro cardápio.",
  ];
  return (
    <AppShell>
      <div
        className={
          step === 3 && onboarding.proposal ? "space-y-8" : "onboarding-container space-y-8"
        }
      >
        <OnboardingStepper
          step={step}
          onStep={(next) => onboarding.navigate(Math.min(next, step + 1))}
        />
        <PageHeader
          eyebrow="UM POUCO DE PLANEJAMENTO. MUITO SABOR."
          title={titles[step] ?? "Seu cardápio"}
          description={descriptions[step]}
        />
        {step < 3 && (
          <Card className="onboarding-panel p-5 sm:p-8">
            <form
              onSubmit={(event) => {
                event.preventDefault();
                if (step === 2) void onboarding.generate();
                else onboarding.navigate(step + 1);
              }}
            >
              <fieldset disabled={onboarding.busy} className="min-w-0">
                {step === 0 && (
                  <ProfileFields
                    profile={draft}
                    catalog={catalog}
                    errors={onboarding.errors}
                    onChange={setDraft}
                  />
                )}
                {step === 1 && (
                  <>
                    <RegionSelector profile={draft} catalog={catalog} onChange={setDraft} />
                    {Object.entries(onboarding.errors)
                      .filter(([key]) => key === "country" || key === "region")
                      .map(([key, message]) => (
                        <p className="field-error" role="alert" key={key}>
                          {message}
                        </p>
                      ))}
                  </>
                )}
                {step === 2 && (
                  <>
                    <PreferenceSelector
                      profile={draft}
                      catalog={catalog}
                      onChange={setDraft}
                      blockedReasons={onboarding.blockedReasons}
                    />
                    <div className="profile-summary">
                      <MapPin size={20} />
                      <div>
                        <strong>
                          {draft.name} · {draft.region}, {draft.country}
                        </strong>
                        <p>
                          {draft.restrictions.length} restrição(ões) informada(s). Preferências não
                          substituem restrições.
                        </p>
                        <Button variant="ghost" size="sm" onClick={() => onboarding.navigate(0)}>
                          Revisar dados
                        </Button>
                      </div>
                    </div>
                    <ScenarioSelector
                      value={onboarding.scenario}
                      onChange={onboarding.setScenario}
                    />
                  </>
                )}
                <div className="mt-8 flex flex-wrap justify-between gap-3 border-t pt-6">
                  {step > 0 ? (
                    <Button variant="outline" onClick={() => onboarding.navigate(step - 1)}>
                      <ArrowLeft size={18} />
                      Voltar
                    </Button>
                  ) : (
                    <span />
                  )}
                  <div className="flex flex-wrap gap-3">
                    {step === 2 && (
                      <Button variant="outline" onClick={() => void onboarding.generate(true)}>
                        Pular por enquanto
                      </Button>
                    )}
                    <Button type="submit">
                      {step === 2 ? "Gerar cardápio" : "Continuar"}
                      <ArrowRight size={18} />
                    </Button>
                  </div>
                </div>
              </fieldset>
            </form>
          </Card>
        )}
        {step === 3 && (
          <>
            <Alert>
              Proposta demonstrativa · {draft.region} · Valores por porção são exemplos, sem cálculo
              ou validação nutricional.
            </Alert>
            {onboarding.busy && (
              <LoadingState
                message={
                  onboarding.proposal
                    ? "Salvando alterações…"
                    : "Preparando sugestões para sua semana…"
                }
              />
            )}
            {onboarding.error && (
              <ErrorState
                message={onboarding.error}
                onRetry={!onboarding.proposal ? () => void onboarding.generate() : undefined}
              />
            )}
            {onboarding.empty && (
              <EmptyState
                title="Nenhum candidato disponível"
                description="O catálogo demonstrativo não atende aos dados informados. Você pode revisar os dados ou tentar outro cenário. Não remova restrições de saúde para obter sugestões."
              />
            )}
            {onboarding.proposal && (
              <section className="space-y-6" aria-label="Proposta inicial">
                <h2>Proposta · 9 a 15 de novembro de 2026</h2>
                <WeeklyPlan plan={onboarding.proposal.plan} interactive={false} />
                <p>Ao aprovar, este perfil e esta semana serão confirmados juntos.</p>
                {onboarding.conflict && (
                  <Button
                    variant="outline"
                    disabled={onboarding.busy}
                    onClick={() => void onboarding.refresh()}
                  >
                    Recarregar versão e revisar
                  </Button>
                )}
                <ApprovalActions
                  onCancel={onboarding.cancel}
                  onApprove={() => void onboarding.approve()}
                  busy={onboarding.busy}
                  disabled={onboarding.conflict}
                />
              </section>
            )}
            {!onboarding.busy && (
              <>
                <ScenarioSelector value={onboarding.scenario} onChange={onboarding.setScenario} />
                {!onboarding.proposal && (
                  <Button variant="outline" onClick={onboarding.cancel}>
                    Voltar às preferências
                  </Button>
                )}
              </>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}
