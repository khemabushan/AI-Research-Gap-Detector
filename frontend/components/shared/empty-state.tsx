import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed border-border px-6 py-16 text-center">
      <span className="flex h-11 w-11 items-center justify-center rounded-full border border-border text-muted">
        <Icon className="h-5 w-5" />
      </span>
      <h3 className="font-display text-base font-semibold">{title}</h3>
      <p className="max-w-sm text-sm text-foreground-muted">{description}</p>
      {action}
    </div>
  );
}
