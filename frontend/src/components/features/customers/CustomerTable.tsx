"use client";

import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";
import { useRouter } from "next/navigation";
import type { CustomerListItem } from "@/hooks/useCustomers";
import { cn } from "@/lib/utils";

type SortConfig = {
  sort: string;
  order: string;
};

type CustomerTableProps = {
  customers: CustomerListItem[];
  isLoading: boolean;
  sortConfig: SortConfig;
  onSort: (field: string) => void;
  pageOffset: number;
};

const SORTABLE_COLUMNS = [
  { key: "company_name", label: "会社名" },
  { key: "contact_name", label: "担当者名" },
] as const;

const NON_SORTABLE_COLUMNS = [
  { key: "phone", label: "電話番号" },
  { key: "email", label: "メールアドレス" },
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

const SKELETON_COLS = ["no", "company", "contact", "phone", "email"];

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

export function CustomerTable({
  customers,
  isLoading,
  sortConfig,
  onSort,
  pageOffset,
}: CustomerTableProps) {
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
            {NON_SORTABLE_COLUMNS.map((col) => (
              <th
                key={col.key}
                className="px-4 py-3 text-left font-medium text-muted-foreground"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            ["sk-1", "sk-2", "sk-3", "sk-4", "sk-5"].map((key) => (
              <SkeletonRow key={key} />
            ))
          ) : customers.length === 0 ? (
            <tr>
              <td
                colSpan={5}
                className="px-4 py-12 text-center text-muted-foreground"
              >
                顧客が見つかりません
              </td>
            </tr>
          ) : (
            customers.map((customer, index) => (
              <tr
                key={customer.id}
                className={cn(
                  "border-t cursor-pointer transition-colors hover:bg-muted/50",
                )}
                onClick={() => router.push(`/customers/${customer.id}/edit`)}
              >
                <td className="px-4 py-3 text-muted-foreground">
                  {pageOffset + index + 1}
                </td>
                <td className="px-4 py-3">{customer.company_name}</td>
                <td className="px-4 py-3">{customer.contact_name}</td>
                <td className="px-4 py-3 text-muted-foreground">
                  {customer.phone ?? "—"}
                </td>
                <td className="px-4 py-3 text-muted-foreground">
                  {customer.email ?? "—"}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
