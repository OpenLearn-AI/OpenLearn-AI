import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api";
import {
    profileResponseSchema,
    type Profile,
} from "@/features/profile/schemas";
import { profileKeys } from "@/features/profile/keys";
import type { ProfileFormValues } from "@/features/profile/schemas";

/**
 * Profile upsert mutation (D5 invalidation convention).
 *
 * `PUT /v1/users/me` is an upsert: it creates the profile if it does
 * not exist, or replaces it if it does. On success the profile query
 * is invalidated so the page reflects the new state without a manual
 * refresh.
 */
export function useUpdateProfile() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (payload: ProfileFormValues) =>
            apiFetch<Profile>("/v1/users/me", {
                method: "PUT",
                body: payload,
                schema: profileResponseSchema,
            }),
        onSuccess: () => {
            void queryClient.invalidateQueries({
                queryKey: profileKeys.all,
            });
        },
    });
}
