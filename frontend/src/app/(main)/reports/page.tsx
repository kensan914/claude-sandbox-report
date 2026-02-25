"use client";

import { Plus } from "lucide-react";
import Link from "next/link";
import { useCallback, useMemo, useState } from "react";
import { Pagination } from "@/components/features/reports/Pagination";
import {
  ReportSearchForm,
  type SearchValues,
} from "@/components/features/reports/ReportSearchForm";
import { ReportTable } from "@/components/features/reports/ReportTable";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { type ReportSearchParams, useReports } from "@/hooks/useReports";

function getDefaultDateFrom(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`;
}

function getDefaultDateTo(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

const PER_PAGE = 20;

function getDefaultSearchValues(): SearchValues {
  return {
    date_from: getDefaultDateFrom(),
    date_to: getDefaultDateTo(),
    salesperson_id: "",
    status: "",
  };
}

export default function ReportsPage() {
  const { user } = useAuth();
  const [searchValues, setSearchValues] = useState<SearchValues>(
    getDefaultSearchValues,
  );
  const [appliedSearch, setAppliedSearch] = useState<SearchValues>(
    getDefaultSearchValues,
  );
  const [page, setPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({
    sort: "report_date",
    order: "desc",
  });

  const queryParams: ReportSearchParams = useMemo(
    () => ({
      date_from: appliedSearch.date_from || undefined,
      date_to: appliedSearch.date_to || undefined,
      salesperson_id: appliedSearch.salesperson_id
        ? Number(appliedSearch.salesperson_id)
        : undefined,
      status: appliedSearch.status || undefined,
      sort: sortConfig.sort,
      order: sortConfig.order,
      page,
      per_page: PER_PAGE,
    }),
    [appliedSearch, sortConfig, page],
  );

  const { data, isLoading } = useReports(queryParams);

  const handleSearch = useCallback(() => {
    setAppliedSearch(searchValues);
    setPage(1);
  }, [searchValues]);

  const handleClear = useCallback(() => {
    const defaults = getDefaultSearchValues();
    setSearchValues(defaults);
    setAppliedSearch(defaults);
    setPage(1);
  }, []);

  const handleSort = useCallback((field: string) => {
    setSortConfig((prev) => ({
      sort: field,
      order: prev.sort === field && prev.order === "desc" ? "asc" : "desc",
    }));
    setPage(1);
  }, []);

  const reports = data?.data ?? [];
  const pagination = data?.pagination;
  const pageOffset = ((pagination?.current_page ?? 1) - 1) * PER_PAGE;

  if (!user) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">日報一覧</h2>
        {user.role === "SALES" && (
          <Button asChild>
            <Link href="/reports/new">
              <Plus className="size-4" />
              新規作成
            </Link>
          </Button>
        )}
      </div>

      <ReportSearchForm
        values={searchValues}
        userRole={user.role as "SALES" | "MANAGER"}
        onChange={setSearchValues}
        onSearch={handleSearch}
        onClear={handleClear}
      />

      <ReportTable
        reports={reports}
        isLoading={isLoading}
        sortConfig={sortConfig}
        onSort={handleSort}
        pageOffset={pageOffset}
      />

      {pagination && (
        <Pagination
          currentPage={pagination.current_page}
          totalPages={pagination.total_pages}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
