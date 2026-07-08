import { useMutation } from "@tanstack/react-query";

import { api } from "@/lib/api-client";

export function useFutureDirections() {
  return useMutation({
    mutationFn: (queryId: number) => api.futureDirections(queryId),
  });
}
