"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
    courseSchema,
    type CourseFormValues,
} from "@/features/courses/schemas";
import {
    CourseApiError,
    useCreateCourse,
    useUpdateCourse,
} from "@/features/courses/api/useCourseMutations";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface CourseFormProps {
    mode: "create" | "edit";
    courseId?: string;
    initialValues?: CourseFormValues;
}

export function CourseForm({
    mode,
    courseId,
    initialValues,
}: CourseFormProps) {
    const router = useRouter();

    const createCourse = useCreateCourse();
    const updateCourse = useUpdateCourse();

    const [title, setTitle] = useState(initialValues?.title ?? "");
    const [description, setDescription] = useState(
        initialValues?.description ?? "",
    );

    const [errors, setErrors] = useState<{
        title?: string;
        description?: string;
    }>({});

    const isSubmitting =
        createCourse.isPending || updateCourse.isPending;

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const values: CourseFormValues = {
            title,
            description: description || null,
        };

        const result = courseSchema.safeParse(values);

        if (!result.success) {
            const fieldErrors: {
                title?: string;
                description?: string;
            } = {};

            for (const issue of result.error.issues) {
                const field = issue.path[0];

                if (field === "title" || field === "description") {
                    fieldErrors[field] = issue.message;
                }
            }

            setErrors(fieldErrors);
            return;
        }

        setErrors({});

        if (mode === "create") {
            createCourse.mutate(result.data, {
                onSuccess: () => {
                    router.push("/courses");
                },
            });

            return;
        }

        if (!courseId) {
            return;
        }

        updateCourse.mutate(
            {
                courseId,
                payload: result.data,
            },
            {
                onSuccess: () => {
                    router.push("/courses");
                },
            },
        );
    };

    const mutationError =
        createCourse.error ?? updateCourse.error;

    const mutationErrorMessage =
        mutationError instanceof CourseApiError
            ? mutationError.status === 401
                ? "Your session has expired. Please log in again."
                : mutationError.status === 403
                  ? "You do not have permission to perform this action."
                  : mutationError.status === 404
                    ? "The course was not found."
                    : mutationError.message
            : mutationError instanceof Error
              ? mutationError.message
              : null;

    return (
        <form
            onSubmit={handleSubmit}
            className="space-y-6"
            noValidate
        >
            <div className="space-y-2">
                <Label htmlFor="course-title">Title</Label>

                <Input
                    id="course-title"
                    value={title}
                    onChange={(event) =>
                        setTitle(event.target.value)
                    }
                    placeholder="Course title"
                    disabled={isSubmitting}
                    aria-invalid={Boolean(errors.title)}
                />

                {errors.title && (
                    <p className="text-sm text-destructive">
                        {errors.title}
                    </p>
                )}
            </div>

            <div className="space-y-2">
                <Label htmlFor="course-description">
                    Description
                </Label>

                <textarea
                    id="course-description"
                    value={description}
                    onChange={(event) =>
                        setDescription(event.target.value)
                    }
                    placeholder="Course description"
                    disabled={isSubmitting}
                    aria-invalid={Boolean(errors.description)}
                    className="min-h-32 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground shadow-xs outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                />

                {errors.description && (
                    <p className="text-sm text-destructive">
                        {errors.description}
                    </p>
                )}
            </div>

            {mutationErrorMessage && (
                <p
                    role="alert"
                    className="text-sm text-destructive"
                >
                    {mutationErrorMessage}
                </p>
            )}

            <Button
                type="submit"
                disabled={isSubmitting}
            >
                {isSubmitting
                    ? "Saving..."
                    : mode === "create"
                      ? "Create Course"
                      : "Save Changes"}
            </Button>
        </form>
    );
}