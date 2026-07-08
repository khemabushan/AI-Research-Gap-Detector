import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export function useAnalyzePapers() {
  return useMutation({
    mutationFn: (queryId: number) => api.analyze(queryId),
  });
}
