import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E configuration — Phase 6 Batch 2 (Batch 5.1 doc refresh).
 *
 * Scope: four spec files exercising the real UI against a running Next.js
 * frontend + real Keycloak + real backend — the three smoke flows (login →
 * dashboard, the instructor course CRUD loop, the profile round trip), the
 * Batch 4.1 onboarding suite, and (since Batch 5.1) the role-aware
 * affordance-visibility checks. Each of the three smoke flows also ends
 * with an IN-SPEC compact-viewport block (360×800) asserting the
 * responsive shell contract on the same session — deliberately NOT a
 * second Playwright project: a full compact re-run would double the
 * serial real-Keycloak logins, and the three specs that create their page
 * via `browser.newPage()` in `beforeAll` would bypass a project viewport
 * anyway, producing a misleading matrix.
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
 *   - Chromium-only project: the flows don't need cross-browser coverage;
 *     the existing Storybook browser tests already cover the
 *     accessibility/browser-matrix concern via @vitest/browser-playwright.
 *     The compact-viewport states are covered in-spec (see above), so the
 *     project count stays at one.
 *   - Retries: 2 on CI (transient flake absorption), 0 locally so a
 *     developer sees the real failure on the first run.
 *   - Trace: `retain-on-failure` keeps artifacts only when a test fails,
 *     avoiding the storage cost of always-on traces.
 *
 * Required environment (consumed by the specs, NOT by this config):
 *   - E2E_USERNAME            — student test user username (login,
 *                               profile, onboarding, and the negative
 *                               affordance-visibility flow)
 *   - E2E_PASSWORD            — student test user password
 *   - E2E_INSTRUCTOR_USERNAME — instructor test account username (the
 *                               course CRUD flow; its hub affordances are
 *                               instructor-gated since Batch 4.3 — the
 *                               flow skips with an explicit message when
 *                               this pair is absent)
 *   - E2E_INSTRUCTOR_PASSWORD — instructor test account password
 *   - NEXT_PUBLIC_API_URL     — Backend API base URL (must be reachable
 *                               from the Playwright runner)
 *   - NEXT_PUBLIC_KEYCLOAK_URL / REALM / CLIENT_ID
 *
 * Auth flow: visiting `/login` auto-initiates the existing OIDC login
 * (the entry bridge — corrective follow-up §C.4) and triggers a full
 * redirect to Keycloak's hosted login page. The specs fill the
 * Keycloak form (#username, #password, #kc-login), then wait for the
 * redirect back to our origin.
 */
const isCI = !!process.env.CI;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false, // Keycloak sessions + course CRUD mutate shared state
  forbidOnly: isCI, // `test.only` is a review-time footgun on CI
  retries: isCI ? 2 : 0,
  workers: 1, // serial — the specs share Keycloak sessions and may
  // mutate the same courses/profile data. Parallelism would race.
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
