import { expect, test } from "@playwright/test";
import { TEST_USERS } from "./helpers/login";

// ログインテストは認証不要の状態で実行する
test.use({ storageState: { cookies: [], origins: [] } });

test.describe("ログイン画面 (SCR-LOGIN)", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
  });

  test("AUTH-001: 正常ログイン（SALES）", async ({ page }) => {
    const user = TEST_USERS.sales;

    await page.getByLabel("メールアドレス").fill(user.email);
    await page.getByLabel("パスワード").fill(user.password);
    await page.getByRole("button", { name: "ログイン" }).click();

    await expect(page).toHaveURL("/reports");
  });

  test("AUTH-002: 正常ログイン（MANAGER）", async ({ page }) => {
    const user = TEST_USERS.manager;

    await page.getByLabel("メールアドレス").fill(user.email);
    await page.getByLabel("パスワード").fill(user.password);
    await page.getByRole("button", { name: "ログイン" }).click();

    await expect(page).toHaveURL("/reports");
  });

  test("AUTH-003: 誤パスワードでログイン失敗", async ({ page }) => {
    await page.getByLabel("メールアドレス").fill(TEST_USERS.sales.email);
    await page.getByLabel("パスワード").fill("wrongpass");
    await page.getByRole("button", { name: "ログイン" }).click();

    await expect(
      page.getByText("メールアドレスまたはパスワードが正しくありません"),
    ).toBeVisible();
  });

  test("AUTH-008: 未認証時のリダイレクト", async ({ page }) => {
    await page.goto("/reports");

    await expect(page).toHaveURL("/login");
  });
});
