"use client";

import { useState } from "react";

import { Alert } from "@/components/atoms/alert";
import { Button } from "@/components/atoms/button";
import { Card } from "@/components/atoms/card";
import { Input } from "@/components/atoms/input";
import { Label } from "@/components/atoms/label";
import { Skeleton } from "@/components/atoms/skeleton";
import { ReviewDialog } from "@/components/molecules/planner-dialog";
import {
  ApprovalActions,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from "@/components/molecules/planner-feedback";
import { MealCard } from "@/features/planner/components/molecules/meal-card";
import { OnboardingStepper } from "@/features/planner/components/molecules/onboarding-stepper";
import { PreferenceSelector } from "@/features/planner/components/organisms/preference-selector";
import { RegionSelector } from "@/features/planner/components/organisms/region-selector";
import { AppShell } from "@/features/planner/components/templates/app-shell";
import { usePlannerSession } from "@/features/planner/providers/planner-provider";
import { useGallery } from "@/features/planner/viewmodels/use-gallery";

export function ComponentGallery() {
  const session = usePlannerSession();
  const vm = useGallery(session);
  const [open, setOpen] = useState(false);
  const [notice, setNotice] = useState("");
  const [step, setStep] = useState(0);
  return (
    <AppShell gallery>
      <PageHeader
        eyebrow="REFERÊNCIA DO PRODUTO"
        title="Ingredientes da interface."
        description="Galeria demonstrativa dos mesmos componentes usados no aplicativo. As interações aqui não alteram seu perfil ou cardápio."
      />
      {notice && <Alert className="bg-herb-soft text-herb mb-6">{notice}</Alert>}
      <div className="gallery-grid">
        <Card className="gallery-section">
          <h2>Cores e superfícies</h2>
          <div className="grid grid-cols-2 gap-4">
            {[
              { name: "Creme", color: "#FAF8F5" },
              { name: "Terracota", color: "#B9472B" },
              { name: "Verde", color: "#2D6A4F" },
              { name: "Verde suave", color: "#EAF3EC" },
            ].map((item) => (
              <div key={item.name}>
                <div className="color-swatch" style={{ background: item.color }} />
                <p className="mt-2 text-sm font-semibold">{item.name}</p>
                <p className="text-muted-foreground text-xs">{item.color}</p>
              </div>
            ))}
          </div>
        </Card>
        <Card className="gallery-section">
          <h2>Tipografia</h2>
          <div>
            <h3 className="text-3xl">Outfit. Lugar à mesa.</h3>
            <p className="mt-3">Plus Jakarta Sans para leitura, instruções e controles.</p>
            <p className="text-muted-foreground mt-3 text-sm">
              Texto auxiliar com contraste e espaço para respirar.
            </p>
          </div>
          <h3>Ações compartilhadas</h3>
          <div className="flex flex-wrap gap-3">
            <Button onClick={() => setOpen(true)}>Revisar exemplo</Button>
            <Button
              variant="outline"
              onClick={() => setNotice("Ação secundária acionada na galeria.")}
            >
              Secundário
            </Button>
            <Button disabled>Indisponível</Button>
          </div>
        </Card>
        <Card className="gallery-section">
          <h2>Campos e orientação</h2>
          <div className="space-y-2">
            <Label htmlFor="gallery-name">Nome do perfil demonstrativo</Label>
            <Input
              id="gallery-name"
              placeholder="Como você prefere ser chamado?"
              value={vm.draft.name}
              onChange={(event) => vm.setDraft({ ...vm.draft, name: event.target.value })}
              aria-describedby="gallery-name-hint"
            />
            <p id="gallery-name-hint" className="text-muted-foreground text-sm">
              Campo editável apenas nesta galeria.
            </p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="gallery-error">Campo com erro</Label>
            <Input id="gallery-error" aria-invalid="true" aria-describedby="gallery-error-text" />
            <p id="gallery-error-text" className="field-error">
              Exemplo de mensagem associada ao campo.
            </p>
          </div>
        </Card>
        <Card className="gallery-section">
          <h2>Feedback e carregamento</h2>
          <Alert>Informação persistente no contexto da ação.</Alert>
          <ErrorState
            message="Exemplo de falha. Seus dados continuam preservados."
            onRetry={() => setNotice("Nova tentativa demonstrada.")}
          />
          <div className="space-y-3" aria-label="Exemplo de skeleton">
            <Skeleton className="h-5 w-3/4" />
            <Skeleton className="h-5 w-1/2" />
          </div>
        </Card>
      </div>
      <div className="mt-6 space-y-6">
        <Card className="gallery-section">
          <h2>Etapas e navegação</h2>
          <OnboardingStepper step={step} onStep={setStep} />
        </Card>
        {session.catalog && (
          <>
            <Card className="gallery-section">
              <RegionSelector profile={vm.draft} catalog={session.catalog} onChange={vm.setDraft} />
            </Card>
            <Card className="gallery-section">
              <PreferenceSelector
                profile={vm.draft}
                catalog={session.catalog}
                onChange={vm.setDraft}
                blockedReasons={vm.blockedReasons}
              />
            </Card>
          </>
        )}
        <div className="gallery-grid">
          <Card className="gallery-section">
            <h2>Card real de refeição</h2>
            {vm.meal ? (
              <MealCard
                meal={vm.meal}
                onDetail={() => setOpen(true)}
                onSwap={() => setOpen(true)}
              />
            ) : (
              <LoadingState message="Carregando exemplo de refeição…" />
            )}
            {vm.error && <ErrorState message={vm.error} />}
          </Card>
          <Card className="gallery-section">
            <h2>Estado vazio</h2>
            <EmptyState
              title="Sua semana está em branco"
              description="Um estado vazio explica o próximo passo, sem deixar você sem saída."
            >
              <Button onClick={() => setNotice("Ação do estado vazio acionada.")}>
                Experimentar ação
              </Button>
            </EmptyState>
          </Card>
        </div>
      </div>
      <ReviewDialog
        open={open}
        onOpenChange={setOpen}
        title="Aprovar exemplo da galeria?"
        description="Esta interação demonstra o padrão de revisão. Nenhum dado do seu plano será alterado."
      >
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="bg-muted rounded-xl p-4">
            <h3>Atual</h3>
            <p>Exemplo em demonstração</p>
          </div>
          <div className="bg-herb-soft rounded-xl p-4">
            <h3>Proposta</h3>
            <p>Confirmação do exemplo</p>
          </div>
        </div>
        <ApprovalActions
          onCancel={() => setOpen(false)}
          onApprove={() => {
            setOpen(false);
            setNotice("Exemplo aprovado na galeria. Seu plano foi preservado.");
          }}
        />
      </ReviewDialog>
    </AppShell>
  );
}
