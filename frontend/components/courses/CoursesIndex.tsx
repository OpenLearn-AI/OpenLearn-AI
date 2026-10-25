"use client";

import { useState } from "react";

import { CourseCard } from "@/components/CourseCard";
import { EmptyState } from "@/components/state/EmptyState";
import { ErrorState } from "@/components/state/ErrorState";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { Input } from "@/components/ui/input";
import { useCourses } from "@/features/courses/api/useCourses";

/**
 * The courses list pattern (Batch 4.2, Swiss Editorial Grid) — the
 * roadmap's "new list-pattern component" with the inline filter state
 * extracted out of the page.
 *
 * Owns exactly what the roadmap assigns it:
 * - the search state and the FROZEN filter semantics (title OR
 *   description, case-insensitive substring — byte-for-byte the
 *   previous page logic, unchanged);
 * - the index bar: a mono live count (`aria-live="polite"`, honest in
 *   every state — "N courses" at rest, "N of M courses" while
 *   filtering, "Loading…" / "—" / "No courses yet" otherwise) and the
 *   bottom-hairline search field with a REAL accessible name (a
 *   visually-hidden label — fixing the previous placeholder-only
 *   defect);
 * - the entry field: a ruled 3/2/1-column grid (3 columns from 72rem
 *   of CONTENT width, 2 from 44rem, 1 below — container queries, so
 *   the density follows the content column, not the viewport);
 * - the four list states in the real kit grammar (LoadingBlock
 *   `role=status`, ErrorState `role=alert` + retry, EmptyState with
 *   the link-only CTA on a truly empty list, and the no-results
 *   message while filtering), flattened page-level via the kit's
 *   `className` so every other kit consumer is untouched.
 *
 * The page around it (title, subtitle, the "+ Create New Course"
 * primary action) lives in `app/(app)/courses/page.tsx`.
 */

/** The flat, hairline presentation applied to the state kit at this
 * page's level (D13): the real kit components and their semantics,
 * without the default card chrome. */
const FLAT_STATE_CLASS =
    "mt-10 flex-col rounded-none border-x-0 border-b-0 bg-transparent px-0 py-12 shadow-none";

export function CoursesIndex() {
    const [searchQuery, setSearchQuery] = useState("");

    const {
        data: courses,
        isLoading,
        isError,
        error,
        refetch,
    } = useCourses();

    // Frozen filter semantics (roadmap must-not-change): title OR
    // description, case-insensitive substring.
    const filteredCourses = (courses ?? []).filter(
        (course) =>
            course.title
                .toLowerCase()
                .includes(searchQuery.toLowerCase()) ||
            (course.description ?? "")
                .toLowerCase()
                .includes(searchQuery.toLowerCase()),
    );

    const total = courses?.length ?? 0;
    const countLine = isLoading
        ? "Loading..."
        : isError
          ? "—"
          : total === 0
            ? "No courses yet"
            : searchQuery !== ""
              ? `${filteredCourses.length} of ${total} ${total === 1 ? "course" : "courses"}`
              : `${total} ${total === 1 ? "course" : "courses"}`;

    return (
        <div>
            {/* Index bar — the honest live count beside the search field. */}
            <div className="mt-8 flex flex-wrap items-end justify-between gap-x-8 gap-y-4 pb-1">
                <p
                    aria-live="polite"
                    className="font-mono text-[0.8125rem] text-muted-foreground"
                >
                    {countLine}
                </p>
                <div className="min-w-[14rem] max-w-[18rem] flex-[0_1_18rem]">
                    <label htmlFor="courses-search" className="sr-only">
                        Search courses
                    </label>
                    <Input
                        id="courses-search"
                        type="search"
                        placeholder="Title or description"
                        autoComplete="off"
                        value={searchQuery}
                        onChange={(event) =>
                            setSearchQuery(event.target.value)
                        }
                        className="h-auto rounded-none border-0 border-b border-input bg-transparent px-0 py-2 text-[0.9375rem] shadow-none focus-visible:ring-0 focus-visible:outline-2 focus-visible:outline-offset-[3px] focus-visible:outline-ring md:text-[0.9375rem] dark:bg-transparent"
                    />
                </div>
            </div>

            {/* The four list states — the primary Create Course action
                stays in the page masthead above, visible in every one
                of them. */}
            {isLoading ? (
                <LoadingBlock
                    message="Loading courses..."
                    className={FLAT_STATE_CLASS}
                />
            ) : isError ? (
                <ErrorState
                    message={
                        error instanceof Error
                            ? error.message
                            : "Failed to load courses."
                    }
                    onRetry={() => void refetch()}
                    className={FLAT_STATE_CLASS}
                />
            ) : filteredCourses.length > 0 ? (
                <ol className="mt-10 grid gap-x-8 gap-y-10 @min-[44rem]:grid-cols-2 @min-[72rem]:grid-cols-3">
                    {filteredCourses.map((course) => (
                        <li key={course.id}>
                            <CourseCard course={course} />
                        </li>
                    ))}
                </ol>
            ) : (
                <EmptyState
                    message={
                        searchQuery
                            ? "No courses found matching your search."
                            : "You don't have any courses yet."
                    }
                    actionHref={searchQuery ? undefined : "/courses/new"}
                    actionLabel={
                        searchQuery ? undefined : "Create your first course"
                    }
                    className={FLAT_STATE_CLASS}
                />
            )}
        </div>
    );
}
