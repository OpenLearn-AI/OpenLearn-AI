import { useQuery } from "@tanstack/react-query";
import { getKeycloak } from "@/lib/keycloak";
import type { Course } from "./useCourses";

async function fetchCourse(courseId: string): Promise<Course> {
    const keycloak = await getKeycloak();

    if (!keycloak || !keycloak.token) {
        throw new Error("Not authenticated");
    }

    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

    const response = await fetch(
        `${baseUrl}/v1/courses/${courseId}`,
        {
            headers: {
                Authorization: `Bearer ${keycloak.token}`,
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
    return useQuery({
        queryKey: ["courses", courseId],
        queryFn: () => fetchCourse(courseId),
        enabled: Boolean(courseId),
    });
}