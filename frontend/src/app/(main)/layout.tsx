"use client";

import { useState } from "react";
import { Header } from "@/components/features/layout/Header";
import { Sidebar } from "@/components/features/layout/Sidebar";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";

// TODO: Replace with real auth hook (e.g. TanStack Query + GET /auth/me)
const MOCK_USER = { name: "田中太郎", role: "SALES" };

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const user = MOCK_USER;

  return (
    <div className="flex min-h-screen flex-col">
      <Header
        user={user}
        onMenuToggle={() => setSidebarOpen((prev) => !prev)}
      />

      <div className="flex flex-1">
        {/* Desktop sidebar */}
        <aside className="hidden lg:block w-60 shrink-0 border-r bg-background">
          <Sidebar />
        </aside>

        {/* Mobile sidebar (Sheet) */}
        <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
          <SheetContent side="left" className="w-60 p-0">
            <SheetTitle className="sr-only">メニュー</SheetTitle>
            <Sidebar className="pt-4" />
          </SheetContent>
        </Sheet>

        {/* Main content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
