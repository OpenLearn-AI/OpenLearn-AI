"use client";

import { CourseForm } from "@/components/courses/CourseForm";
import { useCourse } from "@/features/courses/api/useCourse";
import { useParams } from "next/navigation";

export default function EditCoursePage() {
    const params = useParams<{ id: string }>();
    const courseId = params.id;

    const { data: course, isLoading, isError, error } = useCourse(courseId);

    if (isLoading) {
        return (
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-2xl">
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
                <div className="mx-auto max-w-2xl">
                    <p className="text-sm text-destructive">
                        {error instanceof Error
                            ? error.message
                            : "Failed to load course."}
                    </p>
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