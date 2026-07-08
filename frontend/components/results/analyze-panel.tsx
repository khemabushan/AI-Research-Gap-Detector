"use client";

import { useRouter } from "next/navigation";
import { ArrowRight, Loader2, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ErrorBanner } from "@/components/shared/error-banner";

interface AnalyzePanelProps {
  queryId: number;
  /** True once the backend has extractions for this query (from GET /queries/{id}). */
  isAnalyzed: boolean;
  /** Present once analysis has completed, for the success summary line. */
  summary?: { papersProcessed: number; papersFailed: number };
  isPending: boolean;
  errorMessage: string | null;
  onAnalyze: () => void;
}

export function AnalyzePanel({
  queryId,
  isAnalyzed,
  summary,
  isPending,
  errorMessage,
  onAnalyze,
}: AnalyzePanelProps) {
  const router = useRouter();

  if (isAnalyzed) {
    return (
      <div className="flex flex-col gap-3 rounded-lg border border-teal-dim bg-teal-dim/10 p-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-teal-dim/40 text-teal">
            <Sparkles className="h-4 w-4" />
          </span>
          <div>
            <p className="text-sm font-medium text-foreground">
              {summary
                ? `Extracted structured fields from ${summary.papersProcessed} papers${
                    summary.papersFailed > 0 ? ` (${summary.papersFailed} failed)` : ""
                  }.`
                : "Papers have been analyzed."}
            </p>
            <p className="text-xs text-foreground-muted">
              Ready to detect research gaps and generate project ideas.
            </p>
          </div>
        </div>
        <Button onClick={() => router.push(`/research-gaps/${queryId}`)} className="shrink-0">
          Find research gaps
          <ArrowRight />
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-border bg-surface p-5 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-sm font-medium text-foreground">
          Extract structured fields from every paper
        </p>
        <p className="text-xs text-foreground-muted">
          Runs problem / dataset / methodology / model / limitations extraction, then builds the
          similarity index used for gap detection.
        </p>
      </div>
      <Button onClick={onAnalyze} disabled={isPending} className="shrink-0">
        {isPending ? (
          <>
            <Loader2 className="animate-spin" />
            Analyzing papers…
          </>
        ) : (
          <>
            Analyze papers
            <ArrowRight />
          </>
        )}
      </Button>
      {errorMessage ? (
        <div className="w-full sm:w-auto">
          <ErrorBanner message={errorMessage} onRetry={onAnalyze} />
        </div>
      ) : null}
    </div>
  );
}
