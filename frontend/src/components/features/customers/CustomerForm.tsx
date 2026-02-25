"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Save, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { useForm } from "react-hook-form";
import type { z } from "zod";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import {
  ApiError,
  type CreateCustomerRequest,
  useCreateCustomer,
} from "@/hooks/useCreateCustomer";
import { useDeleteCustomer } from "@/hooks/useDeleteCustomer";
import { useUpdateCustomer } from "@/hooks/useUpdateCustomer";
import { customerSchema } from "@/lib/validations/customer";

/** フォームの入力値型（optional フィールドを含む） */
type CustomerFormInput = z.input<typeof customerSchema>;

type CustomerFormProps = {
  /** 編集モード時の既存顧客データ */
  initialData?: {
    id: number;
    company_name: string;
    contact_name: string;
    address: string | null;
    phone: string | null;
    email: string | null;
  };
};

const inputClass =
  "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50";

export function CustomerForm({ initialData }: CustomerFormProps) {
  const router = useRouter();
  const isEditMode = !!initialData;
  const createCustomer = useCreateCustomer();
  const updateCustomer = useUpdateCustomer(initialData?.id ?? 0);
  const deleteCustomer = useDeleteCustomer(initialData?.id ?? 0);
  const [apiError, setApiError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<CustomerFormInput>({
    resolver: zodResolver(customerSchema),
    defaultValues: initialData
      ? {
          company_name: initialData.company_name,
          contact_name: initialData.contact_name,
          address: initialData.address ?? "",
          phone: initialData.phone ?? "",
          email: initialData.email ?? "",
        }
      : {
          company_name: "",
          contact_name: "",
          address: "",
          phone: "",
          email: "",
        },
  });

  const handleSave = useCallback(
    (data: CustomerFormInput) => {
      setApiError(null);
      const request: CreateCustomerRequest = {
        company_name: data.company_name,
        contact_name: data.contact_name,
        address: data.address || undefined,
        phone: data.phone || undefined,
        email: data.email || undefined,
      };
      const mutation = isEditMode ? updateCustomer : createCustomer;
      mutation.mutate(request, {
        onError: (error) => {
          if (error instanceof ApiError) {
            setApiError(error.message);
          }
        },
      });
    },
    [isEditMode, createCustomer, updateCustomer],
  );

  const handleDelete = useCallback(() => {
    if (!window.confirm("この顧客を削除しますか？この操作は取り消せません。")) {
      return;
    }
    setApiError(null);
    deleteCustomer.mutate(undefined, {
      onError: (error) => {
        if (error instanceof ApiError) {
          setApiError(error.message);
        }
      },
    });
  }, [deleteCustomer]);

  const handleCancel = useCallback(() => {
    if (isDirty) {
      if (!window.confirm("入力内容が破棄されますが、よろしいですか？")) {
        return;
      }
    }
    router.push("/customers");
  }, [isDirty, router]);

  const isSubmitting =
    createCustomer.isPending ||
    updateCustomer.isPending ||
    deleteCustomer.isPending;

  return (
    <form
      onSubmit={handleSubmit(handleSave)}
      className="space-y-6 max-w-lg"
      noValidate
    >
      {apiError && (
        <div className="rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {apiError}
        </div>
      )}

      <FormField<CustomerFormInput>
        label="会社名"
        name="company_name"
        required
        errors={errors}
      >
        <input
          id="company_name"
          type="text"
          className={inputClass}
          placeholder="株式会社○○"
          {...register("company_name")}
        />
      </FormField>

      <FormField<CustomerFormInput>
        label="担当者名"
        name="contact_name"
        required
        errors={errors}
      >
        <input
          id="contact_name"
          type="text"
          className={inputClass}
          placeholder="山田太郎"
          {...register("contact_name")}
        />
      </FormField>

      <FormField<CustomerFormInput> label="住所" name="address" errors={errors}>
        <input
          id="address"
          type="text"
          className={inputClass}
          placeholder="東京都千代田区..."
          {...register("address")}
        />
      </FormField>

      <FormField<CustomerFormInput>
        label="電話番号"
        name="phone"
        errors={errors}
      >
        <input
          id="phone"
          type="tel"
          className={inputClass}
          placeholder="03-1234-5678"
          {...register("phone")}
        />
      </FormField>

      <FormField<CustomerFormInput>
        label="メールアドレス"
        name="email"
        errors={errors}
      >
        <input
          id="email"
          type="email"
          className={inputClass}
          placeholder="example@example.co.jp"
          {...register("email")}
        />
      </FormField>

      <div className="flex items-center gap-3 border-t pt-4">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? (
            <Loader2 className="size-4 animate-spin" />
          ) : (
            <Save className="size-4" />
          )}
          保存
        </Button>

        <Button
          type="button"
          variant="ghost"
          disabled={isSubmitting}
          onClick={handleCancel}
        >
          キャンセル
        </Button>

        {isEditMode && (
          <Button
            type="button"
            variant="destructive"
            disabled={isSubmitting}
            onClick={handleDelete}
            className="ml-auto"
          >
            {deleteCustomer.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Trash2 className="size-4" />
            )}
            削除
          </Button>
        )}
      </div>
    </form>
  );
}
