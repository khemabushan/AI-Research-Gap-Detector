import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export function useResearchGaps() {
  return useMutation({
    mutationFn: (queryId: number) => api.researchGaps(queryId),
  });
}
