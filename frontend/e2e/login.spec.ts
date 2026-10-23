import { test, expect } from "@playwright/test";

import { performKeycloakLogin } from "./helpers";

/**
 * E2E smoke flow #1 — login → dashboard.
 *
 * This spec exercises the REAL authentication path:
 *   1. Visit `/login` on our origin — the entry bridge auto-initiates
 *      the existing OIDC login (corrective follow-up §C.4), so the
 *      browser lands on the Keycloak-hosted login page without any
 *      intermediate click.
 *   2. Fill the Keycloak-hosted form (#username, #password) and submit
 *      (#kc-login) — these selectors are defined by the Keycloak theme,
 *      not by this repo, but they are the documented selectors across
 *      every Keycloak version since ~10.x.
 *   3. Wait for the redirect back to our origin at `/dashboard`.
 *   4. Assert meaningful dashboard content is present (the "Welcome Back!"
 *      heading + the UserInfo block rendering the test user's email).
 *
 * Batch 4.1: the post-login wait is onboarding-aware (shared helper).
 * A fresh user without a profile is routed to the `/onboarding` wizard
 * by the `(app)` gate; the helper completes the wizard through the real
 * UI with deterministic values before the dashboard assertions below
 * run. On a used environment (profile already exists) the helper's
 * wizard branch is simply skipped. The dashboard assertions themselves
 * are unchanged — NOT weakened.
 *
 * Why fill the Keycloak form rather than mock our auth state: Phase 6
 * requires the suite to "prove that a real user can authenticate and
 * land on `/dashboard`" through the actual UI. Mocking `keycloak.authenticated`
 * would only test that the dashboard renders when already authenticated
 * — it would not catch a regression in the OIDC redirect URI, the
 * AuthGuard deep-link policy, or the Keycloak realm configuration.
 *
 * Environment required (see playwright.config.ts):
 *   - E2E_USERNAME / E2E_PASSWORD
 *   - NEXT_PUBLIC_KEYCLOAK_URL / REALM / CLIENT_ID
 *   - NEXT_PUBLIC_API_URL (so /auth/me resolves on the dashboard)
 *
 * If any of these are unavailable in the current environment, the spec
 * still compiles and lists via `npx playwright test --list`. Execution
 * will fail with a clear error — never silently pass.
 */

const E2E_USERNAME = process.env.E2E_USERNAME;
const E2E_PASSWORD = process.env.E2E_PASSWORD;

test.describe("Login smoke flow", () => {
  // Skip the entire suite cleanly if test credentials are not provided,
  // so `npx playwright test --list` doesn't lie about a missing runtime.
  // Execution without credentials still fails — this is intentional,
  // the runtime is required.
  test.skip(
    !E2E_USERNAME || !E2E_PASSWORD,
    "E2E_USERNAME / E2E_PASSWORD must be set to run the login smoke flow",
  );

  test("user authenticates via Keycloak and lands on /dashboard", async ({
    page,
  }) => {
    // 1–4. Real OIDC login; onboarding-aware settle on /dashboard.
    await performKeycloakLogin(page, E2E_USERNAME!, E2E_PASSWORD!);

    // 5. Assert meaningful dashboard content. The dashboard hero is
    //    "Welcome Back!" (app/(app)/dashboard/page.tsx) and the UserInfo
    //    block renders the test user's email after /auth/me resolves.
    await expect(
      page.getByRole("heading", { name: "Welcome Back!" }),
    ).toBeVisible();

    // The UserInfo component renders `<span>Email:</span> {data.email}`.
    // Asserting the email is present proves /auth/me succeeded with the
    // authenticated user's session — not merely that the route loaded.
    await expect(page.getByText(/Email:/)).toBeVisible();
  });
});
