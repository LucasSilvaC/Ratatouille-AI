import { LoadingIndicator } from "@/components/molecules/loading-indicator";

export default function Loading() {
  return (
    <div className="loading-stage" aria-busy="true">
      <LoadingIndicator />
    </div>
  );
}
