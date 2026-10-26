# OpenLearn-AI — Week 6 Plan

**Goal:** one working vertical path — PDF → Docling → targeted OCR → Canonical
Document → chunks → embeddings → pgvector → retrieval → RAG → answer + sources —
with PAL hardened along the way.

**Priorities:** MUST = core path, do not compromise. SHOULD = only if MUST is
stable. STRETCH = only if time allows; never destabilizes MUST.

**Checkpoint:** chunking (P8) working by **Wednesday EOD**, or SHOULD/STRETCH is cut.

| # | Phase | Priority | Depends on |
|---|-------|----------|------------|
| P0 | Baseline | MUST | — |
| P1 | Contract freeze | MUST | P0 |
| P2 | Models + exceptions | MUST | P1 |
| P3 | Interfaces + mocks | MUST | P2 |
| P4 | Factory + configuration | MUST | P3 |
| P5 | Router rewrite | MUST | P2 |
| P6 | Docling ingestion | MUST | P1 |
| P7 | Targeted OCR | MUST | P3, P6 |
| P8 | Chunking | MUST | P6 |
| P9 | Embeddings | MUST | P3, P8 |
| P10 | pgvector store | MUST | P3 |
| P11 | Retrieval + RAG | MUST | P9, P10 |
| P12 | OmniRoute reasoning | SHOULD | P11 |
| P13 | Streaming | SHOULD | P12 |
| P14 | WebSocket chat | SHOULD | P13 |
| P15 | Background ingestion | STRETCH | P8 |
| P16 | Integration tests | MUST | P11 |
| P17 | Final validation | MUST | all |

---

## P0 — Baseline (MUST)
- **Task:** record branch + commit; confirm recovered `backend/app/pal/` and
  `backend/tests/pal/`; run `PYTHONPATH=. uv run pytest tests/pal -q`.
- **Done:** tests pass; starting state recorded. Do not clean or reset the
  recovered PAL before this.

## P1 — Contract freeze (MUST)
- **Task:** finalize and review before implementing: `CanonicalDocument`, `Chunk`,
  `OCRResult`, `EmbeddingResult`, `VectorSearchResult`, `ReasoningResult`,
  `ReasoningChunk`; interface signatures (single + batch OCR/embedding,
  `reason`/`reason_stream`, vector CRUD incl. delete-by-document); `PALError`
  hierarchy.
- **Locked decisions:** `chunk_id = "{document_id}:{seq}"`;
  `Chunk.pages: list[int]`; `EmbeddingResult` validates
  `len(vector) == dimension`; caller-error exception is `InvalidInputError`
  (not `ValidationError`).
- **Done:** frozen contracts committed; no signature churn after this phase.

## P2 — PAL models + exceptions (MUST)
- **Task:** implement frozen models and exception hierarchy; add the embedding
  dimension model validator.
- **Done:** unit tests pass: dimension mismatch, invalid bounding boxes,
  out-of-range confidence are rejected.

## P3 — Interfaces + mocks (MUST)
- **Task:** implement OCR (single/batch), Embedding (single/batch), Reasoning
  (`reason`, `reason_stream`), VectorDB (upsert/search/get/delete); update all
  mocks; mock embedding dimension configurable (default 1024).
- **Done:** mocks satisfy contract tests for every interface.

## P4 — Factory + configuration (MUST)
- **Task:** add PAL settings (`AI_*_PROVIDER`, fallback chains, embedding
  model/dimension, `OMNIROUTE_API_BASE`, `OMNIROUTE_API_KEY`, local device,
  `OCR_MIN_TEXT_CHARS`); rewrite factory: Settings → validated provider instance;
  heavy providers constructed once and reused.
- **Done:** providers selectable via env with zero code changes; unknown provider
  fails at startup.

## P5 — Router rewrite (MUST)
- **Task:** ordered fallback; fallback only on `ProviderError`;
  `InvalidInputError`/`ConfigurationError` fail immediately; log every fallback
  (provider, error class) via structlog; streaming rule — fallback only before
  first chunk.
- **Done:** tests pass: primary success; fallback on provider error; no fallback
  on invalid input; all-fail raises; fallback log emitted.

## P6 — Docling ingestion (MUST)
- **Task:** PDF → Docling → `CanonicalDocument`. Test corpus: text PDF, scanned
  PDF, Arabic document if available, mixed content.
- **Done:** canonical output for the full corpus; structure and page mapping
  preserved.

## P7 — Targeted OCR (MUST)
- **Task:** implement `needs_ocr(page_text)` threshold check; OCR-eligible pages
  go through the PAL OCR provider; OCR text replaces page text, regions attached
  as metadata. Provider selected from ADR-0003 benchmark evidence; implement only
  what validates the scanned-PDF path. No coordinate alignment.
- **Done:** scanned corpus page yields OCR text; heuristic unit-tested.
  Limitation documented: garbage text layers may pass the threshold.

## P8 — Chunking (MUST)
- **Task:** Canonical Document → Chonkie (structure-aware). If Chonkie blocks the
  pipeline, use simple structure-aware chunking instead. Preserve `document_id`,
  `pages`, section/language when available.
- **Done:** chunks retain source metadata; re-chunking produces identical IDs.

## P9 — Embeddings (MUST)
- **Task:** batch-embed chunks via `embed_batch`; dev provider: local/free model
  (e.g., BGE-M3) behind config, lazy-loaded.
- **Done:** vectors match configured dimension (validated at the model); batch
  path works with mock plus a real-provider smoke test.

## P10 — pgvector store (MUST)
- **Task:** enable pgvector; implement upsert, search (`top_k`, filters), get,
  delete (incl. delete-by-document); HNSW cosine index; reject dimension mismatch.
- **Done:** store/retrieve round-trip works; metadata persists; deleting a
  document removes its vectors. May be implemented as an application store rather
  than a PAL adapter if simpler — contract unchanged.

## P11 — Retrieval + RAG (MUST)
- **Task:** RAG service: embed query → pgvector search (`top_k` configurable,
  default 5) → build context (score-ordered chunks with source identifiers) →
  call `ReasoningProvider` (**mock**) → return answer + sources.
- **Done:** end-to-end RAG works with mock reasoning; every answer cites
  `document_id`/page references traceable to chunks.

## P12 — OmniRoute reasoning (SHOULD)
- **Task:** OmniRoute adapter behind `ReasoningProvider`; map timeout/429/5xx to
  `ProviderTimeoutError`/`ProviderRateLimitError`/`ProviderServerError`;
  configurable model and base URL.
- **Done:** RAG answers use a free dev model; failures raise the correct
  `ProviderError` type. No paid APIs.

## P13 — Streaming (SHOULD)
- **Task:** implement `reason_stream` in mock + OmniRoute adapters; enforce the
  terminal-error rule after first chunk.
- **Done:** chunk stream observable; mid-stream failure surfaces once as an
  error — no second provider attempted.

## P14 — WebSocket chat (SHOULD)
- **Task:** chat WebSocket endpoint in the API layer; events:
  `retrieval_started`, `sources_found`, `reasoning_started`, `token`, `done`,
  `error`.
- **Done:** streamed answer + sources reach a minimal client; provider failure
  produces a single `error` event per protocol.

## P15 — Background ingestion (STRETCH)
- **Task:** job/status flow for document processing using existing worker
  infrastructure; synchronous ingestion remains acceptable.
- **Done:** long ingestion does not block HTTP; status queryable.
  **Skip if unstable.**

## P16 — Integration tests (MUST)
- **Task:** deterministic end-to-end test: PDF → canonical → chunks → embeddings
  (mock) → pgvector (test DB) → retrieval → mock reasoning → answer + sources.
  Streaming covered separately. Free external APIs: manual/integration only,
  never CI.
- **Done:** integration suite green with no network dependencies.

## P17 — Final validation (MUST)
- **Task:** run full `pytest` and `PYTHONPATH=. uv run pytest tests/pal -v`;
  verify:
  - [ ] no secrets committed or printed
  - [ ] no provider-specific imports outside PAL
  - [ ] PAL contains no RAG/WebSocket/orchestration code
  - [ ] fallback typed and logged; no mid-stream switching
  - [ ] embedding dimension validated at model and store
  - [ ] chunk IDs deterministic; source metadata survives to answers
  - [ ] document deletion removes vectors
- **Done:** checklist complete; failures fixed before week close.

---

## Scope rules

- A phase blocked more than half a day → adjust scope; do not add architecture.
- New dependencies only with an explicit need this week (Docling, Chonkie,
  pgvector, OmniRoute client, local embedding stack). Nothing else.
- Deferred work (reranking, extra providers, production pipelines) is out of scope
  regardless of progress — see ADR-0009 §7.