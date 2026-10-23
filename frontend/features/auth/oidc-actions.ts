import { markOidcAttempt } from "@/features/auth/oidc-attempt";

/**
 * Shared OIDC action initiation (Batch 4.1 corrective follow-up §C.3).
 *
 * ONE implementation of "send the browser to Keycloak" for every auth
 * entry point — the landing navbar actions and the `/login`/`/register`
 * bridges all funnel through here, so there is no second (drifting)
 * auth implementation and no duplicated token/session state.
 *
 * Behavior preserved from the previous local forms:
 *   - `keycloak.login` / `keycloak.register` call sites and the PKCE /
 *     check-sso init contract in lib/keycloak.ts are untouched.
 *   - The redirect targets are unchanged: login honors the validated
 *     `redirectedFrom` (or `/dashboard`), register lands on
 *     `/dashboard` (whose gate then routes fresh users into
 *     `/onboarding`).
 *   - The OIDC attempt marker is written BEFORE the browser leaves, so
 *     a Back/cancel arrival never auto-loops (see oidc-attempt.ts).
 *
 * `getKeycloak()` is imported dynamically: the landing page stays free
 * of any Keycloak initialization until a visitor actually clicks an
 * auth action, and the module (and its config validation) is never
 * evaluated on surfaces that don't need it.
 */

export type OidcActionKind = "login" | "register";

/**
 * Initiate the Keycloak action. Resolves when the redirect has been
 * started (the navigation itself usually tears the page down before
 * the promise settles) and REJECTS when the action could not be
 * started (unreachable auth service, adapter failure) so callers can
 * surface a real error instead of dead-ending.
 */
export async function initiateOidcAction(
    kind: OidcActionKind,
    redirectPath: string,
): Promise<void> {
    const { getKeycloak } = await import("@/lib/keycloak");
    const keycloak = await getKeycloak();

    if (!keycloak) {
        throw new Error("Unable to connect to the authentication service.");
    }

    // Mark before navigating: if the user comes back to an entry bridge
    // (Back key, cancel, error redirect) it must show the manual form,
    // not fire the redirect again.
    markOidcAttempt(kind);

    if (kind === "register") {
        await keycloak.register({
            redirectUri: `${window.location.origin}${redirectPath}`,
        });
    } else {
        await keycloak.login({
            redirectUri: `${window.location.origin}${redirectPath}`,
        });
    }
}

/** The error message surfaced by every auth entry when the OIDC
 * action cannot be started (same string the previous forms used). */
export const OIDC_CONNECT_ERROR =
    "Unable to connect to the authentication service.";

/** Type guard narrowing an unknown error to a displayable message. */
export function oidcActionErrorMessage(error: unknown): string {
    return error instanceof Error
        ? error.message
        : "Unable to start authentication. Please try again.";
}
