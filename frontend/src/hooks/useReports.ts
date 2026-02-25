"use client";

import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Schemas } from "@/lib/api-types";

type ReportListItem = {
  id: number;
  report_date: string;
  salesperson: Schemas["SalespersonResponse"];
  visit_count: number;
  status: string;
  submitted_at: string | null;
};

type ReportListResponse = {
  data: ReportListItem[];
  pagination: {
    current_page: number;
    per_page: number;
    total_count: number;
    total_pages: number;
  };
};

export type ReportSearchParams = {
  date_from?: string;
  date_to?: string;
  salesperson_id?: number;
  status?: string;
  sort?: string;
  order?: string;
  page?: number;
  per_page?: number;
};

export type { ReportListItem };

export function useReports(params: ReportSearchParams) {
  return useQuery({
    queryKey: ["reports", params],
    queryFn: () =>
      apiClient.get<ReportListResponse>("/reports", {
        params: {
          ...params,
          salesperson_id: params.salesperson_id,
          page: params.page,
          per_page: params.per_page,
        } as Record<string, string | number | undefined>,
      }),
    placeholderData: keepPreviousData,
  });
}
