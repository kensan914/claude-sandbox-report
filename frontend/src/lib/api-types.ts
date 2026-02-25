/**
 * OpenAPI 型定義から抽出した型ヘルパー。
 * `bun run generate:types` で生成される api.d.ts の型を
 * API クライアントで型安全に利用するためのユーティリティ。
 */
import type { components, paths } from "@/types/api";

/** スキーマ型のショートカット */
export type Schemas = components["schemas"];

/** パス型のエクスポート */
export type ApiPaths = paths;

/**
 * 指定パス・メソッドのリクエストボディ型を取得する。
 *
 * @example
 * type LoginBody = RequestBody<"/api/v1/auth/login", "post">;
 * // => { email: string; password: string }
 */
export type RequestBody<
  P extends keyof paths,
  M extends keyof paths[P],
> = paths[P][M] extends {
  requestBody: { content: { "application/json": infer B } };
}
  ? B
  : never;

/**
 * 指定パス・メソッドの成功レスポンス型（200 or 201）を取得する。
 *
 * @example
 * type LoginResponse = ResponseBody<"/api/v1/auth/login", "post">;
 * // => { access_token: string; token_type: string }
 */
export type ResponseBody<
  P extends keyof paths,
  M extends keyof paths[P],
> = paths[P][M] extends {
  responses: {
    200: { content: { "application/json": infer R } };
  };
}
  ? R
  : paths[P][M] extends {
        responses: {
          201: { content: { "application/json": infer R } };
        };
      }
    ? R
    : never;

/**
 * 指定パス・メソッドのクエリパラメータ型を取得する。
 *
 * @example
 * type ReportsQuery = QueryParams<"/api/v1/reports", "get">;
 */
export type QueryParams<
  P extends keyof paths,
  M extends keyof paths[P],
> = paths[P][M] extends { parameters: { query?: infer Q } } ? Q : never;

/**
 * 指定パス・メソッドのパスパラメータ型を取得する。
 *
 * @example
 * type ReportPathParams = PathParams<"/api/v1/reports/{report_id}", "get">;
 */
export type PathParams<
  P extends keyof paths,
  M extends keyof paths[P],
> = paths[P][M] extends { parameters: { path: infer PP } } ? PP : never;
