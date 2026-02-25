"use client";

import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";

type CustomerSearchValues = {
  company_name: string;
  contact_name: string;
};

type CustomerSearchFormProps = {
  values: CustomerSearchValues;
  onChange: (values: CustomerSearchValues) => void;
  onSearch: () => void;
  onClear: () => void;
};

const inputClass =
  "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50";

export function CustomerSearchForm({
  values,
  onChange,
  onSearch,
  onClear,
}: CustomerSearchFormProps) {
  const handleChange = (field: keyof CustomerSearchValues, value: string) => {
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
          <label htmlFor="company_name" className="text-sm font-medium">
            会社名
          </label>
          <input
            id="company_name"
            type="text"
            className={inputClass}
            placeholder="部分一致検索"
            value={values.company_name}
            onChange={(e) => handleChange("company_name", e.target.value)}
          />
        </div>

        <div className="space-y-1">
          <label htmlFor="contact_name" className="text-sm font-medium">
            担当者名
          </label>
          <input
            id="contact_name"
            type="text"
            className={inputClass}
            placeholder="部分一致検索"
            value={values.contact_name}
            onChange={(e) => handleChange("contact_name", e.target.value)}
          />
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

export type { CustomerSearchValues };
