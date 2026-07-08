import { useCallback, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { api, ApiRequestError } from "@/lib/api-client";
import type {
  FutureDirectionsResponse,
  GapReportSummary,
  ResearchGapsResponse,
} from "@/lib/types";
import type { PipelineStageKey } from "@/lib/constants";

interface PipelineState {
  stage: PipelineStageKey;
  completedStages: PipelineStageKey[];
  failedStage?: PipelineStageKey;
  gaps: ResearchGapsResponse | null;
  directions: FutureDirectionsResponse | null;
  error: string | null;
  isRunning: boolean;
}

function isComplete(report: GapReportSummary | null | undefined): report is GapReportSummary {
  return Boolean(
    report && report.identified_gaps.length > 0 && report.novel_project_ideas.length > 0
  );
}

/**
 * Runs /research-gaps then /future-directions in sequence for a query,
 * exposing granular stage state so the UI can show a live progress tracker
 * rather than one opaque spinner across both LLM calls.
 *
 * If `existingGapReport` (from GET /queries/{id}, i.e. already persisted by
 * the backend) is already complete, the pipeline skips straight to
 * "done" instead of re-running two LLM calls — the backend's SQLite row is
 * the source of truth for whether this work has already happened, not any
 * client-side cache.
 */
export function useGapPipeline(queryId: number, existingGapReport?: GapReportSummary | null) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<PipelineState>({
    stage: "gaps",
    completedStages: [],
    gaps: null,
    directions: null,
    error: null,
    isRunning: false,
  });
  const hasStarted = useRef(false);

  const run = useCallback(async () => {
    setState((prev) => ({ ...prev, isRunning: true, error: null, stage: "gaps" }));

    try {
      const gaps = await api.researchGaps(queryId);
      setState((prev) => ({
        ...prev,
        gaps,
        completedStages: [...prev.completedStages, "gaps"],
        stage: "directions",
      }));

      const directions = await api.futureDirections(queryId);
      setState((prev) => ({
        ...prev,
        directions,
        completedStages: [...prev.completedStages, "directions"],
        isRunning: false,
      }));

      // The backend has now persisted the gap report — invalidate the
      // cached query detail so any other view of this query picks it up.
      void queryClient.invalidateQueries({ queryKey: ["query", queryId] });
    } catch (err) {
      const message =
        err instanceof ApiRequestError ? err.detail : "Something went wrong generating the report.";
      setState((prev) => ({
        ...prev,
        error: message,
        failedStage: prev.stage,
        isRunning: false,
      }));
    }
  }, [queryId, queryClient]);

  useEffect(() => {
    if (hasStarted.current) return;
    hasStarted.current = true;

    if (isComplete(existingGapReport)) {
      setState({
        stage: "directions",
        completedStages: ["gaps", "directions"],
        gaps: {
          query_id: queryId,
          topic: "",
          summary: existingGapReport.summary,
          identified_gaps: existingGapReport.identified_gaps,
          clusters: existingGapReport.cluster_summary,
          generated_at: existingGapReport.generated_at,
        },
        directions: {
          query_id: queryId,
          future_directions: existingGapReport.future_directions,
          novel_project_ideas: existingGapReport.novel_project_ideas,
          generated_at: existingGapReport.generated_at,
        },
        error: null,
        isRunning: false,
      });
      return;
    }

    void run();
  }, [run, existingGapReport, queryId]);

  return { ...state, retry: run };
}
