import { useQuery } from "@tanstack/react-query";
import { getAccessToken } from "@/lib/keycloak";
import { useMe } from "@/features/auth/api/useMe";

export interface Course {
    id: string;
    owner_id: string;
    title: string;
    description: string | null;
    created_at: string;
}

async function fetchCourses(): Promise<Course[]> {
    const token = await getAccessToken();

    if (!token) {
        throw new Error("Not authenticated");
    }

    const baseUrl = process.env.NEXT_PUBLIC_API_URL;

    const response = await fetch(`${baseUrl}/v1/courses`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch courses: ${response.status}`);
    }

    return response.json();
}

export function useCourses() {
    const me = useMe();

    return useQuery({
        queryKey: ["courses"],
        queryFn: fetchCourses,
        enabled: me.isSuccess,
    });
}
