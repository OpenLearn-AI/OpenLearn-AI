/**
 * Post-login redirect-target validation (F6).
 *
 * Validate a `redirectedFrom` query value as a safe redirect target: a
 * local, in-app path — never an external or protocol-relative URL, and
 * never the auth screens themselves. The value must start with a single
 * "/" (a path relative to the app origin); "//…" is rejected because the
 * browser resolves a protocol-relative URL against a foreign origin,
 * which would turn the query param into an open redirect. Values that
 * do not start with "/" at all (absolute URLs, schemes such as
 * `javascript:`, bare words) are rejected the same way. Auth routes are
 * rejected so a login/register flow cannot redirect back into itself.
 *
 * Note: this app's web origin serves no `/api` routes (the backend API
 * lives on a separate origin), so no API-path filtering is applied.
 *
 * This prevents open-redirect attacks via crafted query params while
 * preserving the deep-link return-to flow carried over by AuthGuard
 * (`/login?redirectedFrom=<pathname>`). The open-redirect logic itself
 * is intentionally unchanged by Batch 1.1; only its documentation was
 * aligned with the behavior, and `features/auth/redirect.test.ts` pins
 * the policy.
 */
export function safeRedirectTarget(value: string | null): string | null {
    if (!value) return null;
    // Must start with a single slash and must not target the auth routes.
    if (!value.startsWith("/") || value.startsWith("//")) return null;
    if (value.startsWith("/login") || value.startsWith("/register")) {
        return null;
    }
    return value;
}
