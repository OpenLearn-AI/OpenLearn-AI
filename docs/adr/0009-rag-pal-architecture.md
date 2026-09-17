# ADR-0009: PAL, Document Ingestion, and RAG Architecture

* **Status:** Accepted
* **Date:** 2026-09-16
* **Decision Owners:** Muhammad Seyam, OpenLearn-AI Team
* **Scope:** PAL hardening, document ingestion, initial RAG pipeline
* **Related:** `docs/weekly/week-06-plan.md`, ADR-0003 (OCR benchmark), ADR-0004 (pgvector)

## 1. Context

OpenLearn-AI needs a working document → RAG → streaming-chat path. A recovered PAL
skeleton (interfaces, mocks, factory, router) exists but is disconnected from
configuration, under-tested, and unsafe: the router catches all exceptions and falls
back on caller bugs, interfaces lack batch operations, and the vector-store contract
has no write/delete operations. This ADR fixes the target architecture and boundaries
for Week 6 and beyond.

## 2. Decision

**PAL is a provider abstraction layer and nothing else.** It owns capability
interfaces, normalized result models, provider adapters, typed errors, provider
configuration, provider construction, and ordered fallback.

| PAL owns | Application/services own |
|---|---|
| Interfaces: OCR, Embeddings, Reasoning, VectorDB | Document ingestion (Docling) |
| Normalized result models | OCR triggering decision |
| Provider adapters (mock, local, OmniRoute) | Canonical Document, chunking (Chonkie) |
| Exception hierarchy, factory, router | Retrieval + context construction (RAG service) |
| Provider configuration | WebSocket protocol, background jobs, auth, business logic |

```text
Application Services / Workers
        ↓
   PAL interfaces
        ↓
 Provider adapters
        ↓
Local / external providers
```

No plugin framework, provider marketplace, or dynamic discovery. Provider selection
is explicit configuration.

## 3. Architecture

### Pipeline

```text
PDF
 → Docling                  (primary parser)
 → targeted OCR             (only pages with insufficient text)
 → Canonical Document
 → Chonkie chunks           (structure-aware; simple fallback if it blocks)
 → Embeddings (batch)
 → PostgreSQL + pgvector
 → Retrieval (top_k, filters)
 → Context construction
 → Reasoning                (mock → OmniRoute dev gateway)
 → Answer + Sources
 → streamed to chat via WebSocket
```

### 3.1 Ingestion and OCR policy

Docling is the primary ingestion engine; OCR is a targeted fallback, never the
default path. Per page:

```python
if needs_ocr(page.text):        # len(text) < OCR_MIN_TEXT_CHARS (configurable)
    ocr = pal.ocr.extract_text(...)
    page.text = ocr.text        # OCR text replaces extracted text
    page.ocr = ocr.regions      # attach metadata when available
```

Preserve Docling's document structure; do not realign OCR coordinates.
Known limitation: a garbage but non-empty text layer passes the threshold.
Accepted for now — no OCR-quality detection system.

### 3.2 Canonical Document and chunks

Application-level Pydantic models (not PAL models):

- `CanonicalDocument`: `document_id`, `source`, `title`, `language` (from metadata
  or a simple deterministic heuristic), `pages` (`page_number`, `text`,
  structure/metadata, optional OCR metadata).
- `Chunk`: `chunk_id = "{document_id}:{sequence}"` (deterministic → idempotent
  re-ingestion), `document_id`, `pages: list[int]` (chunks may span pages),
  `text`, source metadata.

RAG never reduces retrieved content to bare strings; `chunk_id`, `document_id`,
and page references must survive into the answer's sources.

### 3.3 Storage and retrieval

v1 storage is **PostgreSQL + pgvector**. No other vector database.

- Contract: `upsert`, `search(vector, top_k, filters)`, `get`, `delete` — including
  deleting all vectors of a document (delete-by-document/filter, not only by ID).
- Cosine similarity; HNSW index with the cosine operator. If the implementation
  normalizes vectors, that policy is applied consistently in the embedding/store layer.
- The pgvector implementation may live as an application store rather than a PAL
  adapter if simpler this week; the contract stays the same.
- `top_k` is configurable (default ~5); no fixed range is frozen into the architecture.

The RAG service owns query embedding → search → context construction → reasoning
call → source preservation.

### 3.4 Providers and configuration

- Development uses local/free components and free APIs via **OmniRoute**. OmniRoute
  is a development gateway, not an architectural dependency; only its PAL adapter
  knows it exists.
- Reasoning: mock first (deterministic tests), OmniRoute adapter second.
- Embeddings: local/free model (e.g., BGE-M3) behind configuration; heavy local
  models are lazy-loaded and instantiated once.
- Configuration flows: env → Pydantic Settings → PAL config → factory → provider.
  Providers, fallback chains, model names, base URLs, keys, and device settings come
  from config. Secrets come from env vars only and never appear in logs, errors,
  tests, or commits.

### 3.5 Chat transport

WebSocket is an application transport for streamed reasoning. Protocol (complete
list): `retrieval_started`, `sources_found`, `reasoning_started`, `token`, `done`,
`error`. REST stays valid for non-streaming endpoints. PAL knows nothing about
WebSockets.

## 4. Key contracts

| Capability | Contract |
|---|---|
| OCR | `extract_text(source)`, `extract_text_batch(sources)` |
| Embeddings | `embed(text)`, `embed_batch(texts)`; explicit `dimension`; `EmbeddingResult` enforces `len(vector) == dimension` |
| Reasoning | `reason(messages, ...) -> ReasoningResult`; `reason_stream(messages, ...) -> AsyncIterator[ReasoningChunk]`; message-based input |
| ReasoningChunk | `text`; optional `finish_reason`; optional `usage` (may appear only on the final chunk) |
| VectorDB | `upsert`, `search(vector, top_k, filters)`, `get`, `delete` |

Mocks implement every contract; mock embedding dimension is configurable
(default 1024).

## 5. Failure and fallback behavior

Exception hierarchy (small, typed; no generic `ValidationError` — use
`InvalidInputError`):

```text
PALError
├── ProviderError
│   ├── ProviderUnavailableError
│   ├── ProviderTimeoutError
│   ├── ProviderRateLimitError
│   └── ProviderServerError
├── InvalidInputError
├── ConfigurationError
└── UnsupportedOperationError
```

Router rules:

1. Ordered fallback: primary → configured fallback chain. No load balancing,
   scoring, or dynamic discovery.
2. Fallback **only** on `ProviderError` (timeout, unavailability, rate limit, 5xx).
3. `InvalidInputError`, `ConfigurationError`, and programming errors fail
   immediately — no fallback, no masking.
4. Every fallback is logged via structlog: provider, error class, latency.
5. Streaming: fallback is allowed only **before the first chunk** is emitted.
   After the first chunk, a failure is terminal; the WebSocket layer reports
   `error`. No mid-stream provider switching.

No retry framework beyond this in Week 6.

## 6. Week 6 scope

Execution detail: `docs/weekly/week-06-plan.md`.

| Priority | Content |
|---|---|
| MUST | Hardened PAL (models, interfaces, exceptions, factory, router, config), Docling ingestion, targeted OCR, Canonical Document, chunking, embeddings, pgvector, retrieval, RAG with mock reasoning, source metadata end-to-end, tests |
| SHOULD | OmniRoute reasoning adapter, streaming, WebSocket chat |
| STRETCH | Background ingestion, deeper OCR integration, additional providers |

**Checkpoint:** if chunking is not working by Wednesday, cut SHOULD/STRETCH work
instead of the core path.

## 7. Deferred

Ranking/reranking and BGE reranker (later roadmap phase), speech/vision modalities,
additional vector databases, Kafka/event buses, distributed orchestration, plugin
systems, load balancing, agent frameworks, production-grade ingestion pipelines,
OCR coordinate alignment, language-detection infrastructure.

## 8. Consequences

**Positive.** Providers can be replaced without touching application code; OmniRoute
is disposable; RAG answers are traceable to document/page/chunk; streaming supports
interactive chat; pgvector avoids new infrastructure; failures are predictable and
logged.

**Costs.** PAL requires real implementation and testing effort; provider errors must
be normalized; changing the embedding model later requires explicit dimension
migration; canonical/chunk schemas need careful design. Accepted.