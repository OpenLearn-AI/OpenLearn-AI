"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { useCourse } from "@/features/courses/api/useCourse";

export default function CourseDetailPage() {
    const params = useParams<{ id: string }>();
    const courseId = params.id;

    const { data: course, isLoading, isError, error } = useCourse(courseId);

    if (isLoading) {
        return (
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-3xl">
                    <p className="text-sm text-muted-foreground">
                        Loading course...
                    </p>
                </div>
            </main>
        );
    }

    if (isError || !course) {
        return (
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-3xl space-y-4">
                    <p className="text-sm text-destructive">
                        {error instanceof Error
                            ? error.message
                            : "Failed to load course."}
                    </p>

                    <Link
                        href="/courses"
                        className="inline-flex h-8 items-center justify-center rounded-lg border border-border bg-background px-2.5 text-sm font-medium hover:bg-muted"
                    >
                        Back to Courses
                    </Link>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-background px-4 py-8">
            <div className="mx-auto max-w-3xl space-y-6">
                <div className="flex items-center justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">
                            {course.title}
                        </h1>

                        <p className="mt-2 text-sm text-muted-foreground">
                            Course details
                        </p>
                    </div>

                    <Link
                        href={`/courses/${course.id}/edit`}
                        className="inline-flex h-8 items-center justify-center rounded-lg bg-primary px-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/80"
                    >
                        Edit Course
                    </Link>
                </div>

                <section className="rounded-xl border bg-card p-6 shadow-sm">
                    <div className="space-y-6">
                        <div>
                            <h2 className="text-sm font-medium">
                                Description
                            </h2>

                            <p className="mt-2 text-sm text-muted-foreground">
                                {course.description || "No description"}
                            </p>
                        </div>

                        <div>
                            <h2 className="text-sm font-medium">Created</h2>

                            <p className="mt-2 text-sm text-muted-foreground">
                                {new Date(
                                    course.created_at,
                                ).toLocaleDateString()}
                            </p>
                        </div>
                    </div>
                </section>

                <Link
                    href="/courses"
                    className="inline-flex h-8 items-center justify-center rounded-lg border border-border bg-background px-2.5 text-sm font-medium hover:bg-muted"
                >
                    Back to Courses
                </Link>
            </div>
        </main>
    );
}