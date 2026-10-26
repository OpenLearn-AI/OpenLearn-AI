import Link from "next/link";

import { cn } from "@/lib/utils";
import {
    courseLinkClass,
    entryTitleLinkClass,
    OpenHubLink,
} from "@/components/courses/OpenHubLink";
import type { Course } from "@/features/courses/schemas";

/**
 * Format a course `created_at` timestamp as an ISO calendar date
 * (`YYYY-MM-DD`) in the viewer's local timezone.
 *
 * Batch 4.2 (Swiss Grid): the courses surfaces present created dates
 * in the design's mono data register as ISO dates — deterministic
 * across runtimes and locales (the previous `toLocaleDateString()`
 * rendered differently per environment), direction-neutral, and
 * trivially scannable in the ruled index. The `<time>` element still
 * carries the full original timestamp for machine consumption.
 */
export function formatCourseCreatedDate(isoDateTime: string): string {
    const date = new Date(isoDateTime);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

/**
 * Shared course presentation (Batch 4.2, Swiss Editorial Grid) — the
 * course entry as a RULED INDEX LINE, not a box.
 *
 * Presentational only — no API calls, no business logic, no mutation
 * hooks. Consumed by the courses list (`CoursesIndex`) so the list
 * renders courses in the design's entry grammar.
 *
 * The Batch 4.2 redesign deliberately retires the previous card
 * chrome: no background surface, no border box, no radius, no
 * shadow, and no "Course" pill (the whole page is a courses index —
 * the pill carried no information). The entry's single hairline sits
 * on TOP and darkens on hover / keyboard focus-within, which keeps
 * the affordance discoverable without any container decoration.
 *
 * Batch 4.2 corrections (A2/A8, 2026-10-25): the entry TITLE is now
 * the primary link to the course hub — the largest, most natural
 * target, in the quiet title-link grammar (resting: plain text; on
 * hover: a brass underline at 3px offset; keyboard: the page-wide
 * brass outline). The "Edit" and "Open Hub →" actions stay beside it,
 * so the entry offers one primary destination and the established
 * secondary actions without adding a card or a background — the
 * separation the owner asked for comes from the hairline, the
 * slightly deeper entry padding, and the typographic hierarchy.
 * Long/unbroken titles wrap (`break-words`) instead of stretching
 * or clipping under zoom.
 *
 * Data honesty: every value renders from the real course contract
 * (`title`, `description?`, `created_at`). A null description
 * renders NOTHING (no "No description" filler — the absence is the
 * truth), and the description clamps at three lines so long text
 * cannot create inconsistent entry heights.
 *
 * Bidi: the title and description are user-authored content and are
 * marked `dir="auto"`, so an Arabic title renders correctly inside an
 * LTR page (and vice versa).
 */
export function CourseCard({ course }: { course: Course }) {
    return (
        <article className="border-t border-border pt-5 transition-colors duration-[120ms] hover:border-foreground focus-within:border-ring">
            <p className="font-mono text-[0.8125rem] text-muted-foreground">
                <time dateTime={course.created_at}>
                    {formatCourseCreatedDate(course.created_at)}
                </time>
            </p>
            <h2
                dir="auto"
                className="mt-2 text-xl font-medium leading-[1.3] text-foreground break-words"
            >
                <Link
                    href={`/courses/${course.id}`}
                    className={entryTitleLinkClass}
                >
                    {course.title}
                </Link>
            </h2>
            {course.description ? (
                <p
                    dir="auto"
                    className="mt-2 max-w-[40ch] text-[0.9375rem] leading-[1.6] text-muted-foreground line-clamp-3 break-words"
                >
                    {course.description}
                </p>
            ) : null}
            <p className="mt-4 flex flex-wrap items-baseline gap-x-4 gap-y-1 text-sm">
                <Link
                    href={`/courses/${course.id}/edit`}
                    className={cn(courseLinkClass, "text-muted-foreground")}
                >
                    Edit
                </Link>
                <span aria-hidden="true" className="text-muted-foreground">
                    ·
                </span>
                <OpenHubLink courseId={course.id} />
            </p>
        </article>
    );
}
