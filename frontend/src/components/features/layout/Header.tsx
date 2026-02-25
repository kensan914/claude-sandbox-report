"use client";

import { LogOut, Menu } from "lucide-react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const ROLE_LABELS: Record<string, string> = {
  SALES: "営業",
  MANAGER: "マネージャー",
};

type HeaderProps = {
  user: { name: string; role: string } | null;
  onMenuToggle: () => void;
};

export function Header({ user, onMenuToggle }: HeaderProps) {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await fetch("/api/v1/auth/logout", { method: "POST" });
    } finally {
      router.push("/login");
    }
  };

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center border-b bg-background px-4">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden mr-2"
        onClick={onMenuToggle}
        aria-label="メニューを開く"
      >
        <Menu className="size-5" />
      </Button>

      <h1 className="text-lg font-semibold">営業日報システム</h1>

      <div className="ml-auto flex items-center gap-3">
        {user && (
          <>
            <span className="text-sm hidden sm:inline">{user.name}</span>
            <Badge variant="secondary">
              {ROLE_LABELS[user.role] ?? user.role}
            </Badge>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              aria-label="ログアウト"
            >
              <LogOut className="size-4" />
            </Button>
          </>
        )}
      </div>
    </header>
  );
}
