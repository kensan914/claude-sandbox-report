"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

type ReviewResponse = {
  data: {
    id: number;
    status: string;
  };
};

export function useReviewReport(reportId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      apiClient.patch<ReviewResponse>(`/reports/${reportId}/review`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports", reportId] });
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });
}
