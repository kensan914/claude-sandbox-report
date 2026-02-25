"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { ApiError, apiClient } from "@/lib/api-client";

type VisitRecordInput = {
  customer_id: number;
  visit_content: string;
  visited_at: string;
};

type CreateReportRequest = {
  report_date: string;
  problem?: string;
  plan?: string;
  status: "DRAFT" | "SUBMITTED";
  visit_records: VisitRecordInput[];
};

type CreateReportResponse = {
  data: {
    id: number;
    report_date: string;
    status: string;
  };
};

export function useCreateReport() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: CreateReportRequest) =>
      apiClient.post<CreateReportResponse>("/reports", { body: data }),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      router.push(`/reports/${response.data.id}`);
    },
  });
}

export { ApiError };
export type { CreateReportRequest };
