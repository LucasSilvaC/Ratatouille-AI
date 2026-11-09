import { MealCard } from "@/features/planner/components/molecules/meal-card";
import type { Meal } from "@/features/planner/model/types";

export function MealComparison({ current, proposed }: { current: Meal; proposed?: Meal }) {
  return (
    <div className="space-y-5">
      <section className="space-y-2">
        <h3 className="text-sm font-semibold">Atual</h3>
        <MealCard meal={current} compact />
      </section>
      {proposed && (
        <section className="space-y-2">
          <h3 className="text-herb text-sm font-semibold">Proposta</h3>
          <MealCard meal={proposed} compact />
        </section>
      )}
    </div>
  );
}
