import { useQuery } from "@tanstack/react-query";
import { getKeycloak } from "@/lib/keycloak";

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
    const keycloak = await getKeycloak();

    if (!keycloak || !keycloak.token) {
        throw new Error("Not authenticated");
    }

    const baseUrl = process.env.NEXT_PUBLIC_API_URL;

    const response = await fetch(`${baseUrl}/v1/users/me`, {
        headers: {
            Authorization: `Bearer ${keycloak.token}`,
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