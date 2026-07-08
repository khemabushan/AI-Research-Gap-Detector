import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Formats a paper's citation count for display, e.g. 1500 -> "1.5k citations". */
export function formatCitations(count: number | null): string {
  if (count === null) return "Citations unknown";
  if (count === 0) return "No citations yet";
  if (count >= 1000) return `${(count / 1000).toFixed(1)}k citations`;
  return `${count} citation${count === 1 ? "" : "s"}`;
}

/** Formats a source enum value into a display label. */
export function formatSource(source: "arxiv" | "semantic_scholar"): string {
  return source === "arxiv" ? "arXiv" : "Semantic Scholar";
}

/** Produces a stable short paper reference tag, e.g. paper id 4 -> "P4". */
export function paperTag(paperId: number): string {
  return `P${paperId}`;
}

/** Truncates text to a max length at a word boundary, appending an ellipsis. */
export function truncate(text: string, maxChars: number): string {
  if (text.length <= maxChars) return text;
  return text.slice(0, maxChars).replace(/\s+\S*$/, "") + "…";
}
