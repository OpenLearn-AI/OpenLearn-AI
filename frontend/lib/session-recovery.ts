/**
 * Global 401 session recovery (W1).
 *
 * Before Batch 1.2 there was no global handler for session expiry: a
 * forced token-refresh failure only surfaced as the static
 * "Your session has expired. Please log in again." strings in
 * `CourseForm` and `ProfileForm` — a dead end the user had to escape
 * by hand. This module implements the recovery half of the global 401
 * path defined by the roadmap (Batch 1.2):
 *
 *   1. `isSessionExpiredError` decides whether an error thrown by the
 *      API boundary (`lib/api.ts`) is a session-expiry failure. The
 *      boundary throws `ApiError(401, "Not authenticated")` both when
 *      no token can be obtained (including the forced-refresh failure
 *      path in `lib/keycloak.ts`) and when the backend answers 401.
 *   2. `triggerSessionRecovery` performs the recovery exactly once per
 *      page lifetime: clear the query cache (so no stale authenticated
 *      data survives the session) and route to `/login` carrying
 *      `redirectedFrom` so the login flow can return the user to the
 *      page where the session expired (the same deep-link convention
 *      AuthGuard uses; `features/auth/redirect.ts` validates the value
 *      on the way back).
 *
 * Call sites: the TanStack Query/Mutation cache error observers and the
 * Keycloak refresh-error subscription in `lib/query-provider.tsx`. The
 * recovery navigates with `window.location.assign` — a full reload is
 * the established end-of-session behavior in this app (logout does the
 * same) and guarantees a clean Keycloak re-initialization on the login
 * screen. The one-shot latch keeps concurrent 401s (a mutation plus a
 * refetch storm after the cache clears) from re-triggering or looping.
 */

import { ApiError } from "@/lib/api";

/** The login route every recovery lands on. */
export const SESSION_RECOVERY_LOGIN_PATH = "/login";

/**
 * Decide whether an error thrown by the API boundary is a
 * session-expiry (401) failure that the global recovery handles.
 */
export function isSessionExpiredError(error: unknown): boolean {
    return error instanceof ApiError && error.status === 401;
}

/**
 * Build the `/login` recovery URL carrying `redirectedFrom` for the
 * path the user was on when the session expired.
 */
export function sessionRecoveryTarget(currentPath: string): string {
    const params = new URLSearchParams({ redirectedFrom: currentPath });
    return `${SESSION_RECOVERY_LOGIN_PATH}?${params.toString()}`;
}

/**
 * The current location as a redirectable path (pathname + query), so a
 * deep link with a query string survives the login round trip. Falls
 * back to "/" when no `window` exists (SSR / non-browser tests).
 */
export function currentLocationPath(): string {
    if (typeof window === "undefined") {
        return "/";
    }
    return `${window.location.pathname}${window.location.search}`;
}

export interface SessionRecoveryOptions {
    /** Clear the query cache before routing away (injectable for tests). */
    clearCache?: () => void;
    /** Perform the navigation (defaults to `window.location.assign`). */
    redirect?: (target: string) => void;
    /** The path to carry as `redirectedFrom` (defaults to the current location). */
    currentPath?: string;
}

let recoveryTriggered = false;

/**
 * Perform the global 401 recovery at most once per page lifetime.
 * Safe to call from multiple error sources (query cache, mutation
 * cache, Keycloak refresh-error event): the first call clears the
 * cache and routes to `/login?redirectedFrom=...`; every later call is
 * a no-op until the page reloads.
 */
export function triggerSessionRecovery(
    options: SessionRecoveryOptions = {},
): void {
    if (recoveryTriggered) {
        return;
    }

    recoveryTriggered = true;

    const { clearCache, redirect, currentPath } = options;

    clearCache?.();

    const target = sessionRecoveryTarget(
        currentPath ?? currentLocationPath(),
    );

    if (redirect) {
        redirect(target);
    } else if (typeof window !== "undefined") {
        window.location.assign(target);
    }
}
