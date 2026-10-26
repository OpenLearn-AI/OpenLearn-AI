import { test, expect, type Page } from "@playwright/test";

import { performKeycloakLogin } from "./helpers";

/**
 * E2E smoke flow #2 — course create → read → update → delete, plus the
 * affordance-visibility checks (Batch 5.1).
 *
 * This spec exercises the real UI flow end-to-end against a live backend.
 * Each step uses resilient role/text/label selectors (Phase 5/6 boundary:
 * no `data-testid` attributes exist in the app today, and Phase 6 does
 * NOT redesign the UI to add them).
 *
 * Batch 5.1 (D2) — role-state fix: since Batch 4.3 the course detail
 * hub renders its management affordances ("Edit Course", "Delete
 * Course", the "Upload Material" form, the "You own this course"
 * ownership line) ONLY for the owning instructor (`canManageCourse` =
 * owner + the `instructor` realm role). The CRUD loop therefore runs on
 * the EXISTING instructor test account via E2E_INSTRUCTOR_USERNAME /
 * E2E_INSTRUCTOR_PASSWORD — never the student credentials, and never a
 * silent fallback. When the instructor pair is absent the instructor
 * test skips with an explicit, actionable message.
 *
 * Batch 5.1 (D2) — negative direction: a second, separately scoped test
 * logs in as the existing student test user (E2E_USERNAME /
 * E2E_PASSWORD), creates a course through the real UI (POST /v1/courses
 * is open to every authenticated user), opens its hub, and asserts the
 * management affordances are ABSENT (presentation only — the backend,
 * not the UI, remains the authorization boundary). A role precondition
 * converts a mis-provisioned student account (one that somehow carries
 * the `instructor` role) into an explicit failure instead of a
 * misleading visibility result.
 *
 * Accepted leak (documented, deliberate): the student-created course
 * cannot be deleted through the UI by the student — the delete
 * affordance is instructor-gated (Batch 4.3) and the DELETE API is
 * owner-scoped, so no UI path exists. The title is unique per run (no
 * collisions), and the leak is the suite's existing accepted-leak
 * policy (same as the CRUD loop's failure cleanup). Cleanup, if ever
 * wanted, is an owner action outside the suite; no API bypass is added.
 *
 * Auth precondition: each describe performs its own real Keycloak login
 * ONCE in `beforeAll` (the flows run under DIFFERENT accounts, so they
 * do not share a session) and caches the page in-memory for its single
 * `test()` block.
 *
 * Why a single test block per flow instead of multiple tests: the four
 * CRUD steps form a single semantic transaction (create → use → update
 * → use → delete → verify). Splitting them into separate tests would
 * force each test to either (a) create-and-not-delete test data on
 * failure, or (b) coordinate state via a fixture framework — both worse
 * than a single linear flow that cleans up its own data on the happy
 * path. The affordance-visibility test is a deliberate, separately
 * scoped flow: it verifies a distinct role-state scenario.
 *
 * Failure cleanup: if the CRUD test fails between create and delete,
 * the course is left on the backend. This is accepted — the spec uses a
 * unique title (with timestamp) so re-runs don't collide, and the
 * accumulated test data is a low-rate leak that can be cleaned up via
 * the regular course list UI. No elaborate cleanup framework is built.
 *
 * Batch 5.1 (D1): both flows end with an in-spec compact-viewport block
 * (360×800) asserting the responsive shell contract on the SAME
 * session — no second Playwright project, no repeated Keycloak login.
 *
 * Environment required:
 *   - E2E_USERNAME / E2E_PASSWORD            (student test user — the
 *                                             affordance-visibility flow)
 *   - E2E_INSTRUCTOR_USERNAME / E2E_INSTRUCTOR_PASSWORD
 *                                            (the instructor test account —
 *                                             the CRUD flow; local: the
 *                                             'instructor' account whose
 *                                             password is the root
 *                                             .env.local's
 *                                             OPENLEARN_INSTRUCTOR_USER_PASSWORD)
 *   - NEXT_PUBLIC_KEYCLOAK_URL / REALM / CLIENT_ID
 *   - NEXT_PUBLIC_API_URL  (so /v1/courses endpoints resolve)
 */

const E2E_USERNAME = process.env.E2E_USERNAME;
const E2E_PASSWORD = process.env.E2E_PASSWORD;
const E2E_INSTRUCTOR_USERNAME = process.env.E2E_INSTRUCTOR_USERNAME;
const E2E_INSTRUCTOR_PASSWORD = process.env.E2E_INSTRUCTOR_PASSWORD;

// Unique suffix per run so a leftover course from a previous failed run
// never collides with the current run's title-based lookups.
const RUN_ID = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const INITIAL_TITLE = `E2E CRUD Init ${RUN_ID}`;
const INITIAL_DESC = "Created by the Playwright courses-crud smoke flow.";
const UPDATED_TITLE = `E2E CRUD Updated ${RUN_ID}`;
const UPDATED_DESC = "Updated description from the Playwright smoke flow.";
const STUDENT_TITLE = `E2E Student Affordance ${RUN_ID}`;
const STUDENT_DESC =
  "Created by the Playwright affordance-visibility flow (student account).";

test.describe("Course CRUD smoke flow (instructor)", () => {
  // Skip the instructor flow cleanly when the instructor credential pair
  // is not provided — with an explicit, actionable reason. The CRUD flow
  // exercises the instructor-only hub affordances (Batch 4.3 role
  // gating), so it can NEVER run on the student credentials; there is no
  // silent fallback to E2E_USERNAME.
  test.skip(
    !E2E_INSTRUCTOR_USERNAME || !E2E_INSTRUCTOR_PASSWORD,
    "E2E_INSTRUCTOR_USERNAME / E2E_INSTRUCTOR_PASSWORD must be set to the instructor test account to run the course CRUD flow — the hub's Edit/Delete/Upload affordances render only for the owning instructor (Batch 4.3 role gating), so the student credentials cannot run this flow. Local setup: username 'instructor' + the OPENLEARN_INSTRUCTOR_USER_PASSWORD value from the root .env.local (see docs/development/LOCAL_SETUP.md).",
  );

  let sharedPage: Page;

  test.beforeAll(async ({ browser }: { browser: import("@playwright/test").Browser }) => {
    sharedPage = await browser.newPage();
    // Onboarding-aware (Batch 4.1): a fresh user is routed through the
    // wizard and returns to /dashboard with an existing profile; a used
    // environment settles directly on /dashboard.
    await performKeycloakLogin(
      sharedPage,
      E2E_INSTRUCTOR_USERNAME!,
      E2E_INSTRUCTOR_PASSWORD!,
    );
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

    // ---- 2b. Positive affordance assertions (Batch 5.1, D2) ---------------
    // The logged-in user is the OWNING INSTRUCTOR (the E2E_INSTRUCTOR_*
    // account): the hub renders its management affordances for exactly
    // that role-state — canManageCourse = owner + the `instructor` realm
    // role (Batch 4.3). Asserting them here proves the role-state renders
    // and gives the Edit/Delete steps below an explicit failure site.
    // Presentation only: the backend (require_owned_course + the
    // instructor-gated materials API) remains the authorization boundary;
    // this flow never treats these checks as backend proof.
    await expect(sharedPage.getByText("You own this course")).toBeVisible();
    await expect(
      sharedPage.getByRole("link", { name: "Edit Course" }),
    ).toBeVisible();
    await expect(
      sharedPage.getByRole("button", { name: "Delete Course" }),
    ).toBeVisible();
    await expect(
      sharedPage.getByRole("button", { name: "Upload Material" }),
    ).toBeVisible();

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

    // The dialog's accessible name resolves to its AlertDialogTitle ("Delete
    // this course?"), not the component's `aria-label` — Base UI wires the
    // popup `aria-labelledby` to the Title and labeledby outranks a direct
    // `aria-label` in accessible-name computation, so the /Delete course:/i
    // selector never matched.
    const dialog = sharedPage.getByRole("alertdialog", {
      name: "Delete this course?",
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

    // ---- 7. Compact-viewport shell contract (Batch 5.1, D1) ---------------
    // Same in-spec block as the login flow's step 6, asserted here while
    // still on /courses at the end of the CRUD loop — the shell contract
    // holds on this surface too, on the SAME authenticated session (no
    // second project, no repeated Keycloak login).
    await sharedPage.setViewportSize({ width: 360, height: 800 });

    // Desktop sidebar out of the accessibility tree; the closed drawer's
    // identically-named landmark unmounted (see the login flow's note).
    await expect(
      sharedPage.getByRole("navigation", { name: "Primary navigation" }),
    ).toHaveCount(0);

    const openMenu = sharedPage.getByRole("button", { name: "Open menu" });
    await expect(openMenu).toBeVisible();

    await openMenu.click();
    await expect(
      sharedPage.getByRole("link", { name: "Courses" }),
    ).toBeVisible();

    await sharedPage.getByRole("button", { name: "Close menu" }).click();
    await expect(
      sharedPage.getByRole("navigation", { name: "Primary navigation" }),
    ).toHaveCount(0);

    // The flow's core page content remains visible and usable at the
    // compact width — the courses masthead's create action (which renders
    // in every list state).
    await expect(
      sharedPage.getByRole("link", { name: "+ Create New Course" }),
    ).toBeVisible();

    // Restore the desktop viewport (defensive hygiene — see the login
    // flow's note).
    await sharedPage.setViewportSize({ width: 1280, height: 720 });
  });
});

test.describe("Course hub affordance visibility (student)", () => {
  // The negative direction runs on the EXISTING student test user, with
  // its own explicit skip — independent of the instructor pair above.
  test.skip(
    !E2E_USERNAME || !E2E_PASSWORD,
    "E2E_USERNAME / E2E_PASSWORD must be set to the student test account to run the affordance-visibility flow (local: 'testuser' + the OPENLEARN_TEST_USER_PASSWORD value from the root .env.local).",
  );

  let sharedPage: Page;

  test.beforeAll(async ({ browser }: { browser: import("@playwright/test").Browser }) => {
    sharedPage = await browser.newPage();
    // Onboarding-aware real login for the student account (fresh users
    // complete the wizard; used environments settle on /dashboard).
    await performKeycloakLogin(sharedPage, E2E_USERNAME!, E2E_PASSWORD!);
  });

  test.afterAll(async () => {
    if (sharedPage) {
      await sharedPage.close();
    }
  });

  test("a non-instructor owner's course hub exposes no management affordances", async () => {
    // ---- Role precondition (Batch 5.1, D2 misconfiguration guard) --------
    // The dashboard's account colophon renders the session's REAL realm
    // roles from /auth/me (`<dt>Role:/Roles:</dt><dd>…</dd>`). If the
    // E2E_USERNAME fixture were mis-provisioned WITH the instructor
    // role, the negative assertions below would pass vacuously and
    // report a misleading visibility result — so fail here, with a clear
    // diagnostic, instead.
    const rolesTerm = sharedPage.getByText(/Roles?:/);
    await expect(rolesTerm).toBeVisible();
    const rolesValue = rolesTerm.locator("xpath=following-sibling::dd");
    await expect(rolesValue).toBeVisible();
    await expect(rolesValue).not.toContainText("instructor");

    // ---- Create a course through the real UI -----------------------------
    // POST /v1/courses is open to every authenticated user (role-open by
    // design), so the student can create a course whose hub then proves
    // the negative affordance state.
    await sharedPage.goto("/courses");
    await expect(
      sharedPage.getByRole("heading", { name: /Courses & Learning Hub/i }),
    ).toBeVisible();

    await sharedPage
      .getByRole("link", { name: "+ Create New Course" })
      .click();

    await expect(
      sharedPage.getByRole("heading", { name: "Create Course" }),
    ).toBeVisible();
    await sharedPage.getByLabel("Title").fill(STUDENT_TITLE);
    await sharedPage.getByLabel("Description").fill(STUDENT_DESC);

    await sharedPage.getByRole("button", { name: "Create Course" }).click();
    await sharedPage.waitForURL(/\/courses$/, { timeout: 30_000 });

    await expect(
      sharedPage.getByRole("heading", { name: STUDENT_TITLE, level: 2 }),
    ).toBeVisible();

    // Open THIS course's hub — scoped to its own list item, because the
    // student's owner-scoped list may also hold accepted-leak courses
    // from earlier runs (the CRUD loop's failure cleanup policy).
    await sharedPage
      .getByRole("listitem")
      .filter({ hasText: STUDENT_TITLE })
      .getByRole("link", { name: "Open Hub →" })
      .click();

    await expect(
      sharedPage.getByRole("heading", { name: STUDENT_TITLE, level: 1 }),
    ).toBeVisible();

    // ---- Negative affordance assertions (Batch 5.1, D2) -------------------
    // The hub identifies the non-management relationship ("Course hub",
    // vs the owner-instructor's "You own this course")...
    await expect(
      sharedPage.getByText("Course hub", { exact: true }),
    ).toBeVisible();

    // ...and NONE of the management affordances render: not the Edit
    // link, not the Delete button, not the Upload Material form. The
    // counts assert ABSENCE (the UI gates on canManageCourse = owner +
    // instructor); the backend's require_owned_course and instructor-
    // gated materials API remain the real authorization boundary — this
    // test verifies the interface's honest presentation of that state,
    // never the authorization itself.
    await expect(
      sharedPage.getByRole("link", { name: "Edit Course" }),
    ).toHaveCount(0);
    await expect(
      sharedPage.getByRole("button", { name: "Delete Course" }),
    ).toHaveCount(0);
    await expect(
      sharedPage.getByRole("button", { name: "Upload Material" }),
    ).toHaveCount(0);

    // ---- Accepted leak (documented, deliberate) ---------------------------
    // The student cannot delete this course through the UI: the delete
    // affordance is instructor-gated (Batch 4.3) and the DELETE API is
    // owner-scoped, so no UI cleanup path exists. The unique per-run
    // title prevents collisions; the course remains on the student
    // account as the suite's accepted leak. No API deletion or auth
    // bypass is added here — cleanup is an owner action outside the
    // suite if ever wanted.
  });
});
