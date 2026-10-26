import { queryOptions, useQuery } from "@tanstack/react-query";

import { apiFetch, ApiError } from "@/lib/api";
import { useMe } from "@/features/auth/api/useMe";
import { materialKeys } from "@/features/materials/keys";
import {
    materialResponseSchema,
    materialStatusResponseSchema,
    type Material,
    type MaterialStatusResponse,
} from "@/features/materials/schemas";
import { isTerminalMaterialStatus } from "@/features/materials/flow";

/**
 * Query options for a course's materials list (D5 — `queryOptions`
 * next to the hook; exported for potential prefetch reuse).
 *
 * `GET /v1/courses/{course_id}/materials` — the per-course listing
 * the Week 9 integration confirms Batch 4.3 consumes. Like every
 * course read, the backend authorizes by course ownership; the query
 * is gated on the session resolving (`me.isSuccess`), exactly like
 * `useCourses`.
 */
export function materialsListOptions(courseId: string) {
    return queryOptions({
        queryKey: materialKeys.list(courseId),
        queryFn: () =>
            apiFetch<Material[]>(
                `/v1/courses/${courseId}/materials`,
                { schema: materialResponseSchema.array() },
            ),
    });
}

export function useMaterials(courseId: string) {
    const me = useMe();

    return useQuery({
        ...materialsListOptions(courseId),
        enabled: Boolean(courseId) && me.isSuccess,
    });
}

/**
 * The per-material status poll interval (Batch 4.3). Modest by the
 * roadmap's own instruction — the pipeline's real processing time is
 * dominated by ingestion and embedding, not by this cadence; 5s
 * keeps a class-demo walkthrough visibly live without hammering the
 * API between two people testing it.
 */
export const MATERIAL_STATUS_POLL_INTERVAL_MS = 5000;

/**
 * Query options for a single material's status.
 *
 * `GET /v1/materials/{material_id}/status` — the contract's ONLY
 * status read (it keys on material_id; `job_id` from the 202
 * registration is log correlation and is never queried).
 */
export function materialStatusOptions(materialId: string) {
    return queryOptions({
        queryKey: materialKeys.status(materialId),
        queryFn: () =>
            apiFetch<MaterialStatusResponse>(
                `/v1/materials/${materialId}/status`,
                { schema: materialStatusResponseSchema },
            ),
    });
}

/**
 * Poll a material's status while it is in a NON-TERMINAL state.
 *
 * Polling discipline (the batch's contract rules):
 * - the interval callback stops itself the moment a terminal state
 *   (ready | failed) is observed — no polling after terminal states;
 * - the query is only ENABLED for non-terminal snapshots, so when
 *   the list updates to terminal the observer goes away and the
 *   interval is cleared with it (unmount and course change clean up
 *   the same way — the component owning this hook unmounts);
 * - UNRECOVERABLE poll errors (401/403/404 — the global 401 recovery
 *   takes over, or the material is gone) stop the interval; a
 *   transient network error keeps the modest cadence so a blip
 *   cannot freeze the status forever;
 * - React Query dedupes concurrent same-key fetches, so overlapping
 *   polls cannot stack.
 */
export function useMaterialStatus(
    materialId: string,
    enabled: boolean,
) {
    return useQuery({
        ...materialStatusOptions(materialId),
        enabled: enabled && Boolean(materialId),
        refetchInterval: (query) => {
            const data = query.state.data;
            if (data && isTerminalMaterialStatus(data.status)) {
                return false;
            }

            const pollError = query.state.error;
            if (
                pollError instanceof ApiError &&
                (pollError.status === 401 ||
                    pollError.status === 403 ||
                    pollError.status === 404)
            ) {
                return false;
            }

            return MATERIAL_STATUS_POLL_INTERVAL_MS;
        },
    });
}
