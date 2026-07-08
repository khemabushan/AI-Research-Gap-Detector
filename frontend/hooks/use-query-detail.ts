import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export function useQueryDetail(queryId: number) {
  return useQuery({
    queryKey: ["query", queryId],
    queryFn: () => api.getQuery(queryId),
    enabled: Number.isFinite(queryId) && queryId > 0,
  });
}
