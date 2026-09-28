import { useMutation } from "@tanstack/react-query";
import { getAccessToken } from "@/lib/keycloak";
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


async function updateProfile(
    payload: ProfileFormValues,
): Promise<Profile> {
    const token = await getAccessToken();

    if (!token) {
        throw new ProfileApiError("Not authenticated", 401);
    }
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