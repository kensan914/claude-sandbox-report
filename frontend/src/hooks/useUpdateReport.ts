"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";

type VisitRecordInput = {
  customer_id: number;
  visit_content: string;
  visited_at: string;
};

type UpdateReportRequest = {
  report_date: string;
  problem?: string;
  plan?: string;
  status: "DRAFT" | "SUBMITTED";
  visit_records: VisitRecordInput[];
};

type UpdateReportResponse = {
  data: {
    id: number;
    report_date: string;
    status: string;
  };
};

export function useUpdateReport(reportId: number) {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: UpdateReportRequest) =>
      apiClient.put<UpdateReportResponse>(`/reports/${reportId}`, {
        body: data,
      }),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      queryClient.invalidateQueries({ queryKey: ["reports", reportId] });
      router.push(`/reports/${response.data.id}`);
    },
  });
}

export type { UpdateReportRequest };
