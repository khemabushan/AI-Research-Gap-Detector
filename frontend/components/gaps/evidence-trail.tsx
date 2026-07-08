import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { paperTag } from "@/lib/utils";
import type { Paper } from "@/lib/types";

interface EvidenceTrailProps {
  paperIds: number[];
  papersById: Map<number, Paper>;
}

/**
 * Renders citation-style chips (e.g. [P4]) for each source paper backing a
 * claim. Hovering reveals the paper's title — the whole point being that a
 * reader can check any gap or idea against its actual evidence.
 */
export function EvidenceTrail({ paperIds, papersById }: EvidenceTrailProps) {
  if (paperIds.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="font-mono text-[11px] text-muted">evidence:</span>
      {paperIds.map((id) => {
        const paper = papersById.get(id);
        return (
          <Tooltip key={id}>
            <TooltipTrigger asChild>
              <span className="cursor-default rounded-sm border border-border bg-surface-raised px-1.5 py-0.5 font-mono text-[11px] text-foreground-muted transition-colors hover:border-teal-dim hover:text-teal">
                {paperTag(id)}
              </span>
            </TooltipTrigger>
            <TooltipContent>{paper ? paper.title : `Paper ${id}`}</TooltipContent>
          </Tooltip>
        );
      })}
    </div>
  );
}
