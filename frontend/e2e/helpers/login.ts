import type { Page } from "@playwright/test";

/** テスト用ユーザー情報 */
export const TEST_USERS = {
  sales: {
    email: "tanaka@example.com",
    password: "password123",
    name: "田中太郎",
    role: "SALES" as const,
  },
  manager: {
    email: "yamada@example.com",
    password: "password123",
    name: "山田部長",
    role: "MANAGER" as const,
  },
} as const;

type TestUserKey = keyof typeof TEST_USERS;

/**
 * 指定したユーザーでログインする
 * ログインフォームに入力し、日報一覧画面への遷移を待つ
 */
export async function login(
  page: Page,
  userKey: TestUserKey = "sales",
): Promise<void> {
  const user = TEST_USERS[userKey];

  await page.goto("/login");
  await page.getByLabel("メールアドレス").fill(user.email);
  await page.getByLabel("パスワード").fill(user.password);
  await page.getByRole("button", { name: "ログイン" }).click();

  // ログイン成功後、日報一覧画面に遷移するまで待機
  await page.waitForURL("/reports");
}
