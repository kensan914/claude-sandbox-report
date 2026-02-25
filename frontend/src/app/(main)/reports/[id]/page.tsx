"use client";

import { ArrowLeft, Pencil } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";
import { CommentSection } from "@/components/features/reports/CommentSection";
import { ReportStatusBadge } from "@/components/features/reports/ReportStatusBadge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useReport } from "@/hooks/useReport";
import { useReviewReport } from "@/hooks/useReviewReport";
import type { Schemas } from "@/lib/api-types";

type Comment = Schemas["CommentResponse"];

function formatReportDate(dateString: string): string {
  const date = new Date(`${dateString}T00:00:00`);
  const days = ["日", "月", "火", "水", "木", "金", "土"];
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  const day = days[date.getDay()];
  return `${y}/${m}/${d}（${day}）`;
}

function formatSubmittedAt(dateString: string | null): string {
  if (!dateString) return "—";
  const date = new Date(dateString);
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  const h = String(date.getHours()).padStart(2, "0");
  const min = String(date.getMinutes()).padStart(2, "0");
  return `${m}/${d} ${h}:${min}`;
}

export default function ReportDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const reportId = Number(id);
  const { user, isLoading: isAuthLoading } = useAuth();
  const { data, isLoading: isReportLoading, error } = useReport(reportId);
  const reviewMutation = useReviewReport(reportId);
  const router = useRouter();
  const [showConfirm, setShowConfirm] = useState(false);

  const report = data?.data;

  // SALESが他人の日報にアクセスした場合リダイレクト
  useEffect(() => {
    if (
      report &&
      user &&
      user.role === "SALES" &&
      report.salesperson.id !== user.id
    ) {
      router.replace("/reports");
    }
  }, [report, user, router]);

  // APIエラー時リダイレクト
  useEffect(() => {
    if (error) {
      router.replace("/reports");
    }
  }, [error, router]);

  if (isAuthLoading || isReportLoading || !user || !report) {
    return (
      <div className="space-y-6">
        <div className="h-9 w-48 rounded bg-muted animate-pulse" />
        <div className="h-64 rounded-lg border bg-muted/30 animate-pulse" />
      </div>
    );
  }

  // SALES が他人の日報を見ようとしている場合
  if (user.role === "SALES" && report.salesperson.id !== user.id) {
    return null;
  }

  const canEdit =
    user.role === "SALES" &&
    user.id === report.salesperson.id &&
    report.status === "DRAFT";

  const canComment =
    user.role === "MANAGER" &&
    (report.status === "SUBMITTED" || report.status === "REVIEWED");

  const canReview = user.role === "MANAGER" && report.status === "SUBMITTED";

  const problemComments = report.comments.filter(
    (c: Comment) => c.target === "PROBLEM",
  );
  const planComments = report.comments.filter(
    (c: Comment) => c.target === "PLAN",
  );

  const handleReview = () => {
    reviewMutation.mutate(undefined, {
      onSuccess: () => {
        setShowConfirm(false);
      },
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">日報詳細</h2>
        <div className="flex items-center gap-2">
          {canEdit && (
            <Button variant="outline" asChild>
              <Link href={`/reports/${reportId}/edit`}>
                <Pencil className="size-4" />
                編集
              </Link>
            </Button>
          )}
          <Button variant="outline" asChild>
            <Link href="/reports">
              <ArrowLeft className="size-4" />
              一覧に戻る
            </Link>
          </Button>
        </div>
      </div>

      {/* Meta info */}
      <div className="rounded-lg border p-4 space-y-3">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div>
            <p className="text-sm text-muted-foreground">報告日</p>
            <p className="font-medium">
              {formatReportDate(report.report_date)}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">担当者</p>
            <p className="font-medium">{report.salesperson.name}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">ステータス</p>
            <div className="mt-1">
              <ReportStatusBadge status={report.status} />
            </div>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">提出日時</p>
            <p className="font-medium">
              {formatSubmittedAt(report.submitted_at)}
            </p>
          </div>
        </div>
      </div>

      {/* Visit records */}
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">訪問記録</h3>
        {report.visit_records.length === 0 ? (
          <p className="text-sm text-muted-foreground">訪問記録はありません</p>
        ) : (
          <div className="rounded-lg border overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-2 text-left w-12">#</th>
                  <th className="px-4 py-2 text-left">顧客</th>
                  <th className="px-4 py-2 text-left">訪問内容</th>
                  <th className="px-4 py-2 text-left w-24">訪問時刻</th>
                </tr>
              </thead>
              <tbody>
                {report.visit_records.map(
                  (
                    record: Schemas["VisitRecordDetailResponse"],
                    index: number,
                  ) => (
                    <tr key={record.id} className="border-b last:border-0">
                      <td className="px-4 py-2">{index + 1}</td>
                      <td className="px-4 py-2">
                        {record.customer.company_name}
                      </td>
                      <td className="px-4 py-2 whitespace-pre-wrap">
                        {record.visit_content}
                      </td>
                      <td className="px-4 py-2">{record.visited_at}</td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Problem */}
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">Problem（課題・相談）</h3>
        <div className="rounded-lg border p-4">
          <p className="text-sm whitespace-pre-wrap">
            {report.problem || "記載なし"}
          </p>
        </div>
        <CommentSection
          reportId={reportId}
          target="PROBLEM"
          comments={problemComments}
          canComment={canComment}
        />
      </div>

      {/* Plan */}
      <div className="space-y-2">
        <h3 className="text-lg font-semibold">Plan（明日やること）</h3>
        <div className="rounded-lg border p-4">
          <p className="text-sm whitespace-pre-wrap">
            {report.plan || "記載なし"}
          </p>
        </div>
        <CommentSection
          reportId={reportId}
          target="PLAN"
          comments={planComments}
          canComment={canComment}
        />
      </div>

      {/* Review button */}
      {canReview && (
        <div className="flex justify-end">
          {showConfirm ? (
            <div className="flex items-center gap-3 rounded-lg border p-4">
              <p className="text-sm">この日報を確認済みにしますか？</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowConfirm(false)}
              >
                キャンセル
              </Button>
              <Button
                size="sm"
                onClick={handleReview}
                disabled={reviewMutation.isPending}
              >
                {reviewMutation.isPending ? "処理中..." : "確認"}
              </Button>
            </div>
          ) : (
            <Button onClick={() => setShowConfirm(true)}>確認済みにする</Button>
          )}
        </div>
      )}
    </div>
  );
}
