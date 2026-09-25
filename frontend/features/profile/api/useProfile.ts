import { useQuery } from "@tanstack/react-query";
import { getAccessToken } from "@/lib/keycloak";

export interface Profile {
    id: string;
    user_id: string;
    education_level: string;
    major: string;
    preferred_language: string;
    university: string | null;
    learning_style_vark: string | null;
    daily_available_minutes: number;
}

async function fetchProfile(): Promise<Profile> {
    const token = await getAccessToken();

    if (!token) {
        throw new Error("Not authenticated");
    }

    const baseUrl = process.env.NEXT_PUBLIC_API_URL;

    const response = await fetch(`${baseUrl}/v1/users/me`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        throw new Error(
            `Failed to fetch profile: ${response.status}`,
        );
    }

    return response.json();
}

export function useProfile() {
    return useQuery({
        queryKey: ["profile"],
        queryFn: fetchProfile,
    });
}