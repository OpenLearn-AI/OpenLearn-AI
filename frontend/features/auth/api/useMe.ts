import { useQuery } from "@tanstack/react-query";
import { getKeycloak } from "@/lib/keycloak";
import type { MeResponse } from "../types";

async function fetchMe(): Promise<MeResponse> {
    const keycloak = await getKeycloak();

    if (!keycloak || !keycloak.token) {
        throw new Error("Not authenticated");
    }

    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

    const response = await fetch(`${baseUrl}/auth/me`, {
        headers: {
            Authorization: `Bearer ${keycloak.token}`,
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