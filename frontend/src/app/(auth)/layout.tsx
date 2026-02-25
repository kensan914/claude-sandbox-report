/**
 * (auth) グループ用レイアウト
 * ヘッダー・サイドメニューなしの中央寄せレイアウト
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40">
      {children}
    </div>
  );
}
