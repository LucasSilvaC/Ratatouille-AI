"use client";

import { AlertCircle, Check, Leaf, X } from "lucide-react";
import type { ReactNode } from "react";

import { Alert } from "@/components/atoms/alert";
import { BrandLoader } from "@/components/atoms/brand-loader";
import { Button } from "@/components/atoms/button";
import { Skeleton } from "@/components/atoms/skeleton";
import { LoadingIndicator } from "@/components/molecules/loading-indicator";

export function PageHeader({
  title,
  description,
  eyebrow,
}: {
  title: string;
  description?: string;
  eyebrow?: string;
}) {
  return (
    <header className="mb-8 space-y-3">
      {eyebrow && (
        <p className="text-sm font-semibold tracking-wider text-[var(--herb)]">{eyebrow}</p>
      )}
      <h1 className="text-[28px] leading-tight font-bold tracking-tight sm:text-[32px]">{title}</h1>
      {description && (
        <p className="text-muted-foreground max-w-2xl text-base leading-relaxed">{description}</p>
      )}
    </header>
  );
}
export function LoadingState({
  message = "Preparando sugestões para sua semana…",
}: {
  message?: string;
}) {
  return (
    <section aria-busy="true" className="space-y-6 py-6">
      <LoadingIndicator message={message} />
      <div className="grid gap-4 sm:grid-cols-3">
        {[0, 1, 2].map((item) => (
          <div className="space-y-3" key={item}>
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-5 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        ))}
      </div>
    </section>
  );
}
export function EmptyState({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children?: ReactNode;
}) {
  return (
    <section className="bg-card rounded-2xl border border-dashed px-4 py-10 text-center sm:px-8">
      <Leaf className="mx-auto mb-4 size-8 text-[var(--herb)]" aria-hidden="true" />
      <h2 className="text-2xl font-semibold">{title}</h2>
      <p className="text-muted-foreground mx-auto mt-3 max-w-lg">{description}</p>
      {children && <div className="mt-6 flex flex-wrap justify-center gap-3">{children}</div>}
    </section>
  );
}
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <Alert
      role="alert"
      className="space-y-3 border-[var(--danger)] bg-[var(--danger-soft)] p-4 text-[var(--danger)]"
    >
      <div className="flex items-start gap-3">
        <AlertCircle className="mt-0.5 size-5 shrink-0" aria-hidden="true" />
        <p>{message}</p>
      </div>
      {onRetry && (
        <Button variant="outline" onClick={onRetry} type="button">
          Tentar novamente
        </Button>
      )}
    </Alert>
  );
}
export function ApprovalActions({
  onCancel,
  onApprove,
  busy = false,
  disabled = false,
}: {
  onCancel: () => void;
  onApprove: () => void;
  busy?: boolean;
  disabled?: boolean;
}) {
  return (
    <div className="mt-6 space-y-3">
      {busy && <LoadingIndicator message="Salvando alterações…" compact />}
      <div className="grid grid-cols-1 gap-3 min-[350px]:grid-cols-2 sm:flex sm:justify-end">
        <Button
          type="button"
          variant="outline"
          className="min-w-[120px]"
          onClick={onCancel}
          disabled={busy}
        >
          <X className="size-[18px]" aria-hidden="true" />
          Cancelar
        </Button>
        <Button
          type="button"
          className="min-w-[120px]"
          onClick={onApprove}
          disabled={busy || disabled}
        >
          {busy ? <BrandLoader compact /> : <Check className="size-[18px]" aria-hidden="true" />}
          Aprovar
        </Button>
      </div>
    </div>
  );
}
