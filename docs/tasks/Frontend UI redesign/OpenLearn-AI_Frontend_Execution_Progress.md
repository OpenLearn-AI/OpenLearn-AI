# OpenLearn-AI Frontend Execution Progress

## Purpose

This file is the **living execution record** for:

`OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx`

located at `docs/tasks/Frontend UI redesign/` (the canonical execution-context directory). The roadmap was fully rewritten in place by batch **FR-REB-02** (2026-10-08) — in-document revision **v2.0**; the file name keeps `v1.1` for path stability. The roadmap defines what we intend to do. This file records what we actually did, what is true right now, and what is authorized next.

Revision lineage of this context: authored 2026-10-01 against `staging @ c51f3f1` → re-baselined by FR-REB-00 (roadmap v1.2, against `4c55ecd`) → amended by FR-REB-01 (roadmap v1.3) → **fully rewritten by FR-REB-02 (roadmap v2.0, against `2eccad0`)**. Older ledgers' amendment layering was deliberately collapsed into the concise execution history in this file; the roadmap no longer carries any patchwork structure.

---

## Current State (verified 2026-10-08 at the start of FR-REB-02)

- Repository HEAD: `2eccad0cf13d9ce2ab2a2fa1a4c02daf1077a2e5` — branch `frontend-redesign`, equal to `origin/frontend-redesign`; a merge commit synchronizing the branch with `origin/staging` @ `d1ba348f0d904a60d7e185a95609c110e4dc0422` (staging merge PR #78, `feature/backend-week8`, plus the FR-REB-01 amendments commit `ad64e0c`)
- Working tree at batch start: clean
- Current phase: 0 — Current-State Lock (not started)
- Current batch: **FR-REB-02 — Full execution-context rewrite + Week 9 integration (documentation-only) — COMPLETE**
- Current gate: none passed yet (Gate A is the first)
- Overall status: **EXECUTION CONTEXT REWRITTEN** — roadmap v2.0 carries the current repository truth, the backend→frontend coverage matrix, and the Week 9 integration; all 18 implementation batches remain NOT STARTED; next authorized batch is **0.1**

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

Contract facts: `created_at` fields are declared `format: date-time` in the tracked spec (the F5 live-emission check remains a Batch 0.1/1.4 task); the status vocabulary is the four-value literal `pending → processing → ready | failed`; there is **no retry/reprocess endpoint, no document-content endpoint, no search/chat/citation/enrollment endpoint** in the contract.

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

## Batch Status Board (all details in roadmap v2.0 §13–§14; statuses here)

| Phase | Batch | Title | Status |
|---|---|---|---|
| 0 | 0.1 | Baseline verification run | NOT STARTED |
| 0 | 0.2 | Scope freeze | NOT STARTED |
| 1 | 1.1 | Correctness fixes on core flows (F3, F4, S10, F6) | NOT STARTED |
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

Gates: A (functional reality) → B (closure set done) → C (demo surface locked) → D (design direction locked) → E (redesign complete) → F (presentation ready). None passed.

## Open Questions (current)

| # | Question | Owner | Path |
|---|---|---|---|
| 1 | Does the live API emit offset-bearing datetimes (F5)? The tracked contract declares `format: date-time`; live emission still unverified. | Executing dev | Batch 0.1 probe; settled in 1.4 either way |
| 2 | Staging CORS live preflight — compose-level configuration verified; the live preflight is a confirmation, not an investigation. | Executing dev | Batch 0.1 |
| 3 | E2E promotion re-sequenced to Gate F — team-lead sign-off. | Team lead | Recorded decision at Gate F |
| 4 | Staging or local as the demo environment? | Executing dev | Batch 2.1, driven by Q2 |
| 5 | Does the materials walk join the locked demo journey? | Executing dev | Batch 2.1 decision; requires the instructor-role course-owner test user either way |
| 6 | Keep or remove the unreachable `(app)` loading boundary (S9)? | Executing dev | Trivial decision in Batch 3.2 |
| 7 | Backend response to the course owner-scoping defect; shape of the Week 9 reprocess endpoint when it lands. | Backend pod | Flagged upstream; frontend adapts only when contracts land in `docs/openapi.json` |

## Next Authorized Batch

**Batch 0.1 — Baseline verification run** on baseline `2eccad0` (read-only): the six script runs, the F5 live probe, the staging CORS preflight confirmation, baseline notes for Gate A. It does not start until Seyam authorizes it.
