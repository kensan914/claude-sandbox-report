"use client";

import { Trash2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { type CustomerListItem, useCustomers } from "@/hooks/useCustomers";

const inputClass =
  "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50";

type VisitRecordRowProps = {
  visitContent: string;
  visitedAt: string;
  customerIdError?: string;
  visitContentError?: string;
  visitedAtError?: string;
  onChangeCustomerId: (value: string) => void;
  onChangeVisitContent: (value: string) => void;
  onChangeVisitedAt: (value: string) => void;
  onRemove: () => void;
};

export function VisitRecordRow({
  visitContent,
  visitedAt,
  customerIdError,
  visitContentError,
  visitedAtError,
  onChangeCustomerId,
  onChangeVisitContent,
  onChangeVisitedAt,
  onRemove,
}: VisitRecordRowProps) {
  const [searchText, setSearchText] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [selectedCustomerName, setSelectedCustomerName] = useState("");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { data: customersData } = useCustomers(debouncedSearch, {
    enabled: isOpen && debouncedSearch.length > 0,
  });
  const customers = customersData?.data ?? [];

  const handleSearchChange = useCallback((value: string) => {
    setSearchText(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedSearch(value);
    }, 300);
  }, []);

  const handleSelectCustomer = useCallback(
    (customer: CustomerListItem) => {
      onChangeCustomerId(String(customer.id));
      setSelectedCustomerName(customer.company_name);
      setSearchText("");
      setIsOpen(false);
    },
    [onChangeCustomerId],
  );

  const handleRemoveClick = useCallback(() => {
    if (window.confirm("この訪問記録を削除しますか？")) {
      onRemove();
    }
  }, [onRemove]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="grid grid-cols-[1fr_2fr_auto_auto] gap-3 items-start border rounded-lg p-3">
      {/* 顧客選択 (インクリメンタルサーチ) */}
      <div className="space-y-1">
        <span className="text-sm font-medium">
          顧客 <span className="text-destructive">*</span>
        </span>
        <div className="relative" ref={dropdownRef}>
          <input
            type="text"
            className={inputClass}
            placeholder="顧客を検索..."
            value={isOpen ? searchText : selectedCustomerName}
            onChange={(e) => {
              handleSearchChange(e.target.value);
              if (!isOpen) setIsOpen(true);
            }}
            onFocus={() => {
              setIsOpen(true);
              setSearchText("");
            }}
          />
          {isOpen && customers.length > 0 && (
            <ul className="absolute z-10 mt-1 max-h-48 w-full overflow-auto rounded-md border bg-background shadow-md">
              {customers.map((customer) => (
                <li key={customer.id}>
                  <button
                    type="button"
                    className="w-full px-3 py-2 text-left text-sm hover:bg-accent"
                    onClick={() => handleSelectCustomer(customer)}
                  >
                    {customer.company_name}
                    <span className="ml-2 text-muted-foreground text-xs">
                      ({customer.contact_name})
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          {isOpen && debouncedSearch.length > 0 && customers.length === 0 && (
            <div className="absolute z-10 mt-1 w-full rounded-md border bg-background p-3 text-sm text-muted-foreground shadow-md">
              該当する顧客がありません
            </div>
          )}
        </div>
        {customerIdError && (
          <p className="text-destructive text-sm mt-1" role="alert">
            {customerIdError}
          </p>
        )}
      </div>

      {/* 訪問内容 */}
      <div className="space-y-1">
        <label className="text-sm font-medium">
          訪問内容 <span className="text-destructive">*</span>
          <textarea
            className={`${inputClass} min-h-[72px] resize-y`}
            placeholder="訪問内容を入力..."
            value={visitContent}
            onChange={(e) => onChangeVisitContent(e.target.value)}
          />
        </label>
        {visitContentError && (
          <p className="text-destructive text-sm mt-1" role="alert">
            {visitContentError}
          </p>
        )}
      </div>

      {/* 訪問時刻 */}
      <div className="space-y-1">
        <label className="text-sm font-medium">
          訪問時刻 <span className="text-destructive">*</span>
          <input
            type="time"
            className={inputClass}
            value={visitedAt}
            onChange={(e) => onChangeVisitedAt(e.target.value)}
          />
        </label>
        {visitedAtError && (
          <p className="text-destructive text-sm mt-1" role="alert">
            {visitedAtError}
          </p>
        )}
      </div>

      {/* 削除ボタン */}
      <div className="pt-6">
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          onClick={handleRemoveClick}
          title="訪問記録を削除"
        >
          <Trash2 className="size-4 text-destructive" />
        </Button>
      </div>
    </div>
  );
}
