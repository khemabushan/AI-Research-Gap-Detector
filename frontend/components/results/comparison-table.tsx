import { Badge } from "@/components/ui/badge";
import { paperTag, truncate } from "@/lib/utils";
import type { Extraction, Paper } from "@/lib/types";

interface ComparisonTableProps {
  papers: Paper[];
  extractions: Extraction[];
}

const COLUMNS: { key: keyof Extraction; label: string }[] = [
  { key: "problem", label: "Problem" },
  { key: "dataset", label: "Dataset" },
  { key: "methodology", label: "Methodology" },
  { key: "model", label: "Model" },
  { key: "limitations", label: "Limitations" },
];

export function ComparisonTable({ papers, extractions }: ComparisonTableProps) {
  const extractionByPaperId = new Map(extractions.map((e) => [e.paper_id, e]));

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full min-w-[900px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-border bg-surface-raised">
            <th className="sticky left-0 z-10 bg-surface-raised px-4 py-3 text-left font-mono text-xs uppercase tracking-wide text-muted">
              Paper
            </th>
            {COLUMNS.map((col) => (
              <th
                key={col.key}
                className="px-4 py-3 text-left font-mono text-xs uppercase tracking-wide text-muted"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {papers.map((paper, index) => {
            const extraction = extractionByPaperId.get(paper.id);
            return (
              <tr
                key={paper.id}
                className={index % 2 === 0 ? "bg-surface" : "bg-surface/50"}
              >
                <td className="sticky left-0 z-10 max-w-[220px] bg-inherit px-4 py-3 align-top">
                  <div className="flex items-start gap-2">
                    <Badge variant="outline" className="mt-0.5 shrink-0">
                      {paperTag(paper.id)}
                    </Badge>
                    <span className="text-xs font-medium leading-snug text-foreground">
                      {truncate(paper.title, 60)}
                    </span>
                  </div>
                </td>
                {COLUMNS.map((col) => (
                  <td
                    key={col.key}
                    className="max-w-[220px] px-4 py-3 align-top text-xs leading-relaxed text-foreground-muted"
                  >
                    {extraction ? extraction[col.key] || "Not specified" : "—"}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
