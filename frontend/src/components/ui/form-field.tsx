"use client";

import type * as React from "react";
import type {
  FieldErrors,
  FieldPath,
  FieldValues,
  UseFormReturn,
} from "react-hook-form";

import { cn } from "@/lib/utils";

/**
 * フォームフィールドのエラーメッセージを表示するコンポーネント
 * フィールド下に赤字でバリデーションエラーを表示する
 */
function FormFieldError<T extends FieldValues>({
  errors,
  name,
  className,
}: {
  errors: FieldErrors<T>;
  name: FieldPath<T>;
  className?: string;
}) {
  const pathParts = name.split(".");
  let error: unknown = errors;
  for (const part of pathParts) {
    if (error == null || typeof error !== "object") return null;
    error = (error as Record<string, unknown>)[part];
  }

  const fieldError = error as { message?: string } | undefined;
  if (!fieldError?.message) return null;

  return (
    <p className={cn("text-destructive text-sm mt-1", className)} role="alert">
      {fieldError.message}
    </p>
  );
}

/**
 * フォームフィールドのラッパーコンポーネント
 * ラベル + 入力フィールド + エラーメッセージを統一的に表示する
 */
function FormField<T extends FieldValues>({
  label,
  name,
  required,
  errors,
  children,
  className,
}: {
  label: string;
  name: FieldPath<T>;
  required?: boolean;
  errors: FieldErrors<T>;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("space-y-1", className)}>
      <label htmlFor={name} className="text-sm font-medium leading-none">
        {label}
        {required && <span className="text-destructive ml-1">*</span>}
      </label>
      {children}
      <FormFieldError<T> errors={errors} name={name} />
    </div>
  );
}

/**
 * useFormのヘルパー型
 * zodResolverと組み合わせたuseFormの戻り値型
 */
type FormInstance<T extends FieldValues> = UseFormReturn<T>;

export { FormField, FormFieldError, type FormInstance };
