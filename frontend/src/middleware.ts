import { type NextRequest, NextResponse } from "next/server";

const COOKIE_NAME = "access_token";

/** 認証が必要なパスのプレフィックス（(main) グループ） */
const PROTECTED_PATHS = ["/reports", "/customers"];

/** 認証済みユーザーがアクセスすべきでないパス */
const AUTH_PATHS = ["/login"];

function isProtectedPath(pathname: string): boolean {
  return PROTECTED_PATHS.some(
    (path) => pathname === path || pathname.startsWith(`${path}/`),
  );
}

function isAuthPath(pathname: string): boolean {
  return AUTH_PATHS.some(
    (path) => pathname === path || pathname.startsWith(`${path}/`),
  );
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get(COOKIE_NAME)?.value;

  // 未認証で認証必須ページにアクセス → /login にリダイレクト
  if (!token && isProtectedPath(pathname)) {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }

  // 認証済みで /login にアクセス → /reports にリダイレクト
  if (token && isAuthPath(pathname)) {
    const reportsUrl = new URL("/reports", request.url);
    return NextResponse.redirect(reportsUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/reports/:path*", "/customers/:path*", "/login/:path*"],
};
