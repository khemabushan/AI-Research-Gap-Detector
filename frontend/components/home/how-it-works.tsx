import { FileSearch, Layers, Sparkles } from "lucide-react";

const STEPS = [
  {
    icon: FileSearch,
    title: "Collect & extract",
    body: "Pulls abstracts from arXiv and Semantic Scholar, then extracts problem, dataset, method, and limitations from each.",
  },
  {
    icon: Layers,
    title: "Compare & cluster",
    body: "Embeds every paper and clusters them by approach to see how the field actually groups itself.",
  },
  {
    icon: Sparkles,
    title: "Report the gap",
    body: "Surfaces under-explored combinations and proposes concrete, novel project directions grounded in the evidence.",
  },
];

export function HowItWorks() {
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {STEPS.map((step, index) => (
        <div
          key={step.title}
          className="flex flex-col gap-3 rounded-lg border border-border bg-surface/60 p-5"
        >
          <div className="flex items-center justify-between">
            <span className="flex h-9 w-9 items-center justify-center rounded-md border border-teal-dim bg-teal-dim/30 text-teal">
              <step.icon className="h-4 w-4" />
            </span>
            <span className="font-mono text-xs text-muted">
              {String(index + 1).padStart(2, "0")}
            </span>
          </div>
          <h3 className="font-display text-sm font-semibold">{step.title}</h3>
          <p className="text-sm text-foreground-muted">{step.body}</p>
        </div>
      ))}
    </div>
  );
}
