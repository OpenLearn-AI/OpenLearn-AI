# AI Week 7–8 — Living Progress Ledger

This file is the persistent execution ledger for every AI Week 7–8 batch on branch `ai-week7-8`. It is updated at the end of every batch with actual results — never with planned or aspirational content. Rules for updating it are defined in `docs/tasks/ai-week7-8/GLM-batch-n-patch-lifecycle-rules.md`; the batch plan it tracks is `docs/tasks/ai-week7-8/AI_WEEK_7_8_EXECUTION_ROADMAP.md`.

---

## 1. Project and Branch Context

| Item | Value |
|---|---|
| Repository | `https://github.com/OpenLearn-AI/OpenLearn-AI.git` |
| Branch | `ai-week7-8` (tracks `origin/ai-week7-8`) |
| Executor | Seyam (AI/ML Lead) — single executor for every AI/ML batch |
| Roadmap | `docs/tasks/ai-week7-8/AI_WEEK_7_8_EXECUTION_ROADMAP.md` |
| Lifecycle rules | `docs/tasks/ai-week7-8/GLM-batch-n-patch-lifecycle-rules.md` |
| Date of preparation | 2026-10-04 |
| Ledger status | **Initialized by the documentation-preparation task.** No engineering batch executed yet. |

## 2. Verified Starting Point

| Item | Verified value |
|---|---|
| Starting commit | `a16a6c56f8fda2145cee5ef2abe901e84504a4d6` — "added task docs" (2026-10-04) |
| Remote state at start | `origin/ai-week7-8` at the same SHA; local branch in sync and tracking |
| Starting working tree | Clean — no staged, unstaged, or untracked changes |
| Branch composition | `origin/staging` @ `b6852e5` + the commit adding the two superseded task documents |
| Superseded inputs | Root `WEEK-8-AI-POD-EXECUTION-ROADMAP (1).md` and root `GLM-batch-n-patch-lifecycle-rules.md` (both read in full, content preserved, removed by this task) |

### Verified baseline summary

* All Week 7 pipeline pieces exist and carry repository-level tests: Docling ingestion (`services/ingestion.py`), targeted-OCR decision/enrichment (`services/ocr.py`), single-page-PDF OCR source (`services/ocr_source.py`), structure-aware chunking (`documents/chunking.py`), BGE-M3 provider, pgvector provider + `vector_records` schema (migration `f3a1b7c9d4e2`), PAL router fallback/health.
* The Celery task lifecycle (atomic claiming, transitions, failure handling) is implemented and pinned by 11 tests in `backend/tests/test_material_tasks.py`.
* The content-processing seam raises `NotImplementedError` — the chain is **not composed**.
* Only a `mock` reasoning provider exists; no `litellm`/`openai` SDK in `backend/requirements.txt`.
* `backend/app/services/storage.py` has no fetch/download helper.
* The staging `celery_worker` compose service passes no AI provider environment (repository-level evidence that staging would run `mock` providers).
* CI runs two backend jobs: core tests (`tests --ignore=tests/pal --ignore=tests/documents`) and AI tests (`tests/pal tests/documents`), plus ruff and Alembic checks.
* Full fact base with evidence: roadmap Section 3.4 (facts F1–F21).

## 3. Current Phase and Batch

| Item | Value |
|---|---|
| Current phase | **Phase 0 — Baseline and decisions** (B0 executed 2026-10-04; B1 not started) |
| Next authorized batch | **B1 — Interface and technical decisions** (roadmap Section 8, B1) |
| Batch status | See Section 5 |
| Awaiting | Seyam's explicit instruction to start B1 |

## 4. Status Categories (Keep These Distinct)

* **Documentation preparation — COMPLETED** (this task): three canonical documents created under `docs/tasks/ai-week7-8/`; superseded root documents removed; single patch produced.
* **Engineering work — NOT STARTED**: no batch B0–B11 has been executed. Nothing in this ledger may be read as engineering progress.
* **Existing functionality verified in the repository** (code + tests read on the branch during this documentation task): the items in Section 2 and roadmap facts F1–F21.
* **Existing functionality NOT verified**: pytest suites were **not executed** during this documentation task (no backend dependency stack in the preparation environment). CI-green status is configuration evidence, not an observed run.
* **Runtime/staging behavior requiring future verification**: every staging claim — worker container imports, provider env injection (Q3), seeded-PDF end-to-end flow, OCR trigger behavior in the worker, PAL fallback/health inside the worker, gateway call with budget guard — is unverified and belongs to B5–B7 gates.

## 5. Batch Status

| Batch | Title | Status | Notes |
|---|---|---|---|
| B0 | Baseline ramp-up (run AI suites locally) | **COMPLETE** (2026-10-04) | AI-relevant suite green locally; batch record below |
| B1 | Interface and technical decisions | PENDING | Blocked by B0 |
| B2 | Pipeline stage 1 — ingest + targeted-OCR enrichment | PENDING | Blocked by B1 |
| B3 | Pipeline stage 2 — chunk → embed → persist | PENDING | Blocked by B1 (B2 first recommended) |
| B4 | LiteLLM reasoning provider + config + tests | PENDING | Blocked by B1(b) |
| B5 | Wire chain into Celery seam + storage fetch helper | PENDING | Blocked by B2, B3 (+H2) |
| B6 | Gateway-routed reasoning call + budget-guard evidence | PENDING | Blocked by B4 (+H1) |
| B7 | End-to-end verification and regression | PENDING | Blocked by B5, B6, H1 |
| B8 | Multi-PDF ingestion smoke | PENDING | Blocked by B7 |
| B9 | Chunk-quality review | PENDING | Blocked by B8 |
| B10 | Embedding configuration documented | PENDING | Blocked by B3 |
| B11 | Handoffs, demo readiness, release/tag support | PENDING | Blocked by B7, B9, B10 |

## 6. Completed Work

**Documentation preparation only (this task, 2026-10-04):**

* Cloned the repository, verified branch `ai-week7-8` and its remote tracking state at `a16a6c5`.
* Read both superseded input documents in full; re-verified their repository findings against the actual branch (backend tree unchanged since `7dccffa`; facts F1–F21 in the roadmap).
* Created `docs/tasks/ai-week7-8/AI_WEEK_7_8_EXECUTION_ROADMAP.md` (phases, batches, gates, contracts, risks, DoD).
* Created this ledger (`docs/tasks/ai-week7-8/progress.md`).
* Created `docs/tasks/ai-week7-8/GLM-batch-n-patch-lifecycle-rules.md` (task-adapted batch/patch lifecycle rules).
* Removed the two superseded root documents after confirming no repository references to them.
* Produced one self-contained patch containing exactly the changes above, validated against the starting baseline.

## 7. Pending Work

Every batch B0–B11 (Section 5), in the order and with the gates defined in the roadmap. Nothing has been pre-executed, pre-decided, or pre-verified beyond what Section 6 lists.

## 8. Blockers and Dependencies

* None active at preparation time. Engineering start awaits Seyam's explicit authorization of B0.
* Foreseeable external dependencies (not yet active): H1 (DevOps staging env — required from B5's staging acceptance onward; repository evidence in roadmap F16 shows the AI provider env is currently absent from `celery_worker`), H2 (Backend approval of the storage helper pattern — required before B5 lands the helper).

## 9. Known Risks and Unresolved Decisions

* Q1 image-material OCR scope — decided in B1(c); default proposal: PDF-only resolver, images deferred with a recorded note.
* Q2 reasoning adapter SDK — decided in B1(b); exactly one new dependency line.
* Q3 staging embedding provider — repo-level evidence the gap is real (F16); DevOps must inject `ai_embedding_provider=bge_m3` (+ key env) before any staging run; verified in B7 from worker logs.
* Q4 stale `ocr_tasks` route / missing `process_material` route-retry policy — DevOps finalizes with AI-supplied task name and transient-error list (H5).
* Q5 storage fetch helper pattern — Backend agrees before B5 lands it (H2).
* Risks R1–R5 (time limits vs pipeline latency, model cold-start scope, single-executor serialization, staging-env dependency, silent mock vectors) — roadmap Section 11.2.

## 10. Verification Evidence (This Documentation Task)

Executed and observed in the preparation environment (repository-level only):

* `git clone`, `git checkout ai-week7-8`, `git status`, `git branch --show-current`, `git rev-parse HEAD`, `git fetch origin && git status -sb`, `git rev-parse origin/ai-week7-8` — branch verified, in sync, clean tree.
* `git diff --name-status 7dccffa..HEAD` — backend untouched since the superseded document's evidence commit; only infra + the two task docs changed.
* Direct file reads and targeted greps establishing facts F1–F21 (roadmap Section 3.4), including: the seam's `NotImplementedError`, the 11 pinned tests, `storage.py`'s missing fetch helper, the reasoning factory's mock-only registration, `requirements.txt` without `litellm`/`openai`, config defaults (mock providers, 1200/150, 50-char OCR threshold, 1024-dim), CI job definitions, LiteLLM budget config, and the `celery_worker` compose environment block.
* `git grep` for references to both superseded filenames — none found outside the files themselves.
* Patch construction and validation against a pristine checkout of the starting commit — results recorded in the patch delivery note of this task's final report.

Not executed (and therefore not claimed anywhere):

* Any `pytest` run, `ruff` run, or Alembic run — the preparation environment has no backend dependency stack (no `sqlalchemy`, `docling`, or `sentence-transformers` importable).
* Any staging or runtime check of any kind.

## 11. Deviations from the Roadmap

* None yet — the roadmap itself is the baseline this ledger measures against.
* Standing note for future entries: the single-executor restructure (versus the superseded document's two-person plan) is a **mandated** input to this task, not a deviation; it is recorded in roadmap Sections 1.3 and 7.3.

## 12. The Exact Next Action

Execute **B1 — Interface and technical decisions** (roadmap Section 8, B1): record decisions (a)–(d) in `docs/tasks/ai-week7-8/decisions.md`, restate the enqueue contract unchanged, generate the batch patch per the lifecycle rules, and stop. B1 must not begin until Seyam explicitly authorizes it.

---

## 13. Batch Record Template (append one section per batch, below this line)

Every future batch appends a section here using exactly this template, filled with actual results only. Never fabricate historical entries, test results, commit identifiers, or staging verification. Do not modify earlier entries; corrections are appended as new dated notes.

```markdown
---
## Batch <ID> — <title> — <YYYY-MM-DD>

1. Batch identifier and objective: <ID; one line>
2. Starting commit and initial Git state: <SHA; branch, tracking, sync, clean/dirty + what pre-existing changes existed>
3. Changes actually made: <what was implemented/decided/verified, in concrete terms>
4. Files created / modified / deleted: <exact paths>
5. Tests and commands actually executed: <exact commands>
6. Passes / failures / checks not run: <counts and any failure verbatim; explicit list of anything not run + why>
7. Relevant output / verification evidence: <excerpts, log lines, SQL results, greps — enough to re-check the claim>
8. Deviations from the roadmap: <none, or exact deviation + reason>
9. Blockers / regressions / unresolved questions: <as observed>
10. Final state and next authorized batch: <HEAD SHA, tree state, gate status; the single next batch, or "awaiting instruction">
```

### Batch entries

---

## Batch B0 — Baseline ramp-up and local test verification — 2026-10-04

1. **Batch identifier and objective:** B0 — establish a personally verified baseline of the existing AI components and their tests before any implementation change; no production code touched.
2. **Starting commit and initial Git state:** `a9680d4c7ec98d1cb709edd49d2253d7b21ee56a` ("rewrote docs") on branch `ai-week7-8`, tracking `origin/ai-week7-8`, in sync (`git rev-list --left-right --count HEAD...@{u}` → `0 0`), working tree clean (fresh clone; no staged, unstaged, or untracked changes). This is the commit produced by applying the documentation-preparation patch on top of `a16a6c5`; the ledger's historical entries (Sections 2, 6, 10) refer to that earlier state and remain unchanged per the no-history-rewrite rule.
3. **Changes actually made:** verification only. (i) Every in-scope module and its test files were read in full (the seam facts below); (ii) the AI-relevant pytest set, the optional core suite, and lint were executed; (iii) no code, configuration, or dependency changes of any kind. Concise technical summary of the existing architecture (input to B1, not a decision):
   - **Task layer (implemented + integrated):** sync Celery task `process_material(material_id, s3_key, course_id, owner_id)` (name `app.workers.tasks.material_tasks.process_material`) wraps `asyncio.run`; each invocation builds a task-local async engine + session factory and disposes it in `finally` (loop-bound pools never survive the task). Atomic claim `claim_pending_material` = single conditional UPDATE `pending → processing`; duplicate deliveries become safe no-ops. Missing material → `None`; non-pending → current status returned unchanged. Claim success → `_process_material_content(material, s3_key, course_id, owner_id)` — **the seam (async) currently raises `NotImplementedError`**; any exception → rollback, re-fetch, transition to `failed`, commit, re-raise; success → transition to `ready` + commit. 11 pinned tests stub the seam via `monkeypatch.setattr(material_tasks, "_process_material_content", ...)` and pin the task name and delivery config (`acks_late` False, no `reject_on_worker_lost`, `publish_retry` True, soft 600 s / hard 660 s).
   - **Stage pieces (implemented, library-style, provider-injected — not yet composed):** `ingest_document(source) -> CanonicalDocument` is **synchronous** Docling conversion (PDF with `do_ocr=False`; deterministic `document_id` = file stem; page text = page-ordered join of `doc.texts` provenance; PARTIAL_SUCCESS preserved in metadata). `enrich_document_with_ocr(document, ocr_provider, page_source_resolver)` is **async**, sequential per page; gate `needs_ocr = len(page.text) < settings.ocr_min_text_chars` (default 50; exactly-at-threshold NOT OCR'd); eligible page → resolver → `provider.extract_text(source)` → text replaced + `ocr` metadata merged. `pdf_page_source_resolver(output_dir)` is **synchronous**, producing pypdfium2 single-page PDF artifacts `{stem}-page-{NNNN}.pdf` derived from `document.source` (so worker-side storage fetch must run first); **PDF-only** — non-PDF sources raise `UnsupportedDocumentTypeError` (Q1 evidence for B1(c)). `chunk_document(document, chunk_size, chunk_overlap)` is **synchronous** and deterministic (paragraph → sentence → whitespace hard-split, greedy packing, overlap carry; defaults 1200/150 from settings; `chunk_id = {document_id}:{seq}`; `char_count`/`page_count` metadata; no-text document → `[]`).
   - **PAL (implemented, tested offline):** frozen interfaces (embedding `dimension`/`embed`/`embed_batch`; OCR `extract_text[_batch]`; reasoning `reason`/`reason_stream`/`generate`; vector-db `upsert`/`search`/`get`/`delete`; all carry `health_check`). Factory registrations: OCR `mock`/`gemini`, embedding `mock`/`bge-m3(dimension)`, **reasoning `mock` only**, vector-db `mock`/`postgres(AsyncSession required)`. Router falls back **only on `ProviderError`** (config/input errors raise immediately); streaming falls back only before the first chunk; exhaustion → `ProviderServerError`. `BGEM3EmbeddingProvider` lazy-loads `SentenceTransformer` **per provider instance** behind a `threading.Lock` (B5 must confirm instantiation scope; per-task construction = per-task load), encodes via `asyncio.to_thread`, L2-normalized, fixed internal batch 16, output shape validated against the configured dimension → `ProviderServerError`. `GeminiOCRProvider` accepts **PDF bytes only** (enforces `.pdf` suffix + `%PDF-` header), maps 429 → `ProviderRateLimitError`, 401/403 → `ConfigurationError`, 5xx → `ProviderServerError`, blocking SDK via `asyncio.to_thread`. `PostgresVectorDBProvider` is session-backed, **never commits** (caller owns the transaction), upserts via multi-row `INSERT … ON CONFLICT (id) DO UPDATE` against the Core table (avoids the reserved `metadata` ORM-attribute crash), searches by cosine distance, filters by JSONB containment, and validates dimension against the `EMBEDDING_DIMENSION = 1024` constant that is **deliberately decoupled from `settings.ai_embedding_dimension`** (config drift surfaces as `InvalidInputError`, exactly as the architecture intends).
   - **Persistence:** `vector_records` (id TEXT PK, `VECTOR(1024)`, content, JSONB `metadata`, timestamps; no FK to domain models) — document/chunk provenance (`document_id`, `chunk_id`, pages, section, `char_count`) belongs in the JSONB payload per TS §12.1.
   - **Config/infra notes for B1:** every `ai_*_provider` defaults to `mock`; gateway settings today are legacy-named `omniroute_*` (B1(b) should pick consistent names for the new reasoning/gateway keys); `celery_app` requires `REDIS_PASSWORD` at import time (tests set it before import; no broker is contacted); the stale `app.workers.tasks.ocr_tasks.*` → `ocr_queue` route is still present and `process_material` has no dedicated route/retry policy (Q4); `storage.py` exposes only `generate_upload_url` — **no fetch/download helper exists**, so the worker currently cannot obtain the uploaded file (B5 + H2); the sync/async boundary (sync ingest/chunking vs async enrichment/providers inside the task's `asyncio.run`) is exactly the B1(a) decision surface.
4. **Files created / modified / deleted:** modified `docs/tasks/ai-week7-8/progress.md` only (this entry + Sections 3, 5, 12 status refresh). No other file touched.
5. **Tests and commands actually executed:** (working directory `backend/`; venv at `backend/.venv`, Python 3.12.14; `DATABASE_URL=postgresql+asyncpg://openlearn:ci_password@localhost:5432/openlearn_dev` exported for DB-backed tests, matching CI's DSN exactly)
   - `python -m pytest tests/documents tests/services/test_ocr.py tests/services/test_ocr_language_paths.py tests/services/test_ocr_source.py tests/pal tests/test_material_tasks.py -q` (required AI-relevant set)
   - same command with `-rs` (skip-reason diagnostic)
   - `python -m pytest tests --ignore=tests/pal --ignore=tests/documents -q` (optional core set; CI job 1 command)
   - `python -m ruff check .`
   - `python -m alembic upgrade head` (documented CI precondition for the DB-backed tests)
   - Diagnostic beyond the roadmap command (non-destructive, cleanup scoped to its own rows): `OPENLEARN_PG_TESTS=1 python -m pytest tests/pal/providers/vector_db/test_postgres_provider_integration.py -q`
6. **Passes / failures / checks not run:**
   - Required AI-relevant set: **210 passed, 2 skipped, 0 failed — exit 0** (9.89 s). Both skips are the opt-in real-PostgreSQL integration tests: "Real-PostgreSQL tests are opt-in: set OPENLEARN_PG_TESTS=1" (`test_postgres_provider_integration.py:65,137`).
   - Diagnostic opt-in integration run against the live pgvector DB: **2 passed — exit 0** (0.99 s).
   - Optional core set: **263 passed, 0 failed — exit 0** (17.17 s; one third-party `DeprecationWarning` from `starlette/testclient.py`, no test impact).
   - `ruff check .`: **All checks passed — exit 0**.
   - `alembic upgrade head`: **exit 0**, head `b110ae6051f4`.
   - Not run / not claimed: any staging or runtime verification (out of B0 scope); real model execution (the suites are offline by design — Docling's converter and BGE-M3's `SentenceTransformer` are faked in tests, so no model weights were downloaded or exercised); any Gemini/gateway network call; the Redis broker (tests exercise `_handle_material` directly and never contact it).
7. **Relevant output / verification evidence:** verbatim suite tails — AI set: `210 passed, 2 skipped in 9.89s` / `PYTEST_EXIT=0`; core set: `263 passed, 1 warning in 17.17s` / `CORE_EXIT=0`; ruff: `All checks passed!` / `RUFF_EXIT=0`; integration diagnostic: `2 passed in 0.99s`. Database: PostgreSQL **16.2** + pgvector **0.6.2** at `127.0.0.1:5432` (role `openlearn`, db `openlearn_dev` — CI-identical identity). Environment notes (recorded, not silent): (a) torch installed as the **CPU wheel variant** (`2.14.1+cpu`) because this sandbox has no GPU and limited disk; every other package version matches the `requirements.txt`/`requirements-dev.txt` pins exactly (docling 2.127.0, sentence-transformers 3.3.1, sqlalchemy 2.0.43, celery 5.6.3, fastapi 0.138.1, google-genai 1.24.0, pgvector 0.4.1, pytest 8.3.3, ruff 0.7.4); (b) no Docker and no root in this environment, so the CI `pgvector/pgvector` service container was substituted by an unprivileged bundled PostgreSQL 16.2 + pgvector 0.6.2 instance (pip package `pgserver` binaries) provisioned with CI's exact role/db/DSN; (c) the test suites are fully offline; no provider SDK network access occurred.
8. **Deviations from the roadmap:** none in scope or order — B0 executed exactly as specified (read + run + record; only `progress.md` modified). The two environment substitutions in item 7 are execution-environment facts, not scope deviations, and are recorded for transparency.
9. **Blockers / regressions / unresolved questions:** none. No test failure, no missing dependency, no regression observed. B0's evidence gives B1 one new input to weigh: the legacy `omniroute_*` gateway config-key naming already present in `config.py` when B1(b) names the new gateway/reasoning keys.
10. **Final state and next authorized batch:** HEAD unchanged at `a9680d4c7ec98d1cb709edd49d2253d7b21ee56a` (no commits made; the executor does not commit or push); working tree contains exactly one modification — `docs/tasks/ai-week7-8/progress.md`. Gate G1: B0 leg **passed** (AI-relevant suite green locally, summary recorded); B1 leg pending. Next authorized batch: **B1 — Interface and technical decisions**, awaiting Seyam's explicit instruction.
