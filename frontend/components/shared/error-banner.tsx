import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3">
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
      <div className="flex flex-1 flex-col gap-2">
        <p className="text-sm text-foreground">{message}</p>
        {onRetry && (
          <Button variant="outline" size="sm" className="w-fit" onClick={onRetry}>
            Try again
          </Button>
        )}
      </div>
    </div>
  );
}
