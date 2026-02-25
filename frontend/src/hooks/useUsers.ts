"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Schemas } from "@/lib/api-types";

type UsersResponse = {
  data: Schemas["UserListItemResponse"][];
};

export function useUsers(role?: "SALES" | "MANAGER") {
  return useQuery({
    queryKey: ["users", role],
    queryFn: () =>
      apiClient.get<UsersResponse>("/users", {
        params: role ? { role } : undefined,
      }),
  });
}
