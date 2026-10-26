/**
 * OIDC attempt marker (Batch 4.1 corrective follow-up — §C.4 loop audit).
 *
 * With the auth entry points becoming DIRECT bridges to Keycloak (the
 * landing actions and `/login`/`/register` no longer sit behind a local
 * form), one failure mode opens up: a user who backs out of the hosted
 * Keycloak flow (browser Back, a Keycloak error redirect, or the
 * post-logout landing on `/login`) would be auto-redirected straight
 * back to Keycloak on every arrival — an app↔Keycloak ping-pong.
 *
 * The marker breaks that loop honestly: an entry bridge auto-initiates
 * the OIDC action ONCE per tab; on any later arrival it shows the
 * explicit sign-in button instead (the exact button the previous
 * flow had, so nothing is lost — the user just confirms deliberately).
 * The marker is cleared whenever the bridge observes an authenticated
 * session, so a future logout → `/login` arrival still shows the manual
 * form (LogoutButton marks the attempt before logging out for the same
 * reason).
 *
 * sessionStorage keeps the marker per-tab and self-cleaning (a stale
 * marker cannot survive a browser restart), and it never leaves the
 * device — no credentials or tokens are stored, only the fact that an
 * OIDC redirect was already attempted in this tab.
 */

const STORAGE_KEY = "openlearn.oidc-attempt";

export type OidcAttemptKind = "login" | "register";

export function markOidcAttempt(kind: OidcAttemptKind): void {
    if (typeof window === "undefined") {
        return;
    }

    try {
        window.sessionStorage.setItem(`${STORAGE_KEY}.${kind}`, "1");
    } catch {
        // Storage unavailable (privacy mode, disabled storage): the
        // marker is a UX guard, not a security control — degrading to
        // always-auto is the same behavior as the marker's absence.
    }
}

export function hasOidcAttempt(kind: OidcAttemptKind): boolean {
    if (typeof window === "undefined") {
        return false;
    }

    try {
        return window.sessionStorage.getItem(`${STORAGE_KEY}.${kind}`) === "1";
    } catch {
        return false;
    }
}

export function clearOidcAttempt(kind: OidcAttemptKind): void {
    if (typeof window === "undefined") {
        return;
    }

    try {
        window.sessionStorage.removeItem(`${STORAGE_KEY}.${kind}`);
    } catch {
        // Same degradation as markOidcAttempt.
    }
}
