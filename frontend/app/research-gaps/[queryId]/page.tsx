"use client";

import { useParams, useRouter } from "next/navigation";
import { FlaskConical, FileQuestion } from "lucide-react";

import { EmptyState } from "@/components/shared/empty-state";
import { ErrorBanner } from "@/components/shared/error-banner";
import { GapReportSkeleton } from "@/components/shared/loading-skeletons";
import { GapReportContent } from "@/components/gaps/gap-report-content";
import { useQueryDetail } from "@/hooks/use-query-detail";
import { ApiRequestError } from "@/lib/api-client";

export default function ResearchGapsPage() {
  const params = useParams<{ queryId: string }>();
  const router = useRouter();
  const queryId = Number(params.queryId);

  const { data: detail, isLoading, isError, error, refetch } = useQueryDetail(queryId);

  return (
    <div className="container flex flex-col gap-10 py-10">
      <div className="flex items-center gap-2.5">
        <span className="flex h-8 w-8 items-center justify-center rounded-md border border-amber-dim bg-amber-dim/30 text-amber">
          <FlaskConical className="h-4 w-4" />
        </span>
        <h1 className="font-display text-2xl font-semibold text-balance">
          {detail ? detail.topic : `Query #${queryId}`} — Gap report
        </h1>
      </div>

      {isLoading && <GapReportSkeleton />}

      {isError && (
        <>
          {error instanceof ApiRequestError && error.status === 404 ? (
            <EmptyState
              icon={FileQuestion}
              title="Query not found"
              description={`No query with id ${queryId} exists.`}
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
        </>
      )}

      {detail && (
        <GapReportContent
          queryId={queryId}
          papers={detail.papers}
          existingGapReport={detail.gap_report}
        />
      )}
    </div>
  );
}
