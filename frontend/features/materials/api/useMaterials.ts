import { queryOptions, useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch, ApiError } from "@/lib/api";
import { useMe } from "@/features/auth/api/useMe";
import { materialKeys } from "@/features/materials/keys";
import {
    materialAcceptedResponseSchema,
    materialPagesResponseSchema,
    materialResponseSchema,
    materialStatusResponseSchema,
    type Material,
    type MaterialAcceptedResponse,
    type MaterialPagesResponse,
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

/* -------------------------------------------------------------------------
 * Batch 4.5 — the Week 9 operations: the extracted-text page list and
 * the reprocess request. Both consume the tracked contract through the
 * same `apiFetch` boundary, Zod validation, and key conventions as the
 * 4.3 queries above.
 * ---------------------------------------------------------------------- */

/**
 * The extracted-text viewer's page-list window size. The contract's
 * own default (`limit` 1–500, default 100); a demo-scale document
 * fits one window, and a full window is the only honest signal that
 * more pages may follow (see `mayHaveMorePages`).
 */
export const MATERIAL_PAGES_QUERY_LIMIT = 100;

/**
 * Query options for one window of a material's stored pages
 * (`GET /v1/materials/{material_id}/pages?limit&offset`, Week 9).
 *
 * Each window is its own cache entry — keyed by the material's pages
 * branch plus the window's offset — so "Load more pages" never
 * refetches earlier windows, and a reprocess invalidates the whole
 * branch by prefix.
 */
export function materialPagesOptions(materialId: string, offset = 0) {
    return queryOptions({
        queryKey: [...materialKeys.pages(materialId), offset],
        queryFn: () =>
            apiFetch<MaterialPagesResponse>(
                `/v1/materials/${materialId}/pages` +
                    `?limit=${MATERIAL_PAGES_QUERY_LIMIT}&offset=${offset}`,
                { schema: materialPagesResponseSchema },
            ),
    });
}

/**
 * The viewer's page-list windows (Batch 4.5). The viewer component
 * mounts ONLY when its disclosure is open on a `ready` material —
 * that mount IS the lazy gate ("do not fetch page content until the
 * user opens the viewer") — and each window query is additionally
 * gated on the session resolving (`me.isSuccess`, the established
 * `useMaterials` convention).
 */
export function useMaterialPages(materialId: string, windowCount: number) {
    const me = useMe();

    return useQueries({
        queries: Array.from(
            { length: Math.max(1, windowCount) },
            (_, index) => ({
                ...materialPagesOptions(
                    materialId,
                    index * MATERIAL_PAGES_QUERY_LIMIT,
                ),
                enabled: Boolean(materialId) && me.isSuccess,
            }),
        ),
    });
}

/**
 * The reprocess request (`POST /v1/materials/{material_id}/process`,
 * Week 9) for a terminal (`ready`/`failed`) material, made by the
 * course owner + instructor the backend authorizes.
 *
 * On the 202 acceptance:
 * - `job_id` is logged ONCE for correlation and never queried (the
 *   registration rule, unchanged);
 * - the per-material status cache is seeded with the response's own
 *   `{material_id, status}` so the EXISTING status poll resumes from
 *   the server's answer (the 4.1 onboarding seeding precedent) — no
 *   second polling system, no interval change;
 * - the course's materials list is invalidated (the row returns to
 *   `pending` through the list, the single rendering source);
 * - the material's cached page windows are invalidated — a re-run
 *   may change the stored text under the keep-more-pages rule.
 *
 * Callers own the UI states: `isPending` drives the disabled
 * "Requesting…" control; errors map through
 * `describeMaterialProcessError` (the two documented 409 classes and
 * the 429 pass the backend's own user-readable detail).
 */
export function useProcessMaterial(courseId: string, materialId: string) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: () =>
            apiFetch<MaterialAcceptedResponse>(
                `/v1/materials/${materialId}/process`,
                { method: "POST", schema: materialAcceptedResponseSchema },
            ),
        onSuccess: (accepted) => {
            // Correlation log: identifiers only, once (never a query
            // key or poll target — the registration convention).
            console.info("[materials] reprocess accepted", {
                materialId: accepted.material_id,
                jobId: accepted.job_id,
                status: accepted.status,
            });

            // Seed the existing status poll with the server's own
            // answer so it resumes honestly from the accepted state.
            queryClient.setQueryData<MaterialStatusResponse>(
                materialKeys.status(materialId),
                {
                    material_id: accepted.material_id,
                    status: accepted.status,
                },
            );

            void queryClient.invalidateQueries({
                queryKey: materialKeys.list(courseId),
            });
            void queryClient.invalidateQueries({
                queryKey: materialKeys.pages(materialId),
            });
        },
    });
}
