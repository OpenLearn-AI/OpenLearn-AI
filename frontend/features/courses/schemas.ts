import { z } from "zod";

/**
 * Course domain schemas (D4 — Zod as the single source of truth).
 *
 * Two schemas live here:
 *   - `courseResponseSchema` describes the API response shape from
 *     `GET /v1/courses` and `GET /v1/courses/{id}` (and the response
 *     of POST/PUT). `Course` is `z.infer<typeof courseResponseSchema>`.
 *   - `courseSchema` validates the form payload used by POST/PUT
 *     (title + optional nullable description). `CourseFormValues` is
 *     `z.infer<typeof courseSchema>` and is the request body type.
 *
 * The response schema is checked at the API boundary by `apiFetch`;
 * the form schema is checked by `CourseForm` before submission.
 */

const uuidString = z.string().uuid();

export const courseResponseSchema = z.object({
    id: uuidString,
    owner_id: uuidString,
    title: z.string().min(1).max(255),
    description: z.string().nullable(),
    created_at: z.string().datetime({ offset: true }),
});

export type Course = z.infer<typeof courseResponseSchema>;

export const courseSchema = z.object({
    title: z
        .string()
        .min(1, "Title is required")
        .max(255, "Title must be 255 characters or less"),

    description: z
        .string()
        .min(1, "Description must not be empty")
        .nullable()
        .optional(),
});

export type CourseFormValues = z.infer<typeof courseSchema>;
