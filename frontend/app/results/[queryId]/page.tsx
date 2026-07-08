"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { FileQuestion } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PaperList } from "@/components/results/paper-list";
import { AbstractViewer } from "@/components/results/abstract-viewer";
import { ComparisonTable } from "@/components/results/comparison-table";
import { AnalyzePanel } from "@/components/results/analyze-panel";
import { PaperListSkeleton } from "@/components/shared/loading-skeletons";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorBanner } from "@/components/shared/error-banner";
import { useAnalyzePapers } from "@/hooks/use-analyze";
import { useQueryDetail } from "@/hooks/use-query-detail";
import { ApiRequestError } from "@/lib/api-client";

export default function ResultsPage() {
  const params = useParams<{ queryId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const queryId = Number(params.queryId);

  const { data: detail, isLoading, isError, error, refetch } = useQueryDetail(queryId);
  const analyzeMutation = useAnalyzePapers();

  const [selectedPaperId, setSelectedPaperId] = useState<number | null>(null);

  // Default to the first paper once the query detail has loaded.
  useEffect(() => {
    if (detail && detail.papers.length > 0 && selectedPaperId === null) {
      setSelectedPaperId(detail.papers[0]!.id);
    }
  }, [detail, selectedPaperId]);

  const extractionByPaperId = useMemo(
    () => new Map((detail?.extractions ?? []).map((e) => [e.paper_id, e])),
    [detail]
  );

  const selectedPaper = useMemo(
    () => detail?.papers.find((p) => p.id === selectedPaperId) ?? null,
    [detail, selectedPaperId]
  );

  const hasAnalysis = (detail?.extractions.length ?? 0) > 0;

  function handleAnalyze() {
    analyzeMutation.mutate(queryId, {
      // The backend has now persisted extractions — invalidate the cached
      // query detail so this page re-fetches the authoritative state from
      // the database (single source of truth) rather than trusting this
      // mutation's response to stay in sync on its own.
      onSuccess: () => {
        void queryClient.invalidateQueries({ queryKey: ["query", queryId] });
      },
    });
  }

  if (isLoading) {
    return (
      <div className="container py-10">
        <PaperListSkeleton />
      </div>
    );
  }

  if (isError || !detail) {
    const notFound = error instanceof ApiRequestError && error.status === 404;
    return (
      <div className="container py-20">
        {notFound ? (
          <EmptyState
            icon={FileQuestion}
            title="Query not found"
            description={`No query with id ${queryId} exists. It may have been created against a different backend instance.`}
            action={
              <button
                onClick={() => router.push("/")}
                className="mt-2 text-sm font-medium text-teal hover:underline"
              >
                Start a new search
              </button>
            }
          />
        ) : (
          <ErrorBanner
            message={
              error instanceof ApiRequestError
                ? error.detail
                : "Couldn't load this query. Please try again."
            }
            onRetry={() => void refetch()}
          />
        )}
      </div>
    );
  }

  return (
    <div className="container flex flex-col gap-8 py-10">
      <div className="flex flex-col gap-2">
        <span className="font-mono text-xs uppercase tracking-wide text-muted">
          Query #{queryId}
        </span>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="font-display text-2xl font-semibold text-balance">{detail.topic}</h1>
          <Badge variant="teal">{detail.total_papers} papers</Badge>
        </div>
      </div>

      <AnalyzePanel
        queryId={queryId}
        isAnalyzed={hasAnalysis}
        summary={
          hasAnalysis
            ? {
                papersProcessed: detail.extractions.length,
                papersFailed: detail.total_papers - detail.extractions.length,
              }
            : undefined
        }
        isPending={analyzeMutation.isPending}
        errorMessage={
          analyzeMutation.error instanceof ApiRequestError
            ? analyzeMutation.error.detail
            : analyzeMutation.error
              ? "Analysis failed."
              : null
        }
        onAnalyze={handleAnalyze}
      />

      <Tabs defaultValue="papers">
        <TabsList>
          <TabsTrigger value="papers">Papers</TabsTrigger>
          <TabsTrigger value="comparison" disabled={!hasAnalysis}>
            Comparison table
          </TabsTrigger>
        </TabsList>

        <TabsContent value="papers">
          <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
            <PaperList
              papers={detail.papers}
              selectedPaperId={selectedPaperId}
              onSelect={setSelectedPaperId}
            />
            <div className="rounded-lg border border-border bg-surface p-6">
              <AbstractViewer
                paper={selectedPaper}
                extraction={
                  selectedPaper ? extractionByPaperId.get(selectedPaper.id) : undefined
                }
              />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="comparison">
          {hasAnalysis && (
            <ComparisonTable papers={detail.papers} extractions={detail.extractions} />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
