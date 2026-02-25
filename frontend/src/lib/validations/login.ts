import { z } from "zod";
import { emailSchema, requiredString } from "./common";

/** ログインフォームのバリデーションスキーマ */
export const loginSchema = z.object({
  email: emailSchema(),
  password: requiredString("パスワード"),
});

export type LoginFormValues = z.infer<typeof loginSchema>;
