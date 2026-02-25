import path from "node:path";
import { test as setup } from "@playwright/test";
import { login } from "./helpers/login";

const authFile = path.join(__dirname, "../playwright/.auth/user.json");

setup("SALES ユーザーで認証状態を保存", async ({ page }) => {
  await login(page, "sales");
  await page.context().storageState({ path: authFile });
});
