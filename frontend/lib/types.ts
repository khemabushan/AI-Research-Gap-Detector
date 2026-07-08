// Mirrors app/models/schemas.py in the backend exactly — keep in sync.

export type PaperSource = "arxiv" | "semantic_scholar";

export type QueryStatus =
  | "pending"
  | "collecting"
  | "extracting"
  | "analyzing"
  | "done"
  | "failed";

export interface Paper {
  id: number;
  source: PaperSource;
  external_id: string;
  title: string;
  authors: string[];
  year: number | null;
  abstract: string;
  citation_count: number | null;
  url: string | null;
}

export interface SearchResponse {
  query_id: number;
  topic: string;
  total_papers: number;
  papers: Paper[];
}

export interface Extraction {
  paper_id: number;
  problem: string;
  methodology: string;
  dataset: string;
  model: string;
  limitations: string;
  future_work: string;
}

export interface AnalyzeResponse {
  query_id: number;
  status: QueryStatus;
  papers_processed: number;
  papers_failed: number;
  extractions: Extraction[];
}

export interface ClusterSummary {
  cluster_id: number;
  paper_ids: number[];
  theme: string;
  common_methods: string[];
  common_datasets: string[];
}

export interface ResearchGapsResponse {
  query_id: number;
  topic: string;
  summary: string;
  identified_gaps: string[];
  clusters: ClusterSummary[];
  generated_at: string;
}

export interface ProjectIdea {
  title: string;
  description: string;
  grounded_in_gap: string;
  novelty_rationale: string;
  suggested_approach: string;
}

export interface FutureDirectionsResponse {
  query_id: number;
  future_directions: string[];
  novel_project_ideas: ProjectIdea[];
  generated_at: string;
}

export interface ApiError {
  error?: string;
  detail: string;
}

// ---------------------------------------------------------------------------
// GET /queries/{id}
// ---------------------------------------------------------------------------

export interface GapReportSummary {
  summary: string;
  identified_gaps: string[];
  cluster_summary: ClusterSummary[];
  future_directions: string[];
  novel_project_ideas: ProjectIdea[];
  generated_at: string;
}

export interface QueryDetailResponse {
  query_id: number;
  topic: string;
  status: QueryStatus;
  created_at: string;
  total_papers: number;
  papers: Paper[];
  extractions: Extraction[];
  gap_report: GapReportSummary | null;
}
