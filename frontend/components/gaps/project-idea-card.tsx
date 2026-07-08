import { Lightbulb } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { ProjectIdea } from "@/lib/types";

interface ProjectIdeaCardProps {
  idea: ProjectIdea;
}

export function ProjectIdeaCard({ idea }: ProjectIdeaCardProps) {
  return (
    <Card className="border-teal-dim/60 bg-teal-dim/5 transition-colors hover:border-teal-dim">
      <CardHeader className="pb-2">
        <div className="flex items-start gap-2.5">
          <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-teal-dim/40 text-teal">
            <Lightbulb className="h-3.5 w-3.5" />
          </span>
          <CardTitle className="text-base">{idea.title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <p className="text-sm leading-relaxed text-foreground-muted">{idea.description}</p>

        <Separator />

        <div className="flex flex-col gap-1">
          <span className="font-mono text-[11px] uppercase tracking-wide text-teal">
            Grounded in
          </span>
          <p className="text-xs leading-relaxed text-foreground-muted">{idea.grounded_in_gap}</p>
        </div>

        <div className="flex flex-col gap-1">
          <span className="font-mono text-[11px] uppercase tracking-wide text-teal">
            Why it&rsquo;s novel
          </span>
          <p className="text-xs leading-relaxed text-foreground-muted">
            {idea.novelty_rationale}
          </p>
        </div>

        <div className="flex flex-col gap-1">
          <span className="font-mono text-[11px] uppercase tracking-wide text-teal">
            Suggested approach
          </span>
          <p className="text-xs leading-relaxed text-foreground-muted">
            {idea.suggested_approach}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
