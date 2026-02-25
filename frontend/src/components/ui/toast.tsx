"use client";

import { useAtomValue } from "jotai";
import { X } from "lucide-react";
import { useToast } from "@/hooks/useToast";
import { toastsAtom } from "@/lib/atoms";
import { cn } from "@/lib/utils";

export function ToastContainer() {
  const toasts = useAtomValue(toastsAtom);
  const { removeToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            "flex items-center gap-2 rounded-md border px-4 py-3 text-sm shadow-lg animate-in slide-in-from-top-2 fade-in",
            toast.type === "success" &&
              "border-green-200 bg-green-50 text-green-800",
            toast.type === "error" &&
              "border-destructive/50 bg-destructive/10 text-destructive",
          )}
        >
          <span className="flex-1">{toast.message}</span>
          <button
            type="button"
            onClick={() => removeToast(toast.id)}
            className="shrink-0 rounded-sm opacity-70 hover:opacity-100"
          >
            <X className="size-4" />
            <span className="sr-only">閉じる</span>
          </button>
        </div>
      ))}
    </div>
  );
}
