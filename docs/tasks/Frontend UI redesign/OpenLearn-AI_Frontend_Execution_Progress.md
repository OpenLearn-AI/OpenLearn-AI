# OpenLearn-AI Frontend Execution Progress

## Purpose

This file is the **living execution record** for:

`OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx`

located at `docs/tasks/Frontend UI redesign/` (the canonical execution-context directory). The roadmap was fully rewritten in place by batch **FR-REB-02** (2026-10-08) — in-document revision **v2.0**; the file name keeps `v1.1` for path stability. The roadmap defines what we intend to do. This file records what we actually did, what is true right now, and what is authorized next.

Revision lineage of this context: authored 2026-10-01 against `staging @ c51f3f1` → re-baselined by FR-REB-00 (roadmap v1.2, against `4c55ecd`) → amended by FR-REB-01 (roadmap v1.3) → **fully rewritten by FR-REB-02 (roadmap v2.0, against `2eccad0`)**. Older ledgers' amendment layering was deliberately collapsed into the concise execution history in this file; the roadmap no longer carries any patchwork structure.

---

## Current State (verified 2026-10-15, after Batch 1.1 close-out)

- Repository HEAD: `7dc9f671ee91c3678fcb1bbdac4a563cf3ab3c27` — branch `frontend-redesign`, equal to `origin/frontend-redesign` (the Batch 1.1 patch applied upstream and pushed by Seyam as commit `frontend-redesign-1.1-correctness-fixes-core-flows`). Lineage since the 0.1 baseline: `699c496` (FR-REB-02 patch commit) → `bea19f3` (Batch 0.1 patch applied by Seyam) → `7ebe978` (`scripts/run-batch-0.1-local-verification.sh`, committed by Seyam) → `18d8a69` (0.1-completion + 0.2 scope-freeze patches applied by Seyam as one commit) → `7dc9f67` (Batch 1.1 patch applied by Seyam). Staging containment re-verified at `7dc9f67`: `git merge-base --is-ancestor origin/staging HEAD` passes; `HEAD..origin/staging` empty
- Working tree at batch start: clean (fresh clone of `origin/frontend-redesign` @ `7dc9f67`)
- Current phase: 1 — Minimal Functional Closure — 1.1 EXECUTED (2026-10-15)
- Current batch: **1.1 — Correctness fixes on core flows — EXECUTED (2026-10-15)**: all four findings (F3, F4, S10, F6) fixed in code with the focused F6 policy tests (15) added; the full matrix is green — executor sandbox re-verification at `7dc9f67` (lint, typecheck, unit 37/37 incl. the 15 F6 tests) plus the owner-machine completion run (E2E trio 3/3 with real Keycloak credentials, Storybook 42/42 across 12 files, lint, typecheck, production build with all 9 application routes, and the manual light+dark success-message check). See the 1.1 completion entry below for the evidence table
- Current gate: **Gate A — PASSED (2026-10-15)** — unchanged. **Gate B NOT claimed**: it requires the full closure set (1.1 complete ✓ + 1.2 + 1.3 + 1.4) and the local matrix green including E2E with credentials (1.1's E2E evidence is in; 1.2/1.3/1.4 remain)
- Overall status: **Batch 1.1 EXECUTED (implementation + owner-machine verification); Batch 1.2 — Authentication surface completion (W1, S3, S8) — explicitly authorized by Seyam in the same prompt that supplied the owner evidence, and executed next per the one-batch lifecycle rule**

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

## Batch Status Board (all details in roadmap v2.0 §13–§14; statuses here)

| Phase | Batch | Title | Status |
|---|---|---|---|
| 0 | 0.1 | Baseline verification run | **EXECUTED** (2026-10-14) — baseline run 5/6 script checks PASS; local verification run completed the E2E trio (3/3), F5 live probe, and local CORS preflight; staging preflight carried to 2.1 (Open Question #2) |
| 0 | 0.2 | Scope freeze | **EXECUTED** (2026-10-15) — decision note authored; classification/exclusions/demo candidate frozen; finding register closed (20 dispositions + 5 retired IDs); F5 settled |
| 1 | 1.1 | Correctness fixes on core flows (F3, F4, S10, F6) | **EXECUTED** (2026-10-15) — all four findings fixed, F6 policy tests added, sandbox matrix green; owner-machine completion run: E2E trio 3/3, Storybook 42/42, lint/typecheck/build PASS, manual light/dark S10 check successful; patch applied upstream as `7dc9f67` |
| 1 | 1.2 | Authentication surface completion (W1, S3, S8) | NOT STARTED |
| 1 | 1.3 | Observability and configuration closure (F1 chain, W8) | NOT STARTED |
| 1 | 1.4 | Data contract settlement (F5, metric inventory) | NOT STARTED |
| 2 | 2.1 | Demo journey and environment lock (+ instructor test user; materials-walk decision) | NOT STARTED |
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
| 2 | Staging CORS live preflight — the LOCAL preflight is confirmed (2026-10-14: HTTP 200, origin echo, authorization allowed); the staging-host confirmation is outstanding. | Executing dev | Routed to Batch 2.1's environment lock (staging-vs-local decision; local dev is the documented fallback); closable anytime via `scripts/run-batch-0.1-local-verification.sh --with-staging-preflight` from a staging-reachable host |
| 3 | E2E promotion re-sequenced to Gate F — team-lead sign-off. | Team lead | Recorded decision at Gate F |
| 4 | Staging or local as the demo environment? | Executing dev | Batch 2.1, driven by Q2 |
| 5 | Does the materials walk join the locked demo journey? | Executing dev | Batch 2.1 decision; requires the instructor-role course-owner test user either way |
| 6 | Keep or remove the unreachable `(app)` loading boundary (S9)? | Executing dev | Trivial decision in Batch 3.2 |
| 7 | Backend response to the course owner-scoping defect; shape of the Week 9 reprocess endpoint when it lands. | Backend pod | Flagged upstream; frontend adapts only when contracts land in `docs/openapi.json` |

## Next Authorized Batch

**Batch 1.1 is EXECUTED (2026-10-15)**: implementation at `7dc9f67` (applied upstream by Seyam) + the owner-machine completion run (E2E trio 3/3, Storybook 42/42, lint/typecheck/build PASS, manual light+dark S10 check successful). The next batch in the sequence is **Batch 1.2 — Authentication surface completion (W1, S3, S8)**; Seyam explicitly authorized it in the same prompt that supplied the 1.1 owner evidence, and it is executed next per the one-batch lifecycle rule. Gate B requires the full closure set (1.1 complete ✓ + 1.2 + 1.3 + 1.4) and the local matrix green including E2E with credentials — 1.2/1.3/1.4 remain.
