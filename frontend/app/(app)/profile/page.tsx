"use client";

import { ProfileForm } from "@/components/profile/ProfileForm";
import { useProfile } from "@/features/profile/api/useProfile";
import { useMe } from "@/features/auth/api/useMe";
import { useUserName } from "@/features/auth/useUserName";
import {
    PROFILE_FIELD_COUNT,
    countMissingProfileFields,
} from "@/features/profile/completeness";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { ErrorState } from "@/components/state/ErrorState";

/**
 * Profile page (Batch 4.4, Swiss Editorial Grid).
 *
 * Joins the redesigned family (dashboard, courses hub, create/edit
 * course) after Batch 4.2 retired the gradient hero banner from the
 * dashboard — this page was the last surface still carrying that
 * pre-redesign language (the `primary→primary/80` gradient banner,
 * its "Account Settings" pill, the rounded-2xl card grid, and the
 * filler "Need Assistance?" panel). The redesign is presentation
 * only: every data flow, contract, and E2E pin is preserved —
 *
 * - `useMe` + `useProfile` with its 404→null semantics (create vs.
 *   edit mode) and the `me.isSuccess` gating;
 * - the F4 fix: the form is keyed on the profile identity
 *   (`key={profile?.id ?? "new"}`) so the null→object transition
 *   remounts and re-seeds the fields;
 * - the pinned heading strings ("Create Your Profile" /
 *   "Personal Information"), the pinned submit labels ("Create
 *   Profile" / "Save Changes" — inside ProfileForm), the six field
 *   labels, and the `role="status"` success surface.
 *
 * Composition (the family's masthead grammar): the display-scale
 * title at the container-query clamp, the person's real identity as
 * a quiet mono metadata line (`dir="auto"` name; `dir="ltr"` email —
 * a Latin address must not bidi-shuffle in RTL), one hairline, then
 * the 12-column asymmetric band: the form region (8) and a
 * completeness aside (4, vertical hairline at ≥48rem of content
 * width; stacked with a horizontal rule below). The aside reuses the
 * dashboard's six-tick datum row on the SAME shared derivation
 * (`features/profile/completeness.ts` — one definition of the
 * measure, so the two surfaces can never drift). No cards, no
 * shadows, no filler panels — separation comes from hairlines,
 * spacing, and typographic hierarchy; the single filled Save button
 * is the page's one primary action.
 *
 * The `<main>` is the page's inline-size container (`@container`),
 * so the band's reflow follows the CONTENT column, not the viewport.
 */
export default function ProfilePage() {
    const { data: me, isLoading: meLoading } = useMe();
    const { name: profileName } = useUserName();
    const {
        data: profile,
        isLoading: profileLoading,
        isError,
        error,
    } = useProfile();

    const isLoading = meLoading || profileLoading;

    if (isLoading) {
        return (
            <main className="min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
                <div className="mx-auto w-full max-w-5xl">
                    <LoadingBlock message="Loading your profile data..." />
                </div>
            </main>
        );
    }

    if (isError) {
        return (
            <main className="min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
                <div className="mx-auto w-full max-w-5xl">
                    <ErrorState
                        message={
                            error instanceof Error
                                ? error.message
                                : "Failed to load your profile. Please check your connection or session."
                        }
                    />
                </div>
            </main>
        );
    }

    const missingProfileFields =
        profile === null || profile === undefined
            ? null
            : countMissingProfileFields(profile);
    const filledProfileFields =
        missingProfileFields === null
            ? 0
            : PROFILE_FIELD_COUNT - missingProfileFields;

    return (
        <main className="@container mx-auto w-full max-w-7xl min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
            {/* Masthead — the display-scale title and the person's real
                identity, in the courses hub's masthead grammar. The
                email is appended only when it differs from the display
                name: `useUserName` falls back to the email when the
                session carries no name claims, and that fallback must
                not render the address twice. */}
            <header>
                <h1 className="text-[clamp(1.875rem,4cqi,2.5rem)] font-semibold leading-[1.12] tracking-tight text-foreground break-words">
                    Profile
                </h1>
                <p className="mt-3 flex flex-wrap items-baseline gap-x-3 gap-y-1 font-mono text-[0.8125rem] text-muted-foreground">
                    <span dir="auto">{profileName}</span>
                    {me?.email && me.email !== profileName ? (
                        <>
                            <span aria-hidden="true">·</span>
                            <span dir="ltr" className="break-all">
                                {me.email}
                            </span>
                        </>
                    ) : null}
                </p>
            </header>

            <hr className="mt-6" />

            {/* Content band — the form region and the completeness
                aside across a 12-column grid with a vertical hairline;
                one stacked column with a horizontal rule below 48rem
                of content width. Every region is `min-w-0` so long
                content shrinks and wraps instead of blowing out the
                grid track (the family's zoom/viewport resilience). */}
            <section
                aria-label="Your profile details"
                className="mt-10 grid gap-8 @3xl:grid-cols-12"
            >
                {/* Form region — the page's primary content. The
                    heading and its supporting line make the
                    create-vs-edit distinction (with the submit label
                    inside the form) before the fields begin. */}
                <div className="min-w-0 @3xl:col-span-8">
                    <h2 className="text-[0.8125rem] font-medium text-muted-foreground">
                        {profile
                            ? "Personal Information"
                            : "Create Your Profile"}
                    </h2>
                    <p className="mt-2 max-w-[52ch] text-[0.8125rem] leading-relaxed text-muted-foreground">
                        {profile
                            ? "Update the six details that make up your learning profile."
                            : "Set up the six details that make up your learning profile — you can change them anytime."}
                    </p>

                    {/* F4: key the form on the profile identity so the
                        null→object transition (profile established)
                        remounts it and re-seeds the fields from the
                        actual profile instead of retaining the
                        create-mode defaults. The id is stable across
                        updates, so ordinary saves do not remount. */}
                    <div className="mt-8">
                        <ProfileForm
                            key={profile?.id ?? "new"}
                            profile={profile ?? null}
                        />
                    </div>
                </div>

                {/* Completeness aside — the same six-tick datum measure
                    the dashboard's Profile region shows, on the shared
                    derivation. Real data only; it re-renders with the
                    invalidated query after every save. */}
                <div className="min-w-0 border-t border-border pt-8 @3xl:col-span-4 @3xl:border-t-0 @3xl:border-s @3xl:border-border @3xl:ps-8 @3xl:pt-0">
                    <h2 className="mb-5 text-[0.8125rem] font-medium text-muted-foreground">
                        Completeness
                    </h2>
                    <p className="text-xl font-medium leading-[1.35] text-foreground">
                        {profile === null || profile === undefined
                            ? "Not set up"
                            : missingProfileFields === 0
                              ? "Complete"
                              : `${missingProfileFields} of ${PROFILE_FIELD_COUNT} fields left`}
                    </p>
                    {/* Six datum marks — one per profile field, filled
                        for the carried ones. Decorative (aria-hidden):
                        the text above carries the metric. */}
                    <p aria-hidden="true" className="mt-4 flex gap-1.5">
                        {Array.from(
                            { length: PROFILE_FIELD_COUNT },
                            (_, index) => (
                                <span
                                    key={index}
                                    className={
                                        index < filledProfileFields
                                            ? "h-1.5 w-3 border border-foreground bg-foreground"
                                            : "h-1.5 w-3 border border-input"
                                    }
                                />
                            ),
                        )}
                    </p>
                    <p className="mt-3.5 max-w-[34ch] text-[0.8125rem] text-muted-foreground">
                        {profile === null || profile === undefined
                            ? "Filling in the form creates your profile."
                            : missingProfileFields === 0
                              ? "All profile fields are filled in."
                              : "Fields you can still fill in and save."}
                    </p>
                </div>
            </section>
        </main>
    );
}
