"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Schemas } from "@/lib/api-types";

type ReportDetailResponse = {
  data: Schemas["ReportDetailResponse"];
};

export function useReport(id: number) {
  return useQuery({
    queryKey: ["reports", id],
    queryFn: () => apiClient.get<ReportDetailResponse>(`/reports/${id}`),
    enabled: id > 0,
  });
}
