import { useQuery } from "@tanstack/react-query";

import { apiRequest } from "@/lib/api";
import type { MeResponse } from "../types";

export function useMe() {
  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: () => apiRequest<MeResponse>("/auth/me"),
    retry: 1,
  });
}