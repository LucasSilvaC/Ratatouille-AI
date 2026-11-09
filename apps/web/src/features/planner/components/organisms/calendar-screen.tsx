"use client";

import { CalendarDays, Leaf, MapPin, RefreshCw, Settings2 } from "lucide-react";
import Image from "next/image";

import { Alert } from "@/components/atoms/alert";
import { Button } from "@/components/atoms/button";
import { Card } from "@/components/atoms/card";
import { Label } from "@/components/atoms/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/atoms/select";
import { ReviewDialog } from "@/components/molecules/planner-dialog";
import {
  ApprovalActions,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from "@/components/molecules/planner-feedback";
import { mealPeriodLabels } from "@/features/planner/components/molecules/meal-card";
import { MealComparison } from "@/features/planner/components/organisms/meal-comparison";
import { WeeklyPlan } from "@/features/planner/components/organisms/weekly-plan";
import type { PlannerRepository } from "@/features/planner/model/contracts";
import type { Scenario, Snapshot } from "@/features/planner/model/types";
import { usePlan } from "@/features/planner/viewmodels/use-plan";

interface CalendarScreenProps {
  repository: PlannerRepository;
  snapshot: Snapshot;
  onSnapshot: (snapshot: Snapshot) => void;
  onEdit: () => void;
}

export function CalendarScreen({ repository, snapshot, onSnapshot, onEdit }: CalendarScreenProps) {
  const vm = usePlan({ repository, snapshot, onSnapshot });
  const { plan, profile } = snapshot;
  const busy = vm.pending !== null;
  const mealError = vm.error?.scope === "meal" ? vm.error : null;
  const weekError = vm.error?.scope === "week" ? vm.error : null;
  const currentMeal = vm.mealProposal?.current ?? vm.currentMeal;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-start justify-between gap-5">
        <PageHeader
          eyebrow="UM POUCO DE PLANEJAMENTO. MUITO SABOR."
          title="Sua semana, do seu jeito."
          description="Mais comida de verdade. Menos “o que eu vou comer hoje?”."
        />
        <div className="flex flex-wrap gap-3">
          <Button variant="outline" onClick={onEdit} disabled={busy || !!vm.weekProposal}>
            <Settings2 aria-hidden="true" className="size-4" />
            Editar perfil e preferências
          </Button>
          <Button onClick={vm.generateWeek} disabled={busy || !!vm.weekProposal}>
            <RefreshCw aria-hidden="true" className="size-4" />
            Gerar nova proposta
          </Button>
        </div>
      </div>

      <Card className="border-herb/15 bg-herb-soft relative overflow-hidden rounded-3xl p-6 sm:p-8 md:grid md:grid-cols-[1.2fr_0.8fr] md:gap-8">
        <div className="relative max-w-2xl space-y-4">
          <p className="text-herb flex items-center gap-2 text-sm font-semibold">
            <Leaf aria-hidden="true" className="size-4" />
            FEITO PARA A SUA ROTINA
          </p>
          <h2 className="text-3xl leading-tight font-semibold sm:text-4xl">
            Sabores familiares.
            <br />
            Espaço para suas escolhas.
          </h2>
          <p className="text-muted-foreground max-w-lg">
            {profile?.name ? `${profile.name}, sua` : "Sua"} semana começa com ingredientes da sua
            região e as informações que você compartilhou.
          </p>
          <div className="flex flex-wrap gap-2 text-sm">
            <span className="inline-flex items-center gap-1.5 rounded-full border bg-white px-3 py-1.5">
              <MapPin aria-hidden="true" className="size-4" />
              Região {plan?.region ?? profile?.region}
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full border bg-white px-3 py-1.5">
              <CalendarDays aria-hidden="true" className="size-4" />7 dias · 3 refeições por dia
            </span>
          </div>
        </div>
        <div className="relative mt-6 min-h-56 overflow-hidden rounded-2xl md:mt-0">
          <Image
            src="/illustrations/salada.jpg"
            alt="Fotografia ilustrativa de vegetais frescos em uma tigela; não representa os ingredientes do plano."
            fill
            sizes="(max-width: 767px) 90vw, 440px"
            className="object-cover"
            priority
          />
        </div>
      </Card>

      {vm.notice && <Alert className="border-herb/30 bg-herb-soft text-herb">{vm.notice}</Alert>}
      {vm.pending === "calendar" && <LoadingState message="Carregando seu cardápio…" />}
      {vm.error?.scope === "calendar" && (
        <ErrorState message={vm.error.message} onRetry={vm.reloadCalendar} />
      )}
      {plan?.needsRevalidation && (
        <Alert className="border-warning/30 bg-warning-soft text-warning space-y-3">
          <div>
            <strong>Seu plano precisa de uma nova revisão.</strong>
            <p className="mt-1">
              As restrições do perfil mudaram. As refeições anteriores estão pendentes de
              revalidação demonstrativa.
            </p>
          </div>
          <Button variant="outline" onClick={vm.revalidate} disabled={busy}>
            Revalidar plano
          </Button>
        </Alert>
      )}
      {vm.error?.scope === "plan" && (
        <div className="space-y-3">
          <ErrorState
            message={vm.error.message}
            onRetry={vm.error.conflict ? undefined : vm.revalidate}
          />
          {vm.error.conflict && (
            <Button variant="outline" onClick={vm.reloadPlan} disabled={busy}>
              Recarregar plano atual
            </Button>
          )}
        </div>
      )}
      {vm.pending === "plan" && (
        <LoadingState message="Revisando o plano com as restrições atualizadas…" />
      )}

      {vm.pending === "week" && (
        <LoadingState
          message={
            vm.weekProposal ? "Salvando alterações…" : "Preparando sugestões para sua semana…"
          }
        />
      )}
      {weekError && (
        <div className="space-y-3">
          <ErrorState
            message={weekError.message}
            onRetry={
              weekError.conflict ? undefined : vm.weekProposal ? vm.approveWeek : vm.generateWeek
            }
          />
          {weekError.conflict && (
            <Button variant="outline" onClick={() => vm.refreshReview("week")} disabled={busy}>
              Recarregar e revisar diferenças
            </Button>
          )}
        </div>
      )}
      {vm.empty === "week" && (
        <EmptyState
          title="Nenhuma proposta disponível"
          description="O catálogo demonstrativo não possui candidatos para estas informações. Suas restrições e sua semana atual foram preservadas."
        >
          <Button variant="outline" onClick={onEdit}>
            Revisar perfil e preferências
          </Button>
        </EmptyState>
      )}

      {vm.weekProposal && (
        <section
          className="border-primary/40 bg-primary-soft/40 space-y-6 rounded-3xl border-2 p-4 sm:p-6"
          aria-label="Revisão da nova proposta semanal"
        >
          <PageHeader
            eyebrow="EM REVISÃO"
            title="Aprovar nova proposta semanal?"
            description="Sua semana atual continua aprovada. Ao aprovar esta proposta, todas as 21 refeições serão substituídas."
          />
          <p className="text-muted-foreground text-sm">
            Atual: versão {plan?.version ?? 0} · Proposta: {vm.weekProposal.plan.days.length} dias ·
            Região {vm.weekProposal.plan.region}
          </p>
          <WeeklyPlan plan={vm.weekProposal.plan} interactive={false} />
          {weekError?.conflict && (
            <p className="text-warning text-sm">
              Recarregue a versão atual e revise as diferenças para liberar a aprovação.
            </p>
          )}
          <ApprovalActions
            onCancel={vm.cancelWeek}
            onApprove={vm.approveWeek}
            busy={vm.pending === "week"}
            disabled={!!weekError?.conflict}
          />
        </section>
      )}

      {plan ? (
        <section className="space-y-5" aria-label="Plano semanal aprovado">
          {vm.weekProposal && (
            <p className="bg-herb-soft text-herb rounded-xl px-4 py-3 font-semibold">
              Semana atual aprovada · mantida até a aprovação da proposta
            </p>
          )}
          <WeeklyPlan
            key={plan.id}
            plan={plan}
            onSwap={(dayId, mealId) => void vm.generateMeal(dayId, mealId)}
            onDetail={vm.openMeal}
            interactive={!vm.weekProposal}
            disabled={busy}
          />
        </section>
      ) : (
        <EmptyState
          title="Sua semana ainda está em branco"
          description="Prepare uma proposta para revisar as refeições antes de aprovar."
        >
          <Button onClick={vm.generateWeek} disabled={busy}>
            Criar meu cardápio
          </Button>
        </EmptyState>
      )}

      <aside className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border p-5">
        <div>
          <h2 className="text-lg font-semibold">Um plano que acompanha você.</h2>
          <p className="text-muted-foreground mt-1 text-sm">
            Experimente outra sugestão e revise antes de trocar. Suas escolhas aprovadas permanecem
            até a confirmação.
          </p>
        </div>
        <Button variant="outline" onClick={onEdit} disabled={busy || !!vm.weekProposal}>
          Ajustar preferências
        </Button>
      </aside>
      <p className="text-muted-foreground text-sm">
        Dados exclusivamente fictícios. Porções e valores nutricionais demonstrativos, sem cálculo
        nutricional ou validação clínica.
      </p>

      <details className="bg-muted rounded-2xl border p-4">
        <summary className="min-h-7 cursor-pointer text-sm font-semibold">
          Cenários da demonstração
        </summary>
        <div className="mt-4 max-w-md space-y-2">
          <Label htmlFor="calendar-scenario">Resultado das próximas operações</Label>
          <Select
            value={vm.scenario}
            onValueChange={(value) => vm.setScenario(value as Scenario)}
            disabled={busy}
          >
            <SelectTrigger id="calendar-scenario">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="success">Sucesso</SelectItem>
              <SelectItem value="error">Erro simulado</SelectItem>
              <SelectItem value="empty">Sem candidatos</SelectItem>
              <SelectItem value="conflict">Conflito ao aprovar</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-muted-foreground text-sm">
            O cenário é determinístico. Erro e conflito preservam a proposta para revisão.
          </p>
          <Button
            variant="outline"
            onClick={vm.reloadCalendar}
            disabled={busy || !!vm.weekProposal}
          >
            Recarregar calendário
          </Button>
        </div>
      </details>

      <ReviewDialog
        open={!!vm.selection}
        busy={busy}
        onOpenChange={(open) => {
          if (!open) vm.cancelMeal();
        }}
        title={
          vm.mealProposal
            ? `Revisar ${mealPeriodLabels[vm.mealProposal.current.period].toLowerCase()} de ${vm.selectedDay?.label.toLowerCase() ?? "seu dia"}`
            : "Detalhes da refeição"
        }
        description={
          vm.mealProposal
            ? "Ao aprovar, apenas esta refeição será substituída. Compare a atual e a proposta."
            : "Ingredientes, porções e valores são demonstrativos. Você pode solicitar outra sugestão."
        }
      >
        <div className="space-y-5">
          {currentMeal && (
            <MealComparison current={currentMeal} proposed={vm.mealProposal?.proposed} />
          )}
          {vm.pending === "meal" && (
            <LoadingState
              message={
                vm.mealProposal
                  ? "Salvando alterações…"
                  : "Buscando outra sugestão para esta refeição…"
              }
            />
          )}
          {mealError && <ErrorState message={mealError.message} />}
          {vm.empty === "meal" && (
            <EmptyState
              title="Nenhuma alternativa disponível"
              description="Não encontramos outra opção no catálogo demonstrativo para as restrições informadas. A refeição atual foi mantida."
            />
          )}
          <div className="bg-muted space-y-2 rounded-xl p-3">
            <Label htmlFor="meal-scenario">Cenário demonstrativo da troca</Label>
            <Select
              value={vm.scenario}
              onValueChange={(value) => vm.setScenario(value as Scenario)}
              disabled={busy}
            >
              <SelectTrigger id="meal-scenario">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="success">Sucesso</SelectItem>
                <SelectItem value="error">Erro simulado</SelectItem>
                <SelectItem value="empty">Sem candidatos</SelectItem>
                <SelectItem value="conflict">Conflito ao aprovar</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {mealError?.conflict && (
            <div className="space-y-2">
              <p className="text-warning text-sm">
                A refeição atual pode ter mudado. Recarregue e compare novamente antes de aprovar.
              </p>
              <Button variant="outline" onClick={() => vm.refreshReview("meal")} disabled={busy}>
                Recarregar e revisar diferenças
              </Button>
            </div>
          )}
          {vm.mealProposal ? (
            <ApprovalActions
              onCancel={vm.cancelMeal}
              onApprove={vm.approveMeal}
              busy={vm.pending === "meal"}
              disabled={!!mealError?.conflict}
            />
          ) : (
            <div className="flex flex-wrap justify-end gap-3">
              <Button variant="outline" onClick={vm.cancelMeal} disabled={busy}>
                Fechar
              </Button>
              <Button onClick={() => vm.generateMeal()} disabled={busy}>
                Trocar refeição
              </Button>
            </div>
          )}
          <p className="text-muted-foreground text-xs">
            A fotografia, quando disponível, é apenas ilustrativa e não comprova ingredientes.
          </p>
        </div>
      </ReviewDialog>
    </div>
  );
}
