# OpenLearn-AI — 44-Week Execution Roadmap

**Project:** OpenLearn AI — Arabic-first adaptive learning platform
**Planning horizon:** 44 weeks · 3 Aug 2026 → 6 Jun 2027
**Document type:** Execution control document (weekly, per-pod)
**Status anchor:** Actual project state at end of Week 6 (reconstructed from the six weekly task emails; implementation status cross-verified against the final Technical Specification v4.1 — staging baseline `d293dca`)
**Pods:** A — Backend (Abanoub, Waleed) · B — AI/ML & Data (Seyam, Pola) · C — Frontend (Ibrahim, Waseem) · D — DevOps/QA (Hisham, Montaser) · Docs Owner rotation (Hossam first)
**Review cadence:** Daily async update · Tuesday cross-pod sync · Thursday merge cutoff · Friday staging demo + retro · tag cut only after a passing Friday demo

---

## 1. Purpose

This roadmap defines **what we build, when, who owns it, the deliverable, and the dependency/validation gate** for every one of the 44 weeks. It is the source from which weekly task emails are generated and the reference pod leads use for weekly planning. It deliberately does not explain architecture — that is the Technical Specification's job.

---

## 2. Source of Truth & Planning Rules

**Authority order**

| Source | Role |
| --- | --- |
| `OpenLearn_AI_v4_Technical_Specification.md` (TS v4.1, final — all sections verified against the `staging` baseline `d293dca`) | Technical authority: architecture, implementation status, current vs planned capabilities, NFR targets. Never contradict it. Where an ADR conflicts with the TS, the ADR governs (ADR-0002). |
| Master Roadmap | Strategic authority: project direction, phases, release ladder, graduation objectives. Its strategic intent is preserved in §4 and §6. |
| This 44-week roadmap | Execution authority: tasks, owners, deliverables, dependencies, DoD per week. |
| Weekly task emails (W1–6) | Execution evidence: what was actually assigned and delivered. History is recorded, not rewritten; where an email conflicts with the final TS, the email preserves the historical sequence and the TS determines the current interpretation. |

**Planning rules**

1. **No invented work.** Every task traces to the TS, the Master Roadmap, the previous 44-week plan, or a gap exposed in W1–6.
2. **Implemented ≠ planned.** Work that exists (Keycloak auth, pgvector, course CRUD, PAL providers, deployed infra) is never re-scheduled; work that is target architecture (RAG, KG, SKM, adaptive engine, WebSocket chat, analytics) is scheduled as work to be done.
3. **Targets are targets.** Performance and quality figures from TS §25.1 are scheduled as benchmarks to run, never as results already achieved.
4. **API paths are not invented here.** Only the paths established in TS §22.4 (planned surface) and TS §22.3 (verified surface) appear verbatim in this roadmap. Where no path is established, the task defines the contract ("Implement the retrieval service and its API contract").
5. **No manufactured precision.** The only numbers used are TS §25.1 NFR targets, TS-stated design defaults, and figures documented in the W1–6 emails (historical). No arbitrary dataset sizes, counts, or thresholds.
6. **Status vocabulary** (historical weeks): `Completed` · `Partial — carried to Wn` · `Deferred — rescheduled to Wn`.
7. **Low-capacity weeks** (exam crunches): W25–W27 and W39–W40 carry reduced scope by design.
8. **Contract changes after a Tier freeze** require a new ADR + two pod-lead reviews (ADR-0002 governance; TS §18.4 boundary discipline).
9. **Scope guard:** the signed Out-of-Scope list (15 items, W1) remains binding; changes go through the Tuesday sync.

---

## 3. Current State at End of Week 6

Reconstructed from the six weekly emails; implementation status cross-checked against the final TS (as-built sections §6.1, §11.1, §12.1, §15.1, §19, §21–§23, §25.2).

| Area | Status | Key completed work | Remaining priority |
| --- | --- | --- | --- |
| Governance & docs | Completed | Repo rules; ADRs 1–5 merged + index (W4); ADR-006 draft (superseded by the Keycloak decision), ADR-007/008 opened (W5); CONTRIBUTING/CODEOWNERS; MVP definition approved; risk register v1 (top-3 actively managed); tech-debt register | Keep the ADR pipeline flowing as new decisions land |
| CI/CD & environments | Completed | CI enforced (lint, backend/AI/frontend checks, migration check, eval job, Chromatic); dev + staging compose environments; both apps on public HTTPS | Coverage gates (NFR-10); backup/DR (W12+); production deploy (W43) |
| Auth & identity | Completed | **Keycloak + OIDC (Authorization Code + PKCE)** end-to-end; RS256/JWKS validation; realm roles student/instructor/admin; JIT provisioning; `/auth/me` | Security hardening (W40); self-service registration dependency |
| Backend core | Completed | Course CRUD + ownership, enrollments, profile read/update (users router; `GET/PUT /v1/users/me` per the W6 email), materials + presigned S3-compatible upload (status `pending`), Alembic baseline (12 migrations) | Wire the async processing chain (W7); status endpoint (W7) |
| Frontend foundation | Completed | Design tokens (Tailwind 4, light/dark), Storybook + Chromatic, Keycloak auth UI + protected routes, course list/create/edit, profile page. No client-state library beyond React + TanStack Query (TS §20.1) | Document viewer, chat UI, dashboards, RTL audit |
| Ingestion & OCR | Partial | Docling → `CanonicalDocument`; custom deterministic chunking (`chunk_size`/`chunk_overlap`, 1200/150); **Gemini `gemini-2.5-flash` OCR provider**; BGE-M3 embedding provider (1024-dim) — all as service modules (TS §11.1) | Run the chain inside the Celery worker incl. targeted-OCR orchestration (W7); golden-set hardening (W9) |
| Vector store | Partial | PostgreSQL 16 + **pgvector** (`vector_records`, `VECTOR(1024)`, cosine, JSONB provenance); PAL `VectorDBInterface` incl. delete-by-filter | Production retrieval path + filters (W10) |
| LLM / reasoning | Partial | **LiteLLM gateway deployed** on staging (`gpt-4o-mini` → `gpt-3.5-turbo`, budget cap, Langfuse callback configured — service not deployed); PAL reasoning provider still mock in product flows | Route product reasoning through the gateway via the PAL adapter (W7/W14) |
| Async jobs | Partial | Redis 7.4, Celery worker + beat, Flower deployed on staging — infrastructure only, no processing tasks registered (TS §19.4) | Connect upload → process task chain (W7) |
| Observability | Partial | Prometheus, Loki, Alloy, Grafana, Sentry collecting on staging | Grafana dashboards + alert rules (W7); SLO checks in P5 |
| Evaluation | Partial | Basic eval harness (`python -m app.eval`, registry, JSON datasets, dummy evaluator) wired into CI (TS §10.2) | Golden datasets; retrieval/RAG/adaptation evals (W10+) |
| Retrieval / RAG | Not started | Building blocks exist (pgvector search contract, embeddings, gateway) | Retrieval service (W10) → hybrid + rerank (W13) → RAG (W14) → thin MVP (W16) |
| Knowledge graph | Not started | — (no graph store, no extraction; TS §13) | Schema/storage ADR (W21), extraction spike (W22), pipeline (W23), API + viz (W24) |
| SKM / adaptive | Not started | 6-field profile subset implemented (TS §15.1) | Mastery schema (W27), estimator (W27–29), adaptive engine (W31–33) |
| Analytics | Not started | — | Aggregation + instructor dashboard (W34–35) |
| Multimodal (speech/vision) | Not started | PAL has no Speech/Vision interfaces (TS §8.1 — six interface files) | Stretch/post-v1.0 (TS §29.3) |
| Bilingual / RTL | Partial | Arabic-capable pipeline (Gemini OCR, BGE-M3 multilingual); en/ar constraint enforced in the profile model | Arabic ingestion validation (W9); RTL + bilingual verification vs NFR-8 (W37/W41); bilingual UI depth per scope |

**Architecture changes absorbed from W1–6** (old-plan assumptions that no longer hold — do not resurrect):

1. **Auth:** custom JWT/bcrypt (`/v1/auth/register`, `/v1/auth/login`, ADR-006 draft) → **Keycloak + OIDC** finalized in W6. Custom auth endpoints are deprecated; no password hashes or refresh tokens live in the application database (TS §22.2, ADR-0006).
2. **OCR engine:** PaddleOCR-primary recommendation (ADR-007 spike) → **Gemini `gemini-2.5-flash` provider** is the shipped implementation (TS §11.5). PaddleOCR/Surya remain benchmark candidates in `experiments/` only (ADR-0003).
3. **Vector store:** Qdrant-primary plan → **pgvector is the implemented store** (TS §21.1, ADR-0004). All Qdrant deployment tasks are removed.
4. **Chunking:** LangChain-based plan → **custom deterministic structure-aware chunking**, configuration-parameterized (TS §11.4). LangChain is not part of the stack.
5. **PAL:** seven-interface plan → **five capability interfaces implemented** (embedding, ocr, ranking, reasoning, vector_db) + shared base contract — six interface files; Speech/Vision are future multimodal work (TS §8.1, §29.3).
6. **Runtime:** Python **3.11** in deployment (TS §19.1/§26.1); W1–2 references to Python 3.12 are historical.
7. Old-plan W7 infrastructure items (LiteLLM deploy, observability stack, Celery stack) have landed per the TS; what remains is **wiring them into product flows** — that is Week 7's job.

---

## 4. Phases & Milestones

| Phase | Weeks | Objective | Exit milestone |
| --- | --- | --- | --- |
| P0 — Pre-Flight | W1–4 | Setup, decisions, governance, skeletons, v0.1 | **v0.1.0 tagged (done)** |
| P1 — Foundations | W5–8 | Auth (Keycloak pivot), courses, upload, async wiring, observability | **v0.2 (W8)** |
| P2 — AI Pipeline | W9–20 | Ingestion hardening → retrieval → hybrid + rerank → RAG → chat; Tier 1 contracts | **v0.4 Thin MVP + Gate 1 (W16) · v0.5 + Tier 1 Freeze + Gate 2 (W20)** |
| P3 — Knowledge & Cognition | W21–30 | KG schema/pipeline/viz, quiz generation, SKM mastery; Tier 2 contracts | **v0.6 (W26) · v0.7 + Tier 2 Freeze + Gate 3 (W30)** |
| P4 — Adaptation & Analytics | W31–38 | Adaptive engine, review scheduling, adaptation eval, analytics dashboards | **v0.8 (W34) · v0.9 + Feature Freeze + Gate 4 (W38)** |
| P5 — Hardening | W39–42 | Performance vs TS §25.1 targets, security, docs, DR | **v1.0-rc + Code Freeze + Gate 5 (W42)** |
| P6 — Graduation | W43–44 | Production deployment, dry-runs, presentation | **v1.0 + graduation (W44)** |

---
## 5. Weeks 1–44

**Weeks 1–6 are execution history** (evidence: weekly task emails; implementation status interpreted through the final TS). **Weeks 7–44 are the forward plan**, starting from the state in §3. Weekly structure: Objective → pod tasks → Deliverables → Dependencies (when load-bearing) → Definition of Done.

### Week 1 — Kickoff + Stack Lock

**Status:** Completed (historical)

**Backend** · Frontend stack sign-off (Next.js 16, Tailwind 4, shadcn/ui); backend stack sign-off (FastAPI, PostgreSQL 16, SQLAlchemy 2); FastAPI skeleton prep; DB/Alembic plan.
**AI/ML & Data** · AI stack sign-off; OCR/embedding spike preparation; out-of-scope review.
**Frontend** · Next.js project scaffold + theme settings; design tokens started.
**DevOps/QA** · GitHub org/repo governance (PR templates, CODEOWNERS, branch protection); CI scaffold verified with dummy PR; dev/staging/prod environment config.
**Documentation** · README/CONTRIBUTING/CODEOWNERS check; ADR scaffold in `docs/adr/`; 15-item Out-of-Scope list signed and archived.

*Note: W1 emails referenced Python 3.12 and PaddleOCR; both were later superseded (Python 3.11 runtime — TS §19.1; Gemini OCR provider — TS §11.5).*

### Week 2 — MVP Sign-off + Skeletons

**Status:** Completed (historical)

**Backend** · FastAPI skeleton: `/health`, OpenAPI docs, CORS, env config; basic tests in CI; staging-ready.
**AI/ML & Data** · OCR benchmark methodology (Arabic quality, layout, latency); embedding evaluation structure; AI pipeline I/O contracts drafted; test data organized.
**Frontend** · Design tokens locked (Tailwind 4 + CSS variables, light/dark); `docs/design-tokens.md`; skeleton on public HTTPS; Storybook verified.
**DevOps/QA** · CI/CD stabilized; Dockerfiles for backend/frontend; staging deployment path ready; secrets strategy; smoke checks defined.
**Documentation** · `docs/mvp.md` drafted and circulated; docs structure + conventions.

*Note: PostgreSQL/Alembic deliberately deferred to W3.*

### Week 3 — Hello World on a Real URL + DB Baseline

**Status:** Completed (historical)

**Backend** · PostgreSQL 16 provisioned (dev + staging); Alembic initialized with baseline migration; `users` table migration; migration workflow documented.
**AI/ML & Data** · OCR benchmark executed (PaddleOCR vs Tesseract) and embedding evaluation executed (BGE-M3 vs OpenAI) with documented results and recommendations; golden 20-PDF set (5 clean / 5 scanned / 5 Arabic+English / 5 figures) with manifest.
**Frontend** · Public HTTPS deployment verified; design-token/theme stability; accessibility pass; component-gap review.
**DevOps/QA** · Both skeletons live on public HTTPS; smoke tests green; CI enforced on all PRs.
**Documentation** · MVP definition approved and archived; live deployment URLs documented; ADR 1–5 reviews tracked.

*Note: LiteLLM gateway deployment was targeted for W7 from this point.*

### Week 4 — ADRs + Risk Register + v0.1

**Status:** Completed (historical) — **v0.1.0 tagged**

**Backend** · ADRs 1–5 Accepted and merged + ADR index; CONTRIBUTING.md + CODEOWNERS co-authored.
**AI/ML & Data** · Research-spike template + `docs/spikes/ocr-spike.md` opened; demo-PDF RAG smell test (3 sample Q&A pairs, ≥2 with correct citations — per the W4 email); LiteLLM deployment plan signed, `litellm/proxy` image pre-pulled.
**Frontend** · Storybook → Chromatic visual regression gating PRs; polished visual login page; notebook layout research.
**DevOps/QA** · Eval harness scaffold in CI (dummy evaluator); `scripts/smoke_test.sh`; risk register v1 (top-3 risks under active management); **v0.1.0 tagged + GitHub Release** after passing Friday demo.
**Documentation** · W4 artifact consistency pass; v0.1 readiness record.
*Note: tech-debt register opened (auth scaffold returning 501 → payoff planned W5).*

### Week 5 — Auth + OCR/Embedding Spikes + First PAL Provider

**Status:** Partial — frontend auth tasks carried to W6; auth architecture superseded in W6

**Backend** · `POST /v1/auth/register` + `POST /v1/auth/login` with self-issued JWT/refresh implemented (≥80% auth-module coverage per the W5 email); ADR-006 (token format) drafted. **Superseded:** W6 finalized Keycloak + OIDC; custom endpoints and ADR-006's JWT design deprecated (TS §22.2 historical note).
**AI/ML & Data** · OCR spike on the 20-PDF golden set → **ADR-007** (PaddleOCR-primary recommendation — superseded: the shipped OCR provider is Gemini; PaddleOCR/Surya remain benchmark candidates in `experiments/` per ADR-0003 and TS §11.5). Embedding spike → **ADR-008** (BGE-M3 primary, cloud fallback — consistent with the shipped stack). First PAL provider attempt (PaddleOCRProvider per the W5 email) — not present in the verified baseline; the shipped OCR providers are Gemini + mock (TS §8.1).
**Frontend** · Register/login pages + session handling **not completed — carried to W6**.
**DevOps/QA** · Redis + Celery worker + Flower on staging (sample task end-to-end); observability baseline (Loki, Prometheus, Sentry + `/test/error`); auth integration tests (8 cases) in CI.
**Documentation** · ADR pipeline consistency; spike records reviewed; auth endpoint docs (later superseded).

### Week 6 — Keycloak Pivot + User Mgmt + Course CRUD

**Status:** Completed (historical), including W5 frontend catch-up

**Backend** · Profile API (`GET`/`PUT /v1/users/me` per the W6 email; users router, 6-field profile subset — TS §15.1); **Keycloak RBAC** (roles from validated token `realm_access.roles`); Course CRUD + server-side ownership; `enrollments` table; presigned **S3-compatible** upload URL + material registration (status `pending`, virus-scan stub).
**AI/ML & Data** · OCR and embedding providers finalized behind PAL (Gemini OCR, BGE-M3, pgvector); document pipeline started (Document → OCR → Clean/Normalize → Chunk → Embed); normalized document/chunk schemas; provider fallback + failure tests.
**Frontend** · **Keycloak OIDC (Authorization Code + PKCE)** integration; session state + protected routes (W6 email planned Zustand "where appropriate" — the verified baseline ships no client-state library beyond React + TanStack Query, TS §20.1); `/auth/me` TanStack Query integration; auth UI aligned to Keycloak; RTL tests; course list / create / edit pages; profile page.
**DevOps/QA** · Staging stabilized (Keycloak, queue, storage endpoint, health checks, persistent volumes); CI extended (backend/AI/frontend/lint/migration checks, failing checks block PRs); env config cleanup + `.env.example`.
**Documentation** · Keycloak/OIDC integration doc as auth source of truth; deployment docs updated; tech-debt payoff tracking.

*Note: emails named "MinIO"; the TS-verified deployment consumes an S3-compatible endpoint via configuration (no MinIO service in compose — TS §21.1).*

### Week 7 — Async Pipeline Wiring + LLM Gateway Traffic

**Objective**

* Connect the deployed-but-unwired infrastructure: uploads processed end-to-end by the Celery worker; first reasoning calls through the LiteLLM gateway.

**Backend**

* Enqueue the processing task on material registration (`202 Accepted` + job reference, TS §19.4); implement the material status state machine `pending → processing → ready/failed` (the status vocabulary is owned by the processing phase, TS §11.1).
* Add the processing-status endpoint (`GET /materials/{id}/status`, TS §22.4) + per-course materials list.

**AI/ML & Data**

* Implement the worker-side ingestion chain (TS §11.7): Docling → `CanonicalDocument` → targeted OCR → deterministic chunking (`chunk_size`/`chunk_overlap` config) → BGE-M3 batch embedding → pgvector insert with JSONB provenance.
* Implement the targeted-OCR orchestration loop per ADR-0009 (OCR only for pages with insufficient extracted text, `OCR_MIN_TEXT_CHARS` threshold; TS §11.5); verify PAL provider fallback + health checks behave correctly inside the worker chain.

**Frontend**

* Material upload flow against the presigned URL; processing status display (polling until the realtime channel arrives with chat, W15); course detail page.

**DevOps/QA**

* Verify all PAL providers import cleanly inside the Celery worker container; task routes + retry policy; Grafana dashboards (queue depth, API latency, error rate); **Langfuse decision**: deploy the service or defer with a tech-debt entry (callback already configured, TS §6.1).

**Deliverables**

* Seeded PDF processed end-to-end on staging (text + chunks + vector row queryable); status endpoint; test reasoning call routed via the gateway.

**Dependencies**

* W6 upload pipeline + materials API; W5 Celery/Redis stack; LiteLLM gateway (deployed).

**Definition of Done**

* Material reaches `ready` with chunks + vectors stored; status visible in UI; gateway call succeeds with budget guard active; no provider library imported outside PAL.

### Week 8 — Integration Close-Out + v0.2

**Objective**

* Close P1 with the first integrated flow demoed and the ingestion design fully recorded.

**Backend**

* Publish OpenAPI reference; integration tests for auth → course → material flow; ADR hygiene: confirm the implemented ingestion design (document model, chunking parameters, provenance) is recorded — ADR-0009 already governs PAL/ingestion/RAG; update it or the ADR index rather than opening a duplicate.

**AI/ML & Data**

* Multi-PDF ingestion smoke; chunk-quality review (no orphan/giant chunks); embedding configuration documented (BGE-M3, 1024-dim, batch path).

**Frontend**

* Playwright E2E: register → login → create course → upload → status ready.

**DevOps/QA**

* Coverage baseline report (NFR-10 trajectory); **v0.2.0 tag** after passing Friday demo; cross-training session (auth + queue internals).

**Documentation**

* Launch the Docusaurus public docs site (W2 prep → live URL) with the MVP definition + ADR index.

**Deliverables**

* v0.2.0 tag; E2E test green on staging; ingestion design confirmed in the ADR record; OpenAPI published.

**Definition of Done**

* E2E green; OpenAPI current with implemented routes; tag cut after demo; coverage baseline recorded in CI.

### Week 9 — Document Status Surface + Ingestion Hardening

**Objective**

* Make ingestion robust and observable across the real corpus (Arabic + scanned included).

**Backend**

* Material/document status surface on the materials router (processed document + per-course listing) and an admin reprocess path (`POST /materials/{id}/process`, shape TBD — TS §22.4); idempotent processing keyed on the deterministic `document_id` (TS §11.3).

**AI/ML & Data**

* Ingest the full 20-PDF golden set; Arabic text normalization checks; OCR quality benchmark on the golden set following the ADR-0003 methodology (hand-verified ground truth → metrics) — **record the measured baseline**; NFR-3 (100 pages < 60 s incl. OCR) is the processing-time *target* to benchmark against, not a result.

**Frontend**

* Extracted-text viewer per document/page.

**DevOps/QA**

* Ingestion integration tests in CI; golden-set runner script; failure-mode alarms (worker errors → Sentry).

**Deliverables**

* All golden PDFs processed with text + chunks stored; reprocess idempotent; measured OCR/embedding baseline table.

**Definition of Done**

* Golden set fully processed on staging; duplicate upload does not duplicate rows; baseline recorded in `docs/`.

### Week 10 — Retrieval Foundation (pgvector)

**Objective**

* First production vector retrieval path on stored chunks.

**Backend**

* Implement the retrieval service and define its API contract (top-k + course/document filters on the `VectorDBInterface.search` contract, TS §12.1); path per the TS §22 endpoint vocabulary.

**AI/ML & Data**

* Promote the pgvector provider to the production retrieval path (cosine, metadata filters); retrieval evaluation set v0 (Arabic + English queries with expected chunks); measure precision@5 baseline.

**Frontend**

* Basic search results UI with chunk → document linking.

**DevOps/QA**

* Retrieval health check added to staging smoke; a real eval dataset replaces the dummy job in CI.

**Deliverables**

* End-to-end vector retrieval working on seeded documents; reproducible eval script + baseline numbers.

**Dependencies**

* W7–9 ingestion chain (chunks + vectors must exist).

**Definition of Done**

* Seed queries return relevant chunks on staging; eval runs in CI; provider swappable via config without service-code change.

### Week 11 — Embedding Batch Job + Chunk Surfacing

**Objective**

* Batch (re-)embedding capability and chunk transparency for QA.

**Backend**

* Chunk-inspection surface for QA on the materials/documents read path (chunk text + provenance from `vector_records.metadata`, TS §21.2).

**AI/ML & Data**

* Celery Beat batch embedding job (backfill + model-swap path via PAL config); note that any embedding-model change is an explicit dimension migration, not a config flip (TS §12.1).

**Frontend**

* Chunks/source panel in the document view.

**DevOps/QA**

* Beat schedule monitoring; batch job metrics (throughput, failures) on Grafana.

**Deliverables**

* One Beat run embeds the un-embedded chunk backlog on staging; chunks browsable in UI.

**Definition of Done**

* Batch job completes and is idempotent; re-embedding after a config change produces updated vectors or fails loudly on dimension drift; monitoring shows job metrics.

### Week 12 — v0.3 Ingestion Release

**Objective**

* Tag the ingestion milestone: upload → processed → searchable.

**Backend**

* Demo-flow fixes; storage lifecycle (delete material → chunks/vectors cleanup via the PAL delete-by-filter contract, TS §12.1).

**AI/ML & Data**

* Record retrieval baseline vs targets; open the hybrid-retrieval + reranker design ADR (TS §12.3; ranking is deferred in ADR-0009 — record the adoption decision and provider candidate).

**Frontend**

* v0.3 demo polish.

**DevOps/QA**

* Staging backup script (DB dump + volumes); **v0.3.0 tag** after passing demo.

**Deliverables**

* v0.3.0 tag; hybrid/reranker design ADR opened; backup script in repo.

**Definition of Done**

* Fresh upload becomes searchable within one working session on staging; deletion cleans all derived rows; tag cut after demo.

### Week 13 — Hybrid Retrieval + Reranker

**Objective**

* Improve retrieval quality with hybrid search and the first `RankingInterface` provider.

**Backend**

* Expose the ranked retrieval contract (TS §12.2–§12.3) through the retrieval service API.

**AI/ML & Data**

* Implement a `RankingInterface` provider behind PAL (bge-reranker-v2-m3 is the TS-planned candidate, TS §26.1); hybrid semantic + keyword merge with the TS design weighting (default 70/30, TS §12.3); re-rank only the top-K first-stage candidates (design default K = 20); A/B comparison on the eval set (hybrid vs pure vector — record measured results).

**Frontend**

* Source panel shows ranked citations with scores.

**DevOps/QA**

* Reranker latency logging; retrieval eval regression job.

**Deliverables**

* Working reranker behind config; recorded hybrid-vs-vector comparison.

**Definition of Done**

* Reranker substitutable without changing service code; eval comparison committed; no quality regression on golden queries.

### Week 14 — RAG Pipeline v1

**Objective**

* Grounded generation with citations through the LiteLLM gateway.

**Backend**

* Implement the RAG query service (retrieve → rerank → generate) per ADR-0009/TS §12.2 and define its request/response contract; source preservation rule applies — `chunk_id`, `document_id`, page references survive into the answer's sources.

**AI/ML & Data**

* **Switch reasoning product traffic to the LiteLLM gateway** via the PAL reasoning adapter (`gpt-4o-mini` → `gpt-3.5-turbo` chain, budget guard); grounded prompt + citation format + structured output enforcement + low-confidence clarification handling (the three §12.2 mechanisms); golden RAG Q&A set v1; run the eval harness — measure faithfulness and citation accuracy.

**Frontend**

* Citation chips linking answers to source chunks.

**DevOps/QA**

* Gateway budget alerts; RAG eval job (nightly) in CI.

**Deliverables**

* RAG service returning cited answers on staging; golden set v1 + eval report committed.

**Dependencies**

* W13 retrieval contract; W7 gateway wiring.

**Definition of Done**

* Golden-set queries return answers with correct citations (measured, recorded); eval reproducible in CI; budget guard prevents runaway spend.

### Week 15 — Chat Sessions + Streaming

**Objective**

* Conversational interface on top of the RAG pipeline, with streaming responses.

**Backend**

* Chat session create/list/get/delete with per-user ownership (`POST /chat/session`, TS §22.4); streaming chat transport over WebSocket (`WS /ws/chat/{session_id}`) with the ADR-0009 event protocol (`retrieval_started`, `sources_found`, `reasoning_started`, `token`, `done`, `error`) — with a documented SSE fallback decision if WS proves premature.

**AI/ML & Data**

* Streaming generation via the PAL router streams path; multi-turn context assembly (session history + retrieved chunks); no-context/refusal handling.

**Frontend**

* Chat UI on the sessions API; streaming message rendering; session list; migrate processing status to the same realtime channel (or document why polling stays).

**DevOps/QA**

* WebSocket integration tests; connection-drop/reconnect behavior; streaming load smoke.

**Deliverables**

* Streaming chat with citations on staging; persistent session history.

**Definition of Done**

* Multi-turn chat works against seeded documents with citations; session survives reconnect; tests cover the auth'd WS path.

### Week 16 — v0.4 Thin MVP — GATE 1

**Objective**

* Prove the AI pipeline end-to-end in the browser: chat with a course document.

**Backend**

* Demo deployment config; top integration bug fixes.

**AI/ML & Data**

* RAG iteration on golden-set failure cases; select validated demo questions.

**Frontend**

* Chat polish: empty/loading/error states, mobile check.

**DevOps/QA**

* **Gate 1 review checklist** (AI pipeline proven end-to-end); demo monitoring; staging smoke before demo; **v0.4.0 tag** after passing demo.

**Deliverables**

* v0.4.0 tag; signed Gate 1 checklist.

**Definition of Done**

* A user chats with an uploaded course document in the browser with visible citations; gate signed by TPM + pod leads.

### Week 17 — Full Student Flow E2E

**Objective**

* Wire the whole student journey: auth → enrollment → upload → chat.

**Backend**

* Enrollment → material → chat scoping; permission checks on chat sessions (owner/enrolled only).

**AI/ML & Data**

* Multi-document retrieval design (course-scoped corpora, per-document attribution).

**Frontend**

* Student flow polish; first-run onboarding basics (profile completeness prompt).

**DevOps/QA**

* Playwright E2E for the full student flow running in CI.

**Deliverables**

* Full-flow E2E test green on staging.

**Definition of Done**

* E2E: new user → enroll → upload → chat succeeds on staging; unauthorized access to another user's session returns 403.

### Week 18 — Multi-Document RAG + Tier 1 Contract Drafts

**Objective**

* Retrieval across a course's materials; draft the Tier 1 freeze contracts.

**Backend**

* Course-scoped retrieval + chat across multiple materials.

**AI/ML & Data**

* Multi-document retrieval with cross-document citations; expand multi-doc eval cases; **draft Tier 1 contracts** (OCR output schema, chunk schema, embedding I/O, retrieval contract, RAG request/response — TS §12/§18.4 discipline).

**Frontend**

* Multi-source citation rendering ("answer from documents A, B").

**DevOps/QA**

* Regression eval on multi-doc queries; contract review scheduling.

**Deliverables**

* Multi-doc RAG working on staging; Tier 1 contract drafts circulated.

**Definition of Done**

* A course-scoped query returns correctly attributed multi-document citations; contract drafts reviewed by A + B leads.

### Week 19 — Stabilization + Tier 1 Review

**Objective**

* Reduce defects and freeze-review readiness before the MVP gate.

**Backend**

* Top backend bugs; OpenAPI/spec corrections.

**AI/ML & Data**

* Top AI defects; golden Q&A set expansion; finalize `docs/rag.md` + OCR/chunking docs.

**Frontend**

* Top UI defects; v0.5 demo-flow polish.

**DevOps/QA**

* E2E re-run; coverage report against the NFR-10 trajectory (target ≥70% on core modules); Tier 1 review preparation.

**Deliverables**

* Zero P1 bugs open; Tier 1 contracts review-ready.

**Definition of Done**

* P1 count = 0; coverage measured in CI; review doc circulated 48h before Friday.

### Week 20 — v0.5 Full MVP + Tier 1 Freeze — GATE 2

**Objective**

* Freeze the AI-pipeline foundations and open the graduation runway.

**Backend**

* Tier 1 freeze sign-off; architecture diagram input (as-built).

**AI/ML & Data**

* Final RAG eval on the golden set (recorded); KG design prep (TS §13); demo backlog started (graduation beats).

**Frontend**

* v0.5 demo flow end-to-end.

**DevOps/QA**

* On-call rota; **v0.5.0 tag**; **Gate 2 sign-off**; demo backlog recorded.

**Deliverables**

* v0.5.0 tag; Tier 1 freeze signed; graduation runway opened.

**Definition of Done**

* Full student flow demoed live (register → enroll → upload → chat with citations); Tier 1 frozen; gate checklist signed.

### Week 21 — KG Schema + Storage ADR (light ramp into P3)

**Objective**

* Fix the knowledge-graph data model and storage path before building pipelines.

**Backend**

* KG API design skeleton (concepts/relations per material, TS §13).

**AI/ML & Data**

* **KG schema + storage ADR**: node/edge types `is-a` / `prerequisite-of` / `part-of` with provenance on every node/edge (TS §13.2); storage default **PostgreSQL-first** (relational/JSONB edges — ADR-0004 one-database philosophy, TS §13.3); extraction prompt design.

**Frontend**

* KG viz library research (Cytoscape.js vs D3 — the TS-intended choices, neither currently a dependency) with a recommendation.

**DevOps/QA**

* Document the storage decision path: PostgreSQL JSONB now; a dedicated graph store (e.g., Neo4j) only via a future ADR + a new PAL capability interface (TS §13.3) — no deployment scheduled.

**Deliverables**

* KG schema + storage ADR opened; viz recommendation recorded.

**Definition of Done**

* KG schema ADR in review with B + D leads; storage decision path documented (JSONB default, graph store as evidence-driven future ADR).

### Week 22 — Concept Extraction Spike

**Objective**

* Validate LLM-assisted concept extraction quality before productionizing.

**AI/ML & Data**

* Extraction spike via the reasoning provider (JSON mode, few-shot prompting per TS §13.2) on demo documents; sample-audited concept precision; ADR recommendation (extraction strategy + prompt versioning).

**Backend**

* Implement the chosen KG storage path (default: PostgreSQL JSONB per TS §13.3).

**Frontend**

* Concept detail wireframes; graduation outline v0 support.

**DevOps/QA**

* KG backup/monitoring plan.

**Deliverables**

* Spike report with measured extraction quality; storage ADR merged.

**Definition of Done**

* Spike reproducible (scripts + data committed); decision recorded in ADR; storage reachable from the worker.

### Week 23 — KG Pipeline + Population

**Objective**

* Turn extraction into a pipeline: documents in, concepts + relations stored.

**AI/ML & Data**

* Extraction pipeline worker (chunks → concepts + relations → KG store); concept dedupe/normalization (Arabic + English surfaces); provenance links to source chunks.

**Backend**

* KG API: `GET /knowledge-graph/{material_id}` (nodes/edges with provenance — TS §22.4).

**Frontend**

* Relations list view per material.

**DevOps/QA**

* KG worker observability (job metrics, failure alerts).

**Deliverables**

* The demo corpus yields a populated graph (concepts + relations + provenance).

**Definition of Done**

* KG populated from stored documents reproducibly; provenance resolvable to chunks; API returns a material's graph.

### Week 24 — KG API + KG Viz + Demo Dataset v1

**Objective**

* Make the knowledge layer visible and demoable.

**Backend**

* KG API final; KG ↔ material linkage checks; demo dataset v1 ingestion (demo PDFs → KG).

**AI/ML & Data**

* Extraction refinement from an error sample (misclassified relations); KG sanity checks (schema validation, cycle detection).

**Frontend**

* **KG viz UI**: browse concepts/relations per material (graph view + list).

**DevOps/QA**

* KG sanity tests in CI; KG data backup.

**Deliverables**

* Browsable KG in the UI; new upload populates KG end-to-end.

**Definition of Done**

* Upload → extract → graph visible for a new material; sanity tests green in CI.

### Week 25 — KG-Backed Retrieval Boost (low capacity — exam crunch 1)

**Objective**

* Evaluate prerequisite-aware retrieval expansion behind a flag.

**AI/ML & Data**

* KG-backed query expansion (TS §13.4) behind an eval harness; measure faithfulness/relevance delta on the golden set. Note: full mastery-gated expansion is adaptive-engine territory (§16) — this week evaluates the retrieval-side mechanism only.

**Backend**

* Expansion flag in the retrieval service (config-gated).

**Frontend**

* No major scheduled work.

**DevOps/QA**

* No major scheduled work.

**Deliverables**

* Recorded before/after eval on the golden set; keep-or-defer decision documented.

**Definition of Done**

* Decision (adopt/defer) backed by measured numbers; no regression when flag off.

### Week 26 — v0.6 Knowledge Layer + Quiz Foundations

**Objective**

* Tag the knowledge layer; start the generation track.

**Backend**

* Quiz schema + quiz API contract design (v1: static quizzes from materials; the CAT exam simulator remains a TS §16.5 target behind SKM/IRT, not v1 scope).

**AI/ML & Data**

* Quiz generation via the reasoning provider (`POST /questions/generate`, TS §22.4): MCQ with answer keys, Arabic + English; sampled answer-key validity review.

**Frontend**

* Quiz-taking UI scaffold.

**DevOps/QA**

* Generation cost/latency monitoring (NFR-2 — 10 MCQ < 30 s — is the target to benchmark against); **v0.6.0 tag** after passing demo.

**Deliverables**

* v0.6.0 tag; generated MCQ quiz from a stored material on staging.

**Definition of Done**

* Generated quiz validates against the quiz schema; tag cut after demo.

### Week 27 — SKM Foundations (low capacity — exam crunch 1)

**Objective**

* Stand up the Student Knowledge Model data layer (TS §14).

**Backend**

* Mastery schema migration (per student × concept records, TS §21.4 `SKM_RECORD` design) + service layer.

**AI/ML & Data**

* Mastery estimator v1 following the TS §14.2 evolution strategy (heuristic → weighted moving average; BKT later) + cold-start handling; **ADR: mastery estimation** (v1 estimator + BKT/IRT upgrade path).

**Frontend**

* Profile ↔ CSP field alignment check against TS §15 (no schema drift).

**DevOps/QA**

* No major scheduled work.

**Deliverables**

* Quiz attempt writes a mastery update; estimation ADR merged.

**Definition of Done**

* Attempt → mastery record update verified on staging; cold-start behavior documented.

### Week 28 — Quiz E2E + Mastery v1

**Objective**

* Close the first learning loop: take quiz → mastery changes → visible.

**Backend**

* Quiz attempt API + scoring contract; mastery update hook on attempt events.

**AI/ML & Data**

* Demo quiz pool (difficulty-tagged, answer keys verified) for the demo courses.

**Frontend**

* Quiz-taking flow complete; basic mastery indicator on the student side.

**DevOps/QA**

* E2E test: quiz → mastery update.

**Deliverables**

* Working quiz → mastery loop on staging.

**Definition of Done**

* A student takes a quiz; mastery records update; indicator reflects the change; E2E green.

### Week 29 — SKM Hardening + Adaptive Prep

**Objective**

* Decide the v1 mastery estimator and draft Tier 2 contracts.

**AI/ML & Data**

* BKT/IRT evaluation spike (pyBKT / py-irt — the TS §26.1 candidate libraries — on simulated + accumulated attempt data, TS §14.3–§14.4); measured comparison vs the v1 estimator; adopt only if the data supports it; **draft Tier 2 contracts** (KG schema, quiz schema, mastery schema, adaptive engine I/O).

**Backend**

* Recommendation API contract design (aligning with the §22.4 `recommendations`/`reviews` vocabulary); analytics query design.

**Frontend**

* Recommendation UI wireframes.

**DevOps/QA**

* Tier 2 freeze prep; attempt-data export for the spike.

**Deliverables**

* Estimator decision ADR with measured comparison; Tier 2 drafts circulated.

**Definition of Done**

* Decision recorded with numbers (adopt BKT/IRT or keep the v1 estimator and revisit); drafts out for review 48h before Friday.

### Week 30 — v0.7 Cognition + Tier 2 Freeze — GATE 3

**Objective**

* Freeze the cognition contracts and demo the learning loop.

**Backend**

* Tier 2 freeze sign-off; v0.7 demo support.

**AI/ML & Data**

* Seeded demo accounts with known mastery states.

**Frontend**

* v0.7 demo flow (quiz → mastery → profile).

**DevOps/QA**

* **v0.7.0 tag**; **Gate 3 sign-off**; demo-account verification check.

**Deliverables**

* v0.7.0 tag; Tier 2 freeze signed; seeded demo cohort.

**Definition of Done**

* Quiz → mastery → profile loop works on staging for all seeded accounts; Tier 2 frozen; gate signed.

### Week 31 — Adaptive Engine v1

**Objective**

* First adaptive recommendations from SKM + CSP fusion (TS §16).

**AI/ML & Data**

* Adaptive engine v1: candidate generation → prerequisite check → priority scoring → recommendation production (TS §16.2, thresholds calibrated during implementation); **SM-2 review scheduling** (TS §16.4); documented rule-based fallback if the engine underperforms (TS §28 fallback).

**Backend**

* `GET /recommendations/today` + `GET /reviews/scheduled` (TS §22.4 planned surface).

**Frontend**

* Recommendation UI ("Today's plan": next concepts + due reviews).

**DevOps/QA**

* Adaptation decision logging (inputs → decision, for later evaluation).

**Deliverables**

* Student receives a next-best-action derived from mastery + profile.

**Dependencies**

* W27–28 mastery loop; W21–24 KG prerequisite data (prerequisite check consumes the graph).

**Definition of Done**

* Recommendation reflects the student's mastery records and CSP availability; decisions logged; fallback path configurable.

### Week 32 — Review Schedule + Difficulty Adaptation

**Objective**

* Make quizzes and reviews respond to measured mastery.

**AI/ML & Data**

* SM-2 interval parameters tuned on demo data; mastery → quiz difficulty mapping.

**Backend**

* Adaptive quiz selection capability (serve items by difficulty band + concept) on the quiz contract.

**Frontend**

* Review queue UI; adaptive-quiz indicator.

**DevOps/QA**

* Integration checks: recommendation → UI; difficulty → served quiz.

**Deliverables**

* Quiz difficulty varies with mastery; review items resurface per schedule.

**Definition of Done**

* Two students with different mastery states receive different item bands; review due-dates honored by the queue; integration checks green.

### Week 33 — Adaptation Eval Harness

**Objective**

* Prove adaptation helps before stacking more on it.

**AI/ML & Data**

* Simulated learner trajectories through the engine; regression baseline; **HLR vs SM-2 evaluation** (TS §16.4 target — adopt only if measured better on the simulation; TS §28 records the fallback to fixed SM-2 intervals).

**Backend**

* Recommendation explanation field ("why this now": mastery gap, due review).

**Frontend**

* Recommendation polish using the explanation payload.

**DevOps/QA**

* Adaptation eval job (nightly) in CI.

**Deliverables**

* Eval harness reproducing the baseline; recorded HLR-vs-SM-2 comparison.

**Definition of Done**

* No regression on seeded learners; engine changes gated by the eval job; comparison documented.

### Week 34 — v0.8 Adaptation Release + Analytics Foundations

**Objective**

* Tag adaptation; start the analytics track.

**Backend**

* Analytics aggregation queries (cohort mastery, engagement, quiz outcomes) designed + benchmarked on seeded data.

**AI/ML & Data**

* v0.8 demo; IRT item-difficulty calibration from accumulated attempts (planned target — evaluate data sufficiency honestly before committing, TS §14.4); **CAT exam-simulator decision**: evaluate adaptive item selection (TS §16.5) against accumulated data — schedule post-v1.0 if deferred.

**Frontend**

* Instructor analytics dashboard start (charts shell).

**DevOps/QA**

* **v0.8.0 tag** after passing demo.

**Deliverables**

* v0.8.0 tag; instructor sees cohort mastery from real data.

**Definition of Done**

* Dashboard renders live cohort data; aggregation queries documented; tag cut after demo.

### Week 35 — Learning Analytics Dashboard

**Objective**

* Instructor-facing analytics on real cohort data.

**Backend**

* Analytics endpoints (`GET /analytics/dashboard`, `GET /analytics/heatmap` — TS §22.4) with role-gated access (instructor/admin).

**AI/ML & Data**

* Weak-area detection heuristics (mastery thresholds → alerts feed).

**Frontend**

* Dashboard UI covering the TS §20.3 analytics module scope (learning progress, concept mastery heatmap, study time distribution, exam readiness, goal tracking); admin dashboard scaffold.

**DevOps/QA**

* Dashboard E2E + permission tests.

**Deliverables**

* Instructor dashboard live on staging with real cohort data.

**Definition of Done**

* Instructors see only their courses' analytics; students cannot access instructor endpoints (403 verified); dashboard scope matches TS §20.3.

### Week 36 — Access Verification + Bug Bash #1

**Objective**

* Verify role-gated administration surfaces and run the first full defect sweep.

**Backend**

* RBAC/permission verification across role-gated surfaces (admin role capabilities on courses/users); P1 fixes.

**AI/ML & Data**

* Recommendation iteration from early feedback; quiz pool maintenance.

**Frontend**

* UX polish pass; instructor/student quickstart docs; graduation deck v1 to advisor.

**DevOps/QA**

* **Bug bash #1**: triage the defect backlog, P1s assigned with owners + target weeks.

**Deliverables**

* Role-gated access verified by tests; triage board complete.

**Definition of Done**

* All P1s have owners + target weeks; permission checks covered by tests.

### Week 37 — Bug Fixing + Accessibility + Demo Data

**Objective**

* Close P1s; verify accessibility and RTL-readiness; finalize demo data.

**Backend**

* P1 closure; DB performance prep for the load test.

**AI/ML & Data**

* P1 closure; **demo dataset final**: golden RAG questions validated, quiz pool frozen, demo accounts verified.

**Frontend**

* P1 closure; **WCAG 2.1 AA pass** (axe + keyboard); **RTL-readiness audit** of tokens/layout (first step toward the NFR-8 bilingual/RTL target; full bilingual UI depth per scope).

**DevOps/QA**

* Accessibility validation in CI; demo data snapshot prep.

**Deliverables**

* Zero P1 open; axe-clean report; frozen demo dataset list.

**Definition of Done**

* P1 count = 0; accessibility checks pass in CI; demo data catalog committed.

### Week 38 — v0.9 + Feature Freeze — GATE 4

**Objective**

* Freeze the feature set and lock demo data.

**Backend**

* Feature-freeze sign-off; demo data export.

**AI/ML & Data**

* v1.0 AI baselines recorded (RAG eval, quiz generation quality, adaptation baseline).

**Frontend**

* v0.9 demo polish.

**DevOps/QA**

* Coverage gate check toward NFR-10 (target ≥70% on core modules, measured in CI); demo snapshot + restore test; **v0.9.0 tag**; **Gate 4 sign-off**.

**Deliverables**

* v0.9.0 tag; Feature Freeze active; restore-tested demo snapshot.

**Definition of Done**

* Gate checklist signed; coverage status recorded vs the NFR-10 target; snapshot restore verified on a clean environment.

### Week 39 — Performance Pass (low capacity — exam crunch 2)

**Objective**

* Measure the system against TS §25.1 targets and fix what the numbers expose.

**Backend**

* Query optimization (N+1 elimination, index review, connection-pool tuning); pgvector ANN index evaluation against measured recall/latency (TS §25.3 — index choice benchmarked, not assumed).

**AI/ML & Data**

* RAG latency profiling vs **NFR-1** (<3 s end-to-end — a target to benchmark against, not a claim); NFR-2 check (10 MCQ < 30 s) on the generation path; embedding/OCR throughput checks.

**Frontend**

* Frontend performance audit (Lighthouse baseline; bundle/image budgets set from the audit).

**DevOps/QA**

* **k6 load test vs NFR-4** (50 concurrent users on a single server — the TS target); measured-vs-target table committed; runbooks drafted (deploy, rollback, on-call).

**Deliverables**

* Load test executed with recorded results; top bottlenecks fixed or ticketed with owners.

**Definition of Done**

* Measured-vs-target table in `docs/` (no target restated as achieved); critical bottlenecks resolved or scheduled; runbooks reviewed.

### Week 40 — Security Review + Dry-Run #0

**Objective**

* Independent security pass and the first full rehearsal.

**DevOps/QA**

* OWASP top-10 review; dependency/SAST scan; secrets audit (no credentials in repo/env files); Keycloak realm config review (clients, roles, token lifetimes — NFR-6 checklist); transport-security review (no reverse proxy deployed today — document the ingress TLS posture per TS §24.3); **dry-run #0** (internal demo rehearsal).

**Backend**

* Auth hardening fixes; rate-limiting decision on public and AI-cost-bearing endpoints (TS §24.3).

**AI/ML & Data**

* Prompt-injection review of the RAG chain; PII handling check in logs/traces (minimum-data principle, TS §9.3).

**Frontend**

* Security fixes; token/session storage review per the Keycloak integration doc.

**Deliverables**

* Security report with zero high vulnerabilities open; dry-run #0 completed with notes.

**Definition of Done**

* Findings triaged (fix now vs deferred with owner); dry-run feedback turned into tickets.

### Week 41 — Docs + DR Drill + Bug Bash #2

**Objective**

* Documentation, disaster recovery, and the final defect sweep.

**DevOps/QA**

* **DR drill** (restore from backup with a documented recovery target); runbooks final (deploy, rollback, DR, on-call); **bug bash #2** (P1 count driven toward zero); NFR-8 bilingual/RTL verification pass (UI across en/ar); deployment-mode documentation pass: record the hybrid preset (current staging shape) and the target local/cloud presets per TS §9.1/§23.3 — no invented services; one-command compose check vs NFR-9.

**Backend**

* Bug-bash #2 fixes; final ADR index + as-built architecture diagram update; API reference final.

**AI/ML & Data**

* Bug-bash #2 fixes; v1.0 AI baselines finalized (RAG eval, quiz quality, adaptation baseline).

**Frontend**

* Bug-bash #2 fixes; fallback demo video final.

**Deliverables**

* DR drill report; runbooks merged; updated architecture diagram; deployment-mode docs.

**Definition of Done**

* DR restore demonstrated end-to-end; docs match deployed reality; fallback demo video recorded.

### Week 42 — v1.0-rc + Code Freeze — GATE 5

**Objective**

* Cut the release candidate and freeze the code.

**DevOps/QA**

* Prod-like smoke suite (all critical paths); **dry-run #1 with advisor**; **v1.0-rc tag**; **Code Freeze sign-off** — only rc-critical fixes accepted after this point.

**Backend**

* rc-critical fixes only.

**AI/ML & Data**

* rc-critical fixes only.

**Frontend**

* Demo flow polish; presentation deck v2 draft.

**Deliverables**

* v1.0-rc tag; signed Gate 5 checklist; advisor feedback incorporated.

**Definition of Done**

* All critical paths green on prod-like environment; freeze active; demo data frozen (no changes).

### Week 43 — Production Deployment

**Objective**

* Go live on the production environment.

**DevOps/QA**

* Prod host provisioning; **one-command compose deployment** (NFR-9 target); monitoring/alerting validated on prod; prod smoke checks.

**Backend**

* Migrations applied to prod DB; demo data seeded.

**AI/ML & Data**

* Prod AI verification: gateway budget guard, OCR, embeddings, RAG eval spot-check on prod.

**Frontend**

* Prod verification; slide deck v2.

**Deliverables**

* v1.0-rc live on the production URL with monitoring.

**Definition of Done**

* Prod smoke green; alerts firing to the on-call channel; rollback path tested.

### Week 44 — v1.0 + Graduation

**Objective**

* Ship v1.0 and deliver the graduation presentation.

**DevOps/QA**

* **Dry-run #3 (dress rehearsal)**; artifact submission; on-call during the presentation.

**Backend**

* v1.0 verification standby.

**AI/ML & Data**

* AI-depth section of the presentation; live-system verification.

**Frontend**

* Demo flow final; presentation support.

**Deliverables**

* **v1.0.0 tag**; graduation presentation delivered; final docs + demo video submitted.

**Definition of Done**

* Presentation delivered with the live system; v1.0.0 tagged; project artifacts archived.

---

## 6. Milestone / Release Summary

| Milestone | Week | Purpose | Key deliverable |
| --- | --- | --- | --- |
| v0.1 | W4 (done) | Skeleton + governance | CI, ADRs 1–5, deploy paths, first tag |
| v0.2 | W8 | Foundations closed | Keycloak auth + courses + async pipeline wired, E2E green |
| v0.3 | W12 | Ingestion | Upload → OCR → chunk → embed → searchable |
| v0.4 — Gate 1 | W16 | Thin MVP | In-browser chat with citations on one document |
| v0.5 — Gate 2 | W20 | Full MVP + Tier 1 freeze | Full student flow + frozen AI-pipeline contracts |
| v0.6 | W26 | Knowledge layer | KG populated + browsable; quiz generation v1 |
| v0.7 — Gate 3 | W30 | Cognition + Tier 2 freeze | Quiz → mastery loop; SKM contracts frozen |
| v0.8 | W34 | Adaptation | Adaptive recommendations + review scheduling |
| v0.9 — Gate 4 | W38 | Analytics + feature freeze | Instructor analytics; coverage gate check; frozen features |
| v1.0-rc — Gate 5 | W42 | Hardening + code freeze | Security/load/DR complete; rc tagged |
| v1.0 | W44 | Graduation | Production deployment + presentation |

---

## 7. Cross-Pod Dependencies

| Dependency | From → To | Week | Contract surface |
| --- | --- | --- | --- |
| Presigned upload + materials API | A → C | W6–7 | Material status values; upload URL flow |
| Celery task chain | D (infra) → B (tasks) → A (API status) | W7 | Task routes, status transitions (`pending → processing → ready/failed`) |
| Provider imports in worker | B → D | W7 | PAL provider registration |
| Ingestion outputs → retrieval | B → A | W10 | Chunk/vector schema (Tier 1) |
| Retrieval/rerank contracts | B → A → C | W13 | `RankingInterface`, retrieval contract |
| Reasoning via LiteLLM | B (prompt/eval) → D (gateway ops) | W14 | PAL reasoning adapter, gateway config, budget guard |
| Chat/sessions API | A → C | W15 | Session schema, ADR-0009 WS event protocol |
| Tier 1 contracts (OCR/chunk/embedding/retrieval/RAG) | B + A → all | W20 | Frozen schemas |
| KG schema + API | B → A → C | W21–24 | Node/edge schema (Tier 2); `GET /knowledge-graph/{material_id}` |
| Quiz + mastery schemas | B → A → C | W26–28 | Quiz schema, mastery records (Tier 2) |
| Adaptive engine I/O | B → A → C | W31–32 | Recommendation/review contract (Tier 2; §22.4 paths) |
| Analytics endpoints | A → C | W35 | Role-gated analytics API (§22.4 paths) |
| Environments, CI gates, backups, DR | D → all | Continuous | CI checks; runbooks |

---

## 8. Critical Path

| # | Node | By | Why critical |
| --- | --- | --- | --- |
| 1 | Async ingestion chain wired (upload → targeted OCR → chunk → embed → pgvector) | W7 | Everything in P2 consumes its outputs |
| 2 | Vector retrieval service + filters | W10 | Prerequisite for hybrid, RAG, chat |
| 3 | Hybrid retrieval + reranker | W13 | Retrieval quality gate before RAG |
| 4 | Reasoning traffic via LiteLLM + RAG v1 | W14 | Blocks thin MVP (Gate 1) |
| 5 | Streaming chat (v0.4) | W16 | Gate 1 demo capability |
| 6 | Full student flow E2E (v0.5) | W20 | Gate 2; Tier 1 freeze anchor |
| 7 | KG pipeline + API/viz | W23–24 | Feeds retrieval boost + prerequisite-aware adaptation |
| 8 | SKM mastery loop (quiz → mastery) | W27–28 | Prerequisite for adaptive engine |
| 9 | Adaptive engine v1 + eval | W31–33 | Blocks v0.8 and demo narrative |
| 10 | Analytics on real data | W34–35 | Gate 4 content |
| 11 | Load/security/DR hardening | W39–41 | Gate 5 prerequisites |
| 12 | Production deployment | W43 | v1.0 |

Slack guidance: W25–W27 and W39–W40 are intentionally light (exam crunches); if P2 slips, recover inside W21–24 before the P3 ramp — do not push into crunch weeks.

---

## 9. Risks / Gaps / Assumptions

| Risk / Gap | Impact | Mitigation / planned action |
| --- | --- | --- |
| OCR quality on low-grade scanned Arabic | Wrong chunks poison RAG silently | Gemini OCR current; golden-set benchmark (W9, ADR-0003 methodology) gates ingestion; local engine only via the ADR-0003 benchmark process; worst case: text-native PDFs only (TS §28) |
| RAG quality (grounding, citations) | Credibility risk at Gate 1/2 | Golden Q&A eval from W14; nightly eval job; failure-case iteration loop (W16, W19); citation grounding + structured output + confidence handling are §12.2 requirements, not optional |
| Pod B capacity (2 people carry the whole AI track) | Single point of failure on the critical path | Descope/defer within pod early (W5 lesson); heavy AI weeks paired with light C/D work; cross-training (W8) |
| Week-5-style slip repeats on frontend-heavy weeks | Cascading carry-overs | Thursday merge cutoff enforced; carry-forward made explicit in weekly emails, not hidden |
| pgvector at demo scale is fine, but vector growth unbounded | Retrieval latency drift | Index + filter discipline (W10); ANN index choice benchmarked, not assumed (W39, TS §25.3); document upgrade path (dedicated store only on measured evidence, ADR-0004) |
| Embedding model swap mid-project | Dimension drift breaks retrieval silently | Dimension fixed at 1024 and validated at the PAL boundary; any model change treated as an explicit dimension migration — a schema event, not a config flip (TS §12.1) |
| LiteLLM spend/budget | Gateway throttles product features | Budget guard + alerts (W14); fallback chain (`gpt-4o-mini` → `gpt-3.5-turbo`) already configured |
| Keycloak staging drift (realm/client config, dev 26.7.3 vs staging `latest`) | Auth breakage mid-phase | Realm config reviewed W40; align versions; config-as-documentation; smoke checks include auth |
| WebSocket scope creep in W15 | Chat milestone slip | WS first (ADR-0009 transport) with documented SSE fallback decision; thin MVP needs REST-level reliability only |
| KG extraction noise / storage overhead | Dirty graph misleads adaptation | Few-shot prompting + post-filtering (TS §28); PostgreSQL JSONB default keeps ops cost near zero; dedicated graph store only via future ADR + new PAL interface |
| BKT/IRT data insufficiency | Adaptive quality claims outrun the data | Evolution strategy starts heuristic (TS §14.2); BKT/IRT adopted only on measured evidence (W29); CAT deferred unless data supports it (W34) |
| Bilingual UI expectations vs v1.0 scope | Stakeholder mismatch | Arabic-capable pipeline validated W9; RTL + bilingual verification vs NFR-8 (W37/W41); depth beyond that explicitly post-v1.0 |
| Exam crunches (W25–27, W39–40) collapse capacity | P3/P5 slip | Light weeks pre-planned; buffer absorbed in W21–24 and W37 |
| Multimodal (speech/vision) never scheduled | Vision gap at graduation | Explicitly stretch/post-v1.0 (TS §29.3); revisit at Gate 3 with capacity data |
| Team-member loss | Critical-path stall | Cross-training W8+; contracts + ADRs keep knowledge transferable |

---

## 10. Roadmap → Technical Specification Traceability

| Roadmap area | Weeks | TS reference |
| --- | --- | --- |
| Eight system layers & target learning loop | W7+ execution order | TS §2.3, §6, §17 |
| Hybrid AI / provider philosophy | W7, W14, W41 | TS §7, §9, §10 |
| PAL (five interfaces + base, factory, fallback, health) | W7, W13, W14 | TS §8 |
| Ingestion, targeted OCR, chunking | W7–9 | TS §11 |
| Knowledge pipeline (retrieval → RAG) | W10–20 | TS §12 |
| Knowledge graph | W21–25 | TS §13 |
| Student Knowledge Model (heuristic → BKT/IRT) | W27–30 | TS §14 |
| Student profile (6-field subset → CSP) | W6 (done), W27 | TS §15 |
| Adaptive engine (SM-2/HLR, CAT decision) | W26, W31–34 | TS §16 |
| Modular monolith / backend / API surface | W7–17 | TS §18, §19, §22 |
| Frontend architecture & modules | W7–17, W34–37 | TS §20 |
| Database & pgvector | W3 (done), W10–11 | TS §21 |
| Infrastructure & deployment modes | W7, W39–43 | TS §23 |
| Security & privacy | W40 | TS §24 |
| Performance / NFR benchmarks | W9, W26, W38–39 | TS §25 |
| Technology stack | Continuous (see §2 rules) | TS §26 |
| Research foundations & graduation value | W22, W29, W33; W44 | TS §27, §29, §30 |

---

## 11. Weekly Email Generation Rule

1. Take **Week N + pod** from §5: the pod's bullets become the email's task list, one task per bullet, verbatim.
2. Copy the week's **Deliverables** as "expected outputs" and **Definition of Done** as the checklist; include **Dependencies** whenever listed.
3. For W1–6 weeks, prefix the historical **Status** line; for milestone weeks, add the milestone line from §6. Never restate architecture — link the TS section from §10 when context is needed.
