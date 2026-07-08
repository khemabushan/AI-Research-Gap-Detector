import { ArrowUpRight } from "lucide-react";

interface FutureDirectionListProps {
  directions: string[];
}

export function FutureDirectionList({ directions }: FutureDirectionListProps) {
  return (
    <ul className="flex flex-col gap-2.5">
      {directions.map((direction, index) => (
        <li
          key={index}
          className="flex items-start gap-3 rounded-md border border-border bg-surface px-4 py-3"
        >
          <ArrowUpRight className="mt-0.5 h-4 w-4 shrink-0 text-teal" />
          <p className="text-sm leading-relaxed text-foreground-muted">{direction}</p>
        </li>
      ))}
    </ul>
  );
}
