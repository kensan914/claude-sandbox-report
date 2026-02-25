import { z } from "zod";
import {
  optionalMaxLengthString,
  pastOrTodayDateSchema,
  requiredMaxLengthString,
  requiredString,
  timeStringSchema,
} from "./common";

/** 訪問記録のバリデーションスキーマ */
export const visitRecordSchema = z.object({
  customer_id: requiredString("顧客"),
  visit_content: requiredMaxLengthString(1000, "訪問内容"),
  visited_at: timeStringSchema(),
});

/** 日報フォームのバリデーションスキーマ（提出時） */
export const reportSchema = z.object({
  report_date: pastOrTodayDateSchema(),
  visit_records: z.array(visitRecordSchema),
  problem: optionalMaxLengthString(2000),
  plan: optionalMaxLengthString(2000),
});

/** 日報フォームのバリデーションスキーマ（下書き保存時：報告日のみ必須） */
export const reportDraftSchema = z.object({
  report_date: pastOrTodayDateSchema(),
  visit_records: z.array(visitRecordSchema).optional().default([]),
  problem: optionalMaxLengthString(2000),
  plan: optionalMaxLengthString(2000),
});

export type ReportFormValues = z.infer<typeof reportSchema>;
export type ReportDraftFormValues = z.infer<typeof reportDraftSchema>;
