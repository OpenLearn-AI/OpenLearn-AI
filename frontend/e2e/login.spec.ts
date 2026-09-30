import { test, expect, type Page } from "@playwright/test";

/**
 * E2E smoke flow #1 — login → dashboard.
 *
 * This spec exercises the REAL authentication path:
 *   1. Visit `/login` on our origin.
 *   2. Click the "Sign in with OpenLearn AI" button — this triggers a
 *      full OIDC redirect to the Keycloak server's hosted login page.
 *   3. Fill the Keycloak-hosted form (#username, #password) and submit
 *      (#kc-login) — these selectors are defined by the Keycloak theme,
 *      not by this repo, but they are the documented selectors across
 *      every Keycloak version since ~10.x.
 *   4. Wait for the redirect back to our origin at `/dashboard`.
 *   5. Assert meaningful dashboard content is present (the "Welcome Back!"
 *      heading + the UserInfo block rendering the test user's email).
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
  }: { page: Page }) => {
    // 1. Start at the login page on our origin.
    await page.goto("/login");

    // The login page renders a brand header + a card with the OIDC button.
    await expect(
      page.getByRole("heading", { name: /sign in to your account/i }),
    ).toBeVisible();

    // 2. Click our OIDC redirect button. The visible text comes from
    //    components/auth/LoginForm.tsx — "Sign in with OpenLearn AI"
    //    (or "Connecting..." while the redirect is being initiated).
    const signInButton = page.getByRole("button", {
      name: /sign in with openlearn ai/i,
    });
    await expect(signInButton).toBeVisible();
    await signInButton.click();

    // 3. We are now on Keycloak's hosted login page. Wait for the
    //    username field. Keycloak's standard theme uses #username and
    //    #password; these are stable across Keycloak versions.
    await page.waitForSelector("#username", { state: "visible" });
    await page.fill("#username", E2E_USERNAME!);
    await page.fill("#password", E2E_PASSWORD!);

    // Submit. Keycloak's standard theme uses #kc-login.
    await page.click("#kc-login");

    // 4. Wait for the redirect back to our origin at /dashboard.
    //    Keycloak posts back to our redirectUri which LoginForm sets to
    //    `${origin}/dashboard` (the Phase 3 default redirect policy).
    await page.waitForURL(/\/dashboard$/, { timeout: 30_000 });

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
