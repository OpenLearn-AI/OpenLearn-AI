"use client";

import { useCourses } from "@/features/courses/api/useCourses";

export function CourseTable() {
    const {
        data: courses,
        isLoading,
        isError,
        error,
    } = useCourses();

    if (isLoading) {
        return (
            <div className="rounded-lg border p-6 text-center">
                Loading courses...
            </div>
        );
    }

    if (isError) {
        return (
            <div className="rounded-lg border p-6 text-center text-destructive">
                {error instanceof Error
                    ? error.message
                    : "Failed to load courses."}
            </div>
        );
    }

    if (!courses || courses.length === 0) {
        return (
            <div className="rounded-lg border p-6 text-center text-muted-foreground">
                No courses found.
            </div>
        );
    }

    return (
        <div className="overflow-x-auto rounded-lg border">
            <table className="w-full text-sm">
                <thead className="border-b bg-muted/50">
                    <tr>
                        <th className="px-4 py-3 text-left font-medium">
                            Title
                        </th>
                        <th className="px-4 py-3 text-left font-medium">
                            Description
                        </th>
                        <th className="px-4 py-3 text-left font-medium">
                            Created At
                        </th>
                    </tr>
                </thead>

                <tbody>
                    {courses.map((course) => (
                        <tr
                            key={course.id}
                            className="border-b last:border-0"
                        >
                            <td className="px-4 py-3 font-medium">
                                {course.title}
                            </td>

                            <td className="px-4 py-3 text-muted-foreground">
                                {course.description || "No description"}
                            </td>

                            <td className="px-4 py-3 text-muted-foreground">
                                {new Date(
                                    course.created_at,
                                ).toLocaleDateString()}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}