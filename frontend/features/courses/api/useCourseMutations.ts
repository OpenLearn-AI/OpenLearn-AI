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

/**
 * Delete a course (D5 invalidation convention).
 *
 * `DELETE /v1/courses/{course_id}` returns 204 No Content on success.
 * On success the entire course cache is invalidated — both the list
 * (so the deleted course disappears without a manual refresh) and
 * the detail (so an open detail/edit page doesn't serve stale data).
 *
 * The backend returns 404 if the course doesn't exist and 403 if the
 * authenticated user is not the owner. These surface as `ApiError`
 * via `apiFetch`; callers map them to user-facing messages.
 */
export function useDeleteCourse() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (courseId: string) =>
            apiFetch<void>(`/v1/courses/${courseId}`, {
                method: "DELETE",
            }),
        onSuccess: () => {
            void queryClient.invalidateQueries({
                queryKey: courseKeys.all,
            });
        },
    });
}
