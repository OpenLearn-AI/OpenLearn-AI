"use client";

import * as React from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { useAuth } from "@/lib/auth-context";
import { safeRedirectTarget } from "@/features/auth/redirect";
import {
    clearOidcAttempt,
    hasOidcAttempt,
    markOidcAttempt,
} from "@/features/auth/oidc-attempt";
import {
    initiateOidcAction,
    oidcActionErrorMessage,
} from "@/features/auth/oidc-actions";

/**
 * Minimal, functional authentication entry bridge (Batch 4.1 corrective
 * follow-up §C.4) — replaces the previous local login/register forms,
 * which added a redundant extra click between the landing page and
 * Keycloak.
 *
 * Intended journey (§C.1): landing → Keycloak → OIDC callback →
 * onboarding when required → dashboard or intended destination. The
 * landing's own actions already initiate Keycloak directly; THIS
 * component exists for the arrivals that still must be honored:
 *
 *   - `AuthGuard` redirects unauthenticated visitors of protected
 *     routes to `/login?redirectedFrom=<route>` — the bridge preserves
 *     the deep-link return-to flow (validated by `safeRedirectTarget`,
 *     unchanged).
 *   - `LogoutButton` redirects to `/login` after a confirmed logout.
 *   - Bookmark/typed-history visits to `/login` and `/register`.
 *
 * Loop safety (§C.4: "audit all links and redirects so they do not
 * accidentally loop"):
 *   - The bridge auto-initiates the OIDC action ONCE per tab (the
 *     attempt marker in features/auth/oidc-attempt.ts). A later arrival
 *     in the same tab — Keycloak Back, a cancel/error redirect, or the
 *     post-logout landing — renders the explicit sign-in button
 *     instead of auto-redirecting again, so the app and Keycloak can
 *     never ping-pong.
 *   - An authenticated arrival never auto-fires: the user is replaced
 *     to their target (and the marker cleared so a future logout →
 *     login cycle behaves).
 *   - Every redirect the bridge issues is a validated local target —
 *     never an auth route, never an external URL (open-redirect
 *     protections unchanged).
 *
 * The pinned button strings ("Sign in with OpenLearn AI", "Create
 * account") and the redirect targets are preserved from the previous
 * flow; the E2E suite keeps its real-OIDC coverage through these same
 * strings.
 */

const ENTRY_COPY = {
    login: {
        redirecting: "Taking you to secure sign-in…",
        heading: "Sign in to your account",
        sub: "Continue through OpenLearn's secure sign-on.",
        action: "Sign in with OpenLearn AI",
        busy: "Connecting…",
    },
    register: {
        redirecting: "Taking you to account creation…",
        heading: "Create an account",
        sub: "Continue through OpenLearn's secure sign-on.",
        action: "Create account",
        busy: "Connecting…",
    },
} as const;

/**
 * Storage-event subscription for the attempt marker's external store.
 * Same-tab writes need no notification (the writer component either
 * navigates away immediately or tracks its own pending/error state);
 * cross-tab writes surface through the "storage" event.
 */
function subscribeToStorageEvents(callback: () => void): () => void {
    window.addEventListener("storage", callback);

    return () => {
        window.removeEventListener("storage", callback);
    };
}

export function OidcEntryBridge({ mode }: { mode: "login" | "register" }) {
    const copy = ENTRY_COPY[mode];
    const router = useRouter();
    const searchParams = useSearchParams();
    const { isAuthenticated, isLoading } = useAuth();

    const [error, setError] = React.useState<string | null>(null);
    const [isPending, setIsPending] = React.useState(false);

    // Login honors the validated originally-requested route (the same
    // target policy the previous LoginForm implemented); registration
    // keeps its fixed /dashboard destination — the onboarding gate
    // routes fresh users from there.
    const targetPath =
        mode === "login"
            ? (safeRedirectTarget(searchParams.get("redirectedFrom")) ??
              "/dashboard")
            : "/dashboard";

    // Whether the auto-redirect already ran in this tab — read as an
    // EXTERNAL store (sessionStorage), not React state: a later arrival
    // (Back key, cancel, error redirect, post-logout landing) must
    // require an explicit click instead of auto-redirecting again (the
    // loop guard). useSyncExternalStore keeps the server snapshot
    // (always "not attempted") hydration-safe; cross-tab "storage"
    // events make the snapshot reactive where it can be.
    const attempted = React.useSyncExternalStore(
        subscribeToStorageEvents,
        () => hasOidcAttempt(mode),
        () => false,
    );

    /**
     * Start the OIDC action WITHOUT touching local state — the auto
     * path's connecting card is simply the default render while the
     * redirect is in flight, and the only state it may set (an error)
     * happens after awaits, never synchronously. Writes the attempt
     * marker BEFORE the browser leaves so any return arrival (Back,
     * cancel, error redirect) sees "attempted" and requires an
     * explicit click instead of auto-redirecting again.
     */
    const startAction = React.useCallback(async () => {
        markOidcAttempt(mode);

        try {
            await initiateOidcAction(mode, targetPath);
            // The document usually navigates away before this resolves;
            // if it does not, the pending/attempted rendering stays
            // honest until Keycloak's own navigation wins.
        } catch (cause) {
            console.error(`${mode} failed:`, cause);
            setError(oidcActionErrorMessage(cause));
        }
    }, [mode, targetPath]);

    /** Manual start (the explicit button): adds the pending UI —
     * disable + "Connecting…" — around the same shared start. */
    const handleManualAction = React.useCallback(() => {
        setIsPending(true);
        setError(null);

        void startAction().finally(() => {
            setIsPending(false);
        });
    }, [startAction]);

    // Authenticated arrivals: replace to the target immediately (the
    // entry screens are not for signed-in users) and clear the attempt
    // marker so a later logout → login cycle auto-fires again.
    React.useEffect(() => {
        if (!isLoading && isAuthenticated) {
            clearOidcAttempt(mode);
            router.replace(targetPath);
        }
    }, [isLoading, isAuthenticated, mode, router, targetPath]);

    // The single auto-initiation: only for an unauthenticated arrival
    // whose tab has not attempted this action yet (and with no error on
    // screen — a failed attempt must NOT silently re-fire). An effect —
    // never a render-time side effect. The ref guard makes a React
    // StrictMode double-invoke fire the redirect exactly once in dev.
    const autoStartedRef = React.useRef(false);

    React.useEffect(() => {
        if (
            autoStartedRef.current ||
            isLoading ||
            isAuthenticated ||
            attempted ||
            error ||
            isPending
        ) {
            return;
        }

        autoStartedRef.current = true;
        void startAction();
    }, [
        isLoading,
        isAuthenticated,
        attempted,
        error,
        isPending,
        startAction,
    ]);

    if (!isLoading && isAuthenticated) {
        // The replace above is in flight; render nothing to avoid a
        // content flash.
        return null;
    }

    // Settled, unauthenticated, and the auto-redirect already used in
    // this tab (or a start attempt just failed): the explicit form —
    // the previous flow's manual state, strings unchanged.
    if ((attempted || error) && !isPending) {
        return (
            <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 text-card-foreground shadow-xs">
                <div className="mb-6 space-y-1.5">
                    <h2 className="text-2xl font-bold text-card-foreground">
                        {copy.heading}
                    </h2>
                    <p className="text-sm text-muted-foreground">
                        {copy.sub}
                    </p>
                </div>

                {error && (
                    <p
                        role="alert"
                        className="mb-4 text-sm text-destructive"
                    >
                        {error}
                    </p>
                )}

                <Button
                    type="button"
                    onClick={handleManualAction}
                    disabled={isPending}
                    className="w-full font-medium"
                >
                    {isPending ? copy.busy : copy.action}
                </Button>
            </div>
        );
    }

    // Otherwise (auth initializing, or the one auto-redirect in
    // flight): a calm redirect notice — no dead-end, no flash of a
    // form that is about to navigate away.
    return (
        <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 text-card-foreground shadow-xs">
            {error && (
                <p
                    role="alert"
                    className="mb-4 text-sm text-destructive"
                >
                    {error}
                </p>
            )}
            <LoadingBlock message={isPending ? copy.busy : copy.redirecting} />
        </div>
    );
}
