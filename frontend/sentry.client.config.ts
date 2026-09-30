import * as Sentry from "@sentry/nextjs";

import { config } from "@/lib/config";

/**
 * Client-side Sentry initialization (Phase 6 Batch 3 / D14).
 *
 * Environment labeling:
 *   Reads `config.sentryEnvironment` (from `NEXT_PUBLIC_SENTRY_ENVIRONMENT`
 *   via lib/config.ts). This is a deterministic deployment label — one of
 *   "development", "staging", "production" — replacing the previous
 *   `process.env.NODE_ENV || "staging"` heuristic which conflated staging
 *   and production (both Dockerfile deployments set `NODE_ENV=production`).
 *
 * Sampling policy (environment-aware):
 *   - development: 1.0  (capture everything — local dev noise is signal)
 *   - staging:     0.5  (sample half — staging load is moderate)
 *   - production:  0.1  (sample 10% — production load is highest)
 *
 * These are implementation defaults; the architecture decision (D14)
 * intentionally leaves rates configurable. Adjust at the deployment env
 * level if a different tradeoff is needed.
 *
 * DSN:
 *   Reads `config.sentryDsn` (from `NEXT_PUBLIC_SENTRY_DSN`). When the
 *   DSN is empty (the .env.example default), `Sentry.init` is called
 *   with `dsn: undefined`, which makes the SDK a no-op — local dev
 *   works without a Sentry project configured.
 */
const tracesSampleRateByEnvironment: Record<string, number> = {
    development: 1.0,
    staging: 0.5,
    production: 0.1,
};

Sentry.init({
    dsn: config.sentryDsn ?? undefined,
    environment: config.sentryEnvironment,
    tracesSampleRate:
        tracesSampleRateByEnvironment[config.sentryEnvironment] ?? 1.0,
});
