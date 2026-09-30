import { test, expect, type Page } from "@playwright/test";

/**
 * E2E smoke flow #2 — course create → read → update → delete.
 *
 * This spec exercises the real UI flow end-to-end against a live backend.
 * Each step uses resilient role/text/label selectors (Phase 5/6 boundary:
 * no `data-testid` attributes exist in the app today, and Phase 6 does
 * NOT redesign the UI to add them).
 *
 * Auth precondition: this spec assumes the user is already authenticated.
 * Because Playwright's default behavior is one fresh browser context
 * per test file, this file uses a `beforeAll` that performs the real
 * Keycloak login ONCE and caches the resulting storage state in-memory.
 * The same context is then reused by the single `test()` block below.
 *
 * Why a single test block instead of multiple tests: the four CRUD
 * steps form a single semantic transaction (create → use → update → use
 * → delete → verify). Splitting them into separate tests would force
 * each test to either (a) create-and-not-delete test data on failure,
 * or (b) coordinate state via a fixture framework — both worse than a
 * single linear flow that cleans up its own data on the happy path.
 *
 * Failure cleanup: if the test fails between create and delete, the
 * course is left on the backend. This is accepted — the spec uses a
 * unique title (with timestamp) so re-runs don't collide, and the
 * accumulated test data is a low-rate leak that can be cleaned up via
 * the regular course list UI. No elaborate cleanup framework is built.
 *
 * Environment required:
 *   - E2E_USERNAME / E2E_PASSWORD  (Keycloak test user)
 *   - NEXT_PUBLIC_KEYCLOAK_URL / REALM / CLIENT_ID
 *   - NEXT_PUBLIC_API_URL  (so /v1/courses endpoints resolve)
 */

const E2E_USERNAME = process.env.E2E_USERNAME;
const E2E_PASSWORD = process.env.E2E_PASSWORD;

// Unique suffix per run so a leftover course from a previous failed run
// never collides with the current run's title-based lookups.
const RUN_ID = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const INITIAL_TITLE = `E2E CRUD Init ${RUN_ID}`;
const INITIAL_DESC = "Created by the Playwright courses-crud smoke flow.";
const UPDATED_TITLE = `E2E CRUD Updated ${RUN_ID}`;
const UPDATED_DESC = "Updated description from the Playwright smoke flow.";

test.describe("Course CRUD smoke flow", () => {
  test.skip(
    !E2E_USERNAME || !E2E_PASSWORD,
    "E2E_USERNAME / E2E_PASSWORD must be set to run the course CRUD smoke flow",
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

  test("create → read → update → delete a course through the UI", async () => {
    // ---- 1. CREATE ----------------------------------------------------------
    // Navigate to the courses list and click the "Create New Course"
    // action. The list page header button is rendered as a Link-styled
    // Button (Base UI render prop → <a>).
    await sharedPage.goto("/courses");
    await expect(
      sharedPage.getByRole("heading", { name: /Courses & Learning Hub/i }),
    ).toBeVisible();

    await sharedPage
      .getByRole("link", { name: "+ Create New Course" })
      .click();

    // Create form (app/(app)/courses/new/page.tsx + CourseForm.tsx).
    await expect(
      sharedPage.getByRole("heading", { name: "Create Course" }),
    ).toBeVisible();

    // Field labels come from the Field wrapper; getByLabel resolves the
    // control via the <label htmlFor> association.
    await sharedPage.getByLabel("Title").fill(INITIAL_TITLE);
    await sharedPage.getByLabel("Description").fill(INITIAL_DESC);

    await sharedPage.getByRole("button", { name: "Create Course" }).click();

    // CourseForm redirects to /courses on success.
    await sharedPage.waitForURL(/\/courses$/, { timeout: 30_000 });

    // ---- 2. READ (list + detail) -------------------------------------------
    // The new course should now appear in the list. CourseCard renders
    // the title as an <h2>.
    await expect(
      sharedPage.getByRole("heading", { name: INITIAL_TITLE, level: 2 }),
    ).toBeVisible();

    // Open the detail page via the "Open Hub →" link on the card.
    await sharedPage
      .getByRole("link", { name: "Open Hub →" })
      .first()
      .click();

    // Detail page (app/(app)/courses/[id]/page.tsx). The course title is
    // the page's <h1>.
    await expect(
      sharedPage.getByRole("heading", { name: INITIAL_TITLE, level: 1 }),
    ).toBeVisible();

    // The Description section renders the description we set.
    await expect(
      sharedPage.getByRole("heading", { name: "Description", level: 2 }),
    ).toBeVisible();
    await expect(sharedPage.getByText(INITIAL_DESC)).toBeVisible();

    // ---- 3. UPDATE ----------------------------------------------------------
    // Click "Edit Course" on the detail page → edit form.
    await sharedPage.getByRole("link", { name: "Edit Course" }).click();

    await expect(
      sharedPage.getByRole("heading", { name: "Edit Course" }),
    ).toBeVisible();

    // The edit form is pre-populated with the existing title. Clear and
    // re-fill both fields to exercise the update path.
    await sharedPage.getByLabel("Title").fill(UPDATED_TITLE);
    await sharedPage.getByLabel("Description").fill(UPDATED_DESC);

    await sharedPage.getByRole("button", { name: "Save Changes" }).click();

    // Redirects back to /courses on success.
    await sharedPage.waitForURL(/\/courses$/, { timeout: 30_000 });

    // ---- 4. Verify update + read updated detail ---------------------------
    // The updated title now appears in the list.
    await expect(
      sharedPage.getByRole("heading", { name: UPDATED_TITLE, level: 2 }),
    ).toBeVisible();

    // Open the detail page again to confirm the update persisted.
    await sharedPage
      .getByRole("link", { name: "Open Hub →" })
      .first()
      .click();

    await expect(
      sharedPage.getByRole("heading", { name: UPDATED_TITLE, level: 1 }),
    ).toBeVisible();
    await expect(sharedPage.getByText(UPDATED_DESC)).toBeVisible();

    // ---- 5. DELETE ----------------------------------------------------------
    // The DeleteCourseButton renders as a single "Delete Course" button
    // initially; clicking it swaps it for an alertdialog with
    // "Yes, delete it" / "Cancel".
    await sharedPage.getByRole("button", { name: "Delete Course" }).click();

    const dialog = sharedPage.getByRole("alertdialog", {
      name: /Delete course:/i,
    });
    await expect(dialog).toBeVisible();
    await expect(
      dialog.getByRole("heading", { name: "Delete this course?" }),
    ).toBeVisible();

    await dialog.getByRole("button", { name: "Yes, delete it" }).click();

    // DeleteCourseButton redirects to /courses on success (its redirectTo
    // prop is "/courses" on the detail page).
    await sharedPage.waitForURL(/\/courses$/, { timeout: 30_000 });

    // ---- 6. Verify deletion ------------------------------------------------
    // The course title no longer appears in the list. Use a short timeout
    // because the assertion is "absent" — we want a fast failure if it
    // somehow lingers.
    await expect(
      sharedPage.getByRole("heading", { name: UPDATED_TITLE, level: 2 }),
    ).toHaveCount(0);
  });
});

/**
 * Perform a real Keycloak login through our login page → Keycloak-hosted
 * form → redirect back to /dashboard. Cached storage state could also be
 * used, but this approach is simpler and avoids serialization races in
 * the beforeAll hook.
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
