import { queryOptions, useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api";
import { useMe } from "@/features/auth/api/useMe";
import { courseResponseSchema, type Course } from "@/features/courses/schemas";
import { courseKeys } from "@/features/courses/keys";

/**
 * Query options for the courses list (D5 — `queryOptions` objects next to
 * the hooks). Exported so `prefetchQuery` / `fetchQuery` can reuse the
 * same key + queryFn in future phases without duplicating the definition.
 */
export const coursesListOptions = queryOptions({
    queryKey: courseKeys.lists(),
    queryFn: () =>
        apiFetch<Course[]>("/v1/courses", {
            schema: courseResponseSchema.array(),
        }),
});

export function useCourses() {
    const me = useMe();

    return useQuery({
        ...coursesListOptions,
        enabled: me.isSuccess,
    });
}
