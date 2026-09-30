import { test, expect, type Page } from "@playwright/test";

/**
 * E2E smoke flow #3 — profile create → update round trip.
 *
 * The profile form (components/profile/ProfileForm.tsx) uses a single
 * upsert endpoint: `PUT /v1/users/me` (features/profile/api/useProfileMutation.ts).
 * The backend treats this as upsert, so the same form action handles
 * both initial creation and subsequent updates. The form's submit
 * button label and the page's section heading switch based on whether
 * `useProfile()` returned a profile or `null` (404 from /v1/users/me).
 *
 * This spec is therefore robust to either initial state:
 *   - If the test user has no profile yet → the form button reads
 *     "Create Profile" and the section heading reads "Create Your Profile".
 *   - If the test user already has a profile → the form button reads
 *     "Save Changes" and the section heading reads "Personal Information".
 *
 * In both cases the test:
 *   1. Sets a known-initial set of values.
 *   2. Saves.
 *   3. Verifies the success message + that the page reflects the saved state.
 *   4. Reloads the page to verify the data persisted server-side.
 *   5. Updates to a second set of values.
 *   6. Verifies the update persisted.
 *
 * Selectors use the Field-wrapper labels (Education Level, Major,
 * Preferred Language, University, Learning Style (VARK), Daily Available
 * Minutes) — these are stable across the Phase 5/6 token migration and
 * unaffected by the later UI/UX redesign (which will retain the
 * architectural rails, not the visual presentation).
 *
 * Environment required: same as courses-crud.spec.ts.
 */

const E2E_USERNAME = process.env.E2E_USERNAME;
const E2E_PASSWORD = process.env.E2E_PASSWORD;

const RUN_ID = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const INITIAL = {
  educationLevel: `Initial Edu ${RUN_ID}`,
  major: "Computer Science",
  preferredLanguage: "en",
  university: "OpenLearn Test University",
  learningStyle: "VARK",
  dailyAvailableMinutes: "60",
};
const UPDATED = {
  educationLevel: `Updated Edu ${RUN_ID}`,
  major: "Data Engineering",
  preferredLanguage: "ar",
  university: "OpenLearn Updated University",
  learningStyle: "VARK-V",
  dailyAvailableMinutes: "120",
};

test.describe("Profile round-trip smoke flow", () => {
  test.skip(
    !E2E_USERNAME || !E2E_PASSWORD,
    "E2E_USERNAME / E2E_PASSWORD must be set to run the profile smoke flow",
  );

  let sharedPage: Page;

  test.beforeAll(async ({ browser }: { browser: import("@playwright/test").Browser }) => {
    sharedPage = await browser.newPage();
    await performKeycloakLogin(sharedPage, E2E_USERNAME!, E2E_PASSWORD!);
  });

  test.afterAll(async () => {
    if (sharedPage) {
      await sharedPage.close();
    }
  });

  test("profile data persists across create → reload → update", async () => {
    // ---- 1. Navigate to the profile page -----------------------------------
    await sharedPage.goto("/profile");

    // The profile page renders an <h1> with the user's email (or "User"
    // fallback). Wait for it to confirm the page loaded.
    await expect(sharedPage.getByRole("heading", { level: 1 })).toBeVisible();

    // The left card heading switches based on existing-profile state.
    // Either form of the heading is acceptable as the starting state.
    const createHeading = sharedPage.getByRole("heading", {
      name: "Create Your Profile",
    });
    const updateHeading = sharedPage.getByRole("heading", {
      name: "Personal Information",
    });
    await expect(
      createHeading.or(updateHeading),
    ).toBeVisible();

    // ---- 2. Populate initial values + save ---------------------------------
    await fillProfileForm(sharedPage, INITIAL);

    // The submit button label also switches on create vs. update.
    // Match either variant.
    const submitButton = sharedPage
      .getByRole("button", { name: "Create Profile" })
      .or(sharedPage.getByRole("button", { name: "Save Changes" }));
    await submitButton.click();

    // Success message has role="status" (ProfileForm.tsx renders
    // <p role="status">). Assert it appears — proves the PUT /v1/users/me
    // mutation succeeded.
    await expect(
      sharedPage.getByRole("status"),
    ).toBeVisible({ timeout: 15_000 });

    // ---- 3. Reload to verify persistence -----------------------------------
    await sharedPage.reload();

    // After reload, the section heading should now read "Personal
    // Information" (the profile exists). The form should be pre-populated.
    await expect(
      sharedPage.getByRole("heading", { name: "Personal Information" }),
    ).toBeVisible();

    // Verify the saved values appear in the form inputs.
    await expect(sharedPage.getByLabel("Education Level")).toHaveValue(
      INITIAL.educationLevel,
    );
    await expect(sharedPage.getByLabel("Major")).toHaveValue(INITIAL.major);
    await expect(sharedPage.getByLabel("Preferred Language")).toHaveValue(
      INITIAL.preferredLanguage,
    );
    await expect(sharedPage.getByLabel("University")).toHaveValue(
      INITIAL.university,
    );
    await expect(sharedPage.getByLabel("Learning Style (VARK)")).toHaveValue(
      INITIAL.learningStyle,
    );
    await expect(sharedPage.getByLabel("Daily Available Minutes")).toHaveValue(
      INITIAL.dailyAvailableMinutes,
    );

    // ---- 4. Update to second set of values + save -------------------------
    await fillProfileForm(sharedPage, UPDATED);
    await sharedPage.getByRole("button", { name: "Save Changes" }).click();

    await expect(sharedPage.getByRole("status")).toBeVisible({
      timeout: 15_000,
    });

    // ---- 5. Reload to verify update persisted ------------------------------
    await sharedPage.reload();

    await expect(
      sharedPage.getByLabel("Education Level"),
    ).toHaveValue(UPDATED.educationLevel);
    await expect(sharedPage.getByLabel("Major")).toHaveValue(UPDATED.major);
    await expect(sharedPage.getByLabel("Preferred Language")).toHaveValue(
      UPDATED.preferredLanguage,
    );
    await expect(sharedPage.getByLabel("University")).toHaveValue(
      UPDATED.university,
    );
    await expect(sharedPage.getByLabel("Learning Style (VARK)")).toHaveValue(
      UPDATED.learningStyle,
    );
    await expect(sharedPage.getByLabel("Daily Available Minutes")).toHaveValue(
      UPDATED.dailyAvailableMinutes,
    );
  });
});

/**
 * Fill the profile form with the given values. Clear-then-fill so the
 * test is robust to either an empty form (new profile) or a pre-populated
 * form (existing profile being updated).
 */
async function fillProfileForm(page: Page, values: typeof INITIAL) {
  await page.getByLabel("Education Level").fill(values.educationLevel);
  await page.getByLabel("Major").fill(values.major);
  await page.getByLabel("Preferred Language").selectOption(values.preferredLanguage);
  await page.getByLabel("University").fill(values.university);
  await page.getByLabel("Learning Style (VARK)").fill(values.learningStyle);
  await page.getByLabel("Daily Available Minutes").fill(values.dailyAvailableMinutes);
}

/**
 * Perform the real Keycloak OIDC login via our login page. Same as
 * courses-crud.spec.ts — duplicated intentionally rather than shared via
 * a fixture, so each spec remains self-contained and the Phase 6 review
 * surface stays small.
 */
async function performKeycloakLogin(
  page: Page,
  username: string,
  password: string,
) {
  await page.goto("/login");
  await page
    .getByRole("button", { name: /sign in with openlearn ai/i })
    .click();
  await page.waitForSelector("#username", { state: "visible" });
  await page.fill("#username", username);
  await page.fill("#password", password);
  await page.click("#kc-login");
  await page.waitForURL(/\/dashboard$/, { timeout: 30_000 });
}
