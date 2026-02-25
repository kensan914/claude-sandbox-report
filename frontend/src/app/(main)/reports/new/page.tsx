"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { ReportForm } from "@/components/features/reports/ReportForm";
import { useAuth } from "@/hooks/useAuth";

export default function ReportNewPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  // MANAGER はアクセス不可 → 一覧へリダイレクト
  useEffect(() => {
    if (!isLoading && user?.role === "MANAGER") {
      router.replace("/reports");
    }
  }, [user, isLoading, router]);

  if (isLoading || !user) {
    return (
      <div className="space-y-6">
        <div className="h-9 w-48 rounded bg-muted animate-pulse" />
        <div className="h-64 rounded-lg border bg-muted/30 animate-pulse" />
      </div>
    );
  }

  if (user.role === "MANAGER") {
    return null;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">日報作成</h2>
      <ReportForm />
    </div>
  );
}
