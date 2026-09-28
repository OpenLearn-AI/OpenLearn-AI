import { z } from "zod";

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