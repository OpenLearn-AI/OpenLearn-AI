import { useQuery } from "@tanstack/react-query";
import { getAccessToken } from "@/lib/keycloak";
import type { MeResponse } from "../types";

async function fetchMe(): Promise<MeResponse> {
    const token = await getAccessToken();

    if (!token) {
        throw new Error("Not authenticated");
    }

    const baseUrl = process.env.NEXT_PUBLIC_API_URL;

    const response = await fetch(`${baseUrl}/auth/me`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch /auth/me: ${response.status}`);
    }

    return response.json();
}

export function useMe() {
    return useQuery({
        queryKey: ["auth", "me"],
        queryFn: fetchMe,
    });
}

