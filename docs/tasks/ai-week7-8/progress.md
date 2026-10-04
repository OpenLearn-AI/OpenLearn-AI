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
| Current phase | **Phase 0 — Baseline and decisions** (not started) |
| Next authorized batch | **B0 — Baseline ramp-up: run the existing AI test suite locally** |
| Batch status | See Section 5 |
| Awaiting | Seyam's explicit instruction to start B0 |

## 4. Status Categories (Keep These Distinct)

* **Documentation preparation — COMPLETED** (this task): three canonical documents created under `docs/tasks/ai-week7-8/`; superseded root documents removed; single patch produced.
* **Engineering work — NOT STARTED**: no batch B0–B11 has been executed. Nothing in this ledger may be read as engineering progress.
* **Existing functionality verified in the repository** (code + tests read on the branch during this documentation task): the items in Section 2 and roadmap facts F1–F21.
* **Existing functionality NOT verified**: pytest suites were **not executed** during this documentation task (no backend dependency stack in the preparation environment). CI-green status is configuration evidence, not an observed run.
* **Runtime/staging behavior requiring future verification**: every staging claim — worker container imports, provider env injection (Q3), seeded-PDF end-to-end flow, OCR trigger behavior in the worker, PAL fallback/health inside the worker, gateway call with budget guard — is unverified and belongs to B5–B7 gates.

## 5. Batch Status

| Batch | Title | Status | Notes |
|---|---|---|---|
| B0 | Baseline ramp-up (run AI suites locally) | **PENDING** | Next authorized batch |
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

Execute **B0 — Baseline ramp-up** (roadmap Section 8, B0) in an environment with the backend dependency stack installed: read the listed modules, run the AI-relevant pytest set, record the observed results in a new batch entry (Section 14 template), generate the batch patch per the lifecycle rules, and stop. B0 must not begin until Seyam explicitly authorizes it.

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

*(none yet — engineering batches have not started)*
