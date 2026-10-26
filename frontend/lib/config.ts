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
 *
 * Phase 6 Batch 3 (D14): added `NEXT_PUBLIC_SENTRY_ENVIRONMENT` so the
 * client-side Sentry SDK can label events with a deterministic
 * deployment environment (development / staging / production). This
 * replaces the previous `process.env.NODE_ENV || "staging"` heuristic
 * which conflated staging and production — both Dockerfile deployments
 * set `NODE_ENV=production`.
 */

const httpUrl = z.url({ protocol: /^https?$/ });

const nonEmptyString = z
    .string()
    .transform((value) => value.trim())
    .pipe(z.string().min(1, "must be a non-empty string"));

/**
 * Sentry deployment environment label.
 *
 * Allowed values: "development", "staging", "production". Anything else
 * (including the empty string) falls back to "development" — fail-safe
 * toward the noisier environment so a misconfigured production build
 * is more visible in Sentry, not less.
 */
const sentryEnvironmentSchema = z
    .string()
    .optional()
    .transform((value) => value?.trim())
    .pipe(
        z.enum(["development", "staging", "production"]).default("development"),
    );

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
    NEXT_PUBLIC_SENTRY_ENVIRONMENT: sentryEnvironmentSchema,
});

const parsedEnv = clientEnvSchema.safeParse({
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_KEYCLOAK_URL: process.env.NEXT_PUBLIC_KEYCLOAK_URL,
    NEXT_PUBLIC_KEYCLOAK_REALM: process.env.NEXT_PUBLIC_KEYCLOAK_REALM,
    NEXT_PUBLIC_KEYCLOAK_CLIENT_ID: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID,
    NEXT_PUBLIC_SENTRY_DSN: process.env.NEXT_PUBLIC_SENTRY_DSN,
    NEXT_PUBLIC_SENTRY_ENVIRONMENT: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT,
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
    sentryEnvironment: parsedEnv.data.NEXT_PUBLIC_SENTRY_ENVIRONMENT,
};
