"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import type { CreateCustomerRequest } from "@/hooks/useCreateCustomer";
import { useToast } from "@/hooks/useToast";
import { apiClient } from "@/lib/api-client";

type UpdateCustomerResponse = {
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

export function useUpdateCustomer(customerId: number) {
  const queryClient = useQueryClient();
  const router = useRouter();
  const { addToast } = useToast();

  return useMutation({
    mutationFn: (data: CreateCustomerRequest) =>
      apiClient.put<UpdateCustomerResponse>(`/customers/${customerId}`, {
        body: data,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      addToast("success", "顧客情報を更新しました");
      router.push("/customers");
    },
  });
}
