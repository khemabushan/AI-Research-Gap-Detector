import { Skeleton } from "@/components/ui/skeleton";

export function PaperListSkeleton() {
  return (
    <div className="flex flex-col gap-2">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="flex flex-col gap-2 rounded-lg border border-border p-4">
          <Skeleton className="h-4 w-4/5" />
          <Skeleton className="h-3 w-2/5" />
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-3/5" />
        </div>
      ))}
    </div>
  );
}

export function GapReportSkeleton() {
  return (
    <div className="flex flex-col gap-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="flex gap-4 rounded-lg border border-border p-5">
          <Skeleton className="h-8 w-8 shrink-0 rounded-md" />
          <div className="flex flex-1 flex-col gap-2">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-5 w-4/5" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function ProjectIdeasSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="flex flex-col gap-3 rounded-lg border border-border p-5">
          <Skeleton className="h-4 w-3/5" />
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-2/3" />
        </div>
      ))}
    </div>
  );
}
