"use client";

import { ArrowLeftRight, Coffee, CookingPot, Moon, Utensils } from "lucide-react";
import Image from "next/image";

import { Button } from "@/components/atoms/button";
import { Card } from "@/components/atoms/card";
import type { Meal } from "@/features/planner/model/types";
import { cn } from "@/lib/utils";

export const mealPeriodLabels = { breakfast: "Café da manhã", lunch: "Almoço", dinner: "Jantar" };
const periodIcons = { breakfast: Coffee, lunch: CookingPot, dinner: Moon };

interface MealCardProps {
  meal: Meal;
  onSwap?: () => void;
  onDetail?: () => void;
  compact?: boolean;
  disabled?: boolean;
}

export function MealCard({
  meal,
  onSwap,
  onDetail,
  compact = false,
  disabled = false,
}: MealCardProps) {
  const Icon = periodIcons[meal.period];
  return (
    <Card className="flex h-full min-w-0 flex-col overflow-hidden">
      <div className="text-herb flex items-center gap-2 px-5 pt-5 text-sm font-semibold">
        <Icon aria-hidden="true" className="size-4" />
        {mealPeriodLabels[meal.period]}
      </div>
      {meal.image && !compact && (
        <div className="relative mx-5 mt-4 aspect-[4/3] overflow-hidden rounded-lg">
          <Image
            src={meal.image}
            alt={`Fotografia ilustrativa de ${meal.name}`}
            fill
            sizes="(max-width: 767px) 90vw, 360px"
            className="object-cover"
          />
        </div>
      )}
      <div className={cn("flex flex-1 flex-col gap-4 p-5", compact && "gap-3")}>
        <h3 className={cn("text-xl leading-snug font-semibold", compact && "text-lg")}>
          {meal.name}
        </h3>
        <p className="text-muted-foreground text-sm leading-relaxed">
          {meal.ingredients.join(" · ")}
        </p>
        <div className="text-muted-foreground mt-auto flex flex-wrap items-center gap-x-4 gap-y-1 border-t pt-3 text-sm">
          <span className="inline-flex items-center gap-1.5">
            <Utensils aria-hidden="true" className="size-4" />
            {meal.portions} {meal.portions === 1 ? "porção" : "porções"}
          </span>
          <span className="tabular-nums">{meal.kcal} kcal / porção</span>
        </div>
        <p className="text-muted-foreground text-xs">Porções e valores demonstrativos.</p>
        {(onDetail || onSwap) && (
          <div className="flex flex-wrap gap-2">
            {onDetail && (
              <Button
                variant="ghost"
                size="sm"
                aria-disabled={disabled}
                onClick={() => {
                  if (!disabled) onDetail();
                }}
                aria-label={`Ver detalhes: ${meal.name}`}
              >
                Ver detalhes
              </Button>
            )}
            {onSwap && (
              <Button
                className="grow"
                variant="outline"
                size="sm"
                aria-disabled={disabled}
                onClick={() => {
                  if (!disabled) onSwap();
                }}
                aria-label={`Trocar refeição: ${meal.name}`}
              >
                <ArrowLeftRight aria-hidden="true" className="size-4" />
                Trocar refeição
              </Button>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
