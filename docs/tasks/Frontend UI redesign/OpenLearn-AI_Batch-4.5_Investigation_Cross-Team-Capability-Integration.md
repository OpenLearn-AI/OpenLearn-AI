# OpenLearn-AI — Batch 4.5 Investigation: Cross-Team Capability Integration

**Status: INVESTIGATION EXECUTED (2026-10-26). PROPOSED SCOPE BELOW — NOT IMPLEMENTED. NOTHING IN THIS BATCH MODIFIED APPLICATION CODE. Batch 4.5 implementation starts only on Seyam's explicit authorization.**

| Field | Value |
| --- | --- |
| Investigation type | Investigation Step 1 (read-only repository investigation + evidence-based planning; documentation-only repository changes) |
| Investigated at | `frontend-redesign @ 5df5abd003d5818b59b5130b8084976440d858a5` ("4.4-profile-global-states-rtl-direction", owner-applied upstream 2026-10-26 06:23 +0300) — verified as the actual `origin/frontend-redesign` tip |
| Compared against | `origin/staging @ 41cf5116370eb75549a5e1ad26ee08250dc4c7cc` (merge-base `d1ba348f0d904a60d7e185a95609c110e4dc0422`) |
| Execution context read | Lifecycle rules, the living ledger, roadmap DOCX v2.0 (DOCX-extracted), `planning/Roadmap/44-WEEK-EXECUTION-PLAN .md`, `docs/openapi.json`, the backend materials implementation + tests, CI workflows, infra |
| Repository changes by this batch | Exactly two documentation paths: this note + the execution ledger. No application code, no backend code, no contract, no workflow, no infra, no roadmap DOCX |
| Proposed next step | One implementation batch — **4.5 — Materials lifecycle completion: extracted-text viewer + reprocess control** (Section 7). Awaiting Seyam's authorization |

---

## 1. Repository and branch evidence (Deliverable A)

### 1.1 Starting state (verified before any work)

The execution environment held the previous session's clone (`openlearn-batch43`) at local `HEAD 3d1da92` with the Batch 4.4 work **uncommitted** in its working tree (11 modified + 8 untracked paths). Per the lifecycle's preservation rules, that tree was **not touched**. `git fetch origin` showed the owner had applied 4.4 upstream:

- Local (stale) clone: branch `frontend-redesign`, `HEAD 3d1da92` (the 4.3 base), working tree carrying the uncommitted 4.4 changes.
- `origin/frontend-redesign` = **`5df5abd003d5818b59b5130b8084976440d858a5`** — the owner's commit `4.4-profile-global-states-rtl-direction` (Author MuhammadSeyam, 2026-10-26 06:23:09 +0300), 19 files, +1221/−173.
- `origin/staging` = **`41cf5116370eb75549a5e1ad26ee08250dc4c7cc`**.
- **Protection verification**: every one of the 19 locally-uncommitted 4.4 files was compared against `5df5abd0` — all 11 modified tracked files byte-identical (`git diff 5df5abd0 --stat` over tracked files: empty) and all 8 untracked files md5-identical to the committed versions. The pre-existing local work is redundant with upstream; nothing was lost, discarded, or overwritten. The stale clone and its working tree remain untouched.
- The investigation then ran in a **fresh isolated clone checked out (detached) at `5df5abd0`** with a clean tree — the safe-inspection route the task prescribes.

### 1.2 Branch relationship (both branches fetched, no merge performed)

```
merge-base(origin/frontend-redesign, origin/staging) = d1ba348f0d904a60d7e185a95609c110e4dc0422
origin/staging        = 41cf511  (merge PR #80 pod-d/staging-compose)
origin/frontend-redesign = 5df5abd  (4.4) … 3.1..4.4 redesign + backend Week 9 (PR #81)
```

- `git merge-base --is-ancestor origin/staging HEAD` → **NO** (staging is NOT contained in `frontend-redesign`); the reverse also NO — the branches are **diverged** at `d1ba348`.
- **Commits only on `staging`** (2): `c69a31c` "security(staging): bind backend/frontend/keycloak to localhost only (nginx-only access)" (3 lines in `infra/docker-compose.staging.yml`) + the merge commit `41cf511` (PR #80). **Zero frontend-relevant content.**
- **Commits only on `frontend-redesign`** (~25): the entire redesign sequence (`2ead99a` 3.1 → … → `5df5abd` 4.4, incl. SIDE-01/02 and the 4.2 follow-ups) **plus backend Week 9** (`91c6e03` "feat(backend): implement week 9", merged as `06c2669` PR #81 — backend + `docs/openapi.json` only).
- The merge `frontend-redesign` → `staging` has **not** been performed (the task's stated coordination state; confirmed by the fetch). This is an owner/DevOps coordination item, not something this investigation may act on.

### 1.3 `docs/openapi.json` contract delta (merge-base → 5df5abd0)

Parsed-JSON diff (the drift-guarded, CI-guarded tracked contract; guard: `backend/tests/test_openapi_contract.py`, wired into ci.yml's backend job):

- **Operations added (3)** — all Week 9, all materials, all on `frontend-redesign` only:
  1. `GET /v1/materials/{material_id}/pages` (list; `limit` 1–500 default 100, `offset` ≥ 0)
  2. `GET /v1/materials/{material_id}/pages/{page_number}` (1-based single page)
  3. `POST /v1/materials/{material_id}/process` (manual reprocess)
- **Operations removed from the schema (1)**: `GET /metrics` (moved to a token-protected inline route with `include_in_schema=False` — review hardening B-03; infrastructure, not frontend-relevant).
- **Schemas added**: `MaterialPageResponse {page_number ≥ 1, text}`, `MaterialPagesResponse {material_id, pages[]}`.
- **Schemas changed**: `MaterialAcceptedResponse` — `job_id` is now **nullable** (Week 9 dedup reuses the existing material) and `status` was added. **The 4.3 frontend schema already matches this new shape** (`materialAcceptedResponseSchema` carries `job_id: z.string().nullable()` + `status`), so nothing existing needs repair.
- **Schemas unchanged**: `MaterialResponse` is byte-identical (no new list fields — in particular **no `retry_count` and no page count**), and `ProfileResponse`, `CourseResponse`, `CurrentUserResponse`, the course and upload schemas are unchanged. There is **no newly available field on any existing surface**.
- Net: 14 → 16 tracked operations. **The three unconsumed operations are exactly the three Week 9 additions.**

### 1.4 Environment limitations (stated honestly)

- **No runtime access**: no Docker daemon, no Keycloak, no backend/storage/worker stack, no E2E credentials in this environment. Nothing was executed against a running system; **no staging behavior was verified** (staging was inspected only through Git).
- Backend verification is **static**: the implementation, the contract, and the test suite were read and cross-checked; the tests were **not executed here**. Their CI wiring is verified (ci.yml's core job runs all of `backend/tests/` except `pal`/`documents` — which have their own job — against a digest-pinned pgvector PostgreSQL on every PR); CI run *status* for these commits is not observable from this environment.
- Frontend verification is likewise static (source reading); no build/test run was needed — no application file changed.

---

## 2. Current frontend integration inventory (Deliverable B)

### 2.1 What the frontend consumes today (at 5df5abd0)

All consumption goes through the single `apiFetch` boundary (`frontend/lib/api.ts`) with Zod validation at the edge and TanStack Query:

| Contract operation | Frontend consumer | Since |
| --- | --- | --- |
| `GET /auth/me` | `useMe()` (auth context, role derivations, hub role gating) | pre-redesign |
| `GET`/`PUT /v1/users/me` | `useProfile()` / `useProfileMutation()` (profile, onboarding wizard) | pre-redesign |
| `GET`/`POST` `PUT`/`DELETE /v1/courses…` | `useCourses`, `useCourse`, `useCourseMutations` (list, hub, forms, delete) | pre-redesign |
| `POST /v1/courses/{id}/materials/upload-url` | `CourseMaterials` upload flow (presigned **POST** — not PUT) | Batch 4.3 |
| `POST /v1/courses/{id}/materials` (register) | same flow; 202 acceptance, dedup (`job_id: null`) presented honestly | Batch 4.3 |
| `GET /v1/courses/{id}/materials` | `useMaterials(courseId)` — the list, the single rendering source | Batch 4.3 |
| `GET /v1/materials/{id}/status` | `useMaterialStatus(materialId, enabled)` — 5 s poll, terminal shutdown, unrecoverable-error shutdown | Batch 4.3 |

`GET /health` is the backend liveness probe (tier D — never UI). That is **13 of the 16** tracked operations; the remaining **3 are the Week 9 additions, consumed by no one** (verified: no `pages`/`process` reference anywhere in `frontend/features/materials/` or `frontend/components/courses/`).

### 2.2 The extension points a 4.5 surface would build on (all verified in source)

- **`MaterialRow`** (`frontend/components/courses/CourseMaterials.tsx`): already owns the per-row status poll, the status vocabulary presentation (Queued/Processing/Ready/Failed + geometric indicator), the honest failed copy, and the list-cache patching. The 4.3 batch note names "the failed/ready row's action area" as the reprocess hook point.
- **The materials feature module** (`frontend/features/materials/`): `schemas.ts` (Zod, cross-checked against the contract), `keys.ts` (hierarchical key factory with `all`/`lists`/`statuses` branches), `flow.ts` (pure helpers + 10 unit tests + the error-mapping table incl. 409/413/429 classes), `api/useMaterials.ts` (`queryOptions` pattern, `me.isSuccess` gating, poll discipline).
- **The course-detail hub** (`frontend/app/(app)/courses/[id]/page.tsx`): the Materials region (8 of 12 columns) renders `CourseMaterials` with `canUpload={canManageCourse}`; the hub-slot table (roadmap §9 / ADR-0010 §2.6) reserves "extracted text" as the first future slot — documentation only, nothing rendered (verified).
- **The role derivation** the hub already uses: `canManageCourse = me.id === course.owner_id && me.roles.includes("instructor")` — the exact population the backend's own `require_instructor` + `require_owned_course` accept.
- **The async-state kit** (LoadingBlock/ErrorState/EmptyState) is the only sanctioned state vocabulary; the Swiss Editorial Grid grammar and the RTL/logical-properties discipline (4.4) apply to any new region.

### 2.3 What the current materials surface deliberately does NOT have

No retry/reprocess control (4.3's frozen scope predates the Week 9 landing); no document-content surface of any kind; no page counts; no retry-budget display (the contract exposes `retry_count` only inside the 409 error message); no delete-material, no MIME allow-list, no upload progress percentage, no cancel-in-flight (all absent from the contract — none may be invented).

---

## 3. Cross-team capability matrix (Deliverable C)

Readiness categories: **Ready** (implemented, contract-supported, verified) · **Conditionally ready** (implementation exists; a named dependency must resolve first) · **Not ready** (missing implementation / unstable or absent contract / unresolved behavior) · **Not a frontend feature** (internal by nature).

### 3.1 The two integration candidates

| Field | **C1 — Reprocess control** | **C2 — Extracted-text viewer** |
| --- | --- | --- |
| Capability | The course owner (instructor) can ask the backend to re-run processing of a `ready` or `failed` material within a bounded manual-retry budget | The course owner can read the text the pipeline extracted, per page, for a processed material |
| Evidence | `backend/app/api/materials.py:430–509` (`process_material_handler`); `material_service.claim_material_retry` (atomic claim) + `restore_material_after_publish_failure` (F8 compensation); `models/material.py` `MATERIAL_RETRY_LIMIT = 3`, `retry_count`; 9 focused API tests in `backend/tests/test_material_api.py:1675–2020` (failed→processing, ready→reprocess, in-flight 409, budget-exhausted 409, publish-failure compensation, 404, non-owner instructor 403, student 403, unauthenticated 401); commit `91c6e03` (PR #81) | `backend/app/api/materials.py:363–427` (both handlers); `material_service.list_material_pages` (limit/offset) + `get_material_page`; `models/material_page.py`; pages persisted by the worker in the same processing transaction as `ready` (Week 9 keep-more-pages rule protects prior output on re-run); 8 focused API tests (`test_material_api.py:2267–2660`) incl. empty-before-processed, non-owner 403, 404s, 401, pagination |
| Branch status | `frontend-redesign` only (backend Week 9, PR #81). **Not on `staging`.** | Same — `frontend-redesign` only. **Not on `staging`.** |
| API contract | `POST /v1/materials/{id}/process` in `docs/openapi.json` @ `5df5abd0` — 202 `MaterialAcceptedResponse {material_id, status, job_id\|null}`; documented 401/403/404/409 (two classes: in-flight; budget exhausted)/422/429; `limit_writes` (default 30/min) | `GET /v1/materials/{id}/pages` (+`/{page_number}`) in `docs/openapi.json` — `MaterialPagesResponse`/`MaterialPageResponse`; documented 401/403/404/422; pagination `limit` 1–500 (default 100) / `offset` |
| Authorization | **Verified implemented and tested: bearer + instructor role (`require_role("instructor")`) + course ownership (`require_owned_course`) + per-user write rate limit.** Not admin-gated (see §6 decision D2). 403 tested for non-owner instructors and students | **Verified implemented and tested: bearer + course ownership** (the same `require_owned_course` as the status read; no instructor requirement). 403 tested for non-owners |
| Existing frontend surface | Confirmed absence. Documented hook point: the failed/ready `MaterialRow` action area (4.3 note §7.1) | Confirmed absence. The reserved hub slot "extracted text" (roadmap §9 Table 9; ADR-0010 §2.6) |
| User value | A failed material (e.g. OCR-quota class) stops being a dead end — retry without re-upload; a `ready` material can be re-processed after pipeline improvements. Closes the only unrecoverable state in the materials walk | `ready` becomes meaningful: the owner finally reads what processing produced — the payoff step of the demo's materials walk; first genuine content surface in the hub; per-page structure incl. Arabic text (`dir="auto"`) |
| Readiness | **Ready** (contract-supported, implemented, comprehensively tested; CI-wired) | **Ready** (same) |
| Dependencies | None for the frontend build. Runtime demonstration of a *completed* retry needs the owner's stack (worker + storage + API) — the same prerequisite as 4.3's outstanding walkthrough | Same: non-empty pages need a real `ready` material on the owner's stack; the endpoint honestly returns `pages: []` until processed |
| Recommendation | **Include in 4.5** | **Include in 4.5** (this is the 44-week plan's own Week 9 frontend assignment, and its contract has landed) |

### 3.2 Everything else examined, and why it is out of scope

| Candidate | Finding | Branch | Readiness / disposition |
| --- | --- | --- | --- |
| Week 9 dedup on registration (`job_id: null` reuse) | Backend implemented + tested; **already consumed and honestly presented by the 4.3 frontend** | frontend-redesign | Already delivered — not new scope |
| Retry-budget display ("N of M retries used") | `MaterialResponse` exposes no `retry_count`; the budget appears only inside the 409 message. The UI can surface the 409 text honestly but cannot pre-display remaining budget | — | **Design constraint on C1**, not a capability. No schema change requested (§22: backend-owned breaking changes are excluded) |
| 429 rate limiting (`limit_writes`, 30/min default) | Implemented on upload-url/register/process; already mapped in the 4.3 error table | frontend-redesign | Design constraint on C1 (honest 429 copy) |
| Newly available user/course/material data | **None.** `MaterialResponse` byte-identical; profile/course/auth schemas unchanged (verified by parsed-JSON diff) | — | No candidate |
| Admin capabilities | `require_admin` still has **zero call sites** (verified); the 44-week plan's "admin reprocess path" wording was implemented as owner+instructor (above). No admin role is enforced anywhere | — | Tier E unchanged — **no admin UI** |
| `/health`, `/metrics` (now token-protected, out of schema) | Infrastructure (tier D). `/metrics` hardening is review finding B-03 | both branches (metrics hardening: frontend-redesign) | **Not a frontend feature** |
| Worker failure reporting → Sentry (F9) | Implemented: `setup_worker_sentry()` + `CeleryIntegration` in each forked worker process (`observability.py:64–79`, wired via `worker_process_init`). Internal monitoring | frontend-redesign | **Not a frontend feature** — no UI for internal Sentry events (roadmap §20) |
| CI ingestion tests (Week 9 DevOps item) | ci.yml runs the full backend core suite (incl. the 63-test material API file and the 23-test task file) + a separate AI job (`tests/documents`: chunking + ingestion) against digest-pinned pgvector on every PR | frontend-redesign | **Internal verification support** — raises confidence in the pipeline the UI observes; no UI |
| Golden-Set Runner (Week 9 DevOps item) | **Not implemented.** No runner script exists anywhere in the repository (searched). The OCR benchmark *framework* exists (`experiments/OCR/ocr-benchmark/`: ADR-0003 methodology, ground-truth guidelines, the two decision-lock PDFs) but the 20-PDF golden-set ingestion and the measured baseline table are **not recorded** | — (framework: pre-existing) | **Not ready** — AI-pod deliverable, no frontend consequence; recorded for cross-team visibility |
| OCR/Arabic normalization benchmark results | No measured baseline in `docs/` (searched). The failed-state copy in 4.3 already names the OCR/quota cause class honestly without needing the benchmark | — | Not a frontend dependency |
| Staging-compose security binding | `c69a31c`: 3 lines binding backend/frontend/keycloak to localhost (nginx-only). Pure infrastructure | **staging only** | **Not a frontend feature**; recorded as the known divergence for the eventual merge (owner/DevOps coordination) |
| Search / chunks / citations / chat / enrollment (W10–W17) | No contracts (verified against the tracked spec — zero operations beyond the 16 listed) | — | Tier C future — unchanged; hub slots stay documentation |

---

## 4. DevOps deliverables review for frontend relevance (task §7)

Every completed DevOps item examined resolves to **internal verification or monitoring**, not to a user-facing capability: the CI test jobs (backend core + AI documents suites against real pgvector) strengthen the evidence behind the status literal the UI already renders; the worker→Sentry wiring (F9) reports task failures internally; the staging-compose hardening is infrastructure security. The Golden-Set Runner — the one Week 9 DevOps deliverable that would have produced user-visible quality outcomes — is **not implemented** in this repository. **No DevOps deliverable justifies a UI change.** This matches the roadmap's tier-D classification, which 4.5 does not propose to alter.

---

## 5. Recommended Batch 4.5 scope (Deliverable D)

### 5.1 What should be implemented (one cohesive batch)

**Both C1 and C2, as a single implementation batch** — they complete one user journey (the materials lifecycle on the course hub), share one module (`features/materials/`), one page (the hub's Materials region), one component family (`CourseMaterials`/`MaterialRow`), one hook point (the row's action area), and one test infrastructure. Splitting them would touch the same files twice — the exact rework the roadmap's sequencing logic exists to prevent. Both were already presented to the owner as decisions 1 and 2 in the 4.3 batch note §7; both contracts have since remained stable in the tracked spec through the 4.4 landing.

### 5.2 What must NOT be implemented in 4.5

- Nothing from the Future tier (search W10, chunks W11, citations W13–14, chat W15–16, enrollment W17) — no contracts exist.
- No admin UI of any kind (no enforced admin capabilities exist).
- No pagination/ETag/optimistic-concurrency work, no delete-material, no MIME allow-list, no upload progress/cancel (not in the contract; §22 exclusions stand).
- No UI for CI/Sentry/golden-set internals.
- No Phase 5 work: no E2E-suite realignment, no promotion runs, no demo dry run, no dependency pinning (5.1–5.3 keep their scope; 4.5 only adds the targeted unit/story tests its own surface needs, without claiming any Phase 5 batch complete).

### 5.3 What is blocked and why

**Nothing in the frontend scope is blocked.** The only environment facts, not blockers: (a) demonstrating a completed retry and non-empty pages requires the owner's local stack with the worker running (the same outstanding prerequisite as 4.3's materials walkthrough); (b) the Week 9 backend exists **only on `frontend-redesign`** — until the branches merge, staging cannot serve these endpoints. The primary demo environment is local (owner decision A), so (b) affects only any optional staging use, and is an owner/DevOps coordination item outside this roadmap's control.

### 5.4 What stays in Phase 5

5.1 (final E2E copy/structure alignment, mobile-viewport project, affordance-visibility checks — which 4.5's new controls will then be part of), 5.2 (three green promotion dispatches, a11y sweep, light/dark/LTR/RTL sweep over the FINAL surface including the viewer), 5.3 (demo dry run — whose materials-walk segment naturally extends with "read the extracted text" and, if desired, a retry beat).

### 5.5 Decisions Seyam must make before implementation

| # | Decision | Recommendation |
| --- | --- | --- |
| D1 | Authorize Batch 4.5 as proposed in §7 (one batch, both surfaces)? | Yes — both contracts are landed, tested, and were already teed up by 4.3's note |
| D2 | The plan's W9 wording says "admin reprocess path"; the implemented + tested reality is **owner + instructor** (no admin enforcement exists anywhere). Confirm the UI follows the implementation (owner+instructor), not the plan's "admin" wording | Yes — code against the verified contract; the plan text is superseded by the implementation (the roadmap's own rule: never code against what the contract does not contain) |
| D3 | Should the reprocess control appear on `ready` rows as well as `failed` rows? (The backend supports both: re-run after pipeline improvements vs. retry after failure) | Yes, on both terminal states, with copy that distinguishes retry-after-failure from re-process; the owner may restrict to `failed` if he prefers the narrowest surface |
| D4 | Include a minimal, dated roadmap-DOCX reconciliation inside 4.5 (coverage-matrix rows C→A for the two capabilities; §9/§11 hub-slot fulfilment notes; the §22 retry-UI refinement note), or defer DOCX reconciliation to a later documentation pass? | Include it in 4.5 (the doc-closure/recon-audit precedent: in-place, dated, python-docx, integrity-verified) — but only on explicit authorization; the default without it is batch-note + ledger only, which is sufficient for execution |
| D5 | Confirm 4.5 runs **before** 5.1, so the suite aligns once over the final surface | Yes — same rework-prevention logic that ordered functional fixes before the redesign |

---

## 6. Proposed execution plan (Deliverable E — designed to become the authorized execution prompt)

### Batch 4.5 — Cross-team capability integration: materials lifecycle completion (extracted-text viewer + reprocess control)

**1 · Batch ID and title.** Batch 4.5 — Cross-Team Capability Integration: the materials lifecycle completion. One implementation batch, two named surfaces (A: extracted-text viewer; B: reprocess control).

**2 · User-facing objective.** On the course-detail hub, a `ready` material becomes readable — its owner opens the extracted text, page by page, inside the hub (including Arabic pages rendered correctly in either layout direction); and a terminal material (`failed` — or `ready`, per D3) becomes actionable — the owning instructor requests a reprocess inside the backend's retry budget and watches the honest status vocabulary carry it back through the pipeline. The materials walk gains its payoff step and loses its dead end.

**3 · Exact capabilities included.** Surface A: `GET /v1/materials/{id}/pages` (list, `limit`/`offset` pagination; the single-page endpoint `GET /v1/materials/{id}/pages/{n}` is available for lazy per-page loading if the implementation prefers it — either consumption is contract-honest; the list endpoint alone is sufficient at demo scale). Surface B: `POST /v1/materials/{id}/process`. Nothing else.

**4 · Why 4.5 and not Phase 5 or another batch.** Phase 5 is verification of the existing surface — it has no feature-implementation scope, and absorbing feature work there would blur Gate F's meaning. The two capabilities are the Week 9 frontend assignment and its companion, contract-landed since PR #81, already recorded as pending owner decisions in the 4.3 note §7; the roadmap's §12 alignment rule routes exactly this situation into "a proposed batch for Seyam's authorization." They must precede 5.1 so the test-suite alignment happens once over the final surface (D5).

**5 · Exact frontend files expected to change.**
*Confirmed:*
- `frontend/features/materials/schemas.ts` — add `materialPageResponseSchema`, `materialPagesResponseSchema` (Zod, mirroring the tracked contract); existing schemas byte-preserved.
- `frontend/features/materials/keys.ts` — add the `pages(materialId)` branch under `materialKeys.all`.
- `frontend/features/materials/flow.ts` — add the reprocess/viwer copy + error mapping (409 two-class, 429) and any pure pagination/label helpers.
- `frontend/features/materials/flow.test.ts` — the new pure-helper unit cases.
- `frontend/features/materials/api/useMaterials.ts` — add `materialPagesOptions(materialId)` (+ a `useMaterialPages` hook or equivalent) following the existing `queryOptions`/`me.isSuccess` pattern.
- `frontend/components/courses/CourseMaterials.tsx` — the `MaterialRow` action area (terminal rows): the reprocess control; the viewer disclosure + region.
- `frontend/stories/CourseMaterials.stories.tsx` — the new states (§10).
*Requires implementation-time verification (structural choice):*
- A new `frontend/components/courses/MaterialTextViewer.tsx` if the row component stays lean (recommended — mirrors the 4.3 module split); otherwise the viewer lives inside `CourseMaterials.tsx`.
- The batch note + this ledger (mandatory); the roadmap DOCX **only if D4 is authorized**.

**6 · API endpoints and tracked schemas to consume.** Exactly the three operations in §3.1, read from `docs/openapi.json` @ the verified starting commit (and cross-checked against `backend/app/schemas/material.py` at implementation time, as 4.3 did). `job_id` from the 202 is log-correlation only — logged once (`console.info`, identifiers only), **never queried** (the same rule as registration).

**7 · Role and authorization behavior.** Both surfaces render only within the population the hub already gates: the viewer affordance on `ready` rows (any hub visitor is by construction the course owner today — owner-scoped course read); the reprocess control only where `canManageCourse` (owner **and** instructor — the exact derivation the page already uses for Edit/Delete/upload). Presentation only — the backend's `require_owned_course` / `require_instructor` + `limit_writes` remain the boundary. No admin surface. No student visibility question arises (students cannot reach the hub).

**8 · Loading, empty, success, and error states.**
*Viewer:* lazy (loads when the disclosure opens, `status === "ready"` only) — LoadingBlock while fetching; honest empty (`pages: []` → "No extracted text stored for this material yet."; a page with empty `text` → "This page has no extractable text."); pages rendered as labeled blocks ("Page N") with `dir="auto"` text in a reading-measure column; ErrorState + retry on failure (the established mapping: 401 global recovery; 403/404 honest copy); pagination honest — if a page of results returns exactly `limit` entries, a "Load more pages" control advances `offset`; no fabricated totals.
*Reprocess:* control disabled + "Requesting…" while in flight (duplicate-submit protection); on 202 → invalidate the course's materials list and any cached pages for that material — the row returns to `pending` and the **existing** per-material status poll resumes automatically (no new polling machinery); acceptance copy mirrors the 4.3 rule ("Processing is queued — its status appears in the list."); on 409 → surface the backend's two documented classes honestly (already user-readable: already queued/processing; budget exhausted with "N of 3"); on 429 → "Too many requests — wait a moment and try again."; 401/403/404 via the existing `describeMaterialFlowError` conventions. No progress percentages, phase names, or ETAs anywhere.

**9 · Query/cache invalidation.** New key branch `materialKeys.pages(materialId)`; the viewer query keys there and is enabled only while open on a ready material. The reprocess mutation invalidates `materialKeys.list(courseId)` (existing key) and `materialKeys.pages(materialId)` (a re-run may change the text under the keep-more-pages rule). No other keys touched; no schema/key changes to existing queries.

**10 · Required tests.** Unit (vitest): schema round-trips for the two new response shapes; the 409 (both classes) / 429 mapping; page-label and pagination-helper cases; viewer empty-copy derivation. Storybook (axe fail-on-violation, the standing config): ready row with viewer open (multi-page, an Arabic page `dir="auto"`, an empty-text page), failed row with the reprocess control, in-flight state, the budget-exhausted 409 presentation, both directions via the direction toolbar. E2E: **no new spec** (the materials flow's instrument is the manual walkthrough per roadmap §24; the trio's pins are untouched — all existing accessible names are preserved verbatim); `playwright test --list` must still collect 10/10.

**11 · Manual verification requirements (owner stack).** The 4.3 walkthrough extended by two beats: after `ready`, open the viewer and read the extracted pages (English PDF + the Arabic decision-lock PDF — verifying `dir="auto"` and the Arabic font rail); observe or force a `failed` material (the scanned-PDF quota case), reprocess it, and watch 202 → pending → processing → ready; optionally exercise the budget-exhausted 409 after three manual retries. Light/dark and LTR/RTL spot checks on both surfaces.

**12 · Dependencies and blockers.** None for implementation. Runtime demonstration needs the owner's stack (API + worker + storage) — the same outstanding prerequisite as 4.3's walkthrough, recorded as such. Staging cannot serve these endpoints until the branches merge (owner/DevOps coordination; not a 4.5 dependency).

**13 · Must-not-change constraints.** The 4.3 upload flow and its presigned-POST contract; the polling discipline (5 s, terminal shutdown, unrecoverable-error shutdown, list-as-rendering-source); the dedup honesty; every existing Zod schema byte-for-byte; the hub's masthead/actions/regions and every E2E-pinned string; `notFound()` semantics; the auth flow and `apiFetch` boundary; onboarding, direction toggle, profile, dashboard, courses surfaces; no new dependencies of any kind; no new routes (the viewer is an in-hub disclosure, not a `/materials/[id]` page); backend code, `docs/openapi.json`, workflows, infra — untouched.

**14 · Definition of done.** The two surfaces render in the hub's Materials region on the existing design system, role-gated as specified, in both themes and both directions, axe-clean; the full local matrix is green (typecheck, lint, unit incl. the new cases, storybook incl. the new stories, build, `--list` 10/10); no existing pin or contract consumption changed; the batch note and ledger record the delivery (and the DOCX if D4 is authorized); the Week 9 frontend assignment is recorded as fulfilled in the ledger; the extended walkthrough is either completed on the owner's stack or recorded as outstanding with exact steps.

---

## 7. Investigation verification actually executed (this batch)

| Check | Result |
| --- | --- |
| Git state verification (status, branch, HEAD, fetch, rev-parse ×2, ancestry ×2, log ×2, merge-base) | **Done** — §1.1/§1.2; unexpected local state handled per the lifecycle (stale clone preserved untouched; fresh isolated clone at the verified tip) |
| Pre-existing-changes protection | **Verified byte-identical** — all 19 uncommitted 4.4 files match the owner's `5df5abd0`; nothing discarded or overwritten |
| Lifecycle rules, ledger (board + open questions + 4.1–4.4 entries), roadmap DOCX (python-docx extraction, 452 lines/35 tables), 44-week plan W9 section | **Read in full** |
| `docs/openapi.json` @ 5df5abd0 vs merge-base (parsed-JSON path/schema diff) | **Done** — §1.3 |
| Backend implementation reading (materials API, deps, service, models, worker page persistence, rate limit, observability) | **Done** — §3 |
| Backend test-suite reading (63 material-API tests incl. the 17 Week-9 endpoint tests; tasks; review hardening) | **Done** — not executed here (no runtime; CI wiring verified in ci.yml) |
| Frontend surface reading (apiFetch, features/materials module, CourseMaterials, hub page, stories/E2E inventory) | **Done** — §2 |
| Repository-wide searches (pages/process consumption, require_admin call sites, golden-set runner, OCR baseline, Sentry/alert wiring) | **Done** — §3.2/§4 |
| Documentation-only-batch verification (this note + ledger) | Readable, internally consistent, no claim of unperformed work, no out-of-scope file touched, DOCX untouched |

**Nothing was implemented. No commit, push, merge, rebase, reset, or clean was performed anywhere.**

---

## 8. Ledger status and the proposed update (Deliverable F)

The living ledger at `5df5abd0` records Batch 4.4 as EXECUTED with "next authorized batch = 5.1". This investigation appends: (a) a **Batch Status Board row 4.5 marked PROPOSED** (investigation delivered; implementation awaiting Seyam's authorization); (b) a dated investigation log entry recording the verified evidence, the proposed scope (§5/§6 above), and the decision list (§5.5) — explicitly **not** marking any 4.5 work complete or authorized, and **not** altering the standing "next roadmap batch = 5.1" statement, which changes only if and when Seyam authorizes 4.5.

**The proposed plan remains proposed. Nothing in this batch starts Batch 4.5 implementation, Phase 5, a merge, or any other work.**
