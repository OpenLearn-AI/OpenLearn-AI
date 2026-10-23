"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { ProfileSetupWizard } from "@/components/onboarding/ProfileSetupWizard";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { ErrorState } from "@/components/state/ErrorState";
import { useMe } from "@/features/auth/api/useMe";
import { useProfile } from "@/features/profile/api/useProfile";
import { safeRedirectTarget } from "@/features/auth/redirect";

/**
 * First-login onboarding page (Batch 4.1 — owner decision Q3).
 *
 * Loads the profile through the established query layer (`useMe` +
 * `useProfile`, the same cache entry the `(app)` gate shares) and hands
 * the wizard a contract-backed state:
 *   - `null` (the API's 404)  → a fresh first-login wizard;
 *   - a `Profile` (the API's 200) → the same wizard prefilled, so a
 *     user revisiting `/onboarding` edits their profile instead of
 *     accidentally erasing values with a replacement PUT;
 *   - any request FAILURE → an explicit error with retry. Failures are
 *     never interpreted as "no profile" (Q2), so this page never
 *     pretends the profile is missing.
 *
 * Redirect handling: the `redirectedFrom` query value carried by the
 * gate is validated through the existing `safeRedirectTarget` (open
 * redirects rejected; auth routes rejected) and defaults to
 * `/dashboard`. `useSearchParams` requires the Suspense boundary — the
 * same pattern the login entry uses.
 */
function OnboardingContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const me = useMe();
    const profile = useProfile();

    const redirectTo =
        safeRedirectTarget(searchParams.get("redirectedFrom")) ?? "/dashboard";

    if (me.isPending) {
        return (
            <LoadingBlock
                message="Preparing your session..."
                className="w-full max-w-md"
            />
        );
    }

    if (me.isError) {
        return (
            <ErrorState
                message="We couldn't load your account. Check your connection and try again."
                className="w-full max-w-md"
                onRetry={() => me.refetch()}
            />
        );
    }

    if (profile.isPending) {
        return (
            <LoadingBlock
                message="Loading your profile..."
                className="w-full max-w-md"
            />
        );
    }

    if (profile.isError) {
        return (
            <ErrorState
                message="We couldn't load your profile. Check your connection and try again."
                className="w-full max-w-md"
                onRetry={() => profile.refetch()}
            />
        );
    }

    return (
        <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 text-card-foreground shadow-xs">
            <div className="mb-6 space-y-1.5">
                <h1 className="text-2xl font-bold text-card-foreground">
                    Set up your profile
                </h1>
                <p className="text-sm text-muted-foreground">
                    A few basics so OpenLearn AI fits how you study. You can
                    update these anytime from your profile.
                </p>
            </div>

            <ProfileSetupWizard
                profile={profile.data ?? null}
                onSaved={() => router.replace(redirectTo)}
            />
        </div>
    );
}

export default function OnboardingPage() {
    return (
        <Suspense
            fallback={
                <LoadingBlock
                    message="Loading..."
                    className="w-full max-w-md"
                />
            }
        >
            <OnboardingContent />
        </Suspense>
    );
}
