"use client";

import { Check } from "lucide-react";

import { Button } from "@/components/atoms/button";
import { cn } from "@/lib/utils";

export function OnboardingStepper({
  step,
  onStep,
}: {
  step: number;
  onStep: (step: number) => void;
}) {
  return (
    <nav aria-label="Etapas de criação do cardápio" className="mb-8">
      <ol className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {["Perfil", "Região", "Preferências", "Cardápio"].map((label, index) => (
          <li key={label}>
            <Button
              type="button"
              variant="ghost"
              className={cn(
                "text-muted-foreground w-full justify-start px-3",
                step === index && "bg-[var(--herb-soft)] text-[var(--herb)]",
              )}
              aria-current={step === index ? "step" : undefined}
              disabled={index > step}
              onClick={() => onStep(index)}
            >
              <span
                className={cn(
                  "bg-muted flex size-6 shrink-0 items-center justify-center rounded-full text-xs",
                  index <= step && "bg-[var(--herb)] text-white",
                )}
              >
                {index < step ? <Check className="size-4" aria-hidden="true" /> : index + 1}
              </span>
              {label}
            </Button>
          </li>
        ))}
      </ol>
    </nav>
  );
}
