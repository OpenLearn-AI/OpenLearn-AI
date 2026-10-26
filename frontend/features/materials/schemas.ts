import { z } from "zod";

/**
 * Material domain schemas (Batch 4.3) — Zod as the single source of
 * truth, cross-checked against `docs/openapi.json` (the CI-guarded
 * backend contract) and `backend/app/schemas/material.py`:
 *
 * - `materialResponseSchema` — `GET /v1/courses/{id}/materials` rows:
 *   `{id, course_id, s3_key, title, status, uploaded_by, created_at}`.
 * - `uploadUrlCreateSchema` / `uploadUrlResponseSchema` — the
 *   presigned-POST request `{filename, title}` and the response
 *   `{course_id, title, s3_key, upload_url, upload_fields,
 *   max_size_bytes, expires_in}`. The response documents a
 *   multipart/form-data POST upload (the signed fields first, the
 *   file as the LAST field named `file`) — NOT a PUT; the flow
 *   helpers in `./flow.ts` build exactly that request.
 * - `materialCreateSchema` / `materialAcceptedResponseSchema` — the
 *   registration request `{s3_key, title}` and the 202 response
 *   `{material_id, status, job_id|null}`. `job_id` is correlation
 *   data for logs ONLY (the status endpoint keys on material_id);
 *   Week 9 dedup returns the EXISTING material with `job_id: null`
 *   and its current status, whatever that status is.
 * - `materialStatusResponseSchema` — `GET /v1/materials/{id}/status`:
 *   `{material_id, status}`.
 *
 * The material `status` is the four-value contract literal
 * (pending | processing | ready | failed) — the frontend's entire
 * window into the pipeline (roadmap §10).
 */

const uuidString = z.string().uuid();

/** The contract's complete, closed status set — nothing else renders. */
export const MATERIAL_STATUSES = [
    "pending",
    "processing",
    "ready",
    "failed",
] as const;

export type MaterialStatus = (typeof MATERIAL_STATUSES)[number];

export const materialStatusSchema = z.enum(MATERIAL_STATUSES);

export const materialResponseSchema = z.object({
    id: uuidString,
    course_id: uuidString,
    s3_key: z.string().min(1).max(1024),
    title: z.string().min(1).max(255),
    status: materialStatusSchema,
    uploaded_by: uuidString,
    created_at: z.string().datetime({ offset: true }),
});

export type Material = z.infer<typeof materialResponseSchema>;

/** The presigned-URL request body (both fields 1–255 chars). */
export const uploadUrlCreateSchema = z.object({
    filename: z.string().min(1).max(255),
    title: z.string().min(1).max(255),
});

export type UploadUrlCreate = z.infer<typeof uploadUrlCreateSchema>;

export const uploadUrlResponseSchema = z.object({
    course_id: uuidString,
    title: z.string().min(1).max(255),
    s3_key: z.string().min(1).max(1024),
    upload_url: z.string().url(),
    upload_fields: z.record(z.string(), z.string()),
    max_size_bytes: z.number().int().positive(),
    expires_in: z.number().int().positive(),
});

export type UploadUrlResponse = z.infer<typeof uploadUrlResponseSchema>;

/** The registration request body (the s3_key from the upload-url flow). */
export const materialCreateSchema = z.object({
    s3_key: z.string().min(1).max(1024),
    title: z.string().min(1).max(255),
});

export type MaterialCreate = z.infer<typeof materialCreateSchema>;

export const materialAcceptedResponseSchema = z.object({
    material_id: uuidString,
    status: materialStatusSchema,
    job_id: z.string().nullable(),
});

export type MaterialAcceptedResponse = z.infer<
    typeof materialAcceptedResponseSchema
>;

export const materialStatusResponseSchema = z.object({
    material_id: uuidString,
    status: materialStatusSchema,
});

export type MaterialStatusResponse = z.infer<
    typeof materialStatusResponseSchema
>;
