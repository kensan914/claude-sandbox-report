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

export type CustomerSearchParams = {
  company_name?: string;
  contact_name?: string;
  sort?: string;
  order?: string;
  page?: number;
  per_page?: number;
};

export function useCustomerList(params: CustomerSearchParams) {
  return useQuery({
    queryKey: ["customers", "list", params],
    queryFn: () =>
      apiClient.get<CustomersResponse>("/customers", {
        params: {
          ...params,
        } as Record<string, string | number | undefined>,
      }),
    placeholderData: keepPreviousData,
  });
}
