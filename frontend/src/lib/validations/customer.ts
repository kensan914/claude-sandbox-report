import { z } from "zod";
import {
  emailSchema,
  maxLengthString,
  requiredMaxLengthString,
} from "./common";

/** 電話番号形式（数字・ハイフン・括弧・プラス記号のみ許可） */
const phoneSchema = () =>
  z
    .string()
    .check(z.maxLength(20, "20文字以内で入力してください"))
    .check(
      z.refine(
        (val) => val === "" || /^[\d\-+() ]+$/.test(val),
        "電話番号の形式で入力してください",
      ),
    );

/** 顧客マスタフォームのバリデーションスキーマ */
export const customerSchema = z.object({
  company_name: requiredMaxLengthString(200, "会社名"),
  contact_name: requiredMaxLengthString(100, "担当者名"),
  address: maxLengthString(500).optional().default(""),
  phone: phoneSchema().optional().default(""),
  email: z
    .union([z.literal(""), emailSchema()])
    .optional()
    .default(""),
});

export type CustomerFormValues = z.infer<typeof customerSchema>;
