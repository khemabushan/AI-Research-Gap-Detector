"use client";

import { useBackendHealth } from "@/hooks/use-backend-health";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/constants";

/**
 * Small live indicator of whether the FastAPI backend is reachable at
 * NEXT_PUBLIC_API_BASE_URL. Polls GET /health every 30s via useBackendHealth.
 */
export function ConnectionStatus() {
  const { isSuccess, isError, isLoading } = useBackendHealth();

  const label = isLoading ? "connecting…" : isSuccess ? "backend connected" : "backend unreachable";

  return (
    <div className="hidden items-center gap-1.5 sm:flex" title={API_BASE_URL}>
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full",
          isLoading && "bg-muted",
          isSuccess && "bg-teal",
          isError && "bg-destructive"
        )}
      />
      <span className="font-mono text-xs text-muted">{label}</span>
    </div>
  );
}
