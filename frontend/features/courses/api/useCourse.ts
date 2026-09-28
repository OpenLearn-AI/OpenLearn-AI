import { useQuery } from "@tanstack/react-query";
import { getAccessToken } from "@/lib/keycloak";
import type { Course } from "./useCourses";
import { useMe } from "@/features/auth/api/useMe";

async function fetchCourse(courseId: string): Promise<Course> {
    const token = await getAccessToken();

    if (!token) {
        throw new Error("Not authenticated");
    }

    const baseUrl = process.env.NEXT_PUBLIC_API_URL;

    const response = await fetch(
        `${baseUrl}/v1/courses/${courseId}`,
        {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        },
    );

    if (!response.ok) {
        throw new Error(
            `Failed to fetch course: ${response.status}`,
        );
    }

    return response.json();
}

export function useCourse(courseId: string) {
    const me = useMe();

    return useQuery({
        queryKey: ["courses", courseId],
        queryFn: () => fetchCourse(courseId),
        enabled: Boolean(courseId) && me.isSuccess,
    });
}
