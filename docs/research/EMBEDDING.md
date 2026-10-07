# Embedding Configuration — BGE-M3

**Status:** research documentation, current as of branch `ai-week7-8` @ `a0c1a98db272755c216d708d70bb22fd4119a0bc` ("ai-week7-8-batch-B9"; verified value-by-value during batch B10, 2026-10-07). Research documents inform decisions; they are not implementation authority (see `docs/research/README.md`). Binding contracts live in the ADRs, the Technical Specification, and the code itself. If this page and the code disagree, the code wins — fix this page or file the discrepancy; never document the aspiration.

## Purpose and role

OpenLearn-AI turns ingested course-material text into dense vectors for pgvector persistence. This page records what the embedding configuration **actually is right now** and how the worker reaches it — the embedding leg of the ingestion pipeline (Docling → targeted OCR → structure-aware chunking → **batch embeddings** → pgvector; ADR-0009). It mirrors the role of `docs/research/OCR.md` for this stage. No benchmarks, latency numbers, or retrieval-quality claims belong here.

## Current embedding configuration (summary)

| Setting | Current value | Source of truth |
|---|---|---|
| Provider (staging deployment) | `bge-m3` | `infra/docker-compose.staging.yml` (`celery_worker` env `AI_EMBEDDING_PROVIDER`) |
| Provider (application default) | `mock` | `backend/app/config.py` (`ai_embedding_provider`) |
| Model | `BAAI/bge-m3` — dense embeddings only (BGE-M3 sparse/ColBERT outputs unused) | `backend/app/config.py` (`ai_embedding_model`); `bge_m3_provider.py` module docstring |
| Dimension | 1024 | `config.py` (`ai_embedding_dimension`); `backend/app/models/vector_record.py` (`EMBEDDING_DIMENSION`) |
| Device (staging deployment) | `cpu` | staging compose `AI_EMBEDDING_DEVICE` |
| Device (application default) | `auto` | `config.py` (`ai_embedding_device`) |
| Pipeline batch size (chunks per `embed_batch` call) | 16 | `backend/app/services/document_pipeline.py` — `chunk_embed_and_persist(..., batch_size: int = 16)` keyword default |
| Provider encode batch size (texts per `SentenceTransformer.encode` call) | 16 — deliberately **not** configurable | `bge_m3_provider.py` — `_ENCODE_BATCH_SIZE` module constant |
| Normalization | L2-normalized at encode time | `bge_m3_provider.py` — `_encode_texts` passes `normalize_embeddings=True` |
| Runtime fallback | none (fallback config key exists but is unconsumed) | see "Provider selection and fallback" below |
| Vector storage | PostgreSQL + pgvector, `vector_records`, `VECTOR(1024)`, cosine | `backend/app/models/vector_record.py`; `backend/app/pal/providers/vector_db/postgres_provider.py` |
| Embedding stack | `sentence-transformers==3.3.1` (torch/transformers arrive via the `docling` dependency line) | `backend/requirements.txt` |

## Configuration keys

| Key (`backend/app/config.py`) | Application default | Staging deployment value (`infra/docker-compose.staging.yml`) | Consumed by |
|---|---|---|---|
| `ai_embedding_provider` | `mock` | `bge-m3` | `get_embedding_provider()` in `backend/app/pal/factory.py` |
| `ai_embedding_model` | `BAAI/bge-m3` | `BAAI/bge-m3` | `BGEM3EmbeddingProvider.__init__` (constructor default) |
| `ai_embedding_dimension` | `1024` | `1024` | factory (`dimension=` argument) → provider constructor and shape validation |
| `ai_embedding_device` | `auto` | `cpu` | `BGEM3EmbeddingProvider.__init__` (constructor default) |
| `ai_embedding_fallbacks` | `""` (empty) | not set | **nothing** — `embedding_fallback_list` property exists in `config.py` but has no consumer anywhere in application code |

**Application defaults vs staging deployment values.** Every `ai_*_provider` application default is `mock`, so tests and local development never require model weights or credentials. Staging overrides this at the deployment layer: the `celery_worker` container environment sets `AI_EMBEDDING_PROVIDER=bge-m3` and `AI_EMBEDDING_DEVICE=cpu`. Those staging values are deployment configuration, **not** universal application defaults. Runtime corroboration on record: the B7/B8 staging verifier WCONFIG rows observed `embedding=bge-m3 / 1024 / BAAI/bge-m3, device=cpu, vector=postgres` on the deployed worker (see `docs/tasks/ai-week7-8/progress.md`).

## BGE-M3 provider behavior

`backend/app/pal/providers/embedding/bge_m3_provider.py` — class `BGEM3EmbeddingProvider(EmbeddingInterface)` (`provider_name = "bge-m3"`), implementing the frozen `EmbeddingInterface` contract (`dimension` property; `embed(text)`; `embed_batch(texts)` → `EmbeddingResult`).

* **Lazy loading.** Module import, application import, provider construction, and `health_check()` never load the model. The first `embed`/`embed_batch` call loads `SentenceTransformer(model_name, device=...)` once per provider instance, cached behind a `threading.Lock`; `torch`/`sentence_transformers` are imported lazily inside the load path so application import stays cheap.
* **Async boundary.** `SentenceTransformer.encode` is blocking; both `embed` and `embed_batch` always execute it via `asyncio.to_thread` — never on the event loop thread.
* **Dense only.** The provider produces dense vectors; BGE-M3's sparse/ColBERT outputs, reranking, and retrieval are out of scope.
* **Normalization.** Embeddings are L2-normalized at encode time (`normalize_embeddings=True`; each `EmbeddingResult.metadata` records `"normalized": True`). Downstream cosine similarity therefore reduces to a dot product.
* **Shape validation.** After encode, the output must have shape `(len(texts), ai_embedding_dimension)` or the provider raises `ProviderServerError` — a wrong-dimensional model output is a provider failure, not caller input. `EmbeddingResult` independently enforces `len(vector) == dimension` (`backend/app/pal/models/types.py`).
* **Input validation.** Blank/empty text raises `InvalidInputError` without loading the model; `embed_batch([])` returns `[]` (empty-batch guard — no model load, no encode call).
* **Error mapping.** Model-hub timeout → `ProviderTimeoutError`; hub connection failure or CUDA OOM → `ProviderUnavailableError`; missing `sentence-transformers` install, invalid device value, or dimension < 1 → `ConfigurationError`. No new exception types, no broad `except Exception`.

## Batch / encode path

Two independent batching layers exist (both currently 16, by different mechanisms):

1. **Pipeline batching** — `chunk_embed_and_persist(..., batch_size: int = 16)` in `backend/app/services/document_pipeline.py` slices the chunk list into `batch_size`-sized slices and calls `await embedding_provider.embed_batch([chunk.text for chunk in batch])` once per slice, extending results in submission order (provider contract: one result per input, in input order). The 16 is a keyword default, not a config key, and the worker does not override it. A `batch_size < 1` raises `ValueError` before any work.
2. **Provider-internal encode batching** — `_ENCODE_BATCH_SIZE = 16` module constant in `bge_m3_provider.py`, passed as `model.encode(texts, batch_size=_ENCODE_BATCH_SIZE, show_progress_bar=False, normalize_embeddings=True, convert_to_numpy=True)`. It is **deliberately not configurable** (predictable memory on the 2 vCPU / 8 GiB staging host). There is **no** `ai_embedding_batch_size` config key — this is stated explicitly so nobody invents one.

Actual call path (real names):

```text
Celery task process_material                    (app/workers/tasks/material_tasks.py)
  └─ _process_material_content
       ├─ embedding_provider = get_embedding_provider()          (app/pal/factory.py)
       ├─ vector_db_provider = get_vector_db_provider(session=session)
       └─ chunk_embed_and_persist(document, material_id, ...)    (app/services/document_pipeline.py)
            ├─ chunk_document()                                  (app/documents/chunking.py, sync)
            ├─ per 16-chunk slice: embedding_provider.embed_batch(texts)
            │    └─ BGEM3EmbeddingProvider._encode_texts          (via asyncio.to_thread)
            │         └─ SentenceTransformer.encode(batch_size=16, normalize_embeddings=True)
            ├─ VectorRecord(id="{material_id}:{chunk.chunk_id}", vector, content, metadata)
            └─ vector_db_provider.upsert(records)                 (exactly once; never commits)
```

## Device behavior

* **Key and values.** `ai_embedding_device` (application default `auto`). Accepted values are enforced in the provider: `auto`, `cpu`, `cuda` (`_VALID_DEVICES`; the setting is `.strip().lower()`-normalized; anything else raises `ConfigurationError`).
* **Resolution** (`_resolve_device`). `cpu` → forced CPU. `cuda` → requires an actual CUDA device, otherwise `ProviderUnavailableError`. `auto` → CUDA when `torch.cuda.is_available()`, else CPU.
* **Explicit, not automatic.** Device selection is explicitly configured; only the `auto` mode performs automatic selection. Staging pins `cpu` (the AWS staging host has no CUDA GPU; CPU inference is always sufficient by design).
* **Plumbing.** The factory never passes a device: `get_embedding_provider()` constructs `BGEM3EmbeddingProvider(dimension=...)` and the provider reads `settings.ai_embedding_device` as its constructor default. The resolved concrete device is recorded in each result's metadata (`EmbeddingResult.metadata["device"]`).

## Provider selection and fallback

* **Factory-level, single-provider selection.** `get_embedding_provider(provider=None, dimension=None)` in `backend/app/pal/factory.py`: `"mock"` → `MockEmbeddingProvider(dimension=...)`; `"bge-m3"` → `BGEM3EmbeddingProvider(dimension=...)`; anything else → `ConfigurationError`. No fallback chain is constructed at runtime.
* **The generic `PALRouter` is not in the embedding path.** `backend/app/pal/router.py` implements ordered provider fallback (retry only on `ProviderError`; `InvalidInputError`/`ConfigurationError` raise immediately), but it is not instantiated anywhere in application code — embedding calls go factory → provider directly.
* **`ai_embedding_fallbacks` is currently inert.** The config key and its `embedding_fallback_list` property exist, but no application code consumes them; setting them has no effect today.
* **The mock provider is a selection, not a fallback.** `MockEmbeddingProvider` ("deterministic embedding provider for tests and local development", zero vectors, configurable dimension defaulting to 1024) runs only when `ai_embedding_provider=mock` or when a test injects it directly. It is never chosen automatically at runtime after a BGE-M3 failure.
* **No pipeline-level rescue either.** `chunk_embed_and_persist` implements no retry, fallback, error conversion, or exception swallowing — provider exceptions propagate unchanged to the Celery failure path (material → `failed`).

## Worker construction path (B5 wiring)

The Celery worker constructs the provider per task execution inside `_process_material_content` (`backend/app/workers/tasks/material_tasks.py`):

1. `embedding_provider = get_embedding_provider()` — called with no arguments.
2. The factory reads `settings.ai_embedding_provider` and `settings.ai_embedding_dimension`; for `bge-m3` it returns `BGEM3EmbeddingProvider(dimension=settings.ai_embedding_dimension)`. Model name and device are pulled from settings inside the provider constructor (the project's standard config-passing pattern, shared with the OCR provider).
3. The instance is injected into `chunk_embed_and_persist(...)` together with the session-backed vector provider; the pipeline stage never constructs providers itself and knows nothing about Celery or DB sessions.
4. **Instantiation scope.** Provider construction is per-task (a new provider instance each task run); the model itself is lazy-loaded once per provider instance on first use, behind the provider's lock. This per-task pattern is the recorded Week 7–8 assumption (decisions.md, BGE-M3 instantiation scope, verified at B5) — acceptable for current volumes; changing it is a decision item, not a tweak.

## Vector dimension / storage contract

* **Table.** `vector_records` (`backend/app/models/vector_record.py`): Text primary key; `embedding` column `Vector(EMBEDDING_DIMENSION)` with `EMBEDDING_DIMENSION = 1024`; JSONB `metadata` provenance (`material_id`, `document_id`, `chunk_id`, `pages`, `section`, `language`, `char_count`, `page_count` — built by `_vector_provenance` in `document_pipeline.py`, which invents nothing beyond existing chunk/document fields); cosine similarity (`score = 1 - cosine_distance` in the postgres provider).
* **Dimension is a fixed storage constant.** The column is `VECTOR(1024)` — deliberately decoupled from `settings.ai_embedding_dimension` so that a config drift surfaces as an explicit error (provider-side shape check; per-record `_validate_vector` in the postgres provider) instead of a silent database failure. The `ai_embedding_dimension` key and the storage constant currently agree at 1024.
* **Ids and idempotence.** Storage ids are `{material_id}:{chunk.chunk_id}`; the postgres provider upserts on id conflict (same-material re-ingestion is idempotent) and never commits — the caller's transaction (the worker's `AsyncSession`) owns the write.

## Source-of-truth / verification note

Every value on this page was checked against the code at `ai-week7-8` @ `a0c1a98` (2026-10-07): `backend/app/config.py`, `backend/app/pal/providers/embedding/bge_m3_provider.py`, `backend/app/pal/providers/embedding/mock_provider.py`, `backend/app/pal/interfaces/embedding.py`, `backend/app/pal/factory.py`, `backend/app/pal/router.py`, `backend/app/pal/models/types.py`, `backend/app/services/document_pipeline.py`, `backend/app/workers/tasks/material_tasks.py`, `backend/app/models/vector_record.py`, `backend/app/pal/providers/vector_db/postgres_provider.py`, `backend/requirements.txt`, and `infra/docker-compose.staging.yml`. Provider/factory behavior is pinned by the test suite (`backend/tests/pal/providers/embedding/test_bge_m3_provider.py` — 24 tests, including the device matrix, lazy loading, batch/normalization call contract, empty-batch guard, error mapping, and the factory mapping; `backend/tests/pal/test_factory.py` — mock default, explicit selection, unsupported-provider error). Runtime corroboration — evidence, not source of truth — comes from the B7/B8 staging verifier WCONFIG rows and B8 run `b8v1791400324` vector rows (1024-dim, norm 1.0) on deployed staging. Design context (not as-built authority): ADR-0009 and Technical Specification §8/§12.1.
