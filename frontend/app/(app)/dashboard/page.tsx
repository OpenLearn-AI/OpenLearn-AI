"use client";

import Link from "next/link";

import { formatCourseCreatedDate } from "@/components/CourseCard";
import {
    entryTitleLinkClass,
    OpenHubLink,
} from "@/components/courses/OpenHubLink";
import { EmptyState } from "@/components/state/EmptyState";
import { ErrorState } from "@/components/state/ErrorState";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { useMe } from "@/features/auth/api/useMe";
import { useUserName } from "@/features/auth/useUserName";
import { composeWelcomeGreeting } from "@/features/auth/user-identity";
import { useCourses } from "@/features/courses/api/useCourses";
import { useProfile } from "@/features/profile/api/useProfile";
import {
    PROFILE_FIELD_COUNT,
    countMissingProfileFields,
} from "@/features/profile/completeness";

/**
 * Dashboard (Batch 4.2, Swiss Editorial Grid).
 *
 * Composition (the approved refined direction):
 * - A demoted "running head" — the greeting at quiet scale (the
 *   display weight belongs to the facts, not the greeting; the
 *   previous gradient hero banner, its "Dashboard" pill, and its
 *   subtitle are retired).
 * - A 12-column asymmetric facts band (3 / 3 / 6 with vertical
 *   hairlines): the course count as a large tabular numeral that IS
 *   the link to /courses (the duplicate "View all →" button is
 *   retired), the profile-completeness measure with a six-tick datum
 *   row, and the four most-recently-created courses as a ruled index
 *   list. Only the owner-locked real metrics render — nothing else.
 * - A quiet account colophon at the page foot.
 *
 * Batch 4.2 corrections applied on top (2026-10-25):
 * - Correction A3: the greeting reads "Welcome back, <Name>!" — the
 *   exclamation mark follows the name (`composeWelcomeGreeting`, a
 *   pure unit-tested composition; the name is the session's real
 *   `given_name`, display-cased, never an identifier fallback).
 *   Without a first name the plain "Welcome back!" renders alone —
 *   no dangling comma, no empty-name gap.
 * - Correction A4: the redundant "Courses" region kicker is REMOVED
 *   (the count numeral + unit already say what the region is, and
 *   the shell has a Courses destination), and the spatially
 *   inaccurate "The courses you own. Browse them below." is retired
 *   — on desktop this region sits BESIDE the Profile and Recently
 *   created regions, not above them. The zero-course helper copy
 *   (non-spatial, actionable) is kept.
 * - Correction A2: interactive elements carry restrained, visible
 *   affordances — every fact/link gets its hover/focus treatment,
 *   and the recent-course entry's TITLE is now the link to its hub
 *   (the entry hairline inks on hover/focus-within as before). The
 *   entries remain ruled index lines — separation comes from the
 *   hairlines, spacing, and typographic hierarchy, never from
 *   wrapping every course in a card or background.
 * - Correction A5: the facts band is zoom/viewport-resilient —
 *   `min-w-0` on every grid region (grid blowout protection),
 *   `break-words` + a reading-measure cap on entry titles (long or
 *   unbroken titles wrap instead of stretching or clipping), and
 *   the single 48rem CONTENT-width reflow drives stacking.
 *
 * Heading hierarchy: h1 (greeting) → h2 (the Profile and Recently
 * created region kickers) → h3 (recent course titles). The courses
 * region intentionally carries no heading (correction A4): the
 * numeral link's own name ("4 courses") states what it is.
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
 * The six user-facing content fields and the carried-field count now
 * live in `features/profile/completeness.ts` (shared with the
 * profile page since Batch 4.4 — one definition of the measure).
 */

/** The flat, hairline presentation for the state kit inside the
 * facts band's regions (D13 — real kit grammar, page-level flat
 * look; the kit's other consumers are untouched). */
const FLAT_STATE_IN_REGION =
    "mt-0 flex-col items-start rounded-none border-0 bg-transparent px-0 py-6 text-start shadow-none";

/** The quiet page-link grammar reused from the courses surfaces for
 * the facts band's inline links (underline on hover, brass focus). */
const factLinkClass =
    "text-inherit no-underline underline-offset-[3px] hover:underline hover:decoration-ring focus-visible:outline-2 focus-visible:outline-offset-[3px] focus-visible:outline-ring transition-colors";

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
    const greeting = composeWelcomeGreeting(firstName);

    return (
        <main className="@container mx-auto w-full max-w-7xl min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
            {/* Running head — the personalized greeting (A3):
                "Welcome back, <Name>!" with the exclamation mark after
                the name. `dir="auto"` isolates the name so an Arabic
                first name renders correctly in either layout direction,
                and the composition degrades to the plain "Welcome
                back!" when no first name exists — never a dangling
                comma or empty-name gap. */}
            <h1 className="text-xl font-medium leading-[1.3] text-foreground">
                {greeting.name ? (
                    <>
                        Welcome back,{" "}
                        <span dir="auto">{greeting.name}</span>!
                    </>
                ) : (
                    greeting.text
                )}
            </h1>

            <hr className="mt-6" />

            {/* Facts band — 3 / 3 / 6 regions across a 12-column grid
                with vertical hairlines; one stacked column with
                horizontal rules below 48rem of content width. Every
                region is `min-w-0` so long content can shrink and
                wrap (A5) instead of blowing out the grid track. */}
            <section
                aria-label="Your account at a glance"
                className="mt-10 grid gap-8 @3xl:grid-cols-12"
            >
                {/* Courses — the count as a large tabular numeral; the
                    numeral itself is the link to the courses list.
                    No region kicker (A4): the numeral link's own name
                    ("4 courses") states what the region is, and the
                    shell's navigation already carries a Courses
                    destination. */}
                <div className="min-w-0 @3xl:col-span-3">
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
                            {courseCount === 0 ? (
                                <p className="mt-3.5 max-w-[34ch] text-[0.8125rem] text-muted-foreground">
                                    Create your first course to get
                                    started.
                                </p>
                            ) : null}
                        </>
                    )}
                </div>

                {/* Profile — the completeness measure (the locked
                    "N of 6 fields left" wording) with a six-tick datum
                    row; the measure itself is the link to /profile. */}
                <div className="min-w-0 border-t border-border pt-8 @3xl:col-span-3 @3xl:border-t-0 @3xl:border-s @3xl:border-border @3xl:ps-8 @3xl:pt-0">
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
                    index list; each entry's TITLE is the link to its
                    hub (A2 — the title is the primary, largest
                    target), with the "Open Hub →" action as the
                    directional cue. */}
                <div className="min-w-0 border-t border-border pt-8 @3xl:col-span-6 @3xl:border-t-0 @3xl:border-s @3xl:border-border @3xl:ps-8 @3xl:pt-0">
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
                                    className="group border-t border-border py-4 transition-colors duration-150 first:border-t-0 hover:border-foreground focus-within:border-ring"
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
                                        className="mt-1.5 max-w-[60ch] text-base font-medium leading-[1.4] text-foreground break-words"
                                    >
                                        <Link
                                            href={`/courses/${course.id}`}
                                            className={entryTitleLinkClass}
                                        >
                                            {course.title}
                                        </Link>
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
