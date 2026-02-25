"use client";

import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useUsers } from "@/hooks/useUsers";
import type { UserRole } from "@/lib/atoms/auth";

type SearchValues = {
  date_from: string;
  date_to: string;
  salesperson_id: string;
  status: string;
};

type ReportSearchFormProps = {
  values: SearchValues;
  userRole: UserRole;
  onChange: (values: SearchValues) => void;
  onSearch: () => void;
  onClear: () => void;
};

const STATUS_OPTIONS = [
  { value: "", label: "全件" },
  { value: "DRAFT", label: "下書き" },
  { value: "SUBMITTED", label: "提出済み" },
  { value: "REVIEWED", label: "確認済み" },
];

const inputClass =
  "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50";

const selectClass =
  "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring";

export function ReportSearchForm({
  values,
  userRole,
  onChange,
  onSearch,
  onClear,
}: ReportSearchFormProps) {
  const { data: usersData } = useUsers();
  const salesUsers = usersData?.data.filter((u) => u.role === "SALES") ?? [];

  const handleChange = (field: keyof SearchValues, value: string) => {
    onChange({ ...values, [field]: value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch();
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-lg border bg-background p-4"
    >
      <div className="flex flex-wrap items-end gap-4">
        <div className="space-y-1">
          <label htmlFor="date_from" className="text-sm font-medium">
            報告日
          </label>
          <div className="flex items-center gap-2">
            <input
              id="date_from"
              type="date"
              className={inputClass}
              value={values.date_from}
              onChange={(e) => handleChange("date_from", e.target.value)}
            />
            <span className="text-sm text-muted-foreground">〜</span>
            <input
              id="date_to"
              type="date"
              className={inputClass}
              value={values.date_to}
              onChange={(e) => handleChange("date_to", e.target.value)}
            />
          </div>
        </div>

        {userRole === "MANAGER" && (
          <div className="space-y-1">
            <label htmlFor="salesperson_id" className="text-sm font-medium">
              担当者
            </label>
            <select
              id="salesperson_id"
              className={selectClass}
              value={values.salesperson_id}
              onChange={(e) => handleChange("salesperson_id", e.target.value)}
            >
              <option value="">全件</option>
              {salesUsers.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="space-y-1">
          <label htmlFor="status" className="text-sm font-medium">
            ステータス
          </label>
          <select
            id="status"
            className={selectClass}
            value={values.status}
            onChange={(e) => handleChange("status", e.target.value)}
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex gap-2">
          <Button type="submit" size="sm">
            <Search className="size-4" />
            検索
          </Button>
          <Button type="button" variant="outline" size="sm" onClick={onClear}>
            <X className="size-4" />
            クリア
          </Button>
        </div>
      </div>
    </form>
  );
}

export type { SearchValues };
