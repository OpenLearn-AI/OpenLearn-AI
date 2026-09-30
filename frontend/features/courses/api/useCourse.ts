import { queryOptions, useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api";
import { useMe } from "@/features/auth/api/useMe";
import { courseResponseSchema, type Course } from "@/features/courses/schemas";
import { courseKeys } from "@/features/courses/keys";

/**
 * Query options for a single course detail (D5 — `queryOptions` objects
 * next to the hooks). A function because the key and path depend on the
 * `courseId` parameter; exported so `prefetchQuery` / `fetchQuery` can
 * reuse the same definition in future phases.
 */
export function courseDetailOptions(courseId: string) {
    return queryOptions({
        queryKey: courseKeys.detail(courseId),
        queryFn: () =>
            apiFetch<Course>(`/v1/courses/${courseId}`, {
                schema: courseResponseSchema,
            }),
    });
}

export function useCourse(courseId: string) {
    const me = useMe();

    return useQuery({
        ...courseDetailOptions(courseId),
        enabled: Boolean(courseId) && me.isSuccess,
    });
}
