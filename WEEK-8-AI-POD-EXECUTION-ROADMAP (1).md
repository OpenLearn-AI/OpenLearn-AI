# Week 8 — AI Pod Execution Roadmap

Internal execution roadmap for the AI/ML pod (Pod B). Companion to the official Week 8 team email — it does not replace or extend it.

**Allocation principle:** both members own substantial production code. Seyam concentrates the architecture-sensitive integration and all cross-pod-facing verification; Bola ships independent modules behind contracts fixed at S1. Reviews are merge-gates on architectural compliance only — never a start-gate. Task ID note: IDs are kept from the previous revision where practical; `B5` was renumbered to `S6` because its owner changed, and the former single task `B1` was split into `B1` + `S5` along the pipeline's natural seam (the enriched `CanonicalDocument`).

## 1. Purpose and Baseline

| Item | Value |
|---|---|
| Target milestone | End of Week 8 — P1 close-out: integrated flow demoed, v0.2.0 tagged after the Friday demo |
| Branch inspected | `staging` |
| Commit SHA | `7dccffaf12c9d0aa0127f4d57a2ca5816b6a8035` (2026-10-01) |
| Working tree | Content identical to HEAD; mode-bit (`chmod`) diffs only — no content changes |
| Pod members | Seyam (AI/ML Lead), Bola (AI/ML Engineer; listed as "pula" in `members.txt`) |
| Evidence limits | Repository-level inspection + test-suite reading only. Deployed staging behavior was **not** executed from here; runtime claims below are marked "verify on staging". No commit or push was made. |

Scope rule: only work scheduled through Week 8, justified carryover that blocks a Week 8 deliverable, or concrete handoffs another pod consumes this week. Later-week features are excluded (Section 6).

## 2. Remaining-Work Summary

| # | Workstream | State | Evidence (repo @ 7dccffa) | Why required now |
|---|---|---|---|---|
| W1 | Worker-side ingestion chain (Docling → targeted OCR → chunking → BGE-M3 → pgvector) | **PARTIALLY IMPLEMENTED** — all pieces exist and are tested, but they are not composed; the Celery seam raises `NotImplementedError` | `app/workers/tasks/material_tasks.py` `_process_material_content` raises `NotImplementedError` ("AI/ML-owned pipeline contract"); pieces verified: `services/ingestion.py` (`ingest_document`), `services/ocr.py` (`needs_ocr`, `enrich_document_with_ocr`), `services/ocr_source.py` (`create_single_page_pdf`), `documents/chunking.py`, `pal/providers/embedding/bge_m3_provider.py` (`embed_batch`), `pal/providers/vector_db/postgres_provider.py` (`upsert`), `models/vector_record.py` + migration `f3a1b7c9d4e2` | W7 deliverable carried into W8; nothing reaches `ready`; blocks Backend integration tests, Frontend E2E, Friday demo, and the v0.2.0 tag |
| W2 | LiteLLM-backed PAL reasoning adapter | **MISSING** — only mock exists | `pal/providers/reasoning/` contains only `mock_provider.py`; `pal/factory.py` supports mock only; no `litellm`/`openai` SDK in `backend/requirements.txt`; no gateway URL config key | W7 carryover; one gateway-routed reasoning call with budget guard active is part of the W8 demo and DoD |
| W3 | Multi-PDF ingestion smoke | **NOT DONE** (blocked by W1) | Roadmap Week 8 "AI/ML & Data" bullet; no smoke runner or results in repo | Week 8 AI deliverable; feeds chunk-quality review |
| W4 | Chunk-quality review | **NOT DONE** (blocked by W3) | Roadmap Week 8 "AI/ML & Data" bullet; no review record in repo | Week 8 AI deliverable |
| W5 | Embedding configuration documented | **NOT DONE** | Roadmap Week 8 "AI/ML & Data" bullet; no embedding doc in `docs/` | Week 8 AI deliverable |
| W6 | PAL fallback + health checks inside the worker chain | **UNVERIFIED on runtime** — implemented at PAL level, not exercised in the worker | `pal/router.py` + `tests/pal/test_router.py`; no worker-run evidence | Verified as part of W1 integration (S2/S4), not a separate build task |
| W7 | Storage fetch for the worker | **MISSING helper** — `services/storage.py` has `generate_upload_url` only, no download/get | `grep "def " services/storage.py` | Minimal fetch helper needed so the worker can read the uploaded file (implemented under Backend review — Backend owns the module; ownership unchanged) |

Not pending (do not rebuild): Docling ingestion + `CanonicalDocument` (TS §11.3), structure-aware chunking (§11.4), targeted-OCR orchestration + single-page-PDF source extraction (§11.5), BGE-M3 and pgvector providers, `vector_records` schema, the Celery task status lifecycle with atomic claiming (`claim_pending_material`), `tests/test_material_tasks.py` (11 tests covering claim/failure/idempotency against a stubbed seam — must stay green).

## 3. Execution Plan

Priority: P0 = blocks the Week 8 demo/tag; P1 = Week 8 deliverable or demo input; P2 = Week 8 deliverable, low risk.

The chain splits at its natural technical boundary — the enriched `CanonicalDocument` — giving four independently implementable production units: B1 (ingest + OCR enrichment), S5 (chunk → vectors persistence), B2 (reasoning provider), and S2 (Celery seam wiring). Each has one implementation owner and a fixed interface from S1; nobody waits on the other's implementation to start.

### Stage 1 — Baseline and decisions (unblock everything)

| ID | B0 |
|---|---|
| Title | Ramp-up: run the existing AI test baseline locally |
| Owner / implementation | Bola — implements and reports personally. Priority P0 — no prerequisites |
| Current state | All chain pieces are implemented and tested, but Bola has not worked with them yet |
| Required action | Read `services/ingestion.py`, `services/ocr.py`, `services/ocr_source.py`, `documents/chunking.py`, `workers/tasks/material_tasks.py`, `pal/factory.py`, `pal/interfaces/reasoning.py`, `pal/providers/reasoning/mock_provider.py`, `models/vector_record.py`; run `pytest tests/documents tests/services/test_ocr.py tests/services/test_ocr_source.py tests/pal tests/test_material_tasks.py` locally |
| Deliverable | Half-page summary: what each piece does, its inputs/outputs, anything that looks off |
| Acceptance | All listed suites pass locally; summary delivered to Seyam |
| Verification | Seyam skims the summary (30 min) and confirms Bola can name the chain's seams |
| Review | Light check by Seyam; not a gate for Stage 2 |

| ID | S1 |
|---|---|
| Title | Interface and technical decisions (all Seyam) |
| Owner / implementation | Seyam — decision work, recorded in writing. Priority P0 — deadline: Tuesday 10 PM cross-pod sync |
| Current state | The seam docstring says "[AI/ML-owned]"; no agreed callable signatures; no SDK chosen for the gateway adapter; image-material OCR path undefined (`create_single_page_pdf` is PDF-only, `GeminiOCRProvider` contract is PDF bytes) |
| Required action | (a) Fix the two pipeline stage signatures and the seam callable contract: ingest+enrich stage (file path → enriched `CanonicalDocument`), persist stage (enriched document + injected embedding/vector providers → counts/result), and the content-processing callable (material fields + downloaded file path + injected providers), including sync/async boundary and error semantics (any exception → `failed` status, existing behavior preserved); (b) choose the reasoning adapter SDK (`litellm` SDK vs OpenAI-compatible client inside PAL, base URL `http://litellm:4000`, TS §23.1) and the one new dependency line; (c) decide W8 image-material scope: PDF-only OCR resolver now, images deferred with an explicit note — or in scope |
| Deliverable | Short decision note (PR description or `docs/` note) + the agreed signatures posted in the team channel |
| Acceptance | Bola can implement B1, B2, and the S5 test suite without asking further interface questions; Seyam can implement S5/S2 against the same signatures; Backend (Abanoub) informed — no change to the enqueue contract (`MATERIAL_PROCESSING_TASK_NAME` stays `app.workers.tasks.material_tasks.process_material`) |
| Verification | Decisions recorded in writing before Wednesday; no silent contract drift |
| Review/handoff | Seyam owns; consumers: Bola (B1, B2, S5 tests), Seyam (S5, S2), Abanoub (informed) |

**Stage gate:** S1 decisions posted + B0 suites green → proceed to Stage 2.

### Stage 2 — Bounded implementation (both members, parallel; reviews are merge-gates)

| ID | B1 |
|---|---|
| Title | Pipeline stage 1 — ingest + targeted-OCR enrichment |
| Implementation owner | **Bola** — Priority P0 — depends on S1(a)+(c); starts immediately after S1, no dependency on Seyam's code |
| Bounded scope (verified files) | New stage function in `app/services/document_pipeline.py` (module created; exact naming per S1): `ingest_document()` → page-source resolver wiring `create_single_page_pdf` (PDF sources only, per S1(c); non-PDF sources skip OCR gracefully with a metadata note) + `enrich_document_with_ocr()` → returns the enriched `CanonicalDocument`. Honors ADR-0009 rules: never pass `Page.text` to the provider, preserve Docling structure, OCR text replaces extracted text only below `ocr_min_text_chars`; deterministic temp-artifact handling |
| Contribution from other member | None — contract comes from S1 only |
| Deliverable | Stage function + unit tests (mock OCR provider, tmp-path PDFs: threshold fire/no-fire paths, multi-page, non-PDF path, temp cleanup) |
| Acceptance | New tests green; existing `tests/documents`, `tests/services/test_ocr*` untouched and green; no provider SDK imports (TS §7.3) |
| Verification | `pytest` locally; CI |
| Review | Seyam reviews once, before merge (ADR-0009 compliance) — not before work starts |

| ID | S5 |
|---|---|
| Title | Pipeline stage 2 — chunk → embed → persist |
| Implementation owner | **Seyam** — Priority P0 — depends on S1(a); starts immediately after S1 in parallel with B1 |
| Bounded scope (verified files) | Second stage function in `app/services/document_pipeline.py`: `chunk_document()` (settings defaults 1200/150) → `embed_batch()` loop (batching, empty-input guard) → build `VectorRecord` instances with provenance (`chunk_id`, `document_id`, page refs, `section`, `char_count` — TS §12.1) → vector provider `upsert()` → returns per-document counts/result. Providers injected; no session or Celery knowledge |
| Contribution from other member | **Bola owns this stage's unit test suite** (contract-first against the S1 signature, delivered by Wednesday midday): mock embedding + mock vector provider; cases: batching behavior, empty/no-text document, provenance shape and determinism of `chunk_id` |
| Deliverable | Stage function (Seyam) + its test suite (Bola); Seyam's implementation must satisfy Bola's suite |
| Acceptance | Test suite green; existing `tests/pal` providers tests untouched and green |
| Verification | `pytest` locally; CI |
| Review | No separate review gate — Bola's contract suite + CI are the acceptance mechanism |

| ID | B2 |
|---|---|
| Title | LiteLLM reasoning provider + config wiring + tests |
| Implementation owner | **Bola** — Priority P1 — depends on S1(b); starts immediately after S1, fully independent of the pipeline tasks |
| Bounded scope (verified files) | New provider `app/pal/providers/reasoning/` (per S1(b) SDK) implementing `ReasoningInterface` (`reason`, `reason_stream`), pointed at the gateway base URL from config; new config keys in `app/config.py` (provider name, base URL, model, key env var — follow existing `ai_*` naming); registration in `pal/factory.py` beside mock; its own unit tests with the client mocked (no network in tests) |
| Contribution from other member | None — mock provider and interface are the reference pattern |
| Deliverable | Provider + factory registration + config keys + tests |
| Acceptance | With `ai_reasoning_provider` set to the new value, `get_reasoning_provider()` returns it; tests green offline; no SDK import anywhere outside `backend/app/pal/` (TS §7.3) |
| Verification | `pytest tests/pal`; grep check for SDK imports |
| Review | Seyam reviews once, before merge (PAL boundary compliance) — not before work starts |

**Parallelism:** after S1, four work items run concurrently with no start-blocking: B1 (Bola), B2 (Bola), S5 implementation (Seyam), S5 test suite (Bola). The only cross-person coupling is S5's tests → S5 implementation, resolved contract-first via the S1 signature.

**Stage gate:** B1, B2, S5 implemented, tested, and merge-reviewed → proceed to Stage 3.

### Stage 3 — Integration (Seyam implements; interfaces already fixed)

| ID | S2 |
|---|---|
| Title | Wire the chain into the Celery seam + storage fetch |
| Implementation owner | **Seyam** — Priority P0 — depends on S1, B1, S5 (both stage functions reviewed), DevOps container (H1), Backend approval for the helper (H2) |
| Bounded scope (verified files) | `app/workers/tasks/material_tasks.py`: replace the `NotImplementedError` body of `_process_material_content` with the AI/ML-owned callable — fetch the uploaded file (new minimal helper in `services/storage.py`: s3_key → local file; Backend-owned module, Abanoub approves, ownership unchanged) → run B1's stage → run S5's stage with providers built via `pal/factory.py` (session-scoped pgvector provider) → return. Preserve the task lifecycle exactly: claim, transitions, failure → `failed` (11 existing tests in `tests/test_material_tasks.py` pin this behavior — Seyam updates the stubbed-seam tests in the same file himself) |
| Contribution from other member | None — this is the one tightly coupled unit; splitting it further would force mutual blocking |
| Deliverable | Wired seam + storage fetch helper + updated seam tests |
| Acceptance | On staging (verify with DevOps): one seeded PDF moves `pending → processing → ready`; `vector_records` row queryable with 1024-dim vectors and JSONB provenance; a forced failure marks the material `failed`; all 11 existing tests green |
| Verification | Staging run logs + SQL query on `vector_records`; `pytest tests/test_material_tasks.py` green |
| Review/handoff | Abanoub reviews the storage helper (module owner); output consumed by Backend (H3) and Frontend (H4) |

| ID | S3 |
|---|---|
| Title | First gateway-routed reasoning call + budget-guard evidence |
| Implementation owner | **Seyam** — Priority P1 — depends on B2 merge-reviewed + gateway env on staging (H1); can run as soon as B2 lands, in parallel with S2 |
| Bounded scope | Operational verification, no new code: route one test `reason()` call through `http://litellm:4000` on staging using B2's provider; confirm budget guard active ($10/30-day, `drop_params`) from gateway response/logs; confirm no provider SDK import outside `backend/app/pal/` |
| Deliverable | Call evidence (log excerpt) handed to DevOps for dashboards/Langfuse visibility (H5) |
| Acceptance | Call succeeds; guard behavior confirmed; import-rule grep clean |
| Verification | LiteLLM logs; `grep -r "openai\|litellm" backend/app --include="*.py"` shows PAL-only hits |
| Review/handoff | Evidence consumed by DevOps (Hisham) |

**Stage gate:** seeded PDF reaches `ready` on staging + gateway call succeeds → proceed to Stage 4.

### Stage 4 — Verification, smoke, and Week 8 AI deliverables

| ID | S4 |
|---|---|
| Title | End-to-end verification and regression |
| Implementation owner | **Seyam** — Priority P0 — depends on S2 + S3; Bola supports with B3's corpus results |
| Required action | Full backend suite green (incl. `tests/test_material_tasks.py`, `tests/pal`); one seeded-PDF staging run checked end-to-end: OCR loop fires only on pages below `ocr_min_text_chars` (log/metadata check), PAL fallback/health behave inside the worker (W6), mock-vs-real provider confirmed (staging must run `bge_m3`, not the config default `mock` — check worker logs/model metadata) |
| Deliverable | Short results note in the team channel: what passed, what failed, what is staging-only |
| Acceptance | Suites green; staging flow observable; any gap reported honestly, not papered over |
| Verification | CI + staging logs; Abanoub/Hisham acknowledge |

| ID | B3 |
|---|---|
| Title | Multi-PDF ingestion smoke (Week 8 deliverable, W3) |
| Implementation owner | **Bola** — Priority P1 — depends on S2 + DevOps container (H1); executes independently |
| Required action | Push 4–6 PDFs (born-digital + scanned; English + Arabic — the `experiments/OCR` custom corpus is a source of test files) through upload → worker on staging; record per-file: final status, chunk count, vector rows, whether OCR fired and on which pages |
| Deliverable | Results table posted to the team channel |
| Acceptance | All smoke PDFs reach `ready` (or failures explained); table complete |
| Verification | SQL counts on `vector_records`; worker logs; Seyam consumes results (no approval gate) |

| ID | B4 |
|---|---|
| Title | Chunk-quality review (Week 8 deliverable, W4) |
| Implementation owner | **Bola** — Priority P1 — depends on B3 |
| Required action | From B3's output: chunk `char_count`/`page_count` distributions; flag orphan (very small) and giant (over `chunk_size`) chunks; report anomalies |
| Deliverable | Review note with numbers; config-level fix proposal only if warranted (e.g. `chunk_size`/`chunk_overlap` values) — no new chunking algorithm |
| Acceptance | Review recorded; any proposed change approved by Seyam before implementation (genuine decision, not a formality) |
| Verification | Seyam decides on the proposal |

| ID | S6 |
|---|---|
| Title | Embedding configuration documented (Week 8 deliverable, W5) |
| Implementation owner | **Seyam** — Priority P2 — depends on S5 (he implements the embed path, so documents real values); can run during Stage 3 |
| Required action | One page at `docs/research/EMBEDDING.md` (mirrors `docs/research/OCR.md`): BGE-M3, 1024-dim, batch path and internal encode batch size, device config, provider/fallback config keys, how the worker constructs the provider |
| Deliverable | Doc merged by Thursday cutoff |
| Acceptance | Values match `config.py` and the S5/B2 code, not aspirations |
| Verification | **Bola spot-checks the values against the code** (he implemented B2's config keys and S5's test suite) — reviewer role inversion, no bottleneck |

**Stage gate:** S4 + B3 + B4 + S6 complete → Stage 5.

### Stage 5 — Deliver and demonstrate

- Seyam confirms handoffs H3–H5 are acknowledged by Abanoub, Ibrahim, Hisham.
- Friday: staging demo (register → login → create course → upload → `ready`, one gateway-routed reasoning call). DevOps cuts `v0.2.0` **after** a passing demo — the AI pod does not tag.
- Retro: carry only real, evidenced gaps into Week 9 — no silent scope creep.

### Rhythm (AI-pod-relevant checkpoints)

- **Daily async:** Bola posts B1/B2/S5-test progress; Seyam posts decision, S5/S2, and review status.
- **Tuesday 10 PM sync:** S1 decisions due; DevOps confirms container + env (H1); Backend informed of contract stability.
- **Wednesday midday:** Bola's S5 test suite delivered (Seyam reconciles his S5 implementation against it).
- **Thursday:** merge cutoff — all AI PRs (B1, B2, S5, S2, S6) in and merge-reviewed.
- **Friday:** staging demo + retro.

### Workload balance (evidence-based)

- **Implementation volume is roughly even.** Bola ships two production modules (LiteLLM reasoning provider; ingest+OCR enrichment stage) plus their tests and the S5 contract-test suite. Seyam ships two production units (chunk→vectors persistence stage; Celery seam wiring + storage fetch helper) plus the seam-test updates and the S6 doc. Estimated focused effort: ~4–5 days each — approximately even, not an exact 50/50 claim.
- **Risk is deliberately asymmetric.** Seyam holds the highest-risk unit (S2: async boundary, DB session scoping, 11 pinned lifecycle tests, a Backend-owned file) and all three technical decisions, consistent with lead accountability. Bola's units are lower-risk but genuine feature work behind S1-fixed interfaces — matched to his current familiarity without being trivialized.
- **Reviews are not bottlenecks.** Exactly three reviews exist, each architecturally necessary: Seyam on B1 (ADR-0009) and B2 (PAL boundary), Abanoub on the storage helper (module ownership). Bola's S5 test suite is itself S5's acceptance gate; Bola reviews S6; B3/B4 need no approval to be consumed.

## 4. Dependencies and Handoffs

Format: Provider → Consumer: required output → what it unblocks → verification condition.

| ID | Handoff |
|---|---|
| H1 | DevOps (Hisham) → AI/ML: `celery_worker` container importing all PAL providers cleanly + staging env for AI providers and gateway (base URL/key; `ai_embedding_provider` must be `bge_m3`, not the `mock` default) → unblocks S2/S3/S4/B3 → verify: `celery -A app.workers.celery_app worker` starts clean; BGE-M3 `health_check()` passes in worker; gateway reachable from the backend network |
| H2 | Backend (Abanoub) → AI/ML: review/approval of the minimal `storage.py` fetch helper implemented by Seyam (Backend owns the module; enqueue contract already landed and stable — task name `app.workers.tasks.material_tasks.process_material`, args `(material_id, s3_key, course_id, owner_id)`) → unblocks S2 → verify: helper returns a readable local file for a staged `s3_key` |
| H3 | AI/ML (Seyam) → Backend (Abanoub): implemented seam — no `NotImplementedError` → unblocks Backend's auth→course→material integration tests → verify: `pytest` integration suite green; seeded PDF reaches `ready` |
| H4 | AI/ML (Seyam) → Frontend (Ibrahim): a material that actually reaches `ready` on staging → unblocks upload/status E2E and the Friday demo → verify: `GET /materials/{id}/status` returns `ready`; `vector_records` row queryable |
| H5 | AI/ML (Seyam) → DevOps (Hisham): gateway test-call evidence for dashboards/Langfuse visibility + task name and transient-error list for routes/retry config → unblocks queue visibility and Celery route/retry finalization → verify: LiteLLM logs show the routed call; route config matches the task name |

## 5. Verification and Definition of Done (AI pod, Week 8)

Checks (in order):

1. `pytest tests/documents tests/services/test_ocr.py tests/services/test_ocr_source.py tests/pal tests/test_material_tasks.py` — green locally and in CI.
2. Seeded PDF on staging: `pending → processing → ready`; `vector_records` row with 1024-dim vector + JSONB provenance queryable.
3. OCR trigger check: pages below `ocr_min_text_chars` OCR'd; pages above untouched (log/metadata evidence).
4. Provider check: worker logs show BGE-M3 (not mock) on staging.
5. One reasoning call routed via the gateway with budget guard active; no provider SDK import outside `backend/app/pal/` (grep + review).
6. Multi-PDF smoke table recorded; chunk-quality review recorded; embedding config doc merged.
7. Handoffs H3–H5 delivered and acknowledged.

DoD statements:

- All mandatory AI-pod work scheduled through Week 8 (plus justified W7 carryover W1/W2) is accounted for in Sections 2–4, with an implementation owner and acceptance criteria each.
- Justified previous-week blockers (W1, W2) are resolved — or explicitly escalated with impact documented in the team channel.
- Interfaces and handoffs H1–H5 are agreed, with verification conditions met or exceptions escalated.
- Test results are reported as actually observed; integration is verified to the extent the staging environment allows.
- Known gaps and staging-only limitations are stated explicitly (Section 6); a green local test run is never claimed as staging health.
- No later-week feature or unnecessary architecture has been pulled in (Section 6).

## 6. Out of Scope and Unresolved Questions

Out of scope (later weeks or explicitly excluded — do not start):

- Reprocess endpoint / admin status surface, idempotent-processing hardening (W9); golden 20-PDF benchmark and measured OCR/embedding baselines (W9, ADR-0003 methodology).
- Retrieval/search endpoints (W10), hybrid retrieval + re-ranking (W13), RAG/chat (W14), WebSocket status channel (W15), Knowledge Graph (W21+).
- Local LLM runtime; local OCR engines beyond `experiments/` (ADR-0003); metadata enrichment (TS §11.6); quiz/recommendation/adaptive features.
- New abstractions beyond the single pipeline module; new client libraries beyond the one S1(b) dependency; refactors of working components.

Unresolved questions (owner → smallest resolving action — do not guess):

| # | Question | Owner / when |
|---|---|---|
| Q1 | Image-material OCR path (provider contract is PDF bytes; `create_single_page_pdf` is PDF-only) | Seyam, S1(c), Tuesday — default proposal: PDF-only resolver in W8, images deferred with a recorded note |
| Q2 | Reasoning adapter SDK choice (no `litellm`/`openai` SDK currently in `backend/requirements.txt`) | Seyam, S1(b), Tuesday |
| Q3 | Does staging actually set `ai_embedding_provider=bge_m3`? Config default is `mock` — silent mock vectors would invalidate the demo | Seyam + Hisham, confirm before S2's staging run |
| Q4 | `celery_app.py` routes `app.workers.tasks.ocr_tasks.*` to `ocr_queue`, but no `ocr_tasks` module exists (stale config); `process_material` has no route/retry policy | Hisham during routes/retry config (H5); AI pod supplies task name + transient-error list |
| Q5 | Preferred pattern for the `storage.py` fetch helper (Backend-owned module; Seyam implements, Abanoub approves) | Abanoub, before S2 starts |

## 7. Source Mapping

Authoritative documents (section numbers verified against the repo files):

- `planning/Roadmap/44-WEEK-EXECUTION-PLAN .md` — "Week 7 — Async Pipeline Wiring + LLM Gateway Traffic" (AI/ML & Data bullets: worker-side ingestion chain TS §11.7, targeted-OCR loop per ADR-0009, PAL fallback/health checks; Deliverables: seeded PDF end-to-end, gateway test call); "Week 8 — Integration Close-Out + v0.2" (AI/ML & Data bullets: multi-PDF ingestion smoke, chunk-quality review, embedding configuration documented; Deliverables; Definition of Done).
- `docs/design/OpenLearn_AI_v4_Technical_Specification.md` — §6.1 (gateway budget/callbacks), §7.3 (no provider SDK outside PAL), §8.1 (provider status; reasoning mock-only), §8.3 (provider fallback + health checks), §10.1 (budget guard), §11.3 (CanonicalDocument, deterministic IDs), §11.4 (structure-aware chunking, 1200/150 defaults), §11.5 (targeted OCR, `OCR_MIN_TEXT_CHARS`, Gemini provider contract), §11.7 (worker-side processing chain), §12.1 (pgvector records, JSONB provenance), §23.1 (staging services, gateway endpoint `http://litellm:4000`, Celery config).
- ADRs: ADR-0003 (OCR benchmark location — local engines stay in `experiments/`), ADR-0005 (LiteLLM gateway), ADR-0009 (PAL, ingestion, targeted-OCR policy).
- Historical assignments: `week7.txt` (AI/ML pod tasks carried here), `week6tasks.txt` (pipeline pieces finalized behind PAL), `members.txt` (pod roles; "pula" ↔ Bola identity note in Section 1).

Code evidence (all @ `7dccffa`, paths relative to repo root):

- `backend/app/workers/tasks/material_tasks.py` (lifecycle + seam `NotImplementedError`), `backend/app/workers/publishing.py` (task name), `backend/app/workers/celery_app.py` (routes/beat)
- `backend/app/services/ingestion.py`, `services/ocr.py`, `services/ocr_source.py`, `services/storage.py`
- `backend/app/documents/chunking.py`, `backend/app/models/vector_record.py`, `backend/alembic/versions/f3a1b7c9d4e2_add_vector_records_table.py`
- `backend/app/pal/factory.py`, `pal/interfaces/reasoning.py`, `pal/interfaces/ocr.py`, `pal/providers/reasoning/mock_provider.py`, `pal/providers/embedding/bge_m3_provider.py`, `pal/providers/vector_db/postgres_provider.py`
- `backend/app/config.py` (`ai_*` keys, `ocr_min_text_chars=50`, embedding defaults), `backend/requirements.txt` (no litellm/openai SDK)
- `backend/tests/test_material_tasks.py` (11 seam tests), `tests/documents/`, `tests/services/test_ocr*.py`, `tests/pal/`
- `infra/litellm-config.yaml` (models, $10/30d budget, `drop_params`, Langfuse callback), `infra/docker-compose.staging.yml` (`celery_worker`), `infra/grafana/` (Loki datasource only)
