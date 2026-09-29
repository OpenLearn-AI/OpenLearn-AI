"use client";

import {
    QueryClient,
    QueryClientProvider,
} from "@tanstack/react-query";
import { useState, type ReactNode } from "react";

/**
 * Explicit TanStack Query defaults (D5).
 *
 * The previous provider constructed `new QueryClient()` with no
 * options, which silently inherited the library defaults:
 *   - `staleTime: 0`  (every mount/focus refetched)
 *   - `retry: 3`       (every error retried 3x, including 401s)
 *   - `refetchOnWindowFocus: true` (every alt-tab refetched /auth/me)
 *
 * The deltas below make those defaults deliberate:
 *   - `staleTime: 30_000`  — read models are fresh for 30s; avoids
 *     hammering the API on every component mount.
 *   - `retry: 1`           — one retry on transient failures; a logged-out
 *     visitor's 401 no longer retries three times with backoff.
 *   - `refetchOnWindowFocus: false` — this app is not a dashboard that
 *     needs to snap to the latest on alt-tab; staleTime handles freshness.
 *
 * Individual queries may override these via `queryOptions` where a
 * domain-specific reason exists.
 */
const defaultQueryClientOptions = {
    queries: {
        staleTime: 30_000,
        retry: 1,
        refetchOnWindowFocus: false,
    },
    mutations: {},
};

export function AppQueryProvider({
    children,
}: {
    children: ReactNode;
}) {
    const [queryClient] = useState(
        () => new QueryClient({ defaultOptions: defaultQueryClientOptions }),
    );

    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    );
}
