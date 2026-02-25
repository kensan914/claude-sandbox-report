/**
 * E2Eテスト用データのセットアップ/クリーンアップ
 *
 * バックエンドAPIを直接呼び出してテストデータを投入・削除する。
 * Playwright の globalSetup / globalTeardown や各テストの beforeAll/afterAll で使用する。
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type ApiResponse<T> = { data: T };

/**
 * バックエンドAPIにリクエストを送信するヘルパー
 * テストデータ操作はサーバーサイドで行うため、Cookie ではなくトークンを直接使用する
 */
async function apiRequest<T>(
  method: string,
  path: string,
  options?: { body?: unknown; token?: string },
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (options?.token) {
    headers.Cookie = `access_token=${options.token}`;
  }

  const response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
    method,
    headers,
    body: options?.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(
      `API request failed: ${method} ${path} - ${response.status}: ${errorBody}`,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

/**
 * テストユーザーとしてログインし、認証トークンを取得する
 */
export async function getAuthToken(
  email: string,
  password: string,
): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error(`Login failed for ${email}: ${response.status}`);
  }

  // httpOnly Cookie からトークンを取得
  const setCookie = response.headers.get("set-cookie");
  const tokenMatch = setCookie?.match(/access_token=([^;]+)/);
  if (!tokenMatch) {
    throw new Error("access_token が Set-Cookie ヘッダーに含まれていません");
  }

  return tokenMatch[1];
}

/**
 * テスト用顧客データを作成する
 */
export async function createTestCustomer(
  token: string,
  data: {
    company_name: string;
    contact_name: string;
    phone?: string;
    email?: string;
    address?: string;
  },
): Promise<{ id: number }> {
  const res = await apiRequest<ApiResponse<{ id: number }>>(
    "POST",
    "/customers",
    { body: data, token },
  );
  return res.data;
}

/**
 * テスト用顧客データを削除する
 */
export async function deleteTestCustomer(
  token: string,
  customerId: number,
): Promise<void> {
  await apiRequest("DELETE", `/customers/${customerId}`, { token });
}
