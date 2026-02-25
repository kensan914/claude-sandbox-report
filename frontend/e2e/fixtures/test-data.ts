/**
 * E2Eテスト用テストデータ定義
 *
 * テスト仕様書（TEST_DEFINITION.md）のテストデータ定義に基づく。
 * 実際のデータ投入はバックエンド側のシーダーまたはAPIを通じて行う。
 * ここではテストコード内で参照する定数を定義する。
 */

/** テスト用顧客データ */
export const TEST_CUSTOMERS = {
  C001: {
    company_name: "○○株式会社",
    contact_name: "佐藤一郎",
    phone: "03-1111-2222",
    email: "sato@oo.co.jp",
  },
  C002: {
    company_name: "△△商事",
    contact_name: "伊藤二郎",
    phone: "06-3333-4444",
    email: "ito@sankaku.co.jp",
  },
  C003: {
    company_name: "□□工業",
    contact_name: "渡辺三郎",
    phone: "052-5555-6666",
    email: "watanabe@shiro.co.jp",
  },
} as const;

/** テスト用日報ステータス */
export const REPORT_STATUS = {
  DRAFT: "DRAFT",
  SUBMITTED: "SUBMITTED",
  REVIEWED: "REVIEWED",
} as const;

/** ステータスの日本語表示 */
export const STATUS_LABELS = {
  DRAFT: "下書き",
  SUBMITTED: "提出済み",
  REVIEWED: "確認済み",
} as const;
