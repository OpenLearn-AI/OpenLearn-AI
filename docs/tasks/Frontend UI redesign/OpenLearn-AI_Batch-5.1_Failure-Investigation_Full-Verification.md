# OpenLearn-AI Batch 5.1 — Failure Investigation, Root-Cause Fixes & Full Verification

**Status: EXECUTED (2026-10-26, on branch `frontend-redesign` @ `448829031e3092df3c40c3cd5ba4d05e373b04cb` — the owner-applied `5.1-test-suite-alignment-execution` commit, verified as the `origin/frontend-redesign` tip at execution start. Working tree clean except the batch-owned changes listed in §6. This is the follow-up required by the Batch 5.1 brief after the first real E2E runtime run and the reported Storybook/Vitest run failures.**

This note supersedes the runtime-verification status of `OpenLearn-AI_Batch-5.1_Execution_Test-Suite-Alignment.md` §6–§8: the E2E runtime leg — which that note recorded as BLOCKED/NOT RUN — was executed here in full against the restored local stack, and the three E2E failures observed in the first runtime run are root-caused and fixed. The Storybook run reported in the same brief was re-verified and does not reproduce with the current checkout and tooling (§4).

---

## 1. Verified starting state (2026-10-26)

| Item | Verified value |
|---|---|
| Branch / HEAD | `frontend-redesign` @ `448829031e3092df3c40c3cd5ba4d05e373b04cb` (`5.1-test-suite-alignment-execution`) |
| `origin/frontend-redesign` | `448829031e3092df3c40c3cd5ba4d05e373b04cb` — in sync (`git fetch origin` after the last upstream push; nothing new) |
| `origin/staging` | `41cf5116370eb75549a5e1ad26ee08250dc4c7cc` — the known unmerged divergence (merge-base `d1ba348`); **NOT contained in HEAD, no merge performed or attempted** |
| Working tree at start | Clean (`git status --short` empty; user changes: none) |
| Environment | Node v24.21.0 / npm 11.19.0; Docker daemon present with the dev containers (`infra-keycloak-1` on Keycloak 26.7.3, `infra-db-1`, `infra-redis-1`, `infra-minio-1`) up |
| Services | Keycloak :8080 up (OIDC discovery HTTP 200). Backend :8000 and frontend :3000 were NOT running at start; both were started for this verification (background `uvicorn app.main:app --port 8000` with `backend/.venv`; `npm run dev` in `frontend/`) and `/health` returned 200 after startup |
| Credentials | All four spec credential variables (`E2E_USERNAME`, `E2E_PASSWORD`, `E2E_INSTRUCTOR_USERNAME`, `E2E_INSTRUCTOR_PASSWORD`) present in the environment — presence verified by env-var **name** grep only; values never printed, logged, or committed |
| E2E artifacts from the failing run | `frontend/test-results/` held three failure dirs (login, two onboarding tests) with `error-context.md`, screenshots, traces, and video — all inspected (§2). **These artifacts no longer exist**: the passing rerun replaced `test-results/` contents through Playwright's own run lifecycle; the inspected contents are quoted in this note |

## 2. E2E failures — root causes (per test)

The run under investigation: `npm run test:e2e` → **8 passed, 3 failed, 11 total**, all three failures asserting `getByRole('heading', { name: 'Welcome back!' }).toBeVisible()` with the timeout short-circuited ("element(s) not found" — the locator waited 5 s and matched nothing).

**Shared root cause, established from the artifacts plus live state — NOT three independent bugs.**

`frontend/test-results/…/error-context.md` (all three failure dirs) captured the LIVE page state at failure time:

- The dashboard had fully rendered: the shell sidebar, the account colophon (`Role:` … `student, …`), the 3-courses count link, the profile measure ("2 of 6 fields left"), and the recently-created list were all present and correct — the real OIDC login, `/auth/me`, and `GET /v1/courses` had all succeeded.
- The rendered `<h1>` was **`Welcome back, Muhammad!`** — the sidebar rendered the same identity as `M Muhammad Seyam`.
- The plain `Welcome back!` heading — the only thing the failing locator matched — was genuinely absent, because the personalized variant is what the component renders when the session carries a first name.

Fixture verification (read-only Keycloak Admin API queries through the running `infra-keycloak-1` container; only the non-secret `username/firstName/lastName/email/enabled` fields read): **both dev E2E accounts (`testuser` and `instructor`) now carry `firstName`/`lastName`** (`Muhammad`; `Seyam`). The bootstrap (`infra/dev/bootstrap-keycloak.sh`) creates both accounts **without** name fields — the names were set after provisioning.

- **Failure A** — `e2e/login.spec.ts` `Login smoke flow › user authenticates via Keycloak and lands on /dashboard` (~line 92): the same shared cause. The spec's own comment block asserts the environment premise *"the E2E bootstrap users are provisioned without name claims, so the plain greeting renders here"* — that premise is now false in this environment and was never enforceable (batch 2.2.1 already recorded that Keycloak 26.7.3's first-login **Verify Profile** interstitial sets firstName/lastName for name-less accounts the first time an account logs in manually — the exact mechanism these accounts went through).
- **Failure B** — `e2e/onboarding.spec.ts` `existing profile: /dashboard is reachable without any redirect` (~line 90, now ~97): same shared cause (the error context is byte-equal in the relevant parts to Failure A's).
- **Failure C** — `e2e/onboarding.spec.ts` `save failure preserves values; retry against the real API succeeds` (~line 245): same shared cause at the flow's end. The trace shows the whole flow SUCCEEDED — the real-PUT retry saved the profile and `waitForURL(/\/dashboard/)` resolved to the real dashboard (the artifact's snapshot is the rendered dashboard) — only the plain-greeting pin then failed. **The test's actual verification target (save failure ⇒ preserved values ⇒ retry against the real API ⇒ the application is reachable) passed; nothing about the onboarding gate, wizard, or gate redirect was broken.**

### Why this is a test-layer defect, not an application defect

- The application contract is the **dual-variant composition** (`features/auth/user-identity.ts::composeWelcomeGreeting`, profiled by the user-identity unit tests): `"Welcome back!"` when the session's ID token carries no `given_name`, `"Welcome back, <Name>!"` when it does. The production behavior observed in both artifacts is exactly this contract — there is no regression to fix in the app, and none was caused by Batch 5.1's changes.
- The failing pins asserted an **environment property** ("the accounts carry no name claims") instead of the product contract. That property is (a) no longer true of this environment, and (b) **not guaranteed by any provisioning**: nothing in `setup-dev.sh`/`bootstrap-keycloak.sh` prevents it, and Keycloak's own Verify Profile first-login flow sets names on any manual login (the recorded 2.2.1 finding). Correcting the environment (stripping the names) would only port the fragility to a different local state and could re-break silently at any manual login — the wrong layer.

### The fix (test layer, both affected specs)

Pin the **structure** of the composed greeting — either designed variant — with one anchored regex per file:

```ts
const greetingHeading = /^Welcome back(?:, .+)?!$/;
```

- Matches `Welcome back!` and `Welcome back, Muhammad!`; anchored (`^`/`$`) so it can never match an unrelated "Welcome back …" heading; the exclamation mark is mandatory and the comma segment only exists with a non-empty name — the structural invariants the pure composition and its unit tests already pin.
- Neither the flow steps, nor the not-weakened assertions gloss (dashboard content + roles colophon from the same `/auth/me` data), nor any other selector changed. The variant selection remains the session's real claim — the tests no longer pretend otherwise.
- Sites corrected: `e2e/login.spec.ts` step 5 + the compact-viewport block's core-content pin; `e2e/onboarding.spec.ts` the two failing assertions. Both files' doc comments were rewritten to the true premise (the composition contract + the fixture-name source), replacing the false "E2E users have no name claims" statement.

**Deliberately NOT changed:** the Dashboard story's plain-fallback pin (`Dashboard.stories.tsx`) — in the hermetic story context the Keycloak singleton is uninitialized so `given_name` is always absent and the plain variant is deterministic there; it passed throughout (§4). No application code, no Keycloak/theme/bootstrap change, no environment mutation (the accounts' names were left as-is), no timeout increases, no assertions weakened, no helpers/config changes.

## 3. Storybook / Vitest failures reported in the brief — investigation result

The brief's reported run: **7 test files passed and 1 failed (8 of 8 reported); 51 tests passed and 3 failed; 1 unhandled error** — the 3 CourseDetail tests rendering `Failed to load course.`, plus the unhandled `Cannot connect to the iframe. Did you change the location or submitted a form?` error attributed to `CourseMaterials.stories.tsx` (iframe URL `unknown`).

**This run does not reproduce with the current checkout and tooling.** Evidence:

1. Targeted file run: `npx vitest run --project storybook stories/CourseDetail.stories.tsx` → **1 file passed, 3/3 tests passed** — including the exact three named stories (`Owner — hub with materials`, `Viewer — read-only hub`, `Owner — course without a description`), which render the title h1, the Description h2, the Materials region, and the role-aware actions from their seeded caches.
2. Full-suite runs — twice consecutive: `npm run test:storybook` → **Test Files 26 passed (26); Tests 104 passed (104)** — every story file, including all three CourseDetail stories and the CourseMaterials file, with the axe fail-on-violation config intact and **no unhandled error** in either run's report.
3. Reported-run internal inconsistency supporting an aborted-run diagnosis: the real suite is **26 test files / 104 tests**; the reported run reached only **8 files / 54 tests**. An interrupted harness (the unhandled iframe error) stopped file collection before the majority of files ran — that signature (an early-aborted run, not a story-level failure signature) matches a lost iframe connection during the run rather than a regression in the CourseDetail stories or their mocks.
4. No artifacts from that reported run persist (the Vitest browser runner leaves no `test-results` dir; `frontend/test-results/` holds only the E2E dirs from the same session), so the exact browser console state of the failed run cannot be re-inspected. **Residual uncertainty is recorded honestly** — see §5.

Investigated and ruled out on the current tree:

- **Mocks/contract/provider mismatch with the component:** `CourseDetail.stories.tsx` seeds `authKeys.me()`, `courseKeys.detail(id)`, `materialKeys.list(id)`, and the per-material status polls into a hermetic QueryClient (`staleTime: Infinity`, `retry: false`) before rendering the real page; `useCourse` is enabled when `me.isSuccess`, which the seeded cache satisfies without any network. All four modules (`keys.ts` per domain) are consistent with the seeds; the story still passes as-is.
- **`useParams`/navigation wiring:** both pipelines are provided — the vite alias resolves `next/navigation` to `.storybook/next-navigation-stub.ts` in the Vitest runner (fed by the guarded `setStorybookParams` call in `withSeededCache`), and the static-build path feeds `parameters.nextjs.navigation.segments`. Both mechanisms were additionally reviewed and are called before each render.
- **A story navigating the frame (the error message's own suggestions):** the real components rendered in the stories contain exactly ONE navigation source — `LogoutButton`'s `keycloak.logout()` redirect (target `${window.location.origin}/login`) — and no play in `CourseMaterials.stories.tsx` (nor any other file's plays, grep-verified) interacts with it; the upload form's handler calls `event.preventDefault()` before anything else, so a `<form>`'s default submission (navigation) is impossible; and no story/component code touches `window.location` / `location.href` / `window.open` (grep-verified across `components/` and `stories/`). A frame navigation is therefore not reachable from the stories' interactions — the `unknown` iframe URL in the reported error is consistent with a lost/terminated iframe connection (context teardown or a renderer crash), not a story-driven navigation.
- **Stale-cache/browser-tooling class:** batch 5.1's own execution note already recorded a first-Storybook-run failure in this environment ("stale Playwright browser cache (v1200 vs the package's v1243)"), fixed by `npx playwright install chromium` — the same documented-prerequisite class. The current tooling (`playwright`/`@playwright/test` 1.63.0, `@vitest/browser-playwright` 4.1.11, `@storybook/addon-vitest` 10.6.0, vitest 4.1.11) runs the suite green repeatedly.

### The standing warnings, assessed separately (as the brief required)

- The `stories/**/*.mdx` glob warning and the Base UI `nativeButton` warnings are pre-existing, pass-with-WARN behavior recorded since Batch 1.1 ("warnings, not failures; explicitly not fixed — outside authorized scope"). They are unrelated to both investigations here; still not acted on.
- The `Failed to initialize Keycloak: Failed to generate PKCE challenge` / `A 'Keycloak' instance can only be initialized once` console-error lines come from the specific stories that deliberately exercise the real auth boundary (error-boundary/entry-bridge surfaces) with no Keycloak available — their recorded normal output in a hermetic run, noted in the 5.1 execution note. Verified still pass-with-recorded-output; not failures.

## 4. E2E verification (the runtime leg, executed)

Targeted (immediately after the fix): `npx playwright test e2e/login.spec.ts e2e/onboarding.spec.ts` → **8 passed (12.6s)** — including the three previously failing tests.

Full: `npm run test:e2e` → **11 passed (21.3s), 1 worker, serial** on the restored local stack (Keycloak 26.7.3 + backend :8000 + frontend :3000), with both credential pairs present:

```
✓ e2e/courses-crud.spec.ts        CRUD loop (instructor) + student affordance-visibility flow
✓ e2e/login.spec.ts               login → dashboard (compact block inside)
✓ e2e/onboarding.spec.ts          all 7 gate/wizard tests (compact-… in login + the two corrected pins)
✓ e2e/profile-roundtrip.spec.ts   profile round-trip (compact block inside)
```

The instructor CRUD flow exercised its positive affordance assertions (`You own this course`, `Edit Course`, `Delete Course`, `Upload Material`) against the real instructor account; the separate student flow asserted the negative direction; each smoke flow executed its in-spec 360×800 compact block. Nothing skipped; both required env pairs were consumed by their designed flows.

## 5. Full validation matrix (all commands from `frontend/`; final code state)

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Lint | `npm run lint` | **PASS** (0 findings) |
| 2 | Typecheck | `npm run typecheck` | **PASS** |
| 3 | Unit tests | `npm run test` | **PASS — 107/107 across 9 files** (unchanged by this follow-up) |
| 4 | Storybook + axe | `npm run test:storybook` | **PASS — 104/104 across 26 files** (2 consecutive full runs after the targeted CourseDetail run; final run of the matrix below) |
| 5 | Production build | `npm run build` | **PASS — 11 routes** (verified against the local `frontend/.env.local`; route table identical to the 4.5/5.1 record) |
| 6 | E2E collection | `npx playwright test --list` | **PASS — 11 tests in 4 files, 1 project** (unchanged from 5.1) |
| 7 | E2E runtime | `npm run test:e2e` | **PASS — 11/11** (first full E2E runtime green of the Batch 5.1 cycle; both credential pairs, real Keycloak/API) |
| 8 | Targeted story file | `npx vitest run --project storybook stories/CourseDetail.stories.tsx` | **PASS — 3/3** |
| 9 | Targeted E2E specs (post-fix smoke) | `npx playwright test e2e/login.spec.ts e2e/onboarding.spec.ts` | **PASS — 8/8** |

### Remaining issues / honest limitations

1. **The reported Storybook failure was not reproduced** under the current tree+tooling (two full green runs + a targeted pass at the exact failing point), and no artifacts from that run persist for inspection. The batch treats the current green full-suite result as the verified state; if the failure reappears, first lines of evidence per the harness interruption diagnosis: (a) run `npm run test:storybook` alone (no concurrent E2E run — both drive Playwright Chromium and can contend), (b) confirm `npx playwright install chromium` matches the installed 1.63.0 browser build, (c) capture the full output including the unhandled-error section and the count of test FILES that started (the 8-of-26 signature indicates the run aborted before collection finished).
2. **`frontend/test-results/` artifacts from the first failing run no longer exist** — Playwright's own run lifecycle cleared them on the passing rerun (standard behavior; not a manual deletion). The decisive contents (both `error-context.md` snapshots and the trace conclusions) are quoted in this note.
3. **Local-only verification:** every check here ran locally; no GitHub Actions run (CI or E2E workflow) was executed — nothing can be claimed about CI runs (the standing rule).
4. **The two GitHub repository secrets** (`E2E_INSTRUCTOR_USERNAME`/`E2E_INSTRUCTOR_PASSWORD` for the dispatched staging CRUD run) remain owner actions, unchanged from the 5.1 execution note §5; the standing owner-machine items (fresh-clone acceptance, MinIO rotation, 1.2/1.3 verifications) are unchanged in kind.
5. The dev accounts' name claims were left as-is (this is owned fixture state, and the corrected pins tolerate it by design rather than by force-fitting the environment).
6. One `git fetch origin` was performed (state check only); no push, merge, rebase, reset, clean, commit, history rewrite, or workflow dispatch occurred anywhere.

## 6. Changed files (this follow-up's batch-owned set)

| File | Change |
|---|---|
| `frontend/e2e/login.spec.ts` | The plain-wording greeting pin (step 5 + the compact block's pin) → the structural dual-variant pinned regex `greetingHeading`; header + inline comments rewritten to the true contract/premise |
| `frontend/e2e/onboarding.spec.ts` | The two failing greeting pins → the same structural pinned regex (file-level const); comments rewritten accordingly |
| `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-5.1_Failure-Investigation_Full-Verification.md` | This note (new) |
| `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md` | Ledger: the Current State refresh, the status-board 5.1 row's runtime leg, this follow-up's execution log entry, the Next Authorized Batch statement |

No other file changed — no application/runtime code, no backend, no contract, no CI, no dependency, no Keycloak/bootstrap/theme, no roadmap DOCX, no `docs/openapi.json`, no `playwright.config.ts`, no `e2e/helpers.ts`, no `e2e/courses-crud.spec.ts`/`e2e/profile-roundtrip.spec.ts`.
