import { Quote } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn, formatCitations, formatSource, paperTag, truncate } from "@/lib/utils";
import type { Paper } from "@/lib/types";

interface PaperCardProps {
  paper: Paper;
  isSelected: boolean;
  onSelect: () => void;
}

export function PaperCard({ paper, isSelected, onSelect }: PaperCardProps) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={cn(
        "flex w-full flex-col gap-2 rounded-lg border px-4 py-3 text-left transition-colors",
        isSelected
          ? "border-teal-dim bg-teal-dim/20"
          : "border-border bg-surface hover:border-teal-dim/60 hover:bg-surface-raised"
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-display text-sm font-semibold leading-snug text-balance">
          {paper.title}
        </h3>
        <Badge variant="outline" className="shrink-0">
          {paperTag(paper.id)}
        </Badge>
      </div>

      <p className="text-xs text-foreground-muted">
        {paper.authors.slice(0, 3).join(", ")}
        {paper.authors.length > 3 ? ` +${paper.authors.length - 3} more` : ""}
      </p>

      <p className="text-xs leading-relaxed text-foreground-muted">
        {truncate(paper.abstract, 140)}
      </p>

      <div className="mt-1 flex flex-wrap items-center gap-2 font-mono text-[11px] text-muted">
        <span>{formatSource(paper.source)}</span>
        <span aria-hidden>&middot;</span>
        <span>{paper.year ?? "n.d."}</span>
        <span aria-hidden>&middot;</span>
        <span className="inline-flex items-center gap-1">
          <Quote className="h-3 w-3" />
          {formatCitations(paper.citation_count)}
        </span>
      </div>
    </button>
  );
}
