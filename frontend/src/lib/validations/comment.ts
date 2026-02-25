import { z } from "zod";
import { requiredMaxLengthString } from "./common";

/** コメントフォームのバリデーションスキーマ */
export const commentSchema = z.object({
  content: requiredMaxLengthString(1000, "コメント"),
});

export type CommentFormValues = z.infer<typeof commentSchema>;
