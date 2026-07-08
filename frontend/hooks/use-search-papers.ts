import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export function useSearchPapers() {
  return useMutation({
    mutationFn: ({ topic, maxResultsPerSource }: { topic: string; maxResultsPerSource?: number }) =>
      api.search(topic, maxResultsPerSource),
  });
}
