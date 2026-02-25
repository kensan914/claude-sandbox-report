"use client";

import { useRouter } from "next/navigation";
import { use, useEffect } from "react";
import { CustomerForm } from "@/components/features/customers/CustomerForm";
import { useCustomer } from "@/hooks/useCustomer";

export default function CustomerEditPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const customerId = Number(id);
  const { data, isLoading, error } = useCustomer(customerId);
  const router = useRouter();
  const customer = data?.data;

  // APIエラー時は一覧へリダイレクト
  useEffect(() => {
    if (error) {
      router.replace("/customers");
    }
  }, [error, router]);

  if (isLoading || !customer) {
    return (
      <div className="space-y-6">
        <div className="h-9 w-48 rounded bg-muted animate-pulse" />
        <div className="h-64 rounded-lg border bg-muted/30 animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">顧客マスタ編集</h2>
      <CustomerForm initialData={customer} />
    </div>
  );
}
