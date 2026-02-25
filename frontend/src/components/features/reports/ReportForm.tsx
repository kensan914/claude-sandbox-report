"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Plus, Save, Send } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { useFieldArray, useForm } from "react-hook-form";
import type { z } from "zod";
import { VisitRecordRow } from "@/components/features/reports/VisitRecordRow";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import {
  ApiError,
  type CreateReportRequest,
  useCreateReport,
} from "@/hooks/useCreateReport";
import { reportDraftSchema, reportSchema } from "@/lib/validations";

/** フォームの入力値型（optional フィールドを含む） */
type ReportFormInput = z.input<typeof reportSchema>;

const inputClass =
  "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50";

function getTodayString(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

export function ReportForm() {
  const router = useRouter();
  const createReport = useCreateReport();
  const [apiError, setApiError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isDirty },
    watch,
    setValue,
    trigger,
  } = useForm<ReportFormInput>({
    resolver: zodResolver(reportSchema),
    defaultValues: {
      report_date: getTodayString(),
      visit_records: [],
      problem: "",
      plan: "",
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "visit_records",
  });

  const handleAddVisitRecord = useCallback(() => {
    append({ customer_id: "", visit_content: "", visited_at: "" });
  }, [append]);

  const buildRequest = useCallback(
    (
      data: ReportFormInput,
      status: "DRAFT" | "SUBMITTED",
    ): CreateReportRequest => ({
      report_date: data.report_date,
      problem: data.problem || undefined,
      plan: data.plan || undefined,
      status,
      visit_records: data.visit_records.map((vr) => ({
        customer_id: Number(vr.customer_id),
        visit_content: vr.visit_content,
        visited_at: vr.visited_at,
      })),
    }),
    [],
  );

  const handleDraftSave = useCallback(async () => {
    setApiError(null);
    // Draft: only report_date is required
    const values = watch();
    const result = reportDraftSchema.safeParse(values);
    if (!result.success) {
      // Trigger validation to show errors
      await trigger("report_date");
      return;
    }
    const request = buildRequest(result.data as ReportFormInput, "DRAFT");
    createReport.mutate(request, {
      onError: (error) => {
        if (error instanceof ApiError) {
          setApiError(error.message);
        }
      },
    });
  }, [watch, trigger, buildRequest, createReport]);

  const handleSubmitReport = useCallback(
    async (data: ReportFormInput) => {
      setApiError(null);
      if (
        !window.confirm("日報を提出しますか？提出後は編集できなくなります。")
      ) {
        return;
      }
      const request = buildRequest(data, "SUBMITTED");
      createReport.mutate(request, {
        onError: (error) => {
          if (error instanceof ApiError) {
            setApiError(error.message);
          }
        },
      });
    },
    [buildRequest, createReport],
  );

  const handleCancel = useCallback(() => {
    if (isDirty) {
      if (!window.confirm("入力内容が破棄されますが、よろしいですか？")) {
        return;
      }
    }
    router.push("/reports");
  }, [isDirty, router]);

  const isSubmitting = createReport.isPending;

  return (
    <form
      onSubmit={handleSubmit(handleSubmitReport)}
      className="space-y-6"
      noValidate
    >
      {/* API Error */}
      {apiError && (
        <div className="rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {apiError}
        </div>
      )}

      {/* 報告日 */}
      <FormField<ReportFormInput>
        label="報告日"
        name="report_date"
        required
        errors={errors}
        className="max-w-xs"
      >
        <input
          id="report_date"
          type="date"
          className={inputClass}
          max={getTodayString()}
          {...register("report_date")}
        />
      </FormField>

      {/* 訪問記録 */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold border-b pb-2">訪問記録</h3>

        {fields.length === 0 && (
          <p className="text-sm text-muted-foreground py-4 text-center">
            訪問記録がありません。下のボタンから追加してください。
          </p>
        )}

        {fields.map((field, index) => {
          const vrErrors = errors.visit_records?.[index];
          return (
            <VisitRecordRow
              key={field.id}
              visitContent={watch(`visit_records.${index}.visit_content`) ?? ""}
              visitedAt={watch(`visit_records.${index}.visited_at`) ?? ""}
              customerIdError={vrErrors?.customer_id?.message}
              visitContentError={vrErrors?.visit_content?.message}
              visitedAtError={vrErrors?.visited_at?.message}
              onChangeCustomerId={(v) =>
                setValue(`visit_records.${index}.customer_id`, v, {
                  shouldDirty: true,
                })
              }
              onChangeVisitContent={(v) =>
                setValue(`visit_records.${index}.visit_content`, v, {
                  shouldDirty: true,
                })
              }
              onChangeVisitedAt={(v) =>
                setValue(`visit_records.${index}.visited_at`, v, {
                  shouldDirty: true,
                })
              }
              onRemove={() => remove(index)}
            />
          );
        })}

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleAddVisitRecord}
        >
          <Plus className="size-4" />
          訪問記録を追加
        </Button>
      </div>

      {/* Problem */}
      <FormField<ReportFormInput>
        label="Problem（課題・相談）"
        name="problem"
        errors={errors}
      >
        <textarea
          id="problem"
          className={`${inputClass} min-h-[120px] resize-y`}
          placeholder="今の課題や相談事項を入力してください..."
          {...register("problem")}
        />
      </FormField>

      {/* Plan */}
      <FormField<ReportFormInput>
        label="Plan（明日やること）"
        name="plan"
        errors={errors}
      >
        <textarea
          id="plan"
          className={`${inputClass} min-h-[120px] resize-y`}
          placeholder="明日の予定を入力してください..."
          {...register("plan")}
        />
      </FormField>

      {/* Buttons */}
      <div className="flex items-center gap-3 border-t pt-4">
        <Button
          type="button"
          variant="outline"
          disabled={isSubmitting}
          onClick={handleDraftSave}
        >
          {isSubmitting ? (
            <Loader2 className="size-4 animate-spin" />
          ) : (
            <Save className="size-4" />
          )}
          下書き保存
        </Button>

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? (
            <Loader2 className="size-4 animate-spin" />
          ) : (
            <Send className="size-4" />
          )}
          提出
        </Button>

        <Button
          type="button"
          variant="ghost"
          disabled={isSubmitting}
          onClick={handleCancel}
        >
          キャンセル
        </Button>
      </div>
    </form>
  );
}
