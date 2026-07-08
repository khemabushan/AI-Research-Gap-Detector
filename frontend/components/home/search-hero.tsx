"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ErrorBanner } from "@/components/shared/error-banner";
import { useSearchPapers } from "@/hooks/use-search-papers";
import { EXAMPLE_TOPICS } from "@/lib/constants";
import { ApiRequestError } from "@/lib/api-client";

export function SearchHero() {
  const [topic, setTopic] = useState("");
  const router = useRouter();
  const { mutate, isPending, error } = useSearchPapers();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!topic.trim() || isPending) return;

    mutate(
      { topic: topic.trim() },
      {
        onSuccess: (data) => {
          router.push(`/results/${data.query_id}`);
        },
      }
    );
  }

  return (
    <div className="flex flex-col items-center gap-8 animate-fade-up">
      <div className="flex flex-col items-center gap-3 text-center">
        <span className="font-mono text-xs uppercase tracking-[0.2em] text-teal">
          topic → evidence → gap
        </span>
        <h1 className="max-w-2xl text-balance font-display text-4xl font-semibold tracking-tight sm:text-5xl">
          Feed it a topic. Get back what&rsquo;s missing.
        </h1>
        <p className="max-w-lg text-balance text-foreground-muted">
          Enter a research topic and the system reads the literature, extracts
          methods and datasets from every paper, and reports exactly where the
          field has gaps &mdash; each one traceable to its source.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="w-full max-w-xl">
        <div className="flex items-center gap-2 rounded-lg border border-border bg-surface p-2 shadow-lg transition-colors focus-within:border-teal">
          <span className="pl-2 font-mono text-sm text-muted">&gt;</span>
          <Input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Brain Tumor Segmentation using Deep Learning"
            className="h-11 border-none bg-transparent px-1 shadow-none focus-visible:outline-none"
            disabled={isPending}
            autoFocus
          />
          <Button type="submit" disabled={!topic.trim() || isPending} className="shrink-0">
            {isPending ? (
              <>
                <Loader2 className="animate-spin" />
                Searching
              </>
            ) : (
              <>
                Search
                <ArrowRight />
              </>
            )}
          </Button>
        </div>
      </form>

      {error && (
        <div className="w-full max-w-xl">
          <ErrorBanner
            message={error instanceof ApiRequestError ? error.detail : "Search failed. Please try again."}
          />
        </div>
      )}

      <div className="flex flex-wrap items-center justify-center gap-2">
        <span className="font-mono text-xs text-muted">try:</span>
        {EXAMPLE_TOPICS.map((example) => (
          <button
            key={example}
            type="button"
            onClick={() => setTopic(example)}
            className="rounded-full border border-border px-3 py-1 text-xs text-foreground-muted transition-colors hover:border-teal-dim hover:text-teal"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  );
}
