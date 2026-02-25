"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";

export function useDeleteReport(reportId: number) {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: () => apiClient.delete<void>(`/reports/${reportId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      router.push("/reports");
    },
  });
}
