import { ExternalLink, Quote } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { EmptyState } from "@/components/shared/empty-state";
import { formatCitations, formatSource, paperTag } from "@/lib/utils";
import type { Extraction, Paper } from "@/lib/types";
import { FileText } from "lucide-react";

interface AbstractViewerProps {
  paper: Paper | null;
  extraction?: Extraction;
}

const EXTRACTION_FIELDS: { key: keyof Extraction; label: string }[] = [
  { key: "problem", label: "Problem" },
  { key: "methodology", label: "Methodology" },
  { key: "dataset", label: "Dataset" },
  { key: "model", label: "Model" },
  { key: "limitations", label: "Limitations" },
  { key: "future_work", label: "Future work" },
];

export function AbstractViewer({ paper, extraction }: AbstractViewerProps) {
  if (!paper) {
    return (
      <EmptyState
        icon={FileText}
        title="Select a paper"
        description="Choose a paper from the list to read its abstract and extracted fields."
      />
    );
  }

  return (
    <ScrollArea className="h-[560px] pr-3">
      <div className="flex flex-col gap-4">
        <div className="flex items-start justify-between gap-3">
          <h2 className="font-display text-xl font-semibold leading-snug text-balance">
            {paper.title}
          </h2>
          <Badge variant="teal" className="shrink-0">
            {paperTag(paper.id)}
          </Badge>
        </div>

        <div className="flex flex-wrap items-center gap-2 font-mono text-xs text-muted">
          <span>{paper.authors.join(", ")}</span>
        </div>

        <div className="flex flex-wrap items-center gap-3 font-mono text-xs text-foreground-muted">
          <span>{formatSource(paper.source)}</span>
          <span aria-hidden>&middot;</span>
          <span>{paper.year ?? "n.d."}</span>
          <span aria-hidden>&middot;</span>
          <span className="inline-flex items-center gap-1">
            <Quote className="h-3 w-3" />
            {formatCitations(paper.citation_count)}
          </span>
          {paper.url && (
            <a
              href={paper.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-teal hover:underline"
            >
              View source <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>

        <Separator />

        <div>
          <h3 className="mb-1.5 font-mono text-xs uppercase tracking-wide text-muted">
            Abstract
          </h3>
          <p className="text-sm leading-relaxed text-foreground-muted">{paper.abstract}</p>
        </div>

        {extraction && (
          <>
            <Separator />
            <div className="flex flex-col gap-3">
              <h3 className="font-mono text-xs uppercase tracking-wide text-muted">
                Extracted fields
              </h3>
              {EXTRACTION_FIELDS.map((field) => (
                <div key={field.key} className="flex flex-col gap-1">
                  <span className="font-mono text-[11px] uppercase tracking-wide text-teal">
                    {field.label}
                  </span>
                  <p className="text-sm leading-relaxed text-foreground-muted">
                    {extraction[field.key] || "Not specified"}
                  </p>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </ScrollArea>
  );
}
