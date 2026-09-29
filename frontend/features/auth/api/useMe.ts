import { queryOptions, useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api";
import { meResponseSchema, type Me } from "@/features/auth/schemas";
import { authKeys } from "@/features/auth/keys";

/**
 * Query options for the current-user query (D5 — `queryOptions`
 * objects next to the hooks). Exported so `prefetchQuery` /
 * `fetchQuery` can reuse the same definition.
 */
export const meOptions = queryOptions({
    queryKey: authKeys.me(),
    queryFn: () => apiFetch<Me>("/auth/me", { schema: meResponseSchema }),
});

export function useMe() {
    return useQuery(meOptions);
}
