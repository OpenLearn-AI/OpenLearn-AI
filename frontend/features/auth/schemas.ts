import { z } from "zod";

/**
 * Auth domain schemas (D4 — Zod as the single source of truth).
 *
 * `meResponseSchema` describes the response from `GET /auth/me`.
 * `Me` is `z.infer<typeof meResponseSchema>` and is the single source
 * for the current-user type across the app. The legacy hand-written
 * `features/auth/types.ts` is deleted.
 */

const uuidString = z.string().uuid();

export const meResponseSchema = z.object({
    id: uuidString,
    email: z.string().email(),
    settings: z.record(z.string(), z.unknown()),
    roles: z.array(z.string()),
    keycloak: z.object({
        issuer: z.string(),
        subject: z.string(),
    }),
});

export type Me = z.infer<typeof meResponseSchema>;
