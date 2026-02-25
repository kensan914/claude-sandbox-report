"use client";

import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import { useRouter } from "next/navigation";
import type { ReportListItem } from "@/hooks/useReports";
import { cn } from "@/lib/utils";
import { ReportStatusBadge } from "./ReportStatusBadge";

type SortConfig = {
  sort: string;
  order: string;
};

type ReportTableProps = {
  reports: ReportListItem[];
  isLoading: boolean;
  sortConfig: SortConfig;
  onSort: (field: string) => void;
  pageOffset: number;
};

const DAY_NAMES = ["日", "月", "火", "水", "木", "金", "土"];

function formatReportDate(dateStr: string): string {
  const date = new Date(dateStr);
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const dayName = DAY_NAMES[date.getDay()];
  return `${month}/${day}（${dayName}）`;
}

function formatSubmittedAt(dateStr: string | null): string {
  if (!dateStr) return "—";
  const date = new Date(dateStr);
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${month}/${day} ${hours}:${minutes}`;
}

const SORTABLE_COLUMNS = [
  { key: "report_date", label: "報告日" },
  { key: "salesperson_name", label: "担当者" },
  { key: "visit_count", label: "訪問件数" },
  { key: "status", label: "ステータス" },
  { key: "submitted_at", label: "提出日時" },
] as const;

function SortIcon({
  field,
  sortConfig,
}: {
  field: string;
  sortConfig: SortConfig;
}) {
  if (sortConfig.sort !== field) {
    return <ArrowUpDown className="size-3 text-muted-foreground" />;
  }
  return sortConfig.order === "asc" ? (
    <ArrowUp className="size-3" />
  ) : (
    <ArrowDown className="size-3" />
  );
}

const SKELETON_COLS = ["no", "date", "person", "visits", "status", "submitted"];

function SkeletonRow() {
  return (
    <tr className="animate-pulse">
      {SKELETON_COLS.map((col) => (
        <td key={col} className="px-4 py-3">
          <div className="h-4 rounded bg-muted" />
        </td>
      ))}
    </tr>
  );
}

export function ReportTable({
  reports,
  isLoading,
  sortConfig,
  onSort,
  pageOffset,
}: ReportTableProps) {
  const router = useRouter();

  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full text-sm">
        <thead className="bg-muted/50">
          <tr>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground w-12">
              No.
            </th>
            {SORTABLE_COLUMNS.map((col) => (
              <th
                key={col.key}
                className="px-4 py-3 text-left font-medium text-muted-foreground"
              >
                <button
                  type="button"
                  className="inline-flex items-center gap-1 hover:text-foreground transition-colors"
                  onClick={() => onSort(col.key)}
                >
                  {col.label}
                  <SortIcon field={col.key} sortConfig={sortConfig} />
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            ["sk-1", "sk-2", "sk-3", "sk-4", "sk-5"].map((key) => (
              <SkeletonRow key={key} />
            ))
          ) : reports.length === 0 ? (
            <tr>
              <td
                colSpan={6}
                className="px-4 py-12 text-center text-muted-foreground"
              >
                日報が見つかりません
              </td>
            </tr>
          ) : (
            reports.map((report, index) => (
              <tr
                key={report.id}
                className={cn(
                  "border-t cursor-pointer transition-colors hover:bg-muted/50",
                )}
                onClick={() => router.push(`/reports/${report.id}`)}
              >
                <td className="px-4 py-3 text-muted-foreground">
                  {pageOffset + index + 1}
                </td>
                <td className="px-4 py-3">
                  {formatReportDate(report.report_date)}
                </td>
                <td className="px-4 py-3">{report.salesperson.name}</td>
                <td className="px-4 py-3 text-center">{report.visit_count}</td>
                <td className="px-4 py-3">
                  <ReportStatusBadge status={report.status} />
                </td>
                <td className="px-4 py-3 text-muted-foreground">
                  {formatSubmittedAt(report.submitted_at)}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
