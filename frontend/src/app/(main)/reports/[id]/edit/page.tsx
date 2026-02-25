"use client";

import { useRouter } from "next/navigation";
import { use, useEffect } from "react";
import { ReportForm } from "@/components/features/reports/ReportForm";
import { useAuth } from "@/hooks/useAuth";
import { useReport } from "@/hooks/useReport";

export default function ReportEditPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const reportId = Number(id);
  const { user, isLoading: isAuthLoading } = useAuth();
  const { data, isLoading: isReportLoading, error } = useReport(reportId);
  const router = useRouter();
  const report = data?.data;

  // MANAGER はアクセス不可
  useEffect(() => {
    if (!isAuthLoading && user?.role === "MANAGER") {
      router.replace("/reports");
    }
  }, [user, isAuthLoading, router]);

  // DRAFT以外は詳細画面へリダイレクト
  useEffect(() => {
    if (report && report.status !== "DRAFT") {
      router.replace(`/reports/${reportId}`);
    }
  }, [report, reportId, router]);

  // 本人以外の日報はリダイレクト
  useEffect(() => {
    if (report && user && report.salesperson.id !== user.id) {
      router.replace(`/reports/${reportId}`);
    }
  }, [report, user, reportId, router]);

  // APIエラー時（403等）はリダイレクト
  useEffect(() => {
    if (error) {
      router.replace(`/reports/${reportId}`);
    }
  }, [error, reportId, router]);

  if (isAuthLoading || isReportLoading || !user || !report) {
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

  if (report.status !== "DRAFT" || report.salesperson.id !== user.id) {
    return null;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">日報編集</h2>
      <ReportForm initialData={report} />
    </div>
  );
}
