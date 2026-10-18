# OpenLearn-AI Frontend Execution Progress

## Purpose

This file is the **living execution record** for:

`OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx`

located at `docs/tasks/Frontend UI redesign/` (the canonical execution-context directory). The roadmap was fully rewritten in place by batch **FR-REB-02** (2026-10-08) — in-document revision **v2.0**; the file name keeps `v1.1` for path stability. The roadmap defines what we intend to do. This file records what we actually did, what is true right now, and what is authorized next.

Revision lineage of this context: authored 2026-10-01 against `staging @ c51f3f1` → re-baselined by FR-REB-00 (roadmap v1.2, against `4c55ecd`) → amended by FR-REB-01 (roadmap v1.3) → **fully rewritten by FR-REB-02 (roadmap v2.0, against `2eccad0`)**. Older ledgers' amendment layering was deliberately collapsed into the concise execution history in this file; the roadmap no longer carries any patchwork structure.

---

## Current State (verified 2026-10-18, during the Batch 2.1 decision lock, at Seyam's applied 2.1-discovery commit `005711e`)

- Repository HEAD: `005711ea2659060aa50935af4aea0818782589da` — branch `frontend-redesign`, equal to `origin/frontend-redesign`. Lineage since the 0.1 baseline: `699c496` (FR-REB-02 patch commit) → `bea19f3` (Batch 0.1 patch applied by Seyam) → `7ebe978` (`scripts/run-batch-0.1-local-verification.sh`, committed by Seyam) → `18d8a69` (0.1-completion + 0.2 scope-freeze patches applied by Seyam as one commit) → `7dc9f67` (Batch 1.1 patch applied by Seyam) → `f87c765` (Batch 1.2 patch applied by Seyam) → `b56be14` (Batch 1.3 patch applied by Seyam) → `e10249fd0be06d022051a31b6c000c59b3ccd709` (Batch 1.4 patch applied by Seyam as `frontend-redesign-1.4-data-contract-settlement`) → `65c8a8c189e946b77cb7c55a5ada96cfb405f54` (course-ownership implementation) + `92b67bd` (merge of PR #79 from `course-ownership-fix` — a separate post-1.4 backend change, NOT Batch 1.4 work; see the 1.4 closeout log entry) → `60d3ba5` (`1.4-closeout-evidence-based-review` — the closeout patch applied and committed by Seyam; the 2.1 discovery preflight verified its diff byte-identical to the delivered closeout patch, +64/−9 on this ledger only) → `005711e` (`2.1-discovery-demo-journey-environment-lock.patch` — the 2.1 discovery patch applied and committed by Seyam 2026-10-17; `git show --stat` = exactly the patch's six files, +663/−17: the discovery note, this ledger, the bootstrap script, the dev compose, setup-dev.sh, LOCAL_SETUP.md)
- Working tree: the decision-lock batch executed in a fresh isolated clone at `005711e` (clean tree, no stashes; all prior execution clones and the preserved stash from earlier batches left untouched). The decision-lock changes are uncommitted in that clone and are exactly two documentation files: the new `OpenLearn-AI_Batch-2.1_Product-Owner_Decision-Lock.md` and this ledger — no application code
- Current phase: 2 — Demo Surface Definition. 1.1 EXECUTED (2026-10-15); 1.2 implemented (owner validation pending); 1.3 implemented (Sentry runtime verification blocked); **1.4 EXECUTED (2026-10-17; the live-API validation criterion 3 was owner-confirmed successful on the owner machine on 2026-10-18 — see the addendum in the 2.1 discovery log entry; the executing agent did not perform the owner's test)**
- Current batch: **2.1 — Demo journey and environment lock — PARTIALLY EXECUTED (2026-10-18)**: owner-directed discovery delivered (discovery/runbook note `OpenLearn-AI_Batch-2.1_Discovery_Demo-Journey_Environment-Lock.md`: nine-route inventory re-confirmed at `60d3ba5`; material journey audited — the four material operations exist in the contract and the pipeline is staging-proven, but the frontend surface is scheduled Batch 4.3 scope and the local dev compose has no S3-compatible storage, no Redis, and no Celery worker, so the journey is NOT READY today and nothing in 2.1 fakes it; IA recommendation keeps the nine-route skeleton with the frozen reservation mechanisms; five-entry design-reference shortlist proposed for owner review); owner decisions recorded: local-first demo environment (A), substantial redesign of all implemented pages with visual execution in Phase 4 (B), extensible page architecture via the existing reservation mechanisms only (C), the materials walk adopted as essential (D), instructor test account approved (E); roadmap staging-default wording recorded for formal reconciliation (R1–R9 in the discovery note; no DOCX edit in this batch); instructor-account provisioning implemented (idempotent bootstrap extension + compose + setup script + LOCAL_SETUP section), first execution an owner-machine step (no Docker daemon in the execution sandbox); journey sequence (11 steps with readiness ratings) and dataset proposed for owner lock; **the rehearsal — setup-dev.sh run + bootstrap first run + scripted journey walk — remains the sole 2.1 execution item, on the owner machine**; **decision lock delivered (2026-10-18):** the discovery-review decisions are recorded in `OpenLearn-AI_Batch-2.1_Product-Owner_Decision-Lock.md` (authoritative decision text) — A local-first APPROVED; B substantial redesign APPROVED (authenticated-`/` redirect recorded as approved direction, not yet implemented — the landing renders a "Go to Dashboard" button today); C scoped architecture APPROVED; D material journey APPROVED with two honest qualifications (end-to-end never ran locally; resulting-state = status + list only, no document-content endpoint); E roles/ownership **CLOSED** on owner-confirmed acceptance; onboarding contract audit complete (all six candidate profile fields already supported; PUT is full-replacement upsert; GET 404 = the natural no-profile trigger); language/RTL policy APPROVED with implementation details PENDING EVIDENCE (layout hardcodes `dir="ltr"`; `profiles.preferred_language` en/ar exists; no i18n mechanism); dataset locked to two extraction-tested benchmark PDFs; R1–R9 dispositions fixed (documentation batch after the environment batch)
- Current gate: **Gate A — PASSED (2026-10-15)** — unchanged. **Gate B NOT claimed**: the closure set is now 1.1 ✓ + 1.4 ✓ (owner-confirmed live-API validation) + 1.2 ✓ pending the owner validation + 1.3 ✓ pending the Sentry runtime verification, plus the local matrix green including E2E with credentials — an owner-machine item. **Gate C pending**: the runbook is delivered (this batch); the journey lock, dataset approval, rehearsal, and 2.2's zero-dishonesty settlement remain
- Overall status: **Batch 2.1 decision lock documented — PARTIALLY EXECUTED (the owner-machine rehearsal is the sole outstanding execution item; journey direction and dataset are now owner-locked via the decision record; the design-reference shortlist and 1.4-addendum wording remain owner-review items); the next authorized batch is the local environment gap closure and practical verification, followed by the comprehensive documentation reconciliation batch — frontend execution (2.2) resumes after, per the owner's sequencing**

---

## Execution Rules

- The roadmap (DOCX) is the planned source of truth; this file is the execution history.
- `docs/openapi.json` is the only authoritative API contract reference — CI-guarded against drift; batches never code against endpoints absent from it.
- The 44-week plan (`planning/Roadmap/44-WEEK-EXECUTION-PLAN .md`) is the product roadmap authority; the frontend roadmap is its frontend execution plan.
- Every completed batch updates this file with actuals.
- Every deviation from the roadmap is recorded.
- No speculative features. No fake AI. No UI for internal infrastructure.
- The lifecycle rules (`GLM-batch-n-patch-lifecycle-rules.md`) govern batch mechanics; the roadmap is a DOCX, read/edited with DOCX-aware tooling.

---

## Current Reality — What the Repository Supports Today (verified at `2eccad0`)

### Frontend (source unchanged since `c51f3f1`; re-verified bit-for-bit at `2eccad0`)

- Next.js 16.3.1 App Router, React 19.2.8, TypeScript strict, Tailwind 4, keycloak-js 26.2.4, TanStack Query 5, Zod 4, Sentry 10.74, shadcn-on-Base-UI.
- Nine routes / nine `page.tsx` files: landing, login, register, dashboard, profile, courses list, create, detail, edit. `(app)` has `error.tsx`/`loading.tsx`; `(auth)` has neither (S8).
- Three feature slices (auth, courses, profile); single `apiFetch` boundary; client-side `AuthGuard`; no role-conditional UI anywhere (persona-blind).
- Tests: 22 unit tests (3 files), 42 Storybook stories (12 files) with axe, 3 Playwright E2E specs (login, courses-crud, profile-roundtrip).
- Findings all re-confirmed present in code: F3 (edit form not re-keyed), F5 (`created_at: z.string().datetime({ offset: true })`), S1 (five "Coming soon" strings on the dashboard), S2 (landing markets RAG chat/quizzes/flashcards/knowledge graph), W5 (`shadcn` as runtime dependency), W6/W7 (six `latest` devDependencies + unpinned Chromatic action), W8 (no `engines` field).
- CI chain (`ci.yml`): lint, typecheck, unit, storybook, build on PRs. `e2e.yml` remains workflow_dispatch-only; promotion record 0/3.

### Backend API — the contract the frontend builds against

The authoritative reference is now **`docs/openapi.json`** (tracked, regenerated deterministically by `backend/app/openapi_export.py`, drift-guarded by `backend/tests/test_openapi_contract.py`, app version 0.2.0). It exposes exactly **12 application operations across 4 routers** plus 2 unauthenticated infrastructure endpoints:

| Operation | Contract (request → response) | Auth / authorization |
|---|---|---|
| `GET /auth/me` | → `CurrentUserResponse` (id, email, settings, roles[], keycloak{issuer, subject}) | bearer; roles now an explicit, documented field |
| `GET /v1/users/me` | → `ProfileResponse` (8 fields incl. preferred_language, daily_available_minutes) | bearer |
| `PUT /v1/users/me` | `ProfileUpdate` → `ProfileResponse` | bearer |
| `GET /v1/courses` | → `CourseResponse[]` (id, title, description?, owner_id, created_at) | bearer; **not owner-scoped** (upstream defect) |
| `POST /v1/courses` | `CourseCreate` → `CourseResponse` | bearer |
| `GET /v1/courses/{id}` | → `CourseResponse` | bearer |
| `PUT /v1/courses/{id}` | `CourseCreate` → `CourseResponse` | bearer + ownership |
| `DELETE /v1/courses/{id}` | — | bearer + ownership |
| `POST /v1/courses/{id}/materials/upload-url` | `UploadUrlCreate{filename, title}` → `UploadUrlResponse{upload_url, s3_key, title, course_id, expires_in}` | bearer + instructor role + ownership |
| `POST /v1/courses/{id}/materials` | `MaterialCreate{s3_key, title}` → **202** `MaterialAcceptedResponse{material_id, job_id}` (job_id is log-correlation only, not queryable) | bearer + instructor role + ownership |
| `GET /v1/courses/{id}/materials` | → `MaterialResponse[]` (id, course_id, s3_key, status, title, uploaded_by, created_at) | bearer (course visibility) |
| `GET /v1/materials/{id}/status` | → `MaterialStatusResponse{material_id, status}` | bearer + course ownership |
| `GET /health` | unversioned liveness probe | none — infrastructure |
| `GET /metrics` | Prometheus scrape endpoint | none — infrastructure |

Contract facts: `created_at` fields are declared `format: date-time` in the tracked spec, and the live API is now verified to emit offset-bearing datetimes (Batch 0.1 local probe, 2026-10-14: 5/5 values offset-bearing, sample `2026-10-14T15:52:48.551399Z`) — the frontend schema's `offset: true` is correct as-is; the status vocabulary is the four-value literal `pending → processing → ready | failed`; there is **no retry/reprocess endpoint, no document-content endpoint, no search/chat/citation/enrollment endpoint** in the contract.

New since FR-REB-01 (the staging merge): the OpenAPI publication toolchain, the explicit `CurrentUserResponse`/`KeycloakIdentity` schemas, `backend/tests/test_material_api.py` (behavioral contract tests with fake boto3), and the drift-guard test. **No new endpoints, no frontend changes.**

### RBAC reality (re-derived)

- Keycloak realm issues `student`, `instructor`, `admin` (`infra/realm-export.json`); `GET /auth/me` returns `roles[]`.
- Enforced today: instructor role + course ownership on material upload-url/register; course ownership on the material status read; ownership on course update/delete.
- **Not enforced**: the `admin` role (`require_admin` exists in `backend/app/api/deps.py` with zero call sites) — no admin UI is designed, implied, or faked.
- Not owner-scoped: course listing (any authenticated user sees every course) — backend defect, flagged upstream, never worked around in the frontend.
- Distinction maintained throughout the roadmap: authorization lives in the backend; ownership lives in the backend; the frontend controls only affordance visibility and route accessibility, never security.

### AI / materials pipeline reality

- The Celery pipeline is real and staging-proven (AI Week 7–8, closed): `pending → processing → ready | failed`; Docling ingest → PDF-only targeted OCR (Gemini `gemini-3.6-flash`, 50-char gate) → deterministic chunking (1200/150) → BGE-M3 1024-dim embeddings → pgvector upsert committed atomically with the `ready` transition; retries (3, 60 s backoff); `document_id` is deterministic (source-file derived) — the Week 9 idempotency premise exists at pipeline level, but **no reprocess endpoint exposes it**.
- Zero AI-consumer HTTP endpoints. LiteLLM reasoning is worker-internal. Langfuse tracing disabled. Scanned-PDF OCR not fully validated (quota-blocked fixtures).
- The frontend plan treats all of this as internal infrastructure: status polling is the only user-visible reflection, through the four-value literal. No chat, streaming, retrieval, citations, graph, quizzes, progress percentages, or processing phases — none of it may be faked.

### Infrastructure / DevOps reality

- Staging compose passes `CORS_ORIGINS=https://openlearn-web-staging.duckdns.org,http://localhost:3000` (the old CORS finding stays resolved); full AI runtime configured (Gemini OCR, BGE-M3, pgvector, LiteLLM pinned digests, celery worker/beat/flower, observability stack).
- The **F1 Sentry environment-label chain remains open at `2eccad0`**, verified file-by-file: `frontend/Dockerfile` declares only `NEXT_PUBLIC_SENTRY_DSN` as an ARG; `deploy-staging.yml` passes only the DSN build-arg and its `.env.runtime` heredoc carries only `SENTRY_DSN`; the compose frontend service sets only `SENTRY_DSN`; `infra/.env.staging.example` has only `SENTRY_DSN=`. (The backend service does set `ENVIRONMENT: staging`; the frontend does not.) Batch 1.3 scope is unchanged and fully written out in roadmap v2.0.
- `e2e.yml` unchanged (workflow_dispatch-only; promotion 0/3). `ci.yml` includes backend coverage reporting (not a frontend gate).

---

## Week 9 Integration (44-week plan → frontend roadmap)

Week 9 of `planning/Roadmap/44-WEEK-EXECUTION-PLAN .md` — "Document Status Surface + Ingestion Hardening" — assigns: backend status-surface expansion (processed-document surface + per-course listing) and an admin reprocess path (`POST /materials/{id}/process`, shape TBD); AI golden-set ingestion + Arabic normalization + OCR benchmark; DevOps ingestion CI + alarms; **frontend: extracted-text viewer per document/page**.

Repository evidence at `2eccad0`:

| Week 9 deliverable | Exists today? | Evidence | Frontend disposition |
|---|---|---|---|
| Per-course materials listing | Yes | `GET /v1/courses/{id}/materials` in `docs/openapi.json` | Already classified consumable; list UI is Batch 4.3 scope |
| Processed-document / extracted-text read surface | **No** | No such endpoint in the contract; zero document-content endpoints | **Blocked** — extracted-text viewer (the Week 9 frontend assignment) has no API to consume; IA-reserved as a course-hub slot (roadmap §8); implemented only when the contract lands |
| Admin reprocess path (`POST /materials/{id}/process`) | **No** | Absent from the contract; shape is TBD in the plan | **Blocked/future** — reprocess control UI is explicitly NOT built until the endpoint exists with a stable shape; the old "no retry/reprocess UI" exclusion is narrowed accordingly (it excluded building against nothing, not the planned capability) |
| Golden set / Arabic normalization / OCR benchmark | Backend/AI-pod work | `backend/tests/test_material_api.py` covers contract behavior; golden-set runner is AI/DevOps-owned | Not frontend scope; outcomes (honest failure modes) feed Batch 4.3's failed-state copy |
| Ingestion CI tests + failure alarms | DevOps work | Present in plan; not frontend | Not frontend scope |

Week 9 is therefore **represented, not implemented**: the extracted-text viewer is the first blocked-tier item in the coverage matrix, the hub-slot reservation carries it, and no Week 9 work is marked complete. The immediately following weeks (10–17) are reconciled the same way in roadmap §12 — each frontend assignment is classified against the contract that must exist before it can be built.

---

## Backend → Frontend Coverage State (summary)

The full matrix lives in roadmap v2.0 §6 (columns: capability | API/contract | status | frontend surface | persona | batch/week | dependency | classification). Classification tiers:

- **A — Consumable now (12 operations):** auth/me, profile read/update, course CRUD, materials upload-url/register/list/status. Frontend: 8 of 12 consumed today (auth, profile×2, courses×5); the 4 materials operations are scheduled scope (Batch 4.3). `/health` and `/metrics` are infrastructure (tier D).
- **B — Backend exists, frontend blocked:** none. Every existing user-facing capability is either consumed or scheduled; nothing existing is unbuildable.
- **C — Future roadmap capabilities (44-week plan):** extracted text/document surface (W9), retrieval search (W10), chunk inspection (W11), ranked citations (W13), RAG citations (W14), chat sessions + streaming (W15–16), enrollment + student flow (W17), knowledge graph / quizzes / mastery / analytics (W21+). All IA-reserved or honest-copy only; each names its missing contract.
- **D — Internal / infrastructure, no UI:** `/health`, `/metrics`, Celery pipeline internals, LiteLLM gateway traffic, Langfuse, MinIO, observability stack, OpenAPI tooling, CI eval jobs.
- **E — Intentionally not exposed:** admin UI (role unenforced — no capabilities to expose), v4 spec §22.4 planned-only endpoints, server-side route protection (architecture decision), i18n framework (RTL-readiness via logical properties stays).

No frontend-relevant backend capability is silent.

---

## Execution History (concise, authoritative)

| Batch | Date | Baseline | Scope | Result |
|---|---|---|---|---|
| Pre-context authoring | 2026-10-01 | `staging @ c51f3f1` | Roadmap v1.0 → v1.1 verification pass; 15/18 batches verified clean, 3 with corrections; ledger seeded | Complete |
| FR-REB-00 | 2026-10-08 | `frontend-redesign @ 4c55ecd` (contains `staging @ d3d5887`, AI Week 7–8) | Documentation-only re-baseline: lifecycle rules paths/methods fixed; roadmap reconciled in place (v1.2); ledger re-baselined | Complete; patch `frontend-redesign-FR-REB-00-rebaseline.patch`; upstream commit `c45aa7f` |
| FR-REB-01 | 2026-10-08 | `c45aa7f` | Documentation-only product/UX amendments A–D: materials surface promoted to scheduled Batch 4.3 scope; role-aware IA (§3.5); near-term IA reservation (§3.6); Sentry chain written out; counting slips fixed | Complete; patch `frontend-redesign-FR-REB-01-product-ux-roadmap-amendments.patch`; upstream commit `ad64e0c` |
| Staging sync | 2026-10-08 | `2eccad0` = merge of `staging @ d1ba348` (PR #78, backend Week 8) | Backend contract deliverables landed: `docs/openapi.json` + regeneration tool + drift guard + material API tests + explicit auth schema; zero frontend changes | Applied upstream; the rewrite premise of FR-REB-02 |
| **FR-REB-02** | **2026-10-08** | **`2eccad0`** | **Documentation-only full rewrite of all three execution-context files** — roadmap v2.0 authored fresh from repository evidence (no amendment layering), coverage matrix added, Week 9 integrated, ledger rewritten with current state + concise history, lifecycle rules rewritten for the current protocol | **Complete; patch `frontend-redesign-FR-REB-02-full-roadmap-rewrite-week9.patch`** |
| **0.1** | **2026-10-14** | **`699c496`** (= FR-REB-02 patch commit; contains `2eccad0` + `staging @ d1ba348`) | **Baseline verification run (read-only)**: lint/typecheck/unit/storybook/build all PASS (22 unit tests, 42 stories, 9 routes); E2E trio NOT RUN (credentials absent, suite correctly skipped 3/3); F5 live probe BLOCKED; staging CORS preflight BLOCKED — no Docker daemon in the execution environment, no E2E credentials, staging hosts unreachable; all Bucket A findings re-verified present in code | **PARTIALLY EXECUTED at first pass → completed same day by the local verification run (next row); patch `frontend-redesign-0.1-baseline-verification-run.patch` (ledger + baseline record); applied upstream as `bea19f3`** |
| **0.1-completion** | **2026-10-14** | **`bea19f3`** (local run against the applied 0.1 patch; the verification script was committed upstream as `7ebe978` immediately after the run) | **Local verification run on the owner machine** via `scripts/run-batch-0.1-local-verification.sh`: dev stack healthy (db + Keycloak containers, backend :8000, frontend :3000); E2E trio **3/3 PASS** (Chromium, serial, real Keycloak: courses-crud 1.3s, login 1.3s, profile-roundtrip 1.5s); F5 live probe **PASS** (HTTP 200, COUNT=5 WITH_OFFSET=5, sample `2026-10-14T15:52:48.551399Z`, token captured via the real browser login flow, redacted in all logs); local CORS preflight **PASS** (HTTP 200, `access-control-allow-origin: http://localhost:3000`, `authorization` header allowed, credentials true); staging preflight skipped (owner scoped the run to local) | **Complete — Batch 0.1 EXECUTED; evidence dir `../openlearn-batch-0.1-evidence/run-20261014-190840`; Open Question #1 CLOSED** |
| **0.2** | **2026-10-15** | **`7ebe978`** | **Scope freeze (documentation-only)**: new decision note `OpenLearn-AI_Batch-0.2_Scope-Freeze_Decision-Note.md` ratifying roadmap v2.0 §6 (capability classification, tiers A–E), §22 (exclusion list), §19 (demo journey candidate); finding disposition register F1–F6/W1–W8/S1–S11 (20 findings → exactly one bucket each; F2/W2/W3/S6/S11 verified unassigned in both roadmap v1.3 and v2.0 and recorded as retired); F5 settlement decision (schema frozen as-is; 1.4 reduces to the dashboard metric inventory); environment posture recorded (Q1 closed; Q2 → 2.1). Ledger + decision note only; roadmap DOCX untouched | **Complete — Gate A PASSED (2026-10-15); patch `frontend-redesign-0.2-scope-freeze.patch`** |
| **1.1** | **2026-10-15** | **`18d8a69`** (= 0.2 patch commit; Phase 0 complete, Gate A passed) | **Correctness fixes on core flows**: F3 `key={course.id}` on the edit-mode CourseForm; F4 `key={profile?.id ?? "new"}` on ProfileForm; S10 success token `text-success-foreground` → `text-success`; F6 `safeRedirectTarget` moved to `features/auth/redirect.ts` with its documentation aligned to the actual policy (open-redirect logic unchanged) + 15 focused policy tests. Sandbox matrix green (lint, typecheck, unit 37/37, storybook 42/42, build); E2E re-run + manual light/dark S10 check completed on the owner machine (next row) | **EXECUTED — patch `frontend-redesign-1.1-correctness-fixes-core-flows.patch`; applied upstream by Seyam as `7dc9f67`** |
| **1.1-completion** | **2026-10-15** | **`7dc9f67`** (the 1.1 patch applied upstream and pushed by Seyam) | **Owner-machine verification run** completing 1.1's two pending items, reported by Seyam after the original 1.1 report: E2E trio **3/3 PASS** (`npm run test:e2e`: courses CRUD, Keycloak login, profile round-trip — `E2E_USERNAME`/`E2E_PASSWORD` supplied locally, never recorded in repository files); Storybook **42/42 across 12 files**; lint PASS; typecheck PASS; production build PASS with all 9 application routes; manual light+dark check of the success message **successful (owner-verified manual testing)**. Storybook warnings recorded as warnings, not failures: Vite native config loader ESM/CJS notice, unmatched `stories/**/*.mdx` pattern, Base UI `nativeButton` semantics in some stories — explicitly not fixed (outside 1.1/1.2 authorized scope) | **Complete — Batch 1.1 EXECUTED (2026-10-15)** |
| **1.2** | **2026-10-15** | **`7dc9f67`** (+ the 1.1 close-out ledger update) | **Authentication surface completion**: W1 global 401 recovery — new `lib/session-recovery.ts` (clear-cache → `/login?redirectedFrom=…`, one-shot latch) + cache-level error observers in `lib/query-provider.tsx` + the missing token-expired event wired in `lib/keycloak.ts` (init options untouched) + React-state mirror in `lib/auth-context.tsx` feeding the unchanged AuthGuard + the two forms' static expired-session strings replaced by redirect-expectation copy; S3 register flow — error/loading/null-client states + theme toggle in `app/(auth)/register/page.tsx` (`keycloak.register` call site and redirect target unchanged); S8 — new styled `app/(auth)/error.tsx` + `loading.tsx` mirroring `(app)`. 12 focused unit tests added. Sandbox matrix green (lint, typecheck, unit 49/49, storybook 42/42, build); login E2E + three manual auth validations pending on the owner machine (no Docker/credentials in the execution environment; suite self-skipped 3/3, exit 0) | **PARTIALLY EXECUTED — implementation complete; owner validation pending; patch `frontend-redesign-1.2-authentication-surface-completion.patch`** |
| **1.3** | **2026-10-15** | **`f87c765`** (= 1.2 patch commit) | **Observability and configuration closure**: F1 chain wired across all five primary files — `frontend/Dockerfile` gains the `NEXT_PUBLIC_SENTRY_ENVIRONMENT` ARG/ENV pair (existing convention) and mounts `SENTRY_AUTH_TOKEN`/`SENTRY_ORG`/`SENTRY_PROJECT` as BuildKit secret mounts on the `npm run build` RUN (no ARG/ENV persistence — never in layers, never at runtime); `deploy-staging.yml` passes the matching build-argument (vars-with-fallback pattern per ci.yml's own use of the variable, fallback `'staging'`), adds the three secrets via build-push-action's `secrets` input, and its `.env.runtime` heredoc gains `SENTRY_ENVIRONMENT` from the same expression as the build arg (structural client/server label parity); `infra/docker-compose.staging.yml` frontend service receives `SENTRY_ENVIRONMENT=${SENTRY_ENVIRONMENT}` (DSN handling untouched); `infra/.env.staging.example` gains the five keys with build-time/runtime annotations and empty secret placeholders; W8 — `engines.node: "^20 || ^22"` in `frontend/package.json` from CI (Node 20 in ci/e2e/storybook) + deploy (node:22-alpine) evidence, lockfile root entry synced. Chain-consistency script 40/40; sandbox matrix green (lint, typecheck, unit 49/49, storybook 42/42, build 9 routes with the staging label exercised). **Sentry staging runtime verification BLOCKED / NOT VERIFIED** — requires the upstream-applied deployment, the three GitHub Secrets configured, and Sentry project access | **PARTIALLY EXECUTED — implementation complete; runtime verification outstanding; patch `frontend-redesign-1.3-observability-configuration-closure.patch`** |
| **1.4** | **2026-10-17** | **`b56be14`** (= 1.3 patch commit) | **Data contract settlement**: F5 settled from the 0.1 result — the live API emits offset-bearing datetimes matching the tracked `date-time` contract, so the `offset: true` schema stays frozen as-is (**zero schema change**; `features/courses/schemas.ts` byte-identical; the naive-emission contingency and the note-to-the-backend-pod contingency are both dead); 5 focused tests + 2 evidence-based fixtures added to `lib/api.test.ts` pinning the real `courseResponseSchema` at the apiFetch boundary (UTC `Z` shape — the exact probe sample; explicit `±HH:MM` shape; naive rejection — never silently coerced to UTC; plus a list-shaped boundary test carrying both shapes and a single-object naive-rejection boundary test through the existing error taxonomy); the real dashboard-metric inventory (course count, profile completeness; source data, calculation, interpretation, limitations — no analytics endpoints exist, nothing invented) written into this ledger's 1.4 log entry as the documented location. Sandbox matrix green (lint, typecheck, unit 54/54, storybook 42/42, build 9 routes); **live-API validation BLOCKED / NOT RUN** (no Docker/credentials in the execution environment; test-file + ledger only, zero runtime code changed) | **PARTIALLY EXECUTED — implementation complete; live-API validation outstanding; patch `frontend-redesign-1.4-data-contract-settlement.patch`** |
| **1.4-closeout** | **2026-10-18** | **`92b67bd`** (= PR #79 merge; the 1.4 patch applied upstream as `e10249f`, then the course-ownership fix merged on top) | **Evidence-based closeout review (documentation-only)**: preflight verified (fetch; local branch 0-ahead/2-behind; fast-forward; the stale Phase 2 working-tree state preserved in a stash); PR #79 verified against fetched history (implementation `65c8a8c` + merge `92b67bd`; exactly the four ownership files; merged diff byte-identical to the delivered ownership patch) and kept distinct from Batch 1.4 (`e10249f`); fresh verification at `92b67bd`: frontend unit 54/54 (F5 file 17/17), lint, typecheck PASS; backend ruff + course/OpenAPI-contract 32/32 on a disposable scratch PostgreSQL; core regression 254 passed / 1 pre-existing environmental failure (docling absent); live-API validation still BLOCKED / NOT RUN | **Closeout complete; batch status unchanged (PARTIALLY EXECUTED); patch `frontend-redesign-1.4-closeout-evidence-based-review.patch`** |
| **2.1 (discovery)** | **2026-10-18** | **`60d3ba5`** (= the 1.4 closeout patch applied and committed by Seyam; verified byte-identical to the delivered closeout patch) | **Demo journey, page architecture, and environment lock (documentation + provisioning)**: preflight verified `60d3ba5` and preserved the execution clone; ledger addendum records 1.4's live-API validation as owner-confirmed (status → EXECUTED with attribution, no criterion redefined); nine-route inventory re-confirmed; material journey audited (API-complete; frontend = 4.3; local compose lacks storage/broker/worker); IA recommendation within the frozen classification; five-entry design-reference shortlist; 11-step journey table with readiness ratings; local-first runbook + dataset plan; instructor-account provisioning implemented (not executed in sandbox); roadmap reconciliation items R1–R9 recorded | **PARTIALLY EXECUTED — journey/dataset lock + owner-machine rehearsal outstanding; patch `frontend-redesign-2.1-discovery-demo-journey-environment-lock.patch`** |
| **2.1 (decision-lock)** | **2026-10-18** | **`005711e`** (= the 2.1 discovery patch applied and committed by Seyam; verified as exactly the patch's six files) | **Product-owner decision lock (documentation-only)**: fresh isolated clone at `005711e`; every decision verified against repository evidence before recording — A local-first APPROVED (dev compose re-verified: db + keycloak + bootstrap only; no storage/broker/worker); B substantial redesign APPROVED (authenticated-`/` redirect not yet implemented — recorded as direction; S2 re-verified present); C scoped architecture APPROVED (no plugin/discovery machinery; nine routes re-counted); D material journey APPROVED with two honest qualifications (end-to-end never ran locally; resulting-state = status + list only); Batch 4.3 identifier verified verbatim in the DOCX; E roles/ownership **CLOSED** on owner-confirmed acceptance (labeled as acceptance, not an automated-suite re-run); onboarding contract audit completed — **all six candidate profile fields already supported** (`ProfileUpdate`/`ProfileResponse`, spec §15.1, DB constraints; PUT = full-replacement upsert; GET 404 = no-profile trigger); language/RTL APPROVED as policy, implementation PENDING EVIDENCE (`dir="ltr"` hardcoded; `profiles.preferred_language` en/ar exists; no i18n mechanism); dataset locked to `custom_custom_english_born_digital_005_p001.pdf` (56,951 B, 3,501 chars) + `custom_custom_arabic_born_digital_003_p004.pdf` (41,392 B, 1,797 chars) — all 30 folder candidates extraction-tested via pypdfium2; R1–R9 re-verified OPEN, disposition = the documentation batch after the environment batch; three genuine owner questions recorded (onboarding batch assignment; enum vocabularies; language/RTL staging) | **Complete; new decision record + this ledger; patch `frontend-redesign-2.1-decision-lock-product-direction-record.patch`** |

Facts preserved from the earlier passes that remain verified and current: the AI Week 7–8 pipeline closeout (B0–B11, staging-proven, H4 delivered 2026-10-08); CORS resolution at compose level; the 2026-10-01 verification pass corrections (S10 both-themes scope, F1 deployment-only scope, Batch 3.1 re-scope to ratifying the existing token layer); the Week 8 mapping delta of the 44-week plan (superseded as a blocker when the AI pod closed Weeks 7–8; the plan's project-level Week 8 items — v0.2.0 tag, coverage baseline, OpenAPI publication, docs site — are now partially delivered upstream: **OpenAPI publication has landed**; tag/coverage/docs-site remain non-frontend items).

---

## Execution Log

### FR-REB-02 — Full execution-context rewrite + Week 9 integration (documentation-only)

Status: **COMPLETE** (2026-10-08)

#### Planned
Rewrite all three execution-context files from the current repository state (`frontend-redesign @ 2eccad0`, containing `origin/staging @ d1ba348`): (1) lifecycle rules rewritten for the current protocol including the 44-week plan and OpenAPI contract as mandatory in-scope reads; (2) roadmap DOCX fully rewritten (in-document revision v2.0) as a coherent execution document with the backend→frontend coverage matrix, Week 9 integration, role-aware IA, material lifecycle UX, and the 44-week near-term alignment; (3) this ledger rewritten as the authoritative current execution state. **No frontend implementation; no backend change; no CI/deploy change.**

#### Actual
Executed as planned. Repository verified first (branch, HEAD, remote heads, staging containment, clean tree; the local clone from the FR-REB-00 session was stale at `4c55ecd` and was replaced with a fresh clone of `origin/frontend-redesign @ 2eccad0` — no history rewritten). Inspection pass re-derived from the tree: frontend file inventory (9 routes, 3 slices, 22 unit tests / 12 story files / 3 E2E specs — all unchanged since `c51f3f1`, verified via `git diff c51f3f1..HEAD -- frontend` showing only the two relocated docs deleted); the full API contract extracted from the new `docs/openapi.json` (12 application operations + `/health` + `/metrics`, every schema shape recorded above); RBAC re-derived (instructor+ownership enforced on material writes, `require_admin` zero call sites, course listing unscoped); AI pipeline re-confirmed worker-internal with deterministic `document_id`; F1 Sentry chain re-verified open at every file; Week 9 deliverables checked one by one against the contract (per-course listing exists; processed-document surface, reprocess endpoint, and extracted-text surface do not). The 44-week plan was read in full; Weeks 7–17 read in detail and reconciled.

Rewrites produced: lifecycle rules — current protocol, patch-name immutability, stale-clone resolution rule, documentation-only verification clause, OpenAPI drift-guard reference; roadmap DOCX — 25-section structure authored fresh (see its own §1 reading guide), all counts corrected (12 operations, 9 pages, 22/42/3 test counts), no FR-REB-00/01 patchwork remnants, no stale `c51f3f1`-as-current claims; ledger — this file.

#### Files changed
Exactly the three authorized files:
- `docs/tasks/Frontend UI redesign/GLM-batch-n-patch-lifecycle-rules.md`
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md`
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx`

#### Verification
- Git scope: `git status --short`, `git diff --name-only`, `git diff --cached --name-only`, `git ls-files --others --exclude-standard` — exactly the three authorized files modified, nothing staged, no untracked files.
- DOCX: ZIP integrity test passed; full text re-extracted after the rewrite and reviewed; internal cross-references (§ numbers, matrix rows, batch IDs, gate letters) checked consistent; the document opens with `python-docx` cleanly.
- Consistency: ledger ↔ roadmap ↔ lifecycle rules cross-checked (baseline hashes, operation count, batch structure 6 phases / 18 batches / Gates A–F, Week 9 classification, next-batch pointer).
- Stale-content sweep: zero occurrences of "eleven operations" (correct 12), zero "Eight page files"/"8 pages", zero `frontend/docs` path references, no "FR-REB-00 then FR-REB-01" narrative inside the roadmap, no superseded-CORS or dead-seam current-state claims.
- NOT run (correctly, per the documentation-only scope): lint, typecheck, unit tests, Storybook, build, E2E — no application code was touched, and claiming such runs would violate the honesty rules.

#### Issues / deviations
None blocking. Records: (1) the working clone inherited filemode noise (filesystem reporting `100755` broadly); the fresh clone resolved it — no source file's content changed; (2) the previous ledger's "eleven operations" wording contained an arithmetic slip against its own parenthetical (5+4+1+2); the OpenAPI-derived count 12 is now authoritative; (3) the roadmap TOC is a field code — page numbers refresh on first open (reader action, noted in the document).

#### Commit
N/A (executor does not commit; Seyam applies the patch
`frontend-redesign-FR-REB-02-full-roadmap-rewrite-week9.patch`).

#### Gate impact
None — no gate passed. Gate A remains next, now running against the rewritten context.

---

### 0.1 — Baseline verification run (read-only)

Status: **PARTIALLY EXECUTED → EXECUTED** (completed 2026-10-14 by the local verification run — see the 0.1-completion entry below)

#### Planned
Read-only baseline verification per roadmap Phase 0: run lint, typecheck, unit, storybook, build; run the three E2E specs with real Keycloak credentials; perform the authenticated F5 live probe (`GET /v1/courses`) and inspect the emitted `created_at` representation; confirm the staging CORS preflight for the web origin; re-verify the Bucket A findings against the tree; record the baseline. No code, no configuration, no dependency changes.

#### Actual
Executed on a fresh clone of `origin/frontend-redesign` @ `699c496` (equal to remote HEAD; the FR-REB-02 patch commit on top of baseline `2eccad0`; staging containment re-verified; working tree clean at start). `npm ci` installed from the lockfile without touching it. Results of the six script runs:

1. `npm run lint` — **PASS**, exit 0, no findings.
2. `npm run typecheck` — **PASS**, exit 0 (`tsc --noEmit`, TS 5.9.3).
3. `npm run test` (vitest unit project) — **PASS**, exit 0: 22/22 tests across 3 files (`lib/api.test.ts` 12, `features/courses/api/course-query-options.test.ts` 5, `features/courses/keys.test.ts` 5) — matches the counts recorded at `2eccad0`.
4. `npm run test:storybook` — **PASS**, exit 0: 42/42 tests across 12 story files, axe fail-on-violation active, headless Chromium (playwright v1243 browser build) — matches the counts recorded at `2eccad0`.
5. `npm run build` — **PASS**, exit 0, with the CI-documented fallback `NEXT_PUBLIC_*` values passed as environment variables (no repo file created): 9 app routes + `/_not-found` compiled and prerendered.
6. `npm run test:e2e` — **NOT RUN as flows**: all three specs correctly self-skipped (`3 skipped`, exit 0) because `E2E_USERNAME`/`E2E_PASSWORD` are absent from the execution environment and no credentials may be fabricated. The documented local stack cannot run here (no Docker daemon: no `db`/`keycloak` containers, therefore no Keycloak and no backend on :8000), and the staging target is network-unreachable from the execution environment (see below). This is a missing-prerequisite block, not a test failure.

Environment checks:

7. **F5 live probe — BLOCKED.** The authenticated `GET /v1/courses` could not be performed: no credentials exist in the execution environment (none fabricated, per batch rules), no local stack is possible (Docker absent), and the documented staging API host does not answer from this environment. Contract facts re-confirmed from the tracked `docs/openapi.json` (v0.2.0): `CourseResponse.created_at` is declared `format: date-time`, `GET /v1/courses` requires `HTTPBearer`, and the spec declares no `servers` block — the target URL comes from environment documentation. **Live emission of offset-bearing datetimes remains UNVERIFIED; Open Question #1 stays open.** Probe spec for the rerun: authenticated `GET {API}/v1/courses` with `Authorization: Bearer <real token>`; inspect the raw `created_at` string for a timezone offset (`Z` or `±HH:MM`).
8. **Staging CORS preflight — BLOCKED.** `OPTIONS https://openlearn-api-staging.duckdns.org/v1/courses` with `Origin: https://openlearn-web-staging.duckdns.org`, `Access-Control-Request-Method: GET`, `Access-Control-Request-Headers: authorization` — connection timed out after 15 s (no HTTP response). Diagnostics: DNS resolves the host (16.170.158.155); general egress from the execution environment works (control request to github.com returned 200); ports 443 and 80 to the staging host both time out. The compose-level CORS configuration (`CORS_ORIGINS=https://openlearn-web-staging.duckdns.org,http://localhost:3000`) is unchanged and remains verified at file level; the live preflight confirmation (Open Question #2) stays open and must be run from a host with network access to staging. No infrastructure was changed.

Bucket A findings re-verified present in code at `699c496` (all unchanged from the `2eccad0` verification): F3 (`CourseForm` in `app/(app)/courses/[id]/edit/page.tsx` rendered without `key={course.id}`), F4 (`ProfileForm` in `app/(app)/profile/page.tsx` not re-keyed), F5 (`features/courses/schemas.ts:25` — `created_at: z.string().datetime({ offset: true })`), F6 (`safeRedirectTarget` comment/code drift in `components/auth/LoginForm.tsx`), S1 (exactly five "Coming soon" strings in `app/(app)/dashboard/page.tsx`), S2 (landing markets RAG chat/knowledge graph/quizzes/flashcards), S8 (`(auth)` has no error.tsx/loading.tsx; `(app)` has both), W5 (`shadcn` in runtime dependencies), W6 (six `"latest"` devDependencies), W7 (`chromaui/action@latest` unpinned in `storybook.yml`), W8 (no `engines` field), F1 chain open (Dockerfile has no `NEXT_PUBLIC_SENTRY_ENVIRONMENT` ARG; deploy workflow and compose carry DSN only; `.env.staging.example` DSN only).

#### Files changed
Exactly one file — this ledger:
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md`

No application code, test, configuration, dependency, lockfile, CI, or infrastructure file was modified, created, or deleted. `frontend/test-results/` (empty Playwright output of the skipped run) was removed after the run; the final tracked tree is byte-identical to `699c496`.

#### Verification
- Git scope: `git status --porcelain` after all runs shows only this ledger modified; no staged changes; no untracked residue.
- Patch: generated with the isolated-clone `--binary` method at start commit `699c496`; validated with `git apply --check` + apply on a pristine checkout, byte-identical re-check.

#### Issues / deviations
1. **Three checks blocked (missing prerequisites, not failures):** E2E trio (no credentials + no local stack possible), F5 live probe (no authenticated environment), staging CORS preflight (staging hosts unreachable from the execution environment — TLS timeouts while general egress works). Each is reproducible evidence for the rerun.
2. **Node version deviation:** the execution environment runs Node 24.21.0 / npm 11.19.0; CI pins Node 20. All five script checks are green on Node 24. Not a repository change; recorded as an environment limitation for the baseline.
3. **Completion criterion not met:** the roadmap requires "baseline record exists; every Bucket A item confirmed or reclassified with evidence". Bucket A items are all confirmed with evidence, but the F5 live answer and the CORS preflight confirmation are named Gate A evidence (roadmap §21) and could not be produced here. **Batch 0.1 therefore remains incomplete until the three blocked checks are rerun in an environment with Docker + E2E credentials (local stack) or staging access.** Gate A is NOT passed and must not be claimed.

#### Commit
N/A (executor does not commit; Seyam applies the patch
`frontend-redesign-0.1-baseline-verification-run.patch`).

#### Gate impact
None at first pass — the batch was completed the same day by the local verification run below.

---

### 0.1 — completion: local verification run (owner machine, 2026-10-14)

Status: **COMPLETE** — Batch 0.1 is **EXECUTED** (2026-10-14)

#### Planned
Complete the three checks blocked in the executor's sandbox by rerunning them where the prerequisites exist: the owner's local project (explicitly NOT staging, per Seyam's instruction), using the purpose-built `scripts/run-batch-0.1-local-verification.sh` (delivered by the executor, committed by Seyam as `7ebe978`). The script orchestrates the documented local stack (docker compose `infra/docker-compose.dev.yml` db + Keycloak, backend :8000, frontend :3000), runs the E2E trio with real Keycloak credentials sourced from `.env.local` (never hardcoded), performs the F5 live probe with a REAL access token captured through the browser login flow (no auth weakening; token redacted from all logs), and runs the local CORS preflight. Staging preflight is opt-in (`--with-staging-preflight`) and was not requested.

#### Actual
Run `run-20261014-190840` (2026-10-14T19:08+03:00), executed by Seyam on the owner machine against `bea19f3` + the untracked script. Results:

- **Local stack — PASS (3/3):** `infra-db-1` and `infra-keycloak-1` up (compose dev); Keycloak OIDC discovery answered; backend `GET /health` OK on :8000 (already running, reused); frontend `GET /` OK on :3000 (already running, reused).
- **E2E trio — PASS 3/3** (Chromium, 1 worker, serial, 6.9s total): `courses-crud.spec.ts` create→read→update→delete through the UI (1.3s); `login.spec.ts` Keycloak authentication landing on /dashboard (1.3s); `profile-roundtrip.spec.ts` create→reload→update persistence (1.5s). `E2E_USERNAME`/`E2E_PASSWORD` supplied locally from `.env.local` (`OPENLEARN_TEST_USER_PASSWORD`); nothing fabricated; `frontend/test-results/` relocated into the evidence dir.
- **F5 live probe — PASS:** a real access token was captured via the browser login flow (TOKEN_CAPTURED=yes; token redacted everywhere, file mode 0600, trap-cleaned). Authenticated `GET http://localhost:8000/v1/courses` → HTTP 200; `created_at` analysis: **COUNT=5, WITH_OFFSET=5** (100% offset-bearing), sample `2026-10-14T15:52:48.551399Z`. **The live API emits offset-bearing datetimes — the `z.string().datetime({ offset: true })` schema at `features/courses/schemas.ts:25` is correct as-is. Open Question #1 is CLOSED; Batch 1.4's F5 settlement reduces to keeping the schema and writing the dashboard real-metric inventory.**
- **Local CORS preflight — PASS:** `OPTIONS http://localhost:8000/v1/courses` with `Origin: http://localhost:3000`, `Access-Control-Request-Method: GET`, `Access-Control-Request-Headers: authorization` → HTTP 200; `vary: Origin`; `access-control-allow-origin: http://localhost:3000` (origin echo); allow-methods `DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT`; `access-control-allow-headers: authorization`; `access-control-allow-credentials: true`; max-age 600. The compose-provided `CORS_ORIGINS` mechanism is confirmed working end to end for the local web origin.
- **Staging preflight — SKIPPED by scope** (not requested; Seyam directed verification to the local project only). Open Question #2 remains open as a live confirmation and is routed to Batch 2.1's environment lock, where the staging-vs-local demo decision is made anyway (local dev is the documented fallback). It can be closed at any time with `bash scripts/run-batch-0.1-local-verification.sh --with-staging-preflight` from any host that can reach staging.
- **Fast checks — SKIPPED by design** (`--with-fast-checks` not passed): lint/typecheck/unit/storybook/build already PASS conclusively from the 2026-10-14 baseline run; the script avoids redundant re-runs.
- Post-run repository state: no tracked changes; the script was then committed and pushed by Seyam as `7ebe978`.

#### Files changed
None in this completion step beyond this ledger and the in-repo baseline record addendum (both documentation records of the run):
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md`
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-0.1_Baseline-Record.md` (addendum §8 + final verdict §9)

#### Verification
Evidence is the run's own output (verbatim verdict block pasted by Seyam on 2026-10-14): `VERDICT: BATCH 0.1 LOCAL VERIFICATION PASSED (exit 0)` with the per-check PASS/SKIPPED table and the F5 analysis line. Combined with the five conclusive script runs from the baseline run, all eight Batch 0.1 checks are now concluded. The baseline record's addendum records the full evidence table.

#### Issues / deviations
1. **Staging CORS preflight not produced (owner scope decision, not a failure):** Seyam explicitly scoped verification to the local project. The roadmap lists the CORS preflight confirmation as Gate A evidence; the LOCAL preflight (same compose-provided mechanism, same origin model) is confirmed, and the staging-host confirmation is carried as Open Question #2 into Batch 2.1, where it is a named input to the environment decision. Recorded as a deviation rather than silently claimed.
2. **Local run used already-running services** (backend :8000, frontend :3000 reused; containers up) — consistent with the script's idempotent design; no auth weakening was required anywhere (real Keycloak, real token capture).

#### Commit
N/A (executor does not commit; Seyam applies the patch
`frontend-redesign-0.1-completion-local-verification.patch`).

#### Gate impact
Batch 0.1 completion criterion met: the baseline record exists and every Bucket A item is confirmed with evidence. Gate A now awaits only the 0.2 scope freeze.

---

### 0.2 — Scope freeze (documentation-only)

Status: **COMPLETE** (2026-10-15) — **Gate A PASSED**

#### Planned
Per roadmap v2.0 §14: freeze the classification, defer list, exclusion list, and the demo journey candidate. Files affected: none in the application; the decision note in repo docs plus this ledger. §6 becomes the authoritative capability classification, §22 the authoritative exclusion list, §19 the demo candidate. Validation: every capability in exactly one tier; every finding F1–F6, W1–W8, S1–S11 in exactly one bucket, defer entry, or exclusion. The modernization accomplishments (§2) remain permanently out of scope.

#### Actual
- **Decision note authored:** `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-0.2_Scope-Freeze_Decision-Note.md` (new file) with nine sections: purpose/authority, frozen capability classification (tier table A–E + §13 visibility snapshot), the finding disposition register (25 rows: 20 dispositions + 5 retired IDs), the F5 settlement decision, environment/CORS posture, the frozen demo journey candidate, exclusion-list ratification, the freeze validation table, and the decision record.
- **Finding register reconstruction:** roadmap v2.0 names the ID ranges but carries no consolidated register, so every assignment was recovered and cross-checked: from v2.0's batch objectives and gate table (F3/F4/S10/F6→1.1; W1/S3/S8→1.2; F1/W8→1.3; F5→1.4; S1/S2→2.2; S4/S5/S7/S9→3.2; W4→3.3; W5→3.2; W6/W7→5.3) and from the v1.3 register (extracted from git history at `ad64e0c` — the superseded DOCX still in history) for the finding definitions. **F2, W2, W3, S6, S11 have zero occurrences in both v1.3 and v2.0 outside the range notation** — they carry no findings and are recorded as retired IDs so the validation ranges close cleanly and nobody hunts for ghosts.
- **F5 settled from 0.1 evidence:** the live API emits offset-bearing datetimes (5/5, sample `2026-10-14T15:52:48.551399Z`); the `offset: true` schema is frozen as-is; Batch 1.4 reduces to the dashboard real-metric inventory. Open Question #1 closed.
- **Gate A declared PASSED (2026-10-15):** functional reality known and agreed — baseline record complete (all eight 0.1 checks concluded), classification frozen. One evidence item carried by owner decision (staging-host CORS preflight → Open Question #2 → Batch 2.1; local preflight confirmed; owner explicitly scoped 0.1 verification to the local project). Recorded as a deviation with owner authorization, not silently claimed.
- **No DOCX edit:** the batch ratifies §6/§19/§22 as authoritative — it does not modify them (lifecycle: never silently change the roadmap; §2 modernization accomplishments protected).

#### Files changed
Exactly two files:
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-0.2_Scope-Freeze_Decision-Note.md` (new)
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md` (this ledger: Current State, history row, this log, status board, gates line, next-batch pointer)

#### Verification
- Documentation-only verification per the lifecycle rules: both documents readable and internally consistent; batch IDs, gate letters, finding IDs, and tier letters cross-checked against roadmap v2.0 §6/§13/§14/§19/§21/§22 and the ledger; no document claims work that did not happen.
- Occurrence audit (mechanical): F2/W2/W3/S6/S11 — zero hits in roadmap v1.3 and v2.0 outside the range notation; every other finding ID's assignment verified in both the v2.0 batch objectives and the v1.3 register tables.
- Git scope: `git status --porcelain` shows exactly the two authorized files; no application code, test, config, dependency, CI, or infrastructure file touched; the roadmap DOCX byte-identical.
- NOT run (correctly): lint/typecheck/unit/storybook/build/E2E — no application file changed; claiming such runs would violate the honesty rules.

#### Issues / deviations
1. **Gate A's CORS evidence item:** the roadmap names "the CORS preflight confirmation" among Gate A evidence. The LOCAL preflight is confirmed; the staging-host preflight was scoped out by Seyam ("not staging env") and is carried as Open Question #2 into Batch 2.1, whose environment decision it feeds anyway (local dev is the documented fallback). Gate A is passed on the local confirmation + owner decision, with the carry-over recorded here, in the decision note (§5), and in the Open Questions table — not silently dropped.
2. **Retired finding IDs:** the validation range "F1–F6, W1–W8, S1–S11" implies IDs that do not all exist. Rather than silently validating a subset, the five unassigned IDs are explicitly recorded as retired (verified against both roadmap versions) so the freeze is auditable.

#### Commit
N/A (executor does not commit; Seyam applies the patch
`frontend-redesign-0.2-scope-freeze.patch`).

#### Gate impact
**Gate A — PASSED (2026-10-15).** Phase 0 is complete. The next batch in the sequence is 1.1 (Phase 1 — Minimal Functional Closure); it does not start until Seyam explicitly authorizes it.

---

### 1.1 — Correctness fixes on core flows

Status: **EXECUTED** (2026-10-15) — implementation complete and sandbox-verified at first pass; the two owner-machine validation items (E2E re-run, manual light+dark success-message check) were completed by Seyam and recorded in the 1.1 completion entry below

#### Planned
Per roadmap v2.0 §14 Batch 1.1 and the frozen finding register (decision note §3): fix the four pinned defects — F3 (edit-mode `CourseForm` lacks `key={course.id}` — wrong-record write), F4 (`ProfileForm` not re-keyed on profile identity; null→object never re-seeds state), S10 (success token `text-success-foreground` invisible in both themes → `text-success`), F6 (`safeRedirectTarget` comment/code drift) — without changing form state machines, safeParse paths, mutations, post-save navigation, or the open-redirect logic itself; keep `courses-crud` and `profile-roundtrip` E2E green; batch prompt additionally requires focused F6 policy tests (safe and unsafe redirect cases).

#### Actual
Executed on a fresh clone of `origin/frontend-redesign` @ `18d8a69` (equal to remote HEAD; working tree clean; staging containment re-verified). Authorization chain verified first: ledger records 0.1 EXECUTED + 0.2 EXECUTED + **Gate A PASSED (2026-10-15)** and names Batch 1.1 as the next batch awaiting Seyam's explicit authorization — this batch's prompt is that authorization. Roadmap v2.0 Batch 1.1 row re-read; the v1.3 finding register (superseded DOCX in git history at `ad64e0c`) was consulted for the precise per-finding mechanics ("align safeRedirectTarget with its comment (reject /api or fix the comment)"; F4 = "the null-to-object profile transition never re-seeds useState"). Findings re-verified present in code at `18d8a69` before editing. Per-finding decisions:

1. **F3 — edit-page form identity.** `app/(app)/courses/[id]/edit/page.tsx`: added `key={course.id}` to the edit-mode `<CourseForm>` (plus a short in-code comment). Verified `useCourse` uses no `placeholderData`/`keepPreviousData`, so navigating A→B remounts the form through the loading pass when B is uncached — but when B is already in the TanStack cache the data arrives without a loading pass and the form instance persists with A's state (the wrong-record write path). The key makes the remount unconditional on identity change. Loading/error/mutation/navigation behavior untouched (`CourseForm.tsx` not modified).
2. **F4 — profile form identity.** `app/(app)/profile/page.tsx`: rendered `<ProfileForm key={profile?.id ?? "new"} profile={profile ?? null} />` (plus a short in-code comment). The `Profile.id` UUID is the profile identity: it is stable across ordinary updates (so a save's cache invalidation → refetch → same id → **no remount** — the `role="status"` success contract the E2E asserts is preserved on the update path), and it changes exactly on the null→object transition (profile established), remounting the form so it re-seeds from the actual profile instead of retaining create-mode defaults. `ProfileForm.tsx` itself was modified only by S10.
3. **S10 — success-message token.** `components/profile/ProfileForm.tsx`: the success message's class swapped from `text-success-foreground` to `text-success` (one class, the exact prescribed change; verified this is the only `text-success-foreground` usage in the app). Token evidence: `app/globals.css` defines light `--success: oklch(0.62 0.18 155)` / `--success-foreground: oklch(0.98 0.01 155)` (near-white — invisible on the light card) and dark `--success: oklch(0.70 0.18 155)` / `--success-foreground: oklch(0.15 0.025 155)` (near-black — invisible on the dark card); `text-success` is the chromatic green readable on both card backgrounds. **The roadmap's manual light+dark visual check was NOT performed** (no running app or display in the execution environment) and is left to the owner; no visual claim is made beyond the token arithmetic.
4. **F6 — `safeRedirectTarget` comment/behavior drift.** Resolution of the v1.3 "reject /api or fix the comment" fork: roadmap v2.0's Batch 1.1 row pins "Must NOT change: … the open-redirect logic itself", so the drift is resolved **comment-side** — the code's actual policy is the intended one (the comment claimed "non-API route" filtering the code never did; the app's web origin serves no `/api` routes at all — verified: no `app/api` directory — and the backend API lives on a separate origin, so no API-path filtering is warranted). Mechanics: the function moved verbatim (byte-identical body, zero behavior change) from `components/auth/LoginForm.tsx` to the new pure module `features/auth/redirect.ts` with corrected documentation; `LoginForm.tsx` imports it (one-line import swap — Keycloak init, token handling, login/register flow, and redirect targets untouched). The move follows the roadmap's own architecture direction (auth domain logic under `features/auth/`, cf. the W4 relocation in Batch 3.3) and makes the function testable in the existing `unit` vitest project (`features/**/*.test.ts`) without touching `vitest.config.ts` or importing a `"use client"` component into node tests.

Focused tests added: `features/auth/redirect.test.ts` — 15 tests pinning the documented policy: rejects null/empty, absolute external URL, `javascript:` scheme, protocol-relative `//…`, `/login` (bare + query), `/register`, nested auth-route path, and the prefix-matching edge `/login-page` (documented as-is); accepts `/dashboard`, `/courses`, deep link with dynamic segment, local route with query string, `/profile`.

Known interaction recorded (not a defect of the update path, disclosed for completeness): on the **fresh-user create path** (profile goes null→object in the same session), the F4 remount re-seeds the form when the refetched profile arrives, which also clears the in-form success message after a short visibility window (the mutation's `invalidateQueries` refetch RTT). The live test user has an existing profile, so the E2E takes the update path where the id is stable, no remount occurs, and the `role="status"` assertion is deterministic — this is the path the owner-side E2E confirmation will exercise. Batch 2.1 provisions a new test user: if that user starts profile-less, the E2E's create path may race the message window; if observed, the honest fix belongs to a future authorized batch (e.g. moving the status announcement to a remount-stable boundary), not to a silent E2E weakening.

#### Files changed
Exactly four authorized application files plus two new files required by the batch prompt's focused-test requirement:
- `frontend/app/(app)/courses/[id]/edit/page.tsx` — F3 key fix (+ comment)
- `frontend/app/(app)/profile/page.tsx` — F4 key fix (+ comment)
- `frontend/components/profile/ProfileForm.tsx` — S10 token swap (one class)
- `frontend/components/auth/LoginForm.tsx` — F6: local function definition replaced by the `features/auth/redirect` import (function body unchanged)
- `frontend/features/auth/redirect.ts` — new (F6): `safeRedirectTarget` verbatim + documentation aligned to the actual policy
- `frontend/features/auth/redirect.test.ts` — new (F6): 15 focused policy tests

No changes to `CourseForm.tsx`, `useProfileMutation.ts`, `useProfile.ts`, `useCourse.ts`, schemas, `vitest.config.ts`, Keycloak initialization, token handling, route guards, E2E specs, backend, CI, infrastructure, or the roadmap DOCX.

#### Verification
Run from `frontend/` on Node 24.21.0 / npm 11.19.0 (CI pins Node 20 — same recorded environment deviation as Batch 0.1; not a repository change):

| # | Command | Result | Exit |
|---|---|---|---|
| 1 | `npm ci` (lockfile untouched) | PASS | 0 |
| 2 | `npm run lint` | PASS — no findings | 0 |
| 3 | `npm run typecheck` | PASS (`tsc --noEmit`, TS 5.9.3) | 0 |
| 4 | `npm run test` (vitest unit project) | **PASS — 37/37** across 4 files (22 pre-existing + 15 new `features/auth/redirect.test.ts`) | 0 |
| 5 | `npm run test:storybook` | PASS — 42/42 across 12 story files, axe fail-on-violation active | 0 |
| 6 | `npm run build` (CI-documented fallback `NEXT_PUBLIC_*` env, no repo file created) | PASS — 9 routes + `/_not-found` | 0 |
| 7 | `npx playwright test` | **NOT RUN as flows — 3 skipped** (exit 0): `E2E_USERNAME`/`E2E_PASSWORD` absent, no Docker daemon (`docker info` exit 127), no `.env.local`, nothing on :8000/:3000 — the specs' documented credential gate self-skips; identical missing-prerequisite block as Batch 0.1. No credentials fabricated; no auth weakened; specs untouched | 0 (skip) |
| 8 | Manual light+dark check of the success message (roadmap validation item) | **NOT PERFORMED** — no running app/display in the environment; token-level evidence recorded under S10 above; left to the owner | — |

Environment checks after the run: working tree contains exactly the six batch-owned files (4 modified + 2 new); `frontend/test-results/` from the skipped E2E run removed.

#### Issues / deviations
1. **Two validation items blocked (missing prerequisites, not failures):** the `courses-crud`/`profile-roundtrip` E2E re-run and the manual light+dark S10 check require the owner machine (Docker + credentials + running stack). The lifecycle rules do not prohibit implementing with blocked verification (0.1 precedent), so implementation proceeded; **Batch 1.1 is NOT marked complete** and Gate B is not claimed. Completion path: apply the patch, run the E2E trio (e.g. via `scripts/run-batch-0.1-local-verification.sh` or `npm run test:e2e` with the documented stack up) and eyeball the success message in both themes.
2. **F6 resolution direction:** the v1.3 wording offered "reject /api or fix the comment"; roadmap v2.0's "Must NOT change … the open-redirect logic itself" selects the comment-side fix. Recorded here so the choice is auditable. The function's behavior is byte-identical and now pinned by tests.
3. **F6 file placement deviation (disclosed):** the roadmap's Batch 1.1 "files affected" names four files; the focused-test requirement (batch prompt) plus the unit project's include pattern (`lib/**`, `features/**`) made `features/auth/redirect.ts` + `redirect.test.ts` the minimal honest way to add the tests without editing `vitest.config.ts` or importing UI components into node tests. Consistent with the roadmap's own direction of housing auth domain logic under `features/auth/`.
4. **Node version deviation:** Node 24.21.0 / npm 11.19.0 vs CI's Node 20 — all five script checks green on Node 24, same as recorded at Batch 0.1.

#### Commit
N/A (executor does not commit; Seyam applies the patch
`frontend-redesign-1.1-correctness-fixes-core-flows.patch`).

#### Gate impact
None claimed. Gate A remains passed; Gate B requires the full closure set (1.1 complete + 1.2 + 1.3 + 1.4) and the local matrix green including E2E with credentials — not satisfied yet.

---

### 1.1 — completion: owner-machine verification run (owner machine, 2026-10-15)

Status: **COMPLETE** — Batch 1.1 is **EXECUTED** (2026-10-15)

#### Planned
Complete the two validation items blocked in the executor's sandbox at first pass (same missing-prerequisite block as Batch 0.1 — no Docker, no E2E credentials, no running app): the E2E re-run (`courses-crud`, `profile-roundtrip`, plus the `login` spec) with real Keycloak credentials, and the manual light+dark check of the S10 success message. Both belong to the owner machine, where the prerequisites exist.

#### Actual
Seyam ran the full matrix on the owner machine against the applied Batch 1.1 commit `7dc9f67` and reported the results (evidence supplied with the close-out authorization; the executor did not independently reproduce these runs — they are recorded as owner-reported):

| # | Check | Owner-machine result |
|---|---|---|
| 1 | `npm run test:e2e` (Playwright) | **PASS — 3/3** (`courses-crud.spec.ts`, `login.spec.ts`, `profile-roundtrip.spec.ts`) with locally supplied `E2E_USERNAME`/`E2E_PASSWORD` (real Keycloak; the password value is never recorded in repository files, reports, or logs) |
| 2 | `npm run test:storybook` | **PASS — 42/42 across 12 files** |
| 3 | `npm run lint` | **PASS** |
| 4 | `npm run typecheck` | **PASS** |
| 5 | `npm run build` | **PASS** — production build with all 9 application routes |
| 6 | Manual light+dark check of the success message (roadmap validation item for S10) | **Successful — owner-verified manual testing**; not independently reproduced by the executor |

Warnings observed during the owner's Storybook run — recorded as warnings, not test failures, and explicitly not fixed (outside 1.1/1.2 authorized scope): (a) Vite's native config loader ESM-in-CJS notice on `vitest.config.ts`; (b) the unmatched `stories/**/*.mdx` story-pattern notice (only `.tsx` stories exist); (c) Base UI `nativeButton` semantics warnings from some stories rendering `Button` via a `render` prop inside non-button elements.

Executor cross-check at `7dc9f67` (fresh clone of `origin/frontend-redesign`, clean tree, staging containment re-verified): the applied implementation was reviewed file-by-file against the ledger's 1.1 record — F3 `key={course.id}` present at `app/(app)/courses/[id]/edit/page.tsx:76`; F4 `key={profile?.id ?? "new"}` present at `app/(app)/profile/page.tsx:116`; S10 `text-success` present at `components/profile/ProfileForm.tsx:213` with zero `text-success-foreground` occurrences repo-wide; F6 `features/auth/redirect.ts` with the aligned documentation + `features/auth/redirect.test.ts` with 15 focused policy tests + `LoginForm.tsx` importing the extracted function. The sandbox re-ran lint (PASS), typecheck (PASS), and the unit project (37/37 across 4 files incl. the 15 F6 tests) — all matching the ledger's 1.1 verification table.

#### Files changed
This ledger only (the close-out record):
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md` (Current State, history row 1.1 + new 1.1-completion row, this completion log, status board, next-batch pointer)

#### Verification
Evidence is the owner-run result table above (supplied by Seyam with the close-out authorization) plus the executor's own cross-check runs at `7dc9f67`. All Batch 1.1 acceptance criteria now have evidence: edit A→B saves B's values (F3 + green courses-crud E2E); profile create-then-edit re-seeds (F4 + green profile-roundtrip E2E); success feedback readable in both themes (S10 + owner manual light/dark check).

#### Issues / deviations
None. The two previously blocked items are closed with owner evidence; the three Storybook warnings are recorded as warnings (outside authorized scope), not deviations.

#### Commit
N/A (executor does not commit; the underlying 1.1 implementation was already applied upstream by Seyam as `7dc9f67`; the close-out ledger update is delivered as `frontend-redesign-1.1-close-out.patch`).

#### Gate impact
Batch 1.1's completion criterion is met (all three roadmap completion bullets evidenced). **Gate B remains NOT claimed** — it requires the full closure set (1.1 ✓ + 1.2 + 1.3 + 1.4) and the local matrix green including E2E with credentials.

---

### 1.2 — Authentication surface completion

Status: **PARTIALLY EXECUTED** (2026-10-15) — implementation complete and sandbox-verified; the login E2E and the three roadmap-manual validations (forced refresh failure, throwaway registration, forced render error) belong on the owner machine, where the prerequisites exist (same missing-prerequisite block as 0.1/1.1; not failures, nothing fabricated)

#### Planned
Per roadmap v2.0 §14 Batch 1.2 and the frozen finding register (decision note §3): W1 — global 401 session recovery: clear the query cache and route to `/login` carrying `redirectedFrom`, replacing the two forms' static expired-session strings; S3 — a real register flow: error, loading, and null-client states plus theme parity; S8 — styled `(auth)` error/loading boundaries mirroring `(app)`. Roadmap-named files: `lib/query-provider.tsx`, `lib/auth-context.tsx`, `lib/keycloak.ts`, `app/(auth)/register/page.tsx`, new `app/(auth)/error.tsx` + `loading.tsx`, `CourseForm.tsx`, `ProfileForm.tsx`. Must NOT change: Keycloak init options (check-sso, PKCE, iframe setting), guard consolidation, login redirect-target logic, logout sequence.

#### Actual
Executed on a fresh clone of `origin/frontend-redesign` @ `7dc9f67` (equal to remote HEAD; working tree clean at start; staging containment re-verified). Authorization chain verified first: the ledger records Batch 1.1 EXECUTED (2026-10-15) with owner evidence and names Batch 1.2 as the next batch in sequence — this batch's prompt is Seyam's explicit authorization. Roadmap v2.0 Batch 1.2 row re-read; the v1.3 register (git history `ad64e0c`) consulted for the per-finding mechanics (W1: "No global 401 handler, no token-expired event; only static expired text in two forms"; S3: "No error, loading, or null-client states; silent return; no theme toggle"; S8: "Only (app) has error.tsx / loading.tsx; auth errors hit the unstyled default"). Findings re-verified present in code at `7dc9f67` before editing (grep audit: zero `onAuth*` handlers anywhere; the 401 branches in both forms; `(auth)` without error/loading). Per-finding decisions:

1. **W1 — global 401 session recovery.** New pure module `lib/session-recovery.ts`: `isSessionExpiredError` (ApiError with status 401 — the boundary throws exactly that both when no token can be obtained, which includes the forced-refresh failure path, and when the backend answers 401), `sessionRecoveryTarget` (`/login?redirectedFrom=<pathname><search>` — the same deep-link convention AuthGuard uses; `features/auth/redirect.ts` validates the value on the way back), and `triggerSessionRecovery` (one-shot latch per page lifetime: clear the query cache, then route via `window.location.assign` — the established end-of-session navigation in this app; logout does the same — so the login screen re-initializes Keycloak cleanly). Trigger sources wired in `lib/query-provider.tsx`: error observers on the QueryCache and MutationCache (non-401 errors unaffected; handlers run after the configured retries), plus a subscription to the Keycloak refresh-error event. `lib/keycloak.ts` gains the previously missing token-expired event: a listener registry fanned out from the adapter's `onAuthRefreshError`; the init options are byte-identical to before (protected). `lib/auth-context.tsx` mirrors the event into React state (`setIsAuthenticated(false)`) so the existing, unchanged AuthGuard redirect also reacts. The two forms' static dead-end strings (`"Your session has expired. Please log in again."`) become the expectation-setting `"Your session has expired. Redirecting to sign in..."` — the recovery itself is global, no longer a dead end. The logout sequence, AuthGuard consolidation, and LoginForm redirect-target logic are untouched.
2. **S3 — real register flow.** `app/(auth)/register/page.tsx`: loading state (`isLoading` disables the button, label `"Connecting..."` — same copy as LoginForm), error state (`role="alert"` presentation), and the null-client state surfaced as an error instead of the silent `if (!keycloak) return;`; theme parity via the same `ThemeToggle` placement as the login page. The `keycloak.register` call site and its `/dashboard` redirect target are byte-identical (protected for 4.1).
3. **S8 — styled `(auth)` boundaries.** New `app/(auth)/error.tsx` (Next error-boundary contract: `error` + `reset`; same copy as the `(app)` boundary; card container matching the auth screens' visual language, sized for the centered auth layout) and new `app/(auth)/loading.tsx` (shared `LoadingBlock`, no full-screen wrapper since the auth layout already centers its children).

Focused tests added: `lib/session-recovery.test.ts` — 12 tests covering the 401 classifier (accepts ApiError 401; rejects other statuses, non-ApiError values), the recovery target builder (plain deep link, query-string deep link, root, empty), the no-window fallback, and the trigger semantics (clear-cache-before-redirect ordering, current-location default, no-window no-op, one-shot latch).

#### Files changed
Exactly the seven roadmap-named files, plus the two new files required by the recovery module and its focused tests (disclosed below), plus this ledger:
- `frontend/lib/query-provider.tsx` — W1: cache error observers + event subscription (defaults unchanged)
- `frontend/lib/auth-context.tsx` — W1: refresh-error → `setIsAuthenticated(false)` (cleanup added)
- `frontend/lib/keycloak.ts` — W1: `onAuthRefreshError` fan-out registry (init options byte-identical)
- `frontend/components/courses/CourseForm.tsx` — W1: 401 string replaced (one branch)
- `frontend/components/profile/ProfileForm.tsx` — W1: 401 string replaced (one branch)
- `frontend/app/(auth)/register/page.tsx` — S3: full states + theme toggle (call site unchanged)
- `frontend/app/(auth)/error.tsx` — new (S8)
- `frontend/app/(auth)/loading.tsx` — new (S8)
- `frontend/lib/session-recovery.ts` — new (W1 recovery module)
- `frontend/lib/session-recovery.test.ts` — new (W1: 12 focused tests)

No changes to `AuthGuard.tsx`, `LoginForm.tsx`, `features/auth/redirect.ts`, E2E specs, Storybook stories, schemas, mutations, Keycloak init options, backend, CI, infrastructure, or the roadmap DOCX.

#### Verification
Run from `frontend/` on Node 24.21.0 / npm 11.19.0 (CI pins Node 20 — same recorded environment deviation as 0.1/1.1; not a repository change):

| # | Command | Result | Exit |
|---|---|---|---|
| 1 | `npm run lint` | PASS — no findings | 0 |
| 2 | `npm run typecheck` | PASS (`tsc --noEmit`, TS 5.9.3) | 0 |
| 3 | `npm run test` (vitest unit project) | **PASS — 49/49** across 5 files (37 pre-existing + 12 new `lib/session-recovery.test.ts`) | 0 |
| 4 | `npm run test:storybook` | PASS — 42/42 across 12 story files, axe fail-on-violation active | 0 |
| 5 | `npm run build` (CI-documented fallback `NEXT_PUBLIC_*` env, no repo file created) | PASS — 9 routes + `/_not-found` | 0 |
| 6 | `npx playwright test` | **NOT RUN as flows — 3 skipped** (exit 0): `E2E_USERNAME`/`E2E_PASSWORD` absent, no Docker daemon (`docker info` exit 127), nothing on :8000/:3000 — the specs' documented credential gate self-skips; identical missing-prerequisite block as 0.1/1.1. No credentials fabricated; no auth weakened; specs untouched | 0 (skip) |
| 7 | Manual: forced token-refresh failure → login | **NOT PERFORMED** — owner machine (roadmap §24 marks this manual); left to the owner | — |
| 8 | Manual: throwaway-user registration end to end | **NOT PERFORMED** — owner machine; left to the owner | — |
| 9 | Manual: forced render error shows the styled boundary | **NOT PERFORMED** — owner machine; left to the owner | — |

Environment checks after the run: working tree contains exactly the ten batch-owned files + this ledger; `frontend/test-results/` from the skipped E2E run removed.

#### Issues / deviations
1. **Two new files beyond the roadmap's named list (disclosed):** `lib/session-recovery.ts` + its test. The recovery logic needed to be callable from both `lib/query-provider.tsx` and the Keycloak event path without importing a `"use client"` JSX module into `lib/keycloak.ts`, and the focused-test requirement (this batch's verification instructions) made a pure module the minimal honest way — the same justification pattern as 1.1's `features/auth/redirect.ts`, and the unit project already includes `lib/**`.
2. **Recovery navigation is a full-page redirect** (`window.location.assign`), not SPA navigation: an expired session is an end-of-session event in this app (logout navigates the same way), and a reload guarantees a clean Keycloak re-initialization on the login screen. The one-shot latch prevents concurrent-401 refetch storms from re-triggering. Recorded so the choice is auditable.
3. **The forms' 401 copy is retained, reworded** ("Your session has expired. Redirecting to sign in..."): the roadmap replaces the static strings as the *recovery mechanism*; the line remains as honest transient feedback until the redirect lands. Recorded so the wording change is traceable.
4. **Four validation items pending owner machine (missing prerequisites, not failures):** the login E2E and the three roadmap-manual checks (§24). Batch 1.2 is therefore NOT marked complete and Gate B is not claimed. Completion path: apply the patch, run `npm run test:e2e` with the documented stack up, and walk the three manual items (revoke/expire the session to force a refresh failure; register a throwaway user; force a render error in an `(auth)` route).
5. **Node version deviation:** Node 24.21.0 / npm 11.19.0 vs CI's Node 20 — all five script checks green on Node 24, same as recorded at 0.1/1.1.

#### Commit
N/A (executor does not commit; Seyam applies the patch
`frontend-redesign-1.2-authentication-surface-completion.patch`).

#### Gate impact
None claimed. Gate A remains passed; Gate B requires the full closure set (1.1 ✓ + 1.2 + 1.3 + 1.4) and the local matrix green including E2E with credentials — not satisfied yet.

---

### 1.3 — Observability and configuration closure

Status: **PARTIALLY EXECUTED** (2026-10-15) — implementation complete, all five primary configuration files wired and sandbox-verified (40/40 chain assertions + full script matrix green); the roadmap's validation criterion (Sentry UI shows events tagged `staging` with resolved stack frames from uploaded maps) is **BLOCKED / NOT VERIFIED** — missing prerequisites are deployment-side (see Issues); not failures, nothing fabricated

#### Planned
Per roadmap v2.0 §14 Batch 1.3, §20, and the frozen finding register (decision note §3): wire the F1 environment-label chain end to end — `NEXT_PUBLIC_SENTRY_ENVIRONMENT` as a `frontend/Dockerfile` build ARG (today only the DSN is one), matching build-argument in `.github/workflows/deploy-staging.yml` + `SENTRY_ENVIRONMENT` in its `.env.runtime` heredoc, `SENTRY_ENVIRONMENT` on the compose frontend service, the missing keys in `infra/.env.staging.example`, plus the `SENTRY_AUTH_TOKEN`/`SENTRY_ORG`/`SENTRY_PROJECT` build-time secrets `withSentryConfig` needs; align `package.json` engines with CI/deploy Node (W8). Must NOT change: DSN handling model, Dockerfile build sequence, deploy script order; the chain must agree across all five files. Roadmap-named files: `frontend/Dockerfile`, `.github/workflows/deploy-staging.yml`, `infra/docker-compose.staging.yml`, `infra/.env.staging.example`, `package.json`.

#### Actual
Executed on a fresh clone of `origin/frontend-redesign` @ `f87c765` (equal to remote HEAD; working tree clean at start; staging containment re-verified: `git merge-base --is-ancestor origin/staging HEAD` passes, `HEAD..origin/staging` empty). Authorization chain verified first: the ledger records 0.1 EXECUTED, 0.2 EXECUTED, Gate A PASSED, 1.1 EXECUTED, 1.2 implemented (patch applied upstream as `f87c765`, owner validation still pending) and names Batch 1.3 as the next in sequence — this batch's prompt is Seyam's explicit authorization. Roadmap v2.0 Batch 1.3 row and §20 re-read; the Phase 6 Batch 3 closure record (`docs/tasks/Frontend Modernization/…-closure.md`) consulted for the exact variable semantics (client `NEXT_PUBLIC_SENTRY_ENVIRONMENT` = build-time-inlined via `lib/config.ts`; server `SENTRY_ENVIRONMENT` = runtime-read by `sentry.server.config.ts`; both must carry the same value in deployment; `withSentryConfig` reads the three upload variables from the build environment only). The F1 gap re-verified present at `f87c765` before editing (grep audit: the deploy chain carries DSN only in all four deployment files; the only `SENTRY_ENVIRONMENT` reference repo-wide is `ci.yml`'s build env). The code layer (`lib/config.ts`, both Sentry configs, `next.config.ts`) verified intact and NOT modified — the batch closes deployment wiring, not code.

1. **Build chain (client label).** `frontend/Dockerfile`: added `ARG NEXT_PUBLIC_SENTRY_ENVIRONMENT` + `ENV NEXT_PUBLIC_SENTRY_ENVIRONMENT=$NEXT_PUBLIC_SENTRY_ENVIRONMENT` immediately after the DSN pair — byte-for-byte the existing ARG/ENV convention, so the value reaches `next build` and is inlined via `lib/config.ts` (Zod enum `development|staging|production`, unchanged). `.github/workflows/deploy-staging.yml`: added the matching build-argument. Sourcing decision: `${{ vars.NEXT_PUBLIC_SENTRY_ENVIRONMENT || 'staging' }}` — `ci.yml:168` already reads this exact variable with the vars-with-fallback pattern (fallback `'development'` in CI's dev context); the deploy workflow mirrors it with the deployment tier as fallback, so a missing repo Variable can never mislabel the staging bundle, and no new GitHub configuration is required for a correct deploy. The heredoc's `SENTRY_ENVIRONMENT` uses the identical expression → client and server labels are structurally guaranteed to match (the closure doc's stated requirement).

2. **Source-map upload secrets.** `frontend/Dockerfile`: the `RUN npm run build` step now declares `--mount=type=secret,id=sentry_auth_token|sentry_org|sentry_project` and exports the three variables only for that RUN via `VAR="$(cat /run/secrets/… 2>/dev/null || true)"` — BuildKit secret mounts, the repository's established mechanism (backend/Dockerfile already uses `RUN --mount=type=cache` in the same buildx pipeline: setup-buildx-action@v3 + build-push-action@v6). No `ARG`/`ENV` for secrets → values never enter image layer metadata, the runner stage, or logs; absent/unset secret → empty variable → the SDK skips the upload and the build still succeeds (documented `withSentryConfig` behavior; local/fork builds unaffected). Workflow: the three secrets supplied via `docker/build-push-action@v6`'s `secrets` input from `secrets.SENTRY_AUTH_TOKEN`/`SENTRY_ORG`/`SENTRY_PROJECT` (repo convention: Sentry values are GitHub Secrets — the DSN already is). The input sits on the shared matrix build step; the backend Dockerfile declares no secret mounts, so BuildKit resolves nothing for the backend build (secrets are consumed only where a Dockerfile mounts them). Block-scalar hygiene: no comment lines inside `build-args:`/`secrets:` scalars (every scalar line is passed to buildx verbatim) — documentation lives as real YAML comments above the keys.

3. **Runtime chain (server label).** `deploy-staging.yml` `.env.runtime` heredoc: added `SENTRY_ENVIRONMENT=${{ vars.NEXT_PUBLIC_SENTRY_ENVIRONMENT || 'staging' }}` directly below `SENTRY_DSN` (comment style matches the heredoc's existing comments; compose env-file parsing strips `#` lines — precedent: the existing Week 7–8 comments). `infra/docker-compose.staging.yml` frontend service: added `- SENTRY_ENVIRONMENT=${SENTRY_ENVIRONMENT}` below the existing `SENTRY_DSN` interpolation — the exact pattern by which the DSN already flows (heredoc → `--env-file` interpolation → container env) → `sentry.server.config.ts` reads it at runtime. Backend `ENVIRONMENT: staging` untouched; DSN handling model untouched everywhere (build-time `NEXT_PUBLIC_SENTRY_DSN` secret → ARG; runtime `SENTRY_DSN` secret → heredoc → compose).

4. **Environment example.** `infra/.env.staging.example`: added `NEXT_PUBLIC_SENTRY_ENVIRONMENT=staging` (annotated build-time) and `SENTRY_ENVIRONMENT=staging` (annotated runtime, next to `SENTRY_DSN`), plus a build-time-only block for `SENTRY_AUTH_TOKEN`/`SENTRY_ORG`/`SENTRY_PROJECT` (annotated: BuildKit mounts, never `.env.runtime`, never runtime; secrets left empty — no real values, per file convention). Pre-existing keys untouched; `SENTRY_DSN` kept in place with an accuracy comment distinguishing the client copy (build-time `NEXT_PUBLIC_SENTRY_DSN` GitHub Secret) from the server copy (runtime). `NEXT_PUBLIC_SENTRY_DSN` deliberately NOT added as a new key line: it is a pre-existing chain element outside the five-key F1 gap; its secret name is documented in the comment instead.

5. **W8 — engines.** Evidence gathered: `ci.yml` frontend job, `e2e.yml`, `storybook.yml` all pin Node 20; `frontend/Dockerfile` builds and runs on `node:22-alpine` (both stages); `@types/node` is `^20`. Declared `"engines": { "node": "^20 || ^22" }` in `frontend/package.json` — the precise majors the repository actually exercises (21/23 skipped: never used, never LTS). `package-lock.json` root entry (`packages[""]`) synced with the same field — the only lockfile change (no dependency, resolution, or version changes; `git diff` shows exactly the 3-line engines block; `npm ci` accepts it, exit 0). npm's default `engine-strict=false` verified (no `.npmrc` override) → the declaration is advisory, matching W8's "document compatible versions" intent; the sandbox's Node 24.21.0 remains the recorded environment deviation (outside the declared range — honestly noted, all checks still green).

Scope guards honored: `lib/config.ts`, `sentry.client.config.ts`, `sentry.server.config.ts`, `next.config.ts` (the entire code layer) byte-identical; Dockerfile build sequence preserved (npm ci → COPY → ARGs → build → standalone runner); deploy step order and deployment behavior preserved (build-and-push → deploy, heredoc ordering intact, only additive lines); no observability infrastructure added; `docs/openapi.json` and the roadmap DOCX untouched; no commits/pushes.

#### Files changed
Exactly the five authorized files, plus the lockfile root-entry sync required by the engines declaration (disclosed below), plus this ledger:
- `frontend/Dockerfile` — `NEXT_PUBLIC_SENTRY_ENVIRONMENT` ARG/ENV pair + three BuildKit secret mounts on the build RUN
- `.github/workflows/deploy-staging.yml` — build-argument + `secrets` input + heredoc `SENTRY_ENVIRONMENT` (all additive; YAML comments above the block scalars)
- `infra/docker-compose.staging.yml` — frontend `SENTRY_ENVIRONMENT=${SENTRY_ENVIRONMENT}` (additive)
- `infra/.env.staging.example` — five new keys with build-time/runtime annotations (secrets empty)
- `frontend/package.json` — `engines.node: "^20 || ^22"` (W8)
- `frontend/package-lock.json` — root entry `packages[""].engines` mirrored (the only lockfile change; no dependency/resolution changes — strictly required to keep the manifest and lockfile consistent)

No changes to `lib/config.ts`, `sentry.*.config.ts`, `next.config.ts`, any application code, E2E specs, backend, `docs/openapi.json`, the roadmap DOCX, or `.gitignore`.

#### Verification
Run from `frontend/` (except where noted) on Node 24.21.0 / npm 11.19.0, TS 5.9.3, vitest 4.1.11 (CI pins Node 20 — same recorded environment deviation as 0.1/1.1/1.2; not a repository change):

| # | Command | Result | Exit |
|---|---|---|---|
| 1 | `npm ci` (lockfile untouched beyond the engines root entry — verified by diff) | PASS | 0 |
| 2 | `npm run lint` | PASS — no findings | 0 |
| 3 | `npm run typecheck` | PASS (`tsc --noEmit`, TS 5.9.3) | 0 |
| 4 | `npm run test` (vitest unit project) | PASS — 49/49 across 5 files (unchanged from 1.2; configuration-only batch, no new tests required) | 0 |
| 5 | `npm run test:storybook` | PASS — 42/42 across 12 story files, axe fail-on-violation active (sandbox initially lacked the Playwright Chromium binary — `browserType.launch: Executable doesn't exist`; resolved by `npx playwright install chromium` (v1243 headless shell, 153.0.8010.12) — environment setup, not a repo change) | 0 |
| 6 | `npm run build` with the CI-documented fallback `NEXT_PUBLIC_*` env (no repo file created), exercising `NEXT_PUBLIC_SENTRY_ENVIRONMENT=staging` — the exact value staging will use — through the Zod enum | PASS — 9 routes + `/_not-found` | 0 |
| 7 | Configuration-chain consistency script (sandbox artifact `scripts/verify_chain.py`, not committed): 40 assertions across the five files — build chain (config.ts → Dockerfile ARG → workflow build-arg), runtime chain (server config → heredoc → compose), upload chain (withSentryConfig env-read → Dockerfile mounts → workflow secrets), block-scalar hygiene, step/sequence preservation, key preservation, no-token-shaped-values scan, DSN-model invariants, engines vs CI/deploy evidence | **40/40 PASS** | 0 |
| 8 | Workflow YAML parse (PyYAML `safe_load`) | PASS; `actionlint` NOT RUN (not installed in the environment) | 0 |
| 9 | Compose YAML parse (PyYAML `safe_load`) + `.env.runtime` heredoc render simulation (GitHub expression evaluated on both the fallback and override paths, parsed with env-file semantics: all 25 real keys parse, `SENTRY_ENVIRONMENT=staging`, comments stripped as designed — matching the heredoc's pre-existing comment precedent) | PASS; `docker compose config` NOT RUN (no Docker daemon in the execution environment — `docker` absent, exit 127; same block as 0.1/1.1/1.2) | 0 |
| 10 | Dockerfile: structural assertions (ARG/ENV placement, mount flags, no secret ARG/ENV persistence, runner stage secret-free, build sequence order) + shell semantics simulation of the secret-mount RUN (secret absent → empty var, exit 0; present → value available to the build command only, not persisted) | PASS; real image build NOT RUN (no Docker daemon) | 0 |
| 11 | Secret-exposure audit: `git diff` scanned for token-shaped strings (sntrys_/eyJ/ghp_/sk-…) — none; the three secrets appear only as `${{ secrets.* }}` references; `infra/.env.runtime` confirmed not tracked | PASS | 0 |
| 12 | E2E suite | **NOT RUN** — not part of Batch 1.3's validation (roadmap §24's 1.3 row is the Sentry UI check); no application code changed; and the documented missing-prerequisite block applies (no Docker daemon, no E2E credentials) | — |
| 13 | **Sentry staging runtime verification** (roadmap §14 validation: events tagged `staging` with source-map-resolved frames; sample-rate reflected) | **BLOCKED / NOT VERIFIED** — see Issues | — |

#### Issues / deviations
1. **Sentry runtime verification BLOCKED / NOT VERIFIED — exact missing prerequisites:** (a) the batch is delivered as an uncommitted patch — the workflow/Dockerfile changes do not exist on any pushed branch until Seyam applies and pushes; staging deploys trigger only on pushes to `staging` (and the executor must not push per the lifecycle rules); (b) the three GitHub Secrets (`SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT`) must be configured in repo settings — their existence is not verifiable from the executor's environment (workflow references do not imply configuration; nothing fabricated); (c) the GitHub Variable `NEXT_PUBLIC_SENTRY_ENVIRONMENT` is OPTIONAL — the `'staging'` fallback covers it; (d) Sentry project UI access is required to confirm the events' `staging` label, the staging traces sample rate (0.5), and source-map-resolved frames. Per the batch rules, Batch 1.3 is therefore NOT marked fully complete and the closure-doc runtime items stay unverified; the repository-verifiable closure-doc items (the wiring itself) are done.
2. **Docker-layer checks limited by the environment (missing prerequisites, not failures):** no Docker daemon → the real image build, `docker compose config`, and a buildx dry-run could not be executed; verification relied on YAML parsing, the 40-assertion structural script, the heredoc render simulation, and the shell-semantics simulation. The `--mount=type=secret` mechanism itself is proven in-repo: the backend Dockerfile uses BuildKit mounts in the same buildx pipeline. First upstream staging build after this patch is the honest residual risk point.
3. **`secrets` input placement (disclosed):** the `secrets: |` block sits on the shared matrix build step, so the backend build also receives the three secret definitions. This is safe (BuildKit consumes secrets only where a Dockerfile declares `--mount=type=secret`; the backend Dockerfile declares none; GitHub masks the values in logs) and avoids fragile expression-built multiline secret lists. Recorded so the choice is auditable.
4. **One new key line NOT added (decision recorded):** `NEXT_PUBLIC_SENTRY_DSN` (the build-time client DSN, a pre-existing chain element) is not added to `.env.staging.example` as a key — the batch's chain defines exactly five missing keys; the DSN's build-time secret name is documented in the example's Sentry comment instead. No categorization change to any existing variable was needed; the DSN handling model is untouched.
5. **Lockfile change (disclosed, strictly required):** `frontend/package-lock.json` root entry gained the `engines` field — the only way to keep the manifest and lockfile consistent after the W8 declaration; verified to be the only lockfile change and accepted by `npm ci`.
6. **Node version deviation:** Node 24.21.0 / npm 11.19.0 vs CI's Node 20 — outside the newly declared `^20 || ^22` range (advisory: npm `engine-strict=false`, verified); all script checks green on Node 24, same as recorded at 0.1/1.1/1.2.
7. **Pre-existing observation (not changed, out of scope):** `infra/.env.runtime` is not covered by `.gitignore` (`*.env` does not match `.env.runtime`). The file is generated on the VPS at deploy time and is not tracked, so this batch's exposure profile is unchanged; flagging it for a future owner decision rather than editing an out-of-scope file.

#### Commit
N/A (executor does not commit; Seyam applies the patch
`frontend-redesign-1.3-observability-configuration-closure.patch`).

#### Gate impact
None claimed. Gate A remains passed; Gate B requires the full closure set (1.1 ✓ + 1.2 ✓ pending owner confirmation + 1.3 ✓ pending the Sentry runtime verification + 1.4) and the local matrix green including E2E with credentials — not satisfied yet.

---

### 1.4 — Data contract settlement

Status: **PARTIALLY EXECUTED** (2026-10-17) — implementation complete and sandbox-verified (unit 54/54 including the five new datetime-contract tests; full script matrix green); the roadmap's live-API validation item ("course list and detail load against the live API") is **BLOCKED / NOT RUN** — missing environment prerequisites, the same documented block as 0.1/1.1/1.2/1.3; not failures, nothing fabricated

#### Planned
Per roadmap v2.0 §14 Batch 1.4 and the frozen finding register (decision note §3–§4): settle F5 from the 0.1 result (the tracked contract declares `date-time`; accept/normalize per what the live API emits, with a note to the backend pod if naive); write the real-metric inventory for the dashboard (course count, profile completeness — no analytics endpoints exist). Roadmap-named files: `features/courses/schemas.ts`, `lib/api.test.ts` (fixtures). Must NOT change: the rest of the course schema, query options, mutations, apiFetch error taxonomy.

#### Authorization and prerequisite review
Executed on a fresh clone of `origin/frontend-redesign` @ `b56be14` (equal to remote HEAD after `git fetch origin`; working tree clean at start; staging containment re-verified: `git merge-base --is-ancestor origin/staging HEAD` passes, `HEAD..origin/staging` empty — `origin/staging` @ `d1ba348`). Authorization chain verified first: the ledger records 0.1 EXECUTED + 0.2 EXECUTED + Gate A PASSED + 1.1 EXECUTED + 1.2 implemented (owner validation pending) + 1.3 implemented (runtime verification blocked) and names Batch 1.4 as the next in sequence — this batch's prompt is Seyam's explicit authorization. The Batch 0.1 F5 evidence was re-read from the ledger's 0.1-completion record (not inferred from commit messages): owner-machine run `run-20261014-190840`, authenticated `GET http://localhost:8000/v1/courses` → HTTP 200, COUNT=5 WITH_OFFSET=5, sample `2026-10-14T15:52:48.551399Z`, real browser-captured token (redacted). The 1.1/1.2/1.3 completion records were reviewed for the current verification posture (owner-machine validation and runtime verification still outstanding — none of them gates 1.4's implementation).

#### F5 evidence and settlement decision
Three evidence sources, re-verified at `b56be14` before editing:

1. **Tracked contract** — `docs/openapi.json` (v0.2.0, CI-drift-guarded): `CourseResponse.created_at` is `{type: string, format: date-time}` and required (extracted from the tracked file, not assumed). RFC 3339 `date-time` requires a timezone offset; both the UTC `Z` form and the explicit `±HH:MM` form are contract-valid shapes.
2. **Recorded live behavior** — the Batch 0.1 owner-machine probe (2026-10-14, ledger-recorded): 5/5 `created_at` values offset-bearing, sample `2026-10-14T15:52:48.551399Z` (UTC `Z` form with 6-digit fractional seconds). A fresh live request from this execution environment was NOT possible: no Docker daemon (`docker info` exit 127 — no db/Keycloak containers, no backend on :8000), and the documented staging API host unreachable from this environment (TLS timeouts, DNS resolves — identical diagnostics to the 0.1 baseline finding); recorded as BLOCKED / NOT RUN, no credentials fabricated.
3. **Validator behavior** — the installed `zod` 4.6.5 verified directly against `z.string().datetime({ offset: true })`: accepts the `Z` form (with/without fractional seconds), accepts `±HH:MM` offsets (with/without fractional seconds), rejects a naive datetime (`2026-10-14T15:52:48`) — i.e. the schema never silently treats a naive value as UTC.

Settlement: the live API's observed emission (offset-bearing) matches the tracked contract, so **`features/courses/schemas.ts` is unchanged byte-for-byte** — `created_at: z.string().datetime({ offset: true })` (line 25) stays exactly as frozen by the 0.2 decision note (§4: "correct as-is and frozen"). The roadmap's accept/normalize contingency and the note-to-the-backend-pod contingency are both dead: the live emission satisfies the contract, and there is **no backend contract discrepancy to report**. The smallest evidence-supported change that remains is the focused test coverage the batch prompt requires — the settlement is now pinned by tests against the real schema, not merely asserted.

#### Focused tests added (frontend/lib/api.test.ts)
Five tests in a new `describe("courseResponseSchema — created_at datetime contract (F5)")` block, exercising the REAL `courseResponseSchema` (imported from `@/features/courses/schemas`). Pre-edit coverage audit: the real schema was only exercised incidentally — `features/courses/api/course-query-options.test.ts` runs the real queryFn against a single Z-shaped fixture, and `lib/api.test.ts` pins apiFetch mechanics through a deliberately loose local schema (`created_at: z.string()`) — so the datetime contract itself (both valid shapes, the naive rejection) had no focused coverage. The five tests:

1. accepts the UTC `Z` shape observed from the live API — fixture uses the exact probe sample `2026-10-14T15:52:48.551399Z`;
2. accepts an explicit `±HH:MM` offset shape — fixture `2026-10-14T18:52:48.551399+03:00` (contract-valid `date-time`);
3. rejects a naive datetime without an offset — pins the no-silent-UTC-coercion behavior;
4. boundary: `apiFetch` with `courseResponseSchema.array()` (the exact shape `coursesListOptions` uses for `GET /v1/courses`) validates a course list carrying BOTH datetime shapes in one response;
5. boundary: `apiFetch` with `courseResponseSchema` throws `ApiError` status 0 ("schema validation failed") when the response carries a naive `created_at` — the existing error taxonomy absorbs the contract violation; no new error path was added.

Fixtures are realistic and evidence-based: a `courseWithCreatedAt()` builder producing a full contract-shaped `CourseResponse` (valid UUIDs, title, nullable description) parameterized by the datetime value; both datetime fixtures are offset-bearing, one of them the exact live-observed sample. No existing test, fixture, or mock was modified (the pre-existing 12 tests in the file are untouched and continue to pin apiFetch mechanics through the loose local schema).

#### Real dashboard-metric inventory (this ledger is the documented location)
The roadmap's 1.4 row names only the two frontend files and no separate inventory document, and the lifecycle rules' execution-context set designates none — so the inventory is recorded here, in the living execution record that Batch 2.2 already reads as its execution context. **No separate metrics-inventory document was created** (decision recorded; documentation kept minimal).

Every metric below is derived exclusively from operations that exist in the tracked contract and are consumed by the frontend today. Nothing is invented: no analytics endpoints (the 44-week plan places `GET /analytics/dashboard`/`GET /analytics/heatmap` in Weeks 34–35 and a profile-completeness onboarding prompt in Week 17 — none exist in `docs/openapi.json`), no progress percentages, no engagement or recent-activity data.

**Metric 1 — Course count.**

- Source data: `GET /v1/courses` → `CourseResponse[]`; consumed via `coursesListOptions` (`frontend/features/courses/api/useCourses.ts`), validated by `courseResponseSchema.array()`.
- Calculation: `courses.length` — the length of the validated response array. The dashboard already computes exactly this (`app/(app)/dashboard/page.tsx:16`, `courses?.length ?? 0`), so the metric requires no new data fetching and no new API surface.
- Interpretation: the number of courses visible to the authenticated user in the app's only course listing.
- Limitations: (a) the listing is NOT owner-scoped — any authenticated user sees every course (upstream backend authorization defect, flagged upstream, Open Question #7); the count therefore includes other users' courses, and dashboard copy must not claim "my N courses" until the backend scopes the listing (honest labeling is Batch 2.2's copy decision); (b) the contract has no pagination, so `length` is exact for current dataset sizes but unbounded as data grows; (c) loading, error, and empty states must remain distinct from the count itself (the dashboard already handles all three).

**Metric 2 — Profile completeness.**

- Source data: `GET /v1/users/me` → `ProfileResponse` (8 fields: id, user_id, education_level, major, preferred_language, university, learning_style_vark, daily_available_minutes); consumed via `profileOptions` (`frontend/features/profile/api/useProfile.ts`), validated by `profileResponseSchema`; the queryFn resolves `null` on 404 — "no profile yet" is a legitimate application state.
- Calculation (client-side, from the profile object alone — the backend exposes no completeness field): (1) profile established? (the `null` gate); (2) if established, completeness = the fraction of the **6 user-facing content fields** that carry a value, counting a field as carried when it is non-null AND non-empty. Four are non-nullable in the contract and therefore guaranteed present once a profile exists (`education_level`, `major`, `preferred_language`, `daily_available_minutes`; the create/update form additionally enforces min-length, the `en|ar` enum, and the 1–1440 integer range on them), and two are nullable and are the only variable fields (`university`, `learning_style_vark`). Practical range once a profile exists: **4/6 to 6/6**.
- Interpretation: a data-completeness measure of the profile's user-facing content — NOT a quality, progress, or engagement measure, and not a backend-computed value.
- Limitations: (a) the range is compressed — the floor for any established profile is 4/6 (~67%) because four of the six fields are required by the form; a raw percentage would overstate near-completeness, so Batch 2.2 should present it as outstanding-field copy (e.g. "2 of 6 profile fields left") rather than a percentage scale; (b) the response contract types `university`/`learning_style_vark` as `string|null` with no min-length, so an empty string would schema-pass — the non-empty guard above is part of the honest derivation; (c) `id`/`user_id` are identity fields, excluded from the count; (d) when the profile is not established, the only honest presentation is a create-profile prompt, not a number.

**Also derivable from the same two sources (recorded as an input to 2.2; no new capability claimed):** recent courses — the course list already carries `created_at` (offset-bearing, settled by F5) and the dashboard already renders the first four (`courses.slice(0, 4)`). Nothing beyond these is supportable today: the materials endpoints are per-course and scheduled for Batch 4.3, and no dashboard-aggregatable analytics exist in the contract.

#### Files changed
Exactly the two authorized files, plus this ledger:
- `frontend/lib/api.test.ts` — F5: new focused datetime-contract describe block (5 tests, 2 datetime fixtures, the real-schema import; +91 lines; zero existing lines modified)
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md` — this ledger

**`frontend/features/courses/schemas.ts` was NOT changed** (roadmap-named as a possible target): the 0.2 freeze decision plus the re-verified evidence (contract + recorded probe + validator behavior) make "no correction" the correct settlement; the file is byte-identical to `b56be14`.

No changes to query options or query keys, mutations, cache invalidation, the `apiFetch` boundary or its error taxonomy, authentication/Keycloak initialization/route guards/routing, backend code, `docs/openapi.json`, the roadmap DOCX, dashboard UI, or any Batch 2.1+ work.

#### Verification
Run from `frontend/` on Node 24.21.0 / npm 11.19.0, TS 5.9.3, zod 4.6.5, vitest 4.1.11 (CI pins Node 20 — same recorded environment deviation as 0.1/1.1/1.2/1.3; not a repository change). Baseline unit run before editing: **49/49 across 5 files** (matching the 1.3 record). `npm ci` installed from the lockfile without touching it.

| # | Command | Result | Exit |
|---|---|---|---|
| 1 | `npx vitest run --project unit lib/api.test.ts` (focused datetime schema + fixture tests) | **PASS — 17/17** in the file (12 pre-existing + 5 new F5 tests) | 0 |
| 2 | `npm run test` (vitest unit project) | **PASS — 54/54** across 5 files (49 pre-existing + 5 new) | 0 |
| 3 | `npm run lint` | PASS — no findings | 0 |
| 4 | `npm run typecheck` | PASS (`tsc --noEmit`, TS 5.9.3) | 0 |
| 5 | `npm run test:storybook` | PASS — 42/42 across 12 story files, axe fail-on-violation active (sandbox needed `npx playwright install chromium` — v1243 headless shell; same environment setup as 1.3, not a repo change) | 0 |
| 6 | `npm run build` with the CI-documented fallback `NEXT_PUBLIC_*` env (no repo file created) | PASS — 9 routes + `/_not-found` | 0 |
| 7 | **Live course-list and course-detail verification** (roadmap §14 validation item) | **BLOCKED / NOT RUN** — no Docker daemon (`docker info` exit 127; no db/Keycloak containers, nothing on :8000), no E2E credentials in the environment (none fabricated), and the documented staging API host unreachable (TLS timeouts; DNS resolves — identical diagnostics to the 0.1 baseline). The batch's only runtime-layer change is inside a test file — zero runtime code changed — so the last live evidence (0.1 owner-machine run: HTTP 200 with 5 courses; E2E courses-crud PASS through the real stack) remains the operative live behavior | — |
| 8 | `npm run test:e2e` | **NOT RUN** — not part of Batch 1.4's validation set (the roadmap's 1.4 row and the batch prompt's check list do not include it); the same missing-prerequisite block applies | — |

Scope audit after the run: `git status --porcelain` shows exactly `frontend/lib/api.test.ts` + this ledger modified; no staged changes; no untracked residue (the storybook run's gitignored `frontend/test-results/` output was removed). No dependency, lockfile, CI, or infrastructure file touched.

#### Issues / deviations
1. **Live-API validation blocked (missing prerequisites, not failures):** identical environment block to 0.1/1.1/1.2/1.3. Batch 1.4 is therefore NOT marked complete: the roadmap's validation item "course list and detail load against the live API" stays NOT RUN until exercised where the documented environment exists (owner-machine local stack per `docs/development/LOCAL_SETUP.md`, or staging). Completion path: apply the patch, start the documented local stack, sign in, open the course list and a course detail page — or rerun `scripts/run-batch-0.1-local-verification.sh`, whose F5 probe re-verifies the same contract end to end.
2. **Schema file untouched despite being roadmap-named (disclosed, evidence-driven):** the roadmap's "Files affected" lists `features/courses/schemas.ts` because at planning time the live emission was unknown; the 0.2 freeze (§4) plus the re-verified evidence settle "accept per what the live API emits" as "the schema already accepts exactly the emitted shapes" — no edit is the honest change. The batch prompt's "preserve the existing course schema apart from the specifically authorized datetime correction" is satisfied: no correction is supported by evidence, so nothing beyond the test coverage was touched.
3. **Inventory location decision (recorded):** the inventory lives in this ledger (this 1.4 log entry) rather than a new document — the roadmap names no inventory file for 1.4 (unlike 0.2's "short decision note in repo docs"), and the lifecycle rules name this ledger as the living execution record 2.2 reads. Documentation kept minimal: one file.
4. **Pre-existing stray tracked artifact (out-of-scope finding, not changed):** `frontend/test-results/.last-run.json` (a Playwright run artifact) was committed upstream in the 1.2 patch commit `f87c765` and remains tracked at `b56be14`, while `frontend/.gitignore` ignores `/test-results/`. Removing it is not required for 1.4, so it was left in place and flagged here for a later owner decision (its natural home is suite alignment in 5.1 or housekeeping in 5.3).
5. **Node version deviation:** Node 24.21.0 / npm 11.19.0 vs CI's Node 20 — all checks green on Node 24, same as recorded at 0.1/1.1/1.2/1.3.

#### Acceptance criteria
1. Datetime behavior justified by repository evidence and, where available, a live API response — **SATISFIED** (tracked contract + recorded 0.1 live probe + direct validator verification; the fresh live request from this environment was BLOCKED and is recorded as such).
2. Focused tests cover both relevant datetime shapes — **SATISFIED** (UTC `Z` + explicit `±HH:MM` accepted; naive rejected; both shapes exercised through the apiFetch boundary).
3. Course list and course detail continue to load against the live API when the documented environment and credentials are available — **NOT EXERCISABLE HERE** (environment/credentials unavailable; recorded BLOCKED / NOT RUN with the reason and completion path; zero runtime code changed by this batch).
4. Non-performable live verification explicitly recorded — **SATISFIED** (Verification table rows 7–8).

#### Commit
N/A (executor does not commit; Seyam applies the patch
`frontend-redesign-1.4-data-contract-settlement.patch`).

#### Gate impact
None claimed. Gate A remains passed; Gate B requires the full closure set (1.1 ✓ + 1.2 ✓ pending owner confirmation + 1.3 ✓ pending the Sentry runtime verification + 1.4 ✓ pending the live-API check) and the local matrix green including E2E with credentials — not satisfied yet.

---

### 1.4 — closeout: evidence-based closeout review (documentation-only)

Status: **PARTIALLY EXECUTED — UNCHANGED** (2026-10-18) — an evidence-based closeout review of the 1.4 record, executed after the course-ownership fix was merged upstream (PR #79); every claim below was re-verified against the fetched repository at `92b67bd`; the batch is deliberately NOT marked DONE — the roadmap's live-API validation item remains BLOCKED / NOT RUN, so criterion 3 stays unsatisfied and no criterion was weakened or redefined

#### Purpose and authorization
Seyam's closeout prompt: prepare the formal Batch 1.4 closeout; close the batch only if its required scope is supported by verifiable evidence; reconcile it with the subsequently merged course-ownership fix while keeping the two scopes and their provenance distinct; verify the merge against the fetched history; run only safe, relevant checks; distinguish verified-passed / verified-with-limitations / not-verified / blocked; no commit, no push, no application-code or roadmap-DOCX changes.

#### Repository preflight (before any edit)
- Starting state: the execution clone was detached at `e10249fd0be06d022051a31b6c000c59b3ccd709` with four uncommitted modified files (`backend/app/api/courses.py`, `backend/app/services/course_service.py`, `backend/tests/test_course_api.py`, `docs/openapi.json`) — the out-of-band Phase 2 ownership execution's working-tree state; recorded as found, not assumed clean.
- `git fetch origin --prune`: `origin/frontend-redesign` advanced `e10249f` → `92b67bd`; local branch `frontend-redesign` 0 ahead / 2 behind — a pure fast-forward, no divergence, no force of any kind.
- The four local modifications were diffed against the merged state (`git diff 92b67bd -- <files>`) and found **byte-identical**, and the merge diff (`git diff e10249f 92b67bd`) was found **byte-identical to the delivered ownership patch file** (`openlearn-ai-course-ownership-e10249fd.patch`) — so advancing the branch loses nothing; the pre-merge working-tree state was nevertheless preserved in a git stash rather than discarded, and the branch was fast-forwarded to `92b67bd` (`git merge --ff-only`).
- Post-reconciliation state: on `frontend-redesign` @ `92b67bd`, clean tree, local branch equal to `origin/frontend-redesign`; staging containment re-verified (`git merge-base --is-ancestor origin/staging HEAD` passes; `HEAD..origin/staging` empty). No reset, no rebase, no history rewrite; the delivered Phase 2 patch file outside the repository was untouched.

#### The subsequently merged course-ownership fix (verified; kept distinct from Batch 1.4)
- **Implementation commit** `65c8a8c189e9466b77cb7c55a5ada96cfb405f54` — "openlearn-ai-course-ownership", authored by Muhammad Seyam 2026-10-17T20:37:16+03:00, parent = `e10249f` (branched directly off the Batch 1.4 settlement commit).
- **Merge commit** `92b67bdd0b6187b65c930dd468e986e93a4d8a30` — "Merge pull request #79 from OpenLearn-AI/course-ownership-fix", GitHub-merged (GPG-signed), first parent `e10249f`, second parent `65c8a8c`.
- **Changed files** (`git diff --stat e10249f..92b67bd`): `backend/app/api/courses.py` (25 lines), `backend/app/services/course_service.py` (13), `backend/tests/test_course_api.py` (224), `docs/openapi.json` (10) — 233 insertions, 39 deletions; nothing else. The merged diff is byte-identical to the out-of-band Phase 2 ownership patch: the reviewed patch was applied unchanged.
- **Ownership decision (as merged):** every authenticated user can list and view only the courses they personally own — the owner filter (`Course.owner_id` == the authenticated local user's UUID) is applied inside the `list_courses` database query itself (`backend/app/services/course_service.py`), the list handler passes the resolved local `user.id` (never the Keycloak `sub`), and `GET /v1/courses/{course_id}` delegates to the existing `require_owned_course` helper (own → 200; another user's existing course → 403; nonexistent → 404, with no course data in the rejection body). Scoping is uniform for `student`, `instructor`, and `admin` — **no admin override** — and **no enrollment-based or shared-course visibility** was introduced (the dormant `Enrollment` model remains unused by authorization). Course creation still assigns ownership from the authenticated local user; client-supplied ownership fields are rejected (422). The `docs/openapi.json` 403 description was regenerated by the documented exporter (`python -m app.openapi_export`) to reflect 403 reachability on the by-id GET — a generated-file change only, with the CI drift guard green.
- **Provenance kept distinct:** Batch 1.4 remains exactly `e10249f` — data-contract settlement scope (F5 + the dashboard metric inventory; `frontend/lib/api.test.ts` +91 and this ledger, per the 1.4 log entry's Files-changed record). The ownership fix is a separate backend authorization change merged after 1.4; it is not counted toward 1.4, no 1.4 log text was rewritten, and the 1.4-era statements that were true when written (notably the metric inventory's course-count limitation (a): "the listing is NOT owner-scoped") stand as history — their resolution is recorded here, in Current State, and in Open Question #7.

#### Verification performed (actual results at `92b67bd`, 2026-10-18)
Run on Node 24.21.0 / npm 11.19.0 (same recorded environment deviation as 0.1–1.4; CI pins Node 20) and Python 3.12.15 with the pinned backend requirements subset. Database-mutating backend tests ran only against a disposable scratch PostgreSQL 18.6 + pgvector 0.8.6 created fresh for this verification on localhost (own `initdb`, `alembic upgrade head` green — no new migrations existed between `e10249f` and `92b67bd` — then stopped; never a shared, staging, or production database).

| # | Command | Result | Exit |
|---|---|---|---|
| 1 | `npx vitest run --project unit lib/api.test.ts` (frontend, focused) | **PASS — 17/17** (12 pre-existing + the five 1.4 F5 datetime-contract tests) | 0 |
| 2 | `npm run test` (frontend unit project) | **PASS — 54/54** across 5 files — matches the recorded 1.4 implementation result | 0 |
| 3 | `npm run lint` | PASS | 0 |
| 4 | `npm run typecheck` (`tsc --noEmit`) | PASS | 0 |
| 5 | `python -m ruff check .` (backend) | PASS | 0 |
| 6 | `python -m pytest tests/test_course_api.py tests/test_openapi_contract.py` (backend) | **PASS — 32/32**: the merged ownership matrix (owner-only list/detail, cross-owner 403 with no data leak, missing 404, role uniformity for student/instructor/admin, creation-ownership, untouched update/delete authorization) plus the OpenAPI drift guard — the regenerated contract matches the app | 0 |
| 7 | `python -m pytest tests --ignore=tests/pal --ignore=tests/documents --ignore=tests/services/test_document_pipeline_stage1.py --ignore=tests/services/test_document_pipeline_stage2.py --ignore=tests/services/test_ocr_source.py --ignore=tests/test_material_tasks.py` (backend core regression) | **254 passed, 1 failed** — the single failure is `test_material_api.py::test_api_full_flow_pending_then_ready_via_worker` (`ModuleNotFoundError: docling`), previously proven to fail identically at the pre-merge baseline `e10249f`: a pre-existing environment limitation (the docling/torch AI stack is not installed in this execution environment), not a merge regression. The four excluded files plus `tests/pal/**` and `tests/documents/**` were NOT RUN for the same missing-dependency reason | 1 |
| 8 | Storybook (42/42 recorded) and production build (9 routes recorded) at the 1.4 implementation pass | **NOT RE-RUN** (heavier checks left at their recorded state); sound to rely on for the current tree because the ownership merge changed zero frontend files (`frontend/` is bit-identical between `e10249f` and `92b67bd`) | — |
| 9 | Roadmap §14 live-API validation item ("course list and detail load against the live API") | **BLOCKED / NOT RUN** — re-confirmed today: no Docker daemon (`docker info` exit 127), no local db/Keycloak/backend stack, no E2E credentials in the environment (none fabricated), and the documented staging API host unreachable (TLS timeout; DNS resolves — identical diagnostics to the 0.1/1.1/1.2/1.3/1.4 block). Completion path unchanged: owner-machine local stack per `docs/development/LOCAL_SETUP.md`, or staging; `scripts/run-batch-0.1-local-verification.sh` re-verifies the same contract end to end | — |

#### Acceptance criteria after closeout (roadmap §14 Batch 1.4; ledger 1.4 log entry)
1. Datetime behavior justified by repository evidence and, where available, a live API response — **SATISFIED** (unchanged: tracked contract + Batch 0.1 owner-machine live probe + direct validator verification; the ownership merge touched neither `frontend/features/courses/schemas.ts` nor the contract's `CourseResponse`, so the F5 settlement stands verbatim).
2. Focused tests cover both relevant datetime shapes — **SATISFIED** (re-verified fresh today: 17/17 in `lib/api.test.ts`, 54/54 unit).
3. Course list and course detail continue to load against the live API when the documented environment and credentials are available — **BLOCKED / NOT RUN (unchanged)** — the sole unsatisfied criterion; environment/credentials still unavailable, re-confirmed today with the same diagnostics as the original block.
4. Non-performable live verification explicitly recorded — **SATISFIED** (originally rows 7–8 of the 1.4 Verification table; re-recorded today as row 9 above).

**Closeout verdict: Batch 1.4 does NOT yet qualify for DONE.** Implementation, unit coverage, and the sandbox matrix are verified — now twice, independently — but criterion 3 requires the live-API check that only the documented owner-machine/staging environment can perform. The status stays **PARTIALLY EXECUTED**; the batch closes as far as this environment can honestly close it, with the completion path unchanged. This closeout adds evidence and reconciliation only — it does not weaken, redefine, or waive any criterion, and it attributes nothing of the ownership fix to Batch 1.4.

#### Files changed
Exactly this ledger (this closeout entry, the Current State refresh, the Execution History row, the Batch Status Board 1.4 row, Open Question #7, and Next Authorized Batch). No roadmap DOCX edit: the lifecycle rules place live statuses in this ledger's Batch Status Board ("all details in roadmap v2.0 §13–§14; statuses here"), and no prior batch updated the DOCX for status alone. No application code, no `docs/openapi.json`, no frontend file, no CI or dependency file.

#### Commit
N/A (closeout is documentation-only; per the lifecycle rules the executor does not commit — Seyam applies the patch `frontend-redesign-1.4-closeout-evidence-based-review.patch`).

#### Gate impact
None claimed. Gate A remains passed; Gate B requires the full closure set (1.1 ✓ + 1.2 ✓ pending owner confirmation + 1.3 ✓ pending the Sentry runtime verification + 1.4 ✓ pending the live-API check) and the local matrix green including E2E with credentials — not satisfied yet, unchanged by this closeout.

---

### 2.1 — discovery: demo journey, page architecture, and environment lock (documentation + provisioning)

Status: **PARTIALLY EXECUTED (2026-10-18)** — the owner-directed discovery, runbook, environment lock, dataset plan, and instructor-account provisioning are delivered; the journey/dataset lock awaits Seyam's decisions on the report's open-items table, and the rehearsal (setup + bootstrap first run + scripted walk) is an owner-machine step. No application code changed; the roadmap DOCX was not modified.

#### Purpose and authorization
Seyam's 2.1 discovery prompt: verify the reported baseline `60d3ba5` and the Batch 1.4 closeout record; treat five decisions as authoritative (A local-first demo environment; B substantial redesign of all implemented pages with visual execution in Phase 4 and functional contracts frozen; C extensible page architecture without premature abstraction; D the material journey — upload → processing status → resulting state — is essential and must not be faked or implemented in 2.1; E an instructor-role course-owner test account is approved); produce an evidence-based page inventory, a broader IA proposal, a design-reference shortlist, a recommended demo journey with per-step readiness, an environment/dataset plan, and a scope assessment; document the local-first change in the permitted records and list the roadmap wording needing reconciliation without rewriting the DOCX.

#### Repository preflight (before any edit)
- `git fetch origin --prune`: `origin/frontend-redesign` advanced `92b67bd..60d3ba5` — exactly one commit, `1.4-closeout-evidence-based-review`, authored by Seyam 2026-10-17; `git diff --stat 92b67bd..60d3ba5` = this ledger +64/−9, and the diff is **byte-identical to the delivered `frontend-redesign-1.4-closeout-evidence-based-review.patch`** — the closeout patch was applied verbatim and committed by Seyam.
- Research base: a detached worktree created from the execution clone at `60d3ba5` (`git worktree add`, clean tree). The execution clone itself (branch at `92b67bd`, its then-uncommitted ledger change, and `stash@{0}`) was preserved untouched; that ledger change is byte-identical to the committed `60d3ba5` content. No reset, rebase, force-push, or discard of any kind.

#### The Batch 1.4 record and the owner's confirmation (addendum)
- The committed closeout entry records 1.4 as **PARTIALLY EXECUTED** with criterion 3 ("course list and course detail continue to load against the live API") **BLOCKED / NOT RUN**, verbatim: "Batch 1.4 does NOT yet qualify for DONE." That was accurate when written (the execution environment has no Docker daemon, no local stack, no credentials).
- Seyam has now confirmed that the required live-API flow **was tested successfully on his machine** — the documented environment the closeout named as the completion path. This addendum records criterion 3 as **satisfied on the owner's confirmation** (the executing agent did not personally perform or observe the test; specifics of the owner's run rest with the owner), and upgrades Batch 1.4 to **EXECUTED** in the Status Board, Execution History, and Current State. No criterion was redefined; the closeout evidence stands as written; the ownership fix (PR #79) remains a separate change.
- Gate B remains unclaimed: 1.2's owner validation and 1.3's Sentry runtime verification are still outstanding, and the local matrix including E2E with credentials remains an owner-machine item.

#### What the discovery verified (evidence base for the runbook)
- **Route inventory:** exactly nine `page.tsx` files at `60d3ba5` (landing, login, register, dashboard, courses list, courses/new, courses/[id], courses/[id]/edit, profile) plus both group layouts, both groups' `error.tsx`/`loading.tsx` (S8 verified complete), root layout, `not-found.tsx`. S1/S2 dishonesty re-verified present in code (hard-coded "Student Dashboard", three "Coming soon" stat cards, two "Coming soon" sections with mislabeled "Open Chat"/"View Graph" buttons, "Active Materials" course-count mislabel, "My Materials" nav label, landing marketing RAG/quizzes/flashcards/graph with dead tiles). Zero materials code exists in the frontend (the only "material" strings are the mislabels).
- **Material journey:** the four material operations exist in the contract (upload-url; register → 202 {material_id, job_id}; list; status — four-value literal `pending → processing → ready | failed`) and the pipeline is staging-proven; the frontend surface is Batch 4.3 scheduled scope; **the local dev compose defines only `db` + `keycloak` + the one-shot bootstrap — no S3-compatible storage (boto3 client gets empty credentials; no endpoint), no Redis, no Celery worker** — so `upload-url` fails and a registered material would stay `pending` forever locally. Readiness recorded per step in the runbook (NOT READY / PARTIALLY READY ratings with owning batches). No retry/document-content/search/chat/enrollment endpoint exists — nothing faked.
- **Environment:** the documented local workflow (`docs/development/LOCAL_SETUP.md` + `scripts/setup-dev.sh`, idempotent, non-destructive, secrets generated into git-ignored `.env.local`) supports the demo surface for the consumed operations (providers default to mock; no API keys); staging is staging-proven for the pipeline and demoted to optional per owner decision A; the staging CORS preflight (Q2) reclassified as optional evidence.
- **Accounts:** `infra/dev/bootstrap-keycloak.sh` provisions only `testuser` (role `student`); the realm export already defines the `instructor` role; no instructor account exists. Provisioning for `instructor` / `instructor@example.com` is added by this patch (bootstrap block mirroring the testuser pattern; `OPENLEARN_INSTRUCTOR_USER_PASSWORD` passed through the compose bootstrap service; `setup-dev.sh` generates it into `.env.local` on first creation and appends it to an existing `.env.local` with a notice; LOCAL_SETUP gains a demo-accounts section). **Implemented but NOT executed in the sandbox (no Docker daemon); first run is an owner-machine step; manual kcadm fallback documented in LOCAL_SETUP.**
- **References:** no design-reference selection exists in curated repo records (the raw AI competitive snapshot is explicitly non-authoritative); a five-entry shortlist (LearnHouse, NotebookLM, Google Classroom, Moodle 4.5 course page, Edraak) with URLs, patterns-to-study, cautions, and capability dependencies is proposed for owner review — a recommendation, not a decision.

#### Runbook and dataset (delivered; not yet rehearsed)
The discovery note doubles as the runbook a second person could follow: prerequisites, one-command setup, service topology, backend/frontend startup, availability confirmation, teardown/restart, known gaps, optional-staging rules, the 11-step journey table (per-step route/user/action/expected result/API dependency/readiness/prerequisite/success criterion), the dataset (2 users, 3 instructor-owned courses with `testuser` owning none — the PR #79 scoping made visible, 1–2 text-rich PDFs, no seed script per roadmap §19), and reset behavior. The rehearsal that roadmap §14 names ("dataset steps documented and rehearsed once") requires Docker and is recorded as the outstanding owner-machine step.

#### Roadmap reconciliation (recorded, not executed)
Nine wording items (R1–R9) where the roadmap/records still say staging-default (§14 Batch 2.1 "staging confirmed as demo environment…", 4.3 "on staging" walkthrough, 5.3 "Staging validation and demo dry run", §15 "Staging credential", §24 matrix rows, §19 conditionality, 0.2 note Q4 default, ledger Q2, 5.3 title) are listed in the discovery note §5.2 for a future authorized documentation batch. No DOCX was edited in this batch.

#### Files changed
Exactly: this ledger; the new `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-2.1_Discovery_Demo-Journey_Environment-Lock.md`; `infra/dev/bootstrap-keycloak.sh`; `infra/docker-compose.dev.yml`; `scripts/setup-dev.sh`; `docs/development/LOCAL_SETUP.md`. No application code, no `docs/openapi.json`, no frontend file, no CI/dependency file, no roadmap DOCX.

#### Verification performed
Git preflight and byte-identity checks (above); full reads of the governance trio, the 0.2 decision note, and the v4 spec's governing sections; direct source reads of the entire frontend route tree, shell, features, and the backend storage/materials/celery/compose/bootstrap/setup sources; test matrices cited from the 1.4 closeout (frontend unit 54/54, lint/typecheck, storybook 42/42, build 9 routes; backend course+contract 32/32; regression 254 passed / 1 pre-existing environmental docling failure) — unchanged by the ledger-only `60d3ba5`, not re-run. NOT RUN: any Docker-dependent step (setup script execution, bootstrap first run, local journey rehearsal) — recorded as owner-machine steps.

#### Completion state
Runbook + decisions delivered; **Batch 2.1 stays open on**: (1) Seyam's lock of the journey sequence and dataset (report open-items table), (2) the owner-machine rehearsal (setup-dev.sh + bootstrap first run + scripted walk). Recommended next authorization at the time of that entry: Batch 2.2 — superseded by the owner's sequencing decision recorded in the decision-lock entry below.

---

### 2.1 — decision lock: product direction record (documentation-only)

Status: **COMPLETE (2026-10-18)** — the owner's decisions from the discovery review are preserved in the new standalone record `OpenLearn-AI_Batch-2.1_Product-Owner_Decision-Lock.md` (the authoritative decision text) and summarized here; research, decision reconciliation, and documentation only; no application code, no DOCX edit, no environment implementation.

#### Purpose and authorization
Seyam's decision-lock prompt: preserve the discovery-review decisions in two durable places (this ledger + a standalone Product-Owner Decision Record); investigate every related uncertainty in the actual repository, API contracts, technical specification, execution roadmaps, or existing implementation before documenting a decision as final; do not turn assumptions into facts; distinguish decisions, implementation facts, and future work; reconcile R1–R9; do not implement the frontend redesign or the local AI environment in this batch.

#### What was verified before recording (evidence base)
- Baseline: fresh clone at `005711e` (= `origin/frontend-redesign`; clean tree; parent `60d3ba5`); the commit is exactly the owner's application of the 2.1 discovery patch (6 files, +663/−17). The roadmap DOCX last changed at `699c496` (FR-REB-02) — the R1–R9 wording is confirmed still present verbatim (R1 and R3 captured from the §14 tables; R7 from the 0.2 note line 77).
- Profile/onboarding contract audit: `backend/app/schemas/profile.py`, `backend/app/api/users.py`, `backend/app/services/profile_service.py`, `backend/app/models/profile.py`, spec §15.1, `frontend/features/profile/schemas.ts` + `frontend/components/profile/ProfileForm.tsx`. **All six candidate onboarding fields are already supported** — education_level (str 1–50; spec enum members undefined, free-form string carried), major (str 1–255), preferred_language (Literal `en|ar` + DB CHECK), university (optional str 1–255), learning_style_vark (optional str ≤20), daily_available_minutes (strict int 1–1440). `PUT /v1/users/me` is a full-replacement upsert (required fields must be resent on every update; omitted optionals cleared); `GET /v1/users/me` returns 404 when no profile exists — the natural, already-supported onboarding trigger and completion signal. No endpoint support, persistence, or required-field behavior invented.
- Auth flow: `/login` renders a local shell whose form calls `keycloak.login(...)`; `/register` calls `keycloak.register(...)` with the `/dashboard` redirect; the credential and registration forms are Keycloak-hosted pages; registration enabled by the bootstrap (`registrationAllowed=true`); no Keycloak theme assets exist anywhere in the repository.
- Language/RTL: `frontend/app/layout.tsx` hardcodes `lang="en" dir="ltr"` with the Noto Sans Arabic font rail loaded; no i18n framework, locale switching, or direction handling exists; `profiles.preferred_language` (`en|ar`, DB CHECK) exists but is consumed only as a form-field default; the 44-week plan schedules RTL + bilingual verification against NFR-8 at W37/W41.
- Material journey characterization re-verified at `005711e`: the four contract operations stand (roadmap §6 rows verbatim "Scheduled — Batch 4.3"); zero frontend materials code (the only "material" strings are the S1/S2 mislabels); the dev compose still defines exactly db + keycloak + keycloak-bootstrap (no S3-compatible storage — `backend/.env.example` points at `localhost:9000` with empty credentials — no Redis, no Celery worker). The owner's characterization (backend implemented; gap = local environment + frontend journey) is recorded as **accurate with two qualifications**: the complete end-to-end flow has never run locally, and "inspect the resulting state" means status + list only (no document-content endpoint — the Week 9 blocked-tier item).
- Roles/ownership corroboration (kept distinct from the owner's acceptance testing): `course_service.list_courses(db, owner_id)` owner filter and `require_owned_course` (404/403) are present at HEAD; the automated evidence is cited from its own batches (Phase 2: course tests 31/31 at `e10249f`; 1.4 closeout: course+contract 32/32 at `92b67bd`) — not re-run here.
- Dataset: all 30 PDFs in the two born-digital folders enumerated and extraction-tested (pypdfium2, read-only; every file opened, 1 page each). **Locked:** English `custom_custom_english_born_digital_005_p001.pdf` (56,951 B, 3,501 extracted chars — AlexNet paper p.1) and Arabic `custom_custom_arabic_born_digital_003_p004.pdf` (41,392 B, 1,797 chars); alternates recorded in the decision record. NOT tested: Docling parsing (including Arabic order handling), upload, processing — environment-batch work.
- Roadmap DOCX Batch 4.3 definition captured verbatim ("Batch 4.3 — Course detail hub, forms, delete confirmation, materials surface") — the discovery's Batch 4.3 identifier stands.

#### Decisions recorded (statuses per the decision record)
A local-first — **APPROVED**. B substantial redesign (public landing at `/`; authenticated users redirected to `/dashboard`; real capabilities only; `Get Started`/`Log in` CTAs; truthful dashboard) — **APPROVED**. C maintainable, appropriately scoped architecture — **APPROVED**. D material journey essential — **APPROVED** (with the two qualifications above; frontend surface Batch 4.3). E student/instructor roles + course ownership — **CLOSED** (owner-confirmed acceptance; do not reopen without new contradictory evidence; the roles' similar-looking UI is a future role-aware UX concern). Landing/auth entries + continued Keycloak OIDC/PKCE — **APPROVED** (the authenticated-`/` redirect is approved direction, not yet implemented). Keycloak login/registration appearance — **DEFERRED** to a later separately scoped batch. Sidebar replacing the navbar — **APPROVED** as the redesigned-shell direction (Batch 3.3's home; account/logout near the bottom; role-aware affordances only). First-login onboarding — **APPROVED** as product direction; contract audit complete; batch assignment = owner question. Language preference/RTL — **APPROVED** as the intended UX policy; implementation details **PENDING EVIDENCE**.

#### R1–R9 and sequencing
All nine items re-verified in their sources; R8 was already reclassified by the 2.1 discovery; R1–R7 and R9 remain **OPEN** with disposition = the comprehensive documentation reconciliation batch that follows the environment batch (not this batch, and not silently). **Sequencing locked by the owner:** the next implementation batch is the local environment gap closure and practical verification; then the comprehensive documentation reconciliation; frontend execution (2.2 → Phases 3–4, materials surface at 4.3) resumes afterward, each batch on Seyam's explicit authorization.

#### Files changed
Exactly: the new `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-2.1_Product-Owner_Decision-Lock.md`; this ledger. No application code, no `docs/openapi.json`, no CI/dependency file, no roadmap DOCX, no compose/script change.

#### Verification performed
Git preflight (clone/HEAD/origin equality/commit-stat/DOCX history); full reads of the lifecycle rules, this ledger, the discovery report, the 0.2 note's Q4 region, the 44-week plan (structure plus targeted passes: W6 profile subset, W9, W17, W37/W41, staging cadence), and spec §15.1 with its surroundings; source-level contract audit (profile schemas/router/service/model, auth schemas, login/register pages + LoginForm call sites, landing page, root layout, course service/API, dev compose, bootstrap script, realm export, `.env.example`); DOCX extraction via python-docx (35 tables scanned); pypdfium2 extraction test over all 30 dataset candidates; search-based absence proofs (no materials code, no i18n/direction handling, no logical-property usage in globals.css, no Keycloak theme, `require_admin` still without call sites). NOT RUN: any Docker/API/browser/test execution — no Docker daemon in this sandbox and the batch is documentation-only; the cited test matrices belong to their recorded batches.

#### Completion state
Decision lock delivered; **Batch 2.1 remains open on the owner-machine rehearsal only** (setup-dev.sh + bootstrap first run + scripted walk of the READY steps). Next batch: **local environment implementation and practical testing**, then the comprehensive documentation reconciliation.

---

## Batch Status Board (all details in roadmap v2.0 §13–§14; statuses here)

| Phase | Batch | Title | Status |
|---|---|---|---|
| 0 | 0.1 | Baseline verification run | **EXECUTED** (2026-10-14) — baseline run 5/6 script checks PASS; local verification run completed the E2E trio (3/3), F5 live probe, and local CORS preflight; staging preflight carried to 2.1 (Open Question #2) |
| 0 | 0.2 | Scope freeze | **EXECUTED** (2026-10-15) — decision note authored; classification/exclusions/demo candidate frozen; finding register closed (20 dispositions + 5 retired IDs); F5 settled |
| 1 | 1.1 | Correctness fixes on core flows (F3, F4, S10, F6) | **EXECUTED** (2026-10-15) — all four findings fixed, F6 policy tests added, sandbox matrix green; owner-machine completion run: E2E trio 3/3, Storybook 42/42, lint/typecheck/build PASS, manual light/dark S10 check successful; patch applied upstream as `7dc9f67` |
| 1 | 1.2 | Authentication surface completion (W1, S3, S8) | **PARTIALLY EXECUTED** (2026-10-15) — W1/S3/S8 implemented, 12 focused tests added, sandbox matrix green (lint/typecheck/unit 49/storybook 42/build); login E2E + three manual auth validations pending on the owner machine |
| 1 | 1.3 | Observability and configuration closure (F1 chain, W8) | **PARTIALLY EXECUTED** (2026-10-15) — F1 chain wired across all five primary files (build ARG, workflow build-arg + `secrets` input + heredoc, compose, env example) with BuildKit secret mounts for the three upload secrets; `engines.node: "^20 || ^22"` from CI/deploy evidence (W8); chain script 40/40, sandbox matrix green (lint/typecheck/unit 49/storybook 42/build 9 routes); **Sentry staging runtime verification BLOCKED / NOT VERIFIED** (deployment + GitHub Secrets + Sentry access required) |
| 1 | 1.4 | Data contract settlement (F5, metric inventory) | **EXECUTED** (2026-10-17; live-API validation owner-confirmed 2026-10-18) | — F5 settled: schema frozen as-is per 0.2 §4 (live emission matches the `date-time` contract; zero schema change); 5 focused datetime tests added pinning the real schema at the apiFetch boundary (unit 54/54); real dashboard-metric inventory written (this ledger, 1.4 log entry); sandbox matrix green (lint/typecheck/unit 54/storybook 42/build 9 routes); **live-API validation BLOCKED / NOT RUN** (missing environment prerequisites); closeout review 2026-10-18 re-verified the evidence at `92b67bd` (frontend unit 54/54 incl. F5 file 17/17, lint/typecheck PASS; backend course+contract 32/32) and recorded the post-1.4 course-ownership merge (PR #79) as a separate change; **criterion 3 satisfied 2026-10-18 on Seyam's confirmation that the live-API flow passed on his machine (recorded by the 2.1 discovery addendum; not performed by the executing agent) — status EXECUTED** |
| 2 | 2.1 | Demo journey and environment lock (+ instructor test user; materials-walk decision) | **PARTIALLY EXECUTED** (2026-10-18) — discovery/runbook note delivered (nine-route inventory confirmed; material journey audited: API-complete, frontend surface = 4.3, local env lacks storage/broker/worker — no faking); environment locked local-first (owner decision A; roadmap wording R1–R9 recorded for reconciliation); materials walk adopted as essential (owner decision D); instructor-account provisioning implemented (bootstrap + compose + setup + LOCAL_SETUP), first execution an owner-machine step; journey sequence + dataset proposed for owner lock; **rehearsal outstanding on the owner machine**; decision lock added 2026-10-18 (journey direction + dataset locked to two extraction-tested PDFs; onboarding contract audited — all six fields supported; roles/ownership CLOSED on owner acceptance; R1–R9 dispositions fixed; next batch = local environment implementation) |
| 2 | 2.2 | Honest-surface settlement (S1, S2, role-aware copy) | NOT STARTED |
| 3 | 3.1 | Design direction and tokens | NOT STARTED |
| 3 | 3.2 | Design system foundations in code | NOT STARTED |
| 3 | 3.3 | Application shell (role-aware) | NOT STARTED |
| 4 | 4.1 | Auth screens and landing page | NOT STARTED |
| 4 | 4.2 | Dashboard and courses list (role-aware) | NOT STARTED |
| 4 | 4.3 | Course detail hub + forms + delete confirmation + **materials surface** | NOT STARTED |
| 4 | 4.4 | Profile, global states, responsive/RTL pass | NOT STARTED |
| 5 | 5.1 | Test suite alignment (+ affordance-visibility checks) | NOT STARTED |
| 5 | 5.2 | Verification runs (E2E promotion 3/3, a11y, sweeps) | NOT STARTED |
| 5 | 5.3 | Staging validation and demo dry run (+ pinning) | NOT STARTED |

Gates: A (functional reality) → B (closure set done) → C (demo surface locked) → D (design direction locked) → E (redesign complete) → F (presentation ready). **Gate A PASSED (2026-10-15)** — with the staging-host CORS preflight recorded as a carried-over evidence item routed to Batch 2.1 (owner scope decision; local preflight confirmed). Gates B–F pending.

## Open Questions (current)

| # | Question | Owner | Path |
|---|---|---|---|
| 1 | Does the live API emit offset-bearing datetimes (F5)? | Executing dev | **CLOSED (2026-10-14):** YES — 5/5 values offset-bearing (sample `2026-10-14T15:52:48.551399Z`); the `offset: true` schema is correct as-is; Batch 1.4 keeps it and reduces to the dashboard real-metric inventory |
| 2 | Staging CORS live preflight — the LOCAL preflight is confirmed (2026-10-14: HTTP 200, origin echo, authorization allowed); the staging-host confirmation is outstanding. | Executing dev | **RECLASSIFIED (2026-10-18):** optional evidence for the now-optional staging environment — the owner set local as the default demo environment (Q4 ANSWERED below), so the staging-host confirmation is not a demo prerequisite; closable anytime via `scripts/run-batch-0.1-local-verification.sh --with-staging-preflight` from a staging-reachable host |
| 3 | E2E promotion re-sequenced to Gate F — team-lead sign-off. | Team lead | Recorded decision at Gate F |
| 4 | Staging or local as the demo environment? | Executing dev | **ANSWERED (2026-10-18, owner decision A): LOCAL** — local development is the default and the local stack is the primary demo environment; staging is optional for selective use; the roadmap's staging-default wording (§14 Batch 2.1, 4.3 validation, 5.3, §15, §24) is recorded for formal reconciliation in the 2.1 discovery note §5.2 (R1–R9) |
| 5 | Does the materials walk join the locked demo journey? | Executing dev | **ANSWERED (2026-10-18, owner decision D): YES — adopted as essential.** The upload → status → resulting-state journey stays in the target demo as a designed segment with honest readiness ratings (2.1 discovery note §11); it is NOT implemented in 2.1 — the frontend surface is Batch 4.3 scope and the processing environment (local AI profile preferred, or staging fallback) is a 4.3-era decision; the instructor-role course-owner test-user provisioning is included in the 2.1 patch |
| 6 | Keep or remove the unreachable `(app)` loading boundary (S9)? | Executing dev | Trivial decision in Batch 3.2 |
| 7 | Backend response to the course owner-scoping defect; shape of the Week 9 reprocess endpoint when it lands. | Backend pod | **First half ANSWERED (2026-10-17):** the owner-scoping fix merged upstream as PR #79 (`65c8a8c` + merge `92b67bd`) — `GET /v1/courses` and `GET /v1/courses/{id}` are now owner-scoped (owner-only list/view; no admin override; no enrollment sharing); the 1.4 metric-inventory limitation (a) is resolved at the data layer and the Batch 2.2 course-count copy decision is unblocked. Second half (Week 9 reprocess endpoint shape) still open; frontend adapts only when contracts land in `docs/openapi.json` |

## Next Authorized Batch
**Batch 1.4 is EXECUTED**: implemented at `e10249f` (applied upstream by Seyam), closeout-verified at `92b67bd`, and completed on 2026-10-18 when Seyam confirmed that the live-API validation criterion ("course list and detail load against the live API") passed on his machine — recorded by the 2.1 discovery addendum with attribution (the executing agent did not perform that test). The course-ownership fix merged after 1.4 (PR #79: `65c8a8c` + merge `92b67bd`) remains a separate backend change. **Gate B is still not claimable**: 1.2's owner-machine validation and 1.3's Sentry runtime verification remain outstanding, as does the local matrix including E2E with credentials.

**Batch 2.1 is PARTIALLY EXECUTED (2026-10-18)**: the owner-directed discovery is delivered (runbook/discovery note — nine-route inventory; material journey audited with honest NOT READY ratings; IA recommendation; five-entry design-reference shortlist; 11-step journey table; local-first runbook and dataset plan; R1–R9 recorded; instructor-account provisioning implemented, first run an owner-machine step), and the **decision lock is now also delivered** (`OpenLearn-AI_Batch-2.1_Product-Owner_Decision-Lock.md` + the 2.1 decision-lock entry above): journey direction and dataset owner-locked (two extraction-tested benchmark PDFs), the onboarding contract audited (all six candidate fields already supported), roles/ownership CLOSED on owner-confirmed acceptance, and R1–R9 dispositions fixed. **Batch 2.1 stays open on the owner-machine rehearsal only** (`bash scripts/setup-dev.sh` — which also provisions the `instructor` account — followed by a scripted walk of the journey's READY steps). The staging CORS preflight (Q2) is optional evidence, not a prerequisite.

**The next authorized batch is the local environment gap closure and practical verification** (owner sequencing decision, 2026-10-18): inspect the 44-week plan, the technical specification, the existing Compose configuration, the storage integration, the worker configuration, and the actual pipeline requirements; determine the smallest complete local setup (S3-compatible storage including MinIO where appropriate, Redis, Celery workers, and their configuration) that exercises the existing material-processing flow; implement it and test it practically — not a documentation exercise. **A comprehensive documentation reconciliation batch follows** that environment work and testing (it executes R1–R9 in the roadmap DOCX and 0.2 note, assigns first-login onboarding to a named batch, and settles the language/RTL staging). Frontend execution then resumes per the roadmap — **Batch 2.2 — Honest-surface settlement** remains the next frontend authorization (scope grounded by the discovery: S1 dashboard settlement on the locked real-metric composition, removal of the mislabeled Open Chat / View Graph affordances and the Active Materials mislabel, S2 landing honesty, the role-aware/neutral dashboard heading), with the materials surface at Batch 4.3. Per the lifecycle rules, no batch starts until Seyam explicitly authorizes it.
