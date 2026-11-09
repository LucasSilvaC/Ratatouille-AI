import * as React from "react";

import { cn } from "@/lib/utils";

export type IInputProps = React.InputHTMLAttributes<HTMLInputElement>;

export function Input({ className, ...properties }: IInputProps): React.ReactElement {
  return (
    <input
      className={cn(
        "bg-card placeholder:text-muted-foreground focus-visible:ring-ring flex min-h-12 w-full min-w-0 rounded-xl border border-[var(--border-control)] px-3 py-2 text-base outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-[var(--danger)]",
        className,
      )}
      {...properties}
    />
  );
}
