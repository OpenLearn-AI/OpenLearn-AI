import { ApiError } from "@/lib/api";
import type { MaterialStatus } from "./schemas";

/**
 * Pure helpers for the material upload flow and status presentation
 * (Batch 4.3). No React, no fetch, no imports beyond the error type —
 * the same module-isolation pattern as `user-identity.ts`, so every
 * rule here is unit-testable without a session or a network.
 *
 * The flow these helpers serve (the existing contract ONLY — roadmap
 * §10, Table 12):
 * 1. `POST /v1/courses/{id}/materials/upload-url` with
 *    `{filename, title}` → the presigned POST target.
 * 2. The browser uploads the file DIRECTLY to storage: a
 *    `multipart/form-data` POST to `upload_url` with every
 *    `upload_fields` entry as a form field, followed by the file as
 *    the LAST field named `file` (the exact order the
 *    `UploadUrlResponse` documents — NOT a PUT).
 * 3. `POST /v1/courses/{id}/materials` with `{s3_key, title}` →
 *    202 `{material_id, status, job_id}`. `job_id` is logged for
 *    correlation and NEVER queried (the status endpoint keys on
 *    material_id).
 */

/** ready and failed are the contract's terminal states — once seen,
 * polling stops (roadmap: "Stop polling when the status reaches a
 * supported terminal state"). */
export function isTerminalMaterialStatus(status: MaterialStatus): boolean {
    return status === "ready" || status === "failed";
}

/**
 * Build the presigned-POST form data: every signed field first, the
 * file LAST under the contract's required `file` field name.
 */
export function buildUploadFormData(
    uploadFields: Record<string, string>,
    file: File,
): FormData {
    const formData = new FormData();

    for (const [key, value] of Object.entries(uploadFields)) {
        formData.append(key, value);
    }

    formData.append("file", file);

    return formData;
}

/**
 * Render a byte size as a compact human-readable amount for the
 * too-large error message (binary units — storage limits are set in
 * powers of 1024).
 */
export function formatByteSize(bytes: number): string {
    if (bytes >= 1024 * 1024) {
        const mebibytes = bytes / (1024 * 1024);
        return `${Number.isInteger(mebibytes) ? mebibytes : mebibytes.toFixed(1)} MB`;
    }
    if (bytes >= 1024) {
        return `${Math.round(bytes / 1024)} KB`;
    }
    return `${bytes} bytes`;
}

/** The status label the UI renders — the contract's own vocabulary,
 * presented in the mono data register (never a phase name or
 * percentage: the API exposes none). */
export const MATERIAL_STATUS_LABELS: Record<MaterialStatus, string> = {
    pending: "Queued",
    processing: "Processing",
    ready: "Ready",
    failed: "Failed",
};

/**
 * The honest failure copy (roadmap Table 9): names the PLAUSIBLE
 * cause class the backend's failures actually come from (storage,
 * ingestion, OCR — including quota-blocked scanned PDFs — embedding,
 * persistence) without claiming to know which one occurred — the
 * status endpoint does not expose it. No retry affordance: no retry
 * endpoint is in this batch's scope.
 */
export const MATERIAL_FAILED_COPY =
    "Processing failed. This can happen when a document's content " +
    "cannot be ingested (for example a scanned PDF that needs OCR " +
    "beyond the current quota), when a service limit is hit, or " +
    "when storage fails. The file remains stored with the course.";

/**
 * Map a flow error to honest, user-facing copy. The mapping mirrors
 * the established CourseForm/ProfileForm convention (same 401/403/
 * 404/422 handling, no stack traces, no internal details), plus the
 * material-specific 409/413/429 responses the contract documents.
 */
export function describeMaterialFlowError(error: unknown): string {
    if (error instanceof ApiError) {
        switch (error.status) {
            case 0:
                return (
                    error.message ||
                    "The request could not reach the server."
                );
            case 401:
                // W1: the global 401 recovery clears the query cache
                // and routes to /login; this line only sets the
                // expectation until the redirect.
                return "Your session has expired. Redirecting to sign in...";
            case 403:
                return "You do not have permission to manage materials in this course.";
            case 404:
                return "The course or the uploaded file was not found. If the file was just uploaded, please try again.";
            case 409:
                return error.message ||
                    "The material is already registered or the stored file changed. Refresh the list to see its current state.";
            case 413:
                return error.message ||
                    "The file is larger than the maximum upload size.";
            case 422:
                return "The submitted values are invalid.";
            case 429:
                return "Too many requests. Please wait a moment and try again.";
            default:
                return error.message || "The upload could not be completed.";
        }
    }

    if (error instanceof Error) {
        return error.message;
    }

    return "The upload could not be completed.";
}
