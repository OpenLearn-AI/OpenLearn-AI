"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import {
    courseSchema,
    type CourseFormValues,
} from "@/features/courses/schemas";
import {
    useCreateCourse,
    useUpdateCourse,
} from "@/features/courses/api/useCourseMutations";
import { ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/ui/field";
import { Textarea } from "@/components/ui/textarea";
import { courseLinkClass } from "@/components/courses/OpenHubLink";

interface CourseFormProps {
    mode: "create" | "edit";
    courseId?: string;
    initialValues?: CourseFormValues;
}

/**
 * The shared course create/edit form (Batch 4.3 presentation pass).
 *
 * Everything behavioral is the established contract, unchanged:
 * - the Zod schema and the `safeParse` loop (field errors mapped
 *   from the issues, exactly as before);
 * - the mutation orchestration (`useCreateCourse` / `useUpdateCourse`
 *   with their cache invalidations);
 * - the post-save navigation (`router.push("/courses")` on success —
 *   create AND edit);
 * - the duplicate-submit protection (`isSubmitting` disables the
 *   control) and the form defaults / edit-mode seeding.
 *
 * Batch 4.3 improves the presentation and the error ASSOCIATIONS:
 * - each control's validation error is programmatically associated
 *   (`aria-describedby` → the Field's `role="alert"` paragraph), so
 *   screen readers announce the field error with the control;
 * - the submit row gains a quiet Cancel link back to where the
 *   journey came from (the courses index on create; the course hub
 *   on edit) — a plain link, no behavior of its own;
 * - the API-error paragraph keeps its `role="alert"` and the same
 *   honest status mapping as before.
 */
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
                const field = issue.path[0] as "title" | "description";

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
        mutationError instanceof ApiError
            ? mutationError.status === 401
                ? // W1: the global 401 recovery clears the query cache
                  // and routes to /login (lib/session-recovery.ts); this
                  // line only sets the expectation until the redirect.
                  "Your session has expired. Redirecting to sign in..."
                : mutationError.status === 403
                  ? "You do not have permission to perform this action."
                  : mutationError.status === 404
                    ? "The course was not found."
                    : mutationError.status === 422
                      ? "The submitted values are invalid."
                      : mutationError.message
            : mutationError instanceof Error
                ? mutationError.message
                : null;

    return (
        <form onSubmit={handleSubmit} className="space-y-6" noValidate>
            <Field
                label="Title"
                htmlFor="course-title"
                error={errors.title}
            >
                <Input
                    id="course-title"
                    value={title}
                    onChange={(event) => setTitle(event.target.value)}
                    placeholder="Course title"
                    disabled={isSubmitting}
                    aria-invalid={Boolean(errors.title)}
                    aria-describedby={
                        errors.title ? "course-title-error" : undefined
                    }
                />
            </Field>

            <Field
                label="Description"
                htmlFor="course-description"
                error={errors.description}
                hint="Optional — a sentence or two about what this course covers."
            >
                <Textarea
                    id="course-description"
                    value={description}
                    onChange={(event) =>
                        setDescription(event.target.value)
                    }
                    placeholder="Course description"
                    disabled={isSubmitting}
                    aria-invalid={Boolean(errors.description)}
                    aria-describedby={
                        errors.description
                            ? "course-description-error"
                            : "course-description-hint"
                    }
                />
            </Field>

            {mutationErrorMessage && (
                <p role="alert" className="text-sm text-destructive">
                    {mutationErrorMessage}
                </p>
            )}

            <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
                <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting
                        ? "Saving..."
                        : mode === "create"
                          ? "Create Course"
                          : "Save Changes"}
                </Button>

                <Link
                    href={
                        mode === "create" || !courseId
                            ? "/courses"
                            : `/courses/${courseId}`
                    }
                    className={courseLinkClass}
                >
                    Cancel
                </Link>
            </div>
        </form>
    );
}
