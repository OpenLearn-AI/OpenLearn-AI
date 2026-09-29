import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api";
import { courseResponseSchema, type Course } from "@/features/courses/schemas";
import { courseKeys } from "@/features/courses/keys";
import type { CourseFormValues } from "@/features/courses/schemas";

/**
 * Course create/update mutations (D5 invalidation convention).
 *
 * Both mutations invalidate `courseKeys.lists()` on success so that a
 * freshly created/updated course appears in the courses list without a
 * manual refresh. The update mutation also invalidates the affected
 * detail key so an open detail page reflects the new state.
 *
 * Callers retain responsibility for navigation (the form still pushes
 * to `/courses` on success) — invalidation handles cache consistency,
 * navigation handles the user's viewport.
 */
export function useCreateCourse() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (payload: CourseFormValues) =>
            apiFetch<Course>("/v1/courses", {
                method: "POST",
                body: payload,
                schema: courseResponseSchema,
            }),
        onSuccess: () => {
            void queryClient.invalidateQueries({
                queryKey: courseKeys.lists(),
            });
        },
    });
}

export function useUpdateCourse() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({
            courseId,
            payload,
        }: {
            courseId: string;
            payload: CourseFormValues;
        }) =>
            apiFetch<Course>(`/v1/courses/${courseId}`, {
                method: "PUT",
                body: payload,
                schema: courseResponseSchema,
            }),
        onSuccess: (_data, { courseId }) => {
            void queryClient.invalidateQueries({
                queryKey: courseKeys.lists(),
            });
            void queryClient.invalidateQueries({
                queryKey: courseKeys.detail(courseId),
            });
        },
    });
}
