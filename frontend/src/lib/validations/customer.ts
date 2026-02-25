import { z } from "zod";
import {
  emailSchema,
  maxLengthString,
  requiredMaxLengthString,
} from "./common";

/** 顧客マスタフォームのバリデーションスキーマ */
export const customerSchema = z.object({
  company_name: requiredMaxLengthString(200, "会社名"),
  contact_name: requiredMaxLengthString(100, "担当者名"),
  address: maxLengthString(500).optional().default(""),
  phone: maxLengthString(20).optional().default(""),
  email: z
    .union([z.literal(""), emailSchema()])
    .optional()
    .default(""),
});

export type CustomerFormValues = z.infer<typeof customerSchema>;
