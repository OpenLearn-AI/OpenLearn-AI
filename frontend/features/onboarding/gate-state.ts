import type { Profile } from "@/features/profile/schemas";

/**
 * Onboarding gate state machine (Batch 4.1 — owner decision Q3).
 *
 * A pure function deciding what the authenticated `(app)` gate should
 * do, extracted from the component so every branch is unit-testable in
 * the node environment (the vitest `unit` project has no DOM).
 *
 * The gate must distinguish (Q3 "gate state handling"):
 *   1. Authentication still initializing  → handled by `AuthGuard`
 *      (which wraps the gate); the gate itself then only ever sees an
 *      authenticated context.
 *   2. Unauthenticated user               → `AuthGuard`'s redirect.
 *   3. Profile loading                    → `loading` (render a calm
 *      loading state; no redirect churn).
 *   4. Existing profile (`GET /v1/users/me` → 200) → `ready`.
 *   5. Missing profile (404, surfaced by `useProfile` as `null`) →
 *      `onboarding` — the ONLY signal that may route a user into the
 *      wizard.
 *   6. Profile request failure (network / 5xx / timeout / auth/me
 *      failure) → `error`. Errors are NEVER interpreted as a missing
 *      profile — the user keeps their route and gets a retry.
 *
 * `/profile` is exempt (owner decision Q3): users without a profile can
 * still reach the profile page and create one through the manual form,
 * which also preserves the existing profile E2E contract. `/onboarding`
 * itself sits outside the `(app)` group, so the gate never mounts there
 * and no loop is possible.
 *
 * `profile === undefined` with no pending/error flag is treated as
 * `loading` (a defensive branch: the query has not produced a result
 * yet), never as "missing".
 */

export type OnboardingGateState =
    | "loading"
    | "error"
    | "onboarding"
    | "ready";

/** The gate-exempt route: profile management stays reachable. */
export const ONBOARDING_EXEMPT_PATH = "/profile";

export interface OnboardingGateInput {
    /** `useMe().isPending` — the current-user query has not settled. */
    mePending: boolean;
    /** `useMe().isError` — `/auth/me` failed (session recovery owns 401). */
    meError: boolean;
    /** `useProfile().isPending` — the profile request has not settled. */
    profilePending: boolean;
    /** `useProfile().isError` — the profile request failed (≠ 404). */
    profileError: boolean;
    /** `useProfile().data` — `Profile` (200), `null` (404), `undefined` (unset). */
    profile: Profile | null | undefined;
    /** The current pathname, used for the `/profile` exemption. */
    pathname: string;
}

export function resolveOnboardingGateState(
    input: OnboardingGateInput,
): OnboardingGateState {
    if (input.mePending) {
        return "loading";
    }

    if (input.meError) {
        return "error";
    }

    // Failures are decided BEFORE the pending/undefined branch: a
    // failed query reports `data === undefined` (TanStack's error
    // shape), so the undefined check must never outrank a real error —
    // otherwise a request failure would be held in `loading` forever
    // (or worse, mistaken for "no data yet") instead of surfacing the
    // retry path.
    if (input.profileError) {
        return "error";
    }

    if (input.profilePending || input.profile === undefined) {
        return "loading";
    }

    if (input.profile === null) {
        const exempt =
            input.pathname === ONBOARDING_EXEMPT_PATH ||
            input.pathname.startsWith(`${ONBOARDING_EXEMPT_PATH}/`);
        return exempt ? "ready" : "onboarding";
    }

    return "ready";
}
