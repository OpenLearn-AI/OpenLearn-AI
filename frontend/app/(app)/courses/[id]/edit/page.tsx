"use client";

import Link from "next/link";
import { notFound, useParams } from "next/navigation";

import { CourseForm } from "@/components/courses/CourseForm";
import { useCourse } from "@/features/courses/api/useCourse";
import { courseLinkClass } from "@/components/courses/OpenHubLink";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { ErrorState } from "@/components/state/ErrorState";
import { ApiError } from "@/lib/api";

/**
 * Edit Course (Batch 4.3 presentation pass on the Batch 2 pattern).
 *
 * The pinned heading ("Edit Course"), the shared `CourseForm`, the
 * F3 remount key (navigating between two edit URLs re-seeds the
 * fields from the selected course), and the loading/error/404
 * semantics are unchanged; the page frame joins the courses family.
 */
export default function EditCoursePage() {
    const params = useParams<{ id: string }>();
    const courseId = params.id;

    const {
        data: course,
        isLoading,
        isError,
        error,
    } = useCourse(courseId);

    if (isLoading) {
        return (
            <main className="mx-auto w-full max-w-2xl min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
                <LoadingBlock message="Loading course..." />
            </main>
        );
    }

    // Only an actual 404 from the API means "course not found".
    if (
        isError &&
        error instanceof ApiError &&
        error.status === 404
    ) {
        notFound();
    }

    if (isError || !course) {
        return (
            <main className="mx-auto w-full max-w-2xl min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
                <ErrorState
                    message={
                        error instanceof Error
                            ? error.message
                            : "Failed to load course."
                    }
                />
            </main>
        );
    }

    return (
        <main className="mx-auto w-full max-w-2xl min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
            <p>
                <Link
                    href={`/courses/${courseId}`}
                    className={courseLinkClass}
                >
                    Back to course
                </Link>
            </p>

            <div className="mt-4">
                <h1 className="text-3xl font-semibold tracking-tight text-foreground">
                    Edit Course
                </h1>

                <p className="mt-2 text-sm text-muted-foreground">
                    Update the course&rsquo;s title or description.
                </p>
            </div>

            <hr className="mt-6" />

            <div className="mt-8">
                {/* F3: key the form on the course identity so navigating
                    between two edit URLs remounts it and re-seeds the
                    fields from the selected course — otherwise the cached
                    course B data can render without a loading pass and the
                    form keeps course A's state (wrong-record write). */}
                <CourseForm
                    key={course.id}
                    mode="edit"
                    courseId={course.id}
                    initialValues={{
                        title: course.title,
                        description: course.description,
                    }}
                />
            </div>
        </main>
    );
}
