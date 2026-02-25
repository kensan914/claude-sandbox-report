"use client";

import { CustomerForm } from "@/components/features/customers/CustomerForm";

export default function CustomerNewPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">顧客マスタ登録</h2>
      <CustomerForm />
    </div>
  );
}
