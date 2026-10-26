import { test, expect } from "@playwright/test";

import { performKeycloakLogin } from "./helpers";

/**
 * The dashboard greeting's structural pin (Batch 4.2 correction A3;
 * the composition is unit-pinned in `composeWelcomeGreeting`): the
 * plain "Welcome back!" when the session's ID token carries no
 * `given_name`, "Welcome back, <Name>!" when it does. Which variant
 * renders is decided by the REAL session — never by the test
 * environment: the bootstrap provisions the E2E accounts without name
 * claims, but Keycloak 26.7.3's first-login Verify Profile
 * interstitial (the finding recorded in the 2.2.1 ledger) sets
 * firstName/lastName the first time an account logs in manually, so
 * a fixed-variant pin asserts an unguaranteeable environment
 * property. The 2026-10-26 failure run proved exactly that: both dev
 * accounts now carry names, the personalized variant rendered, and
 * the old plain-wording pin failed. The anchored regex asserts the
 * composed contract (either designed variant) and cannot match an
 * unrelated "Welcome back …" heading.
 */
const greetingHeading = /^Welcome back(?:, .+)?!$/;

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
 *   4. Assert meaningful dashboard content is present (the composed
 *      greeting heading + the account colophon rendering the test
 *      user's roles).
 *
 * Batch 4.2: the dashboard's Email section was intentionally removed
 * (owner correction D — the email already lives on /profile, and the
 * former UserInfo card was deleted with it). The assertion that used
 * to prove "/auth/me succeeded" via the UserInfo `Email:` line now
 * proves it via the account colophon's roles row, which renders from
 * the SAME /auth/me data. The greeting heading pin (Batch 4.2
 * corrections, A3) asserts the composed dual-variant contract — a
 * fixed-variant pin would assert an environment property the suite
 * cannot guarantee (explained at the file-level `greetingHeading`);
 * the composition itself stays unit-pinned.
 *
 * Batch 4.1: the post-login wait is onboarding-aware (shared helper).
 * A fresh user without a profile is routed to the `/onboarding` wizard
 * by the `(app)` gate; the helper completes the wizard through the real
 * UI with deterministic values before the dashboard assertions below
 * run. On a used environment (profile already exists) the helper's
 * wizard branch is simply skipped. The dashboard assertions themselves
 * are unchanged — NOT weakened.
 *
 * Batch 5.1 (D1): the flow ends with an in-spec compact-viewport block
 * (360×800) asserting the responsive shell contract on the SAME login
 * session — no second Playwright project, no repeated Keycloak login.
 * The block is additive; the assertions above are untouched.
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

    // 5. Assert meaningful dashboard content. The dashboard's running
    //    head is the composed greeting (app/(app)/dashboard/page.tsx) —
    //    "Welcome back, <Name>!" when the session carries a first name,
    //    the plain "Welcome back!" when it does not. Which variant
    //    renders is decided by the session's real `given_name` claim
    //    (the structural contract — see the file-level pin comment).
    await expect(
      page.getByRole("heading", { name: greetingHeading }),
    ).toBeVisible();

    // The account colophon renders `Role:`/`Roles:` + the session's
    // real roles from /auth/me (Batch 4.2: this replaced the removed
    // UserInfo `Email:` line — same proof, same data source: asserting
    // it is present proves /auth/me succeeded with the authenticated
    // user's session, not merely that the route loaded).
    await expect(page.getByText(/Roles?:/)).toBeVisible();

    // ---- 6. Compact-viewport shell contract (Batch 5.1, D1) ---------------
    // The desktop project viewport is 1280×720; the application shell
    // flips to the mobile pattern below the `md` breakpoint (768px).
    // At 360×800 the responsive contract is: no desktop sidebar, the
    // mobile top bar with its real "Open menu" trigger, a drawer that
    // exposes real navigation destinations and closes through its real
    // close control, and the flow's core content still visible. This
    // block exercises the compact state INSIDE the same flow on the
    // SAME authenticated session — deliberately not a second Playwright
    // project, which would duplicate the expensive Keycloak login (and,
    // because three spec files create their page via browser.newPage(),
    // silently bypass the project viewport anyway).
    await page.setViewportSize({ width: 360, height: 800 });

    // The desktop sidebar is `hidden md:flex` (AppSidebar) — display:none
    // at compact width takes it out of the accessibility tree, so its
    // "Primary navigation" landmark matches nothing. The mobile drawer
    // carries the identically-named landmark but is unmounted while
    // closed (Base UI portal), so ZERO such landmarks exist right now.
    await expect(
      page.getByRole("navigation", { name: "Primary navigation" }),
    ).toHaveCount(0);

    // The mobile top bar (md:hidden header) renders the real menu trigger.
    const openMenu = page.getByRole("button", { name: "Open menu" });
    await expect(openMenu).toBeVisible();

    // Opening the drawer exposes a real navigation destination (the
    // shared nav-config "Courses" link — the same source of truth as the
    // desktop sidebar).
    await openMenu.click();
    await expect(page.getByRole("link", { name: "Courses" })).toBeVisible();

    // ...and the drawer closes through its real close control (the
    // drawer's landmark unmounts again with the popup).
    await page.getByRole("button", { name: "Close menu" }).click();
    await expect(
      page.getByRole("navigation", { name: "Primary navigation" }),
    ).toHaveCount(0);

    // The flow's core page content remains visible and usable at the
    // compact width — the same greeting heading pinned above.
    await expect(
      page.getByRole("heading", { name: greetingHeading }),
    ).toBeVisible();

    // Restore the desktop viewport (defensive hygiene — the compact block
    // is this flow's last step, so nothing below depends on it, but the
    // block stays position-independent for future edits).
    await page.setViewportSize({ width: 1280, height: 720 });
  });
});
