import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex shrink-0 items-center justify-center gap-2 rounded-xl text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-[var(--primary-hover)]",
        outline: "border border-[var(--border-control)] bg-card text-foreground hover:bg-muted",
        ghost: "text-foreground hover:bg-muted",
      },
      size: { default: "min-h-12 px-5 py-3", sm: "min-h-11 px-3 py-2", lg: "min-h-12 px-8 py-3" },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);

export interface IButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}

export function Button({
  className,
  size,
  variant,
  type = "button",
  ...properties
}: IButtonProps): React.ReactElement {
  return (
    <button
      type={type}
      className={cn(buttonVariants({ size, variant }), className)}
      {...properties}
    />
  );
}
