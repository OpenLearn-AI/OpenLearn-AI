"use client";

import { useState } from "react";

import { EmptyState } from "@/components/state/EmptyState";
import { ErrorState } from "@/components/state/ErrorState";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { Button } from "@/components/ui/button";
import {
    MATERIAL_PAGES_QUERY_LIMIT,
    useMaterialPages,
} from "@/features/materials/api/useMaterials";
import {
    describeMaterialPagesError,
    MATERIAL_EMPTY_PAGE_COPY,
    MATERIAL_NO_PAGES_COPY,
    materialPageLabel,
    mayHaveMorePages,
} from "@/features/materials/flow";
import type { Material } from "@/features/materials/schemas";

/**
 * The extracted-text viewer (Batch 4.5 — the Week 9 frontend
 * assignment): a lazy disclosure region inside a READY material's
 * row, reading `GET /v1/materials/{id}/pages` through the existing
 * materials module.
 *
 * Honesty rules (the tracked contract, cross-checked against
 * `docs/openapi.json`):
 * - mounts ONLY when the disclosure is open on a `ready` material —
 *   nothing is fetched for queued/processing/failed materials, and
 *   the region unmounts the moment the status leaves `ready`;
 * - pages render as clearly labeled blocks ("Page 1", "Page 2", …)
 *   with `dir="auto"` so Arabic and English content each read in
 *   their own direction, inside a constrained reading column;
 * - `pages: []` is stated plainly ("No extracted text stored for
 *   this material yet."); a page with empty `text` is stated plainly
 *   too ("This page has no extractable text.");
 * - pagination is honest: the contract has NO total count, so none is
 *   shown — "Load more pages" appears only when the last window came
 *   back full (a shorter window is the last one by contract);
 * - loading and error states use the shared async-state kit; a failed
 *   read gets the established retry action; 401 hands off to the
 *   global session recovery, and 403/404 map to plain copy with no
 *   internal details (`describeMaterialPagesError`);
 * - extracted text is presented exactly as stored (newlines
 *   preserved) — no reformatting, summarizing, or "AI" treatment.
 */

/** The flat, hairline presentation for the state kit inside the
 * viewer region (the page-level D13 grammar the materials region
 * uses, at the region's tighter rhythm). */
const VIEWER_STATE_CLASS =
    "mt-2 flex-col rounded-none border-x-0 border-b-0 bg-transparent px-0 py-5 text-start shadow-none";

export function MaterialTextViewer({
    material,
    regionId,
}: {
    material: Material;
    /** The disclosure control's `aria-controls` target id (owned by
     * the row so the button and region can never disagree). */
    regionId: string;
}) {
    // How many page-list windows have been requested; each window is
    // its own cached query (see materialPagesOptions), merged below.
    const [windowCount, setWindowCount] = useState(1);

    const windowQueries = useMaterialPages(material.id, windowCount);

    const firstWindow = windowQueries[0]!;
    const lastWindow = windowQueries[windowQueries.length - 1]!;

    // The merged page list across every loaded window — a pending or
    // failed later window simply contributes nothing yet.
    const pages = windowQueries.flatMap((query) => query.data?.pages ?? []);

    const initialPending = firstWindow.isPending;
    const initialError = firstWindow.isError ? firstWindow.error : null;

    const failedWindow = windowQueries.find((query) => query.isError) ?? null;
    const failedWindowError =
        failedWindow !== null && failedWindow.isError
            ? failedWindow.error
            : null;

    const loadingMore =
        !initialPending &&
        !initialError &&
        windowCount > 1 &&
        lastWindow.isPending;

    const morePossible =
        lastWindow.data !== undefined &&
        mayHaveMorePages(
            lastWindow.data.pages.length,
            MATERIAL_PAGES_QUERY_LIMIT,
        );

    return (
        <section
            id={regionId}
            aria-labelledby={`${regionId}-heading`}
            className="mt-3 border-s border-border ps-4 sm:ps-5"
        >
            <h4
                id={`${regionId}-heading`}
                className="font-mono text-[0.6875rem] font-medium uppercase tracking-wider text-muted-foreground"
            >
                Extracted text
            </h4>

            {initialPending ? (
                <LoadingBlock
                    message="Loading extracted text..."
                    className={VIEWER_STATE_CLASS}
                />
            ) : initialError !== null ? (
                <ErrorState
                    message={describeMaterialPagesError(initialError)}
                    onRetry={() => void firstWindow.refetch()}
                    className={VIEWER_STATE_CLASS}
                />
            ) : pages.length === 0 ? (
                <EmptyState
                    message={MATERIAL_NO_PAGES_COPY}
                    className={VIEWER_STATE_CLASS}
                />
            ) : (
                <div>
                    <ol className="divide-y divide-border">
                        {pages.map((page) => (
                            <li
                                key={page.page_number}
                                className="py-4 first:pt-3 last:pb-0"
                            >
                                <p className="font-mono text-[0.6875rem] font-medium uppercase tracking-wider text-muted-foreground">
                                    {materialPageLabel(page.page_number)}
                                </p>
                                {page.text.length > 0 ? (
                                    <p
                                        dir="auto"
                                        className="mt-2 max-w-[60ch] text-[0.9375rem] leading-[1.7] text-foreground break-words whitespace-pre-wrap"
                                    >
                                        {page.text}
                                    </p>
                                ) : (
                                    <p className="mt-2 max-w-[60ch] text-[0.8125rem] leading-[1.6] text-muted-foreground">
                                        {MATERIAL_EMPTY_PAGE_COPY}
                                    </p>
                                )}
                            </li>
                        ))}
                    </ol>

                    {failedWindowError !== null ? (
                        <ErrorState
                            message={describeMaterialPagesError(
                                failedWindowError,
                            )}
                            onRetry={() => void failedWindow?.refetch()}
                            className={VIEWER_STATE_CLASS}
                        />
                    ) : morePossible ? (
                        <div className="mt-5">
                            <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                disabled={loadingMore}
                                onClick={() =>
                                    setWindowCount((count) => count + 1)
                                }
                            >
                                {loadingMore ? "Loading…" : "Load more pages"}
                            </Button>
                        </div>
                    ) : null}
                </div>
            )}
        </section>
    );
}
