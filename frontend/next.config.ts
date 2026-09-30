import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs/config";

/**
 * Plain Next.js config — Phase 0–5 options preserved unchanged.
 *
 * `output: "standalone"` is required by the production Dockerfile
 * (frontend/Dockerfile:41 copies `.next/standalone` into the runner
 * image). Do not drop it.
 */
const nextConfig: NextConfig = {
  output: "standalone",
};

/**
 * Sentry build-time wiring (Phase 6 Batch 3, D14).
 *
 * What this does:
 *   - Registers Sentry's instrumentation hook + build-time plugin so
 *     production stack traces can be source-mapped.
 *   - Configures source-map upload to Sentry when build credentials are
 *     available.
 *
 * Credentials strategy (NO hardcoded secrets):
 *   - `SENTRY_AUTH_TOKEN` — read by the SDK from the environment at build
 *     time. NEVER committed. Supplied via the build environment (CI
 *     secret or local dev's .env.local). This is the Pod D external
 *     dependency documented in the roadmap.
 *   - `SENTRY_ORG` and `SENTRY_PROJECT` — read by the SDK from the
 *     environment at build time. Non-secret slugs; can be committed in
 *     .env.example defaults but MUST be set to real values for actual
 *     upload to occur.
 *
 * Local development behavior:
 *   - When `SENTRY_AUTH_TOKEN` is absent, the Sentry SDK's bundler
 *     plugin gracefully skips source-map upload — `npm run build` and
 *     `npm run dev` continue to work without Sentry credentials.
 *   - This is the official behavior of @sentry/nextjs v10's
 *     `withSentryConfig` — the plugin checks for the token at build
 *     time and only uploads when one is present.
 *
 * Source-map strategy:
 *   - `deleteSourcemapsAfterUpload: true` (SDK default) — keeps source
 *     maps out of the deployed bundle after upload, so they don't ship
 *     to end users.
 *   - No custom `assets`/`ignore` globs — the SDK's default detection
 *     (`.next/static/**`) matches the Next.js standalone build layout.
 *
 * Release strategy:
 *   - The SDK auto-detects the release from the git HEAD SHA when
 *     available. No explicit `release.name` is set — the default
 *     behavior is correct for the Vercel/GHCR deployment pattern.
 */
export default withSentryConfig(nextConfig, {
  // Do not print noisy Sentry build logs unless explicitly debugging.
  silent: true,

  // Source-map upload configuration. The SDK reads `SENTRY_AUTH_TOKEN`,
  // `SENTRY_ORG`, and `SENTRY_PROJECT` from the environment; we do not
  // pass them explicitly so they cannot leak into the build artifact.
  sourcemaps: {
    // Delete source maps from the build output after upload so they
    // don't ship to end users. This is the SDK default; setting it
    // explicitly documents the intent.
    deleteSourcemapsAfterUpload: true,
  },

  // Hide the noisy "no Sentry auth token found, skipping upload" tree
  // of warnings during local dev builds where no token is present.
  // The SDK already degrades gracefully; this just suppresses the
  // verbose output so local builds stay clean.
  // (No additional options — see @sentry/nextjs v10 docs.)
});
