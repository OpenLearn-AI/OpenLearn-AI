import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E configuration — Phase 6 Batch 2.
 *
 * Scope: three smoke flows (login → dashboard, course CRUD, profile round
 * trip) that exercise the real UI against a running Next.js frontend + real
 * Keycloak + real backend.
 *
 * Design notes:
 *   - `baseURL` is configurable via PLAYWRIGHT_BASE_URL so the same suite
 *     runs against a local `next dev`, a local container, or staging
 *     (e.g. https://openlearn-web-staging.duckdns.org). Defaults to
 *     http://localhost:3000 which is the Next.js dev server port.
 *   - No `webServer` block: this repo's local-run path already documents
 *     `scripts/setup-dev.sh` + `npm run dev`. Auto-starting a server here
 *     would mask the "backend/Keycloak must be running" prerequisite and
 *     silently produce red tests when the dependencies are absent. The
 *     E2E workflow (`.github/workflows/e2e.yml`) instead documents the
 *     required environment.
 *   - Chromium-only project: the three smoke flows don't need cross-browser
 *     coverage; the existing Storybook browser tests already cover the
 *     accessibility/browser-matrix concern via @vitest/browser-playwright.
 *   - Retries: 2 on CI (transient flake absorption), 0 locally so a
 *     developer sees the real failure on the first run.
 *   - Trace: `retain-on-failure` keeps artifacts only when a test fails,
 *     avoiding the storage cost of always-on traces.
 *
 * Required environment (consumed by the specs, NOT by this config):
 *   - E2E_USERNAME            — Keycloak test user username
 *   - E2E_PASSWORD            — Keycloak test user password
 *   - NEXT_PUBLIC_API_URL     — Backend API base URL (must be reachable
 *                               from the Playwright runner)
 *   - NEXT_PUBLIC_KEYCLOAK_URL / REALM / CLIENT_ID
 *
 * Auth flow: clicking our "Sign in with OpenLearn AI" button triggers a
 * full OIDC redirect to Keycloak's hosted login page. The specs fill the
 * Keycloak form (#username, #password, #kc-login), then wait for the
 * redirect back to our origin.
 */
const isCI = !!process.env.CI;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false, // Keycloak sessions + course CRUD mutate shared state
  forbidOnly: isCI, // `test.only` is a review-time footgun on CI
  retries: isCI ? 2 : 0,
  workers: 1, // serial — the three specs share a Keycloak session and may
  // mutate the same user's courses/profile. Parallelism would race.
  reporter: isCI
    ? [["html", { open: "never" }], ["list"]]
    : "list",

  use: {
    // Configurable so the same suite runs against a local `next dev`,
    // a local container, or staging. Defaults to http://localhost:3000
    // which is the Next.js dev server port.
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000",
    actionTimeout: 10_000,
    navigationTimeout: 30_000,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    // Keycloak OIDC redirects can be slow; don't fail a healthy flow
    // because Keycloak took 5s to render its login form.
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
