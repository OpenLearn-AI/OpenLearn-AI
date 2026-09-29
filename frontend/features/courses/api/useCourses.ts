import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api";
import { useMe } from "@/features/auth/api/useMe";
import { courseResponseSchema, type Course } from "@/features/courses/schemas";
import { courseKeys } from "@/features/courses/keys";

export function useCourses() {
    const me = useMe();

    return useQuery({
        queryKey: courseKeys.lists(),
        queryFn: () =>
            apiFetch<Course[]>("/v1/courses", {
                schema: courseResponseSchema.array(),
            }),
        enabled: me.isSuccess,
    });
}
