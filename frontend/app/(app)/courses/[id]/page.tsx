"use client";

import Link from "next/link";
import { notFound, useParams } from "next/navigation";

import { useCourse } from "@/features/courses/api/useCourse";
import { useMe } from "@/features/auth/api/useMe";
import { formatCourseCreatedDate } from "@/components/CourseCard";
import { courseLinkClass } from "@/components/courses/OpenHubLink";
import { CourseMaterials } from "@/components/courses/CourseMaterials";
import { DeleteCourseButton } from "@/components/courses/DeleteCourseButton";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { ErrorState } from "@/components/state/ErrorState";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api";

/**
 * Course detail — the CONTENT HUB (Batch 4.3, roadmap Section 9).
 *
 * The page composes the hub's two built regions — the course header
 * with its actions, and the materials region — in the same Swiss
 * Editorial Grid grammar as the dashboard and the courses list:
 * a masthead with the display-scale title and the course's real
 * metadata, one hairline, then the 12-column asymmetric band
 * (Description 4 / Materials 8 with a vertical hairline at ≥48rem
 * of content width; stacked with horizontal rules below).
 *
 * Future hub slots (extracted text, retrieval search, chunks,
 * citations, the AI assistant, enrollment) are DOCUMENTED
 * reservations only — recorded in the Batch 4.3 batch note and
 * ADR-0010's Section 9 table — and are deliberately NOT rendered:
 * no placeholder panels, no coming-soon copy, no disabled buttons,
 * no fake features (roadmap: "reservation is documentation, never
 * rendered UI").
 *
 * Role-aware presentation (roadmap Section 4/8): the management
 * actions (Edit, Delete) and the upload affordance inside the
 * materials region render only for the authenticated user who BOTH
 * carries the instructor role AND owns this course — the same
 * population the backend's own authorization (instructor role +
 * course ownership) accepts. Presentation only: the backend
 * remains the enforcement; hiding is never the boundary. Students
 * cannot reach this page at all today (the owner-scoped course
 * read), so nothing student-specific is invented.
 *
 * Behavior preserved (the courses-crud E2E contract): the 404 →
 * notFound() semantics (only an actual API 404), the loading and
 * error states, the pinned accessible names ("Edit Course",
 * "Delete Course", the alertdialog), the "Description" h2 section
 * that renders the real description, and the post-delete redirect
 * to /courses.
 *
 * The `<main>` is the page's inline-size container (`@container`),
 * so the band's reflow and the title's clamp follow the CONTENT
 * column, not the viewport.
 */
export default function CourseDetailPage() {
    const params = useParams<{ id: string }>();
    const courseId = params.id;

    const {
        data: course,
        isLoading,
        isError,
        error,
    } = useCourse(courseId);
    const { data: me } = useMe();

    if (isLoading) {
        return (
            <main className="min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
                <div className="mx-auto w-full max-w-5xl">
                    <LoadingBlock message="Loading course..." />
                </div>
            </main>
        );
    }

    // Only an actual 404 from the API means "course not found".
    // Network errors, 500s, auth errors etc. are shown as error states.
    if (
        isError &&
        error instanceof ApiError &&
        error.status === 404
    ) {
        notFound();
    }

    if (isError || !course) {
        return (
            <main className="min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
                <div className="mx-auto w-full max-w-5xl space-y-4">
                    <ErrorState
                        message={
                            error instanceof Error
                                ? error.message
                                : "Failed to load course."
                        }
                    />
                    <div className="text-center">
                        <Button
                            variant="outline"
                            size="sm"
                            render={<Link href="/courses" />}
                        >
                            Back to Courses
                        </Button>
                    </div>
                </div>
            </main>
        );
    }

    // The management population: the authenticated instructor who
    // owns this course — derived from the two real sources (the
    // course's owner_id and /auth/me), never assumed.
    const canManageCourse = Boolean(
        me &&
            me.id === course.owner_id &&
            me.roles.includes("instructor"),
    );

    return (
        <main className="@container mx-auto w-full max-w-7xl min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
            {/* Back to the index — the quiet in-content link grammar. */}
            <p>
                <Link
                    href="/courses"
                    className={courseLinkClass}
                >
                    All courses
                </Link>
            </p>

            {/* Masthead — the hub's identity row: the display-scale
                title and the course's real metadata, with the
                management actions at the inline end (role-aware). */}
            <header className="mt-4 grid gap-4 @3xl:grid-cols-[minmax(0,8fr)_minmax(0,4fr)] @3xl:items-end @3xl:gap-8">
                <div className="min-w-0">
                    <h1
                        dir="auto"
                        className="text-[clamp(1.875rem,4cqi,2.5rem)] font-semibold leading-[1.12] tracking-tight text-foreground break-words"
                    >
                        {course.title}
                    </h1>
                    <p className="mt-3 flex flex-wrap items-baseline gap-x-4 gap-y-1 font-mono text-[0.8125rem] text-muted-foreground">
                        <time dateTime={course.created_at}>
                            {formatCourseCreatedDate(course.created_at)}
                        </time>
                        <span aria-hidden="true">·</span>
                        <span>
                            {canManageCourse
                                ? "You own this course"
                                : "Course hub"}
                        </span>
                    </p>
                </div>

                {canManageCourse ? (
                    <div className="flex flex-wrap items-center gap-3 @3xl:justify-end">
                        <Button
                            variant="outline"
                            render={
                                <Link href={`/courses/${course.id}/edit`} />
                            }
                        >
                            Edit Course
                        </Button>
                        <DeleteCourseButton
                            courseId={course.id}
                            courseTitle={course.title}
                            redirectTo="/courses"
                        />
                    </div>
                ) : null}
            </header>

            <hr className="mt-6" />

            {/* The hub's two built regions — Description (4) beside
                Materials (8) with a vertical hairline on wide content
                columns; stacked with horizontal rules below 48rem. */}
            <div className="mt-10 grid gap-8 @3xl:grid-cols-12">
                <section
                    aria-labelledby="course-description-heading"
                    className="min-w-0 @3xl:col-span-4"
                >
                    <h2
                        id="course-description-heading"
                        className="mb-5 text-[0.8125rem] font-medium text-muted-foreground"
                    >
                        Description
                    </h2>
                    {course.description ? (
                        <p
                            dir="auto"
                            className="max-w-[50ch] text-[0.9375rem] leading-[1.7] text-foreground break-words"
                        >
                            {course.description}
                        </p>
                    ) : (
                        <p className="text-[0.9375rem] text-muted-foreground">
                            No description.
                        </p>
                    )}
                </section>

                <section
                    aria-labelledby="course-materials-heading"
                    className="min-w-0 border-t border-border pt-8 @3xl:col-span-8 @3xl:border-t-0 @3xl:border-s @3xl:border-border @3xl:ps-8 @3xl:pt-0"
                >
                    <h2
                        id="course-materials-heading"
                        className="mb-5 text-[0.8125rem] font-medium text-muted-foreground"
                    >
                        Materials
                    </h2>
                    <CourseMaterials
                        courseId={course.id}
                        canUpload={canManageCourse}
                    />
                </section>
            </div>
        </main>
    );
}
