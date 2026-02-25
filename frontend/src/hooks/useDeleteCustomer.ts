"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useToast } from "@/hooks/useToast";
import { apiClient } from "@/lib/api-client";

export function useDeleteCustomer(customerId: number) {
  const queryClient = useQueryClient();
  const router = useRouter();
  const { addToast } = useToast();

  return useMutation({
    mutationFn: () => apiClient.delete<void>(`/customers/${customerId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      addToast("success", "顧客を削除しました");
      router.push("/customers");
    },
  });
}
