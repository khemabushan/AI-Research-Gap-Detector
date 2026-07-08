import { API_BASE_URL } from "@/lib/constants";
import type {
  AnalyzeResponse,
  ApiError,
  FutureDirectionsResponse,
  QueryDetailResponse,
  ResearchGapsResponse,
  SearchResponse,
} from "@/lib/types";

/**
 * Thrown for any non-2xx response or network failure. `status === 0` means
 * the request never reached the server (network/CORS/DNS failure) — callers
 * use this to distinguish "backend is down" from "backend returned an
 * error" and show an appropriate message.
 */
export class ApiRequestError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiRequestError";
    this.status = status;
    this.detail = detail;
  }
}

async function request<TResponse>(
  path: string,
  init?: RequestInit
): Promise<TResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new ApiRequestError(
      0,
      `Could not reach the backend at ${API_BASE_URL}. Check that it's running and that NEXT_PUBLIC_API_BASE_URL is correct.`
    );
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const errorBody = (await response.json()) as ApiError;
      detail = errorBody.detail ?? detail;
    } catch {
      // response had no JSON body — fall back to the generic message
    }
    throw new ApiRequestError(response.status, detail);
  }

  return response.json() as Promise<TResponse>;
}

const get = <TResponse>(path: string) => request<TResponse>(path, { method: "GET" });

const post = <TResponse>(path: string, body: unknown) =>
  request<TResponse>(path, { method: "POST", body: JSON.stringify(body) });

export const api = {
  search: (topic: string, maxResultsPerSource = 15) =>
    post<SearchResponse>("/search", { topic, max_results_per_source: maxResultsPerSource }),

  analyze: (queryId: number) => post<AnalyzeResponse>("/analyze", { query_id: queryId }),

  researchGaps: (queryId: number, numClusters?: number) =>
    post<ResearchGapsResponse>("/research-gaps", {
      query_id: queryId,
      num_clusters: numClusters ?? null,
    }),

  futureDirections: (queryId: number, numIdeas = 5) =>
    post<FutureDirectionsResponse>("/future-directions", {
      query_id: queryId,
      num_ideas: numIdeas,
    }),

  /** Re-fetches a query's full current state — papers, extractions, and gap report if generated. */
  getQuery: (queryId: number) => get<QueryDetailResponse>(`/queries/${queryId}`),

  health: () => get<{ status: string; env: string }>("/health"),
};
