"use client";

import { Circle } from "lucide-react";
import { RadioGroup as RadioGroupPrimitive } from "radix-ui";
import * as React from "react";

import { cn } from "@/lib/utils";

export function RadioGroup({
  className,
  ...props
}: React.ComponentProps<typeof RadioGroupPrimitive.Root>) {
  return <RadioGroupPrimitive.Root className={cn("grid gap-3", className)} {...props} />;
}
export function RadioGroupItem({
  className,
  ...props
}: React.ComponentProps<typeof RadioGroupPrimitive.Item>) {
  return (
    <RadioGroupPrimitive.Item
      className={cn(
        "bg-card focus-visible:ring-ring inline-flex size-5 shrink-0 items-center justify-center rounded-full border border-[var(--border-control)] text-[var(--herb)] outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:border-[var(--herb)]",
        className,
      )}
      {...props}
    >
      <RadioGroupPrimitive.Indicator>
        <Circle className="size-3 fill-current" aria-hidden="true" />
      </RadioGroupPrimitive.Indicator>
    </RadioGroupPrimitive.Item>
  );
}
