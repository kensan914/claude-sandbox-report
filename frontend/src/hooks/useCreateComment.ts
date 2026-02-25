"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Schemas } from "@/lib/api-types";

type CommentCreateRequest = {
  target: "PROBLEM" | "PLAN";
  content: string;
};

type CommentCreateResponse = {
  data: Schemas["CommentCreateResponse"];
};

export function useCreateComment(reportId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CommentCreateRequest) =>
      apiClient.post<CommentCreateResponse>(`/reports/${reportId}/comments`, {
        body: data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports", reportId] });
    },
  });
}
