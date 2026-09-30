"use client";

import { notFound, useParams } from "next/navigation";

import { CourseForm } from "@/components/courses/CourseForm";
import { useCourse } from "@/features/courses/api/useCourse";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { ErrorState } from "@/components/state/ErrorState";
import { ApiError } from "@/lib/api";

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
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-2xl">
                    <LoadingBlock message="Loading course..." />
                </div>
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
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-2xl">
                    <ErrorState
                        message={
                            error instanceof Error
                                ? error.message
                                : "Failed to load course."
                        }
                    />
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-background px-4 py-8">
            <div className="mx-auto max-w-2xl space-y-6">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-foreground">
                        Edit Course
                    </h1>

                    <p className="mt-2 text-muted-foreground">
                        Update your OpenLearn AI course.
                    </p>
                </div>

                <CourseForm
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
