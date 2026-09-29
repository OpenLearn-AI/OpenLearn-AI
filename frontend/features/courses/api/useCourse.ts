import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api";
import { useMe } from "@/features/auth/api/useMe";
import { courseResponseSchema, type Course } from "@/features/courses/schemas";
import { courseKeys } from "@/features/courses/keys";

export function useCourse(courseId: string) {
    const me = useMe();

    return useQuery({
        queryKey: courseKeys.detail(courseId),
        queryFn: () =>
            apiFetch<Course>(`/v1/courses/${courseId}`, {
                schema: courseResponseSchema,
            }),
        enabled: Boolean(courseId) && me.isSuccess,
    });
}
