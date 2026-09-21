"use client";

import { useParams } from "next/navigation";
import { CourseForm } from "@/components/courses/CourseForm";
import { useCourse } from "@/features/courses/api/useCourse";

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
                <div className="mx-auto max-w-2xl rounded-lg border p-6 text-center">
                    Loading course...
                </div>
            </main>
        );
    }

    if (isError) {
        return (
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-2xl rounded-lg border p-6 text-center text-destructive">
                    {error instanceof Error
                        ? error.message
                        : "Failed to load course."}
                </div>
            </main>
        );
    }

    if (!course) {
        return (
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-2xl rounded-lg border p-6 text-center">
                    Course not found.
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-background px-4 py-8">
            <div className="mx-auto max-w-2xl space-y-6">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        Edit Course
                    </h1>

                    <p className="mt-2 text-muted-foreground">
                        Update the course information.
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