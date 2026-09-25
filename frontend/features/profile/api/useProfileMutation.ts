import { useMutation } from "@tanstack/react-query";
import { getKeycloak } from "@/lib/keycloak";
import type { ProfileFormValues } from "../schemas";
import type { Profile } from "./useProfile";

export class ProfileApiError extends Error {
    status: number;

    constructor(message: string, status: number) {
        super(message);
        this.name = "ProfileApiError";
        this.status = status;
    }
}

async function getAccessToken(): Promise<string> {
    const keycloak = await getKeycloak();

    if (!keycloak || !keycloak.token) {
        throw new ProfileApiError("Not authenticated", 401);
    }

    return keycloak.token;
}

async function updateProfile(
    payload: ProfileFormValues,
): Promise<Profile> {
    const token = await getAccessToken();
    const baseUrl = process.env.NEXT_PUBLIC_API_URL;

    const response = await fetch(`${baseUrl}/v1/users/me`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new ProfileApiError(
            `Failed to update profile: ${response.status}`,
            response.status,
        );
    }

    return response.json();
}

export function useUpdateProfile() {
    return useMutation({
        mutationFn: updateProfile,
    });
}