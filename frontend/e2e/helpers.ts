import { expect, type Page } from "@playwright/test";

/**
 * Shared E2E helpers (Batch 4.1).
 *
 * Batch 4.1 adds a first-login onboarding gate to every protected
 * route: a user without a profile (the backend's 404 for
 * `GET /v1/users/me`) is routed to `/onboarding` from any `(app)` route
 * except `/profile`, and only returns to the application after a
 * confirmed profile save. The previously duplicated
 * `performKeycloakLogin` helpers therefore become onboarding-aware, and
 * the wizard-completion routine lives here so the login, courses, and
 * onboarding specs share ONE definition of "post-login settles on the
 * dashboard".
 *
 * The helpers keep the real Keycloak OIDC flow exactly as before
 * (`/login` → "Sign in with OpenLearn AI" → Keycloak's hosted form
 * #username/#password/#kc-login → redirect back to our origin); the
 * only addition is that the post-login wait accepts BOTH landing
 * routes (`/dashboard` directly for users who already have a profile,
 * `/onboarding` for fresh users) and completes the wizard when it
 * appears.
 *
 * The wizard is completed through the real UI with deterministic
 * values — no auth state is mocked anywhere in this file.
 */

/** Deterministic values the shared helper writes into the wizard. */
export const ONBOARDING_WIZARD_VALUES = {
    educationLevel: "E2E Onboarding Education",
    major: "E2E Onboarding Major",
    dailyAvailableMinutes: "90",
    preferredLanguage: "en",
} as const;

/**
 * Complete the onboarding wizard through the real UI. Assumes the
 * browser is already on `/onboarding` (step 1 visible).
 *
 * `expectLanding` is the URL pattern the wizard should land on after
 * the confirmed save — `/dashboard` by default, or the validated
 * original destination (e.g. `/courses`) when the gate carried a
 * `redirectedFrom` value through.
 */
export async function completeOnboardingWizard(
    page: Page,
    values: {
        educationLevel: string;
        major: string;
        dailyAvailableMinutes: string;
        preferredLanguage: string;
    } = ONBOARDING_WIZARD_VALUES,
    expectLanding: RegExp = /\/dashboard/,
): Promise<void> {
    // Step 1 — About your studies.
    await expect(page.getByText(/Step 1 of 3/)).toBeVisible();
    await page.getByLabel("Education Level").fill(values.educationLevel);
    await page.getByLabel("Major").fill(values.major);
    await page.getByRole("button", { name: "Continue" }).click();

    // Step 2 — Your study rhythm.
    await expect(page.getByText(/Step 2 of 3/)).toBeVisible();
    const minutes = page.getByLabel("Daily Available Minutes");
    await minutes.fill(values.dailyAvailableMinutes);
    await page
        .getByLabel("Preferred Language")
        .selectOption(values.preferredLanguage);
    await page.getByRole("button", { name: "Continue" }).click();

    // Step 3 — Optional details & review. The shared helper skips the
    // two optional fields (they may remain empty per the profile
    // contract) and saves the accumulated payload with ONE PUT.
    await expect(page.getByText(/Step 3 of 3/)).toBeVisible();
    await page.getByRole("button", { name: "Save profile" }).click();

    // The wizard navigates only after the API confirms the save; the
    // destination is the validated original target or `/dashboard`.
    await page.waitForURL(expectLanding, { timeout: 30_000 });
}

/**
 * Perform the real Keycloak OIDC login via our login page and settle
 * the post-login state, onboarding-aware.
 *
 * Legacy behavior (2.2.1 fix, preserved): wait for the sign-in button's
 * ENABLED state before clicking — a click processed during the
 * non-silent `check-sso` round trip is destroyed with its document.
 *
 * Batch 4.1 addition: after the Keycloak redirect the browser lands on
 * `/dashboard` (profile exists) or `/onboarding` (fresh user routed by
 * the gate). When the wizard appears it is completed with
 * deterministic values, so every caller — and the assertions in the
 * specs — can rely on the session ending on `/dashboard` with an
 * existing profile.
 */
export async function performKeycloakLogin(
    page: Page,
    username: string,
    password: string,
): Promise<void> {
    await page.goto("/login");

    const signInButton = page.getByRole("button", {
        name: /sign in with openlearn ai/i,
    });
    await expect(signInButton).toBeEnabled({ timeout: 30_000 });
    await signInButton.click();

    await page.waitForSelector("#username", { state: "visible" });
    await page.fill("#username", username);
    await page.fill("#password", password);
    await page.click("#kc-login");

    // Post-login: the gate sends profile-less users to the wizard.
    await page.waitForURL(/\/(dashboard|onboarding)/, { timeout: 30_000 });

    if (page.url().includes("/onboarding")) {
        await completeOnboardingWizard(page);
    }

    // The OIDC redirectUri is `${origin}/dashboard` (the Phase 3
    // default) and the wizard returns to `/dashboard`, so this wait is
    // the same settle point the specs have always relied on.
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 });
}
