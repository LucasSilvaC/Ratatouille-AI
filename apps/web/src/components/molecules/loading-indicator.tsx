import { BrandLoader } from "@/components/atoms/brand-loader";
import { cn } from "@/lib/utils";

export function LoadingIndicator({
  message = "Preparando sua cozinha…",
  compact = false,
  className,
}: {
  message?: string;
  compact?: boolean;
  className?: string;
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className={cn("loading-indicator", compact && "loading-indicator--compact", className)}
    >
      <BrandLoader compact={compact} />
      <p className="loading-indicator__message">{message}</p>
      {!compact && (
        <span className="loading-indicator__dots" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
      )}
    </div>
  );
}
