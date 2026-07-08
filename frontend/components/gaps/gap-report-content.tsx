"use client";

import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { StageProgress } from "@/components/shared/stage-progress";
import { ErrorBanner } from "@/components/shared/error-banner";
import { GapCard } from "@/components/gaps/gap-card";
import { ClusterCard } from "@/components/gaps/cluster-card";
import { FutureDirectionList } from "@/components/gaps/future-direction-list";
import { ProjectIdeaCard } from "@/components/gaps/project-idea-card";
import { GapReportSkeleton, ProjectIdeasSkeleton } from "@/components/shared/loading-skeletons";
import { useGapPipeline } from "@/hooks/use-pipeline";
import type { GapReportSummary, Paper } from "@/lib/types";

interface GapReportContentProps {
  queryId: number;
  papers: Paper[];
  existingGapReport: GapReportSummary | null;
}

/**
 * Mounted only once the parent has finished loading the query's current
 * state via GET /queries/{id} — that's what lets useGapPipeline correctly
 * decide, on its very first render, whether to skip straight to "done"
 * (report already persisted) or kick off /research-gaps + /future-directions.
 */
export function GapReportContent({ queryId, papers, existingGapReport }: GapReportContentProps) {
  const { stage, completedStages, failedStage, gaps, directions, error, isRunning, retry } =
    useGapPipeline(queryId, existingGapReport);

  const papersById = new Map(papers.map((p) => [p.id, p]));

  return (
    <div className="flex flex-col gap-10">
      <StageProgress
        currentStage={stage}
        completedStages={completedStages}
        failedStage={failedStage}
      />

      {error && <ErrorBanner message={error} onRetry={retry} />}

      {/* --- Research Gaps --- */}
      <section className="flex flex-col gap-4">
        <div className="flex items-baseline justify-between">
          <h2 className="font-display text-lg font-semibold">Research gaps</h2>
          {gaps && <Badge variant="amber">{gaps.identified_gaps.length} identified</Badge>}
        </div>

        {gaps?.summary && (
          <p className="max-w-3xl text-sm leading-relaxed text-foreground-muted">
            {gaps.summary}
          </p>
        )}

        {!gaps && !error && <GapReportSkeleton />}

        {gaps && (
          <div className="flex flex-col gap-3">
            {gaps.identified_gaps.map((statement, index) => (
              <GapCard key={index} index={index + 1} statement={statement} />
            ))}
          </div>
        )}
      </section>

      {gaps && gaps.clusters.length > 0 && (
        <section className="flex flex-col gap-4">
          <h2 className="font-display text-lg font-semibold">Paper clusters</h2>
          <p className="max-w-3xl text-sm text-foreground-muted">
            Papers grouped by embedding similarity — this is the evidence base the gaps above were
            derived from.
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {gaps.clusters.map((cluster) => (
              <ClusterCard key={cluster.cluster_id} cluster={cluster} papersById={papersById} />
            ))}
          </div>
        </section>
      )}

      <Separator />

      {/* --- Future Directions & Project Ideas --- */}
      <section className="flex flex-col gap-4">
        <h2 className="font-display text-lg font-semibold">Future research directions</h2>
        {!directions && !error && (
          <div className="flex flex-col gap-2.5">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-12 skeleton rounded-md" />
            ))}
          </div>
        )}
        {directions && <FutureDirectionList directions={directions.future_directions} />}
      </section>

      <section className="flex flex-col gap-4">
        <h2 className="font-display text-lg font-semibold">Novel project ideas</h2>
        {!directions && !error && <ProjectIdeasSkeleton />}
        {directions && (
          <div className="grid gap-4 sm:grid-cols-2">
            {directions.novel_project_ideas.map((idea, index) => (
              <ProjectIdeaCard key={index} idea={idea} />
            ))}
          </div>
        )}
      </section>

      {isRunning && (
        <p className="text-center font-mono text-xs text-muted">
          This can take a minute — the model is reasoning over every paper&rsquo;s extracted
          fields.
        </p>
      )}
    </div>
  );
}
