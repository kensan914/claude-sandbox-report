"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useSetAtom } from "jotai";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { ApiError, apiClient } from "@/lib/api-client";
import type { ResponseBody } from "@/lib/api-types";
import { type AuthUser, authUserAtom } from "@/lib/atoms/auth";
import { type LoginFormValues, loginSchema } from "@/lib/validations/login";

type LoginResponse = ResponseBody<"/api/v1/auth/login", "post">;

export default function LoginPage() {
  const router = useRouter();
  const setAuthUser = useSetAtom(authUserAtom);
  const [apiError, setApiError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormValues) => {
    setApiError(null);
    try {
      const res = await apiClient.post<LoginResponse>("/auth/login", {
        body: data,
      });
      setAuthUser(res.data.user as AuthUser);
      router.push("/reports");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setApiError(error.message);
      } else {
        setApiError("エラーが発生しました");
      }
    }
  };

  return (
    <div className="w-full max-w-sm space-y-6">
      <h1 className="text-center text-2xl font-bold">営業日報システム</h1>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-4 rounded-lg border bg-background p-6 shadow-sm"
      >
        <FormField<LoginFormValues>
          label="メールアドレス"
          name="email"
          required
          errors={errors}
        >
          <input
            id="email"
            type="email"
            autoComplete="email"
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            {...register("email")}
          />
        </FormField>

        <FormField<LoginFormValues>
          label="パスワード"
          name="password"
          required
          errors={errors}
        >
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            {...register("password")}
          />
        </FormField>

        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? "ログイン中..." : "ログイン"}
        </Button>

        {apiError && (
          <p className="text-center text-sm text-destructive" role="alert">
            {apiError}
          </p>
        )}
      </form>
    </div>
  );
}
