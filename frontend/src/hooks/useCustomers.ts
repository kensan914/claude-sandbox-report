"use client";

import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

type CustomerListItem = {
  id: number;
  company_name: string;
  contact_name: string;
  phone: string | null;
  email: string | null;
};

type CustomersResponse = {
  data: CustomerListItem[];
  pagination: {
    current_page: number;
    per_page: number;
    total_count: number;
    total_pages: number;
  };
};

export type { CustomerListItem };

export function useCustomers(
  companyName?: string,
  options?: { enabled?: boolean },
) {
  return useQuery({
    queryKey: ["customers", { company_name: companyName }],
    queryFn: () =>
      apiClient.get<CustomersResponse>("/customers", {
        params: {
          company_name: companyName || undefined,
          per_page: 100,
        },
      }),
    enabled: options?.enabled ?? true,
    placeholderData: keepPreviousData,
  });
}
