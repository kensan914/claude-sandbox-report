"use client";

import { useQuery } from "@tanstack/react-query";
import { useSetAtom } from "jotai";
import { useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import type { Schemas } from "@/lib/api-types";
import { type AuthUser, authUserAtom } from "@/lib/atoms/auth";

type MeResponse = { data: Schemas["UserResponse"] };

export function useAuth() {
  const setAuthUser = useSetAtom(authUserAtom);

  const query = useQuery({
    queryKey: ["auth", "me"],
    queryFn: () => apiClient.get<MeResponse>("/auth/me"),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  useEffect(() => {
    if (query.data) {
      setAuthUser(query.data.data as AuthUser);
    }
  }, [query.data, setAuthUser]);

  return {
    user: query.data?.data ?? null,
    isLoading: query.isLoading,
  };
}
