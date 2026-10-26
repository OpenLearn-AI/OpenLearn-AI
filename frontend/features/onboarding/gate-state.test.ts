import { describe, expect, it } from "vitest";

import {
    ONBOARDING_EXEMPT_PATH,
    resolveOnboardingGateState,
} from "./gate-state";
import type { Profile } from "@/features/profile/schemas";

/**
 * Unit coverage for the Batch 4.1 onboarding gate state machine (Q3).
 *
 * The critical honesty rules pinned here: only a confirmed `null`
 * profile (the 404 mapping in `useProfile`) produces the `onboarding`
 * state; request failures (`meError` / `profileError`) produce `error`
 * and never redirect; `/profile` is exempt; pending queries produce
 * `loading` (no redirect churn).
 */

const profile: Profile = {
    id: "00000000-0000-4000-8000-000000000001",
    user_id: "00000000-0000-4000-8000-000000000002",
    education_level: "Undergraduate",
    major: "Computer Science",
    preferred_language: "en",
    university: null,
    learning_style_vark: null,
    daily_available_minutes: 60,
};

const base = {
    mePending: false,
    meError: false,
    profilePending: false,
    profileError: false,
    profile: profile as Profile | null | undefined,
    pathname: "/dashboard",
};

describe("resolveOnboardingGateState", () => {
    it("state 1/3 — pending me or profile queries resolve to loading", () => {
        expect(
            resolveOnboardingGateState({ ...base, mePending: true }),
        ).toBe("loading");
        expect(
            resolveOnboardingGateState({ ...base, profilePending: true }),
        ).toBe("loading");
        // Defensive: an unset profile result with no pending flag is a
        // loading state, never "missing profile".
        expect(
            resolveOnboardingGateState({ ...base, profile: undefined }),
        ).toBe("loading");
    });

    it("state 2 — me failure is an error, never onboarding", () => {
        expect(resolveOnboardingGateState({ ...base, meError: true })).toBe(
            "error",
        );
    });

    it("state 6 — profile request failure is an error, never onboarding", () => {
        expect(
            resolveOnboardingGateState({
                ...base,
                profile: undefined,
                profileError: true,
            }),
        ).toBe("error");
        // Even a cached null alongside a fresh error stays an error.
        expect(
            resolveOnboardingGateState({
                ...base,
                profile: null,
                profileError: true,
            }),
        ).toBe("error");
    });

    it("state 4 — an existing profile (200) is ready on protected routes", () => {
        expect(resolveOnboardingGateState(base)).toBe("ready");
        expect(
            resolveOnboardingGateState({ ...base, pathname: "/courses" }),
        ).toBe("ready");
        expect(
            resolveOnboardingGateState({
                ...base,
                pathname: "/courses/course-123",
            }),
        ).toBe("ready");
    });

    it("state 5 — a confirmed missing profile (404 → null) requires onboarding", () => {
        expect(
            resolveOnboardingGateState({ ...base, profile: null }),
        ).toBe("onboarding");
        expect(
            resolveOnboardingGateState({
                ...base,
                profile: null,
                pathname: "/courses",
            }),
        ).toBe("onboarding");
    });

    it("the /profile exemption keeps profile management reachable without a profile", () => {
        expect(ONBOARDING_EXEMPT_PATH).toBe("/profile");
        expect(
            resolveOnboardingGateState({
                ...base,
                profile: null,
                pathname: "/profile",
            }),
        ).toBe("ready");
        // Defensive prefix match (the route has no subroutes today).
        expect(
            resolveOnboardingGateState({
                ...base,
                profile: null,
                pathname: "/profile/settings",
            }),
        ).toBe("ready");
        // The exemption is specific — other paths are not covered by it.
        expect(
            resolveOnboardingGateState({
                ...base,
                profile: null,
                pathname: "/profiles",
            }),
        ).toBe("onboarding");
    });

    it("an existing profile is ready even on the exempt route", () => {
        expect(
            resolveOnboardingGateState({
                ...base,
                pathname: "/profile",
            }),
        ).toBe("ready");
    });
});
