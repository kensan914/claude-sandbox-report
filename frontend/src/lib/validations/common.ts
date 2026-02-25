import { z } from "zod";

/**
 * 共通バリデーションユーティリティ
 * 日本語エラーメッセージ付きの共通バリデーションパターン
 */

/** 必須チェック（空文字も不可） */
export const requiredString = (fieldName?: string) =>
  z
    .string()
    .check(
      z.minLength(
        1,
        fieldName ? `${fieldName}を入力してください` : "入力してください",
      ),
    );

/** メール形式チェック */
export const emailSchema = () =>
  requiredString().check(z.email("メール形式で入力してください"));

/** 最大文字数チェック */
export const maxLengthString = (n: number) =>
  z.string().check(z.maxLength(n, `${n}文字以内で入力してください`));

/** 必須 + 最大文字数チェック */
export const requiredMaxLengthString = (n: number, fieldName?: string) =>
  requiredString(fieldName).check(
    z.maxLength(n, `${n}文字以内で入力してください`),
  );

/** 日付文字列（YYYY-MM-DD 形式） */
export const dateStringSchema = () =>
  z
    .string()
    .check(z.regex(/^\d{4}-\d{2}-\d{2}$/, "日付形式で入力してください"));

/** 未来日不可の日付チェック */
export const pastOrTodayDateSchema = () =>
  dateStringSchema().check(
    z.refine((val) => {
      const inputDate = new Date(val);
      const today = new Date();
      today.setHours(23, 59, 59, 999);
      return inputDate <= today;
    }, "未来の日付は指定できません"),
  );

/** 任意のテキスト（空文字許可）+ 最大文字数 */
export const optionalMaxLengthString = (n: number) =>
  z
    .string()
    .check(z.maxLength(n, `${n}文字以内で入力してください`))
    .optional()
    .default("");

/** 時刻文字列（HH:mm 形式） */
export const timeStringSchema = () =>
  z
    .string()
    .check(z.regex(/^\d{2}:\d{2}$/, "時刻形式（HH:mm）で入力してください"));
