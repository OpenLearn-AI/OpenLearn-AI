import { queryOptions, useQuery } from "@tanstack/react-query";

import { apiFetch, ApiError } from "@/lib/api";
import { useMe } from "@/features/auth/api/useMe";
import {
    profileResponseSchema,
    type Profile,
} from "@/features/profile/schemas";
import { profileKeys } from "@/features/profile/keys";

/**
 * Query options for the current user's profile (D5).
 *
 * `GET /v1/users/me` returns 404 when the user has not yet created a
 * profile. That is a legitimate application state (the form switches to
 * "Create Your Profile" mode), so the queryFn catches `ApiError(404)`
 * and resolves to `null` instead of throwing.
 */
export const profileOptions = queryOptions({
    queryKey: profileKeys.current(),
    queryFn: async (): Promise<Profile | null> => {
        try {
            return await apiFetch<Profile>("/v1/users/me", {
                schema: profileResponseSchema,
            });
        } catch (error) {
            if (error instanceof ApiError && error.status === 404) {
                return null;
            }
            throw error;
        }
    },
});

export function useProfile() {
    const me = useMe();

    return useQuery({
        ...profileOptions,
        enabled: me.isSuccess,
    });
}
