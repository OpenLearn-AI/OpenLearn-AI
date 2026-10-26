"use client";

import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { ChevronDown, UploadCloud } from "lucide-react";

import { cn } from "@/lib/utils";
import { apiFetch, ApiError } from "@/lib/api";
import { formatCourseCreatedDate } from "@/components/CourseCard";
import { EmptyState } from "@/components/state/EmptyState";
import { ErrorState } from "@/components/state/ErrorState";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { Button } from "@/components/ui/button";
import { Field } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { MaterialTextViewer } from "@/components/courses/MaterialTextViewer";
import {
    useMaterialStatus,
    useMaterials,
    useProcessMaterial,
} from "@/features/materials/api/useMaterials";
import { materialKeys } from "@/features/materials/keys";
import {
    buildUploadFormData,
    describeMaterialFlowError,
    describeMaterialProcessError,
    formatByteSize,
    isTerminalMaterialStatus,
    MATERIAL_FAILED_COPY,
    MATERIAL_PROCESS_ACCEPTED_COPY,
    MATERIAL_PROCESS_REQUESTING_LABEL,
    MATERIAL_STATUS_LABELS,
} from "@/features/materials/flow";
import {
    materialAcceptedResponseSchema,
    uploadUrlCreateSchema,
    uploadUrlResponseSchema,
    type Material,
    type MaterialAcceptedResponse,
    type MaterialStatus,
    type UploadUrlResponse,
} from "@/features/materials/schemas";

/**
 * The course-detail materials surface (Batch 4.3; the extracted-text
 * viewer and reprocess control added in Batch 4.5) — the roadmap's
 * "course-detail-scoped materials component".
 *
 * Consumes the EXISTING contract only (roadmap §10 / Table 12; the
 * request/response shapes are cross-checked against
 * `docs/openapi.json`):
 *
 * 1. `POST /v1/courses/{id}/materials/upload-url` `{filename,title}`
 *    → the presigned POST target (`upload_url` + `upload_fields`,
 *    `max_size_bytes`, `expires_in`).
 * 2. The browser uploads the file DIRECTLY to storage — a
 *    `multipart/form-data` POST with the signed fields first and the
 *    file LAST (the order the `UploadUrlResponse` documents; NOT a
 *    PUT). The presigned policy is the authorization; no bearer
 *    token, no signed URL, and no file data is ever logged.
 * 3. `POST /v1/courses/{id}/materials` `{s3_key,title}` →
 *    202 `{material_id, status, job_id}`. `job_id` is logged for
 *    correlation and NEVER queried (the status endpoint keys on
 *    material_id); a `null` job_id means Week 9 dedup returned the
 *    EXISTING material — presented honestly as such.
 * 4. (Batch 4.5) `GET /v1/materials/{id}/pages` — the extracted-text
 *    viewer on READY rows (see `MaterialTextViewer`).
 * 5. (Batch 4.5) `POST /v1/materials/{id}/process` — the reprocess
 *    control on terminal (`failed` AND `ready`) rows for the owning
 *    instructor (see `MaterialProcessControl`).
 *
 * Registration/reprocess acceptance is NEVER presented as processing
 * completion: the 202 is acknowledged in its own words, and the
 * material's live status (`pending`/`processing`) comes from the
 * list and the per-material status poll, which stops at the
 * terminal states (`ready`/`failed`).
 *
 * Role-awareness: the upload AND reprocess affordances render ONLY
 * where the existing authorization model allows them (the owning
 * instructor — the caller derives this from `me` +
 * `course.owner_id`); the extracted-text viewer renders for any hub
 * visitor on a `ready` row (the page read is already owner-scoped;
 * the backend's `require_owned_course` on the pages endpoint remains
 * the boundary). Hiding a control is presentation, never the
 * authorization boundary (the backend enforces instructor role +
 * course ownership on every step).
 *
 * Honesty rules (roadmap Table 9): no progress percentages, no
 * phase names, no ETA, no fake AI reasoning, no retry-budget
 * prediction (`MaterialResponse` exposes no `retry_count` — the
 * budget is only ever surfaced through the backend's own documented
 * 409 detail), and the failed state names the plausible cause CLASS
 * without claiming to know which one occurred.
 */

/** The flat, hairline presentation for the state kit inside this
 * region (the page-level D13 grammar — the kit's real components
 * and semantics, without the card chrome). */
const FLAT_STATE_CLASS =
    "mt-6 flex-col rounded-none border-x-0 border-b-0 bg-transparent px-0 py-6 text-start shadow-none";

/** The upload flow's phases — one observable step at a time. */
type UploadPhase = "idle" | "url" | "uploading" | "registering";

const PHASE_MESSAGES: Record<Exclude<UploadPhase, "idle">, string> = {
    url: "Requesting an upload link…",
    uploading: "Uploading the file…",
    registering: "Registering the material…",
};

/** Prefill helper: a sensible default title from the chosen file —
 * the base name without its extension (editable; presentation
 * state only). */
export function titleFromFilename(filename: string): string {
    const base = filename.replace(/\.[^.]+$/u, "").trim();
    return base.slice(0, 255);
}

export function CourseMaterials({
    courseId,
    canUpload,
}: {
    courseId: string;
    canUpload: boolean;
}) {
    const {
        data: materials,
        isLoading,
        isError,
        error,
        refetch,
    } = useMaterials(courseId);

    return (
        <div>
            {canUpload ? (
                <MaterialUploadForm courseId={courseId} />
            ) : null}

            {isLoading ? (
                <LoadingBlock
                    message="Loading materials..."
                    className={FLAT_STATE_CLASS}
                />
            ) : isError ? (
                <ErrorState
                    message={
                        error instanceof Error
                            ? error.message
                            : "Failed to load materials."
                    }
                    onRetry={() => void refetch()}
                    className={FLAT_STATE_CLASS}
                />
            ) : (materials ?? []).length === 0 ? (
                <EmptyState
                    message="No materials in this course yet."
                    className={FLAT_STATE_CLASS}
                />
            ) : (
                <ol className="mt-2">
                    {(materials ?? []).map((material) => (
                        <MaterialRow
                            key={material.id}
                            material={material}
                            courseId={courseId}
                            canManage={canUpload}
                        />
                    ))}
                </ol>
            )}
        </div>
    );
}

/**
 * The owning instructor's upload affordance — one submit drives the
 * three-step contract flow sequentially; the submit control is
 * disabled while any step is in flight (duplicate-submit
 * protection), and every failure is honest, mapped copy (no stack
 * traces, no signed URLs, no internal details).
 */
function MaterialUploadForm({ courseId }: { courseId: string }) {
    const queryClient = useQueryClient();

    const [title, setTitle] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [titleError, setTitleError] = useState<string | undefined>(
        undefined,
    );
    const [fileError, setFileError] = useState<string | undefined>(undefined);
    const [phase, setPhase] = useState<UploadPhase>("idle");
    const [flowError, setFlowError] = useState<string | null>(null);
    const [accepted, setAccepted] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const inFlight = phase !== "idle";
    const phaseMessage =
        phase === "idle" ? null : PHASE_MESSAGES[phase];

    function resetValidation() {
        setTitleError(undefined);
        setFileError(undefined);
        setFlowError(null);
        setAccepted(null);
    }

    async function handleSubmit(
        event: React.FormEvent<HTMLFormElement>,
    ): Promise<void> {
        event.preventDefault();
        if (inFlight) {
            return;
        }

        resetValidation();

        // Pre-flight validation mirrors the contract's own bounds
        // (UploadUrlCreate: filename + title, 1–255 chars each) — the
        // backend still validates; this is presentation honesty.
        const parsed = uploadUrlCreateSchema.safeParse({
            filename: file?.name ?? "",
            title,
        });

        if (!file) {
            setFileError("Choose a file to upload.");
            if (!parsed.success) {
                applyTitleIssues(parsed.error.issues);
            }
            return;
        }

        if (!parsed.success) {
            applyTitleIssues(parsed.error.issues);
            if (parsed.error.issues.some((i) => i.path[0] === "filename")) {
                setFileError("Choose a valid file (its name is too long).");
            }
            return;
        }

        setPhase("url");

        try {
            // 1 — the presigned POST target.
            const uploadTarget = await apiFetch<UploadUrlResponse>(
                `/v1/courses/${courseId}/materials/upload-url`,
                {
                    method: "POST",
                    body: parsed.data,
                    schema: uploadUrlResponseSchema,
                },
            );

            // Contract-driven size guard: the policy itself limits the
            // object (content-length-range, max_size_bytes); failing
            // BEFORE the transfer is the honest, immediate version.
            if (file.size > uploadTarget.max_size_bytes) {
                throw new ApiError(
                    413,
                    `This file is larger than the maximum upload size of ${formatByteSize(uploadTarget.max_size_bytes)}.`,
                );
            }

            setPhase("uploading");

            // 2 — the direct-to-storage POST. The presigned fields are
            // the authorization; NO Authorization header, and the
            // signed URL is never logged or displayed.
            const uploadResponse = await fetch(uploadTarget.upload_url, {
                method: "POST",
                body: buildUploadFormData(uploadTarget.upload_fields, file),
            });

            if (!uploadResponse.ok) {
                throw new ApiError(
                    uploadResponse.status,
                    uploadResponse.status === 413
                        ? "The file is larger than the maximum upload size."
                        : "The file upload failed. The upload link may have expired — please try again.",
                );
            }

            setPhase("registering");

            // 3 — registration (202). The response's job_id is
            // correlation data for logs ONLY — logged, never queried.
            const registered =
                await apiFetch<MaterialAcceptedResponse>(
                    `/v1/courses/${courseId}/materials`,
                    {
                        method: "POST",
                        body: {
                            s3_key: uploadTarget.s3_key,
                            title: uploadTarget.title,
                        },
                        schema: materialAcceptedResponseSchema,
                    },
                );

            // Correlation log: identifiers only (never the signed URL,
            // never the s3_key contents, never tokens).
            console.info("[materials] registration accepted", {
                materialId: registered.material_id,
                jobId: registered.job_id,
                status: registered.status,
            });

            // Acceptance is not completion (roadmap): say so in the
            // exact terms the response supports.
            setAccepted(
                registered.job_id === null
                    ? "This file is already in the course — showing its current state."
                    : "Material registered. Processing is queued — its status appears in the list below.",
            );

            // Reset the form; the list refetches through the shared
            // cache so the new row (and its live status) appears.
            setTitle("");
            setFile(null);
            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
            await queryClient.invalidateQueries({
                queryKey: materialKeys.list(courseId),
            });
        } catch (cause) {
            setFlowError(describeMaterialFlowError(cause));
        } finally {
            setPhase("idle");
        }
    }

    /** Map the pre-flight schema issues to the title field's copy
     * (the same wording convention as CourseForm). */
    function applyTitleIssues(
        issues: { path: (string | number | symbol)[]; code: string }[],
    ) {
        for (const issue of issues) {
            if (issue.path[0] === "title") {
                setTitleError(
                    issue.code === "too_big"
                        ? "Title must be 255 characters or less."
                        : "Title is required.",
                );
            }
        }
    }

    return (
        <form
            onSubmit={(event) => void handleSubmit(event)}
            noValidate
            className="border-t border-border pt-6"
        >
            <div className="grid gap-5 md:grid-cols-2 md:gap-8">
                <Field
                    label="Material title"
                    htmlFor="material-title"
                    error={titleError}
                >
                    <Input
                        id="material-title"
                        value={title}
                        onChange={(event) => setTitle(event.target.value)}
                        placeholder="e.g. Lecture 1 — handout"
                        disabled={inFlight}
                        aria-invalid={Boolean(titleError)}
                        aria-describedby={
                            titleError ? "material-title-error" : undefined
                        }
                    />
                </Field>

                <Field
                    label="File"
                    htmlFor="material-file"
                    error={fileError}
                >
                    <input
                        ref={fileInputRef}
                        id="material-file"
                        type="file"
                        disabled={inFlight}
                        aria-invalid={Boolean(fileError)}
                        aria-describedby={
                            fileError ? "material-file-error" : undefined
                        }
                        onChange={(event) => {
                            const chosen = event.target.files?.[0] ?? null;
                            setFile(chosen);
                            setFileError(undefined);
                            // A sensible default from the real file —
                            // only when the title is still empty.
                            if (chosen && title.trim() === "") {
                                setTitle(titleFromFilename(chosen.name));
                            }
                        }}
                        className="w-full cursor-pointer rounded-lg border border-input bg-transparent text-sm text-muted-foreground outline-none transition-colors file:me-3 file:inline-flex file:h-8 file:cursor-pointer file:rounded-lg file:border-0 file:bg-muted file:px-3 file:text-sm file:font-medium file:text-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 dark:bg-input/30"
                    />
                </Field>
            </div>

            <div className="mt-5 flex flex-wrap items-center gap-x-6 gap-y-3">
                <Button type="submit" disabled={inFlight || !file || !title}>
                    <UploadCloud
                        aria-hidden="true"
                        className="size-4"
                        data-icon="inline-start"
                    />
                    {inFlight ? phaseMessage : "Upload Material"}
                </Button>

                {/* The in-flight phase is announced politely — a
                    percentage or progress bar does not exist in the
                    contract and none is fabricated. */}
                <p
                    role="status"
                    aria-live="polite"
                    className="font-mono text-[0.8125rem] text-muted-foreground"
                >
                    {phaseMessage ?? accepted}
                </p>
            </div>

            {flowError ? (
                <p
                    role="alert"
                    aria-live="assertive"
                    className="mt-4 text-sm text-destructive"
                >
                    {flowError}
                </p>
            ) : null}
        </form>
    );
}

/** The reprocess request's user-facing feedback (Batch 4.5): either
 * the 202 acceptance (its own words — never a fabricated processing
 * state) or a mapped error message (the two documented 409 classes
 * and the 429 carry the backend's own user-readable detail). */
export type MaterialProcessFeedback =
    | { kind: "accepted" }
    | { kind: "error"; message: string };

/**
 * The reprocess control (Batch 4.5) — a purely presentational piece
 * of a terminal material row: the "Reprocess" action plus its
 * feedback message. The owning row drives it with the mutation's
 * state (`useProcessMaterial` owns the request and the cache
 * effects); keeping the presentation separate keeps `MaterialRow`
 * focused and makes every state — including the documented
 * retry-budget-exhausted 409 — renderable as an honest, hermetic
 * story.
 *
 * The control is disabled and reads "Requesting…" while the request
 * is in flight (duplicate-submit protection); acceptance is a
 * `role=status` note, errors a `role=alert` — the same live-region
 * grammar as the upload form.
 */
export function MaterialProcessControl({
    visible,
    pending,
    feedback,
    onRequest,
}: {
    /** The owning instructor + a terminal (`ready`|`failed`) status. */
    visible: boolean;
    /** The reprocess request is in flight. */
    pending: boolean;
    feedback: MaterialProcessFeedback | null;
    onRequest: () => void;
}) {
    if (!visible && feedback === null) {
        return null;
    }

    return (
        <>
            {visible ? (
                <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    disabled={pending}
                    onClick={onRequest}
                >
                    {pending
                        ? MATERIAL_PROCESS_REQUESTING_LABEL
                        : "Reprocess"}
                </Button>
            ) : null}

            {feedback?.kind === "accepted" ? (
                <p
                    role="status"
                    aria-live="polite"
                    className="font-mono text-[0.8125rem] text-muted-foreground"
                >
                    {MATERIAL_PROCESS_ACCEPTED_COPY}
                </p>
            ) : feedback?.kind === "error" ? (
                <p role="alert" className="text-sm text-destructive">
                    {feedback.message}
                </p>
            ) : null}
        </>
    );
}

/**
 * One materials-list row. Rows in a non-terminal state own their
 * per-material status poll (`GET /v1/materials/{id}/status`, keyed on
 * material_id — job_id is never queried); the poll stops itself at
 * the terminal states, and a polled change patches the shared list
 * cache so the list stays the single rendering source. Unmounting
 * the row (or changing course) removes the query observer and the
 * interval with it.
 *
 * Batch 4.5 adds the terminal-row action area: the extracted-text
 * viewer disclosure on `ready` rows (lazy — the viewer, and its
 * page-list queries, exist only while open on a ready material) and
 * the reprocess control for the owning instructor on `failed` AND
 * `ready` rows.
 */
function MaterialRow({
    material,
    courseId,
    canManage,
}: {
    material: Material;
    courseId: string;
    canManage: boolean;
}) {
    const queryClient = useQueryClient();

    const [viewerOpen, setViewerOpen] = useState(false);

    const statusQuery = useMaterialStatus(
        material.id,
        !isTerminalMaterialStatus(material.status),
    );

    const polledStatus = statusQuery.data?.status;
    const liveStatus: MaterialStatus = polledStatus ?? material.status;

    const processMutation = useProcessMaterial(courseId, material.id);

    // The request feedback, plus the state needed to derive its
    // visibility WITHOUT a state-clearing effect: the acceptance note
    // speaks while the pipeline visibly runs (non-terminal) and
    // yields to the outcome the moment a terminal state lands; an
    // error speaks while the material still sits in the state the
    // request was made from (the 409/429 classes never change the
    // status, so they persist until the next request — exactly as
    // they should).
    const [processFeedback, setProcessFeedback] = useState<
        | { kind: "accepted" }
        | { kind: "error"; message: string; status: MaterialStatus }
        | null
    >(null);

    const visibleFeedback: MaterialProcessFeedback | null = (() => {
        if (processFeedback === null) {
            return null;
        }
        if (processFeedback.kind === "accepted") {
            return isTerminalMaterialStatus(liveStatus)
                ? null
                : processFeedback;
        }
        return liveStatus === processFeedback.status
            ? processFeedback
            : null;
    })();

    async function handleReprocess(): Promise<void> {
        if (processMutation.isPending) {
            return;
        }

        setProcessFeedback(null);
        try {
            await processMutation.mutateAsync();
            setProcessFeedback({ kind: "accepted" });
        } catch (cause) {
            setProcessFeedback({
                kind: "error",
                message: describeMaterialProcessError(cause),
                status: liveStatus,
            });
        }
    }

    useEffect(() => {
        if (polledStatus && polledStatus !== material.status) {
            queryClient.setQueryData<Material[]>(
                materialKeys.list(courseId),
                (current) =>
                    current === undefined
                        ? current
                        : current.map((entry) =>
                              entry.id === material.id
                                  ? { ...entry, status: polledStatus }
                                  : entry,
                          ),
            );
        }
    }, [polledStatus, material.id, material.status, courseId, queryClient]);

    const viewerRegionId = `material-${material.id}-extracted-text`;
    const canReprocess =
        canManage && isTerminalMaterialStatus(liveStatus);
    const showActions =
        liveStatus === "ready" || canReprocess || visibleFeedback !== null;

    return (
        <li className="border-t border-border py-3.5 transition-colors duration-150 first:border-t-0 hover:border-foreground">
            <p className="flex items-baseline justify-between gap-4">
                <time className="font-mono text-[0.8125rem] text-muted-foreground">
                    {formatCourseCreatedDate(material.created_at)}
                </time>
                <MaterialStatusMark status={liveStatus} />
            </p>
            <h3
                dir="auto"
                className="mt-1.5 max-w-[60ch] text-base font-medium leading-[1.4] text-foreground break-words"
            >
                {material.title}
            </h3>
            {liveStatus === "failed" ? (
                <p className="mt-1.5 max-w-[60ch] text-[0.8125rem] leading-[1.6] text-muted-foreground">
                    {MATERIAL_FAILED_COPY}
                </p>
            ) : null}

            {showActions ? (
                <div className="mt-2.5 flex flex-wrap items-center gap-x-5 gap-y-2">
                    {liveStatus === "ready" ? (
                        <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            aria-expanded={viewerOpen}
                            aria-controls={viewerRegionId}
                            onClick={() => setViewerOpen((open) => !open)}
                        >
                            <ChevronDown
                                aria-hidden="true"
                                className={cn(
                                    "size-3.5 transition-transform duration-150",
                                    viewerOpen && "rotate-180",
                                )}
                                data-icon="inline-start"
                            />
                            Extracted text
                        </Button>
                    ) : null}
                    <MaterialProcessControl
                        visible={canReprocess}
                        pending={processMutation.isPending}
                        feedback={visibleFeedback}
                        onRequest={() => void handleReprocess()}
                    />
                </div>
            ) : null}

            {/* The viewer exists ONLY while open on a ready material —
                the lazy gate itself. A reprocess that moves the
                material back into the pipeline unmounts it (extracted
                text is never rendered for queued/processing/failed
                materials); if it becomes ready again, it remounts
                fresh (a reprocess invalidated the cached pages). */}
            {viewerOpen && liveStatus === "ready" ? (
                <MaterialTextViewer
                    material={material}
                    regionId={viewerRegionId}
                />
            ) : null}
        </li>
    );
}

/**
 * The status presentation (roadmap Table 9): the contract's own
 * vocabulary as text — Queued / Processing / Ready / Failed — in the
 * mono data register, with a small geometric indicator whose color
 * REINFORCES the label but never carries it alone. No percentages,
 * phases, or ETAs are fabricated (the API exposes none), and the
 * processing indicator's gentle pulse is the only motion (covered
 * by the token layer's prefers-reduced-motion guard).
 */
function MaterialStatusMark({ status }: { status: MaterialStatus }) {
    return (
        <span
            className="inline-flex items-center gap-1.5 font-mono text-[0.6875rem] font-medium uppercase tracking-wider"
        >
            <span
                aria-hidden="true"
                className={cn(
                    "size-1.5 shrink-0 rounded-full",
                    status === "pending" && "bg-muted-foreground/50",
                    status === "processing" &&
                        "bg-ring animate-pulse",
                    status === "ready" && "bg-success",
                    status === "failed" && "bg-destructive",
                )}
            />
            <span
                className={cn(
                    status === "pending" && "text-muted-foreground",
                    status === "processing" && "text-foreground",
                    status === "ready" && "text-success",
                    status === "failed" && "text-destructive",
                )}
            >
                {MATERIAL_STATUS_LABELS[status]}
            </span>
        </span>
    );
}
