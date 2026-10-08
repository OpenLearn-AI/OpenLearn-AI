# OpenLearn-AI Frontend Execution Progress

## Purpose

This file records the actual execution of:

`OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1`

(v1.1 supersedes v1.0 — it folds in the verification corrections below.)

The roadmap defines what we intend to do.
This file records what we actually did.

---

## Current State

- Current phase: 0 — Current-State Lock (not started)
- Current batch: 0.1 — Baseline verification run (next up)
- Current gate: none passed yet (Gate A is the first)
- Repository HEAD: `c51f3f10aa3c1cc716088e5468bb4f9dfc60839a`
- Branch: `staging` (clean working tree, in sync with `origin/staging`)
- Last completed batch: none (roadmap verified, execution not begun)
- Overall status: ROADMAP VERIFIED AND ISSUED AS v1.1 — awaiting approval to start Batch 0.1

---

## Execution Rules

- Roadmap is the planned source of truth.
- This file is the execution history.
- Every completed batch must update this file.
- Every deviation from the roadmap must be recorded.
- Every discovered issue must be recorded.
- Do not silently change roadmap scope.
- Do not repeat completed work.
- Preserve protected application logic.
- No speculative features.
- No fake AI.

---

## Roadmap Verification

### Overall verification

- Verified against repository: yes — full clone of `OpenLearn-AI/OpenLearn-AI`, branch `staging`
- Verification commit: `c51f3f10aa3c1cc716088e5468bb4f9dfc60839a` (clean tree)
- Verification date: 2026-10-01
- Result: **roadmap is executable as written.** 15 of 18 batches verified with zero
  corrections; 3 batches verified with minor evidence-based corrections (below).
  No batch is blocked, obsolete, already complete, or needs re-ordering.
  The repo HEAD equals the baseline HEAD the roadmap was authored against
  (`c51f3f1`), so there has been zero drift since the Big Pickle investigation.
- Disposition: all three corrections, the two additional mislabels folded into
  Batch 2.2 (Active Materials stat card, Navbar My Materials label), the sharpened
  CORS finding, and the answered Week 8 mapping are incorporated in roadmap
  **v1.1** (2026-10-01). v1.0 is superseded; the corrections below are the record
  of what changed and why.

### Corrections Required (applied in roadmap v1.1)

| Batch | Status | Required Correction |
|---|---|---|
| 1.1 | VERIFIED WITH MINOR CORRECTION | S10 evidence description: `ProfileForm.tsx` uses `text-success-foreground`, a *background-paired* token — near-white in light theme, near-black in dark theme — so the success message is invisible in **both** themes, not only dark. The roadmap's fix (`text-success`) remains exactly correct; only the defect description widens. |
| 1.3 | VERIFIED WITH MINOR CORRECTION | F1 is narrower than the roadmap assumes: `lib/config.ts` + `sentry.client.config.ts` + `sentry.server.config.ts` already implement environment labeling (v1.1 closure doc, Phase 6 Batch 3 / D14). Remaining work is only the deployment chain: `NEXT_PUBLIC_SENTRY_ENVIRONMENT` build ARG in `frontend/Dockerfile` (currently only `NEXT_PUBLIC_SENTRY_DSN` is an ARG), the matching build-arg in `deploy-staging.yml`, `SENTRY_ENVIRONMENT` runtime var in `infra/docker-compose.staging.yml` (frontend service sets only `SENTRY_DSN`), and the missing keys in `infra/.env.staging.example`. One addition: source-map upload additionally needs `SENTRY_AUTH_TOKEN`/`SENTRY_ORG`/`SENTRY_PROJECT` (Pod D secrets) available at build time — currently absent from `deploy-staging.yml`; fold into this batch or raise as an infra task. Also note actual paths: compose + env example live under `infra/`, not repo root. |
| 3.1 | VERIFIED WITH MINOR CORRECTION | The token layer the batch plans to create largely **already exists**: `app/globals.css` has a complete `@theme` block (core + semantic colors, full light/dark parity, typography scale, spacing, radius, shadows, breakpoints, sidebar, charts, Arabic font fallback), confirmed by the v1.1 closure doc ("Token architecture (D9) — design tokens, dark mode, logical utilities" complete) and `docs/design-tokens.md`. Re-scope 3.1 from "define and encode tokens" to: **ratify/adjust the existing token layer against the chosen design direction, add the genuinely missing groups (interaction states, motion principles, border weights), codify the RTL/logical-properties discipline, and write the design-decision ADR.** Batch position, dependencies, and Gate D are unchanged. |

### Confirmed Batches

| Batch | Status | Evidence |
|---|---|---|
| 0.1 | VERIFIED | All six scripts exist (`package.json`: lint, typecheck, test, test:storybook, build, test:e2e); 3 E2E specs with `test.skip` without credentials; F5 real (`schemas.ts:25` demands offset datetimes); CORS question real (see Q3 below). |
| 0.2 | VERIFIED | Every Big Pickle code re-checked against source: F3, F4, F5, F6, W1, W4, W5, W6/W7, W8, S1, S2, S3, S4, S5, S7, S8, S10 all confirmed present in code. Classification is freezable as-is. |
| 1.1 | VERIFIED (see correction) | Edit page renders `CourseForm` with no `key` (F3); `ProfileForm` seeds 6× `useState` from props with no re-key (F4); `text-success-foreground` (S10); `safeRedirectTarget` comment claims API routes rejected, code rejects only `/login`/`/register` (F6). |
| 1.2 | VERIFIED | No global 401 handler (`query-provider.tsx` has no error callback; `getAccessToken()` silently returns null on refresh failure); static session-expired strings in `CourseForm` + `ProfileForm`; register page is a stub (silent `return` on null client, no error/loading states, no theme toggle while login page has one); `(auth)` group has no `error.tsx`/`loading.tsx` while `(app)` has both; Keycloak init = `check-sso` + PKCE S256 + `checkLoginIframe:false` exactly as protected. |
| 1.4 | VERIFIED | `created_at: z.string().datetime({ offset: true })`; no analytics endpoints exist in `backend/app/api/` (auth, courses, deps, materials, users only) — metric inventory = course count + profile fields, as the roadmap states. |
| 2.1 | VERIFIED | All 9 journey routes exist and behave as mapped; staging URLs documented in `playwright.config.ts` / `e2e.yml` comments (`openlearn-web-staging.duckdns.org`); CORS risk confirmed and sharpened (see Q3). |
| 2.2 | VERIFIED | Dashboard: 3 of 4 stat cards "Coming soon" + 2 "Coming soon" sections; "Open Chat"/"View Graph" buttons link to `/courses` (mislabeled). Landing: hero copy markets RAG/quizzes/flashcards/knowledge-graph; "RAG Chat"/"Knowledge Graph" tiles link to `/dashboard`. All as flagged (S1/S2). |
| 3.2 | VERIFIED | `components/ui/dialog.tsx` does not exist; `shadcn` is a runtime dependency and `globals.css` imports `shadcn/tailwind.css` (W5); `courseKeys.list(filters)` has zero non-test usages (S4); badge used only in its own story (S5); `components.json` hooks alias points at nonexistent `@/hooks` (S7); `DeleteCourseButton` hand-rolls an accessible `role="alertdialog"` confirm panel (extraction must preserve semantics — roadmap says "identical semantics"). |
| 3.3 | VERIFIED | `useUserName` hook lives in `components/UserName.tsx` (misfiled), consumed by Navbar and profile page; `UserInfo` calls `useMe()` directly (W4); shell = Navbar (theme toggle desktop+mobile, avatar→profile, mobile menu) + footer + `AuthGuard` wrapping children in `(app)/layout.tsx`; logout currently lives in the dashboard's Session Control card (placement is presentation, may move to user menu). |
| 4.1 | VERIFIED | `(auth)/layout.tsx`, login, register, landing, `LoginForm` all exist; Suspense boundary around LoginForm confirmed with explanatory comment; `keycloak.login`/`keycloak.register` call sites confirmed; E2E asserts `Welcome Back!` dashboard heading + `sign in to your account` heading + `Sign in with OpenLearn AI` button (lockstep updates needed exactly as planned). |
| 4.2 | VERIFIED | `useCourses` gates on `me.isSuccess` (split-identity mitigation — protected); `courses/page.tsx` holds `searchQuery` inline + client-side filter (Bucket B extraction valid); `CourseCard` exists. |
| 4.3 | VERIFIED | Detail/new/edit pages + `CourseForm` + `DeleteCourseButton` exist; `notFound()` on API 404 confirmed in edit page; CRUD E2E asserts the full loop including `alertdialog` delete — the regression net is real. |
| 4.4 | VERIFIED | Profile page + `ProfileForm` + `not-found.tsx` + `(app)` error/loading exist; profile spec asserts `role="status"` success contract; Storybook direction (LTR/RTL) toolbar + light/dark backgrounds sync confirmed in `.storybook/preview.tsx`. |
| 5.1 | VERIFIED | Spec copy assertions confirmed (`Welcome Back!`, `+ Create New Course`, `Open Hub →`, `Courses & Learning Hub`, `Email:`); `playwright.config.ts` runs a single `chromium` / Desktop Chrome project with `workers: 1`, CI retries 2 / local 0 (protected settings as listed); login helper duplicated in courses-crud + profile-roundtrip specs. |
| 5.2 | VERIFIED | `e2e.yml` is workflow_dispatch-only and self-documents promotion as 0/3 ("Run 1/3: pending … Required CI: NO"); `test:storybook` runs axe at `test: 'error'` (runtime verification pending, per its own comment). |
| 5.3 | VERIFIED | Exactly six devDependencies on `latest` (`@chromatic-com/storybook`, `@vitest/browser-playwright`, `@vitest/coverage-v8`, `playwright`, `vite`, `vitest`); `storybook.yml` uses `chromaui/action@latest` (unpinned); staging deploy is live and health-gated. |

### Deferred / Obsolete

| Item | Status | Reason |
|---|---|---|
| Materials upload UI | DEFERRED (unchanged) | Backend seam raises `NotImplementedError` (`backend/app/workers/tasks/material_tasks.py:174`); v4 spec §22.4 self-describes the processing trigger as "Planned". Gate C trigger stands. |
| AI chat / quiz / graph UI | DEFERRED (unchanged) | `backend/app/api/` contains exactly 5 files (auth, courses, deps, materials, users) — zero AI routes; v4 §22.4: "none of these endpoints is implemented today". No fake AI. |
| Server-side route protection, i18n framework, pagination, coverage gates, analytics | EXCLUDED (unchanged) | All match the v1.1 closure doc's own Deferred Backlog (§13) and Scope Guard (§14) — the repo's exclusions and the roadmap's Section 16 agree 1:1. |
| S9 — unreachable `(app)/loading.tsx` | DECISION PENDING (unchanged) | Kept as the trivial keep-or-remove decision inside Batch 3.2. |

### Week 8 definition — verification against the 44-week plan

The 44-week plan (`planning/Roadmap/44-WEEK-EXECUTION-PLAN .md`, §5 "Week 8 —
Integration Close-Out + v0.2") does **not** match the roadmap's operational
definition as written. The delta, verified against both documents and the code:

| 44-week plan Week 8 item | Reality (repository evidence) | Disposition |
|---|---|---|
| Frontend: "Playwright E2E: register → login → create course → upload → status ready" | Upload → status-ready is **impossible**: the material-processing seam deterministically fails (`NotImplementedError`); v4 spec §22.4 marks the processing trigger "Planned". | Deviation recorded. Achievable subset (register/login/CRUD/profile) is exactly what the roadmap's closure set covers. |
| Register included in the E2E flow | Roadmap completes register (S3, Batch 1.2) and validates it **manually**, not as an E2E spec (no test expansion). | Accepted delta — record, optionally revisit at 5.1 lockstep. |
| E2E green **on staging** | E2E promotion runs are 0/3 and re-sequenced to Gate F (rework rationale: the redesign rewrites asserted copy). | Matches roadmap Open Question 4 — needs Seyam/team-lead sign-off. |
| v0.2.0 tag after passing Friday demo, coverage baseline (NFR-10), OpenAPI published, Docusaurus launch | Tag/coverage/OpenAPI/docs-site are project-level or other-pod deliverables; the v1.1 closure doc explicitly rejects coverage-gated testing. | Out of frontend roadmap scope; surfaced for the team lead. |

**Conclusion:** the roadmap's repo-anchored Week 8 closure set (F3, F4, F5,
W1, S3, S8, S10, F1, F6, W8, S1/S2 decisions + Sentry runtime verification +
one green local Storybook/axe run) is the *achievable frontend meaning* of the
plan's Week 8, and it also completes the v1.1 closure doc's own "runtime
verification pending" handoff list (E2E promotion, Sentry runtime, manual
critical-flow gate). This resolves Open Question 1 with evidence; the closure
set itself needs **no change**. The mapping delta above must be confirmed by
Seyam / the team lead so the closure claim lands where the plan expects it.

### Demo surface — verified

The proposed supervisor journey is **confirmed** against the implementation:
landing → register (stub → completed in 1.2) → login (Keycloak hosted, works)
→ dashboard (placeholder cards → settled in 2.2) → create course → detail →
edit (F3 → fixed in 1.1) → delete with confirmation (works, alertdialog) →
profile (F4/S10 → fixed in 1.1) → logout (works, cache cleared). Real API
usage confirmed (8 routes via the single `apiFetch` boundary; no mocks
anywhere in `features/`). Additional honesty evidence found during
verification, to fold into Batch 2.2: the first dashboard stat card is labeled
"Active Materials" while showing the course count, and the Navbar labels
`/courses` as "My Materials" — both are mislabels of the same kind as S1/S2
and are covered by that batch's copy-honesty pass. No journey expansion needed.

### AI / backend dependency strategy — verified

Confirmed unchanged and correct: zero AI-reachable endpoints; materials REST
contract exists (upload-url, register, list, status) but the pipeline always
fails; LiteLLM gateway is deployed yet unused by product flows (44-week plan
§3: "PAL reasoning provider still mock in product flows"); frontend consumes
exactly the 8 routes the roadmap lists; the split identity-resolution
mitigation (`useCourses` gated on `me.isSuccess`) exists in code and is
preserved. **No fake AI** remains the rule. Two upstream flags re-confirmed:
course listing is not owner-scoped (`list_courses(db)` — no owner filter), and
staging CORS is unresolved (below).

### Open Questions — updated by verification evidence

| # | Question | Update after verification |
|---|---|---|
| 1 | Week 8 mapping | **Answered with evidence** — see the Week 8 delta table above; needs Seyam's confirmation, not a roadmap change. |
| 2 | Does F5 hold? | Still open — by design. The schema provably demands offsets (`datetime({ offset: true })`); only the live API answer settles it. Batch 0.1/1.4 unchanged. |
| 3 | Staging CORS | **Sharpened**: `backend/app/config.py` defaults `cors_origins` to `http://localhost:3000`, and `infra/docker-compose.staging.yml`'s backend service has **no `CORS_ORIGINS` passthrough at all** — an out-of-band `.env.runtime` entry alone cannot reach the container. Fixing it requires a compose edit + backend restart (infra-owned). The Batch 0.1 preflight and the local-demo fallback both stand. |
| 4 | E2E promotion to Gate F | Unchanged; `e2e.yml` itself documents the 3-green-runs promotion protocol, currently 0/3. Sign-off still needed. |
| 6 | AI pod before Gate C | No movement — v4 §22.4 + backend code confirm nothing has landed. Trigger unchanged. |

---

# Execution Log

## Phase 0 — Current-State Lock

### Batch 0.1 — Baseline verification run

Status: NOT STARTED

#### Planned
Re-verify the investigation's machine-checkable claims (six scripts, 3 E2E
specs, F5 offset check, staging CORS preflight) and produce the baseline
record every later gate cites. Read-only.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None. (Verification pass on 2026-10-01 already re-confirmed the repo matches
the investigation at the same HEAD.)

#### Commit
N/A.

#### Gate impact
Produces the evidence for Gate A.

---

### Batch 0.2 — Scope freeze

Status: NOT STARTED

#### Planned
Freeze the bucket classification, defer list, exclusion list, and demo
journey candidate; write the short decision note in repo docs.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None. (All Big Pickle codes were re-confirmed against source on 2026-10-01 —
the classification in roadmap Section 3 is freezable as written, plus the
three evidence corrections recorded above.)

#### Commit
N/A.

#### Gate impact
Gate A.

---

## Phase 1 — Minimal Functional Closure

### Batch 1.1 — Correctness fixes on core flows

Status: NOT STARTED

#### Planned
F3 (`key={course.id}` on edit-mode CourseForm), F4 (re-key ProfileForm on
profile identity), S10 (`text-success`), F6 (align `safeRedirectTarget` with
its comment). Files: `courses/[id]/edit/page.tsx`, `profile/page.tsx`,
`components/profile/ProfileForm.tsx`, `components/auth/LoginForm.tsx`.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None. Note: S10 affects both themes (see Corrections table).

#### Commit
N/A.

#### Gate impact
Contributes to Gate B.

---

### Batch 1.2 — Authentication surface completion

Status: NOT STARTED

#### Planned
Global 401 recovery (W1), real register flow (S3), styled `(auth)`
error/loading boundaries (S8). Files: `lib/query-provider.tsx`,
`lib/auth-context.tsx`, `lib/keycloak.ts`, `(auth)/register/page.tsx`, new
`(auth)/error.tsx` + `loading.tsx`, `CourseForm.tsx`, `ProfileForm.tsx`.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Contributes to Gate B.

---

### Batch 1.3 — Observability and configuration closure

Status: NOT STARTED

#### Planned
F1: wire `NEXT_PUBLIC_SENTRY_ENVIRONMENT` through Dockerfile build ARG +
`deploy-staging.yml` build-args + compose runtime `SENTRY_ENVIRONMENT` +
`infra/.env.staging.example` keys; verify one labeled event with source maps.
W8: declare `engines.node` (CI runs Node 20, Docker image runs Node 22).
See Corrections table for the sharpened scope (code layer already done;
SENTRY_AUTH_TOKEN build secret additionally required).

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None yet. Expected: source-map upload needs the Pod D `SENTRY_AUTH_TOKEN`
secret available at build time.

#### Commit
N/A.

#### Gate impact
Contributes to Gate B.

---

### Batch 1.4 — Data contract settlement

Status: NOT STARTED

#### Planned
Settle F5 from the Batch 0.1 result (keep schema + proving fixture if offsets;
accept both shapes + normalize if naive); write the dashboard metric
inventory note. Files: `features/courses/schemas.ts`, `lib/api.test.ts`.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Completes Gate B.

---

## Phase 2 — Demo Surface Definition

### Batch 2.1 — Demo journey and environment lock

Status: NOT STARTED

#### Planned
Lock journey, page inventory, environment (staging pending the CORS answer;
local is the documented fallback), and the demo dataset runbook. No
application code.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None. Note: CORS fix requires an infra-owned compose change (see Open
Question 3 update).

#### Commit
N/A.

#### Gate impact
Contributes to Gate C.

---

### Batch 2.2 — Honest-surface settlement

Status: NOT STARTED

#### Planned
Settle dashboard + landing structure (S1/S2): remove or replace Coming-soon
cards/sections, remove mislabeled Open Chat / View Graph buttons, rewrite
landing copy to only claim real capabilities. Files:
`(app)/dashboard/page.tsx`, `app/page.tsx`. Structural edits only.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None. Also fold in the two additional mislabels found in verification
("Active Materials" stat card label; Navbar "My Materials" label).

#### Commit
N/A.

#### Gate impact
Completes Gate C.

---

## Phase 3 — UI/UX Direction and Foundations

### Batch 3.1 — Design direction and tokens

Status: NOT STARTED

#### Planned
Design direction + token layer. **Re-scoped after verification:** the token
foundation already exists in `app/globals.css` (colors incl. semantic states
with light/dark parity, typography, spacing, radius, shadows, breakpoints).
Remaining: ratify/adjust tokens against the chosen direction; add
interaction-state, motion, and border-weight groups; codify the RTL
logical-properties discipline; write the design-decision ADR. Preserve the
Tailwind 4 CSS-first model and the next-themes class strategy.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Contributes to Gate D.

---

### Batch 3.2 — Design system foundations in code

Status: NOT STARTED

#### Planned
Refine primitives on tokens; extract the alert-dialog primitive (new
`components/ui/dialog.tsx`) preserving `DeleteCourseButton`'s exact
semantics; restyle the async-state kit; vendor the shadcn stylesheet and
drop the runtime dependency (W5); remove dead code (S4 list factory, S5
badge, S7 hooks alias); settle S9. Files: `components/ui/*`,
`components/state/*`, `globals.css`, `package.json`, `components.json`,
`features/courses/keys.ts`.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Contributes to Gate D.

---

### Batch 3.3 — Application shell

Status: NOT STARTED

#### Planned
Redesign the shared protected-page structure (nav, user menu with logout,
theme toggle placement, container/header pattern, footer, responsive
breakpoints); relocate `useUserName` to `features/auth` (W4). Files:
`components/Navbar.tsx`, `components/UserName.tsx`,
`components/auth/UserInfo.tsx`, `(app)/layout.tsx`, `app/layout.tsx`,
`features/auth/`. Preserve `useMe` key, AuthGuard position, nav targets,
logout sequence.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Completes Gate D.

---

## Phase 4 — Full Frontend Redesign

### Batch 4.1 — Auth screens and landing page

Status: NOT STARTED

#### Planned
Redesign `(auth)` layout, login, register, and landing on the new system.
Preserve keycloak call sites, `safeRedirectTarget`, the Suspense boundary,
and the 1.2 register states. Lockstep: login E2E copy assertions.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Contributes to Gate E.

---

### Batch 4.2 — Dashboard and courses list

Status: NOT STARTED

#### Planned
Dashboard pattern with the locked real-metric composition; courses list
pattern with search, card grid, real empty state; extract the inline filter
state. Preserve `useCourses` gating and filter semantics.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Contributes to Gate E.

---

### Batch 4.3 — Course detail, forms, and delete confirmation

Status: NOT STARTED

#### Planned
Detail layout, form pattern (validation + API-error presentation),
delete-confirmation on the 3.2 dialog primitive with identical semantics;
keep `notFound()`-on-404, schemas, mutations, cache invalidation,
navigation, and the 1.1 key fixes.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Contributes to Gate E.

---

### Batch 4.4 — Profile, global states, responsive/RTL pass

Status: NOT STARTED

#### Planned
Profile pattern (create-vs-edit presentation settled once), global 404/error
states restyled, responsive + RTL pass using the Storybook direction toolbar.
Preserve profile schema/mutation, 404-to-null semantics, the F4 key fix, and
the `role="status"` contract.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Completes Gate E.

---

## Phase 5 — Integration and Hardening

### Batch 5.1 — Test suite alignment

Status: NOT STARTED

#### Planned
Update the 3 E2E specs to final copy/structure (role-based selectors); add
the compact mobile-viewport check (second Playwright project or in-spec
assertions). Preserve one-test-per-flow, real-Keycloak login,
skip-without-credentials, worker/retry settings.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Contributes to Gate F.

---

### Batch 5.2 — Verification runs

Status: NOT STARTED

#### Planned
Three consecutive green `e2e.yml` dispatch runs against staging; one green
`test:storybook` a11y run; recorded light/dark/LTR/RTL sweep with contrast
spot-check. Execution only — no file changes.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Contributes to Gate F.

---

### Batch 5.3 — Staging validation and demo dry run

Status: NOT STARTED

#### Planned
Final staging deploy; repeat Sentry event + source-map verification on the
final build; refresh demo dataset; one full dry run of the locked journey;
pin the six `latest` devDependencies and the Chromatic action digest.

#### Actual
Not executed yet.

#### Files changed
None.

#### Verification
Not executed yet.

#### Issues / deviations
None.

#### Commit
N/A.

#### Gate impact
Completes Gate F — presentation ready.
