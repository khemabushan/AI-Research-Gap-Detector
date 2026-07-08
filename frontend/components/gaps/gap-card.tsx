import { Card, CardContent } from "@/components/ui/card";

interface GapCardProps {
  index: number;
  statement: string;
}

export function GapCard({ index, statement }: GapCardProps) {
  return (
    <Card className="border-amber-dim/60 bg-amber-dim/5">
      <CardContent className="flex gap-4 p-5">
        <span className="font-mono text-2xl font-semibold leading-none text-amber/70">
          {String(index).padStart(2, "0")}
        </span>
        <div className="flex flex-col gap-1 pt-0.5">
          <span className="font-mono text-[11px] uppercase tracking-wide text-amber">
            Research gap {index}
          </span>
          <p className="text-balance font-display text-base leading-snug text-foreground">
            {statement}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
