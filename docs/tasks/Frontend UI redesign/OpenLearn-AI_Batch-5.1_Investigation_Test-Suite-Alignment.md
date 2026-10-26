# OpenLearn-AI Batch 5.1 Investigation — Test Suite Alignment

**Status: INVESTIGATION ONLY (2026-10-26). No application or test code was modified by this investigation. The proposed plan below is PROPOSED and awaits Seyam's explicit authorization before Batch 5.1 executes.**

Investigation base: `frontend-redesign` @ `515fa7620c32b74aaa98d6b464207f77b9e6ab0c` (the owner's "Changed landing screenshot" commit; `0e68757` — the owner-applied Batch 4.5 execution — is its parent).

---

## 1. Actual starting state (verified 2026-10-26)

| Item | Verified value |
|---|---|
| Branch | `frontend-redesign` |
| HEAD | `515fa7620c32b74aaa98d6b464207f77b9e6ab0c` — "Changed landing screenshot" (a 1-file binary change to `frontend/public/courses-preview.png`; zero E2E relevance) |
| `origin/frontend-redesign` | `515fa7620c32b74aaa98d6b464207f77b9e6ab0c` — local in sync (fresh clone; `git fetch origin` found nothing new) |
| `origin/staging` | `41cf5116370eb75549a5e1ad26ee08250dc4c7cc` — the known unmerged divergence (merge-base `d1ba348`; staging holds only `c69a31c`, the 3-line staging-compose localhost binding + PR #80 merge — zero frontend relevance). **No merge performed or attempted** (the batch brief explicitly forbids it). |
| Working tree | Completely clean — `git status --short` empty, `git diff --stat` empty. No Batch 4.5 files remain modified or untracked. |

**Batch 4.5 presence in the baseline: CONFIRMED.** `0e68757` ("4.5-materials-lifecycle") is HEAD's parent, and `a1a5415` (the owner-applied 4.5 investigation commit) is its parent — exactly the lineage the brief describes. The ledger's Batch 4.5 execution entry and its board row are present and read EXECUTED. The 4.5 surfaces (`MaterialTextViewer.tsx`, `MaterialProcessControl` wiring in `CourseMaterials.tsx`, the materials module additions) are all in the tree.

**Batch 5.1 status in the ledger: NOT STARTED** (board row) with the Next Authorized Batch statement naming 5.1 "Test suite alignment (+ affordance-visibility checks)" as the next roadmap batch, pending Seyam's explicit authorization. This investigation is that authorization's first (investigation-only) step; the lifecycle prerequisites (rules read, ledger read, roadmap DOCX extracted via python-docx, 44-week plan read, Batch 4.5 notes read) were all performed.

## 2. The actual E2E inventory (paths verified)

The brief and roadmap TABLE 27 name three specs + the config. The repository actually holds **four spec files plus one shared helper**, all verified at the stated paths:

```text
frontend/e2e/login.spec.ts            — 1 test
frontend/e2e/courses-crud.spec.ts     — 1 test
frontend/e2e/profile-roundtrip.spec.ts — 1 test
frontend/e2e/onboarding.spec.ts       — 7 tests (Batch 4.1; NOT in 5.1's frozen file list)
frontend/e2e/helpers.ts               — performKeycloakLogin + completeOnboardingWizard
frontend/playwright.config.ts         — 1 project (chromium), workers 1, retries CI:2/local:0
```

`npx playwright test --list` (the lifecycle-permitted, non-mutating collection command) was executed in this investigation: **10 tests in 4 files, 1 project** — matching the ledger's 4.5-era record.

### How login works and where credentials are consumed

- `performKeycloakLogin` (helpers.ts): `goto("/login")` → the entry bridge auto-initiates the real OIDC flow → wait for Keycloak's hosted form (`#username`, `#password`, `#kc-login` — Keycloak-theme selectors, external to this repo, documented stable across Keycloak ~10.x–26.x) → fill → redirect back → `waitForURL(/\/(dashboard|onboarding)/)` → complete the wizard through the real UI if the user is profile-less → settle on `/dashboard`. **No auth state is mocked anywhere in the trio** (the onboarding spec's documented `page.route` interception of `GET/PUT /v1/users/me` is that spec's own, in-file, and always cleaned up).
- Credentials: every spec reads `E2E_USERNAME` / `E2E_PASSWORD` and `test.skip`s the whole describe when absent — "the suite skips without credentials" (roadmap must-not-change) holds today.
- The documented local run path (`scripts/run-batch-0.1-local-verification.sh`) pins `E2E_USERNAME=testuser` and `E2E_PASSWORD=$OPENLEARN_TEST_USER_PASSWORD` from `.env.local`. The provisioning (`infra/dev/bootstrap-keycloak.sh`) creates **`testuser` (realm role `student`)** and **`instructor` (realm role `instructor`)**; `.env.local` stores both dev-only passwords (`OPENLEARN_TEST_USER_PASSWORD`, `OPENLEARN_INSTRUCTOR_USER_PASSWORD`). `e2e.yml` carries only `E2E_USERNAME`/`E2E_PASSWORD` secrets.

### Current config behavior (`playwright.config.ts`)

- `testDir: ./e2e`; `fullyParallel: false`; `workers: 1` (serial — shared Keycloak session and shared course/profile state); `retries: isCI ? 2 : 0`; `actionTimeout: 10s`; `navigationTimeout: 30s`; trace `retain-on-failure`; screenshot/video `only-on-failure`/`retain-on-failure`; `baseURL = PLAYWRIGHT_BASE_URL ?? http://localhost:3000`; **one project: `chromium` on `devices["Desktop Chrome"]`** (default viewport 1280×720); no `webServer` block (deliberate — masks nothing).
- Stale doc comment only: the header still says "three smoke flows" — the suite has been four spec files since Batch 4.1. Comment drift; no behavior.

## 3. Per-spec selector/assertion audit against the final UI (post-4.5)

Every pinned string was verified against the current component source (dashboard, courses page, CoursesIndex, CourseCard, OpenHubLink, detail hub, new/edit pages, CourseForm, DeleteCourseButton, ProfileForm, Profile page, onboarding wizard/gate, MobileNav/AppSidebar/nav-config) and the exact copy strings were re-verified programmatically.

### login.spec.ts — ALIGNED; no selector changes needed

| Assertion | Current UI source | Verdict |
|---|---|---|
| `getByRole("heading", { name: "Welcome back!" })` | `app/(app)/dashboard/page.tsx` h1 = `composeWelcomeGreeting(firstName)`; name-less E2E users (bootstrap sets username+email only, no name claims) render the plain fallback `"Welcome back!"` (`features/auth/user-identity.ts`) | LIVE — and correctly non-matching for the personalized variant (the pin is not a substring of `Welcome back, <Name>!`) |
| `getByText(/Roles?:/)` | the account colophon's `<dt>` renders `Role:`/`Roles:` from real `/auth/me` data (`me.roles`; `extract_roles` = token realm roles) | LIVE |
| Skip-without-credentials; Keycloak-hosted selectors | unchanged contract | LIVE |

### courses-crud.spec.ts — selectors ALL LIVE; one **latent role-state break**

| Assertion | Current UI source | Verdict |
|---|---|---|
| `heading /Courses & Learning Hub/i` | `app/(app)/courses/page.tsx` h1 | LIVE |
| `link "+ Create New Course"` | courses page masthead Button-as-Link (renders in every list state) | LIVE |
| `heading "Create Course"` | `app/(app)/courses/new/page.tsx` h1 | LIVE |
| `getByLabel("Title")` / `getByLabel("Description")` | CourseForm Field associations (`htmlFor` = `course-title` / `course-description`) | LIVE |
| `button "Create Course"` / `button "Save Changes"` | CourseForm submit (mode-switched) | LIVE |
| `heading {INITIAL_TITLE, level: 2}` | CourseCard `<h2>` wrapping the title link | LIVE |
| `link "Open Hub →"` | `OpenHubLink` — the arrow is a literal text character inside the accessible name (pinned by design, A2/A8) | LIVE |
| `heading {TITLE, level: 1}` | detail hub `<h1>` | LIVE |
| `heading "Description", level: 2` | detail hub Description region `<h2>` | LIVE |
| `link "Edit Course"` | detail hub masthead — **renders ONLY when `canManageCourse`** (`me.id === course.owner_id && me.roles.includes("instructor")`, Batch 4.3) | LIVE string, **gated render** |
| `heading "Edit Course"` | edit page h1 (ungated route; backend `require_owned_course` enforces) | LIVE |
| `button "Delete Course"` + `alertdialog "Delete this course?"` + `button "Yes, delete it"` | DeleteCourseButton on the gated masthead; the dialog name resolves via `aria-labelledby`→AlertDialogTitle (documented in-file since 3.2) | LIVE string, **gated render** |

**The latent break (this investigation's central finding):** the CRUD loop's step 3 and step 5 go through the detail page's role-gated affordances, which since Batch 4.3 render only for the owner **with the instructor realm role**. But every documented credential convention assigns `E2E_USERNAME = testuser` (student): `e2e.yml` ("Keycloak test user"), the 0.1 local-verification runner (hard `E2E_USERNAME=testuser`), and the bootstrap's own role assignment. `POST /v1/courses` is open to any authenticated user (`backend/app/api/courses.py`: "POST /v1/courses never rejects on role or ownership"), so the create step passes for a student — then the "Edit Course" click times out, because the affordance never renders. The trio has not been executed since 2.2.1 (pre-4.3), which is why this has never been observed live; the 4.3 note's "pins unchanged" statement was true of the strings but overlooked the render condition. **The suite cannot be green on the documented credential path without resolving the E2E user's role.** The resolution is Section 6's credential design — not a selector change, and not a weakening of any assertion.

### profile-roundtrip.spec.ts — ALIGNED; no selector changes needed

| Assertion | Current UI source | Verdict |
|---|---|---|
| `heading {level: 1}` | profile page h1 "Profile" | LIVE |
| `heading "Create Your Profile"` / `"Personal Information"` | profile page h2 (profile-state-switched) | LIVE |
| Six labels: Education Level, Major, Preferred Language, University, Learning Style (VARK), Daily Available Minutes | ProfileForm Field associations | LIVE |
| `button "Create Profile"` / `"Save Changes"` | ProfileForm submit (mode-switched) | LIVE |
| `getByRole("status")` | ProfileForm `<p role="status">` success paragraph | LIVE |

Known, previously-recorded limitation (2.2.1 finding, unchanged): in CREATE mode the F4 remount (`key={profile?.id ?? "new"}`) destroys the success message on the null→object transition, so the success assertion can only pass in update mode. In every established run path the beforeAll login (wizard-completing when fresh) guarantees an existing profile, so the spec runs in update mode. **Not a 5.1 fix** (the remount is the load-bearing F4 fix); it remains recorded for the owner.

### onboarding.spec.ts — ALIGNED (audited, though outside 5.1's frozen file list)

All seven tests' pins verified live: "Step N of 3" (`Step {step+1} of {STEPS.length}`), radiogroup "Education Level", radio names incl. tiles ("1 hour", "English", "Other"), "Your education level", "Major", "Continue"/"Back"/"Save profile", validation copy ("Education level is required", "Major is required"), gate copy ("We couldn't load your profile", "Try again"), save-failure copy ("We couldn't save your profile. Your answers are preserved…"), the greeting pin, and the `/Courses & Learning Hub/i` landing assertion. **No changes needed or proposed** — which also keeps the suite-wide completion criterion ("no spec asserts copy that no longer exists") true without touching an unauthorized file.

### Stale-copy summary

Zero stale copy strings exist in any spec. The 5.1 "alignment" work is therefore NOT a selector-rewrite batch — the specs are already role-based and accessible-name-based (roadmap §17's goal was largely met by the 2.2.1/4.1/4.3 lockstep updates). The real 5.1 work is: (a) the role-state fix + affordance checks, (b) compact mobile coverage, (c) the config doc-comment refresh.

## 4. Mobile-viewport strategy — comparison and recommendation

### Option A — a second Playwright project (compact viewport)

How it would look: a `chromium-mobile` project with `viewport: { width: 360, height: 800 }` (360 = the audit-proven compact width; `md`/768px is the shell's flip breakpoint), so the whole suite re-runs compact.

**Why it is NOT the cheap option in THIS repository:**

1. **It silently does not apply to 3 of the 4 spec files.** courses-crud, profile-roundtrip, and onboarding create their pages via `browser.newPage()` in `beforeAll` — which bypasses the project's `use` options and always yields the 1280×720 default context. A naive second project would report "chromium-mobile: green" while those files actually ran at desktop width — exactly the "misleading test matrix" the brief forbids. Making Option A honest requires editing the `beforeAll` page creation in all three specs (reading `test.info().project.use`) **plus onboarding.spec.ts — which is outside 5.1's authorized file list**.
2. **It duplicates the expensive Keycloak flows.** workers=1, serial: a full compact re-run adds 4 more real OIDC logins (~doubles the trio's wall time), and CI's retries=2 re-runs whole files. The brief explicitly asks to avoid "accidental duplication of expensive Keycloak flows".
3. The roadmap's own objective row offers the choice ("second Playwright project **or in-spec assertions**"); only the §6 dependency table mentions "second Playwright project" — the objective's either/or governs.

### Option B — in-spec compact-viewport checks (RECOMMENDED)

Keep one project; inside each of the three authorized specs, add a compact block (360×800) at the flow's natural end via `setViewportSize`, asserting the **responsive shell contract** — not merely "the page loads":

- Desktop sidebar absent: `getByRole("navigation", { name: "Primary navigation" })` → `toHaveCount(0)` (the sidebar is `hidden md:flex`; the drawer's identically-named nav is unmounted while closed — verified in MobileNav.tsx/AppSidebar.tsx).
- Mobile top bar present: `getByRole("button", { name: "Open menu" })` visible (`md:hidden` header, `aria-label="Open menu"`).
- Meaningful usability moment: open the drawer, assert a real destination inside it (e.g. the "Courses" link, exact name), close via `aria-label="Close menu"`.
- Flow-content survival: the spec's core content pin still visible at 360px (greeting / "+ Create New Course" / "Personal Information" respectively).

Placement per spec: login.spec (page fixture) after the dashboard assertions; courses-crud after the delete verification (still on /courses); profile-roundtrip after the final reload assertions. One-test-per-flow is untouched (additions inside the existing single test); worker/retry settings untouched by construction; zero extra logins; onboarding.spec remains valid, desktop-only, documented.

**Recommendation: Option B.** It is the smallest honest change (three authorized files + a comment-only config touch), it tests the real mobile shell contract, and it avoids both the duplication and the misleading-matrix failure modes. Because the roadmap's validation row says "all three specs at both viewports", this reading — each spec delivers its compact check in-spec rather than as a duplicated full run — is surfaced as owner decision **D1** below.

## 5. Role-aware affordance-visibility analysis (final UI, verified)

The role-aware controls in the final UI, all in the course surfaces, all driven by ONE derivation on the detail page — `canManageCourse = me.id === course.owner_id && me.roles.includes("instructor")` (real `/auth/me` roles = token realm roles):

| Affordance | Accessible name / selector | Renders for |
|---|---|---|
| Detail hub Edit action | `link "Edit Course"` | owner + instructor |
| Detail hub Delete action | `button "Delete Course"` (+ `alertdialog "Delete this course?"`, `button "Yes, delete it"`) | owner + instructor |
| Ownership metadata line | text `You own this course` (vs `Course hub`) | owner + instructor (vs everyone else) |
| Materials upload form | `button "Upload Material"` (fields `getByLabel("Material title")`, `getByLabel("File")`) | owner + instructor (`canUpload`) |
| Reprocess control / Extracted-text viewer | `button "Reprocess"` / `button "Extracted text"` | terminal-status materials (not reachable in a CRUD-only flow — no materials exist; out of 5.1's check set, covered by the 4.5 stories/walkthrough) |
| Courses list "+ Create New Course"; card "Edit" + "Open Hub →" | as pinned in the CRUD spec | every signed-in user (list is owner-scoped; `POST /v1/courses` is role-open) — NOT role-gated |

Product observations recorded (NOT acted on — out of 5.1 scope): (1) the list card's "Edit" link is not role-gated while the hub's Edit/Delete are — the 4.3-approved design ("edit/delete for the owning instructor"); the asymmetry is presentation-only (backend `require_owned_course` enforces). (2) A student who creates a course can therefore never delete it through the UI (delete affordance is instructor-gated; the DELETE API is owner-scoped) — a consequence of the owner-approved 4.3 gating, relevant to the negative test's cleanup (below).

### Which affordance checks 5.1 should add

**Positive (instructor), folded into the existing CRUD test — strengthening, never weakening:** immediately after opening the created course's hub (before the existing Edit click):

```ts
await expect(sharedPage.getByText("You own this course")).toBeVisible();
await expect(sharedPage.getByRole("link", { name: "Edit Course" })).toBeVisible();
await expect(sharedPage.getByRole("button", { name: "Delete Course" })).toBeVisible();
await expect(sharedPage.getByRole("button", { name: "Upload Material" })).toBeVisible();
```

**Negative (non-instructor owner), one focused test in courses-crud.spec.ts** (its own flow — the CRUD flow itself remains one test): log in as the existing student test user → create a course through the real UI (role-open POST) → open its hub →

```ts
await expect(page.getByText("Course hub")).toBeVisible();
await expect(page.getByRole("link", { name: "Edit Course" })).toHaveCount(0);
await expect(page.getByRole("button", { name: "Delete Course" })).toHaveCount(0);
await expect(page.getByRole("button", { name: "Upload Material" })).toHaveCount(0);
```

plus a precondition guard: after login, the dashboard colophon's roles line must NOT contain `instructor` (converts a mis-provisioned `E2E_USERNAME` into an explicit, diagnosable failure).

**Boundaries honored:** presentation checks only — the backend (`require_owned_course`, instructor+ownership on materials) remains the authorization boundary; no role system invented; no existing CRUD assertion weakened; no new accounts, credentials, or secret files (the two accounts and both dev passwords already exist — `bootstrap-keycloak.sh` + `.env.local`).

### Credential design (the role-state fix — D2)

- **courses-crud's CRUD loop** consumes a new env pair **`E2E_INSTRUCTOR_USERNAME` / `E2E_INSTRUCTOR_PASSWORD`** (the existing Batch-2.1 instructor account; on the local stack, `instructor` + `.env.local`'s `OPENLEARN_INSTRUCTOR_USER_PASSWORD`), with its own explicit `test.skip` when absent. No silent fallback to `E2E_USERNAME` — a fallback would mask the role requirement and make both affordance directions untrustworthy.
- **The negative affordance test** consumes the existing `E2E_USERNAME` / `E2E_PASSWORD` (the student `testuser`) with its own skip — the file's describe-level skip becomes two per-test skips with explicit messages.
- login, profile-roundtrip, and onboarding keep `E2E_USERNAME` unchanged (any authenticated user satisfies them; the documented testuser path stays valid).

### Limitations recorded

- The student's negative-test course **cannot be deleted through the UI by the student** (the affordance is instructor-gated). The course leaks on the local student account — accepted under the suite's existing accepted-leak policy (unique per-run title), documented in-file; cleanup, if ever wanted, is an owner action outside the suite (the DELETE API is owner-scoped).
- No second non-owner state beyond the student exists in the fixtures, and none is invented. A non-owner INSTRUCTOR (instructor role, someone else's course) cannot be tested: the owner-scoped read 403s before any affordance renders. That boundary is backend-enforced and already covered by backend tests; not a UI-presentation concern.
- The "Extracted text"/"Reprocess" controls are not assertable in a CRUD-only flow (they need materials with terminal statuses — the 4.5 stories and the owner's materials walkthrough own that surface).

## 6. Exact validation plan (commands from `frontend/`; established Node 24.21.0 / npm 11.19.0)

| Check | Command | Prerequisites |
|---|---|---|
| Lint | `npm run lint` | none (no services) |
| Typecheck | `npm run typecheck` | none |
| Unit tests | `npm run test` (107 tests, plain-node project) | none |
| Storybook + axe (a11y) | `npm run test:storybook` (104 tests; fail-on-violation intact) | Playwright browser binaries (`npx playwright install`); no external services |
| Production build | `npm run build` (11 routes) | NEXT_PUBLIC_* build env (the documented `.env.example` values); no services |
| E2E collection | `npx playwright test --list` | none — **executed in this investigation: 10 tests in 4 files** |
| Full E2E, desktop + in-spec compact blocks | `npm run test:e2e` | the real stack (Keycloak + backend + frontend; `bash scripts/setup-dev.sh` then start the API/worker/frontend) AND credentials: `E2E_USERNAME`/`E2E_PASSWORD` (student testuser) + `E2E_INSTRUCTOR_USERNAME`/`E2E_INSTRUCTOR_PASSWORD` (instructor; the `.env.local` value) — specs skip cleanly per-test when a required pair is absent, never silently pass |

Classification: lint/typecheck/unit/storybook/build/`--list` run **without external services**; E2E execution **requires the full stack and valid credentials** and **skips when credentials are absent** (existing pattern, preserved per-test under the proposed design). CI (`ci.yml`) runs the same chain; e2e.yml is dispatch-only and its staging secrets do not yet include the instructor pair — flagged below, not a 5.1 change.

**The 5.1 completion criterion mapped:** fully green local matrix against the final UI — lint, typecheck, unit, Storybook-with-axe, build, and the three specs executing at the desktop project with each spec's in-spec compact-viewport block green, with no assertion against obsolete copy (audited: none exists today; the alignment work adds, it does not rescue).

## 7. Risks, dependencies, and pre-implementation resolutions

1. **The latent role-state break (must-fix inside 5.1):** without the D2 credential design, the CRUD spec fails on every documented credential path. This is the batch's highest-value correction and it *strengthens* the suite.
2. **`e2e.yml` lacks instructor secrets (owner/DevOps follow-up, outside 5.1's must-not-change CI):** a dispatched staging run without the instructor pair would skip the CRUD test (honest skip, explicit message) — acceptable and honest, but the owner should add `E2E_INSTRUCTOR_USERNAME`/`E2E_INSTRUCTOR_PASSWORD` secrets before the 5.2 promotion runs if those runs should exercise the CRUD flow.
3. **D1 — mobile strategy deviation from the §6 table's phrasing:** in-spec checks vs a second project. Recommend in-spec (Section 4); the owner confirms. If the owner insists on the full matrix, the honest Option-A shape is documented (project + `beforeAll` viewport threading in three specs AND onboarding.spec — growing the file list beyond the frozen four).
4. **The negative test's course leak** on the student account (Section 5 limitations) — accepted-leak policy, documented.
5. **Profile create-mode remount** (2.2.1 finding) — tolerated as-is; unchanged by 5.1.
6. **Greeting pins depend on the E2E users carrying no name claims** — true for both provisioned accounts (username+email only); already documented in-file; no action.
7. `playwright` / `@vitest/browser-playwright` devDeps are `latest`-pinned — dependency versions must not change in 5.1 (nothing in the plan touches them).
8. Environment limitation (standing, every batch): **no Docker/Keycloak/backend/credentials in the execution environment — E2E execution and the owner-stack walkthroughs remain owner-machine items.** All findings above are static-source-verified (plus the permitted `--list`); no runtime claim is made.

## 8. Minimal proposed changed-file list (for the authorized 5.1 execution)

```text
frontend/e2e/login.spec.ts            — + compact-viewport block (additive)
frontend/e2e/courses-crud.spec.ts     — per-test credential skips; CRUD loop → E2E_INSTRUCTOR_*;
                                         + positive affordance assertions (in-flow);
                                         + negative affordance-visibility test (student, own course);
                                         + compact-viewport block
frontend/e2e/profile-roundtrip.spec.ts — + compact-viewport block (additive)
frontend/playwright.config.ts          — doc-comment refresh only (four flows; in-spec compact
                                          checks documented); zero behavioral change
+ the batch note (new .md) and the ledger entry (the execution batch's documentation)
```

Untouched by design: `e2e/helpers.ts` (no change needed — the credential switch is per-spec env reads; `performKeycloakLogin` is already parameterized), `e2e/onboarding.spec.ts` (verified aligned; outside the frozen list), CI/workflows, package.json/dependencies, all application code, backend, contract, roadmap DOCX.

## 9. Proposed implementation and verification sequence (after authorization)

1. Lifecycle §1 state re-verification at the then-current HEAD; read rules + ledger + this note.
2. Implement the four-file delta exactly as Sections 4–6 specify (additive; no assertion removed or weakened; one-test-per-flow preserved; skip semantics per-test with explicit messages).
3. Validate: lint, typecheck, unit, Storybook-with-axe, build, `playwright test --list` (expect 11 tests in 4 files — the one added affordance test).
4. Documentation: the 5.1 batch note + the ledger update (board row → EXECUTED, dated log entry, Next Authorized Batch → 5.2).
5. Patch via the isolated-clone method from the verified start commit; `git apply --check` + apply + byte-identity on a pristine checkout; secret/artifact scan; report and stop.
6. Owner-machine items after 5.1 lands: the full E2E run with both credential pairs (desktop + in-spec compact), joining the standing outstanding walkthroughs.

## 10. Explicit no-modification statement

This investigation **modified no application or test code and no configuration**. The only repository changes produced are this investigation note and the ledger's investigation record (board row + dated entry), delivered as a documentation patch per the lifecycle's patch method. No commit, no push, no merge/rebase/reset/clean, no history rewrite, and no remote operations beyond the permitted `git fetch origin` state check were performed. `docs/openapi.json`, the CI workflows, the roadmap DOCX, and all `frontend/` sources are untouched. The Playwright collection command (`--list`) was the only test command executed; no E2E, unit, Storybook, build, or lint run is claimed.
