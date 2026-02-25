"use client";

import { Plus } from "lucide-react";
import Link from "next/link";
import { useCallback, useMemo, useState } from "react";
import {
  CustomerSearchForm,
  type CustomerSearchValues,
} from "@/components/features/customers/CustomerSearchForm";
import { CustomerTable } from "@/components/features/customers/CustomerTable";
import { Pagination } from "@/components/features/reports/Pagination";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import {
  type CustomerSearchParams,
  useCustomerList,
} from "@/hooks/useCustomers";

const PER_PAGE = 20;

const DEFAULT_SEARCH_VALUES: CustomerSearchValues = {
  company_name: "",
  contact_name: "",
};

export default function CustomersPage() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const [searchValues, setSearchValues] = useState<CustomerSearchValues>(
    DEFAULT_SEARCH_VALUES,
  );
  const [appliedSearch, setAppliedSearch] = useState<CustomerSearchValues>(
    DEFAULT_SEARCH_VALUES,
  );
  const [page, setPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({
    sort: "company_name",
    order: "asc",
  });

  const queryParams: CustomerSearchParams = useMemo(
    () => ({
      company_name: appliedSearch.company_name || undefined,
      contact_name: appliedSearch.contact_name || undefined,
      sort: sortConfig.sort,
      order: sortConfig.order,
      page,
      per_page: PER_PAGE,
    }),
    [appliedSearch, sortConfig, page],
  );

  const { data, isLoading } = useCustomerList(queryParams);

  const handleSearch = useCallback(() => {
    setAppliedSearch(searchValues);
    setPage(1);
  }, [searchValues]);

  const handleClear = useCallback(() => {
    setSearchValues(DEFAULT_SEARCH_VALUES);
    setAppliedSearch(DEFAULT_SEARCH_VALUES);
    setPage(1);
  }, []);

  const handleSort = useCallback((field: string) => {
    setSortConfig((prev) => ({
      sort: field,
      order: prev.sort === field && prev.order === "asc" ? "desc" : "asc",
    }));
    setPage(1);
  }, []);

  const customers = data?.data ?? [];
  const pagination = data?.pagination;
  const pageOffset = ((pagination?.current_page ?? 1) - 1) * PER_PAGE;

  if (isAuthLoading || !user) {
    return (
      <div className="space-y-6">
        <div className="h-9 w-48 rounded bg-muted animate-pulse" />
        <div className="h-24 rounded-lg border bg-muted/30 animate-pulse" />
        <div className="rounded-lg border">
          <div className="space-y-4 p-4">
            {["sk-a", "sk-b", "sk-c"].map((key) => (
              <div key={key} className="h-8 rounded bg-muted animate-pulse" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">顧客マスタ一覧</h2>
        <Button asChild>
          <Link href="/customers/new">
            <Plus className="size-4" />
            新規登録
          </Link>
        </Button>
      </div>

      <CustomerSearchForm
        values={searchValues}
        onChange={setSearchValues}
        onSearch={handleSearch}
        onClear={handleClear}
      />

      <CustomerTable
        customers={customers}
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
