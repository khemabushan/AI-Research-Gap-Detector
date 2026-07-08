import { ScrollArea } from "@/components/ui/scroll-area";
import { PaperCard } from "@/components/results/paper-card";
import type { Paper } from "@/lib/types";

interface PaperListProps {
  papers: Paper[];
  selectedPaperId: number | null;
  onSelect: (paperId: number) => void;
}

export function PaperList({ papers, selectedPaperId, onSelect }: PaperListProps) {
  return (
    <ScrollArea className="h-[560px] pr-3">
      <div className="flex flex-col gap-2">
        {papers.map((paper) => (
          <PaperCard
            key={paper.id}
            paper={paper}
            isSelected={paper.id === selectedPaperId}
            onSelect={() => onSelect(paper.id)}
          />
        ))}
      </div>
    </ScrollArea>
  );
}
