import Link from "next/link";
import { ScanSearch } from "lucide-react";

import { ConnectionStatus } from "@/components/shared/connection-status";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-ink/80 backdrop-blur-md">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-md border border-teal-dim bg-teal-dim/40 text-teal">
            <ScanSearch className="h-4 w-4" />
          </span>
          <span className="font-display text-base font-semibold tracking-tight">
            Research Gap Detector
          </span>
        </Link>
        <ConnectionStatus />
      </div>
    </header>
  );
}
