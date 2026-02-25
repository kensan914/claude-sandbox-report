"use client";

import { useSetAtom } from "jotai";
import { useCallback } from "react";
import { type Toast, toastsAtom } from "@/lib/atoms";

const AUTO_DISMISS_MS = 5000;

export function useToast() {
  const setToasts = useSetAtom(toastsAtom);

  const addToast = useCallback(
    (type: Toast["type"], message: string) => {
      const id = crypto.randomUUID();
      setToasts((prev) => [...prev, { id, type, message }]);

      if (type === "success") {
        setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== id));
        }, AUTO_DISMISS_MS);
      }
    },
    [setToasts],
  );

  const removeToast = useCallback(
    (id: string) => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    },
    [setToasts],
  );

  return { addToast, removeToast };
}
