import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

/**
 * Polls GET /health so the UI can show a small connection-status indicator
 * rather than letting the person discover the backend is unreachable only
 * when a search fails.
 */
export function useBackendHealth() {
  return useQuery({
    queryKey: ["backend-health"],
    queryFn: () => api.health(),
    retry: false,
    refetchInterval: 30_000,
    refetchOnWindowFocus: true,
  });
}
