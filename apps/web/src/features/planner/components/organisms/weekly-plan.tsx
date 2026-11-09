"use client";

import { useId, useState } from "react";

import { Button } from "@/components/atoms/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/atoms/tabs";
import { MealCard } from "@/features/planner/components/molecules/meal-card";
import type { PlanDay, WeeklyPlan as WeeklyPlanModel } from "@/features/planner/model/types";
import { cn } from "@/lib/utils";

export interface WeeklyPlanProps {
  plan: WeeklyPlanModel;
  onSwap?: (dayId: string, mealId: string) => void;
  onDetail?: (dayId: string, mealId: string) => void;
  interactive?: boolean;
  disabled?: boolean;
}

function dateLabel(date: string, short = false) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "numeric",
    month: short ? "2-digit" : "long",
    timeZone: "UTC",
  }).format(new Date(`${date}T12:00:00Z`));
}

export function WeeklyPlan({
  plan,
  onSwap,
  onDetail,
  interactive = true,
  disabled = false,
}: WeeklyPlanProps) {
  const [selectedId, setSelectedId] = useState(() => {
    const today = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Sao_Paulo" }).format(
      new Date(),
    );
    return plan.days.find((day) => day.date === today)?.id ?? plan.days[0]?.id ?? "";
  });
  const selectedDay = plan.days.find((day) => day.id === selectedId) ?? plan.days[0];
  const id = useId();

  function meals(day: PlanDay, compact = false) {
    return day.meals.map((meal) => (
      <MealCard
        key={meal.period}
        meal={meal}
        compact={compact}
        disabled={disabled}
        onSwap={interactive && onSwap ? () => onSwap(day.id, meal.id) : undefined}
        onDetail={interactive && onDetail ? () => onDetail(day.id, meal.id) : undefined}
      />
    ));
  }

  return (
    <Tabs defaultValue="day" className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold">Seu cardápio</h2>
          <p className="text-muted-foreground mt-1 text-sm">
            {plan.days[0] && dateLabel(plan.days[0].date)} a{" "}
            {plan.days.at(-1) && dateLabel(plan.days.at(-1)!.date)} de{" "}
            {plan.days[0]?.date.slice(0, 4)}
          </p>
        </div>
        <TabsList aria-label="Visualização do cardápio">
          <TabsTrigger value="day">Por dia</TabsTrigger>
          <TabsTrigger value="week">Semana</TabsTrigger>
        </TabsList>
      </div>
      <TabsContent value="day" className="space-y-6">
        <div
          role="group"
          aria-label="Escolha um dia"
          className="grid grid-cols-4 gap-2 sm:grid-cols-7"
        >
          {plan.days.map((day) => (
            <Button
              key={day.id}
              variant="outline"
              aria-pressed={selectedDay?.id === day.id}
              aria-controls={`${id}-day`}
              className={cn(
                "h-auto min-h-16 min-w-0 flex-col gap-1 px-1 py-3",
                selectedDay?.id === day.id && "border-herb bg-herb-soft text-herb",
              )}
              onClick={() => setSelectedId(day.id)}
              onKeyDown={(event) => {
                if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
                event.preventDefault();
                const position = plan.days.findIndex((item) => item.id === day.id);
                const nextIndex =
                  event.key === "Home"
                    ? 0
                    : event.key === "End"
                      ? plan.days.length - 1
                      : (position + (event.key === "ArrowRight" ? 1 : -1) + plan.days.length) %
                        plan.days.length;
                const next = plan.days[nextIndex];
                if (next) setSelectedId(next.id);
                const buttons = event.currentTarget.parentElement?.querySelectorAll("button");
                buttons?.[nextIndex]?.focus();
              }}
            >
              <span className="text-sm">{day.label.split("-")[0]}</span>
              <span className="text-xs">{dateLabel(day.date, true)}</span>
            </Button>
          ))}
        </div>
        {selectedDay && (
          <section
            id={`${id}-day`}
            aria-label={`${selectedDay.label}, ${dateLabel(selectedDay.date)}`}
            className="space-y-4"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-xl font-semibold">
                {selectedDay.label}, {dateLabel(selectedDay.date)}
              </h3>
              <span className="bg-herb-soft text-herb rounded-full px-3 py-1 text-sm">
                3 refeições planejadas
              </span>
            </div>
            <div className="grid items-stretch gap-5 md:grid-cols-3">{meals(selectedDay)}</div>
          </section>
        )}
      </TabsContent>
      <TabsContent value="week">
        <div className="grid items-start gap-5 md:grid-cols-2 xl:grid-cols-3">
          {plan.days.map((day) => (
            <section
              key={day.id}
              className="bg-muted min-w-0 space-y-3 rounded-2xl p-3 sm:p-4"
              aria-label={day.label}
            >
              <div className="px-1 py-2">
                <h3 className="text-lg font-semibold">{day.label}</h3>
                <p className="text-muted-foreground text-sm">{dateLabel(day.date)}</p>
              </div>
              <div className="space-y-3">{meals(day, true)}</div>
            </section>
          ))}
        </div>
      </TabsContent>
    </Tabs>
  );
}
