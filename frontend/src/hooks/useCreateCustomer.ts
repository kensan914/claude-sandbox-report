"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useToast } from "@/hooks/useToast";
import { ApiError, apiClient } from "@/lib/api-client";

type CreateCustomerRequest = {
  company_name: string;
  contact_name: string;
  address?: string;
  phone?: string;
  email?: string;
};

type CreateCustomerResponse = {
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

export function useCreateCustomer() {
  const queryClient = useQueryClient();
  const router = useRouter();
  const { addToast } = useToast();

  return useMutation({
    mutationFn: (data: CreateCustomerRequest) =>
      apiClient.post<CreateCustomerResponse>("/customers", { body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      addToast("success", "顧客を登録しました");
      router.push("/customers");
    },
  });
}

export { ApiError };
export type { CreateCustomerRequest };
