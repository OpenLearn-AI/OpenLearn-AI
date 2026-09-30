import { z } from "zod";

/**
 * Profile domain schemas (D4 — Zod as the single source of truth).
 *
 * Two schemas live here:
 *   - `profileResponseSchema` describes the API response from
 *     `GET /v1/users/me` and `PUT /v1/users/me` (upsert). `Profile`
 *     is `z.infer<typeof profileResponseSchema>`.
 *   - `profileSchema` validates the form payload used by `PUT /v1/users/me`.
 *     `ProfileFormValues` is `z.infer<typeof profileSchema>` and is the
 *     request body type.
 *
 * Cross-checked against `backend/app/schemas/profile.py`:
 * `ProfileResponse` (id, user_id, education_level, major,
 * preferred_language, university, learning_style_vark,
 * daily_available_minutes).
 */

const uuidString = z.string().uuid();

export const profileResponseSchema = z.object({
    id: uuidString,
    user_id: uuidString,
    education_level: z.string(),
    major: z.string(),
    preferred_language: z.string(),
    university: z.string().nullable(),
    learning_style_vark: z.string().nullable(),
    daily_available_minutes: z.number().int(),
});

export type Profile = z.infer<typeof profileResponseSchema>;

export const profileSchema = z.object({
    education_level: z
        .string()
        .min(1, "Education level is required")
        .max(50, "Education level must be 50 characters or less"),

    major: z
        .string()
        .min(1, "Major is required")
        .max(255, "Major must be 255 characters or less"),

    preferred_language: z.enum(["en", "ar"], {
        message: "Preferred language must be English or Arabic",
    }),

    university: z
        .string()
        .min(1, "University must not be empty")
        .max(255, "University must be 255 characters or less")
        .nullable()
        .optional(),

    learning_style_vark: z
        .string()
        .min(1, "Learning style must not be empty")
        .max(20, "Learning style must be 20 characters or less")
        .nullable()
        .optional(),

    daily_available_minutes: z
        .number()
        .int("Daily available minutes must be an integer")
        .min(1, "Daily available minutes must be at least 1")
        .max(1440, "Daily available minutes must be 1440 or less"),
});

export type ProfileFormValues = z.infer<typeof profileSchema>;