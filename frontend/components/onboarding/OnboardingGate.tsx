"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { LoadingBlock } from "@/components/state/LoadingBlock";
import { ErrorState } from "@/components/state/ErrorState";
import { useMe } from "@/features/auth/api/useMe";
import { useProfile } from "@/features/profile/api/useProfile";
import { resolveOnboardingGateState } from "@/features/onboarding/gate-state";

/**
 * First-login onboarding gate (Batch 4.1 — owner decision Q3).
 *
 * Mounted in `app/(app)/layout.tsx` INSIDE `AuthGuard` (which is
 * untouched), wrapping the `AppShell`. `AuthGuard` guarantees the gate
 * only ever evaluates an authenticated context, so the gate's own
 * concern is exactly the profile state:
 *
 *   - `loading`   → a calm loading block while `GET /v1/users/me`
 *     settles. The gate, the dashboard, and the profile page share the
 *     same TanStack Query cache entry (`profileKeys.current()`), so
 *     this is ONE request per cache lifetime, not one per route or per
 *     render.
 *   - `ready`     → the profile exists (200), or the current route is
 *     the `/profile` exemption: children (the real application) render.
 *   - `onboarding`→ the profile is confirmed missing — the queryFn maps
 *     a 404 from `/v1/users/me` to `null` and NOTHING else does. The
 *     effect redirects (replace) to `/onboarding?redirectedFrom=<here>`
 *     so the wizard can return the user to their original destination
 *     after saving. While the redirect is in flight a loading block is
 *     rendered (no protected content flashes).
 *   - `error`     → `/auth/me` or the profile request failed (network,
 *     timeout, 5xx). These are NEVER interpreted as a missing profile:
 *     the user stays on their route with an explicit error and a retry.
 *     A 401 is additionally handled globally by the session-recovery
 *     path (lib/session-recovery.ts), which routes to `/login`.
 *
 * Loop safety (structural): `/onboarding` lives outside the `(app)`
 * group, so the gate never mounts there; `/profile` is exempt; every
 * redirect is a `replace` triggered from an effect — never during
 * render — and only from the `onboarding` state, which requires a
 * settled `null` profile.
 */
export function OnboardingGate({ children }: { children: React.ReactNode }) {
    const me = useMe();
    const profile = useProfile();
    const router = useRouter();
    const pathname = usePathname();

    const state = resolveOnboardingGateState({
        mePending: me.isPending,
        meError: me.isError,
        profilePending: profile.isPending,
        profileError: profile.isError,
        profile: profile.data,
        pathname,
    });

    useEffect(() => {
        if (state !== "onboarding") {
            return;
        }

        const params = new URLSearchParams({ redirectedFrom: pathname });
        router.replace(`/onboarding?${params.toString()}`);
    }, [state, pathname, router]);

    if (state === "ready") {
        return <>{children}</>;
    }

    if (state === "error") {
        const message = me.isError
            ? "We couldn't load your account. Check your connection and try again."
            : "We couldn't load your profile. Check your connection and try again.";

        return (
            <div className="flex min-h-svh items-center justify-center px-4 py-8">
                <ErrorState
                    message={message}
                    className="w-full max-w-md"
                    onRetry={() => {
                        if (me.isError) {
                            me.refetch();
                        } else {
                            profile.refetch();
                        }
                    }}
                />
            </div>
        );
    }

    // `loading` and the pre-redirect `onboarding` state both render a
    // calm, deterministic placeholder — never protected content, and
    // never a redirect issued from render.
    return (
        <div className="flex min-h-svh items-center justify-center px-4 py-8">
            <LoadingBlock
                message={
                    state === "onboarding"
                        ? "Setting up your profile space..."
                        : "Checking your profile..."
                }
                className="w-full max-w-md"
            />
        </div>
    );
}
