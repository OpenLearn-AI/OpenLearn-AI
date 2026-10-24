import { expect, type Page } from "@playwright/test";

/**
 * Shared E2E helpers (Batch 4.1; corrective follow-up revision).
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
 * Corrective follow-up: `/login` is now a DIRECT bridge to Keycloak —
 * arriving there auto-initiates the existing OIDC login once per tab
 * (the hosted form appears without any intermediate click; the manual
 * "Sign in with OpenLearn AI" button remains for return-after-attempt
 * and error arrivals). The helpers keep the real Keycloak OIDC flow
 * (`/login` → Keycloak's hosted form #username/#password/#kc-login →
 * redirect back to our origin) and complete the wizard through the real
 * UI with deterministic values — no auth state is mocked anywhere in
 * this file.
 *
 * Batch 4.2: education level is entered through stage tiles (a named
 * stage commits directly; a custom value goes through the uncovered
 * "Other" free-text input). The finite, contract-backed choices remain
 * single-select tiles: the minute presets map onto the integer
 * `daily_available_minutes` (any 1-1440 value still goes through the
 * custom input), and the `preferred_language` enum maps to
 * English/العربية tiles. The optional VARK learning-style field uses a
 * genuine multi-select toggle group (the contract field is free text);
 * the shared helper leaves it untouched, and the interim review step
 * no longer exists.
 */

/** Deterministic values the shared helper writes into the wizard. */
export const ONBOARDING_WIZARD_VALUES = {
    educationLevel: "E2E Onboarding Education",
    major: "E2E Onboarding Major",
    // Preset-tile values (the wizard's tiles for daily_available_minutes).
    dailyAvailableMinutes: "60",
    // preferred_language enum value (the "English" tile).
    preferredLanguage: "en",
} as const;

/** Tile labels for the contract values the helper writes. */
const MINUTE_TILE_LABELS: Record<string, string> = {
    "15": "15 min",
    "30": "30 min",
    "60": "1 hour",
    "120": "2 hours",
};

const LANGUAGE_TILE_LABELS: Record<string, string> = {
    en: "English",
    ar: "العربية",
};

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
    options: {
        /** Hook the instant before the final save — e.g. to drop a
            `GET /v1/users/me` interception so the confirmed save and
            the race against the onboarding gate hit the real API. */
        beforeSave?: (page: Page) => Promise<void>;
    } = {},
): Promise<void> {
    // Step 1 — About your studies. Education level is entered through
    // the stage tiles: a canonical stage commits its value directly;
    // any custom value goes through the honest "Other" free-text input.
    await expect(page.getByText(/Step 1 of 3/)).toBeVisible();
    const canonicalStages = ["High school", "Undergraduate", "Postgraduate"];
    const educationGroup = page.getByRole("radiogroup", {
        name: "Education Level",
    });
    if (canonicalStages.includes(values.educationLevel)) {
        await educationGroup
            .getByRole("radio", { name: values.educationLevel })
            .click();
    } else {
        await educationGroup.getByRole("radio", { name: "Other" }).click();
        await page
            .getByLabel("Your education level")
            .fill(values.educationLevel);
    }
    await page.getByLabel("Major").fill(values.major);
    await page.getByRole("button", { name: "Continue" }).click();

    // Step 2 — Your study rhythm: finite, contract-backed choices as
    // single-select tiles.
    await expect(page.getByText(/Step 2 of 3/)).toBeVisible();
    const minutesTile = MINUTE_TILE_LABELS[values.dailyAvailableMinutes];
    if (!minutesTile) {
        throw new Error(
            `No preset tile for dailyAvailableMinutes "${values.dailyAvailableMinutes}" — use 15/30/60/120 or extend MINUTE_TILE_LABELS`,
        );
    }
    await page.getByRole("radio", { name: minutesTile }).click();

    const languageTile = LANGUAGE_TILE_LABELS[values.preferredLanguage];
    if (!languageTile) {
        throw new Error(
            `No tile for preferredLanguage "${values.preferredLanguage}" — use en/ar`,
        );
    }
    await page.getByRole("radio", { name: languageTile }).click();

    await page.getByRole("button", { name: "Continue" }).click();

    // Step 3 — Optional details. The shared helper skips the two
    // optional fields (they may remain empty per the profile contract)
    // and saves the accumulated payload with ONE PUT; the interim
    // review step was removed in the Batch 4.2 redesign.
    await expect(page.getByText(/Step 3 of 3/)).toBeVisible();
    await options.beforeSave?.(page);
    await page.getByRole("button", { name: "Save profile" }).click();

    // The wizard navigates only after the API confirms the save; the
    // destination is the validated original target or `/dashboard`.
    await page.waitForURL(expectLanding, { timeout: 30_000 });
}

/**
 * Perform the real Keycloak OIDC login and settle the post-login state,
 * onboarding-aware.
 *
 * Corrective follow-up: navigating to `/login` IS the login action —
 * the entry bridge auto-initiates the existing Keycloak flow once per
 * tab (loop-guarded: a return arrival shows the explicit button
 * instead of auto-redirecting again), so this helper waits for the
 * hosted form to appear. The post-login wait accepts BOTH landing
 * routes (`/dashboard` directly for users who already have a profile,
 * `/onboarding` for fresh users) and completes the wizard when it
 * appears.
 */
export async function performKeycloakLogin(
    page: Page,
    username: string,
    password: string,
): Promise<void> {
    await page.goto("/login");

    // The bridge's auto-initiation covers auth initialization +
    // Keycloak redirect; the hosted form (#username) is the first
    // Keycloak-owned element on the other side.
    await page.waitForSelector("#username", { state: "visible", timeout: 30_000 });
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
