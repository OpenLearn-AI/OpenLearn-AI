"use client";

import Link from "next/link";

import { formatCourseCreatedDate } from "@/components/CourseCard";
import { OpenHubLink } from "@/components/courses/OpenHubLink";
import { EmptyState } from "@/components/state/EmptyState";
import { ErrorState } from "@/components/state/ErrorState";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { useMe } from "@/features/auth/api/useMe";
import { useUserName } from "@/features/auth/useUserName";
import { useCourses } from "@/features/courses/api/useCourses";
import { useProfile } from "@/features/profile/api/useProfile";
import type { Profile } from "@/features/profile/schemas";

/**
 * Dashboard (Batch 4.2, Swiss Editorial Grid).
 *
 * Composition (the approved refined direction):
 * - A demoted "running head" — the pinned `Welcome Back!` greeting at
 *   quiet scale (the display weight belongs to the facts, not the
 *   greeting; the previous gradient hero banner, its "Dashboard"
 *   pill, and its subtitle are retired).
 * - A 12-column asymmetric facts band (3 / 3 / 6 with vertical
 *   hairlines): the course count as a large tabular numeral that IS
 *   the link to /courses (the duplicate "View all →" button is
 *   retired), the profile-completeness measure with a six-tick datum
 *   row, and the four most-recently-created courses as a ruled index
 *   list. Only the owner-locked real metrics render — nothing else.
 * - A quiet account colophon at the page foot.
 *
 * Owner corrections applied on top of the direction (Batch 4.2):
 * - Correction D: the greeting is personalized with the
 *   authenticated user's FIRST name when one exists — the real
 *   `given_name` claim via `useUserName` (no new request, no mock,
 *   no identifier fallback; SIDE-01's rule stands). The pinned
 *   "Welcome Back!" text remains the heading's leading substring in
 *   every case, and when no first name exists the plain greeting
 *   renders alone — never an awkward empty name.
 * - Correction D: the Email section is REMOVED from the dashboard
 *   (the email already lives on /profile). The colophon carries only
 *   the account's roles — real `/auth/me` data, rendered from the
 *   session, never hard-coded (no "Student" wording on this shared
 *   surface). The former `UserInfo` card is deleted with it.
 * - Correction C: no bottom branding bar — the shell footer was
 *   removed in `AppShell`.
 *
 * Heading hierarchy (D15): h1 (greeting) → h2 (the three region
 * kickers) → h3 (recent course titles) — the previous page skipped
 * h2 entirely.
 *
 * Data freezes (roadmap must-not-change): `useCourses` with its
 * `me.isSuccess` gating, `courseCount = courses?.length ?? 0`, the
 * six-field profile-completeness derivation, and the read-only
 * nature of the page. All copy strings for the metrics are the
 * established ones.
 *
 * The `<main>` is the page's inline-size container (`@container`),
 * driving the facts band's 48rem reflow and the recent list's
 * density by CONTENT width rather than viewport.
 */

/**
 * The six user-facing content fields of `ProfileResponse` (the identity
 * fields `id`/`user_id` are excluded). This is the denominator of the
 * profile-completeness measure — the same derivation recorded in the
 * ledger's Batch 1.4 real-metric inventory: a field counts as carried
 * when it is non-null AND non-empty. Four fields are non-nullable in the
 * contract (guaranteed present once a profile exists); `university` and
 * `learning_style_vark` are the only variable ones.
 */
const PROFILE_FIELD_COUNT = 6;

function countMissingProfileFields(profile: Profile): number {
    const values = [
        profile.education_level,
        profile.major,
        profile.preferred_language,
        profile.university,
        profile.learning_style_vark,
        profile.daily_available_minutes,
    ];
    const carried = values.filter(
        (value) => value !== null && String(value).trim() !== "",
    ).length;
    return PROFILE_FIELD_COUNT - carried;
}

/** The flat, hairline presentation for the state kit inside the
 * facts band's regions (D13 — real kit grammar, page-level flat
 * look; the kit's other consumers are untouched). */
const FLAT_STATE_IN_REGION =
    "mt-0 flex-col items-start rounded-none border-0 bg-transparent px-0 py-6 text-start shadow-none";

/** The quiet page-link grammar reused from the courses surfaces for
 * the facts band's inline links (underline on hover, brass focus). */
const factLinkClass =
    "text-inherit no-underline underline-offset-[3px] hover:underline hover:decoration-ring focus-visible:outline-2 focus-visible:outline-offset-[3px] focus-visible:outline-ring";

export default function DashboardPage() {
    const {
        data: courses,
        isLoading: coursesLoading,
        isError: coursesError,
        error,
        refetch,
    } = useCourses();
    const {
        data: profile,
        isLoading: profileLoading,
        isError: profileError,
    } = useProfile();
    const { data: me } = useMe();
    const { firstName } = useUserName();

    const courseCount = courses?.length ?? 0;
    const missingProfileFields = profile === null || profile === undefined
        ? null
        : countMissingProfileFields(profile);
    const recentCourses = (courses ?? []).slice(0, 4);
    const filledProfileFields =
        missingProfileFields === null
            ? 0
            : PROFILE_FIELD_COUNT - missingProfileFields;

    return (
        <main className="@container mx-auto w-full max-w-7xl min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
            {/* Running head — the pinned greeting, personalized with the
                authenticated user's first name when the session carries
                one. `dir="auto"` isolates the name so an Arabic first
                name renders correctly in either layout direction, and
                the name is a plain trailing word (no added punctuation)
                so the fallback greeting renders clean. */}
            <h1 className="text-xl font-medium leading-[1.3] text-foreground">
                Welcome Back!
                {firstName ? (
                    <>
                        {" "}
                        <span dir="auto">{firstName}</span>
                    </>
                ) : null}
            </h1>

            <hr className="mt-6" />

            {/* Facts band — 3 / 3 / 6 regions across a 12-column grid
                with vertical hairlines; one stacked column with
                horizontal rules below 48rem of content width. */}
            <section
                aria-label="Your account at a glance"
                className="mt-10 grid gap-8 @3xl:grid-cols-12"
            >
                {/* Courses — the count as a large tabular numeral; the
                    numeral itself is the link to the courses list. */}
                <div className="@3xl:col-span-3">
                    <h2 className="mb-5 text-[0.8125rem] font-medium text-muted-foreground">
                        Courses
                    </h2>
                    {coursesLoading ? (
                        <>
                            <p className="text-xl font-medium text-foreground">
                                Loading...
                            </p>
                            <p className="mt-3.5 text-[0.8125rem] text-muted-foreground">
                                Fetching your courses.
                            </p>
                        </>
                    ) : coursesError ? (
                        <>
                            <p className="text-[4.5rem] font-semibold leading-none text-foreground tabular-nums">
                                —
                            </p>
                            <p className="mt-3.5 text-[0.8125rem] text-muted-foreground">
                                Couldn&rsquo;t load your courses.
                            </p>
                        </>
                    ) : (
                        <>
                            <p>
                                <Link
                                    href="/courses"
                                    className={`${factLinkClass} block text-[4.5rem] font-semibold leading-none text-foreground tabular-nums hover:text-ring hover:no-underline`}
                                >
                                    {courseCount}
                                    <span className="mt-2 block text-sm font-medium text-muted-foreground">
                                        {courseCount === 1
                                            ? "course"
                                            : "courses"}
                                    </span>
                                </Link>
                            </p>
                            <p className="mt-3.5 max-w-[34ch] text-[0.8125rem] text-muted-foreground">
                                {courseCount > 0
                                    ? "The courses you own. Browse them below."
                                    : "Create your first course to get started."}
                            </p>
                        </>
                    )}
                </div>

                {/* Profile — the completeness measure (the locked
                    "N of 6 fields left" wording) with a six-tick datum
                    row; the measure itself is the link to /profile. */}
                <div className="border-t border-border pt-8 @3xl:col-span-3 @3xl:border-t-0 @3xl:border-s @3xl:border-border @3xl:ps-8 @3xl:pt-0">
                    <h2 className="mb-5 text-[0.8125rem] font-medium text-muted-foreground">
                        Profile
                    </h2>
                    {profileLoading ? (
                        <>
                            <p className="text-xl font-medium text-foreground">
                                Loading...
                            </p>
                            <p className="mt-3.5 text-[0.8125rem] text-muted-foreground">
                                Fetching your profile.
                            </p>
                        </>
                    ) : profileError ? (
                        <>
                            <p className="text-xl font-medium leading-[1.35] text-foreground">
                                —
                            </p>
                            <p className="mt-3.5 text-[0.8125rem] text-muted-foreground">
                                Couldn&rsquo;t load your profile.
                            </p>
                        </>
                    ) : (
                        <>
                            <p>
                                <Link
                                    href="/profile"
                                    className={`${factLinkClass} text-xl font-medium leading-[1.35] text-foreground`}
                                >
                                    {profile === null
                                        ? "Not set up"
                                        : missingProfileFields === 0
                                          ? "Complete"
                                          : `${missingProfileFields} of ${PROFILE_FIELD_COUNT} fields left`}
                                </Link>
                            </p>
                            {/* Six datum marks — one per profile field,
                                filled for the carried ones. Decorative
                                (aria-hidden): the text above carries the
                                metric. */}
                            <p
                                aria-hidden="true"
                                className="mt-4 flex gap-1.5"
                            >
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
                                {profile === null
                                    ? "Create your profile to personalize your dashboard."
                                    : missingProfileFields === 0
                                      ? "All profile fields are filled in."
                                      : "Fields you can still fill in on your profile."}
                            </p>
                        </>
                    )}
                </div>

                {/* Recently created — the four most recently created
                    courses (the API's created_at DESC order) as a ruled
                    index list; each entry links to its hub. */}
                <div className="border-t border-border pt-8 @3xl:col-span-6 @3xl:border-t-0 @3xl:border-s @3xl:border-border @3xl:ps-8 @3xl:pt-0">
                    <h2 className="mb-5 text-[0.8125rem] font-medium text-muted-foreground">
                        Recently created
                    </h2>
                    {coursesLoading ? (
                        <LoadingBlock
                            message="Loading your courses..."
                            className={FLAT_STATE_IN_REGION}
                        />
                    ) : coursesError ? (
                        <ErrorState
                            message={
                                error instanceof Error
                                    ? error.message
                                    : "Failed to load your courses."
                            }
                            onRetry={() => void refetch()}
                            className={FLAT_STATE_IN_REGION}
                        />
                    ) : courseCount === 0 ? (
                        <EmptyState
                            message="You don't have any courses yet."
                            actionHref="/courses/new"
                            actionLabel="Create your first course"
                            className={FLAT_STATE_IN_REGION}
                        />
                    ) : (
                        <ol>
                            {recentCourses.map((course) => (
                                <li
                                    key={course.id}
                                    className="border-t border-border py-3.5 first:border-t-0 hover:border-foreground focus-within:border-ring"
                                >
                                    <p className="flex items-baseline justify-between gap-4">
                                        <time className="font-mono text-[0.8125rem] text-muted-foreground">
                                            {formatCourseCreatedDate(
                                                course.created_at,
                                            )}
                                        </time>
                                        <OpenHubLink courseId={course.id} />
                                    </p>
                                    <h3
                                        dir="auto"
                                        className="mt-1.5 text-base font-medium leading-[1.4] text-foreground"
                                    >
                                        {course.title}
                                    </h3>
                                </li>
                            ))}
                        </ol>
                    )}
                </div>
            </section>

            {/* Account colophon — roles only. The Email row was removed
                with the dashboard's Email section (owner correction D:
                the email already lives on /profile); the roles are real
                /auth/me data (never hard-coded — no "Student" wording
                on this shared surface) and render once the me query
                resolves, which is also the session-level proof the E2E
                login spec asserts on. */}
            {me ? (
                <div className="mt-16 border-t border-border pt-5">
                    <dl className="flex flex-wrap gap-x-12 gap-y-3">
                        <div className="flex items-baseline gap-2">
                            <dt className="text-[0.8125rem] font-medium text-foreground">
                                {me.roles.length === 1 ? "Role:" : "Roles:"}
                            </dt>
                            <dd className="font-mono text-[0.8125rem] text-muted-foreground">
                                {me.roles.join(", ")}
                            </dd>
                        </div>
                    </dl>
                </div>
            ) : null}
        </main>
    );
}
