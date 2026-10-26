"use client";

import {
    MutationCache,
    QueryCache,
    QueryClient,
    QueryClientProvider,
} from "@tanstack/react-query";
import { useEffect, useState, type ReactNode } from "react";

import { onKeycloakRefreshError } from "@/lib/keycloak";
import {
    isSessionExpiredError,
    triggerSessionRecovery,
} from "@/lib/session-recovery";

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

/**
 * W1 — the global 401 path.
 *
 * The provider owns the application-wide session recovery: when any
 * query or mutation fails with a session-expiry error (ApiError 401,
 * both for a failed token refresh and for a 401 response), or when
 * Keycloak reports a failed forced token refresh through its
 * `onAuthRefreshError` event, the query cache is cleared and the
 * browser routes to `/login` carrying `redirectedFrom`
 * (lib/session-recovery.ts). Non-401 errors are unaffected; the cache
 * handlers run after the configured retries are exhausted.
 *
 * The mounted client is registered on mount so the cache handlers
 * (constructed with the client) never reference the component variable
 * during initialization; the one-shot latch inside
 * `triggerSessionRecovery` makes the multiple trigger sources safe.
 */
let mountedQueryClient: QueryClient | null = null;

function performSessionRecovery(): void {
    triggerSessionRecovery({
        clearCache: () => mountedQueryClient?.clear(),
    });
}

export function AppQueryProvider({
    children,
}: {
    children: ReactNode;
}) {
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: defaultQueryClientOptions,
                queryCache: new QueryCache({
                    onError: (error) => {
                        if (isSessionExpiredError(error)) {
                            performSessionRecovery();
                        }
                    },
                }),
                mutationCache: new MutationCache({
                    onError: (error) => {
                        if (isSessionExpiredError(error)) {
                            performSessionRecovery();
                        }
                    },
                }),
            }),
    );

    // Register the mounted client for the recovery path and subscribe
    // to the Keycloak token-refresh-failure event (covers failures
    // observed outside the query/mutation caches;
    // lib/auth-context.tsx separately mirrors the event into React
    // auth state so the existing AuthGuard redirect reacts as well).
    useEffect(() => {
        mountedQueryClient = queryClient;

        const unsubscribe = onKeycloakRefreshError(() => {
            performSessionRecovery();
        });

        return () => {
            unsubscribe();

            if (mountedQueryClient === queryClient) {
                mountedQueryClient = null;
            }
        };
    }, [queryClient]);

    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    );
}
