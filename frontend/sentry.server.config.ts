import * as Sentry from "@sentry/nextjs";

/**
 * Server-side Sentry initialization (Phase 6 Batch 3 / D14).
 *
 * Environment labeling:
 *   Reads `SENTRY_ENVIRONMENT` from the runtime environment. This is the
 *   server-side counterpart to the client's `NEXT_PUBLIC_SENTRY_ENVIRONMENT`
 *   — both must be set to the same value in deployment (e.g. "staging"
 *   in the staging Docker Compose, "production" in production). The
 *   client var is build-time-inlined into the browser bundle; the server
 *   var is read at runtime by the Node server (matches the existing
 *   `SENTRY_DSN` pattern used by `infra/docker-compose.staging.yml`).
 *
 *   This replaces the previous `process.env.NODE_ENV || "staging"`
 *   heuristic which conflated staging and production — both Dockerfile
 *   deployments set `NODE_ENV=production` in the runner stage, so the
 *   old code labeled every deployment as "production".
 *
 * Sampling policy (environment-aware, mirrors the client):
 *   - development: 1.0  (capture everything)
 *   - staging:     0.5  (sample half)
 *   - production:  0.1  (sample 10%)
 *
 * DSN:
 *   Reads `SENTRY_DSN` directly from the runtime environment. This is
 *   the established server-side convention (matches the backend pattern
 *   in `backend/app/observability.py:16`). It is injected at runtime by
 *   the staging Docker Compose (`infra/docker-compose.staging.yml:214`)
 *   and would be injected similarly in production.
 */

/**
 * Resolve the Sentry environment label deterministically.
 *
 * Falls back to "development" when unset — fail-safe toward the noisier
 * environment so a misconfigured production deployment is more visible
 * in Sentry, not less.
 */
function resolveSentryEnvironment(): string {
    const env = process.env.SENTRY_ENVIRONMENT?.trim();
    if (env === "development" || env === "staging" || env === "production") {
        return env;
    }
    return "development";
}

const tracesSampleRateByEnvironment: Record<string, number> = {
    development: 1.0,
    staging: 0.5,
    production: 0.1,
};

const environment = resolveSentryEnvironment();

Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment,
    tracesSampleRate: tracesSampleRateByEnvironment[environment] ?? 1.0,
});
