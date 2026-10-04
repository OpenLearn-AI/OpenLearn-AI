# B1 — Interface and Technical Decisions (AI Week 7–8)

* **Status:** Recorded (2026-10-05) — decision batch, no production code.
* **Baseline:** branch `ai-week7-8` @ `9f7f55046444f0aa8ca95db02dc8a8a3a5894630` ("ai-week7-8-batch-B0.patch").
* **Author:** Seyam (AI/ML Lead), executed as batch B1 per `AI_WEEK_7_8_EXECUTION_ROADMAP.md` Section 8, B1.
* **Purpose:** fix, in writing, the pipeline contracts and scope decisions that B2–B5 implement. Every decision below is labeled:
  * **[Authority]** — established by an ADR / the Technical Specification / the 44-week plan / existing implementation contracts.
  * **[Chosen]** — chosen design where authority does not prescribe an answer (simplest complete solution; reasoning recorded).
  * **[Future]** — planned extension, explicitly not built now.
  * **[Out of scope]** — excluded from Week 7–8 (roadmap Section 11.3).

---

## 1. Authority and evidence

Authority hierarchy per ADR-0002 and `docs/README.md`: ADRs → README → Technical Specification → 44-week execution plan → research. This roadmap and `progress.md` are task documents and never override the above. Sources inspected in full for this batch:

| Source | Constraints it establishes for B1 |
|---|---|
| **ADR-0005** (LiteLLM gateway) | LiteLLM proxy is *the* LLM gateway and the implementation of the PAL `ReasoningInterface`. Applications call PAL interfaces, never provider SDKs. Provider credentials, routing, retries, key rotation, and cost tracking are configured at the **gateway and deployment layer**. Production providers: OpenAI, Anthropic, GLM through LiteLLM. Proxy port 4000. |
| **ADR-0009** (PAL / ingestion / OCR / RAG) | PAL is a provider abstraction layer and nothing else; no plugin framework, marketplace, or dynamic discovery. Pipeline: Docling → targeted OCR → CanonicalDocument → chunks → batch embeddings → pgvector. OCR is a per-page fallback (`len(text) < OCR_MIN_TEXT_CHARS`); OCR text replaces extracted text; Docling structure preserved. Config flow: env → Pydantic Settings → PAL config → factory → provider; secrets from env vars only, never in logs/errors/tests/commits. Chunk `chunk_id`/`document_id`/page provenance must survive end-to-end. Heavy local models lazy-loaded, instantiated once. §3.4 names OmniRoute as a development gateway, "not an architectural dependency" (see §3.7 below for the recorded resolution). |
| **ADR-0004** (pgvector) | v1 vector store = pgvector in the project PostgreSQL; vector access stays behind the PAL `VectorDBInterface`. |
| **ADR-0002** (documentation authority) | Hierarchy above; contradictions are recorded, never silently resolved. |
| **ADR-0003** (OCR benchmark location) | Local OCR engines live in `experiments/` only; a winning engine would be *reimplemented* in the backend after benchmarking — no local-OCR expansion now. |
| **ADR-0001** (modular monolith) | One FastAPI process; in-process interface calls; no message buses, orchestration frameworks, or network boundaries between domains. |
| **TS §6.1, §7.2–7.3** | As-built staging: `backend` service env carries `LITELLM_API_BASE=http://litellm:4000`; `litellm` service holds master+salt keys via env. Reasoning target = LiteLLM-backed PAL adapter. PAL boundary is enforced: no provider SDK imported outside `backend/app/pal/`. |
| **TS §8.1–8.4** | PAL interfaces and factory config flow; router fallback only on `ProviderError`; streaming fallback only before the first chunk. Reasoning provider today: mock only. |
| **TS §10.1, §10.3** | Reasoning via gateway: `gpt-4o-mini` default, `gpt-3.5-turbo` fallback, master-key auth, $10/30-day budget; chunking defaults 1200/150; OCR Gemini `gemini-2.5-flash` keyed by `GEMINI_API_KEY`. |
| **TS §11.2–11.5, §11.7** | Enabled ingestion formats: PDF, DOCX, HTML, Markdown, images. `document_id` is deterministic from the source file stem. Chunk `chunk_id = {document_id}:{seq}`. Gemini provider contract: local PDF path → bytes (`%PDF-` validated) → `OCRResult`; sequential batch. Target worker pipeline §11.7. |
| **TS §12.1** | `vector_records`: text PK, `VECTOR(1024)` fixed (not read from settings — drift must surface as error), JSONB `metadata` carries document/chunk provenance; postgres provider is session-backed (caller passes `AsyncSession`); cosine similarity. |
| **TS §23.1–23.3** | Staging topology and env; mode selection happens through PAL provider configuration, not separate service topologies. |
| **44-week plan W7/W8** | Worker-side ingestion chain is AI/ML (Pod B) work; DoD: material `ready` with chunks+vectors, gateway call with budget guard, no provider library outside PAL. Cross-pod table: "Celery task chain D (infra) → B (tasks) → A (API status)"; "Reasoning via LiteLLM B → D, W14". No pod is assigned a worker-side storage fetch anywhere in the plan. |
| **Code (branch @ 9f7f550)** | Seam `_process_material_content` raises `NotImplementedError` (`material_tasks.py:174`); 11 pinned lifecycle tests stub it via monkeypatch; `claim_pending_material` commits the claim before returning; `transition_material_status` flushes, caller commits; `ingest_document`/`chunk_document` synchronous, `enrich_document_with_ocr` async; `pdf_page_source_resolver`/`create_single_page_pdf` PDF-only (suffix check, `UnsupportedDocumentTypeError`); `GeminiOCRProvider` accepts PDF bytes only and reads `settings.gemini_api_key`/`settings.ai_ocr_model` as constructor defaults (the project's credential-passing pattern); `PostgresVectorDBProvider` session-backed, never commits; `BGEM3EmbeddingProvider` lazy-loads the model per provider instance behind a lock; `storage.py` = `_s3_client()` + `generate_upload_url` only (boto3, sync, SigV4); factory builds providers from `settings.ai_*`; `config.py` `ai_*` naming + unused legacy `omniroute_api_base`/`omniroute_api_key` (no consumer anywhere — verified by repo-wide grep); `infra/litellm-config.yaml` resolves provider keys via `os.environ/OPENAI_API_KEY` inside the gateway container, `master_key: os.environ/LITELLM_MASTER_KEY`, `default_model: gpt-4o-mini`, budget $10/30d, `drop_params: true`; staging compose: `backend` has `LITELLM_API_BASE`, `celery_worker` has full S3 env but **no** AI/gateway env (roadmap F16), `litellm` env passes only master+salt keys. |

---

## 2. Pipeline contract (Decision A)

**Module shape (Decision D of the roadmap, recorded here):** one module `backend/app/services/document_pipeline.py` containing the two stage functions and one result model. No pipeline class hierarchy, no registry, no orchestration framework, no plugin system **[Authority: ADR-0009 "no plugin framework", ADR-0001, roadmap §11.3]**. The stage module imports application modules and PAL *interfaces* only; it never imports a provider SDK **[Authority: TS §7.3, ADR-0009]**.

### 2.1 Stage 1 — ingest + targeted-OCR enrichment

```python
async def ingest_and_enrich(
    source_path: str | Path,
    *,
    ocr_provider: OCRInterface,
    page_source_resolver: PageSourceResolver | None = None,
) -> CanonicalDocument
```

* Calls the existing synchronous `ingest_document(source_path)` directly, then awaits the existing `enrich_document_with_ocr(document, ocr_provider, resolver)` **[Authority: modules exist unchanged; roadmap B2]**.
* If `page_source_resolver` is `None` **and** the source is a PDF (`.pdf` suffix of the local path — the same rule `create_single_page_pdf` and `GeminiOCRProvider` already enforce), the stage wires the default `pdf_page_source_resolver()` itself; artifacts are written next to the source file **[Chosen: simplest composition that still lets tests inject fakes; roadmap B2 wires the resolver inside the stage]**. If an explicit resolver is passed, it is used verbatim.
* Non-PDF sources skip OCR entirely (Decision C, §4): no resolver call, no provider call, a metadata note is added **[Chosen per roadmap B1(c) default]**.
* Output: the enriched `CanonicalDocument` (same object; OCR text replaces page text below the threshold; `ocr` metadata merged) **[Authority: `services/ocr.py` contract]**.

### 2.2 Stage 2 — chunk → embed → persist

```python
class PersistResult(BaseModel):
    material_id: str
    document_id: str
    chunk_count: int          # chunks produced by chunk_document
    embedded_count: int       # chunks actually embedded
    upserted_count: int       # vector records handed to the provider
    vector_ids: list[str]
    skipped: bool = False     # True when the document produced no chunks (no-op)

async def chunk_embed_and_persist(
    document: CanonicalDocument,
    *,
    material_id: str,
    embedding_provider: EmbeddingInterface,
    vector_db_provider: VectorDBInterface,
    chunk_size: int | None = None,      # None → settings.chunk_size (1200)
    chunk_overlap: int | None = None,   # None → settings.chunk_overlap (150)
    batch_size: int = 16,
) -> PersistResult
```

* Sequence: `chunk_document(document, chunk_size, chunk_overlap)` → empty-input guard (no usable text → `PersistResult(skipped=True)` with zero counts and **no** provider calls) → loop `embed_batch(texts)` in `batch_size` batches → build `VectorRecord` rows → single `vector_db_provider.upsert(records)` **[Authority: roadmap B3; `chunking.py` deterministic contract]**.
* **Vector-record identity [Chosen]:** `VectorRecord.id = f"{material_id}:{chunk_id}"`. Reasoning: `document_id` is the file stem (TS §11.3) and is **not** globally unique — two materials uploading the same filename would collide on `chunk_id` and the postgres provider's `INSERT … ON CONFLICT (id) DO UPDATE` would silently overwrite the first material's vectors. Scoping the storage id by `material_id` (unique per upload) keeps re-ingestion of the same material idempotent while making different materials independent. ADR-0009's provenance rule is unaffected: `chunk_id`, `document_id`, and page references survive in metadata.
* **Provenance payload [Chosen, per TS §12.1 / ADR-0009]:** `metadata = {"material_id", "document_id", "chunk_id", "pages", "section", "language", "char_count", "page_count"}`; `content = chunk.text`. The JSONB payload is the only place provenance lives (mirrors the `VectorRecord` DTO contract; no schema change).
* Providers and their errors are PAL concerns; the stage maps nothing and retries nothing **[Authority: PAL exception hierarchy; router owns provider fallback]**.
* Output: `PersistResult` — the per-document counts the seam logs and tests assert on **[Authority: roadmap B1(a) "per-document counts/result"]**.

### 2.3 Sync/async boundary

* The Celery task stays synchronous and wraps everything in `asyncio.run(...)` **[Authority: existing task, pinned tests]**. Inside the task's dedicated event loop: `ingest_document()` and `chunk_document()` are called **synchronously (inline)** — the loop is task-local (prefork worker process per task), so a CPU-bound blocking call delays nothing else; introducing thread executors would add machinery without a demonstrated need **[Chosen]**. All provider interactions remain `await`ed: sequential per-page OCR enrichment, batched embeddings, the vector upsert **[Authority: provider interfaces are async]**. Revisit `asyncio.to_thread` for Docling only if B7/B8 profiling shows it matters — **[Future]**, not built now.

### 2.4 Database/session ownership

* The task owns its task-local engine + session factory (created in `process_material`, disposed in `finally`) — unchanged **[Authority: existing Phase-1B ownership model]**.
* The seam receives the **same live `AsyncSession`** that `_handle_material` uses, as a keyword-only parameter (see §6). Rationale: `claim_pending_material` commits the claim before returning; `transition_material_status` only flushes. Sharing the session means the vector upserts and the final `ready` transition commit **atomically** — no "ready without vectors" / "vectors without ready" window — and the failure path (rollback → transition `failed` → commit) already discards partial vector writes with zero new error-handling code. The postgres provider's never-commit contract is honored exactly as designed (caller owns the transaction) **[Chosen; provider contract is Authority]**.
* The stage functions themselves never see sessions or Celery — the caller constructs the session-backed provider via the factory and injects it **[Authority: roadmap B3; factory docstring]**.

### 2.5 Error propagation

* Any exception inside content processing → existing behavior: log, rollback, re-fetch, transition `failed`, commit, re-raise **[Authority: pinned lifecycle]**. PAL errors arrive already normalized (`ProviderError` family fallback-eligible; `InvalidInputError`/`ConfigurationError` fail immediately) **[Authority: TS §8.4]**. The pipeline adds no retry policy — provider fallback is the router's job, Celery routes/retries are H5/DevOps **[Authority: roadmap Q4/H5]**.

### 2.6 What the pipeline does not own

Material claim/status transitions and the status vocabulary; the enqueue contract; engine/session-factory lifecycle; the storage fetch call (it happens in the seam, §5); provider SDK imports; OCR page-artifact rendering (`ocr_source.py` owns it); retry/route policy; any business logic beyond composition.

---

## 3. Reasoning / LiteLLM architecture (Decision B)

### 3.1 The chain of responsibility

```text
Application/worker  →  PAL ReasoningInterface  →  LiteLLM gateway  →  model providers
(config selects)       (PAL provider adapter)     (routing, fallback,   (keys held HERE only)
                                                   budget, logging)
```

**[Authority: ADR-0005 — "Applications call the PAL interface rather than provider-specific SDKs. Provider credentials, routing, retries, key rotation, and cost tracking are configured at the gateway and deployment layer."]** LiteLLM is the application's LLM gateway **[Authority]**. OmniRoute is *not* the architectural gateway and must not couple to the PAL/reasoning layer (§3.7).

### 3.2 How the application reaches LiteLLM

Only through a PAL reasoning provider (built in B4), speaking the OpenAI-compatible chat-completions protocol over HTTP to the gateway base URL from configuration. No API router, service, or worker imports an HTTP LLM client directly; the SDK import lives only under `backend/app/pal/` **[Authority: TS §7.3, roadmap §10.1]**. TS §23.1 already deploys the base URL as `LITELLM_API_BASE=http://litellm:4000` on the backend service.

### 3.3 Client choice — `openai` SDK inside PAL **[Chosen]**

* **Decision:** implement the B4 provider with the official **`openai` Python SDK** (`AsyncOpenAI(base_url=…, api_key=…)`), pointed at the LiteLLM gateway. **Exact dependency line for B4 to add to `backend/requirements.txt` (one line, per roadmap B1(b)):**

  ```text
  openai==3.24.0
  ```

  (`openai` 3.24.0 is the latest published version at decision time, verified on PyPI 2026-10-05; B4 confirms the pin resolves cleanly against the existing stack — including its `httpx2` transport requirement vs the dev-only `httpx==0.28.1` pin — before writing the line. The dependency is **not** added in B1.)
* **Why not the `litellm` SDK:** ADR-0005 assigns routing, fallback, retries, budget, and key handling to the *gateway*; the deployed proxy already provides all of it (`litellm-config.yaml`: model_list fallback, `max_budget`, `drop_params`). A client-side `litellm` SDK would duplicate exactly those capabilities behind the app boundary and pull a heavy transitive stack — violating the one-dependency, no-new-machinery constraints (roadmap §11.3) without adding a capability the architecture wants the app to have. The `openai` SDK is the canonical client for OpenAI-compatible endpoints, has first-class async + streaming (needed for `reason_stream`), and is the smallest compatible boundary.
* **Intended usage (B4 implements; recorded here so no re-decision is needed):** constructor defaults from settings (`api_key=None → settings.litellm_api_key`, `model=None → settings.ai_reasoning_model`, `base_url=None → settings.litellm_api_base`) — mirroring `GeminiOCRProvider` exactly; `reason()` → `client.chat.completions.create(...)` → `ReasoningResult(text, model, provider="litellm", usage)`; `reason_stream()` → `stream=True`, deltas mapped to `ReasoningChunk`, `usage` only on the final chunk **[Authority: ADR-0009 ReasoningChunk contract]**; error mapping onto the PAL hierarchy mirroring the Gemini pattern: `APITimeoutError` → `ProviderTimeoutError`, `APIConnectionError` → `ProviderUnavailableError`, `RateLimitError` → `ProviderRateLimitError`, `InternalServerError` (5xx) → `ProviderServerError`, `AuthenticationError`/`PermissionDenied` (401/403) → `ConfigurationError` (not fallback-eligible); `health_check()` → cheap authenticated `client.models.list()` call (final endpoint choice in B4). Factory value: `ai_reasoning_provider=litellm`; `mock` default unchanged **[Authority: factory pattern, TS §8.2]**.

### 3.4 Configuration ownership — which values belong where

| Layer | Values | Owner / mechanism |
|---|---|---|
| **Application → gateway** | `litellm_api_base` (default `http://litellm:4000`; env `LITELLM_API_BASE` — already deployed on the backend service), `litellm_api_key` (env `LITELLM_API_KEY`; a LiteLLM virtual/master key; default empty), `ai_reasoning_model` (default `gpt-4o-mini` — the gateway's `default_model`), `ai_reasoning_provider` (`mock` default; `litellm` added by B4), `ai_reasoning_fallbacks` (existing PAL chain) | `config.py` Settings fields via pydantic-settings (env → Settings → factory → provider, ADR-0009). B4 adds these keys following the `ai_*` + provider-named-secret convention (`gemini_api_key` precedent). **[Chosen naming; flow is Authority]** |
| **Gateway → model providers** | `OPENAI_API_KEY` (today), future `ANTHROPIC_API_KEY`/GLM keys, key rotation, staging-vs-production separation | Referenced from `litellm-config.yaml` as `os.environ/…` and injected **only into the litellm container env** — deployment configuration owned by DevOps (ADR-0005). These are **not** application settings and never appear in `config.py` **[Authority]** |
| **Secrets never hardcoded/committed** | `LITELLM_MASTER_KEY`, `LITELLM_SALT_KEY`, `LITELLM_API_KEY`, `OPENAI_API_KEY` and all future provider keys, `GEMINI_API_KEY`, `S3_*` credentials, `DATABASE_URL`, `REDIS_PASSWORD` | Env vars only; `.env` is gitignored; compose interpolates `${VAR}` **[Authority: ADR-0009 §3.4; existing compose/config practice]** |

Staging wiring gaps (recorded observations, **no B1 action**; resolved by DevOps under H1): the `litellm` service env currently passes only master+salt keys, so `OPENAI_API_KEY` (referenced by the config) must be added to the container env; the `celery_worker` env passes no AI provider or gateway settings at all (roadmap F16) and will need `LITELLM_API_BASE`/`LITELLM_API_KEY` plus the AI provider vars for B5–B7.

### 3.5 Routing ownership

* **Model/model-fallback routing belongs to the gateway**: `model_list` (primary `gpt-4o-mini`, fallback `gpt-3.5-turbo`), budget guard, `drop_params` **[Authority: ADR-0005, F18]**.
* **Provider routing belongs to PAL**: which reasoning *provider implementation* is active (`ai_reasoning_provider`) and the ordered fallback chain (`ai_reasoning_fallbacks`, router fallback only on `ProviderError`, streaming fallback only before the first chunk) **[Authority: ADR-0009 §5, TS §8.3]**.
* The application selects a model *by name* through configuration; it never hard-codes one **[Authority: TS §10.1 "the architecture does not hard-code models"]**.
* **Credential selection belongs to the gateway layer** (which provider key to use per model); the application holds only the gateway key **[Authority: ADR-0005]**.

### 3.6 Future provider support without redesign

* **New direct provider (OpenAI/Anthropic/GLM/…):** add a `model_list` entry + provider key env var in the gateway deployment config. Zero changes to PAL interfaces, the factory, or application code. If a use case ever demands calling a provider *directly* (bypassing the gateway), a new PAL provider value can be added additively behind the unchanged `ReasoningInterface` — the interface is provider-agnostic by design **[Authority: interface contract; ADR-0005 "provider changes … do not require application-wide SDK changes"]**.
* **User-supplied/provider credentials (per-user keys):** **[Future — out of current scope]**; not designed now. The PAL boundary keeps the option open without pre-building anything (roadmap §11.3).

### 3.7 OmniRoute — evidence and recorded resolution

* **Repository evidence:** OmniRoute exists in the codebase **only** as two unused `config.py` fields (`omniroute_api_base`, `omniroute_api_key` — no consumer anywhere; verified by repo-wide grep) left from Week-6 planning (`week-06-plan.md` P12 "OmniRoute reasoning — SHOULD", never implemented). No SDK, adapter, or infra reference exists. ADR-0009 §3.4 defines its role: "Development uses local/free components and free APIs via OmniRoute. OmniRoute is a development gateway, **not an architectural dependency**." ADR-0005 + the 44-week plan (W7 "reasoning call routed via the gateway"; W14 "Reasoning via LiteLLM") + TS §7.2/§10.1 all bind the reasoning path to the LiteLLM gateway.
* **Resolution [Chosen, on top of Authority]:** OmniRoute is treated strictly as the **current free development credential source, consumed at the gateway layer**: if/when an OmniRoute-provided OpenAI-compatible credential is used, DevOps injects it as a litellm-container env var and (if needed) as an `openai`-compatible `model_list` entry in `litellm-config.yaml`. The application and PAL never learn of it.
* **Noted ADR-0009 tension (recorded, not silently resolved):** ADR-0009 §3.4 sketches "Reasoning: mock first, OmniRoute adapter second". This B1 resolves that sketch in favor of the gateway architecture by applying ADR-0009's own principle — OmniRoute must be known to exactly one, disposable component — which the gateway configuration satisfies even more strongly than a PAL adapter would (no adapter exists; building one would add exactly the coupling ADR-0009 forbids). This interpretation is flagged for Seyam's ratification in the B1 review; it blocks nothing (B2/B3 are unaffected; B4 builds the LiteLLM adapter either way).
* **Disposition of the legacy `omniroute_*` config fields:** dead configuration. B4 removes/replaces them when it touches `config.py` for the new gateway keys (a B4 implementation consequence — not done in B1, since B1 modifies no code).

---

## 4. Document type / OCR scope (Decision C)

* **Current behavior [Authority]:** ingestion's enabled format set is PDF, DOCX, HTML, Markdown, and images (TS §11.2, `ingestion.py`); the OCR page-source resolver is **PDF-only** (`create_single_page_pdf` raises `UnsupportedDocumentTypeError` for any non-`.pdf` suffix); the Gemini provider accepts **PDF bytes only** (`.pdf` suffix + `%PDF-` header validation). A non-PDF document forced through the PDF OCR path would therefore crash mid-pipeline.
* **Decision [Chosen per roadmap B1(c) default]:** the Week 7–8 targeted-OCR path is **PDF-only**.
  * PDF sources: resolver + OCR enrichment exactly as implemented (pages below `settings.ocr_min_text_chars`).
  * Non-PDF sources: the pipeline **skips OCR gracefully** — no exception, no provider call — and records a per-document note in `document.metadata["ocr"] = {"applied": False, "skipped": True, "reason": "non_pdf_source_not_in_week7_8_ocr_scope"}` (document-level; no page is modified). PDF detection = `.pdf` suffix of the local source path, the same rule the resolver and provider already enforce, so behavior can never disagree between layers.
  * The chained pipeline never lets a `UnsupportedDocumentTypeError` from the OCR path fail an otherwise-ingestible document; conversion errors from ingestion itself still propagate (existing typed errors) **[Authority: `ingestion.py` error surface]**.
* **Image-specific ingestion/OCR expansion: deferred [Future]** — explicitly recorded per the roadmap default; deviating later requires a new decision entry. A non-PDF resolver can be added later without signature changes (the resolver is an injected `PageSourceResolver`), so nothing is closed off.
* **A broader document-ingestion pipeline upgrade (format expansion, engine benchmarking via ADR-0003, richer normalization) is a future improvement and is outside the current Week 7–8 implementation scope [Out of scope]** — Week 9+ owns ingestion hardening; no redesign is started here.

---

## 5. Storage fetch and Backend/Celery integration (Decision D)

* **Evidence [Authority]:** `storage.py` exposes only upload-URL generation (F13) and is **Backend-owned** (roadmap §10.1; handoff H2). The 44-week plan assigns the worker-side chain to Pod B and assigns a storage fetch to nobody; the `celery_worker` compose service already receives the full S3 env (endpoint/access/secret/bucket/region), so the worker has the credentials it needs. The pipeline's consumers (`ingest_document`, `create_single_page_pdf`) are path-based.
* **Decision:** yes — implement the helper **within AI Week 7–8 work (B5)**, as the smallest possible addition inside Backend-owned `backend/app/services/storage.py`, with **Backend approval (H2) recorded before B5 lands it**. Implementing it ourselves avoids manufacturing a cross-team blocker for a capability nothing in the plan assigns elsewhere; it does **not** silently change ownership — the module owner approves the pattern first, exactly as the roadmap's H2 defines **[Chosen within roadmap Authority]**.
* **Boundary contract (B1 decides; B5 implements):**
  * Name (B5 finalizes with Backend, e.g. `download_material_to_temp`); **synchronous** (boto3 is sync; the task's event loop is task-local, §2.3); input = the task's existing `s3_key` argument plus nothing else required (bucket from `settings.s3_bucket_name`; reuses the existing `_s3_client()` construction unchanged).
  * **Returns a local `Path`** to a readable file — not bytes (Docling and pypdfium2 are path-oriented; a bytes API would force a temp file anyway and double the handling), and not a stream (no back-pressure value for a one-shot worker download) **[Chosen]**.
  * Writes into a **per-task temporary directory** created by the caller (the seam); the helper itself creates no global state.
  * **Cleanup/lifecycle:** the seam deletes the whole per-task temp directory (downloaded source + single-page OCR artifacts) in a `finally` block, on success and on failure — deterministic, no background reaper **[Chosen; satisfies roadmap B5 "deterministic temp-file cleanup"]**.
  * The presigned-upload path and `generate_upload_url` are untouched; no new configuration keys (the helper consumes the existing `S3_*` settings).
* **If Backend withholds H2 approval:** B5's recorded fallback applies — the seam is implemented behind a fetchable-file parameter so only the helper call site waits **[Authority: roadmap B5 stop-condition]**.

---

## 6. Celery contract preservation

Restated verbatim, unchanged by B1 and by every batch that implements these decisions:

* Task name: `app.workers.tasks.material_tasks.process_material`
* Arguments: `(material_id, s3_key, course_id, owner_id)` — published by `publishing.enqueue_material_processing` via `send_task`.
* Lifecycle semantics unchanged: atomic claim (`pending → processing`, committed), missing material → `None`, non-pending → current status no-op, success → `ready` + commit, **any exception inside content processing → `failed` + commit + re-raise**; task-local engine/event loop per invocation; delivery config and time limits pinned by the tripwire tests (`acks_late` False, no `reject_on_worker_lost`, `publish_retry` True, soft 600 s / hard 660 s).
* The seam callable keeps its positional contract `(material, s3_key, course_id, owner_id)`; B1 adds **no code**. For B5, the seam signature is extended by one **keyword-only `session: AsyncSession`** (§2.4) so the provider construction and atomic persist (§2.4) match the roadmap's B5 description; B5 updates the stubbed-seam tests for that parameter in the same file **without weakening any of the 11 pinned assertions** **[Authority: roadmap B5 explicitly authorizes stub updates in-file]**. The public task contract above is not touched by that internal change.

---

## 7. Implementation consequences (what each batch now implements)

* **B2 — stage 1:** create `backend/app/services/document_pipeline.py` with `ingest_and_enrich` exactly per §2.1: wire `pdf_page_source_resolver` for PDF sources; skip OCR for non-PDF with the §4 metadata note; no provider SDK imports; tests `backend/tests/services/test_document_pipeline_stage1.py` (threshold fires/not, multi-page, non-PDF skip note, temp-artifact cleanup, mock OCR provider, `tmp_path` PDFs).
* **B3 — stage 2:** extend the same module with `chunk_embed_and_persist` + `PersistResult` per §2.2: batching loop with empty-input guard; `VectorRecord` identity `{material_id}:{chunk_id}`; the §2.2 provenance payload; injected providers only; tests `backend/tests/services/test_document_pipeline_stage2.py` (batching, empty document no-op, provenance shape, `chunk_id` determinism).
* **B4 — LiteLLM reasoning provider:** `backend/app/pal/providers/reasoning/litellm_provider.py` implementing `ReasoningInterface` with the `openai` SDK per §3.3 (constructor defaults ← settings; error-mapping table; streaming contract); factory value `litellm`; `config.py` keys `ai_reasoning_model`, `litellm_api_base`, `litellm_api_key` (and disposition of the dead `omniroute_*` fields per §3.7); **one** dependency line `openai==3.24.0` in `backend/requirements.txt` (pin re-verified at implementation); offline unit tests with the client mocked; import-rule grep shows SDK strings only under `backend/app/pal/`.
* **B5 — seam wiring + storage helper:** implement the seam body (fetch via helper → stage 1 → stage 2 with factory-built providers, pgvector provider receiving the shared task session per §2.4) with `finally` temp-dir cleanup; add the minimal fetch helper to `backend/app/services/storage.py` per §5 **after H2 approval**; update the stubbed-seam tests for the keyword-only `session` parameter and add wired-path coverage; never weaken the 11 pinned tests.
* **DevOps coordination (not AI code):** H1 staging env for `celery_worker` (AI provider vars + `LITELLM_API_BASE`/`LITELLM_API_KEY`) and provider-key env inside the `litellm` container (§3.4); H5 task-name/transient-error handoff unchanged.

---

## 8. Open questions / assumptions

Genuinely unresolved items only:

1. **Ratification of the OmniRoute resolution (§3.7)** — the interpretation that resolves ADR-0009's "OmniRoute adapter second" line into a gateway-layer credential source is recorded with evidence and flagged for Seyam's decision at B1 review. Nothing in B2–B5 depends on it; if Seyam instead wants a PAL-level OmniRoute adapter, that is a new decision entry. (Status: open for ratification, non-blocking.)
2. **BGE-M3 instantiation scope** — the provider lazy-loads the model per provider instance; B5 confirms the observed load pattern (per-task construction) and records it (roadmap §11.2 risk). Assumption for Week 7–8 volumes: per-task construction is acceptable; any change becomes a decision item. (Status: assumption, verified at B5.)
3. **`openai==3.24.0` pin compatibility** — B4 verifies the line resolves cleanly against the current stack (including the `httpx2` transport requirement vs the dev-only `httpx==0.28.1` pin) before writing `requirements.txt`; if it does not, B4 re-opens B1(b) with evidence per the roadmap's stop-condition. (Status: assumption, verified at B4.)
4. **Gateway `/v1` surface assumption** — the provider targets the OpenAI-compatible chat surface of the deployed proxy (`http://litellm:4000`); B6's live gateway call is the runtime proof. (Status: assumption, verified at B6.)
