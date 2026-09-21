import { z } from "zod";

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