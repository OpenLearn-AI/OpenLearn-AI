# OpenLearn-AI Frontend Execution Progress

## Purpose

This file records the actual execution of:

`OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx`

located at `docs/tasks/Frontend UI redesign/` (the canonical execution-context directory since the documentation relocation; older references to `frontend/docs/…` are stale). The roadmap was re-baselined in place by batch FR-REB-00 (in-document revision v1.2, 2026-10-08) and amended in place by batch FR-REB-01 (in-document revision v1.3, 2026-10-08, the product/UX roadmap amendments A–D); the file name keeps v1.1 for path stability.

(v1.1 supersedes v1.0 — it folds in the verification corrections below.)

The roadmap defines what we intend to do.
This file records what we actually did.

---

## Current State

- Current phase: 0 — Current-State Lock (not started; execution context re-baselined and amended first)
- Current batch: FR-REB-01 — Product/UX Roadmap Amendments (documentation-only) — COMPLETE
- Current gate: none passed yet (Gate A is the first)
- Repository HEAD: `c45aa7f4e24252590c3d1ad2fb2b4629fcdd9161` (branch `frontend-redesign`; the FR-REB-00 commit `c45aa7f` on top of `4c55ecd`, which contains `origin/staging` @ `d3d58879cfb1952392bb49ee955ec6b16c576432` via merge `e788772`; local HEAD equals `origin/frontend-redesign`)
- Branch: `frontend-redesign` (HEAD in sync with `origin/frontend-redesign`; this batch's documentation changes are deliberately left uncommitted in the working tree because the batch emits a patch instead of a commit, exactly as FR-REB-00's rules require)
- Last completed batch: FR-REB-01 (product/UX roadmap amendments only — NO frontend implementation; preceded by FR-REB-00, documentation re-baselining only)
- Overall status: EXECUTION CONTEXT RE-BASELINED AND AMENDED — roadmap in-document revision v1.3 carries amendments A–D (materials surface scheduled, role-aware IA, near-term IA reservation, Sentry env chain written out); awaiting approval to start Batch 0.1 on baseline `c45aa7f4`

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
- The lifecycle rules (`docs/tasks/Frontend UI redesign/GLM-batch-n-patch-lifecycle-rules.md`) govern batch mechanics; the roadmap is a DOCX in this directory, read/edited with DOCX-aware tooling.

---

# Product/UX Amendment Pass FR-REB-01 — Targeted Roadmap Amendments (2026-10-08)

This section is the **current planning-scope record**. FR-REB-01 was **documentation-only**: no frontend implementation, no backend change, no configuration change. It amends the roadmap in place (in-document revision v1.2 → **v1.3**); it does not re-baseline, does not renumber the batch structure (still six phases, eighteen batches, Gates A–F), and does not invalidate any technical fact FR-REB-00 verified. Files touched: exactly the three execution-context files (this ledger, the lifecycle rules note, the roadmap DOCX).

## Why

A read-only Product/UX/Frontend-Architecture audit of the roadmap against the repository (baseline `c45aa7f4`, clean tree) and the 44-week plan (`planning/Roadmap/44-WEEK-EXECUTION-PLAN .md`) found the roadmap factually accurate but materially conservative in four places, plus two counting slips:

- the only AI capability with a real, staging-proven, user-visible payoff — the materials upload → status flow — was scoped as an optional Gate C stretch rather than scheduled work;
- the frontend is persona-blind (zero role-conditional UI) although the backend enforces role and ownership rules;
- the shell and hub are designed as if course CRUD were terminal while the 44-week plan assigns the frontend pod near-term surfaces (W9–W17);
- the F1 Sentry environment-label chain was described but not fully written out against the deployment files;
- accuracy: the roadmap said "Eight page files" / "9 paths / 8 pages" (there are **nine** `page.tsx` files) and called the backend's **eleven operations across five mounted routers** (plus unversioned `GET /health`) "eleven routes".

## The four amendments (roadmap in-document revision v1.3)

- **A — Materials Upload + Processing Status promoted to scoped work.** The surface is now scheduled Phase 4 work inside **Batch 4.3** against the **existing contract only**: presigned PUT upload via `POST /v1/courses/{id}/materials/upload-url`, registration via `POST /v1/courses/{id}/materials` (202 with `material_id` + `job_id`, log-correlation only), material list, and status polling across the four-value literal `pending → processing → ready | failed`. Honest failed-state messaging including OCR/quota-related failures; **no retry/reprocess control** (no retry API exists); no fake progress percentages or phases; no fake AI reasoning UI; no new backend functionality. Demo-walk prerequisite recorded in Batch 2.1: an instructor-role course-owner test user on staging. Roadmap touchpoints: Sections 3.3 (Bucket C inventory), 5 (journey + demo data), 12 (Phase 4 intro), 16 (Table 11 narrowed), 17 (Open Question 6), 18 (Gate F conditions), 19 (ten questions), Tables 5/6/7/8/9/10, Gates C/E, and Batch 4.3 itself.
- **B — Role-aware information architecture (new roadmap Section 3.5).** RBAC documented as both a functional-correctness requirement (never present an action the API will refuse) and an information-architecture/design requirement (navigation, headings, page composition say who the surface is for). Personas documented from evidence: instructor = upload gated by role + course ownership; student = honest current scope (any authed user can list all courses — the backend defect, Open Question 7; no enrollment API until plan W17; no learning content), no upload affordance shown; admin = realm role with **zero** backend enforcement (`require_admin` has no call sites), so no admin UI is designed or implied. Consumes the roles `/auth/me` already returns (`meResponseSchema.roles`); adds no authorization framework, duplicates no Keycloak/backend logic, never treats client-side gating as security. Folded into Batches 2.2, 3.3, 4.2, 4.3, and 5.1 (affordance-visibility assertions only, never as authorization tests).
- **C — Near-term IA reservation (new roadmap Section 3.6).** Three-tier classification: *consumable today* (auth, profile, course CRUD, materials contract — built in 4.3), *near-term API-dependent* (W9–W17: extracted text, search, chunks/source panel, ranked citations, citation chips, chat/streaming, enrollment — **IA reservation only**), *later/future* (knowledge graph, quizzes, exams, mastery, analytics, recommendations — honest copy only). The redesigned course detail is designated the primary content/learning hub; Batch 4.3 records the attachment slots in the batch note and the design ADR. Explicitly: no placeholder screens, no empty coming-soon panels, no fake data, no fake search box, no chat composer, no citation chips, no speculative API clients — the reservation is documentation, never rendered UI. Verified premise: `backend/app/api/` still exposes only auth/users/courses/materials and zero AI-consumer endpoints.
- **D — Sentry environment chain written out (Batch 1.3).** The full verified path is now explicit: `frontend/Dockerfile` build ARG (today only the DSN is one) → `.github/workflows/deploy-staging.yml` build-argument (absent today) **and** its `.env.runtime` heredoc → `infra/docker-compose.staging.yml` frontend `SENTRY_ENVIRONMENT` (both sides today pass only `SENTRY_DSN`) → `infra/.env.staging.example` keys (`NEXT_PUBLIC_SENTRY_ENVIRONMENT`, `SENTRY_ENVIRONMENT`, `NEXT_PUBLIC_SENTRY_DSN`) — plus the `SENTRY_AUTH_TOKEN`/`SENTRY_ORG`/`SENTRY_PROJECT` build-time secrets `next.config.ts`'s `withSentryConfig` needs. Gate F's observability condition and Table 5's Sentry row now depend on that wired chain.

## Accuracy fixes (directly verified in this pass)

- **Page count:** nine `page.tsx` files for nine route paths. Corrected in roadmap §2 ("Nine page files…"), Table 1 ("9 paths / 9 pages"), and — with attribution — in the FR-REB-00 inspection bullet below ("nine-route/eight-page tree" → nine-page tree, FR-REB-01).
- **Operation-count terminology:** the backend's application API exposes **eleven operations across five mounted routers** (courses 5, materials 4 including the status router, auth 1, users 2) plus unversioned `GET /health`; the frontend consumes **eight**; nine `page.tsx` files. The old wording ("eleven routes") conflated routers/operations; the numbers were verified, not invented. Roadmap §2 now states this exactly.
- **Traceability:** roadmap Batch 1.3 and this ledger's Batch 1.3 record now describe the same chain, the same files, the same `.github/workflows/` path.

## What this batch does NOT claim

- Materials UI is **not implemented** — it is now scheduled scope (Batch 4.3), status NOT STARTED.
- Role-aware UI is **not implemented** — Section 3.5 is a recorded decision, not code; the dashboard heading and Navbar labels are unchanged in the repository.
- No W9–W17 capability is implemented or faked; no retrieval/chat/citation/chunk HTTP API exists; zero AI-consumer endpoints remain the verified fact.
- No new batch was created, no batch was renumbered, no gate passed, no batch 0.1–5.3 started, no application file of any kind was touched.

## Status classification after FR-REB-01

| Category | Items |
|---|---|
| Completed facts (unchanged) | FR-REB-00 technical re-baseline; AI Week 7–8 pipeline staging-proven; CORS resolved at compose level; E2E promotion still 0/3; Sentry env gap still open until Batch 1.3 runs |
| Newly scoped planning work (NOT STARTED) | Materials surface (4.3); role-aware IA application (2.2, 3.3, 4.2, 4.3, 5.1); hub reservation notes (4.3 + design ADR); precise F1 chain (1.3); materials-walk decision (2.1) |
| Blocked on future backend/API availability | Extracted text (W9), retrieval search (W10), chunk inspection (W11), citations (W13–14), chat/streaming (W15–16), enrollment (W17) — IA reservation only, per Section 3.6 |
| Unchanged exclusions | Retry/reprocess UI, fake progress/phases, pagination, i18n framework, analytics, server-side auth, coverage thresholds, spec §22.4 endpoints, fake AI |

---

# Re-Baseline FR-REB-00 — Frontend Execution Context Re-baselining (2026-10-08)

This section is the **technical baseline record** (the product/UX planning-scope amendments recorded by FR-REB-01 sit above it). It was written by batch FR-REB-00, which was **documentation-only**: no frontend implementation, no backend change, no configuration change. Everything below the next horizontal rule is the **historical record** (the 2026-10-01 roadmap verification pass against the then-current staging branch) and is preserved unmodified. Nothing in it was erased; where reality has since moved on, the correction is recorded here and in the re-baselined roadmap, not by editing history.

## Why the previous execution context became stale

The v1.1 roadmap and this ledger were authored against branch `staging` at HEAD `c51f3f10aa3c1cc716088e5468bb4f9dfc60839a` on 2026-10-01. Since then the repository advanced substantially on non-frontend tracks, and the `frontend-redesign` branch was synchronized with the current `origin/staging` (`d3d5887`, the AI Week 7–8 merge PR #77) via merge commit `e788772`, then carried two documentation commits (`7ded23a` docs relocate, `4c55ecd` archved unwanted docs) that moved the execution context from `frontend/docs/` to `docs/tasks/Frontend UI redesign/` and archived the internal three-engineer allocation document. The old context therefore described a repository that no longer exists: its materials-pipeline premise (a `NotImplementedError` seam), its staging CORS finding, and its execution-context file paths were all outdated.

## What was inspected and verified (all at HEAD `4c55ecd`, clean tree, 2026-10-08)

- **Repository state:** branch `frontend-redesign`; local HEAD `4c55ecd` equals `origin/frontend-redesign`; `origin/staging` @ `d3d5887` is an ancestor of HEAD (verified with `git merge-base --is-ancestor`); working tree clean before any edit. Expected published HEAD after the archive cleanup confirmed.
- **Frontend (`frontend/`):** `git diff --stat c51f3f1..HEAD -- frontend` shows **zero source changes** — only the deletion of the two relocated modernization documents. `package.json` (Next.js 16.3.1 App Router, React 19.2.8, TypeScript 5 strict, Tailwind 4, keycloak-js 26.2.4, TanStack Query 5, Zod 4, Sentry 10.74, shadcn-on-Base-UI), the nine-route/nine-page tree (page-file count corrected by FR-REB-01 — nine `page.tsx` files, not eight), three feature slices, the `apiFetch` boundary, `AuthGuard`, the async-state kit, 22 unit tests / 42 stories / 3 Playwright specs, and the six CI scripts are all exactly as the v1.1 roadmap recorded. Spot checks re-confirmed the investigation findings still hold in code: F3 (edit page still lacks `key={course.id}`), F5 (`created_at: z.string().datetime({ offset: true })` still demands offsets), S1 (five "Coming soon" strings in the dashboard), S2 (landing still markets RAG chat/quizzes/flashcards/knowledge graph).
- **Backend integration surface (`backend/app/`):** the HTTP API surface is unchanged in shape — still exactly the five route modules (auth, users, courses, materials incl. the status router); **zero AI-consumer endpoints exist**. The materials flow changed fundamentally: `register_material_handler` now enqueues real processing (commit-before-publish contract, 202 with `material_id` + `job_id`), and `process_material` is a full Celery task — atomic `pending`→`processing` claim, storage fetch from MinIO, Stage 1 (Docling ingest + PDF-only targeted OCR, Gemini `gemini-3.6-flash` behind the 50-char text gate), Stage 2 (chunking 1200/150 → BGE-M3 1024-dim L2-normalized embeddings → pgvector upsert committed atomically with the `ready` transition), retry policy (3 retries, 60 s backoff) and 10 m/11 m task limits, failure path marking `failed`. Upload-url/register require instructor role + course ownership; the status read requires course ownership. Course listing remains not owner-scoped (upstream defect unchanged).
- **AI capabilities (`backend/app/pal/`, `backend/app/services/document_pipeline.py`, workers, `docs/tasks/ai-week7-8/`, `docs/research/EMBEDDING.md`):** AI Week 7–8 (batches B0–B11) is closed and merged. The pipeline is **staging-proven**: the B7 final staging run observed a seeded PDF travel pending → processing → ready in ~54 s with vector rows persisted; the LiteLLM reasoning adapter is proven against the real gateway (`gemini-3.6-flash`, budget guard confirmed from the running gateway's configuration). Recorded limitations: scanned-PDF OCR is **not** fully validated (Gemini free-tier quota blocked the scanned fixtures), Langfuse tracing is disabled, Celery routes/retry finalization remains DevOps-owned. H4 ("a material actually reaches ready on staging") was delivered to the frontend pod on 2026-10-08 with provider-side evidence; the HTTP status endpoint and browser flows were never exercised by the AI pod's evidence.
- **Infrastructure / DevOps (`infra/`, `.github/workflows/`, `scripts/`):** the staging compose now passes `CORS_ORIGINS=https://openlearn-web-staging.duckdns.org,http://localhost:3000` to the backend container — **the v1.1 CORS finding is resolved at the configuration level** (the old claim that no passthrough exists is obsolete). The compose additionally runs the full AI runtime (Gemini OCR, BGE-M3, pgvector, LiteLLM with pinned digests), celery worker on `celery,ingestion_queue` + beat + Flower, Prometheus/Loki/Alloy/Grafana (api-latency-p95 dashboard), and a profile-gated `minio-init` job handled explicitly by `infra/deploy.sh`. `deploy-staging.yml` wires the AI runtime secrets with a fail-loud guard; `ci.yml` adds backend coverage reporting. The frontend deploy path still passes only `SENTRY_DSN` (compose) and declares only `NEXT_PUBLIC_SENTRY_DSN` (Dockerfile) — **the F1 Sentry environment-labeling deployment gap remains open**, as do the Node `engines` declaration (W8) and the six floating `latest` devDependencies + unpinned Chromatic action (W6/W7). `e2e.yml` is unchanged: workflow_dispatch-only, promotion still 0/3.

## Decisions recorded by this re-baseline

- **All 18 batches, their buckets, gates, and the stability contract remain valid and unchanged** — the frontend code they target is bit-for-bit the code they were written against. No batch is marked complete; none was implemented.
- **The materials stretch-flow trigger has FIRED.** The v1.1 roadmap's own mechanism ("if the seam lands, a minimal upload + status view becomes a stretch flow — Gate C decision") now applies with its premise satisfied and staging-proven. The minimal materials upload + status view is the eligible Gate C stretch decision (requires an instructor test user on staging); it is still **not** scheduled work and remains excluded until that decision adopts it. **UPDATE (FR-REB-01): superseded in planning scope — the decision has been taken. The minimal upload + status view is now scheduled scope in Batch 4.3 (roadmap revision v1.3); what remains at Gate C is only whether the materials walk joins the demo journey, and the instructor-role course-owner test user is now a Batch 2.1 prerequisite. The technical premise recorded here is unchanged.**
- **Batch 0.1's CORS check becomes a confirmation, not an investigation.** The compose-level evidence resolves Open Question 3's escalation path; only the live preflight remains.
- **Open Question 1 (Week 8 mapping) is superseded:** the AI pod closed Weeks 7–8 and staging merged the work, so the dead-seam mapping delta no longer blocks anything; the historical delta stays recorded below for the record.
- **The roadmap is re-baselined in place** (in-document revision v1.2 inside the v1.1-named file for path stability): cover evidence line, Section 1 (purpose + revision record), Section 2 (baseline), Tables 5/6/7/11/12 rows affected by the new reality, Section 6 (AI and backend dependency strategy), Phase 0 intro, and Batch 0.1 validation were reconciled; the batch structure was deliberately not renumbered.
- **No fake AI stands.** Zero AI-consumer HTTP endpoints remain the verified fact; the new pipeline is worker-internal and adds no user-facing surface. Landing-copy honesty (S2) and the dashboard metric decision (S1) are unchanged in substance.

## What remains to be implemented

Everything. The execution log below still reads NOT STARTED for Batches 0.1–5.3, and that remains true. The next authorized step is **Batch 0.1 — Baseline verification run** on the new baseline (`c45aa7f4` — the FR-REB-00 commit, which is where FR-REB-01 also verified the repository), followed by the existing phase order through Gate F. The only new decision point the re-baseline adds is the Gate C stretch decision on the minimal materials upload + status view. **UPDATE (FR-REB-01): that decision is resolved — the surface is scheduled scope (Batch 4.3); Gate C now only decides whether its walk joins the demo journey. Roadmap Sections 3.5/3.6 and Tables 1, 5, 6, 7, 8, 9, 10, 11, 12, 13 plus Batches 1.3/2.1/2.2/3.3/4.2/4.3/5.1 carry the amendments; batch structure, buckets, gates, and stability contract are unchanged.**

---

# Historical Record (pre-re-baseline, 2026-10-01 — preserved as written)

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

## Batch FR-REB-00 — Frontend Execution Context Re-baselining (documentation-only)

Status: COMPLETE (2026-10-08)

#### Planned
Re-baseline the three execution-context files against the current repository
(`frontend-redesign` @ `4c55ecd`, containing `origin/staging` @ `d3d5887`):
update the lifecycle rules (canonical paths, DOCX handling, binary-patch
method), reconcile the roadmap DOCX where the synchronized staging baseline
(AI Week 7–8, documentation relocation) had made it stale, and record the new
baseline in this ledger. **No frontend implementation.**

#### Actual
Executed exactly as planned. Repository state verified first (branch, HEAD,
remote heads, staging containment, clean tree). Full inspection pass over
frontend, backend, AI, and infra (see the re-baseline section above for the
complete evidence). The lifecycle rules were corrected in place: stale
`frontend/docs/…` paths replaced with the canonical
`docs/tasks/Frontend UI redesign/` paths, staging-containment check added to
the verification commands, DOCX read/edit/verify guidance added, the isolated-
clone `--binary` patch method adopted from the `ai-week7-8` rules, and a
documentation-only-batch verification clause added. The roadmap DOCX was
edited in place with `python-docx` (21 targeted paragraph/cell edits, styles
and TOC preserved) and re-verified by re-extraction and zip-integrity check:
cover evidence line, Section 1 purpose/revision record (now v1.2), Section 2
baseline, Table 5 (staging CORS, materials, RAG rows), Table 6 (materials and
AI rows), Section 6 intro + Table 7 + defects paragraph, Phase 0 intro, Batch
0.1 validation, Table 11 (materials/AI exclusions), Table 12 (Q1/Q3/Q6). The
batch structure (6 phases / 18 batches / Gates A–F) was deliberately kept.
No implementation batch was started, advanced, or marked complete.

#### Files changed
Exactly the three authorized files:
- `docs/tasks/Frontend UI redesign/GLM-batch-n-patch-lifecycle-rules.md`
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md`
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx`

#### Verification
- Git scope check: `git status --short`, `git diff --name-only`,
  `git diff --cached --name-only`, `git ls-files --others --exclude-standard`
  — only the three authorized files modified; nothing else touched.
- Roadmap DOCX: re-opened with `python-docx`; zip integrity test passed;
  text re-extracted (63,949 chars) and reviewed; zero stale `frontend/docs`
  references remain; remaining `c51f3f1` mentions are correctly framed
  historical references; no obsolete "NotImplementedError" claims remain as
  current-state statements.
- Lifecycle rules: full re-read after edit; canonical paths verified.
- This ledger: re-read for internal consistency (Current State vs re-baseline
  section vs historical record).
- NOT run (correctly, per the documentation-only scope): lint, typecheck,
  unit tests, Storybook, build, E2E — no application code was touched, and
  claiming such runs would violate the honesty rules.

#### Issues / deviations
None. No pre-existing Git changes existed at batch start (tree was clean), so
no preservation handling was needed. One authoring note: the roadmap's
in-document revision is v1.2 while the file name keeps v1.1 — recorded
deliberately in both the roadmap revision record and this ledger for path
stability, not treated as an inconsistency.

#### Commit
N/A (executor does not commit; Seyam applies the patch).

#### Gate impact
None — no gate passed. Gate A remains the next gate and now runs against the
re-baselined context. Produces the corrected execution context that Batch 0.1
cites.

---

## Batch FR-REB-01 — Product/UX Roadmap Amendments (documentation-only)

Status: COMPLETE (2026-10-08)

#### Planned
Apply the read-only Product/UX audit's four amendments (A — materials
upload + status surface promoted to scheduled Phase 4 scope against the
existing contract; B — role-aware information architecture; C — near-term IA
reservation for the 44-week plan's W9–W17 surfaces; D — the Sentry
environment chain written out end to end) plus the verified accuracy fixes
(nine page files; eleven backend operations across five mounted routers), to
the three execution-context files only: amend the roadmap DOCX in place
(in-document revision v1.2 → v1.3, file name unchanged), record the
amendment in this ledger, and note the amendment pass in the lifecycle
rules. **No frontend implementation.**

#### Actual
Executed as planned. Repository state verified first (branch
`frontend-redesign`, local HEAD = `origin/frontend-redesign` =
`c45aa7f4` — the FR-REB-00 commit on top of `4c55ecd`; `origin/staging` @
`d3d5887` contained; working tree clean except the pre-existing
`frontend-redesign-FR-REB-00-rebaseline.patch`, which was left untouched).
Evidence for every amendment was re-verified against the repository before
writing: materials endpoints, dependencies (instructor role + course
ownership on upload/register; ownership-only on list/status), the 202
response shape, the four-value status literal, absence of any retry
endpoint, the realm roles (`student`/`instructor`/`admin`), `require_admin`
with zero call sites, `meResponseSchema.roles` rendered as text only, the
nine `page.tsx` files, eleven API operations across five routers + unversioned
`GET /health`, eight consumed operations, the Sentry chain gaps in
`frontend/Dockerfile`, `.github/workflows/deploy-staging.yml`,
`infra/docker-compose.staging.yml`, `infra/.env.staging.example`, and the
44-week plan's W9–W17 frontend assignments.

The roadmap DOCX was edited in place with `python-docx` (57 asserted edit
groups: run-preserving paragraph spans, single-paragraph cell rebuilds with
original run formatting, one cloned validation-matrix row, and 14 inserted
paragraphs for new Sections 3.5 and 3.6 placed before Section 4) and
re-verified by re-extraction and zip-integrity check. Touchpoints: cover
evidence line; Section 1 (purpose + revision record, now v1.3); Section 2
(baseline note, page/operation/material-routes sentences); Table 1 routes
row; Section 3 intro; Bucket C inventory; new Sections 3.5 + 3.6; Tables 5,
6, 7, 8; Sections 5 (journey + demo data) and 12 (Phase 4 intro); Batches
1.3 (D), 2.1, 2.2, 3.3, 4.2, 4.3 (A + B + C), 5.1; Gates C/E evidence;
validation matrix (new materials-walk row); exclusions (Table 11 narrowed);
Open Question 6; Gate F conditions; the ten questions. Core properties
bumped (revision 2, modified 2026-10-08). The batch structure (6 phases /
18 batches / Gates A–F) was deliberately kept — no new batch number was
invented; the materials surface folded into Batch 4.3 per "amend; do not
rewrite". Ledger updates: Purpose note, Current State, the new FR-REB-01
section above, UPDATE annotations on the three superseded FR-REB-00
statements, the nine-page correction, and the NOT-STARTED planned text for
Batches 1.3, 2.1, 2.2, 3.3, 4.2, 4.3, and 5.1. Lifecycle rules: one
sentence noting the amendment pass.

#### Files changed
Exactly the three authorized files:
- `docs/tasks/Frontend UI redesign/GLM-batch-n-patch-lifecycle-rules.md`
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md`
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx`

#### Verification
- Git scope check: `git status --short`, `git diff --stat`,
  `git diff --name-only`, `git ls-files --others --exclude-standard` — only
  the three authorized files modified; the pre-existing FR-REB-00 patch
  untouched; nothing else changed; no staged or committed changes.
- Roadmap DOCX: re-opened with `python-docx`; zip integrity test passed;
  text re-extracted (76,227 chars vs 63,130 before) and the full diff
  reviewed line by line; post-conditions asserted — corrected strings
  present (nine page files, eleven operations, `9 paths / 9 pages`, the
  v1.3 revision entry, Sections 3.5/3.6, the materials-walk row) and stale
  strings absent ("Eight page files", "9 paths / 8 pages", "eleven routes",
  "Deferred (stretch)", "eligible Gate C stretch decision"); heading styles
  and TOC field untouched (TOC refresh is a reader action per the document's
  own note).
- Facts re-verified before writing (see Actual): RBAC deps/schemas, material
  API contract and status literal, no retry endpoint, realm roles,
  `require_admin` unused, page/route/operation counts, Sentry chain files,
  W9–W17 plan assignments, zero AI-consumer endpoints.
- Ledger: re-read end to end for internal consistency (Current State vs
  FR-REB-01 section vs FR-REB-00 UPDATE annotations vs batch plans).
- Lifecycle rules: re-read after edit; the one-sentence amendment note sits
  in the existing revision sentence.
- NOT run (correctly, per the documentation-only scope): lint, typecheck,
  unit tests, Storybook, build, E2E — no application code was touched, and
  claiming such runs would violate the honesty rules.

#### Issues / deviations
None blocking. Notes for the record: (1) the roadmap's in-document revision
is now v1.3 while the file name keeps v1.1 — same deliberate path-stability
decision FR-REB-00 recorded, extended rather than contradicted; (2) the
document's Table of Contents is a field code and does not auto-refresh —
new Sections 3.5/3.6 appear after a reader updates the field, as the
document's own TOC note instructs; (3) the FR-REB-00 commit `c45aa7f`
predates this batch, so Current State now records `c45aa7f4` as the verified
HEAD; (4) Batch 4.3's planned "new course-detail-scoped materials component"
is named generically on purpose — concrete file naming belongs to the batch
that implements it.

#### Commit
N/A (executor does not commit; Seyam applies the patch
`frontend-redesign-FR-REB-01-product-ux-roadmap-amendments.patch`).

#### Gate impact
None — no gate passed. Gate A remains next. The Gate C decision recorded by
FR-REB-00 (adopt or defer the materials stretch flow) is resolved by
amendment A: adopted as scheduled scope; Gate C now only locks whether the
materials walk joins the demo journey (recorded in Batches 2.1 and 4.3).

---

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
F1: wire the environment label end to end, per the roadmap's FR-REB-01
write-out — `NEXT_PUBLIC_SENTRY_ENVIRONMENT` as a `frontend/Dockerfile`
build ARG (today only the DSN is one) + the matching build-argument in
`.github/workflows/deploy-staging.yml` (absent today) + `SENTRY_ENVIRONMENT`
in that workflow's `.env.runtime` heredoc and on the frontend service in
`infra/docker-compose.staging.yml` (both today pass only `SENTRY_DSN`) +
`infra/.env.staging.example` keys (`NEXT_PUBLIC_SENTRY_ENVIRONMENT`,
`SENTRY_ENVIRONMENT`, `NEXT_PUBLIC_SENTRY_DSN`); source-map upload secrets
(`SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT` — Pod D) available at
image build time because `next.config.ts` runs `withSentryConfig` at build;
verify one labeled event with source maps.
W8: declare `engines.node` (CI runs Node 20, Docker image runs Node 22).
See Corrections table for the sharpened scope (code layer already done).

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
local is the documented fallback), and the demo dataset runbook. Record the
materials-walk decision — whether the upload → status surface now scheduled
in Batch 4.3 joins the locked journey (roadmap FR-REB-01, Sections 3.5/5) —
and, if it does, create the prerequisite instructor-role course-owner test
user on staging. No application code.

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
landing copy to only claim real capabilities. Settle the role-ambiguous copy
in the role-aware direction of roadmap Section 3.5 (FR-REB-01): the
hard-coded Student Dashboard heading becomes role-aware or neutral copy, and
the Navbar label names its destination truthfully. Files:
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
logout sequence. Labels and visibility follow the role-aware IA (roadmap
Section 3.5, FR-REB-01): destinations named truthfully for any signed-in
role using the roles `/auth/me` already returns, and no link added for a
capability that does not exist (Section 3.6); nav link targets unchanged.

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
state. Preserve `useCourses` gating and filter semantics. Dashboard heading
and stat composition role-aware per roadmap Section 3.5 (FR-REB-01) — no
hard-coded Student wording on a shared surface.

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

FR-REB-01 amendments carried here (roadmap v1.3): compose the detail as the
content hub of Section 3.6 with its stable regions and add the scheduled
materials surface — presigned upload via
`POST /v1/courses/{id}/materials/upload-url`, register via
`POST /v1/courses/{id}/materials` (202 with `material_id` + `job_id`, log
correlation only), material list, and status polled across the four-value
literal `pending/processing/ready|failed`, with honest failed-state
messaging including OCR/quota-related failures; the upload affordance
renders only for the signed-in course-owner instructor (Section 3.5; the
API answers 403 otherwise); hub slots (extracted text, search, chunks,
citations, chat, enrollment) documented in the batch note and the design
ADR, never rendered. Must-not: no new backend functionality, no
retry/reprocess control (no retry API exists), no fake progress
percentages, processing phases, or AI reasoning UI. Validation adds the
instructor-role upload → status walkthrough on staging (honest failure
copy), the student no-affordance check, and the no-placeholder-slot check.

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
skip-without-credentials, worker/retry settings. Role-aware affordance
checks may assert visibility for the instructor test user (roadmap
Section 3.5, FR-REB-01) — interface behavior only, never an authorization
boundary.

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
