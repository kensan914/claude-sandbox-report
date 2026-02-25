"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

type CustomerDetailResponse = {
  data: {
    id: number;
    company_name: string;
    contact_name: string;
    address: string | null;
    phone: string | null;
    email: string | null;
    created_at: string;
    updated_at: string;
  };
};

export type { CustomerDetailResponse };

export function useCustomer(id: number) {
  return useQuery({
    queryKey: ["customers", id],
    queryFn: () => apiClient.get<CustomerDetailResponse>(`/customers/${id}`),
    enabled: id > 0,
  });
}
