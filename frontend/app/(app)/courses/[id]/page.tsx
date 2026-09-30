"use client";

import Link from "next/link";
import { notFound, useParams } from "next/navigation";

import { useCourse } from "@/features/courses/api/useCourse";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { ErrorState } from "@/components/state/ErrorState";
import { DeleteCourseButton } from "@/components/courses/DeleteCourseButton";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api";

export default function CourseDetailPage() {
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
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-3xl">
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
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-3xl space-y-4">
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

    return (
        <main className="min-h-screen bg-background px-4 py-8">
            <div className="mx-auto max-w-3xl space-y-6">
                <div className="flex items-center justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight text-foreground">
                            {course.title}
                        </h1>

                        <p className="mt-2 text-sm text-muted-foreground">
                            Course details
                        </p>
                    </div>

                    <Button
                        variant="outline"
                        size="sm"
                        render={<Link href={`/courses/${course.id}/edit`} />}
                    >
                        Edit Course
                    </Button>
                </div>

                <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
                    <div className="space-y-6">
                        <div>
                            <h2 className="text-sm font-medium text-card-foreground">
                                Description
                            </h2>

                            <p className="mt-2 text-sm text-muted-foreground">
                                {course.description || "No description"}
                            </p>
                        </div>

                        <div>
                            <h2 className="text-sm font-medium text-card-foreground">
                                Created
                            </h2>

                            <p className="mt-2 text-sm text-muted-foreground">
                                {new Date(
                                    course.created_at,
                                ).toLocaleDateString()}
                            </p>
                        </div>
                    </div>
                </section>

                {/* Delete action — confirmation dialog + invalidation */}
                <DeleteCourseButton
                    courseId={course.id}
                    courseTitle={course.title}
                    redirectTo="/courses"
                />

                <Button
                    variant="outline"
                    size="sm"
                    render={<Link href="/courses" />}
                >
                    Back to Courses
                </Button>
            </div>
        </main>
    );
}
