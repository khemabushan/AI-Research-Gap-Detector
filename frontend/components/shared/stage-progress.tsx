import { Check, Loader2 } from "lucide-react";

import { PIPELINE_STAGES, type PipelineStageKey } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface StageProgressProps {
  currentStage: PipelineStageKey;
  completedStages: PipelineStageKey[];
  failedStage?: PipelineStageKey;
}

export function StageProgress({
  currentStage,
  completedStages,
  failedStage,
}: StageProgressProps) {
  return (
    <ol className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-0">
      {PIPELINE_STAGES.map((stage, index) => {
        const isDone = completedStages.includes(stage.key);
        const isCurrent = stage.key === currentStage && !isDone;
        const isFailed = stage.key === failedStage;
        const isLast = index === PIPELINE_STAGES.length - 1;

        return (
          <li key={stage.key} className="flex flex-1 items-center gap-3">
            <div className="flex items-center gap-3">
              <span
                className={cn(
                  "flex h-7 w-7 shrink-0 items-center justify-center rounded-full border font-mono text-xs",
                  isDone && "border-teal bg-teal text-ink",
                  isCurrent && "border-teal text-teal",
                  isFailed && "border-destructive text-destructive",
                  !isDone && !isCurrent && !isFailed && "border-border text-muted"
                )}
              >
                {isDone ? (
                  <Check className="h-3.5 w-3.5" />
                ) : isCurrent ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  index + 1
                )}
              </span>
              <span
                className={cn(
                  "text-sm",
                  (isDone || isCurrent) && "text-foreground",
                  isFailed && "text-destructive",
                  !isDone && !isCurrent && !isFailed && "text-muted"
                )}
              >
                {stage.label}
              </span>
            </div>
            {!isLast && (
              <div
                className={cn(
                  "mx-3 hidden h-px flex-1 bg-border sm:block",
                  isDone && "bg-teal-dim"
                )}
              />
            )}
          </li>
        );
      })}
    </ol>
  );
}
