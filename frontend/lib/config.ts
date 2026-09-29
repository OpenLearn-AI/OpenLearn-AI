import { z } from "zod";

/**
 * Central frontend configuration (D15).
 *
 * Single source of truth for the client-side NEXT_PUBLIC_* variables.
 * Consumers must import `config` from this module instead of reading
 * process.env directly.
 *
 * NEXT_PUBLIC_* values are statically inlined into the client bundle at
 * build time, so they must be present when `next build` runs (see
 * frontend/Dockerfile and frontend/.env.example).
 */

const httpUrl = z.url({ protocol: /^https?$/ });

const nonEmptyString = z
    .string()
    .transform((value) => value.trim())
    .pipe(z.string().min(1, "must be a non-empty string"));

const clientEnvSchema = z.object({
    NEXT_PUBLIC_API_URL: httpUrl,
    NEXT_PUBLIC_KEYCLOAK_URL: httpUrl,
    NEXT_PUBLIC_KEYCLOAK_REALM: nonEmptyString,
    NEXT_PUBLIC_KEYCLOAK_CLIENT_ID: nonEmptyString,
    NEXT_PUBLIC_SENTRY_DSN: z
        .string()
        .optional()
        .transform((value) => {
            const trimmed = value?.trim();
            return trimmed ? trimmed : null;
        }),
});

const parsedEnv = clientEnvSchema.safeParse({
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_KEYCLOAK_URL: process.env.NEXT_PUBLIC_KEYCLOAK_URL,
    NEXT_PUBLIC_KEYCLOAK_REALM: process.env.NEXT_PUBLIC_KEYCLOAK_REALM,
    NEXT_PUBLIC_KEYCLOAK_CLIENT_ID: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID,
    NEXT_PUBLIC_SENTRY_DSN: process.env.NEXT_PUBLIC_SENTRY_DSN,
});

if (!parsedEnv.success) {
    const problems = parsedEnv.error.issues
        .map((issue) => `  - ${issue.path.join(".")}: ${issue.message}`)
        .join("\n");

    throw new Error(
        "Invalid frontend configuration. Fix the following environment variables:\n" +
            problems +
            "\nNEXT_PUBLIC_* values are client-side configuration and must be set at build time (see frontend/.env.example)."
    );
}

export const config = {
    apiUrl: parsedEnv.data.NEXT_PUBLIC_API_URL,
    keycloak: {
        url: parsedEnv.data.NEXT_PUBLIC_KEYCLOAK_URL,
        realm: parsedEnv.data.NEXT_PUBLIC_KEYCLOAK_REALM,
        clientId: parsedEnv.data.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID,
    },
    sentryDsn: parsedEnv.data.NEXT_PUBLIC_SENTRY_DSN,
};
