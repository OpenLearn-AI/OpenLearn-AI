# 44-Week Engineering Execution Plan

**Project:** OpenLearn AI — Adaptive Educational Intelligence Platform
**Planning Horizon:** 44 weeks · 3 August 2026 → 6 June 2027
**Document Type:** Engineering Execution Plan (weekly, per-Pod)
**Source Documents:** `MASTER_ROADMAP.md` v1.0 (SSOT for scope/timeline) · `OpenLearn_AI_v4_Technical_Specification.md` v4.0 (SSOT for architecture)
**Audience:** Pod A (Backend, 2 engineers) · Pod B (AI/ML, 3 engineers) · Pod C (Frontend, 2 engineers) · Pod D (DevOps/QA/Eval, 2 engineers) · TPM
**Repo Path:** `44-WEEK-EXECUTION-PLAN.md` (repo root)
**Review Cadence:** Weekly sprint planning (Monday); Friday demo + retro; monthly milestone review (last Friday)

---

## 1. Executive Summary

This document is the **operational weekly execution plan** for OpenLearn AI across the full 44-week delivery cycle. It is built by fusing two authoritative project documents — the **Master Roadmap** (scope, phases, milestones, releases, risks, capacity) and the **Technical Specification v4.0** (eight-layer architecture, Provider Abstraction Layer, AI/ML algorithms, data models, NFRs) — and decomposing each roadmap-level deliverable into concrete engineering tasks owned by one of four Pods.

OpenLearn AI is an AI-powered adaptive learning platform: a student or instructor uploads PDFs, the platform runs OCR + chunking + embedding, builds a RAG layer with citations, extracts concepts into a Knowledge Graph, models each student's cognitive state from quiz performance using Bayesian Knowledge Tracing, and uses that model to drive personalized recommendations and adaptive quiz difficulty. The system follows a **Hybrid AI / Provider-Agnostic** architecture: every AI component (reasoning, embedding, OCR, vector DB, ranking, speech, vision) is reached through a standardized interface in the Provider Abstraction Layer, so providers can be swapped via configuration.

### 1.1 The Four Pods

| Pod | Headcount | Lead | Primary Ownership |
|---|---|---|---|
| **A — Backend & Platform** | 2 | Backend Lead | Auth, user mgmt, course CRUD, file upload, document ingestion API, search API, chat API (SSE/WS), KG API, quiz API, recommendation API, analytics aggregation, admin API, PostgreSQL/Alembic, Qdrant vector DB ops |
| **B — AI/ML & Data** | 3 | AI Lead | OCR pipeline, chunking, embedding model serving, hybrid retrieval, reranker, RAG prompt assembly, RAG eval harness, concept extraction, Knowledge Graph construction, quiz generation, cognitive model (BKT/IRT), adaptive engine, recommendation engine v1 |
| **C — Frontend & UX** | 2 | Frontend Lead | Next.js 16 App Router, Tailwind CSS 4, shadcn/ui, design tokens, Storybook, all student/instructor/admin UI, accessibility (WCAG 2.1 AA on critical paths), demo polish |
| **D — DevOps / QA / Eval** | 2 | DevOps/QA Lead | GitHub Actions CI/CD, dev/staging/prod environments, monitoring (Grafana + Prometheus + Loki + OpenTelemetry + Sentry), ML eval harness, SLOs, security review, performance/load tests, backup/DR drills, runbooks |

The **firefighter**, **TPM**, and **Docs Owner** are rotating roles drawn from the 9 engineers; they are not additional headcount.

### 1.2 The Five Quality Gates

The plan is anchored on five hard pass/fail gates. Every weekly task list is designed so that the relevant gate can be signed on or before its target date.

| Gate | Week | Anchor | Slack to Graduation |
|---|---|---|---|
| G1 — v0.4 Thin MVP | W16 | Pre-loaded PDF + chat UI (no auth); cited answer in browser | Early warning; if missed, PB-06 triggers |
| G2 — v0.5 + Tier 1 Architecture Freeze | W20 | Full MVP; ADRs 1–15; 5 Tier 1 interface contracts frozen | 1 week |
| G3 — v0.7 + Tier 2 Architecture Freeze | W30 | Quiz + mastery + KG end-to-end; 4 Tier 2 contracts frozen | 2 weeks |
| G4 — v0.9 + Feature Freeze | W38 | Dashboards; coverage ≥ 60% on critical paths; 3 people cross-trained on DevOps | 1 week |
| G5 — v1.0-rc + Code Freeze | W42 | Perf + security + DR drill + runbooks complete | Hard (0 weeks) |
| Final — v1.0 | W44 | Production deployment + graduation presentation | Hard (0 weeks) |

### 1.3 The Critical Path

```
Stack lock (W1) → OCR (W9–W10) → Chunking (W11) → Embeddings (W12) → Vector DB (W13) → RAG (W14–W15)
  → v0.4 Thin MVP (W16) → Full student flow (W17–W18) → Tier 1 Freeze (W20)
    → Concept extraction (W23) → KG (W24) → Cognitive model spike (W25–W27) → Cognitive model impl (W28)
      → Tier 2 Freeze (W30) → Adaptive spike (W29–W31) → Adaptive engine (W31–W33)
        → Feature Freeze (W38) → Hardening (W39–W41) → Code Freeze (W42) → Prod deploy (W43) → Graduation (W44)
```

Critical-path slack totals **~4 weeks**, distributed (not concentrated at the end). Any slip on the critical chain consumes this slack; when slack is exhausted on a segment, the descope protocol or a scoped fallback (F-1 … F-7) triggers automatically.

### 1.4 How to Use This Document

- **Every Monday:** Pod leads review the current week's section (Week X) for their Pod, confirm task ownership, and surface blockers in the cross-pod Tuesday sync.
- **Every Friday:** Demo the week's `Expected Output` artifacts on staging (not localhost). Sprint exit checks the `Definition of Done` for each Pod and the `Week X Definition of Done`.
- **When a task depends on another Pod:** consult the `Dependencies` and `Handoff` fields, then the **Cross-Pod Handoff Matrix** (Section 11).
- **When a roadmap milestone is referenced:** consult **Section 12 (Milestone → Task Traceability)** to see which weeks and Pods contribute.
- **When a release is being prepared:** consult **Section 13 (Release Execution Plan)**.
- **When in doubt about a technical decision:** the Technical Specification v4.0 is the architectural authority; the Master Roadmap is the scope/timeline authority. See **Section 2** and **Section 16** for conflict resolution.

This plan is **not** a re-statement of the roadmap. It is the engineering decomposition: each roadmap-level milestone is broken into the API contracts, schemas, jobs, prompts, UI states, tests, and infrastructure tasks that make it shippable, with explicit Pod ownership and inter-Pod handoffs.

---

## 2. Source Documents & Planning Authority

This execution plan is derived from two source documents with **distinct, non-overlapping authorities**. When the two documents address the same topic, the table below determines which is binding.

### 2.1 Authority Assignment

| Topic | Primary Authority | Secondary / Reference |
|---|---|---|
| Project phases, week-by-week windows | **Master Roadmap** | — |
| Version roadmap (v0.1 → v1.0) and target dates | **Master Roadmap** | — |
| Quality gates (G1–G5) and sign-off criteria | **Master Roadmap** | — |
| Out-of-Scope list (15 items, signed at kickoff) | **Master Roadmap** | Tech Spec's broader vision is post-v1.0 |
| Capacity model (1,820 usable hours) | **Master Roadmap** | — |
| Pod structure, headcount, rotating roles | **Master Roadmap** | — |
| Risks (R-01 … R-32), playbooks (PB-01 … PB-06), fallbacks (F-1 … F-7) | **Master Roadmap** | Tech Spec's risk register overlaps |
| Sprint timeline (sprint name, owner, deliverable, exit criterion per week) | **Master Roadmap** | — |
| Integration milestones (IM-1 … IM-15) | **Master Roadmap** | — |
| Eight-layer system architecture | **Technical Specification** | — |
| Provider Abstraction Layer (7 interfaces) | **Technical Specification** | Roadmap mentions LiteLLM gateway as the PAL implementation |
| AI/ML algorithm choice (BKT, IRT, SM-2, Half-Life Regression) | **Technical Specification** | Roadmap constrains *when* (rolling average first; IRT in v0.8 if data supports) |
| SKM evolution strategy (v0.5.0 heuristic → v0.5.1 WMA → v0.5.2 BKT) | **Technical Specification** | Roadmap's "rolling average v1" = Tech Spec's v0.5.1 WMA stage |
| Data models, ER schema, API endpoints | **Technical Specification** | — |
| NFR-1 … NFR-10 | **Technical Specification** | Roadmap's stricter targets (P95 < 2s vs NFR-1's < 3s) win for graduation gates |
| Hybrid AI / Local-First / Cloud-Optional philosophy | **Technical Specification** | Roadmap's "production-grade single-URL deploy" is the v1.0 reality; Local-First is a Tech Spec design principle that informs architecture but does not change the deployment topology |
| Three deployment configurations (Local / Hybrid / Cloud Docker Compose profiles) | **Technical Specification** | — |
| Tech stack component choices | **Master Roadmap** (binding) | Tech Spec's "Recommended Stack" table is aspirational; conflicts listed below |

### 2.2 Detected Conflicts and Resolution

The two source documents are mostly consistent, but several conflicts were identified during planning. Each is resolved explicitly so the four Pods have a single, unambiguous instruction.

| # | Conflict | Roadmap Position | Tech Spec Position | Resolution (binding for this plan) |
|---|---|---|---|---|
| C-1 | **Vector DB choice** | Qdrant (self-hosted, single node); pgvector is fallback F-1 | ChromaDB (embedded) is the default | **Qdrant wins** (Roadmap authority for stack). ChromaDB remains the documented fallback pattern; Pod D maintains Qdrant and the F-1 swap path. |
| C-2 | **Default LLM provider** | LiteLLM proxy in front of OpenAI / Anthropic / GLM (cloud-first for production) | Ollama + Qwen 2.5 7B local-first | **Both**: LiteLLM gateway is the implementation of the PAL `ReasoningInterface`. Local Ollama + Qwen 2.5 is configured for development and demo predictability; cloud providers (OpenAI/Anthropic/GLM) are wired through LiteLLM for production quality. The PAL priority chain lets the system fall back from cloud to local on rate-limit. |
| C-3 | **Embedding default** | BGE-M3 self-hosted (with OpenAI text-embedding-3-small as F-3) | BGE-M3 (BAAI/bge-m3) via Sentence Transformers, 1024-dim | **Aligned** — BGE-M3 is the v1.0 default, 1024-dim. F-3 swap is to OpenAI text-embedding-3-small. No conflict. |
| C-4 | **Test coverage target** | ≥ 60% on critical paths (Feature Freeze gate, TM-11) | ≥ 70% on core modules (NFR-10) | **Roadmap wins** for graduation gate (60% on critical paths). Pod D targets 70% on core modules as the internal stretch; 60% is the gate. |
| C-5 | **RAG latency target** | P95 < 2s on RAG under 50 concurrent users (Engineering Success #5, TM-12) | NFR-1: < 3s end-to-end (single user) | **Roadmap wins** as the stricter, gate-bearing requirement (P95 < 2s @ 50 users). NFR-1's 3s single-user target is a relaxed lower bound used only for non-load scenarios. |
| C-6 | **User roles** | Student, instructor, admin (3 roles) | Student, Teacher, Admin, Guest, Contributor (5 roles) | **Roadmap wins** for v1.0 scope: 3 roles ship. Guest and Contributor are post-v1.0 per the Tech Spec's "Future Vision" and are not in the v1.0 plan. Pod A's RBAC middleware enforces only 3 roles. |
| C-7 | **Arabic / multilingual UI** | OOS-11: English only in v1.0; Arabic/French in v2.0 | Central vision: Arabic+English bilingual, full RTL | **Roadmap wins** for **product UI** (English-only in v1.0). **However**, the **content pipeline** (OCR, embeddings, LLM, RAG) MUST still handle Arabic content because (a) the Tech Spec's recommended models (BGE-M3, PaddleOCR, Qwen 2.5) are multilingual and chosen specifically for Arabic quality, and (b) demo data may include Arabic PDFs. The UI shell is English-only; the backend is Arabic-capable. Flagged in Section 16. |
| C-8 | **Recommendation engine v2** | v1 only (rule-based + simple content-based); v2 features (peer recommendations, collaborative filtering) explicitly out of scope (OOS-6) | Tech Spec describes richer peer/content recommendations as core to the Adaptive Engine | **Roadmap wins**: v1.0 ships rule-based + content-based only. The Adaptive Engine produces "next-best-concept" recommendations; peer/collaborative filtering is deferred. |
| C-9 | **IRT integration timing** | Roadmap: "IRT v0.8 if data supports" — conditional, gated on quiz data volume | Tech Spec: IRT is part of the SKM v0.5.2 stage alongside BKT | **Hybrid**: Pod B builds IRT scaffolding (the `py-irt` integration, the question-difficulty table) by W30 as part of Tier 2 freeze deliverables. **IRT is activated in v0.8 (W34) only if quiz data volume supports parameter estimation** (≥ 5 interactions per question). If insufficient data: IRT stays dormant, CAT uses a simplified Easy → Medium → Hard sequential progression (Tech Spec primary fallback). |
| C-10 | **Auth implementation** | Self-hosted JWT + refresh tokens (`fastapi-users` or `supertokens`); Google OAuth | JWT + bcrypt (12 rounds) + optional OAuth; 5 roles | **Aligned**: Pod A implements JWT + refresh + Google OAuth + bcrypt(12). `fastapi-users` library is the implementation base. 3 roles (per C-6). |
| C-11 | **Orchestration** | Docker Swarm or k3s — **NOT full K8s** | Docker Compose only (single-node) | **Roadmap wins**: Docker Compose for dev/staging; k3s for prod (single node). Pod D does not deploy full Kubernetes. |
| C-12 | **Analytics dashboard depth** | 4 chart types, 30-day window (structural descope) | Full dashboard (heatmap, readiness, time distribution, goal tracking) | **Roadmap wins** for v1.0: 4 chart types, 30-day window. Pod C implements 4 charts; the Tech Spec's full chart list is the post-v1.0 target. |
| C-13 | **Mobile responsiveness** | Desktop-first; mobile best-effort (OOS-8) | Not emphasized | **Aligned**: desktop-first. Pod C ensures no horizontal scroll on tablet; mobile is best-effort, not a tested target. |

Conflicts that cannot be confidently resolved are flagged in **Section 16 (Gaps & Ambiguities)** rather than silently resolved.

### 2.3 Conflict Resolution Protocol (for conflicts that emerge during execution)

1. Pod lead detects the conflict and opens a GitHub issue tagged `roadmap-spec-conflict`.
2. TPM triages within 3 business days; assigns authority per the table above.
3. If authority is unclear, TPM escalates to a T2 decision (TPM + 2 pod leads; max 1 week).
4. Resolution is recorded as an ADR (`docs/adr/`) and noted in the next Revision History entry.
5. The Pod that owns the affected task updates its task list and re-estimates impact.

---

## 3. Project Architecture & Execution Context

This section gives every Pod lead a shared mental model of the system they are building. It is condensed from the Technical Specification v4.0 (Sections 6–17) and the Master Roadmap (High-Level Architecture).

### 3.1 Eight-Layer System Architecture

OpenLearn AI is structured as **eight interdependent layers** forming a closed feedback loop. Each Pod's work touches multiple layers; the table below maps each layer to its primary Pod and the roadmap phase where it ships.

| Layer | Purpose | Primary Pod | Tech Spec Components | Ships By |
|---|---|---|---|---|
| L1 — Content Ingestion | PDF/DOCX/PPTX/image upload; text extraction; OCR; semantic chunking | Pod B (algorithm) + Pod A (API/jobs) + Pod D (infra) | PyMuPDF, PaddleOCR + Tesseract + Document AI (F-6), unstructured.io, semantic chunker | v0.3 (W12) |
| L2 — Knowledge Base (RAG) | Embeddings; vector store; hybrid retrieval; reranker; RAG generation with citations | Pod B (algorithm) + Pod A (search API, chat API) + Pod D (Qdrant ops) | BGE-M3 (1024-dim), Qdrant (F-1: pgvector), BM25, bge-reranker-v2-m3, LiteLLM gateway | v0.4 Thin MVP (W16), v0.5 Full MVP (W20) |
| L3 — Knowledge Graph | Concept extraction; is-a / prerequisite-of / part-of relations; provenance; prerequisite-aware query expansion | Pod B (extraction algorithm) + Pod A (KG API) + Pod D (Neo4j ops) | LLM-assisted extraction (JSON mode), Neo4j (F-2: JSONB in PG), NetworkX (dev) | v0.6 (W26) |
| L4 — Student Knowledge Model (SKM) | Per-(student, concept) mastery tracking; BKT 4-parameter model; IRT for question difficulty; cold-start heuristic | Pod B (algorithm) + Pod A (mastery schema, API) | pyBKT, py-irt, evolution strategy (heuristic → WMA → BKT) | v0.7 (W30) |
| L5 — Customized Student Profile (CSP) | 13 profile fields: education level, major, goals, VARK style, preferred language, learning speed, available time, past results, mastery vector, interests | Pod A (storage) + Pod C (onboarding UI) + Pod B (auto-estimation fields) | CSP table; onboarding wizard; SKM ↔ CSP bidirectional feedback | v0.7 (W30) |
| L6 — Adaptive Learning Engine | Fuses SKM + CSP + KG to produce 4 decision types: concept selection, difficulty calibration, modality selection, scheduling (SM-2 + Half-Life Regression) | Pod B (engine) + Pod A (recommendation API) + Pod C (recommendation UI) | 4-step decision process; SM-2 scheduler; Half-Life Regression; rule-based fallback (F-7) | v0.8 (W34) |
| L7 — Generation & Simulation | MCQ / True-False / Fill-blank / Short-Answer generation; 4 summary types; flashcards; CAT exam simulator | Pod B (generation algorithm) + Pod C (quiz UI) + Pod A (quiz API) | LLM-generated MCQs with answer keys; CAT with IRT-driven item selection | v0.7 quiz (W30), v0.8 CAT (W34) |
| L8 — Learning Analytics | Cohort mastery, quiz pass rates, engagement, mastery heatmap, readiness scores, weak-area alerts (4 chart types, 30-day window) | Pod A (aggregation queries) + Pod C (dashboard UI) + Pod D (eval) | Recharts; instructor dashboard; analytics aggregation queries | v0.9 (W38) |

### 3.2 Provider Abstraction Layer (PAL)

The PAL is the architectural mechanism that makes the Hybrid AI philosophy operational. Pod B and Pod A **must** reach every AI provider through one of the 7 PAL interfaces; no core module imports a provider library directly.

| Interface | Methods | Default Provider | Cloud Fallback | Fallback ID |
|---|---|---|---|---|
| `ReasoningInterface` | `generate(prompt, context)`, `extract_concepts(text)`, `generate_questions(text, params)` | Ollama + Qwen 2.5 7B (local) | OpenAI / Anthropic / GLM via LiteLLM | — |
| `EmbeddingInterface` | `embed(text)`, `embed_batch(texts)` | BGE-M3 (local, 1024-dim) | OpenAI text-embedding-3-small | F-3 |
| `OCRInterface` | `extract_text(image)`, `extract_text_batch(images)` | PaddleOCR (local) | Google Document AI | F-6 |
| `SpeechInterface` | `synthesize(text)`, `transcribe(audio)` | Piper TTS + Whisper (local) | OpenAI TTS / Google Speech | — |
| `VectorDBInterface` | `store(vectors, metadata)`, `search(query_vector, top_k, filters)`, `delete(ids)` | Qdrant (self-hosted) | pgvector (PG extension) | F-1 |
| `VisionInterface` | `analyze(image, prompt)` | LLaVA / Qwen-VL (local) | GPT-4o Vision | — |
| `RankingInterface` | `rank(query, documents, top_k)` | bge-reranker-v2-m3 (local) | Cohere Rerank | — |

Each PAL interface implementation exposes a `health_check()` method. The PAL calls these periodically and routes traffic to the next provider in the configured priority chain on failure. Pod B implements the PAL; Pod A and Pod D integrate with it.

### 3.3 Three Execution Modes (Configuration Presets)

The Tech Spec defines three Docker Compose profiles. Pod D ships all three; production v1.0 uses **Hybrid mode** (local data + cloud LLM for quality).

| Mode | LLM | Embeddings | Vector DB | OCR | Storage | Use Case |
|---|---|---|---|---|---|---|
| Local | Ollama (local) | BGE-M3 (local) | Qdrant (local) | PaddleOCR (local) | MinIO (local) | Privacy-sensitive; offline; development |
| **Hybrid (v1.0 prod)** | Cloud (OpenAI/Anthropic/GLM via LiteLLM) | BGE-M3 (local) or OpenAI | Qdrant (local) | PaddleOCR (local) | MinIO (local) | v1.0 production deployment |
| Cloud | Cloud | Cloud | Cloud (Qdrant Cloud or pgvector) | Cloud (Document AI) | S3 | Constrained hardware |

### 3.4 Frozen Interface Contracts (the "10 Contracts")

These 10 contracts are frozen at their respective freeze dates. Post-freeze changes require a new ADR + migration plan + TPM approval + 2 pod leads' review. Every Pod must respect these contracts in code from the moment they are frozen.

| # | Contract | Frozen At | Owner |
|---|---|---|---|
| 1 | OCR output schema (extracted text + layout JSON) | W20 (Tier 1) | Pod B |
| 2 | Chunk schema (fields, metadata, IDs) | W20 (Tier 1) | Pod B |
| 3 | Embedding I/O (input text, output vector dim, model_id) | W20 (Tier 1) | Pod B |
| 4 | Vector DB query API (top-k, filters, payload) | W20 (Tier 1) | Pod A + Pod B |
| 5 | RAG request/response (query, filters, response with citations) | W20 (Tier 1) | Pod A + Pod B |
| 6 | KG concept/relation schema (node types, edge types, provenance) | W30 (Tier 2) | Pod B |
| 7 | Quiz schema (question types, metadata, scoring) | W30 (Tier 2) | Pod B + Pod A |
| 8 | Student mastery schema (per student-concept record) | W30 (Tier 2) | Pod B + Pod A |
| 9 | Adaptive engine I/O (input: student state; output: next action) | W30 (Tier 2) | Pod B |
| 10 | Auth token format (JWT claims, refresh flow) | W8 | Pod A |

### 3.5 Technology Stack (Binding for v1.0)

| Layer | Choice | Owner | Fallback |
|---|---|---|---|
| Frontend | Next.js 16 (App Router) + React 19 + TypeScript 5 + Tailwind CSS 4 + shadcn/ui + Zustand + TanStack Query | Pod C | — |
| Frontend charts | Recharts (analytics) + Cytoscape.js/D3.js (KG viz) | Pod C | — |
| Backend API | FastAPI (Python 3.12) + Pydantic v2 + Uvicorn + SQLAlchemy 2 + Alembic | Pod A | — |
| Primary DB | PostgreSQL 16 + JSONB + (pgvector as F-1) | Pod A | — |
| Vector DB | Qdrant (self-hosted, single node) | Pod D + Pod A | F-1: pgvector |
| Knowledge Graph | Neo4j Community Edition | Pod D + Pod B | F-2: JSONB in PG |
| LLM Gateway | LiteLLM proxy (front of OpenAI / Anthropic / GLM; Ollama for local dev) | Pod B + Pod D | F-4: cost-driven model swap |
| Embeddings | BGE-M3 (BAAI/bge-m3), 1024-dim, self-hosted | Pod B | F-3: OpenAI text-embedding-3-small |
| OCR | PaddleOCR (primary) + Tesseract (fallback) + Google Document AI (escalation) | Pod B | F-6: Document AI |
| Document parsing | unstructured.io + PyMuPDF | Pod B | — |
| Chunking / Retrieval | LangChain (orchestration) + BM25 hybrid + bge-reranker-v2-m3 | Pod B | — |
| Async jobs / queue | Redis 7 + Celery 5 | Pod D + Pod A | F-5: Inngest |
| Cache | Redis (shared with queue) | Pod A + Pod D | — |
| Object storage | MinIO (self-hosted) / AWS S3 in prod | Pod D | — |
| Auth | JWT + refresh tokens (`fastapi-users`) + Google OAuth + bcrypt(12) | Pod A | — |
| Containerization | Docker + Docker Compose (dev/staging); k3s (prod, single node) — **NOT full K8s** | Pod D | — |
| CI/CD | GitHub Actions | Pod D | — |
| IaC | Terraform (light) for prod infra | Pod D | — |
| Cloud provider | Hetzner (primary, cost) or AWS (ecosystem) | Pod D | — |
| Monitoring | Grafana + Prometheus + Loki + OpenTelemetry | Pod D | — |
| Error tracking | Sentry (free tier) | Pod D | — |
| LLM observability | Langfuse (open-source) | Pod D | — |
| Frontend analytics | PostHog (self-hosted) | Pod D | — |
| Feature flags | Unleash (self-hosted) or env vars | Pod D | — |
| Tests | pytest (backend), Vitest + React Testing Library (frontend), Playwright (E2E) | All pods | — |
| Docs | Docusaurus + Markdown ADRs in repo | TPM (Docs Owner rotation) | — |

### 3.6 Multi-Store Data Architecture

| Store | Purpose | Default Provider | Cloud Alternative | Access Pattern |
|---|---|---|---|---|
| PostgreSQL 16 | Relational data (users, courses, materials, chunks metadata, CSP, SKM records, quiz attempts, exam sessions, review items, goals) | Self-hosted | Supabase / managed PG | CRUD with complex joins |
| Qdrant | Vector embeddings + similarity search | Self-hosted (single node) | Qdrant Cloud / pgvector | Vector similarity + metadata filter |
| Redis | Task queue, cache, session data, pub/sub for WebSocket | Self-hosted | Redis Cloud | Key-value, pub/sub |
| MinIO / S3 | Original PDFs, images, extracted text, generated artifacts | MinIO (self-hosted) | AWS S3 | Large binary objects |
| Neo4j | Knowledge Graph: concepts, relations, prerequisites, provenance | Neo4j Community | Neo4j Aura / JSONB in PG | Graph traversal, pattern matching |

### 3.7 Key Non-Functional Requirements (NFRs)

The NFRs below are binding for v1.0. Where the roadmap imposes a stricter target than the Tech Spec, the roadmap wins (per Section 2.2).

| Code | Category | Requirement | Source | Owner |
|---|---|---|---|---|
| NFR-1 (strict) | Performance | RAG P95 < 2s under 50 concurrent users | Roadmap (Engineering Success #5, TM-12) | Pod A + Pod B + Pod D |
| NFR-2 | Performance | 10 MCQ generation < 30s | Tech Spec | Pod B |
| NFR-3 | Performance | 100-page PDF processing < 60s incl. OCR | Tech Spec | Pod B |
| NFR-4 | Scalability | 50 concurrent users on single server | Tech Spec + Roadmap | Pod D + Pod A |
| NFR-5 | Reliability | Uptime > 99% in production | Tech Spec | Pod D |
| NFR-6 | Security | bcrypt + HTTPS + JWT mandatory | Tech Spec + Roadmap | Pod A + Pod D |
| NFR-7 (relaxed for v1.0) | Privacy | 100% offline operation available | Tech Spec | Pod B (PAL) — Partial: production v1.0 uses Hybrid mode (cloud LLM). Offline mode is a documentation/descope target. |
| NFR-8 (scoped for v1.0) | Usability | English-only UI in v1.0; backend pipeline is Arabic-capable | Roadmap OOS-11 overrides | Pod C |
| NFR-9 | Maintainability | One-command deployment (Docker Compose) | Tech Spec | Pod D |
| NFR-10 (binding) | Test coverage | ≥ 60% on critical paths (gate); internal stretch 70% on core modules | Roadmap (TM-11 gate) + Tech Spec (stretch) | All pods |

### 3.8 Capacity Context

The plan is sized against **1,820 usable engineering hours** (pessimistic, after a 60% productivity multiplier). Phase-by-phase effective hours:

| Phase | Window | Active members (avg) | Hrs/wk per active | Effective hrs/wk |
|---|---|---|---|---|
| Pre-semester surge | Aug–Sep 2026 (8 wks) | 8.5 (–1 firefighter) | 16 | ~136 |
| Semester 1 | Oct 2026 – mid-Jan 2027 (15 wks) | 7.0 (–1 firefighter) | 8 | ~56 |
| Exam crunch 1 | Late Jan 2027 (3 wks) | 3.0 | 4 | ~12 |
| Semester 1 break | Feb 2027 (4 wks) | 6.5 | 11 | ~72 |
| Semester 2 (light) | Mar – mid-Apr 2027 (6 wks) | 7.0 | 8 | ~56 |
| Exam crunch 2 | Late Apr – early May 2027 (3 wks) | 3.0 | 4 | ~12 |
| Final push | Mid-May – Jun 2027 (5 wks) | 8.0 | 20 | ~160 |

Pod leads must plan tasks to fit these budgets. Weeks marked **"low-capacity"** (W25–W27 exam crunch 1, W39–W40 exam crunch 2) intentionally contain maintenance/buffer work, not new features.

---

## 4. Roadmap Phases & Milestones

### 4.1 The Seven Phases

| Phase | Name | Window | Weeks | Theme | Primary Pod | Exit Gate |
|---|---|---|---|---|---|---|
| **P0** | Pre-Flight | Aug 3 – Aug 30, 2026 | W1–4 | Setup, decisions, MVP definition, skeleton deploy | All pods | v0.1 deployed |
| **P1** | Foundations | Aug 31 – Sep 27, 2026 | W5–8 | Auth, courses, upload, UI shell | Pod A + Pod C | v0.2 deployed |
| **P2** | AI Pipeline | Sep 28 – Dec 20, 2026 | W9–20 | OCR → embeddings → RAG; v0.4 thin MVP at W16; v0.5 + Tier 1 Freeze at W20 | Pod B (with A + C) | **v0.5 + Tier 1 Architecture Freeze** |
| **P3** | Knowledge & Cognition | Dec 21, 2026 – Feb 27, 2027 | W21–30 | KG + quiz + cognitive model; research spike on cognitive model in W25–W27; Tier 2 Freeze at W30 | Pod B (light) | **v0.7 + Tier 2 Architecture Freeze** |
| **P4** | Adaptation & Analytics | Feb 28 – Apr 24, 2027 | W31–38 | Adaptive engine (research spike in W29–W31), dashboards; Feature Freeze at W38 | Pod B + Pod C | **v0.9 + Feature Freeze** |
| **P5** | Hardening | Apr 25 – May 23, 2027 | W39–42 | Perf, security, docs, DR | Pod D (lead) + all | **v1.0-rc + Code Freeze** |
| **P6** | Graduation | May 24 – Jun 6, 2027 | W43–44 | Final prod deploy, dry-runs, presentation | TPM + all | **v1.0 + presentation** |

### 4.2 Version Roadmap

| Version | Target Date | Week | Theme | Key Capability | Gate |
|---|---|---|---|---|---|
| v0.1 | Sep 12, 2026 | W6 | Skeleton | Repo, CI, dev env, empty Next.js + FastAPI, auth scaffold, hello-world deploy | — |
| v0.2 | Sep 26, 2026 | W8 | Foundations | User mgmt, course CRUD, file upload, basic UI shell | — |
| v0.3 | Oct 24, 2026 | W12 | Ingestion | OCR pipeline, chunking, raw text stored | — |
| v0.4 | Nov 21, 2026 | W16 | **Thin MVP** | Pre-loaded PDF + chat UI; AI pipeline proven end-to-end | **G1** |
| v0.5 | Dec 19, 2026 | W20 | **Full MVP + Tier 1 Freeze** | RAG with citations, end-to-end student flow, Tier 1 Architecture Freeze | **G2** |
| v0.6 | Jan 30, 2027 | W26 | Knowledge layer | KG (concepts + relations), KG-backed retrieval boost | — |
| v0.7 | Feb 27, 2027 | W30 | Cognition + Tier 2 Freeze | Cognitive model (rolling-average mastery), quiz generation v1, Tier 2 Architecture Freeze | **G3** |
| v0.8 | Mar 27, 2027 | W34 | Adaptation | Adaptive engine (next-best-concept, difficulty adjustment); IRT if data supports | — |
| v0.9 | Apr 24, 2027 | W38 | Analytics + Feature Freeze | Learning analytics dashboard, admin dashboard (minimal), Feature Freeze | **G4** |
| v1.0-rc | May 22, 2027 | W42 | Hardening + Code Freeze | Perf, security, bug bash, docs, DR drill, Code Freeze | **G5** |
| v1.0 | Jun 5, 2027 | W44 | **Graduation** | Production deployment, final docs, graduation presentation | **Final** |

### 4.3 Integration Milestones (IM-1 … IM-15)

| IM # | Week | Components Integrated | Verifiable Outcome | Owner |
|---|---|---|---|---|
| IM-1 | W6 | Frontend ↔ Auth ↔ DB | User registers in UI, appears in DB | A-Lead |
| IM-2 | W8 | Frontend ↔ Course API ↔ Storage | Instructor creates course + uploads PDF | A-Lead |
| IM-3 | W10 | Upload → OCR job → DB | Uploaded PDF's text is in DB | B-Lead |
| IM-4 | W13 | OCR → Chunking → Embeddings → VectorDB | Full ingestion pipeline runs end-to-end | B-Lead |
| IM-5 | W15 | VectorDB → Reranker → RAG | Query returns cited answer via curl | B-Lead |
| IM-6 | W16 | RAG ↔ Chat API ↔ Chat UI (thin MVP) | User chats with document in browser, no auth | A-Lead + C-Lead |
| IM-7 | W17 | Full student flow (auth → course → upload → chat) | E2E Playwright test green | D-Lead |
| IM-8 | W24 | OCR → Concept extraction → KG | KG populated from new upload | B-Lead |
| IM-9 | W25 | KG → RAG retrieval boost | RAG eval faithfulness improves | B-Lead |
| IM-10 | W28 | Quiz generation → Quiz UI → Mastery update | Student takes quiz, mastery changes | A-Lead + C-Lead |
| IM-11 | W32 | Mastery → Adaptive engine → Recommendation UI | Student sees a recommendation | B-Lead + C-Lead |
| IM-12 | W33 | Adaptive engine → Quiz difficulty | Quiz difficulty adapts | B-Lead |
| IM-13 | W35 | Analytics dashboard ↔ real DB data | Instructor sees real cohort metrics | A-Lead + C-Lead |
| IM-14 | W41 | Full system on staging under load | 50 concurrent users; P95 < 2s | D-Lead |
| IM-15 | W43 | Production deployment end-to-end | v1.0 live on prod URL | D-Lead |

### 4.4 Testing Milestones (TM-1 … TM-15)

| TM # | Week | Milestone | Coverage / Quality Bar | Owner |
|---|---|---|---|---|
| TM-1 | W4 | Unit test infra in CI | pytest + Vitest configured; sample tests pass | D-Lead |
| TM-2 | W8 | Auth + course CRUD unit tests | ≥ 80% line coverage on these modules | A-Lead |
| TM-3 | W12 | OCR pipeline integration tests | 5 sample PDFs; assertions on output schema | B-Lead |
| TM-4 | W15 | RAG golden set v1 | 50 Q&A pairs; eval script runs in CI | B-Lead |
| TM-5 | W17 | E2E test (Playwright) for student flow | 1 E2E test green on staging | D-Lead |
| TM-6 | W20 | Coverage ≥ 40% on critical paths | Measured in CI | D-Lead |
| TM-7 | W24 | KG sanity tests | Schema validation; cycle detection | B-Lead |
| TM-8 | W28 | Quiz + mastery E2E test | Student takes quiz, mastery updates, assertion | D-Lead |
| TM-9 | W33 | Adaptation eval harness | Simulated trajectories; regression baseline | B-Lead |
| TM-10 | W36 | Bug bash #1 | Top-50 bugs triaged; P1s assigned | D-Lead |
| TM-11 | W38 | Coverage ≥ 60% on critical paths | Measured in CI; gate for Feature Freeze | D-Lead |
| TM-12 | W39 | Load test | 50 concurrent users; P95 < 2s | D-Lead |
| TM-13 | W40 | Security review | OWASP top 10; SAST clean; no high vulns | D-Lead |
| TM-14 | W41 | Bug bash #2 | ≤ 3 P1s open | D-Lead |
| TM-15 | W42 | Smoke tests on prod-like env | All critical paths green | D-Lead |

### 4.5 Documentation Milestones (DM-1 … DM-16)

| DM # | Week | Milestone | Artifact | Owner |
|---|---|---|---|---|
| DM-1 | W2 | MVP definition | `docs/mvp.md` | TPM |
| DM-2 | W4 | First 5 ADRs | `docs/adr/001-005` | TPM |
| DM-3 | W4 | Team norms + contributing guide | `CONTRIBUTING.md`, `README.md` | TPM |
| DM-4 | W8 | API reference v1 (auto-generated) | OpenAPI spec published | A-Lead |
| DM-5 | W8 | Docusaurus site live | Public docs URL | C-Lead |
| DM-6 | W11 | OCR + chunking design docs | `docs/ocr.md`, `docs/chunking.md` | B-Lead |
| DM-7 | W15 | RAG design doc + eval methodology | `docs/rag.md` | B-Lead |
| DM-8 | W19 | ADRs 1–15 complete | All architecture decisions recorded | TPM |
| DM-9 | W20 | Architecture diagram v1 | Single-page system diagram | TPM |
| DM-10 | W23 | KG design doc | `docs/kg.md` | B-Lead |
| DM-11 | W27 | Cognitive model design doc | `docs/student-model.md` | B-Lead |
| DM-12 | W31 | Adaptive engine design doc | `docs/adaptive.md` | B-Lead |
| DM-13 | W36 | Instructor quickstart + student quickstart | User-facing docs | C-Lead |
| DM-14 | W39 | Runbooks: deploy, rollback, DR, on-call | `docs/runbooks/` | D-Lead |
| DM-15 | W41 | Final architecture diagram + ADR index | Updated to reflect actual code | TPM |
| DM-16 | W42 | README polish + demo recording | `README.md` final + 5-min demo video | TPM + C-Lead |

### 4.6 Graduation Preparation Milestones (GPM-0 … GPM-12)

Graduation prep is a 22-week runway starting W20.

| GPM # | Week | Milestone | Owner |
|---|---|---|---|
| GPM-0 | W20 | Demo backlog started — list of "moments that would make good demo beats" | TPM |
| GPM-1 | W24 | Demo backlog reviewed; top-10 beats selected | TPM + advisor |
| GPM-2 | W26 | Presentation outline v0 (story arc) | TPM |
| GPM-3 | W30 | Demo script skeleton (what to click, what to say) | TPM |
| GPM-4 | W32 | Slide template chosen; first 5 slides drafted | TPM + C-Lead |
| GPM-5 | W34 | Demo script v1 (filled in) | TPM |
| GPM-6 | W36 | Full deck v1 reviewed by advisor | TPM |
| GPM-7 | W38 | Demo data curated (clean, predictable, reproducible) | B-Lead + C-Lead |
| GPM-8 | W40 | Dry-run #0 (internal, no advisor) | TPM |
| GPM-9 | W41 | Fallback demo video recorded | C-Lead |
| GPM-10 | W42 | Dry-run #1 with advisor | TPM |
| GPM-11 | W43 | Slide deck v2; dry-run #2; prod deployment stable | TPM + D-Lead |
| GPM-12 | W44 | Dry-run #3 (dress rehearsal); submit artifacts | TPM |

### 4.7 Demo Data Milestones (DDM-1 … DDM-8)

| DDM # | Week | Milestone | Owner |
|---|---|---|---|
| DDM-1 | W20 | Demo PDF set chosen (3 courses × 5–10 PDFs each, all clean, all OCR-able) | B-Lead |
| DDM-2 | W24 | Demo dataset v1: all demo PDFs ingested, OCR'd, embedded, in staging | B-Lead + D-Lead |
| DDM-3 | W30 | 5 demo student accounts created with seeded mastery states | B-Lead + A-Lead |
| DDM-4 | W34 | Demo quiz pool: 20 quizzes with known-good answers, tagged by concept | B-Lead |
| DDM-5 | W36 | 5 known-good RAG questions identified and validated (golden demo set) | B-Lead |
| DDM-6 | W38 | Demo data snapshot created; restore script tested | D-Lead |
| DDM-7 | W40 | Demo data loaded on prod-like env; smoke-tested | D-Lead |
| DDM-8 | W42 | Demo data frozen; no changes after this point | TPM |

### 4.8 Risk Snapshot (Top Red Risks)

The full risk register is in Section 15. The top red risks (score ≥ 12) that drive the most planning constraints:

| ID | Risk | Score | Affected Weeks | Mitigation Starts |
|---|---|---|---|---|
| R-01 | OCR quality too low on real-world PDFs | 16 | W5 spike, W9–W10 pipeline | W5 (spike) |
| R-02 | RAG quality unacceptable (hallucinations, wrong citations) | 16 | W14–W16, W17 eval | W15 (eval harness) |
| R-16 | Exam crunch 1 collapses capacity (late Jan 2027) | 16 | W25–W27 | W20 (planning buffer) |
| R-18 | v0.5 (MVP) slips past W20 | 15 | W14–W20 | W16 (thin MVP gate) |
| R-03 | Adaptive engine fails to converge | 12 | W29–W33 | W29 (research spike) |
| R-07 | LLM API provider changes terms | 12 | Continuous | W7 (LiteLLM gateway) |
| R-17 | Exam crunch 2 eats into hardening | 12 | W39–W40 | W37 (front-loaded hardening) |
| R-20 | Feature Freeze slips past W38 | 12 | W31–W38 | W34 (dashboard parallel work) |
| R-21 | A key team member drops out | 12 | Continuous | W4 (cross-training) |
| R-22 | Pod B (AI/ML) overloaded | 12 | W9–W34 | W4 (Pod B restructured to 7 components) |

### 4.7 Scoped Fallbacks (F-1 … F-7)

| Fallback ID | Trigger | What Swaps | Cost | Owner |
|---|---|---|---|---|
| F-1 | Qdrant down > 1h unresolved OR Pod B can't maintain it | Qdrant → pgvector (Postgres extension) | 1 day | D-Lead |
| F-2 | Neo4j ops too heavy OR KG schema not converging | Neo4j → JSONB in Postgres with recursive CTEs | 3 days | D-Lead + A-Lead |
| F-3 | Self-hosted BGE-M3 too slow OR GPU unavailable | BGE-M3 → OpenAI text-embedding-3-small | 1 day | B-Lead |
| F-4 | LLM API cost > $300/month | GPT-4-class → GPT-4o-mini or DeepSeek or GLM-4-flash for non-critical paths | 1 day | D-Lead |
| F-5 | Celery + Redis ops too heavy | Celery → Inngest (serverless) | 1 week | D-Lead |
| F-6 | PaddleOCR quality too low on real PDFs | PaddleOCR → Google Document AI (managed) | 3 days | B-Lead |
| F-7 | Adaptive engine research spike fails | ML-based adaptive → rule-based adaptive (if-else) | 0 days | B-Lead |

---



## 5. 44-Week Detailed Execution Plan

Each weekly section follows the same structure: roadmap context, four Pod subsections (each with Objective, Tasks, and per-task fields: Task / Why / Expected Output / Dependencies / Handoff / Definition of Done), Cross-Pod Integration, and a Week-level Definition of Done. Tasks are derived from the Master Roadmap sprint timeline (scope/timeline authority) and decomposed using the Technical Specification (algorithm/architecture authority).

### Week 1 — Kickoff + Stack Lock

#### Roadmap Context

- **Phase:** P0 Pre-Flight
- **Milestone:** Stack decision doc signed; GitHub org + repo created; README with team norms; Out-of-Scope list signed
- **Release:** Pre-v0.1
- **Primary Objective:** Lock the technology stack, stand up the repo and CI scaffold, provision environments, and sign the Out-of-Scope list. Remove every excuse for not starting real work in P1.

#### Backend Pod

##### Objective
Stand up the FastAPI application skeleton, the database baseline, and the repository structure so Pod A can begin auth work in W5 with no infra friction.

##### Tasks

**Task:** Initialize the FastAPI backend repository with Python 3.12, Pydantic v2, SQLAlchemy 2, Alembic, Uvicorn, and the standard project layout (`backend/app/api/`, `backend/app/services/`, `backend/app/repositories/`, `backend/app/domain/`, `backend/app/pal/`).
**Why:** The Tech Spec mandates FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic (Section 19.1, 26.1); the modular monolith requires a fixed directory structure that mirrors modules (Ingestion, Retrieval, Generation, KG, SKM, CSP, Adaptive, Analytics).
**Expected Output:** `backend/` directory with `pyproject.toml`, `app/main.py` exposing a `/health` endpoint returning `{"status": "ok"}`, and an empty `alembic/` directory.
**Dependencies:** GitHub org created (TPM task); Python 3.12 installed on dev machines.
**Handoff:** Repository URL and directory layout documented in `README.md` so Pod C, Pod B, and Pod D can clone and contribute.
**Definition of Done:** `uvicorn app.main:app --reload` runs locally; `/health` returns 200; `ruff check` passes on initial commit.

**Task:** Create the Alembic configuration and the initial empty migration so the first real migration (the `users` table, W3) has a baseline.
**Why:** The roadmap W3 sprint requires a `users` table migration (TM-1 supports it); Alembic must be initialized before any model is added.
**Expected Output:** `alembic.ini`, `alembic/env.py` configured for SQLAlchemy 2 async, and a baseline migration.
**Dependencies:** FastAPI skeleton (above).
**Handoff:** Migration workflow documented in `README.md` (`alembic revision --autogenerate -m "msg"` then `alembic upgrade head`).
**Definition of Done:** `alembic upgrade head` runs on a local Postgres with no errors; `alembic current` shows the baseline.

**Task:** Draft ADR-001 (stack lock), ADR-002 (repo structure), ADR-003 (API versioning with `/v1` prefix), ADR-004 (env management with Pydantic Settings + `.env` files per environment), ADR-005 (LLM gateway = LiteLLM proxy). Each ADR follows the template in the Master Roadmap (Context / Decision / Alternatives / Consequences / Open questions).
**Why:** The roadmap W4 sprint requires ADRs 1–5 merged (DM-2); docs-first workflow (Roadmap §Documentation Strategy) means ADRs precede code that depends on them.
**Expected Output:** Five ADR markdown files in `docs/adr/001-stack-lock.md` through `005-llm-gateway.md`, each marked `Proposed` pending pod-lead review.
**Dependencies:** Tech Spec Sections 7, 8, 18, 19, 26 (source for decisions); Roadmap Technology Stack table.
**Handoff:** ADRs circulated to all pod leads for review by EOD Friday W1; merge target W4.
**Definition of Done:** All 5 ADRs opened as PRs; at least 1 review comment from each pod lead; status moves to `Accepted` by W4.

#### AI/ML & Data Pod

##### Objective
Begin the parallel spike tracks (OCR + embeddings + LLM gateway) that must conclude in W5 with ADRs so P2 can start immediately. Stand up the PAL skeleton so Pod B can develop against interfaces, not implementations.

##### Tasks

**Task:** Initialize the Provider Abstraction Layer (PAL) skeleton: abstract base classes for the 7 interfaces (`ReasoningInterface`, `EmbeddingInterface`, `OCRInterface`, `SpeechInterface`, `VectorDBInterface`, `VisionInterface`, `RankingInterface`) in `backend/app/pal/interfaces/`. Each interface declares its methods (per Tech Spec Section 8.1) and a `health_check()` method.
**Why:** The Tech Spec mandates that no core module imports a provider library directly (Section 18.3); the PAL is the architectural boundary that enforces this. Without the interfaces, Pod B's W9 OCR pipeline work would hard-code PaddleOCR.
**Expected Output:** Seven abstract base classes with type-annotated method signatures and docstrings referencing the Tech Spec section that defines them.
**Dependencies:** Backend skeleton (Pod A); Tech Spec Section 8.1.
**Handoff:** PAL interfaces published in `backend/app/pal/interfaces/__init__.py`; Pod A imports them when writing services.
**Definition of Done:** `python -c "from app.pal.interfaces import ReasoningInterface"` succeeds; all 7 interfaces have docstrings; ruff/mypy pass.

**Task:** Assemble the **20-PDF golden set** for OCR evaluation: 5 clean digital PDFs, 5 scanned PDFs, 5 mixed Arabic+English PDFs, 5 with figures/diagrams. Tag each with expected word count and known tricky regions (rotated pages, columns). Commit to `tests/data/golden_pdfs/` with a `manifest.json`.
**Why:** R-01 (OCR quality, score 16) is the top red risk; PB-01 trigger metric is "< 90% success rate on the 20-PDF golden set at W10 demo." The set must exist before W5's OCR spike.
**Expected Output:** `tests/data/golden_pdfs/` containing 20 PDFs + `manifest.json` with metadata.
**Dependencies:** None (data gathering task).
**Handoff:** Manifest handed to Pod D for inclusion in the eval harness scaffold (W4).
**Definition of Done:** 20 PDFs committed; manifest validates; Pod B-Lead confirms coverage of the 4 categories.

**Task:** Draft the LiteLLM gateway deployment plan: Docker image, port (default 4000), provider config for at least 2 providers (OpenAI + Anthropic, or OpenAI + GLM), key rotation strategy, cost-tracking endpoint.
**Why:** ADR-005 (LLM gateway) is being written this week; the gateway must be deployed in W7 (Roadmap W7 sprint "LLM gateway"). R-07 (LLM provider change, score 12) is mitigated structurally by the gateway.
**Expected Output:** `docs/plans/litellm-gateway.md` with deployment, config, and fallback chain (per Tech Spec Section 9.2 graceful degradation strategy).
**Dependencies:** ADR-005 draft.
**Handoff:** Plan handed to Pod D for W7 deployment.
**Definition of Done:** Plan reviewed by D-Lead and B-Lead; deployment steps reproduce on a fresh machine.

#### Frontend Pod

##### Objective
Initialize the Next.js 16 skeleton with the App Router, Tailwind CSS 4, shadcn/ui, TypeScript 5, and Storybook so Pod C can begin UI work in W2 with the design system in place.

##### Tasks

**Task:** Initialize the Next.js 16 application using `create-next-app@latest` with TypeScript, App Router, Tailwind CSS 4, ESLint, and the `src/` directory pattern. Configure `next.config.ts` for environment variable validation with Zod.
**Why:** Tech Spec Section 20.1 mandates Next.js 16 with App Router; Roadmap W2 sprint requires the skeleton to "run locally and on Vercel/preview." TypeScript 5 is the binding version per Tech Spec Section 26.1.
**Expected Output:** `frontend/` directory with `next.config.ts`, `tsconfig.json`, `tailwind.config.ts`, `postcss.config.mjs`, `src/app/layout.tsx`, `src/app/page.tsx`.
**Dependencies:** GitHub repo (TPM); Node 20+ installed.
**Handoff:** Repo URL + setup steps documented in `README.md`.
**Definition of Done:** `npm run dev` starts on `:3000`; `npm run build` succeeds; ESLint passes.

**Task:** Install and configure shadcn/ui: run `npx shadcn-ui@latest init`, configure `components.json` for Tailwind 4, install the base component set (button, input, label, card, dialog, dropdown-menu, form, toast).
**Why:** Tech Spec Section 26.1 mandates shadcn/ui for accessible, consistent components; W2 sprint requires "Storybook shows base components."
**Expected Output:** `src/components/ui/` with the base components; `components.json` committed.
**Dependencies:** Next.js skeleton (above).
**Handoff:** Component library available to all Pod C engineers for W2 design tokens work.
**Definition of Done:** All base components render in Storybook (or `npm run dev` if Storybook is W2); type-check passes.

**Task:** Configure Storybook 8 with the Next.js framework preset, including Tailwind CSS 4 integration and dark mode toggle.
**Why:** The W2 sprint exit criterion requires "Storybook shows base components." Storybook is the design-system contract surface for Pod C.
**Expected Output:** `.storybook/main.ts` and `.storybook/preview.ts` configured; a sample story for the Button component.
**Dependencies:** shadcn/ui installed.
**Handoff:** Storybook URL accessible to all Pod C engineers; deploy to Chromatic (free tier) for visual regression in CI (Pod D W4 task).
**Definition of Done:** `npm run storybook` starts on `:6006`; Button story renders in light and dark mode.

#### DevOps / QA Pod

##### Objective
Stand up the GitHub Actions CI scaffold, provision the three environments (dev/staging/prod), and seed the risk register. The CI pipeline is the gate that every PR must pass from W2 onward.

##### Tasks

**Task:** Create the GitHub Actions CI workflow `.github/workflows/ci.yml` that runs on every PR: lint (ruff for Python, ESLint + Prettier for TypeScript), unit tests (pytest + Vitest), build (Docker images for backend + frontend), documentation check (file-existence rule: new endpoint/schema/ADR must have corresponding doc), license scan, coverage report posted as PR comment.
**Why:** Roadmap §CI/CD Strategy mandates this 7-stage pipeline on every PR; TM-1 (W4) requires "pytest + Vitest configured; sample tests pass" — the workflow is the scaffold that delivers this.
**Expected Output:** `.github/workflows/ci.yml` with 7 jobs (lint, unit-test, integration-test-stub, build, docs-check, license-scan, coverage-report); a sample pytest test and a sample Vitest test that both pass.
**Dependencies:** Both Pod A and Pod C skeletons (so CI has something to lint/test/build).
**Handoff:** CI green on a dummy PR by EOD Friday W1 (Roadmap W1 exit criterion: "CI green on a dummy PR").
**Definition of Done:** A PR with a deliberate failing test correctly blocks merge; a passing PR is mergeable; coverage report appears as PR comment.

**Task:** Provision the three environments: `dev` (developer machines, synthetic data), `staging` (auto-deploy on every `main` merge, anonymized real + demo data), `prod` (manual deploy on tag, real user + demo data). Each environment has a documented URL.
**Why:** Roadmap W1 sprint requires "`dev` / `staging` / `prod` environments documented and reachable"; Tech Spec Section 23 defines the three deployment configurations.
**Expected Output:** `infra/environments.md` documenting each environment's URL, data, refresh cadence, and access controls. Staging URL accessible from outside the team by EOD Friday W1.
**Dependencies:** Cloud provider account (Hetzner or AWS, per stack table).
**Handoff:** Environment URLs handed to all Pod leads; TPM includes them in the README.
**Definition of Done:** Each env has a URL; staging shows a placeholder Nginx page (hello-world); prod URL reserved but not deployed (W3 deploys).

**Task:** Seed the risk register with the 32 risks from the Master Roadmap (R-01 … R-32) and assign owners. Create a GitHub Project board with columns: Risk ID / Description / Likelihood / Impact / Score / Owner / Mitigation / Trigger / Status.
**Why:** Roadmap §Risk Register is the SSOT; risks must be tracked from W1 so the W4 risk register v1 (TPM task) has substance. Biweekly review cadence starts W2.
**Expected Output:** `docs/risk-register.md` (or GitHub Project board) with all 32 risks; each with an owner and a mitigation summary.
**Dependencies:** None (planning task).
**Handoff:** Risk register visible to all pod leads; biweekly review agenda template committed to `docs/retro-agenda.md`.
**Definition of Done:** 32 risks logged; owners confirmed in W1 Friday demo; TPM reviews top red risks (R-01, R-02, R-16, R-18, R-03, R-07, R-17, R-20, R-21, R-22).

#### Cross-Pod Integration

- **Backend ↔ Frontend:** Both repos exist; CI scaffold enforces a common PR review protocol. Pod A's `/health` endpoint and Pod C's Next.js skeleton are the first deployable artifacts. No API contract yet (that comes in W5).
- **Backend ↔ AI/ML:** Pod A creates the `backend/app/pal/` directory; Pod B owns the contents (interfaces in W1, implementations starting W5). This is a shared code surface — both Pods must agree on the layout before any code lands.
- **DevOps/QA ↔ All Pods:** The CI scaffold is binding on every PR from W2 onward; Pod D publishes the CI status badge in `README.md`. The three environments are reachable by every Pod lead.
- **TPM ↔ All Pods:** The Out-of-Scope list is signed by all pod leads + advisor by EOD Friday W1 (Roadmap exit criterion).

#### Week 1 Definition of Done

1. GitHub org + repo exist; PR template, CODEOWNERS, and `main` branch protection rules in place.
2. Out-of-Scope list (15 items) signed by all pod leads + advisor.
3. CI scaffold green on a dummy PR.
4. Three environments documented and staging URL reachable.
5. ADRs 1–5 opened as PRs (status `Proposed`); pod-lead review started.
6. PAL skeleton committed; 7 interfaces defined.
7. 20-PDF golden set committed with manifest.
8. Next.js 16 + FastAPI skeletons both run locally.
9. Risk register seeded with all 32 risks.
10. Friday demo on staging (even if just "hello world" pages on both apps).

---

### Week 2 — MVP Sign-off + Skeletons

#### Roadmap Context

- **Phase:** P0 Pre-Flight
- **Milestone:** MVP definition doc approved by all pod leads; ≥ 8 active members confirmed; Next.js skeleton + FastAPI skeleton deployable
- **Release:** Pre-v0.1
- **Primary Objective:** Lock the MVP definition, deploy both skeletons to staging, and confirm team capacity. Begin design tokens and choose the demo PDF for the v0.4 thin MVP.

#### Backend Pod

##### Objective
Harden the FastAPI skeleton with OpenAPI docs, CORS, env config, and a deployment story so v0.1 (W6) ships cleanly. Set up the SQLAlchemy 2 async engine and session manager.

##### Tasks

**Task:** Configure OpenAPI documentation: enable FastAPI's auto-generated OpenAPI at `/openapi.json` and `/docs` (Swagger UI) and `/redoc` (ReDoc). Document every endpoint with summary, description, response model, and example. Configure CORS to allow the frontend origin (configurable per env).
**Why:** Tech Spec Section 22.1 mandates REST + WebSocket architecture with OpenAPI as the contract surface; DM-4 (W8) requires "API reference v1 (auto-generated)" — the foundation must exist now.
**Expected Output:** `app/main.py` with CORS middleware, OpenAPI config, and at least the `/health` endpoint documented with a response model.
**Dependencies:** FastAPI skeleton (W1).
**Handoff:** OpenAPI URL accessible to Pod C for client code generation (W5+); Pod D includes the OpenAPI lint check in CI.
**Definition of Done:** `/docs` renders in browser; `/openapi.json` returns valid OpenAPI 3.1 schema; CORS allows `localhost:3000` in dev.

**Task:** Configure SQLAlchemy 2 async engine with `asyncpg` driver; create the session manager (`app/db/session.py`) with `async_sessionmaker` and a `get_db` FastAPI dependency. Configure the Alembic `env.py` to use async engine.
**Why:** Tech Spec Section 19.1 mandates SQLAlchemy 2; async is required because Pod A will write async route handlers and async Celery tasks. The `users` table migration in W3 depends on this.
**Expected Output:** `app/db/session.py`, `app/db/base.py` (declarative base), updated `alembic/env.py`.
**Dependencies:** Alembic init (W1); Postgres provisioned (D-Lead task W1).
**Handoff:** `get_db` dependency available to Pod A engineers writing routes in W5+.
**Definition of Done:** A trivial sync + async round-trip test passes; Alembic can read the engine.

#### AI/ML & Data Pod

##### Objective
Continue spike prep: write the eval methodology for the OCR spike (W5) and the embedding spike (W5). Choose the demo PDF for v0.4 thin MVP (Roadmap W3 sprint) in collaboration with Pod C and TPM.

##### Tasks

**Task:** Write `docs/plans/ocr-spike-methodology.md` defining: the 20-PDF golden set test protocol (success criteria = ≥ 90% extraction quality, ≤ 5% character error rate), the 3 candidate engines to evaluate (PaddleOCR, Tesseract, Google Document AI), the metrics (character error rate, word error rate, layout preservation, Arabic character accuracy, latency, memory), and the decision matrix.
**Why:** Roadmap W5 sprint requires "Compare PaddleOCR vs Tesseract vs Document AI on 5 sample PDFs; choice ADR drafted." The methodology must exist before the spike. PB-01 trigger metric references "the 20-PDF golden set at W10 demo."
**Expected Output:** `docs/plans/ocr-spike-methodology.md` (3–5 pages).
**Dependencies:** Golden set (W1).
**Handoff:** Methodology reviewed by D-Lead (for eval harness integration) and B-Lead; spike owner (B-Lead or B-1) follows it in W5.
**Definition of Done:** Methodology merged; metrics defined; decision matrix explicit.

**Task:** Write `docs/plans/embedding-spike-methodology.md` defining: the eval dataset (10–20 Arabic+English query-chunk pairs with relevance labels), the 2 candidate models (BGE-M3 self-hosted, OpenAI text-embedding-3-small), the metrics (MTEB-style retrieval accuracy, latency per batch, memory footprint, dim size).
**Why:** Roadmap W5 sprint requires "Compare BGE-M3 vs OpenAI text-embedding-3-small on quality + latency; choice ADR drafted." Tech Spec Section 10.2 specifies the 4-dimension framework (quality, resource, privacy, latency).
**Expected Output:** `docs/plans/embedding-spike-methodology.md`.
**Dependencies:** None (planning).
**Handoff:** Spike owner (B-1) follows it in W5.
**Definition of Done:** Methodology merged; both candidate models installed locally for W5.

**Task:** Choose the **demo PDF for v0.4 thin MVP** (Roadmap W3 sprint: "demo PDF selected"). Criteria: 30–80 pages, clean digital text (no scanned), single language (English or Arabic), clearly sectioned, ~50 identifiable concepts. Commit to `tests/data/demo_pdf/v0.4.pdf` with metadata.
**Why:** The v0.4 thin MVP (W16) requires a pre-loaded PDF; choice must be locked by W3 so OCR/chunking/embedding pipelines can be tested against it throughout P2.
**Expected Output:** `tests/data/demo_pdf/v0.4.pdf` + `metadata.json` (page count, expected concepts, language, source attribution).
**Dependencies:** None.
**Handoff:** PDF committed; Pod C acknowledges it will be the W16 demo subject; TPM notes it in the demo backlog (GPM-0 starts W20).
**Definition of Done:** PDF committed; metadata complete; B-Lead confirms it is OCR-able.

#### Frontend Pod

##### Objective
Deliver the design tokens (Tailwind config + shadcn theme) and confirm the Next.js skeleton deploys to a preview URL. Storybook shows base components.

##### Tasks

**Task:** Define the design tokens: color palette (primary, secondary, accent, semantic colors for success/warning/error/info), typography scale (font families, sizes, line heights), spacing scale, border radii, shadows, breakpoints. Implement as Tailwind CSS 4 config + CSS variables for theming.
**Why:** Tech Spec Section 20.1 mandates Tailwind 4 + shadcn/ui; design tokens are the contract surface that all UI work in P1+ depends on. W3 sprint requires "Tokens reviewed and locked."
**Expected Output:** `frontend/tailwind.config.ts` with full token definitions; `frontend/src/styles/globals.css` with CSS variables; `frontend/src/lib/utils.ts` with `cn()` helper.
**Dependencies:** shadcn/ui installed (W1).
**Handoff:** Tokens reviewed by C-Lead and locked by W3; all Pod C engineers use them; Storybook stories consume them.
**Definition of Done:** Tokens documented in `docs/design-tokens.md`; light/dark themes render correctly in Storybook.

**Task:** Deploy the Next.js skeleton to a public preview URL (Vercel preview or staging) using the staging environment from W1.
**Why:** Roadmap W3 sprint requires "Both apps deployed to public URLs over HTTPS"; this W2 task is the prep step so W3 deploys cleanly.
**Expected Output:** Staging URL showing the Next.js skeleton's default page over HTTPS.
**Dependencies:** Staging environment (Pod D W1).
**Handoff:** URL handed to Pod D for inclusion in the W3 v0.1 deploy task.
**Definition of Done:** URL accessible from outside the team; HTTPS enforced (HTTP redirects to HTTPS); page loads in < 2s.

#### DevOps / QA Pod

##### Objective
Begin the eval harness scaffold (the structure that Pod B's RAG golden set will plug into from W15) and complete the unit-test infra in CI (TM-1 prep).

##### Tasks

**Task:** Create the eval harness scaffold `backend/app/eval/` with: a `BaseEvaluator` abstract class, a `Metric` dataclass (name, value, threshold), a `run_evaluator(name, dataset, config)` function, and a CLI entry point `python -m app.eval run <evaluator_name> --dataset <path>`. Document the eval harness design in `docs/eval-harness.md`.
**Why:** TM-1 (W4) requires "Unit test infra in CI"; TM-4 (W15) requires "RAG golden set v1; eval script runs in CI"; the harness must exist as a skeleton by W4. Tech Spec Section 28.2 mandates the "Fallback Always" risk philosophy, which requires measurable triggers — the eval harness is what produces those measurements.
**Expected Output:** `backend/app/eval/` skeleton; `docs/eval-harness.md` design doc; a sample `DummyEvaluator` that runs in CI.
**Dependencies:** Backend skeleton (Pod A W1).
**Handoff:** Pod B plugs the RAG golden set evaluator into this scaffold in W15; Pod D extends it for KG sanity (W24) and adaptation eval (W33).
**Definition of Done:** `python -m app.eval run dummy --dataset tests/data/dummy.json` returns 0 with a metrics JSON.

**Task:** Configure pytest with async support (`pytest-asyncio`), fixtures (`conftest.py` with `db_session`, `client`, `mock_user`), and coverage reporting (`pytest-cov` with `--cov=app --cov-report=xml --cov-report=term`). Configure Vitest with `jsdom` environment, `@testing-library/react`, and coverage (`vitest --coverage`).
**Why:** TM-1 (W4) requires "pytest + Vitest configured; sample tests pass"; TM-2 (W8) requires "≥ 80% line coverage on auth + course CRUD modules."
**Expected Output:** `backend/pytest.ini` and `backend/tests/conftest.py`; `frontend/vitest.config.ts` and `frontend/src/test/setup.ts`; sample tests on both sides that pass.
**Dependencies:** Backend + frontend skeletons (W1).
**Handoff:** All Pod A and Pod C engineers use these test infrastructures from W3 onward; CI runs them on every PR.
**Definition of Done:** `pytest` and `npm test` both pass with 1+ sample test each; coverage reports generate.

#### Cross-Pod Integration

- **Backend ↔ Frontend:** Pod A exposes `/health`; Pod C's Next.js skeleton can call it via a server-side fetch (configured in `next.config.ts`). This is the first Backend ↔ Frontend integration — minor, but validates CORS and HTTPS.
- **Backend ↔ AI/ML:** Pod A creates `app/db/`; Pod B owns `app/pal/`. Both directories coexist; the boundary is documented in `docs/architecture.md`.
- **AI/ML ↔ DevOps/QA:** Pod B's eval methodology docs inform Pod D's eval harness scaffold. Pod B will write the actual RAG evaluator in W15 using Pod D's `BaseEvaluator` abstraction.
- **Frontend ↔ DevOps/QA:** Pod C's Storybook deploy + Pod D's CI scaffold integrate via Chromatic (visual regression) in W4.
- **TPM ↔ All Pods:** MVP definition doc (`docs/mvp.md`) is reviewed and signed by all pod leads. The MVP statement from the Roadmap ("A logged-in student can upload a PDF, the platform extracts its text and images, embeds the content, and the student can chat with the document and get cited answers — all deployed to a real URL") is the binding definition.

#### Week 2 Definition of Done

1. MVP definition doc (`docs/mvp.md`) approved by all pod leads + advisor.
2. ≥ 8 active members confirmed (if < 8, descope protocol triggers per Roadmap §Operating Assumptions).
3. OpenAPI docs live at staging URL.
4. SQLAlchemy 2 async engine configured; Alembic ready for first migration.
5. OCR + embedding spike methodologies merged.
6. Demo PDF for v0.4 selected and committed.
7. Design tokens defined and locked.
8. Next.js skeleton deployed to staging preview URL.
9. Eval harness scaffold exists; `DummyEvaluator` runs.
10. pytest + Vitest configured with sample tests.

---

### Week 3 — Hello World on a Real URL + DB Baseline

#### Roadmap Context

- **Phase:** P0 Pre-Flight
- **Milestone:** Both apps deployed to public URLs over HTTPS; Postgres provisioned; Alembic init; first migration creates `users` table; design tokens locked; demo PDF committed
- **Release:** v0.1 prep
- **Primary Objective:** Ship the first real deployment to staging. Stand up the database baseline. This is the first Friday demo on a real URL (not localhost).

#### Backend Pod

##### Objective
Deploy the FastAPI app to staging over HTTPS, run the first Alembic migration to create the `users` table, and prepare the auth scaffold for W5.

##### Tasks

**Task:** Write the first Alembic migration creating the `users` table per the Tech Spec ER diagram (Section 21.2): `id UUID PK`, `email VARCHAR UNIQUE NOT NULL`, `password_hash VARCHAR NOT NULL`, `preferred_lang VARCHAR DEFAULT 'en'`, `settings JSONB DEFAULT '{}'`, `created_at TIMESTAMP`, `updated_at TIMESTAMP`. Include a downgrade path.
**Why:** Tech Spec Section 21.2 defines the `USER` entity; the W5 auth work (register + login) depends on this table. The migration is the foundation for all future schema changes.
**Expected Output:** `alembic/versions/<hash>_create_users_table.py` with upgrade + downgrade.
**Dependencies:** SQLAlchemy 2 async engine (W2).
**Handoff:** Migration runs on dev + staging; Pod A engineers can write User SQLAlchemy models in W5.
**Definition of Done:** `alembic upgrade head` succeeds on staging; `alembic downgrade -1` succeeds; table schema matches the spec.

**Task:** Deploy the FastAPI app to staging: write the `Dockerfile` (multi-stage: builder with uv/pip, runtime slim), the `docker-compose.staging.yml` service for FastAPI + Postgres, and the GitHub Actions `deploy-staging.yml` workflow that auto-deploys on `main` merge.
**Why:** Roadmap W3 sprint requires "Both apps deployed to public URLs over HTTPS"; Roadmap §CI/CD Strategy mandates "main auto-deploys to staging." v0.1 (W6) requires a deployed login page.
**Expected Output:** `backend/Dockerfile`, `infra/docker-compose.staging.yml`, `.github/workflows/deploy-staging.yml`.
**Dependencies:** Staging environment (Pod D W1); CI scaffold (Pod D W1).
**Handoff:** Pod C deploys its Next.js app to staging using the same compose pattern; Pod D owns the staging infra.
**Definition of Done:** Staging URL shows FastAPI `/docs` over HTTPS; smoke test hits `/health` after deploy.

**Task:** Scaffold the auth module: `app/api/v1/auth.py` (route definitions only — empty handlers), `app/services/auth_service.py` (service interface), `app/domain/user.py` (Pydantic models: `UserCreate`, `UserRead`, `UserInDB` with `password_hash`). Configure `fastapi-users` library or equivalent.
**Why:** W5 sprint requires "Email/password register, login, JWT issue/refresh; tests ≥ 80%." The scaffold must exist so W5 work can focus on logic, not framework setup.
**Expected Output:** Auth module skeleton with route stubs returning 501 Not Implemented; Pydantic models defined.
**Dependencies:** Users table migration (above); `fastapi-users` library added to `pyproject.toml`.
**Handoff:** Pod A-1 picks this up in W5 to implement register + login + JWT.
**Definition of Done:** Routes exist; Pydantic models validate; OpenAPI shows the auth endpoints.

#### AI/ML & Data Pod

##### Objective
Install the candidate OCR and embedding engines locally so W5 spikes can run without setup delay. Confirm the demo PDF is OCR-able.

##### Tasks

**Task:** Install PaddleOCR (v4, Arabic+English models), Tesseract 5 (with Arabic training data), and the Google Document AI Python client. Write a `scripts/install_ocr_deps.sh` that reproduces the install on a fresh Ubuntu machine.
**Why:** W5 spike requires all 3 OCR engines runnable; without local install, the spike loses a day to setup.
**Expected Output:** `scripts/install_ocr_deps.sh` runs clean on a fresh Ubuntu 22.04; all 3 engines importable in Python.
**Dependencies:** None.
**Handoff:** Script committed; all Pod B engineers run it to set up dev environments.
**Definition of Done:** `python -c "import paddleocr; import pytesseract; from google.cloud import documentai"` succeeds.

**Task:** Install BGE-M3 (via `sentence-transformers`) and the OpenAI Python client (with `text-embedding-3-small` access). Verify the BGE-M3 model downloads to `~/.cache/huggingface/` and produces a 1024-dim vector for a sample Arabic+English sentence.
**Why:** W5 embedding spike requires both models runnable; F-3 fallback path requires the OpenAI client pre-wired.
**Expected Output:** `scripts/install_embedding_deps.sh`; sample script `scripts/test_embeddings.py` that prints vectors for both models.
**Dependencies:** OpenAI API key configured in `.env` (D-Lead).
**Handoff:** BGE-M3 model cached; Pod B-1 runs the spike in W5.
**Definition of Done:** Both models produce 1024-dim vectors for `"Hello world مرحبا"`; latency logged.

**Task:** Run the demo PDF (chosen W2) through PaddleOCR as a smoke test; verify text is extracted with reasonable quality. Note any pages that fail extraction.
**Why:** The v0.4 thin MVP depends on this PDF being processable; if PaddleOCR fails on it now, we know early and pick another PDF.
**Expected Output:** `tests/data/demo_pdf/v0.4_extracted_text.txt` (smoke output); a brief report of any problematic pages.
**Dependencies:** PaddleOCR installed (above); demo PDF committed (W2).
**Handoff:** Smoke output shared with B-Lead; if quality is poor, pick a new PDF before W4 lock.
**Definition of Done:** PDF extracts to > 90% of expected text; problematic pages flagged.

#### Frontend Pod

##### Objective
Deploy the Next.js skeleton to staging with HTTPS, configure the routing shell, and prepare for the W5 auth UI work.

##### Tasks

**Task:** Write the `Dockerfile` for Next.js (multi-stage: builder with `npm ci` and `npm run build`, runtime with `node:20-alpine` running `next start`). Add the Next.js service to `docker-compose.staging.yml`.
**Why:** Roadmap W3 sprint requires "Both apps deployed to public URLs over HTTPS"; Pod C must mirror Pod A's deploy story.
**Expected Output:** `frontend/Dockerfile`; updated `infra/docker-compose.staging.yml` with the Next.js service.
**Dependencies:** Pod A's compose pattern (W3 task above) for consistency.
**Handoff:** Pod D's GitHub Actions deploys both services on `main` merge.
**Definition of Done:** Staging URL renders the Next.js default page over HTTPS; Next.js SSR works (view page source shows server-rendered HTML).

**Task:** Build the app shell: `src/app/(auth)/layout.tsx`, `src/app/(student)/layout.tsx`, `src/app/(instructor)/layout.tsx`, `src/app/(admin)/layout.tsx` route groups with empty pages. Add a sidebar component, topnav, and breadcrumbs (placeholder data only).
**Why:** W7 sprint requires "App shell with sidebar, topnav, breadcrumbs, route guards." Laying the shell now lets W5+ auth work drop into existing routes.
**Expected Output:** Route group layouts; `src/components/layout/Sidebar.tsx`, `Topnav.tsx`, `Breadcrumbs.tsx` (all using shadcn/ui primitives).
**Dependencies:** Design tokens (W2).
**Handoff:** Pod C engineers use these route groups for all feature work in P1+.
**Definition of Done:** Routes `/login`, `/dashboard`, `/courses`, `/admin` exist (empty pages); sidebar renders; breadcrumbs show current route.

#### DevOps / QA Pod

##### Objective
Wire up the staging deploy pipeline end-to-end and validate that smoke tests run after every deploy. Begin observability baseline setup.

##### Tasks

**Task:** Complete the staging deploy workflow: on merge to `main`, build Docker images for backend + frontend, push to the registry (GitHub Container Registry free tier), pull on the staging server, run `docker-compose -f infra/docker-compose.staging.yml up -d`, run smoke tests (`curl /health` for backend, `curl /` for frontend), notify Slack on failure.
**Why:** Roadmap §CI/CD Strategy mandates "main auto-deploys to staging" + "smoke tests after every deploy"; Roadmap W3 sprint requires "URLs accessible from outside the team."
**Expected Output:** `.github/workflows/deploy-staging.yml` complete with all steps; Slack webhook integration; smoke test script `scripts/smoke_test.sh`.
**Dependencies:** Pod A + Pod C Dockerfiles (W3).
**Handoff:** Every `main` merge from W3 onward triggers this workflow; Pod D monitors it.
**Definition of Done:** A test merge to `main` triggers the workflow; staging URL shows the new code within 5 minutes; smoke test passes; Slack notification received.

**Task:** Provision Postgres 16 on staging (Docker container with persistent volume, daily backup cron job, and a connection string stored in GitHub Actions secrets). Configure Pod A's Alembic to run `alembic upgrade head` as part of the deploy workflow.
**Why:** Pod A's first migration (users table) must run on staging for the W5 auth work to test against a real DB; Tech Spec Section 21 mandates PG 16 with JSONB.
**Expected Output:** `infra/docker-compose.staging.yml` includes a `postgres` service with volume + backup; deploy workflow runs Alembic migrations.
**Dependencies:** Staging server provisioned (W1).
**Handoff:** Pod A engineers can connect to staging Postgres for debugging; backup script tested.
**Definition of Done:** `psql $STAGING_DB_URL -c "SELECT * FROM users"` returns empty table; backup runs daily at 02:00 UTC; restore tested.

#### Cross-Pod Integration

- **Backend ↔ Frontend:** Both apps deployed to staging; CORS configured. Frontend can call backend `/health` (first real cross-service call on staging).
- **Backend ↔ DevOps/QA:** Alembic migration runs in the deploy workflow; smoke test verifies the DB is reachable from the backend container.
- **AI/ML ↔ DevOps/QA:** Pod B's local install scripts (`install_ocr_deps.sh`, `install_embedding_deps.sh`) are reviewed by Pod D for inclusion in the dev environment setup.
- **End-to-end:** A user opens the staging URL, sees the Next.js skeleton; the backend's `/health` returns 200; Postgres has the `users` table. This is the first end-to-end smoke test on staging.

#### Week 3 Definition of Done

1. Both apps (FastAPI + Next.js) deployed to staging over HTTPS.
2. `users` table migration runs on staging; table is queryable.
3. Auth module scaffold exists (routes stubbed, Pydantic models defined).
4. OCR engines (PaddleOCR + Tesseract + Document AI client) installed locally.
5. Embedding models (BGE-M3 + OpenAI client) installed; 1024-dim vectors verified.
6. Demo PDF for v0.4 confirmed OCR-able.
7. App shell route groups + sidebar + topnav + breadcrumbs exist (empty pages).
8. Staging deploy workflow runs end-to-end on `main` merge; smoke tests pass; Slack notification works.
9. Postgres 16 running on staging with daily backup.
10. Friday demo: open staging URL in browser; show Next.js page + FastAPI `/docs` + Postgres `users` table.

---

### Week 4 — ADRs + Risk Register + v0.1 Tag

#### Roadmap Context

- **Phase:** P0 Pre-Flight (final week)
- **Milestone:** ADRs 1–5 merged; team norms + contributing guide; risk register v1; eval harness scaffold in CI; **v0.1 tag + demo**
- **Release:** v0.1 (tag `v0.1.0`)
- **Primary Objective:** Close out P0 by merging ADRs, signing team norms, completing the risk register, and tagging v0.1. The demo is "log in to deployed URL" (a placeholder page is acceptable; the system runs).

#### Backend Pod

##### Objective
Merge ADRs 1–5, finalize the contributing guide, and prepare the auth work for W5 kickoff. Ensure the codebase passes all CI checks on `main`.

##### Tasks

**Task:** Incorporate pod-lead review comments on ADRs 1–5; move status from `Proposed` to `Accepted`. Add the ADR index file `docs/adr/README.md` listing all ADRs with status and last-updated date.
**Why:** Roadmap DM-2 (W4) requires "First 5 ADRs merged"; Roadmap §Documentation Strategy mandates an ADR index. Tech Spec Sections 7, 8, 18, 19, 26 are the source material.
**Expected Output:** All 5 ADRs marked `Accepted` and merged to `main`; `docs/adr/README.md` index published.
**Dependencies:** ADR drafts (W1); pod-lead reviews (W1–W3).
**Handoff:** ADRs visible to all engineers; future ADRs (6–17) follow the same template.
**Definition of Done:** 5 ADRs merged; index page renders in Docusaurus (W8 task); TPM confirms in W4 retro.

**Task:** Co-author `CONTRIBUTING.md` with TPM: branching model (trunk-based with short-lived feature branches), commit conventions (Conventional Commits), PR rules (1 reviewer, 2 for frozen interfaces), code review checklist, how to run tests locally, how to add a new module. Add `CODEOWNERS` file mapping each top-level directory to a pod lead.
**Why:** Roadmap DM-3 (W4) requires `CONTRIBUTING.md` + `README.md`; Roadmap §Git Workflow specifies the rules; CODEOWNERS enforces PR review routing.
**Expected Output:** `CONTRIBUTING.md`, `CODEOWNERS` committed.
**Dependencies:** Repo structure (W1); TPM collaboration.
**Handoff:** All engineers onboard using the guide from W5 onward.
**Definition of Done:** PR template auto-fills with the checklist; CODEOWNERS triggers correct reviewer requests.

**Task:** Write the first tech-debt register entry: "P0 tech debt: auth module scaffold returns 501; Pod A-1 to implement in W5." Add `docs/tech-debt.md` with the register format.
**Why:** Roadmap §Documentation Strategy mandates a tech debt register with type, interest rate, principal, owner. W12 has the first formal "tech debt sweep" — entries must accumulate from W4.
**Expected Output:** `docs/tech-debt.md` with at least 1 entry.
**Dependencies:** None.
**Handoff:** All Pod leads add entries as they accrue; reviewed at every monthly milestone review.
**Definition of Done:** Register exists; TPM reviews at W4 retro; first entry has owner + payoff date.

#### AI/ML & Data Pod

##### Objective
Wrap up P0 by completing the spike methodologies and adding a research-spike template. Confirm the LiteLLM gateway plan is ready for W7 implementation.

##### Tasks

**Task:** Add a `docs/templates/research-spike.md` template: research question, candidates/options, evaluation criteria, experiment design, expected evidence, decision/output. Use the OCR spike (W5) and embedding spike (W5) as the first two instances.
**Why:** Roadmap §RESEARCH / SPIKE TASKS section mandates this structure; PB-01, PB-02, PB-03 all reference spike outputs. The template must exist before the W5 spikes run.
**Expected Output:** `docs/templates/research-spike.md`; two instances opened as `docs/spikes/ocr-spike.md` and `docs/spikes/embedding-spike.md` (status: Not Started).
**Dependencies:** Spike methodologies (W2).
**Handoff:** Spike owners (B-Lead for OCR, B-1 for embeddings) fill in the experiment and decision sections in W5.
**Definition of Done:** Template merged; two spike instances exist with the methodology referenced.

**Task:** Review the LiteLLM gateway deployment plan (W1) with D-Lead; confirm the Docker image, port, provider config, and key rotation strategy. Pre-pull the `litellm/proxy` Docker image to staging.
**Why:** W7 sprint requires "LiteLLM proxy deployed; key rotation; cost tracking." Pre-pulling the image saves deploy time in W7.
**Expected Output:** Plan signed off by D-Lead; `litellm/proxy` image pre-pulled on staging.
**Dependencies:** LiteLLM gateway plan (W1).
**Handoff:** Pod D implements the deploy in W7 using the pre-pulled image.
**Definition of Done:** Plan reviewed; image cached on staging; `docker images | grep litellm` returns the image.

**Task:** Run a quick "quality smell test" on the demo PDF using BGE-M3 + a sample RAG prompt via the OpenAI API (cloud, since LiteLLM gateway isn't deployed yet). Verify the pipeline concept produces a cited answer.
**Why:** This is a de-risking exercise: if the end-to-end pipeline (chunk → embed → retrieve → LLM) produces garbage even on a clean PDF, we know in W4 — not W16. R-02 (RAG quality, score 16) starts mitigation here.
**Expected Output:** A short report `tests/data/demo_pdf/v0.4_smell_test.md` with 3 sample Q&A pairs and observations.
**Dependencies:** Demo PDF; BGE-M3 (W3); OpenAI API access.
**Handoff:** Report shared with B-Lead; if quality is poor, spike scope expands in W5.
**Definition of Done:** 3 Q&A pairs generated; at least 2 with correct citations; report committed.

#### Frontend Pod

##### Objective
Polish the skeleton for the v0.1 demo: a clean login page (visual only, no auth yet), responsive layout, dark mode toggle. Confirm Storybook deploy.

##### Tasks

**Task:** Build a polished login page at `/login` using shadcn/ui `Card`, `Input`, `Button`, `Label` components. Visual only — the form does not submit (Pod A-1 wires it in W5). Dark mode toggle in the topnav. Responsive on mobile (best-effort, per OOS-8).
**Why:** Roadmap v0.1 milestone requires "login page on deployed URL"; the v0.1 demo (W4 Friday) shows this page. First impression for the team and advisor.
**Expected Output:** `frontend/src/app/(auth)/login/page.tsx` + `frontend/src/components/auth/LoginForm.tsx`; dark mode toggle in `Topnav.tsx`.
**Dependencies:** Design tokens (W2); app shell (W3).
**Handoff:** Pod A-1 wires the form to `/v1/auth/login` in W5; Pod C-1 builds the register page in W5.
**Definition of Done:** Page renders on staging; dark mode toggle persists in localStorage; Lighthouse accessibility ≥ 90.

**Task:** Deploy Storybook to Chromatic (free tier) and add a CI job that runs visual regression on every PR. Document the Storybook URL in `README.md`.
**Why:** Roadmap W2 sprint requires "Storybook shows base components"; visual regression catches UI breaks before merge. Roadmap §Testing Strategy covers frontend unit tests.
**Expected Output:** `.github/workflows/storybook.yml` running `chromatic` on every PR; Chromatic project ID configured in GitHub secrets.
**Dependencies:** Storybook configured (W1); Chromatic account.
**Handoff:** Every Pod C PR gets a Chromatic diff; C-Lead reviews visual changes.
**Definition of Done:** A PR with a deliberate Button color change shows a Chromatic diff; PR is blocked until the change is accepted.

#### DevOps / QA Pod

##### Objective
Finalize the eval harness scaffold in CI (TM-1), complete the risk register v1, and prepare the v0.1 tag. Run the first end-to-end smoke test on staging.

##### Tasks

**Task:** Wire the eval harness scaffold into CI: add a `eval` job to `.github/workflows/ci.yml` that runs `python -m app.eval run dummy --dataset tests/data/dummy.json` on every PR. Add a `backend/app/eval/evaluators/` directory for future evaluators (RAG, KG, adaptation).
**Why:** TM-1 (W4) requires "Unit test infra in CI"; TM-4 (W15) requires "RAG golden set v1; eval script runs in CI." The scaffold must be wired now so W15's RAG evaluator plugs in without CI changes.
**Expected Output:** Updated `.github/workflows/ci.yml` with eval job; `backend/app/eval/evaluators/__init__.py`.
**Dependencies:** Eval harness scaffold (W2).
**Handoff:** Pod B adds the RAG evaluator in W15; Pod D adds the KG sanity evaluator in W24 and the adaptation evaluator in W33.
**Definition of Done:** CI runs the dummy evaluator on every PR; job passes on a clean PR; job fails if the dummy evaluator errors.

**Task:** Complete the risk register v1 with all 32 risks: each has L, I, Score, Owner, Mitigation, Trigger, Status. Review at W4 retro. Identify the top 3 risks to actively manage in P1 (typically R-01 OCR, R-02 RAG, R-22 Pod B overload).
**Why:** Roadmap W4 sprint requires "Risk register v1 + eval harness scaffold"; biweekly risk review starts W2; first formal review at W4 retro.
**Expected Output:** `docs/risk-register.md` finalized; GitHub Project board synced.
**Dependencies:** Risk register seeded (W1).
**Handoff:** TPM owns the register from W5 onward; biweekly review at retros; top 3 risks have active mitigations tracked weekly.
**Definition of Done:** 32 risks documented; top 3 have weekly status updates; reviewed at W4 retro.

**Task:** Run the first end-to-end smoke test on staging: open the staging URL in a browser; click through the login page; verify the backend `/health` returns 200; verify Postgres is reachable; verify the staging deploy workflow runs on merge. Document the smoke test script `scripts/smoke_test.sh` for reuse.
**Why:** TM-1 (W4) is "Unit test infra in CI" but the smoke test is the operational equivalent for staging; every deploy from W3 onward runs this. v0.1 demo requires a working staging URL.
**Expected Output:** `scripts/smoke_test.sh` (curl-based checks for `/health`, `/`, and Postgres connectivity).
**Dependencies:** Both apps deployed to staging (W3).
**Handoff:** Smoke test runs automatically after every staging deploy (Pod D W3 task).
**Definition of Done:** Smoke test passes on staging; script committed; v0.1 demo (Friday W4) uses it as a pre-flight check.

**Task:** Tag `v0.1.0` on `main` after the W4 Friday demo passes. Cut a GitHub Release with release notes referencing the v0.1 milestone criteria.
**Why:** Roadmap v0.1 milestone (Sep 12, 2026 = W6, but tag may be cut earlier if criteria met; W4 demo confirms readiness). Version Roadmap table lists v0.1 as W6 target, but P0 exit (W4) requires v0.1 tag if criteria met.
**Expected Output:** Git tag `v0.1.0` pushed; GitHub Release published.
**Dependencies:** All W4 DoD items above.
**Handoff:** TPM announces v0.1 to the team + advisor; P1 starts W5.
**Definition of Done:** Tag exists; release notes reference ADRs 1–5, MVP definition, deploy URLs.

#### Cross-Pod Integration

- **Backend ↔ Frontend:** Login page renders on staging; backend `/health` is reachable from the frontend (CORS verified).
- **Backend ↔ DevOps/QA:** ADRs 1–5 merge informs CI rules (e.g., API versioning ADR-003 means CI lints `/v1/` prefix on all routes); risk register assigns owners across all pods.
- **AI/ML ↔ DevOps/QA:** Eval harness scaffold is wired into CI; Pod B will plug the RAG evaluator in W15.
- **TPM ↔ All Pods:** Risk register, contributing guide, ADR index, tech-debt register — all owned by TPM in collaboration with pod leads.
- **End-to-end:** A user opens staging URL → sees login page → backend is reachable → DB has users table → CI passes → tag v0.1.0 cut.

#### Week 4 Definition of Done

1. ADRs 1–5 marked `Accepted` and merged.
2. `CONTRIBUTING.md`, `CODEOWNERS`, `docs/tech-debt.md` committed.
3. v0.1 milestone criteria met (Roadmap Gate 1 list, but for v0.1: repo + CI + dev env + empty Next.js + FastAPI + auth scaffold + hello-world deploy).
4. Eval harness scaffold runs in CI on every PR.
5. Risk register v1 reviewed at W4 retro; top 3 risks identified.
6. Login page rendered on staging; Storybook deployed to Chromatic; visual regression in CI.
7. LiteLLM gateway plan signed off; image pre-pulled to staging.
8. Demo PDF smell test passes (3 Q&A pairs, 2+ with correct citations).
9. End-to-end smoke test passes on staging.
10. **v0.1.0 tag cut; GitHub Release published; Friday demo passes (login page on staging URL).**

---



### Week 5 — Auth + OCR/Embedding Spikes Begin

#### Roadmap Context

- **Phase:** P1 Foundations
- **Milestone:** Auth: register + login; Auth UI; OCR spike; Embedding spike
- **Release:** v0.2 prep
- **Primary Objective:** Ship the auth foundation (backend + UI) and run the OCR + embedding spikes in parallel. P1 starts the boring-but-required backbone: nothing AI-related ships here, but Pod B uses P1 to de-risk P2.

#### Backend Pod

##### Objective
Implement the auth flow (register, login, JWT issue/refresh) with ≥ 80% test coverage. Freeze the auth token format (Contract 10) by EOD Friday so Pod C can build against it.

##### Tasks

**Task:** Implement the `/v1/auth/register` endpoint: accept `UserCreate` (email, password), hash password with bcrypt(12 rounds), insert into `users` table, return `UserRead` (no password_hash). Validate email format and password strength (min 8 chars, 1 uppercase, 1 digit). Return 409 on duplicate email.
**Why:** Roadmap W5 sprint requires "Email/password register, login, JWT issue/refresh; tests"; Tech Spec Section 24.1 mandates bcrypt(12) for password hashing. Auth is the foundation for everything (Contract 10 frozen at W8).
**Expected Output:** `app/api/v1/auth.py::register` route; `app/services/auth_service.py::register_user`; unit tests covering happy path + 5 error cases (duplicate email, weak password, invalid email, missing fields, db error).
**Dependencies:** Users table migration (W3); `fastapi-users` library (W3 scaffold).
**Handoff:** Pod C-1 builds the register page UI calling this endpoint; Pod A-2 implements login (W5 also, possibly A-1 and A-2 split).
**Definition of Done:** Endpoint returns 201 on valid input; 409 on duplicate; 422 on validation error; coverage ≥ 80% on auth module.

**Task:** Implement the `/v1/auth/login` endpoint: accept `UserLogin` (email, password), verify password against `password_hash`, issue JWT access token (24h expiry) + refresh token (7d expiry), return `TokenResponse`. Configure JWT secret from env var.
**Why:** Same sprint; Tech Spec Section 22.2 mandates JWT with refresh tokens; Contract 10 (auth token format) freezes at W8.
**Expected Output:** `app/api/v1/auth.py::login`; `app/services/auth_service.py::authenticate_user`; `app/services/jwt_service.py` (encode/decode/refresh); unit tests ≥ 80% coverage.
**Dependencies:** Register endpoint (above); `pyjwt` library.
**Handoff:** Pod C-1 wires the login form to this endpoint; Pod A-2 implements RBAC middleware (W6).
**Definition of Done:** Login returns 200 + tokens on valid creds; 401 on invalid; refresh endpoint returns new access token; tests pass.

**Task:** Draft ADR-006 (auth token format): JWT claims structure (`sub` = user_id, `role` = student/instructor/admin, `exp`, `iat`, `jti`), refresh flow (refresh token rotates on use), token revocation strategy (blacklist on logout). Mark `Proposed`; move to `Accepted` at W8 with Contract 10 freeze.
**Why:** Contract 10 (auth token format) freezes at W8 (Roadmap §Frozen Interface Contracts); the ADR is the frozen artifact.
**Expected Output:** `docs/adr/006-auth-token-format.md` (status `Proposed`).
**Dependencies:** JWT implementation (above); Tech Spec Section 22.2.
**Handoff:** Pod C reviews the claims structure for frontend parsing; Pod A-2 finalizes at W8.
**Definition of Done:** ADR opened as PR; C-Lead + B-Lead reviewed; ready for W8 freeze.

#### AI/ML & Data Pod

##### Objective
Run the OCR spike (B-Lead) and embedding spike (B-1) in parallel, using the methodologies from W2. Both spikes must produce a choice ADR by EOD Friday.

##### Tasks

**Task:** Run the OCR spike per `docs/spikes/ocr-spike.md`: process the 20-PDF golden set through PaddleOCR, Tesseract, and Google Document AI. Measure character error rate, word error rate, layout preservation, Arabic character accuracy, latency, and memory for each. Write a decision matrix; recommend PaddleOCR as primary with Tesseract fallback (per Roadmap stack lock) or invoke PB-01 trigger if quality < 90%.
**Why:** Roadmap W5 sprint requires "Compare PaddleOCR vs Tesseract vs Document AI on 5 sample PDFs; choice ADR drafted." PB-01 (R-01) trigger metric is "< 90% success rate on the 20-PDF golden set at W10 demo" — the spike produces the baseline measurement now.
**Expected Output:** Filled `docs/spikes/ocr-spike.md` with results table + recommendation; ADR-007 (OCR choice) opened.
**Dependencies:** 20-PDF golden set (W1); all 3 OCR engines installed (W3); spike methodology (W2).
**Handoff:** ADR-007 reviewed by B-Lead, D-Lead; informs the W9 OCR pipeline implementation.
**Definition of Done:** 20 PDFs processed through all 3 engines; metrics table complete; recommendation is PaddleOCR primary + Tesseract fallback unless PB-01 triggers.

**Task:** Run the embedding spike per `docs/spikes/embedding-spike.md`: embed 10–20 Arabic+English query-chunk pairs with BGE-M3 (local) and OpenAI text-embedding-3-small (cloud). Measure retrieval accuracy (precision@5), latency per batch (10 chunks, 100 chunks, 1000 chunks), memory footprint, and dim size. Recommend BGE-M3 as primary (per Roadmap stack lock) with OpenAI as F-3 fallback.
**Why:** Roadmap W5 sprint requires "Compare BGE-M3 vs OpenAI text-embedding-3-small on quality + latency; choice ADR drafted." W12 embedding batch job depends on the choice.
**Expected Output:** Filled `docs/spikes/embedding-spike.md`; ADR-008 (embedding choice) opened.
**Dependencies:** Both models installed (W3); spike methodology (W2).
**Handoff:** ADR-008 reviewed by B-Lead; informs W12 embedding pipeline.
**Definition of Done:** Both models benchmarked; recommendation is BGE-M3 primary with documented F-3 trigger.

**Task:** Implement the first PAL provider: `PaddleOCRProvider` in `backend/app/pal/providers/ocr/paddleocr_provider.py` implementing `OCRInterface.extract_text(image) -> OCRResult` and `extract_text_batch(images) -> List[OCRResult]`. Include `health_check()` that verifies the model is loaded.
**Why:** W9 OCR pipeline implementation depends on having the provider ready. Tech Spec Section 8.1 mandates all providers implement the interface.
**Expected Output:** `PaddleOCRProvider` class with type-annotated methods; unit tests with sample images.
**Dependencies:** PAL interfaces (W1); PaddleOCR install (W3).
**Handoff:** Pod B-Lead uses this in the W9 OCR pipeline worker.
**Definition of Done:** `provider.extract_text(sample_image)` returns text + bounding boxes; `health_check()` returns True when model loaded.

#### Frontend Pod

##### Objective
Build the register and login pages, wire them to the backend, handle auth state in the frontend, and protect routes. First real API integration.

##### Tasks

**Task:** Implement the register page at `/register` using the `LoginForm` pattern from W4. Form fields: email, password, confirm password. Client-side validation (Zod schema matching backend). On submit, `POST /v1/auth/register` via TanStack Query mutation. Handle 409 (email taken), 422 (validation), success (redirect to `/login` with toast).
**Why:** Roadmap W5 sprint requires "Auth UI; Register/login pages, protected routes, session handling." Tech Spec Section 20.1 mandates TanStack Query for server state.
**Expected Output:** `frontend/src/app/(auth)/register/page.tsx`; `frontend/src/features/auth/api/useRegister.ts` (mutation hook); `frontend/src/features/auth/schemas.ts` (Zod schemas).
**Dependencies:** Backend `/v1/auth/register` (W5 Pod A); design tokens (W2).
**Handoff:** User can register on staging; Pod A-2 wires login (W5).
**Definition of Done:** Register form submits to backend; success redirects to `/login`; errors render inline; Lighthouse a11y ≥ 90.

**Task:** Implement the login page at `/login`: form fields email + password. On submit, `POST /v1/auth/login` via TanStack Query. Store tokens in `httpOnly` cookies (via Next.js server action) or in-memory + refresh-on-401 interceptor. Protect routes via middleware (`src/middleware.ts`) that redirects to `/login` if no valid token.
**Why:** Roadmap W5 sprint; Tech Spec Section 22.2 mandates JWT; Tech Spec Section 20.1 mandates Zustand for client state (token) + TanStack Query for server state.
**Expected Output:** `frontend/src/app/(auth)/login/page.tsx`; `frontend/src/features/auth/api/useLogin.ts`; `frontend/src/middleware.ts`; `frontend/src/stores/auth-store.ts` (Zustand).
**Dependencies:** Backend `/v1/auth/login` (W5 Pod A); register page (above).
**Handoff:** Pod C-2 builds the protected dashboard page (W6); user can log in and reach `/dashboard`.
**Definition of Done:** Login persists across refresh (token in cookie); protected routes redirect; logout clears token; tests with React Testing Library.

#### DevOps / QA Pod

##### Objective
Stand up async job infrastructure (Celery + Redis) for the W9 OCR pipeline, and begin observability baseline (logs, metrics, Sentry).

##### Tasks

**Task:** Deploy Redis 7 to staging (Docker container with persistence + password auth). Configure Celery 5 with the Redis broker; create `backend/app/workers/celery_app.py` with task serialization (JSON), task routes (e.g., `ocr_tasks` → `ocr_queue`), and a `celery beat` schedule for periodic tasks (placeholder). Deploy Flower dashboard for monitoring.
**Why:** Roadmap W7 sprint requires "Celery + Redis running; sample task; Flower dashboard." W9 OCR pipeline depends on async jobs being ready. Tech Spec Section 19.2 mandates async processing for OCR/chunking/embedding.
**Expected Output:** `infra/docker-compose.staging.yml` adds `redis` + `celery_worker` + `flower` services; `backend/app/workers/celery_app.py`; a sample task `app/workers/tasks/sample.py` that logs "hello."
**Dependencies:** Staging infra (W1–W3).
**Handoff:** Pod B uses the task queue for W9 OCR; Pod A uses it for W13 embedding batch.
**Definition of Done:** A queued sample task completes; Flower dashboard shows it; Redis persists across restarts.

**Task:** Begin observability baseline: deploy Loki (log aggregation), Prometheus (metrics), and Sentry (error tracking). Configure `structlog` in the backend for structured JSON logs to stdout (Loki picks them up). Configure Sentry SDK in both backend and frontend.
**Why:** Roadmap W7 sprint requires "Logs to Loki, metrics to Prometheus, Sentry for errors; a test error appears in Sentry." Tech Spec Section 26.1 mandates structlog + Sentry.
**Expected Output:** `infra/docker-compose.staging.yml` adds `loki` + `prometheus` + `grafana` services; backend `structlog` config; `frontend/src/lib/sentry.ts` initialized; a `/test/error` endpoint that throws an exception.
**Dependencies:** Staging infra.
**Handoff:** All pods ship logs to Loki + errors to Sentry from W5 onward; Pod D builds Grafana dashboards in W7.
**Definition of Done:** A test error appears in Sentry within 30s; logs visible in Loki; Prometheus scrapes backend metrics.

**Task:** Write integration tests for the auth endpoints (register + login + refresh) against the real staging Postgres. Add to the CI integration-test job.
**Why:** Roadmap TM-2 (W8) requires "Auth + course CRUD unit tests; ≥ 80% line coverage." Integration tests (against real DB) are distinct from unit tests (mocked DB) per Roadmap §Testing Strategy.
**Expected Output:** `backend/tests/integration/test_auth.py` with 8+ test cases (happy path, 409, 422, 401, expired token, refresh rotation, etc.).
**Dependencies:** Auth endpoints (W5 Pod A); staging Postgres (W3).
**Handoff:** Pod A-2 extends these for course CRUD in W6.
**Definition of Done:** Tests pass in CI; coverage on auth module ≥ 80%; tests run in < 5 min.

#### Cross-Pod Integration

- **Backend ↔ Frontend:** First real API integration — register + login. ADR-006 (auth token format) is the contract surface; both Pods must respect it before W8 freeze.
- **Backend ↔ DevOps/QA:** Auth integration tests run in CI; Pod D's Postgres staging is the test bed.
- **AI/ML ↔ DevOps/QA:** Pod B's first PAL provider (`PaddleOCRProvider`) runs in Pod D's Celery worker container; Pod D verifies the worker can import it.
- **AI/ML ↔ Backend:** The OCR + embedding spikes inform the W9 pipeline design; ADR-007 and ADR-008 must merge before W9 starts.

#### Week 5 Definition of Done

1. Auth: register + login + JWT issue/refresh work on staging; ≥ 80% test coverage on auth module.
2. ADR-006 (auth token format) opened; reviewed by C-Lead + B-Lead.
3. OCR spike complete; ADR-007 (OCR choice) opened; recommendation is PaddleOCR primary + Tesseract fallback (or PB-01 trigger documented).
4. Embedding spike complete; ADR-008 (embedding choice) opened; recommendation is BGE-M3 primary.
5. First PAL provider (`PaddleOCRProvider`) implemented with unit tests.
6. Register + login pages work on staging; protected routes redirect; tokens persist.
7. Redis + Celery + Flower running on staging; sample task completes.
8. Loki + Prometheus + Sentry deployed; test error appears in Sentry.
9. Auth integration tests pass in CI.
10. Friday demo: register → login → reach `/dashboard` → log out.

---

### Week 6 — User Mgmt + Course CRUD + v0.1 Tag

#### Roadmap Context

- **Phase:** P1 Foundations
- **Milestone:** v0.1 deployed (skeleton on real URL); user mgmt: profile + RBAC; course CRUD API; course UI; file upload to S3/MinIO
- **Release:** v0.1 (W6 target)
- **Primary Objective:** Land user profile + RBAC, course CRUD, file upload, and the course UI. v0.1 is officially tagged this week (per Version Roadmap table).

#### Backend Pod

##### Objective
Implement user profile CRUD, RBAC middleware (3 roles: student/instructor/admin), and the course CRUD API. Stand up the file upload pipeline (presigned URLs to MinIO).

##### Tasks

**Task:** Implement the `/v1/users/me` (GET profile), `/v1/users/me` (PUT update profile) endpoints. Profile fields per Tech Spec Section 15.1 (subset for v1.0: education_level, major, university, preferred_language, learning_style_vark, daily_available_minutes — full CSP comes in W30). Add the `profiles` table migration.
**Why:** Tech Spec Section 15 defines the CSP; v1.0 ships a subset of profile fields. RBAC middleware enforces that users can only update their own profile.
**Expected Output:** `app/api/v1/users.py` with GET + PUT; `app/services/profile_service.py`; Alembic migration for `profiles` table.
**Dependencies:** Auth (W5); users table (W3).
**Handoff:** Pod C-2 builds the profile UI in W7; Pod B uses the profile data in W30 cognitive model.
**Definition of Done:** Profile CRUD works; only the authenticated user can read/update their profile; tests ≥ 80%.

**Task:** Implement RBAC middleware: 3 roles (student, instructor, admin) per Roadmap OOS-aligned scope (Tech Spec's 5 roles reduced to 3 per C-6 resolution). Roles stored in `users.role` column. Middleware `app/middleware/rbac.py` reads the JWT `role` claim and enforces route-level permissions (e.g., only `instructor` can POST `/v1/courses`).
**Why:** Tech Spec Section 22.2 defines roles; Roadmap restricts to 3 for v1.0 (per C-6 resolution). RBAC is the foundation for course ownership (instructor creates, student enrolls).
**Expected Output:** `app/middleware/rbac.py`; `app/api/deps.py::require_role(role)` dependency; tests covering all role × endpoint combinations.
**Dependencies:** JWT (W5); role column in users table (migration this week).
**Handoff:** Pod A-Lead uses `require_role` on the course CRUD endpoints (below).
**Definition of Done:** Student cannot create a course (403); instructor can; admin can list all courses; tests pass.

**Task:** Implement the `/v1/courses` CRUD: POST (instructor only, sets `owner_id` = current user), GET (list — student sees enrolled courses; instructor sees owned; admin sees all), GET `/{id}` (membership check), PUT (owner only), DELETE (owner only). Add `courses` table migration with `id`, `owner_id`, `title`, `description`, `created_at`. Add `enrollments` table (`user_id`, `course_id`, `enrolled_at`).
**Why:** Roadmap W6 sprint requires "Course CRUD API; ownership checks." Tech Spec ER diagram includes `MATERIAL` owned by `USER`; `COURSE` is the parent of `MATERIAL`.
**Expected Output:** `app/api/v1/courses.py`; `app/services/course_service.py`; Alembic migration.
**Dependencies:** RBAC middleware (above); users table.
**Handoff:** Pod C-2 builds course UI in W6; IM-2 (W8) integrates frontend ↔ course API ↔ storage.
**Definition of Done:** All 5 CRUD operations work; ownership enforced; coverage ≥ 80%.

**Task:** Implement the file upload pipeline: `/v1/courses/{course_id}/materials/upload-url` returns a presigned MinIO/S3 URL; the browser uploads directly; `/v1/courses/{course_id}/materials` (POST) registers the upload in the DB (`materials` table: `id`, `course_id`, `title`, `s3_key`, `status='pending'`, `uploaded_by`, `created_at`). Add a virus-scan stub (TODO comment, real scan in W39 security review).
**Why:** Roadmap W6 sprint requires "File upload to S3/MinIO; presigned upload; server-side download; virus scan stub." Tech Spec Section 11.2 sequence diagram shows this flow.
**Expected Output:** `app/api/v1/materials.py`; `app/services/storage_service.py` (MinIO client); `materials` table migration.
**Dependencies:** MinIO deployed (Pod D W6); courses table (above).
**Handoff:** Pod B's W9 OCR pipeline reads `materials` rows with `status='pending'` and processes them.
**Definition of Done:** A PDF uploads to MinIO via presigned URL; material row created; `GET /v1/materials/{id}` returns metadata.

#### AI/ML & Data Pod

##### Objective
Implement the second and third PAL providers (Tesseract + Google Document AI fallbacks for OCR), and the BGE-M3 embedding provider. Continue spike follow-up: harden the chosen models.

##### Tasks

**Task:** Implement `TesseractOCRProvider` and `GoogleDocumentAIProvider` in `backend/app/pal/providers/ocr/`. Each implements `OCRInterface` and `health_check()`. Configure the OCR priority chain in `config.yaml`: PaddleOCR (primary) → Tesseract (fallback) → Document AI (escalation for hard cases).
**Why:** Tech Spec Section 9.2 mandates a 3-level degradation strategy (primary → fallback → safe fallback). F-6 trigger ("PaddleOCR quality too low on real PDFs") swaps to Document AI.
**Expected Output:** Two provider classes with unit tests; `config/providers.yaml` with the OCR priority chain.
**Dependencies:** PaddleOCRProvider (W5); OCR spike (W5).
**Handoff:** Pod B-Lead uses the chain in the W9 OCR pipeline worker.
**Definition of Done:** Each provider returns text + bounding boxes for sample images; priority chain documented.

**Task:** Implement `BGEEmbeddingProvider` in `backend/app/pal/providers/embedding/bge_provider.py` implementing `EmbeddingInterface.embed(text) -> EmbeddingResult` and `embed_batch(texts) -> List[EmbeddingResult]`. Return 1024-dim float32 vectors. `health_check()` verifies model loaded.
**Why:** W12 embedding batch job depends on this; F-3 trigger swaps to OpenAI provider.
**Expected Output:** `BGEEmbeddingProvider` class; unit tests verifying 1024-dim output for English + Arabic text.
**Dependencies:** BGE-M3 install (W3); embedding spike (W5).
**Handoff:** Pod B-1 uses this in the W12 embedding batch job.
**Definition of Done:** `provider.embed("hello")` returns a 1024-dim vector; batch of 100 chunks completes in < 5s.

**Task:** Implement `OpenAIEmbeddingProvider` as the F-3 fallback. Implement `LiteLLMReasoningProvider` (the cloud reasoning provider that calls LiteLLM gateway) — even though the gateway isn't deployed yet (W7), the provider class can be written and tested against OpenAI directly.
**Why:** F-3 trigger swaps BGE-M3 → OpenAI embeddings; the provider must exist for the swap to be a config change, not a code change. W7 deploys the LiteLLM gateway; the provider should be ready by then.
**Expected Output:** `OpenAIEmbeddingProvider` + `LiteLLMReasoningProvider` classes with unit tests (mocked API calls).
**Dependencies:** Embedding spike (W5); OpenAI API key (D-Lead).
**Handoff:** Pod D deploys LiteLLM in W7; Pod B-Lead uses the reasoning provider in W15 RAG prompt assembly.
**Definition of Done:** Both providers pass unit tests with mocked responses; provider swap is a `config.yaml` change.

#### Frontend Pod

##### Objective
Build the course list / create / edit UI (instructor-only). Implement the profile page. Prepare the file upload UI for W8 integration.

##### Tasks

**Task:** Implement the course list page at `/courses`: table of courses the user owns (instructor) or is enrolled in (student). "Create Course" button visible to instructors only. Empty state for new users. Pagination (10 per page).
**Why:** Roadmap W6 sprint requires "Course UI; Course list, create, edit pages; instructor-only." Tech Spec Section 20.2 lists Material Management UI as a primary frontend module.
**Expected Output:** `frontend/src/app/(student|instructor)/courses/page.tsx`; `frontend/src/features/courses/api/useCourses.ts` (TanStack Query); `frontend/src/features/courses/components/CourseTable.tsx`.
**Dependencies:** Backend `/v1/courses` GET (W6 Pod A); auth state (W5).
**Handoff:** Pod C-2 builds the create page (below); IM-2 (W8) integrates upload.
**Definition of Done:** List renders on staging; RBAC hides "Create" button from students; pagination works.

**Task:** Implement the create + edit course pages: `/courses/new` (instructor only) and `/courses/{id}/edit` (owner only). Form: title, description. On submit, POST/PUT to `/v1/courses`. Validate with Zod. Redirect to course detail page on success.
**Why:** Same sprint; instructor must be able to create a course for IM-2 (W8: instructor creates course + uploads PDF).
**Expected Output:** `frontend/src/app/(instructor)/courses/new/page.tsx`; `frontend/src/app/(instructor)/courses/[id]/edit/page.tsx`; mutation hooks.
**Dependencies:** Backend course CRUD (W6 Pod A); course list (above).
**Handoff:** Pod C-2 builds the course detail page (W7) that hosts the file upload.
**Definition of Done:** Instructor can create + edit courses; student gets 403; form validates; redirect works.

**Task:** Implement the profile page at `/profile`: editable form for the v1.0 subset of CSP fields (education_level dropdown, major, university, preferred_language, learning_style_vark quiz-style selector, daily_available_minutes slider). On submit, PUT `/v1/users/me`.
**Why:** Tech Spec Section 15 defines the CSP; v1.0 ships a subset; profile is the foundation for the cognitive model's P(L0) initialization in W30.
**Expected Output:** `frontend/src/app/(student)/profile/page.tsx`; `frontend/src/features/profile/api/useProfile.ts`.
**Dependencies:** Backend `/v1/users/me` (W6 Pod A); design tokens (W2).
**Handoff:** Pod B-2 (later) uses the profile data in the cognitive model; Pod C-2 will add VARK quiz UI in W29.
**Definition of Done:** Profile loads + saves; VARK selector renders as a 4-question quiz; form validates.

#### DevOps / QA Pod

##### Objective
Deploy MinIO to staging (object storage), monitor the auth endpoints with Sentry + Grafana, and prepare the async job integration tests.

##### Tasks

**Task:** Deploy MinIO to staging (Docker container with persistent volume, console UI on port 9001, S3-compatible API on port 9000). Create buckets: `openlearn-materials` (uploaded PDFs), `openlearn-artifacts` (extracted text, generated MCQs), `openlearn-backups` (DB backups). Configure access keys in GitHub Actions secrets.
**Why:** Pod A's W6 file upload pipeline depends on MinIO; Pod B's W9 OCR pipeline reads from it. Tech Spec Section 21.1 lists MinIO as the default object storage.
**Expected Output:** `infra/docker-compose.staging.yml` adds `minio` service; `scripts/init-minio-buckets.sh`; bucket creation scripted.
**Dependencies:** Staging infra.
**Handoff:** Pod A's `storage_service.py` connects to MinIO using the access keys; Pod B reads materials from MinIO in W9.
**Definition of Done:** MinIO console accessible; 3 buckets created; presigned URL upload works from a script.

**Task:** Build the first Grafana dashboard: "OpenLearn Staging Overview" with panels for: backend request rate, error rate (5xx), P95 latency, Postgres connections, Redis queue depth, Celery worker count. Configure Prometheus alertmanager for: 5xx rate > 5%, P95 > 5s, queue depth > 100.
**Why:** Roadmap W7 sprint requires "Logs to Loki, metrics to Prometheus, Sentry for errors"; Grafana dashboards are the visualization layer. Tech Spec Section 26.1 mandates Grafana + Prometheus.
**Expected Output:** `infra/grafana/dashboards/staging-overview.json`; `infra/grafana/alerts.yml`; alerts routed to Slack.
**Dependencies:** Loki + Prometheus + Sentry (W5).
**Handoff:** Pod D monitors staging during all P1+ sprints; alerts wake on-call (rotation starts W20).
**Definition of Done:** Dashboard renders on Grafana staging URL; a synthetic load test triggers the latency alert.

**Task:** Tag `v0.1.0` if not already tagged in W4. The Version Roadmap table lists v0.1 as W6 target (Sep 12, 2026). If W4 demo passed, tag exists; otherwise tag this week.
**Why:** Roadmap Version Roadmap targets v0.1 at W6.
**Expected Output:** Git tag `v0.1.0`; GitHub Release published.
**Dependencies:** All W4 + W5 + W6 DoD items.
**Handoff:** TPM announces v0.1; P1 continues toward v0.2 at W8.
**Definition of Done:** Tag exists; release notes reference auth + course CRUD + upload + UI shell; advisor notified.

#### Cross-Pod Integration

- **Backend ↔ Frontend:** Course list + create + edit + profile pages all call backend APIs. RBAC enforced on both sides.
- **Backend ↔ AI/ML:** Pod A's `materials` table is the input for Pod B's W9 OCR pipeline. Schema must be agreed this week (or W7 at latest).
- **Backend ↔ DevOps/QA:** Pod A's storage_service connects to Pod D's MinIO. Presigned URL generation requires shared access keys.
- **AI/ML ↔ DevOps/QA:** Pod B's PAL providers run inside Pod D's Celery worker container; Pod D verifies imports.
- **End-to-end:** Register → log in → create course → see it in list → edit profile. (Upload is W8 IM-2.)

#### Week 6 Definition of Done

1. v0.1.0 tagged and released.
2. User profile CRUD works (subset of CSP fields).
3. RBAC middleware enforces 3 roles on all endpoints.
4. Course CRUD API works; ownership enforced; ≥ 80% coverage.
5. File upload pipeline: presigned URL → MinIO → DB row created.
6. OCR PAL providers (PaddleOCR + Tesseract + Document AI) implemented; priority chain configured.
7. BGE-M3 + OpenAI embedding providers implemented.
8. LiteLLM reasoning provider implemented (mocked tests).
9. Course list + create + edit + profile pages work on staging.
10. MinIO deployed; 3 buckets created; Grafana dashboard live; alerts configured.

---

### Week 7 — Async Jobs + Observability + LLM Gateway

#### Roadmap Context

- **Phase:** P1 Foundations
- **Milestone:** Routing + nav; async job infra; observability baseline; LLM gateway
- **Release:** v0.2 prep
- **Primary Objective:** Complete the async job infrastructure, deploy the LiteLLM LLM gateway, and harden observability. Pod C finalizes routing + nav. This week is infrastructure-heavy: it sets up everything Pod B needs for W9+ AI pipeline work.

#### Backend Pod

##### Objective
Wire the async job infrastructure into the API: the API enqueues tasks, the worker consumes them, and progress is reported back via WebSocket. Build the WebSocket foundation for the W17 chat API.

##### Tasks

**Task:** Implement the task-enqueue pattern in the API: when a material is uploaded (W6), enqueue an OCR job by calling `celery_app.send_task("ocr.process_material", args=[material_id])`. Update the material's `status` to `queued`. Add a `/v1/materials/{id}/status` endpoint returning the current status (`pending`, `queued`, `processing`, `ready`, `failed`).
**Why:** Tech Spec Section 19.2 mandates async processing for OCR/chunking/embedding; Roadmap W7 sprint requires async job infra. W9 OCR pipeline picks up `queued` materials.
**Expected Output:** `app/services/material_service.py::enqueue_processing`; `app/api/v1/materials.py::get_status`; unit tests.
**Dependencies:** Celery + Redis (Pod D W5); materials table (W6).
**Handoff:** Pod B's W9 OCR worker task consumes the queue; Pod C's W9 UI polls `/status` or subscribes to WebSocket (W8).
**Definition of Done:** Uploading a material sets status to `queued` and enqueues a task; `/status` returns the current status; tests pass.

**Task:** Implement the WebSocket foundation for progress updates: `/ws/materials/{material_id}` connection that pushes `status` changes to the client when the worker reports them. Worker reports via Redis pub/sub; API subscribes and forwards to WS clients.
**Why:** Tech Spec Section 11.2 sequence diagram shows "WebSocket push 'Material ready'" after OCR completes. Tech Spec Section 22.1 lists WebSocket as the architecture for streaming operations.
**Expected Output:** `app/api/v1/ws/materials.py` WebSocket endpoint; `app/services/progress_publisher.py` (Redis pub/sub).
**Dependencies:** Redis (Pod D W5); async job infra (above).
**Handoff:** Pod C-1 subscribes to the WS in W9 UI; Pod A extends the pattern for `/ws/chat/{session_id}` in W17.
**Definition of Done:** A test job updates status; WS client receives the update within 1s; connection closes on material ready.

**Task:** Implement the `/v1/courses/{course_id}/materials` GET endpoint (list materials in a course, paginated, with status filter). Add `documents` table fields for OCR metadata (planned for W10): for now, just `materials` table with `id`, `course_id`, `title`, `s3_key`, `status`, `uploaded_by`, `created_at`, `updated_at`.
**Why:** W8 IM-2 integration requires frontend to list course materials; W10 will add the `documents` table for OCR output (per Roadmap W10 sprint "Document model + ingestion service").
**Expected Output:** `app/api/v1/materials.py::list_materials`; pagination helper.
**Dependencies:** Materials table (W6).
**Handoff:** Pod C-1 builds the course detail page (W7) listing materials; Pod A-2 adds the `documents` table in W10.
**Definition of Done:** Endpoint returns paginated materials; filter by status works; tests pass.

#### AI/ML & Data Pod

##### Objective
Begin the OCR pipeline implementation (worker task skeleton + first end-to-end test on the demo PDF). The actual OCR pipeline v1 ships in W9; this week is preparation.

##### Tasks

**Task:** Implement the OCR worker task skeleton: `app/workers/tasks/ocr.py::process_material(material_id)` that: (1) loads the material row from DB, (2) downloads the PDF from MinIO, (3) calls `OCRInterface.extract_text` via the PAL (priority chain: PaddleOCR → Tesseract → Document AI), (4) stores the extracted text + layout JSON in a `documents` table (migration next week, W10), (5) updates material status to `ready` or `failed`. Wrap each step in try/except with structured logging.
**Why:** W9 sprint requires "Async job: PDF → text + layout JSON; stored in DB." Building the skeleton now (against a temporary `documents` table or a JSON column on `materials`) lets W9 focus on OCR quality, not plumbing.
**Expected Output:** `app/workers/tasks/ocr.py`; `app/services/ocr_service.py` (orchestrates PAL calls); unit tests with a mock PDF.
**Dependencies:** Async job infra (Pod D W5); PAL OCR providers (W6); materials table (W6).
**Handoff:** Pod B-Lead hardens this in W9 to handle images, multi-page, scanned PDFs.
**Definition of Done:** Skeleton runs end-to-end on the demo PDF; produces text + layout JSON; updates status.

**Task:** Implement the chunking strategy: `app/services/chunking_service.py::chunk_document(text, layout) -> List[Chunk]` using LangChain's `RecursiveCharacterTextSplitter` (or `SemanticChunker` if available). Each chunk has: `id`, `material_id`, `text`, `chunk_index`, `page_range`, `section_title`, `language` (auto-detected), `difficulty_hint` (placeholder). Target ~500 words per chunk (per Tech Spec Section 11.5).
**Why:** Roadmap W11 sprint requires "Chunking strategy; recursive + semantic chunking; metadata (page, section); ADR." Tech Spec Section 11.5 specifies the chunk schema. Implementing now lets W11 focus on semantic chunking refinement + ADR.
**Expected Output:** `app/services/chunking_service.py`; `chunks` table migration; unit tests with sample text.
**Dependencies:** None (algorithm task).
**Handoff:** Pod B-Lead refines in W11 (semantic boundaries, metadata enrichment); Pod A exposes via `/v1/documents/{id}/chunks` (W11).
**Definition of Done:** 1 PDF → 100+ chunks with metadata; chunking runs in < 30s for a 100-page PDF.

**Task:** Draft ADR-009 (chunking strategy): recursive + semantic, ~500 word target, metadata schema, language detection approach. Reference LangChain text splitters. Mark `Proposed`.
**Why:** Roadmap W11 sprint requires "Chunking strategy; ADR"; Tier 1 Freeze (W20) requires Contract 2 (chunk schema) frozen.
**Expected Output:** `docs/adr/009-chunking-strategy.md`.
**Dependencies:** Chunking implementation (above); Tech Spec Section 11.5.
**Handoff:** Pod B-Lead finalizes in W11; freezes at W20.
**Definition of Done:** ADR opened; reviewed by A-Lead (consumer of chunk API).

#### Frontend Pod

##### Objective
Build the app shell polish: sidebar navigation, breadcrumbs, topnav with user menu, route guards, and the course detail page (hosting the file upload UI for W8).

##### Tasks

**Task:** Complete the app shell: sidebar with navigation items (Dashboard, Courses, Materials, Quizzes, Recommendations — placeholders for non-existent features). Topnav with user menu (Profile, Logout). Breadcrumbs based on the current route. Route guards: redirect to `/login` if no token; redirect to `/403` if role not authorized.
**Why:** Roadmap W7 sprint requires "App shell with sidebar, topnav, breadcrumbs, route guards." All routes exist as empty pages.
**Expected Output:** `src/components/layout/Sidebar.tsx`, `Topnav.tsx`, `Breadcrumbs.tsx`; `src/middleware.ts` updated with role-based redirects.
**Dependencies:** Auth state (W5); design tokens (W2).
**Handoff:** Pod C engineers populate each route with real content in P2+.
**Definition of Done:** All nav items render; breadcrumbs show current path; route guards work for all 3 roles.

**Task:** Build the course detail page at `/courses/{id}`: header (title, description, owner), tabs (Materials, Students, Settings), and the Materials tab content (list of materials with status badges, "Upload PDF" button visible to instructors). Empty state for new courses.
**Why:** W8 IM-2 requires "instructor creates course + uploads PDF" — the course detail page is the surface for this. Tech Spec Section 20.2 lists Material Management UI as a primary frontend module.
**Expected Output:** `frontend/src/app/(instructor)/courses/[id]/page.tsx`; `frontend/src/features/courses/components/MaterialsTab.tsx`.
**Dependencies:** Course CRUD API (W6); materials list endpoint (W7 Pod A).
**Handoff:** Pod C-1 wires the upload button to the presigned URL flow in W8.
**Definition of Done:** Course detail renders; materials list shows status badges; upload button visible to instructors only.

#### DevOps / QA Pod

##### Objective
Deploy the LiteLLM LLM gateway to staging with at least 2 providers configured (OpenAI + Anthropic, or OpenAI + GLM). Wire cost tracking and key rotation. Continue observability: log all LLM calls to Langfuse.

##### Tasks

**Task:** Deploy LiteLLM proxy to staging: Docker container running `litellm/proxy`, config file `infra/litellm-config.yaml` defining 2+ providers (OpenAI `gpt-4o-mini` + Anthropic `claude-3-5-sonnet` or GLM), key rotation via env vars, cost tracking enabled (LiteLLM's built-in `/spend` endpoint). Expose on port 4000.
**Why:** Roadmap W7 sprint requires "LiteLLM proxy deployed; key rotation; cost tracking." R-07 (LLM provider change, score 12) is structurally mitigated by this. ADR-005 (LLM gateway) is the binding decision.
**Expected Output:** `infra/docker-compose.staging.yml` adds `litellm` service; `infra/litellm-config.yaml`; keys in GitHub secrets.
**Dependencies:** LiteLLM plan (W1); pre-pulled image (W4).
**Handoff:** Pod B's `LiteLLMReasoningProvider` (W6) connects to this gateway; Pod B-Lead uses it in W15 RAG prompt assembly.
**Definition of Done:** `curl http://staging:4000/v1/chat/completions -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hello"}]}'` returns a response; `/spend` endpoint shows cost.

**Task:** Deploy Langfuse (open-source LLM observability) to staging. Configure the LiteLLM proxy to log all calls to Langfuse. Build a Grafana panel for LLM call rate, latency, cost, error rate.
**Why:** Tech Spec Section 26.1 mandates Langfuse; R-06 (LLM cost overruns, score 9) mitigation requires cost monitoring. Pod D owns the eval harness; Langfuse is the LLM-specific eval surface.
**Expected Output:** `infra/docker-compose.staging.yml` adds `langfuse` service; LiteLLM config updated; Grafana LLM dashboard.
**Dependencies:** LiteLLM gateway (above); Grafana (W6).
**Handoff:** Pod B monitors RAG prompt quality via Langfuse traces from W15 onward.
**Definition of Done:** A test LLM call appears in Langfuse with input/output/latency/cost; Grafana LLM panel renders.

**Task:** Write integration tests for the async job pipeline: enqueue a sample OCR task, verify it processes, verify status updates, verify WebSocket push. Add to CI integration-test job.
**Why:** Roadmap TM-3 (W12) requires "OCR pipeline integration tests; 5 sample PDFs; assertions on output schema." The harness must exist before W12.
**Expected Output:** `backend/tests/integration/test_async_pipeline.py` with 3 test cases (success, failure, timeout).
**Dependencies:** Async job infra (W5); WebSocket (W7 Pod A); OCR worker skeleton (W7 Pod B).
**Handoff:** Pod B extends with 5-PDF tests in W12 (TM-3).
**Definition of Done:** Tests pass in CI; run time < 5 min.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Pod A's enqueue pattern + WebSocket progress is the contract Pod B's worker must satisfy. Pod B's worker reports status via Redis pub/sub that Pod A's WS endpoint subscribes to.
- **Backend ↔ Frontend:** Course detail page (Pod C) calls materials list endpoint (Pod A). WebSocket for progress updates is the real-time integration.
- **AI/ML ↔ DevOps/QA:** Pod B's PAL providers run inside Pod D's Celery worker; LiteLLM gateway is consumed by Pod B's reasoning provider; Langfuse logs Pod B's LLM calls.
- **Backend ↔ DevOps/QA:** Pod A's async job infra depends on Pod D's Redis + Celery deployment.

#### Week 7 Definition of Done

1. Async job infra: API enqueues tasks, worker processes, status updates via WS.
2. WebSocket foundation for progress updates works.
3. Materials list endpoint paginated with status filter.
4. OCR worker skeleton runs end-to-end on demo PDF.
5. Chunking service implemented + chunks table migrated.
6. ADR-009 (chunking strategy) opened.
7. App shell complete (sidebar, topnav, breadcrumbs, route guards).
8. Course detail page renders with materials tab.
9. LiteLLM gateway deployed; 2 providers configured; cost tracking live.
10. Langfuse deployed; LLM calls logged; Grafana LLM panel renders.
11. Async pipeline integration tests pass in CI.

---

### Week 8 — Integration Week + v0.2 Tag

#### Roadmap Context

- **Phase:** P1 Foundations (final week)
- **Milestone:** Integration: course → upload → storage; first user-facing docs; **v0.2 tag + demo**
- **Release:** v0.2 (tag `v0.2.0`)
- **Primary Objective:** Close P1 with end-to-end integration: instructor creates course → uploads PDF → sees it listed. Tag v0.2. Freeze the auth token format (Contract 10). Publish API reference v1 and Docusaurus site.

#### Backend Pod

##### Objective
Complete the IM-2 integration (frontend ↔ course API ↔ storage). Freeze ADR-006 (auth token format, Contract 10). Publish OpenAPI-generated API reference.

##### Tasks

**Task:** Integrate the course → upload → storage flow: verify the frontend can call `/v1/courses/{id}/materials/upload-url`, upload to MinIO, then POST `/v1/courses/{id}/materials` to register the upload. Fix any CORS, auth, or RBAC issues that surface during integration. Add idempotency: re-uploading the same PDF (by content hash) doesn't create a duplicate material.
**Why:** Roadmap W8 sprint requires "Integration: course → upload → storage; end-to-end; instructor creates course, uploads PDF, sees it listed; E2E Playwright test passes." IM-2 milestone.
**Expected Output:** Bug fixes across `app/api/v1/materials.py`, `app/services/material_service.py`, `app/middleware/rbac.py`; idempotency check on content hash.
**Dependencies:** All W5–W7 work.
**Handoff:** Pod D's E2E Playwright test (TM-5, but a basic version runs at W8) verifies the flow on staging.
**Definition of Done:** Instructor creates course + uploads PDF + sees it listed; idempotency check prevents duplicates; E2E test green.

**Task:** Freeze ADR-006 (auth token format, Contract 10): move status from `Proposed` to `Accepted`. All pod leads sign. Document the JWT claims structure (`sub`, `role`, `exp`, `iat`, `jti`), refresh flow (rotation), and revocation strategy. Update the Tech Spec reference if needed.
**Why:** Roadmap §Frozen Interface Contracts: "Contract 10 frozen at W8." Post-freeze changes require a new ADR + migration + TPM approval + 2 pod leads' review.
**Expected Output:** ADR-006 marked `Accepted`; `docs/contracts/10-auth-token-format.md` with examples.
**Dependencies:** ADR-006 draft (W5); pod-lead review (W5–W7).
**Handoff:** All Pods respect the frozen contract from W9 onward; any change requires freeze exception.
**Definition of Done:** ADR merged; contract doc published; all pod leads + TPM sign.

**Task:** Publish the API reference v1: configure FastAPI's OpenAPI to export a complete spec (all v1 endpoints, schemas, examples). Deploy to the Docusaurus site (built by Pod C this week) at `docs.openlearn.ai/api/v1`. Add a CI check that the OpenAPI spec is up-to-date on every PR.
**Why:** Roadmap DM-4 (W8) requires "API reference v1 (auto-generated); OpenAPI spec published." DM-5 (W8) requires Docusaurus site live.
**Expected Output:** `infra/scripts/export-openapi.py` (dumps spec to `docs/static/openapi/v1.json`); CI check; Docusaurus API reference page.
**Dependencies:** All v1 endpoints implemented (W5–W7); Docusaurus site (Pod C W8).
**Handoff:** Pod C links the API reference from the Docusaurus sidebar; all engineers reference it for client work.
**Definition of Done:** `docs.openlearn.ai/api/v1` renders the spec; CI fails if a new endpoint isn't documented; spec versioned.

#### AI/ML & Data Pod

##### Objective
Verify the OCR worker skeleton processes real uploads. Begin the RAG eval harness planning (the harness ships in W15–W16, but planning starts now).

##### Tasks

**Task:** Run the OCR worker skeleton on 5 real uploads (the 5 sample PDFs from the golden set's "clean digital" category). Verify the end-to-end flow: material uploaded → task enqueued → worker processes → text + layout JSON stored → material status updated to `ready`. Document any failures.
**Why:** Roadmap W8 sprint implicitly requires the pipeline to be runnable end-to-end before P2 starts (W9). PB-01 trigger metric ("90% success on 20-PDF golden set at W10 demo") needs a baseline now.
**Expected Output:** Test report `docs/p1/ocr-pipeline-smoke-test.md` with results for 5 PDFs.
**Dependencies:** OCR worker skeleton (W7); async job infra (Pod D W5).
**Handoff:** Pod B-Lead hardens for the 20-PDF golden set in W10 (TM-3 is W12).
**Definition of Done:** 5/5 clean digital PDFs process successfully; report committed.

**Task:** Draft the RAG eval harness design doc `docs/rag-eval-harness.md`: 50 Q&A pairs format, faithfulness metric (Ragas or custom), relevance metric, evaluation script, CI integration plan. Plan for the golden set to be authored by Pod B + advisor in W14 (before the W15 freeze).
**Why:** Roadmap TM-4 (W15) requires "RAG golden set v1; 50 Q&A pairs; eval script runs in CI." PB-02 trigger metric ("Faithfulness < 0.7 OR relevance < 0.7 on 50-Q golden set at W16") needs the harness.
**Expected Output:** `docs/rag-eval-harness.md` (design + plan); `docs/eval/rag-golden-set-schema.md`.
**Dependencies:** Eval harness scaffold (Pod D W2).
**Handoff:** Pod B-Lead implements the harness in W15; Pod D integrates into CI.
**Definition of Done:** Design doc reviewed by D-Lead + B-Lead; plan is actionable for W14.

**Task:** Draft ADR-010 (embedding I/O contract — input text, output vector dim 1024, model_id field). Mark `Proposed`. This is Contract 3, frozen at W20.
**Why:** Tier 1 Architecture Freeze (W20) freezes Contract 3; the ADR must be drafted before freeze.
**Expected Output:** `docs/adr/010-embedding-io-contract.md`.
**Dependencies:** Embedding spike (W5); BGE-M3 provider (W6).
**Handoff:** Pod B-1 finalizes in W12 (embedding batch job week); freezes at W20.
**Definition of Done:** ADR opened; reviewed by A-Lead (consumer of embeddings via Vector DB).

#### Frontend Pod

##### Objective
Build and deploy the Docusaurus documentation site. Polish the upload UI for the v0.2 demo. Complete the integration with backend for the IM-2 milestone.

##### Tasks

**Task:** Build the Docusaurus site: install Docusaurus 3 in `docs/` directory, configure the sidebars (Architecture, ADRs, API Reference, Runbooks, Quickstarts), theme (matching the app design tokens), and deploy to a public URL (`docs.openlearn.ai` or a Vercel subdomain). Add the first content: Getting Started, Instructor Quickstart (W8 partial), Architecture overview (single-page diagram from the Tech Spec).
**Why:** Roadmap DM-5 (W8) requires "Docusaurus site live; public docs URL." DM-4 (W8) requires API reference linked.
**Expected Output:** `docs/` Docusaurus project; deployed to a public URL; sidebar configured; 3 initial docs (Getting Started, Instructor Quickstart, Architecture).
**Dependencies:** API reference (Pod A W8).
**Handoff:** TPM (Docs Owner rotation) maintains the site from W9 onward; all engineers contribute docs via PR.
**Definition of Done:** Docusaurus URL accessible from outside the team; sidebar renders; search works.

**Task:** Polish the upload UI on the course detail page: drag-and-drop zone, file type validation (PDF/PNG/JPEG), file size limit (50 MB per Roadmap v0.5 gate), upload progress bar, success toast, error toast. Connect to the presigned URL flow.
**Why:** Roadmap W8 IM-2 demo requires "instructor creates course + uploads PDF" — the UI must be polished for the demo. Tech Spec Section 11.2 sequence diagram shows the upload flow.
**Expected Output:** Updated `MaterialsTab.tsx` with `UploadZone.tsx` component; integration with `/upload-url` + PUT to MinIO + POST to register.
**Dependencies:** Backend upload pipeline (W6); WebSocket progress (W7).
**Handoff:** Pod C-1 demostrates this in the v0.2 Friday demo.
**Definition of Done:** Drag-and-drop works; progress bar shows upload + processing; success/error states render; demo passes.

**Task:** Build the v0.2 demo flow end-to-end: register as instructor → create course → upload PDF → see it in materials list with "processing" → wait for "ready" status → view extracted text (placeholder, real OCR text comes in W9). Add a basic E2E test with Playwright.
**Why:** Roadmap v0.2 milestone requires "instructor creates course + uploads PDF" demo on staging. TM-5 (W17) is the formal E2E milestone, but a basic version runs at W8.
**Expected Output:** `frontend/tests/e2e/instructor-upload.spec.ts` Playwright test; demo script.
**Dependencies:** All W5–W8 work.
**Handoff:** Pod D extends this test in W17 (TM-5) to cover the full student flow.
**Definition of Done:** E2E test passes on staging; demo runs without crash.

#### DevOps / QA Pod

##### Objective
Run the IM-2 E2E test on staging, validate auth + course CRUD coverage ≥ 80% (TM-2), and tag v0.2.0. Begin cross-training: 1 Pod A engineer shadows Pod D for 20% time on infra tasks (per Roadmap §Pod Cross-Training Plan).

##### Tasks

**Task:** Verify TM-2 milestone: auth + course CRUD unit tests with ≥ 80% line coverage. Run `pytest --cov=app/api/v1/auth --cov=app/api/v1/courses --cov-report=term` and confirm coverage. If below 80%, pair with Pod A to add tests.
**Why:** Roadmap TM-2 (W8) is a testing milestone that must be met for v0.2 to ship.
**Expected Output:** Coverage report; test additions if needed.
**Dependencies:** All W5–W8 Pod A work.
**Handoff:** Coverage report posted as a comment on the v0.2 release PR.
**Definition of Done:** Coverage ≥ 80% on auth + course CRUD modules; report committed.

**Task:** Run the E2E Playwright test (Pod C W8) on staging as part of the v0.2 demo prep. If any step fails, file bugs and pair with Pod A + Pod C to fix before Friday demo.
**Why:** v0.2 demo must pass on staging; E2E test is the automated guarantee.
**Expected Output:** Test results report; bug fixes if needed.
**Dependencies:** Pod C E2E test (W8); staging environment.
**Handoff:** v0.2 demo on Friday uses the E2E test as a pre-flight check.
**Definition of Done:** E2E test green on staging; demo ready.

**Task:** Tag `v0.2.0` on `main` after Friday demo passes. Cut a GitHub Release with release notes referencing: auth (register + login + JWT), RBAC (3 roles), course CRUD, file upload to MinIO, async job infra, LiteLLM gateway, Docusaurus site, API reference v1.
**Why:** Roadmap v0.2 milestone (Sep 26, 2026 = W8) is the P1 exit gate.
**Expected Output:** Git tag `v0.2.0`; GitHub Release published.
**Dependencies:** All W5–W8 DoD items.
**Handoff:** TPM announces v0.2; P2 (AI Pipeline) starts W9 with the critical path.
**Definition of Done:** Tag exists; release notes complete; advisor notified; demo video recorded (5-min screencast).

**Task:** Begin cross-training: 1 Pod A engineer spends 20% of W8 shadowing Pod D on infra tasks (deploying a service to staging, reading a Grafana dashboard, triaging a Sentry error). Document the cross-training plan in `docs/cross-training.md`.
**Why:** Roadmap §Pod Cross-Training Plan: "W4–W8: One Pod A engineer spends 20% time shadowing Pod D on infra tasks." Feature Freeze (W38) requires "≥ 3 people cross-trained on DevOps tasks" (Gate 4 sign-off).
**Expected Output:** `docs/cross-training.md` with the plan and W8 shadowing log.
**Dependencies:** Pod A + Pod D coordination.
**Handoff:** Pod A engineer continues shadowing through W8; Pod B engineer begins vector DB ops shadowing in W9.
**Definition of Done:** Pod A engineer can deploy a service to staging; can read a Grafana panel; can triage a Sentry error.

#### Cross-Pod Integration

- **Backend ↔ Frontend:** IM-2 integration is the headline: instructor creates course + uploads PDF on staging. WebSocket progress updates flow during the demo.
- **Backend ↔ AI/ML:** Pod A's `materials` table is the input Pod B's W9 OCR pipeline will consume. Schema validated.
- **AI/ML ↔ DevOps/QA:** Pod B's OCR worker skeleton runs in Pod D's Celery worker; integration tests verify.
- **Frontend ↔ DevOps/QA:** Docusaurus deploy; E2E test runs on staging.
- **TPM ↔ All Pods:** v0.2 release signed by all pod leads; risk register reviewed at W8 retro.
- **End-to-end:** Register → login → create course → upload PDF → see "processing" → see "ready" → view material. This is the IM-2 verifiable outcome.

#### Week 8 Definition of Done

1. IM-2 integration: instructor creates course + uploads PDF + sees it listed. E2E Playwright test green.
2. ADR-006 (auth token format) frozen as Contract 10; all pod leads sign.
3. API reference v1 published at `docs.openlearn.ai/api/v1`.
4. Docusaurus site live at public URL.
5. OCR worker skeleton processes 5 sample PDFs end-to-end.
6. RAG eval harness design doc merged.
7. ADR-010 (embedding I/O contract) opened.
8. Upload UI polished (drag-and-drop, progress, success/error states).
9. TM-2 met: auth + course CRUD coverage ≥ 80%.
10. **v0.2.0 tag cut; GitHub Release published; Friday demo passes; P2 starts W9.**

---



### Week 9 — OCR Pipeline v1 + Thin MVP Chat UI Scaffold

#### Roadmap Context

- **Phase:** P2 AI Pipeline (CRITICAL PATH begins)
- **Milestone:** OCR pipeline v1; OCR UI feedback + thin MVP chat UI scaffold
- **Release:** v0.3 prep
- **Primary Objective:** Ship OCR pipeline v1: async job that takes a PDF and produces text + layout JSON in the DB. Pod C scaffolds the chat UI for v0.4 thin MVP. The critical path starts here — every slip from W9 onward risks W16.

#### Backend Pod

##### Objective
Support Pod B's OCR pipeline v1 by adding the `documents` table (OCR output storage) and the `/v1/documents/{id}` endpoint. Continue vector DB deploy prep with Pod D.

##### Tasks

**Task:** Add the `documents` table migration per Contract 1 (frozen at W20, but drafted now): `id UUID PK`, `material_id FK`, `extracted_text TEXT`, `layout_json JSONB` (page-level text + bounding boxes), `ocr_engine VARCHAR` (which engine produced it), `language_detected VARCHAR`, `page_count INT`, `processed_at TIMESTAMP`, `processing_time_ms INT`. Add a corresponding SQLAlchemy model + Pydantic schema.
**Why:** Tech Spec Section 11.4 specifies OCR output structure; Roadmap W9 sprint requires "Async job: PDF → text + layout JSON; stored in DB." Contract 1 freezes at W20.
**Expected Output:** Alembic migration; `app/domain/document.py`; `app/repositories/document_repository.py`.
**Dependencies:** Materials table (W6).
**Handoff:** Pod B's OCR worker writes to this table; Pod A exposes via `/v1/documents/{id}`.
**Definition of Done:** Migration runs; model + schema validate; tests pass.

**Task:** Implement `/v1/documents/{id}` GET endpoint: returns the document's text, layout, metadata. Paginated text access via `?page=N`. RBAC: only the material's course owner or enrolled students can read.
**Why:** Roadmap W9 sprint requires "OCR UI feedback + thin MVP chat UI scaffold" — the UI needs to display extracted text. Tech Spec Section 22.3 lists `/materials/{id}/status` (W6 done) but `/documents/{id}` is the new endpoint.
**Expected Output:** `app/api/v1/documents.py::get_document`; pagination helper.
**Dependencies:** Documents table (above); RBAC (W6).
**Handoff:** Pod C-1 displays extracted text in the materials UI (W9); Pod B reads via service layer.
**Definition of Done:** Endpoint returns document + paginated text; RBAC enforced; tests pass.

**Task:** Begin Qdrant deploy prep with Pod D: write `infra/docker-compose.staging.yml` Qdrant service spec (single node, persistent volume, port 6333), collection schema design (vector dim 1024, payload fields: `material_id`, `chunk_id`, `page_range`, `section_title`, `language`). Plan the embedding write path: on chunk creation → Celery task → embed → store in Qdrant.
**Why:** Roadmap W13 sprint requires "Vector DB deploy (Qdrant) + embedding write path + search API." Prep now so W13 focuses on integration, not infra setup. Tech Spec Section 13.2 lists Qdrant.
**Expected Output:** Qdrant compose spec; collection schema design doc `docs/plans/qdrant-collection.md`.
**Dependencies:** MinIO + Celery + Redis (W5–W7).
**Handoff:** Pod D deploys Qdrant in W13; Pod A implements the search API in W13.
**Definition of Done:** Compose spec reviewed by D-Lead; collection design reviewed by B-Lead.

#### AI/ML & Data Pod

##### Objective
Ship OCR pipeline v1: async worker that takes a material, runs it through PaddleOCR (with Tesseract fallback), stores text + layout JSON in the `documents` table. Process the 5 sample PDFs (W8 smoke test) and verify text extraction.

##### Tasks

**Task:** Implement the OCR pipeline v1 worker: `app/workers/tasks/ocr.py::process_material(material_id)` (built on the W7 skeleton). The full flow: (1) load material row, (2) download PDF from MinIO, (3) parse with PyMuPDF for native text, (4) for pages with no native text, run PaddleOCR, (5) if PaddleOCR fails, run Tesseract as fallback, (6) merge results, (7) store text + layout JSON in `documents` table, (8) update material status to `ready`, (9) report progress via Redis pub/sub. Wrap in try/except with structured logging; on failure, set status to `failed` with an error message.
**Why:** Roadmap W9 sprint requires "Async job: PDF → text + layout JSON; stored in DB." Tech Spec Section 11.4 specifies the OCR processing flow. The critical path begins here.
**Expected Output:** `app/workers/tasks/ocr.py` (full implementation); `app/services/ocr_service.py` (orchestrator); unit + integration tests.
**Dependencies:** Documents table (Pod A W9); PAL OCR providers (W6); async job infra (W5–W7).
**Handoff:** Pod B-1 hardens for images, multi-page, scanned PDFs in W10; Pod C-1 displays extracted text in UI.
**Definition of Done:** 5 sample PDFs from W8 smoke test process successfully; text + layout JSON stored; status updates work; tests pass.

**Task:** Implement the OCR UI feedback hook: when OCR completes, the worker publishes a `material.ready` event to Redis pub/sub on the `materials:{material_id}` channel. Pod A's WebSocket endpoint (W7) forwards this to connected clients.
**Why:** Tech Spec Section 11.2 sequence diagram shows "WebSocket push 'Material ready'" as the final step.
**Expected Output:** Updated `app/workers/tasks/ocr.py` with the publish step; integration test verifying the WS client receives the event.
**Dependencies:** WebSocket foundation (W7).
**Handoff:** Pod C-1's UI subscribes to the WS and updates the material's status badge in real time.
**Definition of Done:** WS client receives `material.ready` event within 1s of OCR completion; test passes.

**Task:** Begin chunking service refinement: add semantic chunking (LangChain `SemanticChunker` or a custom sentence-embedding-based splitter). Add metadata enrichment: language detection (per chunk), difficulty hint (vocabulary frequency + sentence complexity), content type classification (definition / explanation / example / proof / problem — per Tech Spec Section 11.6).
**Why:** Roadmap W11 sprint requires "Chunking strategy; recursive + semantic chunking; metadata." Tech Spec Section 11.5–11.6 specifies semantic chunking + metadata enrichment. Implementing now lets W11 focus on the ADR and refinement.
**Expected Output:** Updated `app/services/chunking_service.py`; `app/services/metadata_enrichment.py`; unit tests on a sample document.
**Dependencies:** Chunking service skeleton (W7); BGE-M3 for semantic chunking (W6).
**Handoff:** Pod B-Lead finalizes in W11; Pod A exposes via `/v1/documents/{id}/chunks` (W11).
**Definition of Done:** Semantic chunking produces 100+ chunks from a 100-page PDF; metadata enrichment assigns language + difficulty + content type per chunk.

#### Frontend Pod

##### Objective
Build the OCR UI feedback (extracted text preview with loading state) and scaffold the thin MVP chat UI (single page, no auth, pre-loaded PDF). The chat UI ships at W16; scaffolding starts now.

##### Tasks

**Task:** Build the extracted text preview on the course detail page's Materials tab: when a material's status is `processing`, show a skeleton loader + progress bar (from WS). When `ready`, show the extracted text in a paginated viewer with page navigation. When `failed`, show an error message with a retry button.
**Why:** Roadmap W9 sprint requires "OCR UI feedback + thin MVP chat UI scaffold; Upload progress + extracted text preview." Tech Spec Section 20.2 lists Material Management UI as a primary module.
**Expected Output:** `frontend/src/features/materials/components/ExtractedTextViewer.tsx`; integration with WS for status updates.
**Dependencies:** Backend `/v1/documents/{id}` (W9 Pod A); WS foundation (W7).
**Handoff:** Pod C-1 demos this in W9 Friday demo; Pod B uses the preview to verify OCR quality.
**Definition of Done:** Loading → ready → failed states all render correctly; paginated text viewer works; WS updates status badge in real time.

**Task:** Scaffold the thin MVP chat UI at `/chat` (single page, no auth, no nav). Layout: header with demo PDF title, scrollable message list, input box at bottom, "Send" button. No backend integration yet — the chat box echoes input back with a "TODO: connect to RAG" placeholder. Style with shadcn/ui + design tokens.
**Why:** Roadmap W9 sprint requires "Thin MVP chat UI scaffolded." W16 v0.4 thin MVP requires this page to work end-to-end. Starting now lets W14–W16 focus on RAG integration, not UI.
**Expected Output:** `frontend/src/app/chat/page.tsx`; `frontend/src/features/chat/components/ChatMessageList.tsx`, `ChatInput.tsx`.
**Dependencies:** Design tokens (W2); shadcn/ui (W1).
**Handoff:** Pod C-Lead wires to backend in W17 (chat API + SSE streaming); for v0.4 (W16), Pod A-Lead + Pod C-Lead integrate a simplified backend.
**Definition of Done:** Page renders; input echoes back; layout is responsive; matches design tokens.

#### DevOps / QA Pod

##### Objective
Run TM-3 prep: write integration tests for the OCR pipeline (5 sample PDFs, assertions on output schema). Set up Qdrant backup script (runs daily, restores tested).

##### Tasks

**Task:** Write OCR pipeline integration tests: `backend/tests/integration/test_ocr_pipeline.py` covering 5 PDFs (3 clean digital, 1 scanned, 1 mixed Arabic+English). For each: enqueue the task, wait for `ready` status, verify `documents` table row exists with non-empty `extracted_text` and valid `layout_json`. Assert the schema matches Contract 1 (drafted this week by Pod A).
**Why:** Roadmap TM-3 (W12) requires "OCR pipeline integration tests; 5 sample PDFs; assertions on output schema." Pod D writes the test harness now so W12 is just running it on the final 5 PDFs.
**Expected Output:** `backend/tests/integration/test_ocr_pipeline.py`; 5 PDFs in `tests/data/ocr_test_pdfs/`.
**Dependencies:** OCR pipeline v1 (W9 Pod B); documents table (W9 Pod A).
**Handoff:** Pod B-1 finalizes the 20-PDF golden set test in W10; Pod D runs the formal TM-3 test in W12.
**Definition of Done:** 5 test PDFs process; schema assertions pass; test runs in < 5 min in CI.

**Task:** Write the Qdrant backup script: `scripts/backup_qdrant.sh` that snapshots the Qdrant collection to MinIO (`openlearn-backups/qdrant/{date}.tar.gz`). Test restore on a fresh Qdrant instance. Schedule daily backup via Celery beat.
**Why:** R-05 (Qdrant ops too heavy, score 9) mitigation requires backups; Tech Spec Section 21 lists Qdrant as the vector DB. Pod D owns Qdrant ops.
**Expected Output:** `scripts/backup_qdrant.sh`; restore procedure documented in `docs/runbooks/qdrant.md` (partial — full runbook in W39).
**Dependencies:** Qdrant deployed (W13 — but the script can be written now and tested against a local Qdrant).
**Handoff:** Pod D runs the backup daily from W13 onward; restore tested monthly.
**Definition of Done:** Backup creates a valid tarball; restore succeeds on a fresh Qdrant; daily schedule configured.

**Task:** Continue cross-training: Pod B engineer (B-1 or B-2) begins shadowing Pod D on vector DB ops (Qdrant backups, index rebuilds, monitoring) for 20% of W9. Per Roadmap §Pod Cross-Training Plan: "W9–W20: One Pod B engineer learns vector DB ops (Qdrant backups, index rebuilds)."
**Why:** R-05 mitigation; Feature Freeze (W38) requires 3 people cross-trained on DevOps.
**Expected Output:** `docs/cross-training.md` updated with W9 entry: Pod B engineer can run a Qdrant backup + restore.
**Dependencies:** Pod B + Pod D coordination.
**Handoff:** Pod B engineer continues shadowing through W20; can independently triage Qdrant issues by W20.
**Definition of Done:** Pod B engineer performs a backup + restore under Pod D supervision.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Pod A's `documents` table is the output target for Pod B's OCR worker. Schema validated this week (Contract 1 draft).
- **Backend ↔ Frontend:** Pod A's `/v1/documents/{id}` endpoint serves Pod C's extracted text viewer. WS for status updates.
- **AI/ML ↔ Frontend:** Pod B's OCR worker produces text that Pod C displays; WS event flow.
- **AI/ML ↔ DevOps/QA:** Pod B's worker runs in Pod D's Celery container; integration tests verify.
- **Backend ↔ DevOps/QA:** Qdrant deploy prep (joint); backup script.

#### Week 9 Definition of Done

1. `documents` table migrated; `/v1/documents/{id}` endpoint works.
2. Qdrant deploy prep done (compose spec + collection design).
3. OCR pipeline v1 processes 5 sample PDFs end-to-end; text + layout JSON stored.
4. WS event `material.ready` fires on completion; UI updates.
5. Chunking service refined (semantic + metadata enrichment).
6. Extracted text viewer renders with loading/ready/failed states.
7. Thin MVP chat UI scaffolded at `/chat`.
8. OCR pipeline integration tests written (5 PDFs).
9. Qdrant backup script written; restore tested locally.
10. Friday demo: upload PDF → see "processing" → see "ready" → view extracted text.

---

### Week 10 — OCR Hardening + Document Model

#### Roadmap Context

- **Phase:** P2 AI Pipeline
- **Milestone:** OCR hardening (images, multi-page, scanned); document model + ingestion service
- **Release:** v0.3 prep
- **Primary Objective:** Harden OCR for the 20-PDF golden set (PB-01 trigger metric). Add idempotency and the `documents` table fields needed for W11 chunking. Cross Pod B capacity allocation toward the W12 v0.3 demo.

#### Backend Pod

##### Objective
Harden the ingestion service: idempotency (re-upload doesn't duplicate), ingestion status tracking, and the document model expansion (OCR metadata fields). Begin the chunks table migration.

##### Tasks

**Task:** Implement ingestion idempotency: compute SHA-256 hash of uploaded PDF; check `materials.content_hash` column; if hash exists, return the existing material_id instead of creating a new row. Add the `content_hash` column via migration.
**Why:** Roadmap W10 sprint requires "Document model + ingestion service; idempotency; Re-uploading same PDF doesn't duplicate."
**Expected Output:** Migration adding `content_hash` to `materials`; `material_service.py::register_upload` checks hash first.
**Dependencies:** Materials table (W6).
**Handoff:** Pod C's upload UI handles the "already exists" response gracefully.
**Definition of Done:** Re-uploading the same PDF returns the existing material_id; no duplicate row created; tests pass.

**Task:** Expand the `documents` table with OCR metadata: `ocr_engine`, `ocr_version`, `confidence_score` (per-page average), `page_count`, `word_count`, `processing_time_ms`, `failed_pages` (array of page numbers that fell back to Tesseract or Document AI). Migration + updated Pydantic schema.
**Why:** Tech Spec Section 11.4 specifies OCR metadata; PB-01 evaluation requires per-page confidence; Pod D's eval harness needs `failed_pages` to track fallback frequency.
**Expected Output:** Migration; updated `Document` Pydantic schema; updated OCR worker to populate these fields.
**Dependencies:** Documents table (W9).
**Handoff:** Pod D's eval harness reads `failed_pages` to compute fallback rate (PB-01 trigger metric).
**Definition of Done:** Migration runs; OCR worker populates all fields; tests verify.

**Task:** Add the `chunks` table migration per Contract 2 (frozen at W20): `id UUID PK`, `document_id FK`, `material_id FK`, `chunk_index INT`, `text TEXT`, `page_range VARCHAR` (e.g., "12-13"), `section_title VARCHAR`, `language VARCHAR`, `difficulty_hint VARCHAR`, `content_type VARCHAR` (definition/explanation/example/proof/problem), `embedding_status VARCHAR` (`pending`/`embedded`/`failed`), `created_at TIMESTAMP`. Add SQLAlchemy model + Pydantic schema.
**Why:** Roadmap W11 sprint requires "Chunking API + storage; `/v1/documents/{id}/chunks` endpoint; paginated." The table must exist before W11. Tier 1 Freeze (W20) freezes Contract 2.
**Expected Output:** Alembic migration; `app/domain/chunk.py`; `app/repositories/chunk_repository.py`.
**Dependencies:** Documents table (W9).
**Handoff:** Pod B-Lead writes chunks via the chunking service (W11); Pod A exposes via `/v1/documents/{id}/chunks` (W11).
**Definition of Done:** Migration runs; model + schema validate; tests pass.

#### AI/ML & Data Pod

##### Objective
Harden OCR for the 20-PDF golden set: handle images, scanned PDFs, multi-page documents, and mixed Arabic+English content. Document AI fallback for hard cases. Verify ≥ 90% success rate (PB-01 trigger).

##### Tasks

**Task:** Run OCR on the full 20-PDF golden set (W1). For each PDF: process via PaddleOCR primary; if confidence < 0.85 on any page, fall back to Tesseract for that page; if Tesseract also fails, escalate to Google Document AI. Record per-PDF results in `docs/p2/ocr-hardening-results.md` with success/failure, fallback frequency, character error rate vs ground truth (where available), latency, memory.
**Why:** Roadmap W10 sprint requires "OCR hardening (images, multi-page, scanned); fallback to Document AI on failure; 20 PDFs processed; ≥ 90% success." PB-01 trigger: if < 90% success, the playbook triggers.
**Expected Output:** `docs/p2/ocr-hardening-results.md` with full results table; ADR-007 (OCR choice) updated with the final decision.
**Dependencies:** OCR pipeline v1 (W9); 20-PDF golden set (W1).
**Handoff:** TPM + B-Lead review; if PB-01 triggers, decision by EOD W11.
**Definition of Done:** ≥ 18/20 PDFs process successfully (90%); report committed; ADR-007 finalized.

**Task:** Implement the Document AI escalation path: when PaddleOCR + Tesseract both fail on a page (confidence < 0.7 OR empty text), call `GoogleDocumentAIProvider.extract_text` (PAL provider from W6). Handle the API rate limit + cost (track via LiteLLM cost monitoring). Store the Document AI result with `ocr_engine = 'document_ai'` in the documents table.
**Why:** Roadmap W10 sprint requires "fallback to Document AI on failure." F-6 trigger swaps the entire OCR pipeline to Document AI if PaddleOCR is consistently bad.
**Expected Output:** Updated `app/services/ocr_service.py` with escalation logic; integration tests with a deliberately bad PDF (scanned + rotated).
**Dependencies:** GoogleDocumentAIProvider (W6); Google Cloud credentials (D-Lead).
**Handoff:** Pod D's eval harness reports escalation frequency; if > 20% of pages escalate, F-6 trigger is approached.
**Definition of Done:** A deliberately bad PDF triggers Document AI escalation; result stored; cost tracked in Langfuse/Grafana.

**Task:** Implement Arabic-specific OCR preprocessing: detect Arabic text (via `langdetect`), apply right-to-left text direction correction, normalize Arabic characters (e.g., ي/ى unification), handle Arabic diacritics (tashkeel) preservation.
**Why:** Tech Spec Section 11.4 notes PaddleOCR's superior Arabic quality; Arabic preprocessing improves downstream embedding + RAG quality. R-01 (OCR quality) mitigation specifically mentions Arabic.
**Expected Output:** `app/services/arabic_text_processor.py`; unit tests with Arabic PDFs from the golden set.
**Dependencies:** OCR pipeline v1 (W9); Arabic PDFs in golden set.
**Handoff:** Pod B-1 uses this in the chunking + embedding pipeline; Pod B-Lead verifies RAG quality on Arabic content.
**Definition of Done:** Arabic PDF produces correctly-directioned text; diacritics preserved; downstream chunking handles Arabic.

#### Frontend Pod

##### Objective
Continue chat UI scaffolding: build the citation rendering component (clickable [1], [2] links that scroll to source chunks). This will be used in W15 RAG integration and W16 v0.4 demo.

##### Tasks

**Task:** Build the citation rendering component: `frontend/src/features/chat/components/CitationLink.tsx` — a clickable `[1]`-style link that, on click, opens a side panel showing the source chunk's text + page number + section title. The component takes a list of citations (each with chunk_id + display_text) and renders them inline.
**Why:** Roadmap W15 sprint requires "RAG prompt assembly + citation rendering; clickable citations jump to source chunk." Tech Spec Section 12.1 mentions citation grounding. Building the component now lets W15 focus on integration.
**Expected Output:** `CitationLink.tsx`; `frontend/src/features/chat/components/SourcePanel.tsx`; Storybook stories.
**Dependencies:** Design tokens (W2); chat UI scaffold (W9).
**Handoff:** Pod C-Lead wires to backend in W15; Pod B's RAG response includes citations in a structured format.
**Definition of Done:** Component renders inline `[1]` links; click opens source panel; Storybook story shows 3 use cases.

**Task:** Build the chat message list component with markdown rendering (using `react-markdown` + `remark-gfm` for tables/code blocks). Render assistant messages with streaming token effect (CSS animation that reveals text progressively). Render user messages right-aligned.
**Why:** Tech Spec Section 20.2 lists RAG Chat Interface as a primary module; Section 25.2 mentions LLM response streaming for perceived responsiveness.
**Expected Output:** `frontend/src/features/chat/components/ChatMessageList.tsx`; markdown renderer config.
**Dependencies:** Chat UI scaffold (W9); shadcn/ui (W1).
**Handoff:** Pod C-Lead wires streaming in W17 (SSE).
**Definition of Done:** Markdown renders correctly (headings, lists, code, tables); streaming animation works on a mock stream.

#### DevOps / QA Pod

##### Objective
Wire the OCR pipeline integration tests (W9) into CI on every PR. Begin monitoring OCR quality metrics (success rate, fallback frequency, latency) in Grafana.

##### Tasks

**Task:** Add the OCR pipeline integration tests (5 PDFs from W9) to the CI integration-test job. Run on every PR that touches `app/workers/tasks/ocr.py` or `app/services/ocr_service.py`. Configure the test to use a smaller PDF subset (1 PDF) for fast PR feedback, and the full 5-PDF set on `main` merges.
**Why:** Roadmap TM-3 (W12) requires "OCR pipeline integration tests"; the tests must run in CI to be meaningful. Tech Spec Section 25.1 mandates test coverage.
**Expected Output:** Updated `.github/workflows/ci.yml` with conditional OCR test execution.
**Dependencies:** OCR pipeline integration tests (W9).
**Handoff:** Pod D runs the formal 20-PDF golden set test in W12 (TM-3) on the v0.3 release tag.
**Definition of Done:** PR touching OCR code triggers the integration test; test passes on a clean PR; fails on a deliberately broken PR.

**Task:** Build the OCR quality Grafana dashboard: panels for OCR success rate (last 24h / 7d), PaddleOCR vs Tesseract vs Document AI usage breakdown, average confidence score, P95 processing latency per page, failed pages count. Source data from the `documents` table + Langfuse traces.
**Why:** PB-01 trigger metric requires monitoring OCR success rate; R-01 mitigation requires observability.
**Expected Output:** `infra/grafana/dashboards/ocr-quality.json`; alert for success rate < 90%.
**Dependencies:** Grafana (W6); documents table with OCR metadata (W10 Pod A).
**Handoff:** Pod B-Lead monitors during P2; TPM reviews at monthly milestone reviews.
**Definition of Done:** Dashboard renders on staging; alert fires when success rate drops below 90% (test by uploading a deliberately bad PDF).

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Pod A expands `documents` table; Pod B populates it. Schema must be agreed before W10 starts.
- **Backend ↔ Frontend:** Pod A's chunks table migration supports Pod C's future chunk viewer (W11).
- **AI/ML ↔ DevOps/QA:** OCR integration tests run in CI; Grafana dashboard monitors OCR quality.
- **End-to-end:** Upload PDF → OCR (with fallbacks) → text + metadata stored → status `ready` → UI displays. PB-01 metric measurable.

#### Week 10 Definition of Done

1. Ingestion idempotency (content hash) works.
2. `documents` table expanded with OCR metadata fields.
3. `chunks` table migrated (Contract 2 draft).
4. 20-PDF golden set processed; ≥ 90% success rate (or PB-01 triggers).
5. Document AI escalation path works for hard cases.
6. Arabic-specific OCR preprocessing implemented.
7. Citation rendering component built (with Storybook stories).
8. Chat message list with markdown rendering + streaming animation built.
9. OCR integration tests run in CI on OCR-touching PRs.
10. OCR quality Grafana dashboard live; alert for < 90% success.

---

### Week 11 — Chunking Strategy + ADR

#### Roadmap Context

- **Phase:** P2 AI Pipeline
- **Milestone:** Chunking strategy (recursive + semantic, metadata); ADR; chunking API + storage
- **Release:** v0.3 prep
- **Primary Objective:** Finalize the chunking strategy with ADR-009. Ship the `/v1/documents/{id}/chunks` endpoint. Pod B begins embedding batch job prep (W12 ships it).

#### Backend Pod

##### Objective
Ship the chunks API (`/v1/documents/{id}/chunks` paginated). Begin embedding batch job prep (joint with Pod B). Continue design docs.

##### Tasks

**Task:** Implement `/v1/documents/{id}/chunks` GET endpoint: paginated list of chunks for a document. Filters: `language`, `content_type`, `page_range`. Returns chunk text + metadata. RBAC enforced.
**Why:** Roadmap W11 sprint requires "Chunking API + storage; `/v1/documents/{id}/chunks` endpoint; paginated; Frontend can fetch chunks." Tier 1 Freeze (W20) freezes Contract 2.
**Expected Output:** `app/api/v1/chunks.py::list_chunks`; pagination + filter helpers; tests.
**Dependencies:** Chunks table (W10); chunking service (W7/W9).
**Handoff:** Pod C-1 displays chunks in the document viewer; Pod B-1 reads chunks for embedding batch job.
**Definition of Done:** Endpoint returns paginated chunks; filters work; RBAC enforced; tests pass.

**Task:** Begin the embedding batch job prep (joint with Pod B): plan the Celery task that, on chunk creation, enqueues an embedding task. Design the chunk → embedding → Qdrant write flow. Plan batching (e.g., 100 chunks per batch) and rate limiting (LiteLLM gateway cost tracking).
**Why:** Roadmap W12 sprint requires "Embedding batch job; Async job: chunk → embedding → store; batching; rate limit." Prep now lets W12 focus on implementation.
**Expected Output:** `docs/plans/embedding-batch-job.md` design doc.
**Dependencies:** BGEEmbeddingProvider (W6); Qdrant deploy prep (W9).
**Handoff:** Pod B-1 implements in W12; Pod D monitors cost.
**Definition of Done:** Design doc reviewed by B-Lead + A-Lead + D-Lead.

**Task:** Co-author the OCR design doc (`docs/ocr.md`, DM-6 due W11) with Pod B-Lead: architecture, PAL provider priority chain, fallback strategy, Arabic preprocessing, performance characteristics.
**Why:** Roadmap DM-6 (W11) requires "OCR + chunking design docs; `docs/ocr.md`, `docs/chunking.md`." Tech Spec Section 11 is the source.
**Expected Output:** `docs/ocr.md` (3–5 pages).
**Dependencies:** OCR pipeline v1 (W9–W10); ADR-007 (W5).
**Handoff:** TPM (Docs Owner) publishes; all engineers reference.
**Definition of Done:** Doc merged; reviewed by D-Lead; referenced in Docusaurus.

#### AI/ML & Data Pod

##### Objective
Finalize ADR-009 (chunking strategy). Co-author the chunking design doc. Prepare the embedding batch job (skeleton + tests, W12 implementation).

##### Tasks

**Task:** Finalize ADR-009 (chunking strategy): recursive + semantic chunking, ~500 word target, metadata schema (page_range, section_title, language, difficulty_hint, content_type), language detection approach, difficulty estimation formula. Mark `Accepted`. Reference LangChain text splitters + Tech Spec Section 11.5.
**Why:** Roadmap W11 sprint requires "Chunking strategy; ADR." Tier 1 Freeze (W20) freezes Contract 2 (chunk schema). The ADR is the binding decision.
**Expected Output:** `docs/adr/009-chunking-strategy.md` marked `Accepted`; `docs/contracts/02-chunk-schema.md` with examples.
**Dependencies:** Chunking service refinement (W9); chunks table (W10).
**Handoff:** All Pods respect the frozen schema (post-W20 freeze); Pod B-1 implements embedding using the schema.
**Definition of Done:** ADR merged; reviewed by A-Lead + D-Lead; contract doc published.

**Task:** Co-author the chunking design doc (`docs/chunking.md`, DM-6 due W11) with Pod A-Lead: algorithm details, metadata enrichment approach, performance characteristics, edge cases (very long pages, mixed-language documents, mathematical formulas).
**Why:** Roadmap DM-6 (W11) requires `docs/chunking.md`.
**Expected Output:** `docs/chunking.md` (3–5 pages).
**Dependencies:** Chunking service refinement (W9); ADR-009.
**Handoff:** TPM publishes; Pod B-1 references for embedding batch job.
**Definition of Done:** Doc merged; reviewed by B-Lead; referenced in Docusaurus.

**Task:** Implement the embedding batch job skeleton: `app/workers/tasks/embedding.py::embed_chunks(material_id)` that: (1) loads all chunks for a material, (2) batches them (100 per batch), (3) calls `EmbeddingInterface.embed_batch` via the PAL, (4) writes vectors + metadata to Qdrant via `VectorDBInterface.store`, (5) updates each chunk's `embedding_status` to `embedded`. Rate-limit via Celery config (max 1 batch per second to avoid LiteLLM gateway overload).
**Why:** Roadmap W12 sprint requires "Embedding batch job; Async job: chunk → embedding → store." Skeleton now lets W12 focus on testing + 1,000 chunks end-to-end.
**Expected Output:** `app/workers/tasks/embedding.py` skeleton; `app/services/embedding_service.py`; unit tests with mock chunks.
**Dependencies:** BGEEmbeddingProvider (W6); Qdrant deploy prep (W9); chunks table (W10).
**Handoff:** Pod B-1 finalizes in W12; Pod A exposes search API in W13.
**Definition of Done:** Skeleton runs on 10 chunks; produces Qdrant vectors; updates status.

#### Frontend Pod

##### Objective
Build the chunks viewer (paginated, filterable) on the document detail page. Begin the source panel for the chat UI (where cited chunks display).

##### Tasks

**Task:** Build the chunks viewer: tab on the document detail page showing chunks in a paginated list. Each chunk displays: text (truncated to 500 chars with "show more"), page range, section title, language badge, difficulty badge, content type badge. Filters: language, content type, page range.
**Why:** Tech Spec Section 20.2 lists Material Management UI as a primary module; chunks viewer supports instructor verification of chunking quality.
**Expected Output:** `frontend/src/features/materials/components/ChunksViewer.tsx`; filter UI.
**Dependencies:** Backend `/v1/documents/{id}/chunks` (W11 Pod A); design tokens (W2).
**Handoff:** Pod C-1 demos this in W11 Friday demo; instructor can verify chunking.
**Definition of Done:** Chunks list paginated; filters work; badges render; truncation + expand works.

**Task:** Build the source panel for the chat UI: side panel that shows the source chunk's full text + page number + section title when a citation is clicked (built on W10's `CitationLink` + `SourcePanel` skeleton). Fetches the chunk from `/v1/documents/{id}/chunks?chunk_id=...`.
**Why:** Roadmap W15 sprint requires "clickable citations jump to source chunk." Tech Spec Section 12.1 mentions citation grounding.
**Expected Output:** Updated `SourcePanel.tsx` with API integration; loading + error states.
**Dependencies:** Citation component (W10); chunks API (W11 Pod A).
**Handoff:** Pod C-Lead wires to backend RAG response in W15.
**Definition of Done:** Clicking a citation opens the source panel with the full chunk; loading + error states work.

#### DevOps / QA Pod

##### Objective
Continue P2 monitoring: add chunking metrics (chunks per document, avg chunk size, language distribution) to Grafana. Begin load test planning (formal load test is W39 TM-12, but a baseline measurement now reveals bottlenecks early).

##### Tasks

**Task:** Add chunking metrics to Grafana: chunks per document (histogram), average chunk size (words), language distribution (Arabic vs English vs mixed), content type distribution. Source data from the `chunks` table.
**Why:** Chunking quality affects downstream RAG; observability surfaces anomalies (e.g., a document producing 5 chunks when peers produce 100).
**Expected Output:** Updated `infra/grafana/dashboards/staging-overview.json` with chunking panels.
**Dependencies:** Chunks table (W10).
**Handoff:** Pod B-Lead monitors chunking quality; TPM reviews at monthly reviews.
**Definition of Done:** Dashboard renders chunking panels; data updates in real time.

**Task:** Run a baseline load test: 10 concurrent users hitting `/health` + `/v1/courses` + `/v1/documents/{id}` for 5 minutes. Measure P50/P95 latency, error rate, resource utilization (CPU, memory, DB connections). Document results in `docs/p2/baseline-load-test-w11.md`.
**Why:** Roadmap TM-12 (W39) is the formal load test (50 users, P95 < 2s), but a baseline now reveals early bottlenecks (e.g., DB connection pool too small). R-09 (DB performance) mitigation.
**Expected Output:** Load test report; k6 script `scripts/load-test-baseline.js`.
**Dependencies:** Staging environment; k6 installed.
**Handoff:** Pod D refines in W39; Pod A addresses bottlenecks found.
**Definition of Done:** Test runs for 5 min without crashing; report committed; bottlenecks flagged.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Pod A ships chunks API; Pod B populates chunks table. Embedding batch job design is joint.
- **Backend ↔ Frontend:** Chunks API + chunks viewer + source panel integration.
- **AI/ML ↔ DevOps/QA:** Chunking metrics in Grafana; baseline load test on staging.
- **End-to-end:** Upload → OCR → chunking → chunks visible in UI → metadata (language, difficulty, content type) displayed.

#### Week 11 Definition of Done

1. `/v1/documents/{id}/chunks` endpoint works (paginated, filtered).
2. Embedding batch job prep design doc merged.
3. OCR design doc (`docs/ocr.md`) merged (DM-6).
4. ADR-009 (chunking strategy) accepted; Contract 2 draft published.
5. Chunking design doc (`docs/chunking.md`) merged (DM-6).
6. Embedding batch job skeleton runs on 10 chunks.
7. Chunks viewer built with filters + badges.
8. Source panel built with API integration.
9. Chunking metrics in Grafana dashboard.
10. Baseline load test report committed.

---

### Week 12 — v0.3 Tag + Embedding Batch Job

#### Roadmap Context

- **Phase:** P2 AI Pipeline
- **Milestone:** v0.3 tag + demo (Ingestion milestone); embedding batch job
- **Release:** v0.3 (tag `v0.3.0`)
- **Primary Objective:** Ship v0.3 (PDF parsed, text visible in UI). Embed 1,000 chunks end-to-end. Run TM-3 (OCR integration tests on 5 PDFs). Pod B begins vector DB deploy with Pod D (W13 ships search API).

#### Backend Pod

##### Objective
Support the v0.3 demo: ensure the full ingestion flow (upload → OCR → chunking) works on staging. Begin Qdrant deploy with Pod D.

##### Tasks

**Task:** Verify the v0.3 demo flow end-to-end on staging: instructor uploads a PDF → OCR runs → chunks created → instructor views extracted text + chunks in UI. Fix any integration bugs. Prepare the demo script.
**Why:** Roadmap v0.3 milestone (Oct 24, 2026 = W12) requires "Demo: upload PDF, see extracted text + chunks." v0.3 demo passes.
**Expected Output:** Demo script `docs/demo-scripts/v0.3.md`; bug fixes if needed.
**Dependencies:** All W9–W11 work.
**Handoff:** TPM runs the v0.3 demo on Friday W12.
**Definition of Done:** Demo runs on staging without crashing; demo script committed.

**Task:** Begin Qdrant deploy (joint with Pod D): deploy Qdrant to staging using the W9 compose spec. Create the `openlearn_chunks` collection with vector config (size=1024, distance=Cosine). Write the Qdrant client wrapper `app/services/qdrant_service.py` implementing `VectorDBInterface` (store, search, delete).
**Why:** Roadmap W13 sprint requires "Vector DB deploy (Qdrant) + embedding write path + search API." Starting now lets W13 focus on integration. Tech Spec Section 13.2 lists Qdrant.
**Expected Output:** Qdrant running on staging; `app/services/qdrant_service.py`; `QdrantVectorDBProvider` in `backend/app/pal/providers/vector_db/qdrant_provider.py`.
**Dependencies:** Qdrant deploy prep (W9).
**Handoff:** Pod B-1 writes embeddings to Qdrant in W12 batch job; Pod A implements search API in W13.
**Definition of Done:** Qdrant reachable at `staging:6333`; collection created; `provider.store(vectors, metadata)` works in a unit test.

**Task:** Tag `v0.3.0` on `main` after Friday demo. Cut a GitHub Release with release notes referencing: OCR pipeline (PaddleOCR + Tesseract + Document AI fallback), chunking strategy (recursive + semantic + metadata), chunks API, async job infrastructure, observability stack.
**Why:** Roadmap v0.3 milestone.
**Expected Output:** Git tag `v0.3.0`; GitHub Release published.
**Dependencies:** All W9–W12 DoD items.
**Handoff:** TPM announces v0.3; P2 continues toward W16 thin MVP.
**Definition of Done:** Tag exists; release notes complete; advisor notified.

#### AI/ML & Data Pod

##### Objective
Ship the embedding batch job: 1,000 chunks embedded end-to-end with rate limiting + cost tracking. Begin hybrid retrieval design (BM25 + vector).

##### Tasks

**Task:** Implement the embedding batch job (final version, built on W11 skeleton): `app/workers/tasks/embedding.py::embed_chunks(material_id)` that batches chunks (100 per batch), calls `BGEEmbeddingProvider.embed_batch`, writes to Qdrant via `QdrantVectorDBProvider.store`, updates `chunks.embedding_status`. Rate-limit via Celery config (1 batch/sec). On failure, mark chunks as `failed` and retry once. Cost tracking via Langfuse.
**Why:** Roadmap W12 sprint requires "Embedding batch job; 1,000 chunks embedded end-to-end."
**Expected Output:** Final `app/workers/tasks/embedding.py`; integration test verifying 1,000 chunks process end-to-end.
**Dependencies:** BGEEmbeddingProvider (W6); Qdrant (Pod A W12); chunks table (W10).
**Handoff:** Pod A's search API (W13) reads from Qdrant; Pod B-Lead uses embeddings for retrieval in W14.
**Definition of Done:** 1,000 chunks embed in < 10 min; cost < $0.50; no failures; status updates correct.

**Task:** Run TM-3: formal OCR pipeline integration tests on 5 PDFs with assertions on output schema. Update the test report `docs/p2/ocr-hardening-results.md` with W12 results. Verify ≥ 90% success rate.
**Why:** Roadmap TM-3 (W12) is a testing milestone: "5 sample PDFs; assertions on output schema."
**Expected Output:** TM-3 test report; updated `docs/p2/ocr-hardening-results.md`.
**Dependencies:** OCR pipeline hardening (W10); integration tests (W9).
**Handoff:** TPM reviews at W12 monthly milestone review (Oct 2026: "OCR works").
**Definition of Done:** 5/5 PDFs pass schema assertions; ≥ 90% OCR success on the broader 20-PDF golden set.

**Task:** Begin hybrid retrieval design (BM25 + vector): research BM25 implementation options (Postgres full-text search vs `rank_bm25` library vs Elasticsearch). Plan the 4-stage retrieval pipeline (query embedding → hybrid search → re-ranking → context assembly) per Tech Spec Section 12.2.
**Why:** Roadmap W14 sprint requires "Hybrid retrieval (BM25 + vector); Combine BM25 + vector scores; weighting." W14 is only 2 weeks away; design now.
**Expected Output:** `docs/plans/hybrid-retrieval.md` design doc.
**Dependencies:** Embedding batch job (W12); Qdrant (Pod A W12).
**Handoff:** Pod B-Lead implements in W14; Pod B-1 implements reranker in W14.
**Definition of Done:** Design doc reviewed; implementation plan clear for W14.

#### Frontend Pod

##### Objective
Finalize the v0.3 demo UI: ensure the upload → OCR → chunks flow is polished. Continue the chat UI components (input box with auto-resize, send button with loading state).

##### Tasks

**Task:** Polish the v0.3 demo UI: verify the upload → processing → ready → view text → view chunks flow renders correctly on staging. Fix any visual bugs. Add a "demo mode" indicator (banner) on the materials page for clarity during the demo.
**Why:** v0.3 demo must be polished; the demo shows the ingestion pipeline working end-to-end.
**Expected Output:** Bug fixes; demo mode banner.
**Dependencies:** All W9–W11 work.
**Handoff:** Pod C-Lead demos v0.3 on Friday W12.
**Definition of Done:** Demo flows smoothly; no visual bugs; banner visible.

**Task:** Build the chat input component: `frontend/src/features/chat/components/ChatInput.tsx` with auto-resizing textarea, send button, Shift+Enter for newline, Enter to send, loading state on send. Character limit (4,000 chars). Disabled state when no session.
**Why:** Tech Spec Section 20.2 lists RAG Chat Interface as a primary module; thin MVP (W16) requires this input.
**Expected Output:** `ChatInput.tsx`; Storybook stories for default, loading, disabled states.
**Dependencies:** Chat UI scaffold (W9); shadcn/ui (W1).
**Handoff:** Pod C-Lead wires to backend in W16 (thin MVP) and W17 (full chat API).
**Definition of Done:** Auto-resize works; keyboard shortcuts work; loading state renders; Storybook stories committed.

#### DevOps / QA Pod

##### Objective
Run TM-3 verification, monitor the embedding batch job cost, and prepare for the W13 vector DB integration. Continue cross-training: Pod B engineer continues Qdrant ops shadowing.

##### Tasks

**Task:** Run TM-3 with Pod B-Lead: execute the 5-PDF integration tests on staging, verify schema assertions, document results in `docs/p2/tm-3-results.md`. Confirm ≥ 90% success on the 20-PDF golden set.
**Why:** Roadmap TM-3 (W12) is a testing milestone.
**Expected Output:** TM-3 results doc; coverage report on OCR module.
**Dependencies:** OCR pipeline (W9–W10); integration tests (W9).
**Handoff:** TPM reviews at monthly milestone.
**Definition of Done:** TM-3 results committed; metric met.

**Task:** Monitor the embedding batch job cost via Langfuse + Grafana: confirm 1,000 chunks cost < $0.50. Set up alert for cost > $5/day (R-06 mitigation). Document the cost baseline.
**Why:** R-06 (LLM API cost overruns, score 9) mitigation requires cost monitoring; F-4 trigger ("LLM API cost > $300/month") requires monthly tracking.
**Expected Output:** Cost baseline doc `docs/p2/embedding-cost-baseline.md`; Grafana cost alert.
**Dependencies:** Embedding batch job (Pod B W12); Langfuse (W7).
**Handoff:** Pod D monitors monthly; F-4 triggers if cost exceeds threshold.
**Definition of Done:** 1,000-chunk cost measured; alert configured; baseline doc committed.

**Task:** Continue Pod B cross-training: Pod B engineer (B-1 or B-2) performs a Qdrant index rebuild + backup + restore under Pod D supervision. Document in `docs/cross-training.md`.
**Why:** Roadmap §Pod Cross-Training Plan continues through W20. R-05 mitigation.
**Dependencies:** Qdrant deployed (Pod A W12).
**Handoff:** Pod B engineer can triage Qdrant issues independently by W20.
**Definition of Done:** Pod B engineer performs rebuild + backup + restore.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Qdrant deploy is joint; embedding batch job writes to Qdrant.
- **Backend ↔ Frontend:** v0.3 demo flow integrates all Pods.
- **AI/ML ↔ DevOps/QA:** TM-3 results; embedding cost monitoring; Qdrant cross-training.
- **End-to-end:** Upload → OCR → chunks → embeddings in Qdrant → v0.3 demo.

#### Week 12 Definition of Done

1. v0.3.0 tagged; demo passes; release notes published.
2. Qdrant deployed to staging; collection created.
3. Embedding batch job processes 1,000 chunks in < 10 min; cost < $0.50.
4. TM-3 met: 5-PDF integration tests pass; ≥ 90% OCR success on 20-PDF golden set.
5. Hybrid retrieval design doc merged.
6. Chat input component built.
7. Cost monitoring live; alert configured.
8. Pod B engineer performs Qdrant ops under supervision.
9. Friday demo (v0.3) passes on staging.
10. Monthly milestone review (Oct 2026: "OCR works") completed.

---



### Week 13 — Vector DB + Embedding Write Path + Search API

#### Roadmap Context

- **Phase:** P2 AI Pipeline (CRITICAL PATH)
- **Milestone:** Vector DB deploy (Qdrant) + embedding write path + search API; IM-4 (OCR → Chunking → Embeddings → VectorDB end-to-end)
- **Release:** v0.4 prep
- **Primary Objective:** Ship the search API (`/v1/search?q=...` returns top-k). Verify the full ingestion pipeline runs end-to-end (IM-4). Pod B begins BM25 implementation for W14 hybrid retrieval.

#### Backend Pod

##### Objective
Ship the search API. Wire the embedding write path: on chunk creation → enqueue embedding task → write to Qdrant. Validate IM-4 with Pod B.

##### Tasks

**Task:** Implement the `/v1/search` GET endpoint: accepts `q` (query string), `course_id` (filter), `material_id` (filter, optional), `top_k` (default 10). Returns a list of search results, each with `chunk_id`, `material_id`, `text` (truncated to 500 chars), `page_range`, `section_title`, `score` (similarity), `language`. Uses `QdrantVectorDBProvider.search(query_vector, top_k, filters)`. Embeds the query via `BGEEmbeddingProvider.embed(q)` first.
**Why:** Roadmap W13 sprint requires "/v1/search?q=... returns top-k; endpoint returns ranked results." Tech Spec Section 22.3 doesn't list this explicitly but it's implied by Section 12.2 retrieval process. Tier 1 Freeze (W20) freezes Contract 4 (vector DB query API).
**Expected Output:** `app/api/v1/search.py::search`; `app/services/search_service.py`; tests with sample queries.
**Dependencies:** Qdrant (Pod A W12); BGEEmbeddingProvider (W6); embedding batch job (Pod B W12).
**Handoff:** Pod C-1 builds a search UI component (W14); Pod B-Lead uses for retrieval in W14 hybrid.
**Definition of Done:** `/v1/search?q=linear+regression&course_id=X` returns 10 ranked chunks; filters work; tests pass.

**Task:** Implement the embedding write path: when the chunking service creates a chunk (W11), automatically enqueue an embedding task via `celery_app.send_task("embedding.embed_chunks", args=[material_id])`. Verify the chunk's `embedding_status` updates from `pending` → `embedded` within 10 minutes of chunk creation.
**Why:** Roadmap W13 sprint requires "embeddings written on chunk creation; new chunks auto-embed." Tech Spec Section 11.2 sequence diagram shows parallel embedding during ingestion.
**Expected Output:** Updated `app/services/chunking_service.py` to enqueue; integration test verifying the full pipeline (upload → OCR → chunk → embed → Qdrant).
**Dependencies:** Chunking service (W11); embedding batch job (Pod B W12).
**Handoff:** IM-4 verification: Pod B-Lead confirms the pipeline runs end-to-end on a fresh upload.
**Definition of Done:** A new upload produces embedded chunks in Qdrant within 10 minutes; `embedding_status` correct; integration test passes.

**Task:** Draft ADR-011 (vector DB query API contract): top-k search, filters (`course_id`, `material_id`, `language`), payload fields, score field. Mark `Proposed`. This is Contract 4, frozen at W20.
**Why:** Tier 1 Freeze (W20) freezes Contract 4.
**Expected Output:** `docs/adr/011-vector-db-query-api.md` (Proposed); `docs/contracts/04-vector-db-query-api.md`.
**Dependencies:** Search API (above).
**Handoff:** Pod B-Lead finalizes in W14 (hybrid retrieval); freezes at W20.
**Definition of Done:** ADR opened; reviewed by B-Lead + C-Lead.

#### AI/ML & Data Pod

##### Objective
Verify IM-4 (full ingestion pipeline end-to-end). Begin BM25 implementation for W14 hybrid retrieval. Implement the reranker PAL provider (bge-reranker-v2-m3).

##### Tasks

**Task:** Verify IM-4: run the full ingestion pipeline on a fresh upload (a 50-page PDF from the demo PDF set). Steps: (1) upload via UI, (2) OCR runs, (3) chunking runs, (4) embedding batch job runs, (5) chunks + embeddings in Qdrant, (6) `/v1/search?q=...` returns relevant chunks. Document timing for each step.
**Why:** Roadmap IM-4 (W13) requires "Full ingestion pipeline runs end-to-end." This is the integration milestone that proves the pipeline works before W14 retrieval + W15 RAG.
**Expected Output:** IM-4 verification report `docs/p2/im-4-verification.md` with timing + results.
**Dependencies:** Search API (Pod A W13); embedding batch job (W12).
**Handoff:** TPM + B-Lead review at Friday demo; if pipeline fails, escalate (it's on critical path).
**Definition of Done:** A fresh upload produces searchable chunks within 15 minutes; search returns relevant results; report committed.

**Task:** Implement the BM25 retrieval component: `app/services/bm25_service.py` using `rank_bm25.BM25Okapi` over chunk texts. Index all chunks for a material on demand (or maintain a Postgres GIN index on `chunks.text`). Return top-k chunks with BM25 scores.
**Why:** Roadmap W14 sprint requires "Hybrid retrieval (BM25 + vector); Combine BM25 + vector scores." Tech Spec Section 12.2 specifies 70% semantic / 30% keyword weighting. BM25 must exist before W14.
**Expected Output:** `app/services/bm25_service.py`; unit tests with sample corpus.
**Dependencies:** Chunks table (W10).
**Handoff:** Pod B-Lead combines with vector search in W14 hybrid retrieval.
**Definition of Done:** BM25 returns top-k chunks for a sample query; scores reasonable.

**Task:** Implement the reranker PAL provider: `BGERerankerProvider` in `backend/app/pal/providers/ranking/bge_reranker_provider.py` implementing `RankingInterface.rank(query, documents, top_k)`. Loads `bge-reranker-v2-m3` model via `sentence-transformers`. Cross-encoder: jointly processes query + each document, returns relevance scores.
**Why:** Roadmap W14 sprint requires "Reranker integration; bge-reranker-v2-m3 cross-encoder; top-20 → top-5." Tech Spec Section 12.2 specifies re-ranking as the 3rd stage. Tech Spec Section 26.1 lists bge-reranker-v2-m3.
**Expected Output:** `BGERerankerProvider` class; unit tests verifying reranking improves precision@5 vs raw vector search.
**Dependencies:** `sentence-transformers` library; bge-reranker-v2-m3 model download.
**Handoff:** Pod B-1 integrates in W14 hybrid retrieval pipeline.
**Definition of Done:** Provider reranks 20 candidates → top 5 in < 2s for a sample query; precision improves.

#### Frontend Pod

##### Objective
Build the search UI component: a search bar on the course detail page that calls `/v1/search` and displays results with chunk previews. Continue the chat UI (session list placeholder).

##### Tasks

**Task:** Build the search UI: a search bar at the top of the course detail page. On submit, calls `/v1/search?q=...&course_id=X` and displays results in a list. Each result shows: chunk text (truncated, with the query highlighted), page range, section title, score, "View in document" link.
**Why:** Tech Spec Section 20.2 lists Material Management UI as a primary module; search supports content discovery. The search UI also validates the search API contract.
**Expected Output:** `frontend/src/features/search/components/SearchBar.tsx`, `SearchResults.tsx`; integration with `/v1/search`.
**Dependencies:** Search API (Pod A W13); design tokens (W2).
**Handoff:** Pod C-1 demos search in W13 Friday demo; Pod B-Lead uses search results to validate retrieval quality.
**Definition of Done:** Search returns results in < 2s; query highlighted; results paginate; "View in document" link works.

**Task:** Build the chat session list placeholder: a sidebar component on the `/chat` page that lists previous chat sessions (empty state for now, since chat isn't wired). Each session shows: title (auto-generated from first message), last message preview, timestamp. "New chat" button.
**Why:** Tech Spec Section 20.2 lists RAG Chat Interface with chat history management. Preparing the UI now lets W17 focus on backend integration.
**Expected Output:** `frontend/src/features/chat/components/SessionList.tsx`; empty state design.
**Dependencies:** Chat UI scaffold (W9); design tokens (W2).
**Handoff:** Pod C-Lead wires to backend `/v1/chat/session` endpoint in W17.
**Definition of Done:** Sidebar renders with empty state; "New chat" button creates a new session placeholder.

#### DevOps / QA Pod

##### Objective
Monitor the full ingestion pipeline (IM-4) in Grafana. Set up Qdrant alerts (down > 1h triggers F-1 evaluation). Continue cross-training.

##### Tasks

**Task:** Add Qdrant monitoring to Grafana: panels for collection size (vector count), query latency (P50/P95), error rate, storage usage, index build time. Configure alert: "Qdrant down > 1h" → triggers F-1 evaluation per R-05 mitigation.
**Why:** R-05 (Qdrant ops too heavy, score 9) mitigation requires monitoring; F-1 trigger ("Qdrant down > 1h unresolved") requires an alert. Tech Spec Section 13.2 lists Qdrant.
**Expected Output:** `infra/grafana/dashboards/qdrant.json`; alert rule.
**Dependencies:** Qdrant (Pod A W12); Grafana (W6).
**Handoff:** Pod D monitors; if alert fires, D-Lead evaluates F-1 invocation within 48h per the Fallback rules.
**Definition of Done:** Dashboard renders Qdrant metrics; alert fires when Qdrant is stopped (test by stopping the container).

**Task:** Run a full pipeline integration test in CI: upload a sample PDF → wait for OCR → wait for chunking → wait for embedding → call `/v1/search` → verify results. Add to the CI integration-test job, runs on `main` merges.
**Why:** IM-4 verification; ensures the pipeline doesn't break across PRs.
**Expected Output:** `backend/tests/integration/test_full_pipeline.py`; CI integration.
**Dependencies:** Full pipeline (W9–W13); search API (W13 Pod A).
**Handoff:** Pod D runs nightly on staging; failures wake on-call.
**Definition of Done:** Test runs end-to-end in < 10 min in CI; passes on a clean `main` merge.

**Task:** Continue cross-training: Pod B engineer (B-1 or B-2) performs a Qdrant collection re-index + verifies search still works afterward. Document in `docs/cross-training.md`.
**Why:** Roadmap §Pod Cross-Training Plan continues; Feature Freeze (W38) requires 3 DevOps-capable people.
**Dependencies:** Qdrant (Pod A W12).
**Handoff:** Pod B engineer can independently triage Qdrant issues by W20.
**Definition of Done:** Re-index completes; search returns results post-re-index; documented.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Search API + embedding write path + Qdrant deploy — joint effort. IM-4 verification.
- **Backend ↔ Frontend:** Search API + search UI integration.
- **AI/ML ↔ DevOps/QA:** Full pipeline integration test in CI; Qdrant monitoring.
- **End-to-end (IM-4):** Upload → OCR → chunking → embeddings → Qdrant → search → results in UI. This is the first full AI pipeline integration.

#### Week 13 Definition of Done

1. `/v1/search` endpoint works; returns top-k ranked chunks with filters.
2. Embedding write path: new chunks auto-embed within 10 minutes.
3. ADR-011 (vector DB query API) opened.
4. IM-4 verified: full pipeline runs end-to-end on a fresh upload in < 15 min.
5. BM25 retrieval component implemented.
6. Reranker PAL provider implemented (`BGERerankerProvider`).
7. Search UI built; results highlight query.
8. Chat session list placeholder built.
9. Qdrant Grafana dashboard + alert configured.
10. Full pipeline integration test in CI passes.

---

### Week 14 — Hybrid Retrieval + Reranker Integration

#### Roadmap Context

- **Phase:** P2 AI Pipeline (CRITICAL PATH)
- **Milestone:** Hybrid retrieval (BM25 + vector); reranker integration; IM-5 prep (VectorDB → Reranker → RAG)
- **Release:** v0.4 prep
- **Primary Objective:** Ship hybrid retrieval combining BM25 + vector scores. Integrate the reranker (top-20 → top-5). This is the retrieval foundation for RAG in W15.

#### Backend Pod

##### Objective
Support Pod B's hybrid retrieval by exposing a `/v1/retrieve` internal endpoint (used by the chat API in W17). Begin chat API + SSE streaming design.

##### Tasks

**Task:** Implement the `/v1/retrieve` POST endpoint (internal, used by chat API): accepts `query`, `course_id`, `material_id` (optional), `top_k` (default 5). Returns the top-k re-ranked chunks with full text + metadata + scores (vector score, BM25 score, reranker score). Calls `RetrievalService.retrieve(query, filters)` which orchestrates: query embedding → hybrid search (BM25 + vector) → reranker → context assembly.
**Why:** Tech Spec Section 12.2 specifies the 4-stage retrieval pipeline; the chat API (W17) calls this internally. Exposing it as an endpoint enables direct testing + Pod C verification.
**Expected Output:** `app/api/v1/retrieve.py::retrieve`; `app/services/retrieval_service.py` (orchestrator); tests.
**Dependencies:** Search API (W13); hybrid retrieval (Pod B W14); reranker (Pod B W14).
**Handoff:** Pod A-Lead uses this in W17 chat API; Pod C-1 can call directly for debugging.
**Definition of Done:** Endpoint returns re-ranked top-5 chunks with all scores; tests pass; latency < 1s.

**Task:** Begin chat API + SSE streaming design: `/v1/chat` POST creates a session; `/v1/chat/{session_id}/message` POST sends a message and returns an SSE stream of tokens. Plan session persistence (`chat_sessions` + `chat_messages` tables). Plan the RAG flow: receive message → retrieve context → call LLM via LiteLLM gateway → stream tokens → save message.
**Why:** Roadmap W17 sprint requires "RAG chat API + streaming; `/v1/chat` SSE streaming; session persistence." Design now so W17 focuses on implementation.
**Expected Output:** `docs/plans/chat-api-design.md` design doc.
**Dependencies:** Retrieval service (W14); LiteLLM gateway (W7); RAG prompt (Pod B W15).
**Handoff:** Pod A-Lead implements in W17; Pod C-Lead wires UI.
**Definition of Done:** Design doc reviewed; table schemas drafted.

#### AI/ML & Data Pod

##### Objective
Ship hybrid retrieval (BM25 + vector, 70/30 weighting) and integrate the reranker (top-20 → top-5). Verify retrieval quality on the demo PDF. Begin RAG prompt design.

##### Tasks

**Task:** Implement hybrid retrieval: `app/services/retrieval_service.py::retrieve(query, filters, top_k)` that: (1) embeds the query via BGE-M3, (2) calls `QdrantVectorDBProvider.search(query_vector, top_k=20, filters)` for semantic search, (3) calls `BM25Service.search(query, top_k=20, filters)` for keyword search, (4) merges results with 70% semantic / 30% keyword weighting (per Tech Spec Section 12.2), (5) calls `BGERerankerProvider.rank(query, merged_top_20, top_k=5)` for re-ranking, (6) assembles context (top-5 chunks, respecting LLM context window).
**Why:** Roadmap W14 sprint requires "Hybrid retrieval (BM25 + vector); Combine BM25 + vector scores; weighting" and "Reranker integration; top-20 → top-5." Tech Spec Section 12.2 specifies the 4-stage pipeline.
**Expected Output:** `retrieval_service.py`; integration tests verifying hybrid beats pure vector on a sample golden set (5–10 query-chunk pairs).
**Dependencies:** Search API (Pod A W13); BM25 (W13); reranker (W13).
**Handoff:** Pod B-Lead uses in W15 RAG prompt assembly; Pod A exposes via `/v1/retrieve` (above).
**Definition of Done:** Hybrid retrieval returns re-ranked top-5 in < 1s; beats pure vector on precision@5 on the sample set.

**Task:** Begin RAG prompt design: draft the prompt template with citation placeholders. Format: "Answer the question based on the following context. Cite sources using [1], [2], etc. corresponding to the context chunks. If the answer is not in the context, say 'I don't know.' Context: [1] {chunk_1_text} (Source: {chunk_1_metadata}) [2] {chunk_2_text}... Question: {user_question} Answer:". Plan structured output (JSON with `answer` + `citations` array).
**Why:** Roadmap W15 sprint requires "RAG prompt assembly + citation rendering; Prompt template with citations; LLM gateway call; safety." Tech Spec Section 12.1 mentions citation grounding + structured output enforcement.
**Expected Output:** `docs/plans/rag-prompt-design.md`; draft prompt template in `app/services/rag_service.py`.
**Dependencies:** Retrieval service (W14); LiteLLM gateway (W7).
**Handoff:** Pod B-Lead finalizes in W15; Pod C-Lead renders citations via CitationLink component (W10).
**Definition of Done:** Prompt template drafted; structured output schema defined; reviewed by B-Lead.

**Task:** Run retrieval quality evaluation on the demo PDF: prepare 5–10 query-chunk pairs (queries with known-good source chunks). Run hybrid retrieval + reranker; measure precision@5, recall@5, MRR. Document results in `docs/p2/retrieval-quality-w14.md`.
**Why:** PB-02 trigger metric ("Faithfulness < 0.7 OR relevance < 0.7 on 50-Q golden set at W16") requires baseline measurement. R-02 (RAG quality, score 16) mitigation.
**Expected Output:** Quality report; baseline metrics.
**Dependencies:** Hybrid retrieval (W14); demo PDF.
**Handoff:** Pod B-Lead compares against W15 RAG eval; TPM reviews.
**Definition of Done:** 5–10 queries evaluated; precision@5 > 0.7; report committed.

#### Frontend Pod

##### Objective
Build the chat message rendering with streaming effect (full version). Build the source panel integration (displaying retrieved chunks alongside the chat).

##### Tasks

**Task:** Build the streaming chat message component: receives an SSE stream of tokens from the backend, renders them progressively with a typing cursor. Handle errors (display inline), handle completion (remove cursor, enable input).
**Why:** Tech Spec Section 25.2 mandates LLM response streaming for perceived responsiveness. Roadmap W17 sprint requires chat with streaming.
**Expected Output:** Updated `ChatMessageList.tsx` with SSE handling; `frontend/src/features/chat/hooks/useChatStream.ts`.
**Dependencies:** Chat UI scaffold (W9); chat input (W12); markdown rendering (W10).
**Handoff:** Pod C-Lead wires to backend in W17; for W16 thin MVP, wires to a simpler endpoint.
**Definition of Done:** Mock SSE stream renders progressively; cursor visible; completion handled.

**Task:** Build the source panel integration for the chat: when an assistant message includes citations, the source panel displays the cited chunks. Each citation `[1]` in the message maps to a chunk in the panel. Clicking a citation scrolls the panel to that chunk.
**Why:** Tech Spec Section 12.1 mentions citation grounding; Roadmap W15 sprint requires "clickable citations jump to source chunk."
**Expected Output:** Updated `SourcePanel.tsx` with multi-citation support; integration with chat message rendering.
**Dependencies:** Source panel skeleton (W11); CitationLink (W10).
**Handoff:** Pod C-Lead wires to backend RAG response (with citations array) in W15.
**Definition of Done:** Multiple citations render; clicking scrolls to chunk; panel updates on new messages.

#### DevOps / QA Pod

##### Objective
Monitor retrieval quality metrics in Grafana. Set up Langfuse tracing for all LLM calls (now that retrieval + RAG prompt will start firing). Continue cross-training.

##### Tasks

**Task:** Add retrieval quality metrics to Grafana: panels for retrieval latency (P50/P95), hybrid vs vector-only precision (when golden set queries are run), reranker latency, BM25 vs Qdrant query latency. Source data from application metrics (Prometheus) + Langfuse.
**Why:** R-02 (RAG quality) mitigation requires observability; PB-02 trigger requires monitoring faithfulness + relevance.
**Expected Output:** `infra/grafana/dashboards/retrieval-quality.json`.
**Dependencies:** Retrieval service (Pod B W14); Prometheus + Langfuse (W7).
**Handoff:** Pod B-Lead monitors during P2; TPM reviews at monthly reviews.
**Definition of Done:** Dashboard renders; data updates on each retrieval call.

**Task:** Configure Langfuse tracing for the LiteLLM gateway: every LLM call logs input prompt, output, tokens, latency, cost, model. Verify traces appear in Langfuse UI. Build a Grafana panel for LLM call rate, latency, cost, error rate (if not done in W7).
**Why:** R-06 (LLM cost) mitigation; R-02 (RAG quality) evaluation requires trace inspection.
**Expected Output:** Langfuse config in `infra/litellm-config.yaml`; verified traces.
**Dependencies:** LiteLLM gateway (W7); Langfuse (W7).
**Handoff:** Pod B-Lead inspects traces in W15 RAG iteration.
**Definition of Done:** A test LLM call appears in Langfuse with full trace; Grafana panel renders.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** `/v1/retrieve` endpoint exposes Pod B's retrieval service. Joint design.
- **Backend ↔ Frontend:** Search UI calls `/v1/search`; source panel integration for chat.
- **AI/ML ↔ Frontend:** RAG prompt design informs citation rendering format.
- **AI/ML ↔ DevOps/QA:** Retrieval quality monitoring; Langfuse tracing.
- **End-to-end:** Upload → OCR → chunk → embed → search → retrieve → rerank. Retrieval is ready for W15 RAG.

#### Week 14 Definition of Done

1. `/v1/retrieve` endpoint works; returns re-ranked top-5 chunks with all scores.
2. Chat API + SSE design doc merged.
3. Hybrid retrieval (BM25 + vector, 70/30) implemented; beats pure vector on precision@5.
4. Reranker integrated (top-20 → top-5); precision improves.
5. RAG prompt design doc merged; prompt template drafted.
6. Retrieval quality baseline measured (precision@5 > 0.7 on 5–10 queries).
7. Streaming chat message component built.
8. Source panel integration built.
9. Retrieval quality Grafana dashboard live.
10. Langfuse tracing for LLM calls verified.

---

### Week 15 — RAG Prompt + Citation Rendering + RAG Eval Harness v1

#### Roadmap Context

- **Phase:** P2 AI Pipeline (CRITICAL PATH)
- **Milestone:** RAG prompt assembly + citation rendering; RAG eval harness v1 (TM-4); IM-5 (VectorDB → Reranker → RAG returns cited answer via curl); DM-7 (RAG design doc); DDM-1 (demo PDF set chosen)
- **Release:** v0.4 prep
- **Primary Objective:** Ship the RAG prompt with citation rendering. Run RAG eval harness v1 (50 Q&A pairs). Verify IM-5 (query returns cited answer via curl). Choose the demo PDF set (3 courses × 5–10 PDFs) for the v1.0 demo.

#### Backend Pod

##### Objective
Finalize the retrieval service contract with Pod B. Begin the chat API skeleton (W17 ships it). Support the RAG eval harness by exposing `/v1/rag/query` (internal, for the eval script).

##### Tasks

**Task:** Implement the `/v1/rag/query` POST endpoint (internal, used by eval harness + chat API): accepts `query`, `course_id`, `material_id` (optional), `session_id` (optional, for logging). Calls `RetrievalService.retrieve` → `RAGService.generate_answer(retrieved_chunks, query)` → returns `{answer, citations, retrieval_scores, generation_metadata}`. The chat API (W17) wraps this with SSE streaming.
**Why:** TM-4 (W15) requires the eval script to run in CI; the script needs an endpoint to call. Roadmap W17 sprint requires the chat API to call retrieval + RAG; this endpoint is the shared core.
**Expected Output:** `app/api/v1/rag.py::query`; `app/services/rag_service.py::generate_answer`; tests.
**Dependencies:** Retrieval service (Pod B W14); RAG prompt (Pod B W15).
**Handoff:** Pod B-Lead uses for eval harness; Pod A-Lead wraps with SSE in W17.
**Definition of Done:** Endpoint returns answer + citations via curl; latency < 3s; tests pass.

**Task:** Begin the chat API skeleton: `app/api/v1/chat.py` with `/v1/chat` POST (creates session, returns `session_id`) and `/v1/chat/{session_id}/message` POST (returns SSE stream). Skeleton returns a mock SSE stream ("hello" tokens) for now; Pod A-Lead finalizes in W17. Add `chat_sessions` + `chat_messages` table migrations.
**Why:** Roadmap W17 sprint requires the chat API. Skeleton now lets W17 focus on RAG integration + SSE.
**Expected Output:** `app/api/v1/chat.py` skeleton; `chat_sessions` + `chat_messages` migrations; `app/services/chat_service.py`.
**Dependencies:** Chat API design (W14); auth (W5).
**Handoff:** Pod A-Lead finalizes in W17; Pod C-Lead wires UI in W17.
**Definition of Done:** POST creates a session; POST message returns a mock SSE stream; tables migrated.

**Task:** Co-author the RAG design doc (`docs/rag.md`, DM-7 due W15) with Pod B-Lead: 4-stage retrieval pipeline, prompt template, citation format, eval methodology, fallback strategies.
**Why:** Roadmap DM-7 (W15) requires `docs/rag.md`.
**Expected Output:** `docs/rag.md` (5+ pages).
**Dependencies:** Retrieval + RAG (W14–W15); eval harness (W15).
**Handoff:** TPM publishes; all engineers reference.
**Definition of Done:** Doc merged; reviewed by B-Lead + D-Lead; in Docusaurus.

#### AI/ML & Data Pod

##### Objective
Ship the RAG prompt with citations + safety guardrails. Implement the RAG eval harness v1 (50 Q&A golden set). Verify IM-5. Choose the demo PDF set (DDM-1).

##### Tasks

**Task:** Implement the RAG service: `app/services/rag_service.py::generate_answer(query, retrieved_chunks)` that: (1) assembles the prompt template with retrieved chunks as context, (2) calls `LiteLLMReasoningProvider.generate(prompt, context)` via the PAL, (3) parses the structured output (answer + citations), (4) applies safety guardrails (faithfulness check — does the answer cite real chunks? If not, return "I don't know" per the prompt instruction), (5) returns `{answer, citations: [{chunk_id, display_text, page_range, section_title}]}`.
**Why:** Roadmap W15 sprint requires "RAG prompt assembly + citation rendering; Prompt template with citations; LLM gateway call; safety; clickable citations jump to source chunk." Tech Spec Section 12.1 specifies citation grounding + structured output + confidence scoring.
**Expected Output:** `app/services/rag_service.py`; prompt template; unit tests with sample retrieved chunks.
**Dependencies:** Retrieval service (W14); LiteLLM gateway (W7); RAG prompt design (W14).
**Handoff:** Pod A exposes via `/v1/rag/query` (W15); Pod C-Lead renders citations via CitationLink (W10).
**Definition of Done:** Sample query returns an answer with 2+ citations; faithfulness check catches hallucinated citations; tests pass.

**Task:** Implement the RAG eval harness v1 (TM-4): 50 Q&A pairs (authored by Pod B + advisor in W14 prep, or this week if needed) with expected answers + acceptable source chunks. The harness `backend/app/eval/evaluators/rag_evaluator.py` (extends Pod D's `BaseEvaluator`) runs: for each Q&A pair, call `/v1/rag/query`, measure faithfulness (Ragas or custom — does the answer match the expected?), relevance (does it cite acceptable sources?), latency. Output a metrics JSON.
**Why:** Roadmap TM-4 (W15) requires "RAG golden set v1; 50 Q&A pairs; eval script runs in CI." PB-02 trigger metric ("Faithfulness < 0.7 OR relevance < 0.7 on 50-Q golden set at W16") depends on this.
**Expected Output:** `backend/app/eval/evaluators/rag_evaluator.py`; `tests/data/rag_golden_set.json` (50 Q&A pairs); CI integration.
**Dependencies:** Eval harness scaffold (Pod D W2); RAG service (above); `/v1/rag/query` (Pod A W15).
**Handoff:** Pod D runs in CI on every PR from W15 onward (TM-4); Pod B-Lead iterates on RAG based on results.
**Definition of Done:** 50 Q&A pairs authored; harness runs end-to-end; faithfulness + relevance scores produced; CI integration works.

**Task:** Verify IM-5: run a query against the demo PDF via `/v1/rag/query` (curl). Confirm the response includes an answer with at least 2 citations pointing to real chunks. Document in `docs/p2/im-5-verification.md`.
**Why:** Roadmap IM-5 (W15) requires "Query returns cited answer via curl." This is the final integration milestone before the v0.4 thin MVP.
**Expected Output:** IM-5 verification doc with sample curl + response.
**Dependencies:** RAG service (above); `/v1/rag/query` (Pod A W15); demo PDF embedded.
**Handoff:** TPM reviews; if response is poor quality, PB-02 triggers.
**Definition of Done:** curl returns a JSON response with answer + 2+ citations; citations resolve to real chunks.

**Task:** Choose the demo PDF set (DDM-1): 3 courses × 5–10 PDFs each, all clean, all OCR-able. Suggested courses: (1) Intro to Machine Learning, (2) Data Structures & Algorithms, (3) Linear Algebra. Commit to `tests/data/demo_pdfs/` with a manifest.
**Why:** Roadmap DDM-1 (W20, but choosing now lets W20 just confirm) requires the demo PDF set. v0.4 thin MVP (W16) uses one PDF from this set.
**Expected Output:** `tests/data/demo_pdfs/` with 15–30 PDFs + manifest.
**Dependencies:** Demo PDF for v0.4 (W2); 20-PDF golden set (W1).
**Handoff:** Pod D ingests these into staging in W24 (DDM-2).
**Definition of Done:** 15–30 PDFs committed; manifest complete; all PDFs OCR-able.

#### Frontend Pod

##### Objective
Wire the citation rendering to the RAG response format. Polish the chat UI for the W16 thin MVP demo.

##### Tasks

**Task:** Wire the citation rendering: define the expected RAG response format (JSON schema with `answer` markdown + `citations` array). Update `ChatMessageList.tsx` to parse citations from the response and render `[1]`, `[2]` inline. Clicking a citation opens `SourcePanel` with the chunk. Fetch the full chunk text from `/v1/documents/{id}/chunks?chunk_id=...` if not already loaded.
**Why:** Roadmap W15 sprint requires "Prompt returns answer with [1], [2] cites; user can verify source." Tech Spec Section 12.1 mentions citation grounding.
**Expected Output:** Updated `ChatMessageList.tsx` + `SourcePanel.tsx`; integration tests with mock RAG response.
**Dependencies:** Citation component (W10); RAG response schema (Pod B W15).
**Handoff:** Pod C-Lead wires to real backend in W16 thin MVP.
**Definition of Done:** Mock RAG response renders with clickable citations; clicking opens source panel.

**Task:** Polish the chat UI for the v0.4 thin MVP demo: ensure the `/chat` page (no auth, no nav, single pre-loaded PDF) is clean and ready for W16 demo. Add a header showing the demo PDF title. Remove the "TODO: connect to RAG" placeholder. The page is ready to be wired to the backend in W16.
**Why:** Roadmap v0.4 thin MVP (W16) requires "Pre-loaded PDF + chat UI; ask question, get cited answer." UI must be demo-ready.
**Expected Output:** Polished `/chat` page; demo script draft.
**Dependencies:** Chat UI scaffold (W9); citation rendering (W10 + W15 above).
**Handoff:** Pod A-Lead + Pod C-Lead integrate the backend in W16.
**Definition of Done:** Page renders cleanly; demo script draft committed; C-Lead sign-off.

#### DevOps / QA Pod

##### Objective
Wire the RAG eval harness into CI (TM-4 finalization). Monitor RAG quality in Grafana. Begin load test planning for the W16 thin MVP (ensure it survives 5 questions without crashing).

##### Tasks

**Task:** Wire the RAG eval harness (Pod B W15) into CI: add an `eval` job to `.github/workflows/ci.yml` that runs `python -m app.eval run rag --dataset tests/data/rag_golden_set.json` on every PR touching RAG code. Post the metrics (faithfulness, relevance, latency) as a PR comment. Configure thresholds: PR fails if faithfulness < 0.7 or relevance < 0.7 (PB-02 trigger).
**Why:** Roadmap TM-4 (W15) requires "eval script runs in CI." PB-02 trigger metric requires automated evaluation.
**Expected Output:** Updated CI workflow; PR comment template.
**Dependencies:** RAG eval harness (Pod B W15); eval scaffold (W2).
**Handoff:** Pod B-Lead iterates on RAG based on eval results; Pod D monitors thresholds.
**Definition of Done:** PR touching RAG code triggers the eval; metrics posted; PR fails if below threshold.

**Task:** Run a load test on the RAG pipeline: simulate 5 concurrent users asking questions for 5 minutes. Measure P95 latency (target: < 3s per Tech Spec NFR-1, but roadmap target is < 2s under 50 users for W39 TM-12 — this is a baseline). Document results in `docs/p2/rag-load-test-w15.md`.
**Why:** v0.4 thin MVP (W16) requires "demo survives 5 questions without crashing." Load test reveals bottlenecks early.
**Expected Output:** Load test report; k6 script `scripts/load-test-rag.js`.
**Dependencies:** RAG service (Pod B W15); `/v1/rag/query` (Pod A W15).
**Handoff:** Pod D refines in W39 (TM-12) for the formal 50-user test.
**Definition of Done:** Test runs 5 min without crashing; P95 latency reported; bottlenecks flagged.

**Task:** Add RAG quality metrics to Grafana: panels for faithfulness score (last 50 queries), relevance score, RAG latency (P50/P95), citation count distribution, "I don't know" rate. Source data from the eval harness + Langfuse traces.
**Why:** R-02 (RAG quality, score 16) mitigation requires observability; PB-02 trigger requires monitoring.
**Expected Output:** `infra/grafana/dashboards/rag-quality.json`.
**Dependencies:** RAG eval harness (Pod B W15); Langfuse (W7); Grafana (W6).
**Handoff:** Pod B-Lead monitors during P2; TPM reviews at monthly reviews.
**Definition of Done:** Dashboard renders; data updates on each eval run.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** `/v1/rag/query` endpoint exposes Pod B's RAG service. Joint design.
- **Backend ↔ Frontend:** RAG response schema is the contract between backend and frontend citation rendering.
- **AI/ML ↔ DevOps/QA:** RAG eval harness in CI; RAG quality monitoring.
- **AI/ML ↔ TPM:** Demo PDF set chosen (DDM-1) — TPM notes for graduation prep runway (GPM-0 starts W20).
- **End-to-end (IM-5):** Query via curl → retrieval → reranker → RAG → cited answer. The AI pipeline is proven end-to-end.

#### Week 15 Definition of Done

1. `/v1/rag/query` endpoint works; returns answer + citations via curl.
2. Chat API skeleton exists; `chat_sessions` + `chat_messages` migrated.
3. RAG design doc (`docs/rag.md`) merged (DM-7).
4. RAG service implemented: prompt template, LLM call, citation parsing, faithfulness check.
5. RAG eval harness v1 implemented: 50 Q&A pairs; faithfulness + relevance metrics.
6. IM-5 verified: curl query returns cited answer.
7. Demo PDF set (3 courses × 5–10 PDFs) chosen (DDM-1).
8. Citation rendering wired to RAG response; source panel fetches chunks.
9. Chat UI polished for v0.4 thin MVP demo.
10. TM-4 met: RAG eval runs in CI; metrics posted as PR comments; thresholds enforced.
11. RAG load test (5 users, 5 min) passes; P95 latency reported.
12. RAG quality Grafana dashboard live.

---

### Week 16 — v0.4 Thin MVP (GATE 1)

#### Roadmap Context

- **Phase:** P2 AI Pipeline (CRITICAL PATH)
- **Milestone:** **v0.4 Thin MVP tag + demo (GATE 1)**; RAG eval harness v1 (continued)
- **Release:** v0.4 (tag `v0.4.0`)
- **Primary Objective:** Ship the v0.4 thin MVP: a pre-loaded PDF, no auth, a single chat box, an answer with citations. Deployed to a public URL. Demo survives 5 questions without crashing. This is the early warning gate — if it doesn't ship, PB-06 triggers.

#### Backend Pod

##### Objective
Wire the thin MVP backend: a simplified chat endpoint (no auth, no session persistence) that calls the RAG service. Deploy to a public URL.

##### Tasks

**Task:** Implement the thin MVP chat endpoint: `/v1/chat/thin-mvp` POST (no auth required) accepts `{question}` and returns `{answer, citations}` synchronously (not SSE — simpler for the demo). Internally calls `RetrievalService.retrieve(question, course_id=<demo_course>)` then `RAGService.generate_answer`. Hardcode the `course_id` to the demo PDF's course.
**Why:** Roadmap v0.4 thin MVP requires "Pre-loaded PDF + chat UI; ask question, get cited answer; demo survives 5 questions without crashing." The simplified endpoint avoids auth + SSE complexity for the demo. The full chat API (W17) adds auth + sessions + SSE.
**Expected Output:** `app/api/v1/chat.py::thin_mvp_chat`; integration test verifying 5 questions return answers without crashing.
**Dependencies:** Retrieval service (W14); RAG service (W15); demo PDF embedded.
**Handoff:** Pod C-Lead wires the `/chat` page to this endpoint.
**Definition of Done:** 5 sample questions return answers with citations within 5s each; no crashes; endpoint deployed to staging public URL.

**Task:** Deploy v0.4 to the public staging URL: configure DNS (if not already), verify HTTPS, smoke test the `/chat` page + `/v1/chat/thin-mvp` endpoint. Ensure the demo PDF is pre-loaded (OCR + chunks + embeddings in Qdrant).
**Why:** Roadmap v0.4 thin MVP exit criteria #6: "Deployed to a public URL."
**Expected Output:** Public URL accessible; smoke test passes.
**Dependencies:** All W9–W16 work.
**Handoff:** TPM announces the URL; advisor invited to Friday demo.
**Definition of Done:** URL accessible from outside the team; HTTPS enforced; demo PDF pre-loaded.

**Task:** Tag `v0.4.0` on `main` after Friday demo passes. Cut a GitHub Release with release notes referencing: OCR pipeline, chunking, embeddings, Qdrant, hybrid retrieval, reranker, RAG with citations, thin MVP chat endpoint.
**Why:** Roadmap v0.4 milestone (Nov 21, 2026 = W16) — **Gate 1**.
**Expected Output:** Git tag `v0.4.0`; GitHub Release published.
**Dependencies:** All W9–W16 DoD items + Gate 1 sign-off.
**Handoff:** TPM announces v0.4; all pod leads sign Gate 1.
**Definition of Done:** Tag exists; release notes complete; Gate 1 sign-off doc signed by all pod leads + TPM.

#### AI/ML & Data Pod

##### Objective
Verify the RAG eval harness passes the PB-02 threshold (faithfulness ≥ 0.7, relevance ≥ 0.7). If below, invoke PB-02 playbook. Iterate on RAG prompt if needed.

##### Tasks

**Task:** Run the RAG eval harness on the v0.4 thin MVP endpoint: 50 Q&A pairs, measure faithfulness + relevance. If either < 0.7, invoke PB-02 playbook (per Roadmap §Risk Mitigation Strategy): default branch is A (increase reranker weight) + D (add "If you don't know, say 'I don't know'" prompt). Document the decision.
**Why:** PB-02 trigger: "Faithfulness < 0.7 OR relevance < 0.7 on 50-Q golden set at W16." R-02 (RAG quality, score 16) mitigation.
**Expected Output:** Eval results report; PB-02 decision doc if triggered.
**Dependencies:** RAG eval harness (W15); thin MVP endpoint (Pod A W16).
**Handoff:** If PB-02 triggers, B-Lead implements the chosen branch by EOD W17; TPM informs the team.
**Definition of Done:** Eval results committed; faithfulness ≥ 0.7 AND relevance ≥ 0.7 (or PB-02 invoked with decision doc).

**Task:** Iterate on the RAG prompt if eval results are below threshold: apply PB-02 branch A (increase reranker weight from 0.5 to 0.7) and/or branch D (add explicit "I don't know" instruction). Re-run eval. Document before/after metrics.
**Why:** PB-02 default branch (A + D combined).
**Expected Output:** Updated prompt template; before/after eval report.
**Dependencies:** RAG eval harness (W15); prompt template (W15).
**Handoff:** Pod A-Lead deploys the updated prompt; Pod C-Lead verifies citations still render.
**Definition of Done:** Eval metrics improve to ≥ 0.7 on both faithfulness + relevance (or PB-02 escalation continues).

**Task:** Prepare 5 known-good demo questions for the v0.4 Friday demo: questions that the RAG service reliably answers with 2+ citations. Test each on staging; document expected answers.
**Why:** v0.4 thin MVP exit criterion #7: "demo survives 5 questions without crashing." Demo questions must be reliable.
**Expected Output:** `docs/demo-scripts/v0.4-questions.md` with 5 questions + expected answers.
**Dependencies:** RAG service (W15); demo PDF.
**Handoff:** TPM uses these for the Friday demo.
**Definition of Done:** 5 questions return reliable answers on staging; doc committed.

#### Frontend Pod

##### Objective
Wire the `/chat` page to the thin MVP endpoint. Polish for the v0.4 demo.

##### Tasks

**Task:** Wire the `/chat` page to `/v1/chat/thin-mvp`: on submit, POST the question, display loading state, render the answer with markdown + clickable citations, display source panel on citation click. Handle errors (network, 5xx) with a friendly message + retry button.
**Why:** Roadmap v0.4 thin MVP requires "chat UI; ask question, get cited answer." This is the final integration.
**Expected Output:** Updated `/chat` page with API integration; loading/error states.
**Dependencies:** Thin MVP endpoint (Pod A W16); citation rendering (W15); chat UI components (W9–W15).
**Handoff:** Pod C-Lead demos in W16 Friday demo.
**Definition of Done:** 5 demo questions return answers with citations; loading + error states work; demo passes.

**Task:** Polish the `/chat` page for the demo: ensure the page is visually clean (centered chat box, demo PDF title in header, "Powered by OpenLearn AI" footer). Add a subtle loading animation while waiting for the answer. Test on different screen sizes (desktop + tablet, mobile best-effort per OOS-8).
**Why:** v0.4 is the first demo to the advisor; visual polish matters for credibility.
**Expected Output:** Polished page; Lighthouse score ≥ 80 on Performance + Accessibility.
**Dependencies:** Chat UI (W9–W16).
**Handoff:** Pod C-Lead demos in W16 Friday demo.
**Definition of Done:** Page is visually clean; Lighthouse passes; demo flows smoothly.

#### DevOps / QA Pod

##### Objective
Validate the v0.4 thin MVP against Gate 1 criteria. Run the final load test (5 questions, no crash). Monitor RAG quality + cost during the demo.

##### Tasks

**Task:** Validate Gate 1 criteria (v0.4 Thin MVP sign-off): (1) specific PDF pre-loaded, (2) OCR has run, text + chunks in DB, (3) embeddings in vector DB, (4) simple chat UI accepts a question, (5) system returns an answer with at least 2 citations, (6) deployed to a public URL, (7) demo survives 5 questions without crashing. Document validation in `docs/gates/gate-1-v0.4-thin-mvp.md`.
**Why:** Roadmap Gate 1 sign-off criteria. All pod leads + TPM must sign.
**Expected Output:** Gate 1 validation doc; sign-off page.
**Dependencies:** All W9–W16 work.
**Handoff:** All pod leads + TPM sign; TPM announces Gate 1 passed.
**Definition of Done:** All 7 criteria verified; sign-off doc signed; Gate 1 passed.

**Task:** Monitor the v0.4 demo in real time: Grafana dashboard open during the demo; watch RAG latency, error rate, Qdrant query latency, LLM cost. If any metric spikes, document for post-demo retrospective.
**Why:** v0.4 is the first end-to-end AI pipeline demo; real-time monitoring catches issues.
**Expected Output:** Demo monitoring report (post-demo).
**Dependencies:** Grafana dashboards (W6–W15).
**Handoff:** Pod D reviews at W16 retro; informs W17+ improvements.
**Definition of Done:** Demo monitored; report committed; retro action items logged.

**Task:** Run a final smoke test on the public URL before the Friday demo: 5 demo questions, verify answers + citations, verify no crashes. If any fails, escalate immediately (PB-06 trigger if v0.4 cannot ship).
**Why:** PB-06 trigger: "v0.4 Thin MVP not demoable at W16." Final smoke test catches last-minute issues.
**Expected Output:** Smoke test report; PB-06 invocation doc if triggered.
**Dependencies:** Thin MVP endpoint (Pod A W16); demo questions (Pod B W16).
**Handoff:** If PB-06 triggers, TPM decides branch (A: slip to W18; B: invoke F-3 OpenAI embeddings; C: descope v0.5).
**Definition of Done:** Smoke test passes (or PB-06 invoked with decision).

#### Cross-Pod Integration

- **Backend ↔ Frontend:** Thin MVP endpoint + `/chat` page wired.
- **Backend ↔ AI/ML:** Thin MVP endpoint calls retrieval + RAG service.
- **AI/ML ↔ DevOps/QA:** RAG eval results; PB-02 trigger if below threshold.
- **End-to-end (IM-6):** User chats with document in browser, no auth, gets cited answer. The AI pipeline is proven end-to-end.

#### Week 16 Definition of Done

1. **v0.4.0 tagged; Gate 1 signed by all pod leads + TPM.**
2. Thin MVP endpoint deployed to public URL over HTTPS.
3. RAG eval harness passes (faithfulness ≥ 0.7, relevance ≥ 0.7) or PB-02 invoked with decision.
4. 5 known-good demo questions documented.
5. `/chat` page wired to thin MVP endpoint; loading + error states work.
6. `/chat` page polished; Lighthouse ≥ 80.
7. Gate 1 validation doc signed; all 7 criteria verified.
8. Demo monitoring report committed.
9. Friday demo (v0.4) passes on staging public URL; advisor invited.
10. If v0.4 ships on time: P2 continues toward W20 Tier 1 Freeze with full slack. If not: PB-06 triggers, P2/P3 timeline replanned.

---



### Week 17 — Full Chat API + E2E Student Flow

#### Roadmap Context

- **Phase:** P2 AI Pipeline
- **Milestone:** RAG chat API + streaming + chat UI; student flow integration; IM-7 (full student flow E2E Playwright test); TM-5 (E2E test green on staging)
- **Release:** v0.5 prep
- **Primary Objective:** Ship the full chat API with SSE streaming + session persistence. Wire the chat UI to the full API. Validate the full student flow end-to-end (auth → course → upload → chat) via Playwright. This is the integration week before the v0.5 + Tier 1 Freeze at W20.

#### Backend Pod

##### Objective
Ship the full chat API: `/v1/chat` POST (create session), `/v1/chat/{session_id}/message` POST (SSE stream), `/v1/chat/sessions` GET (list sessions), `/v1/chat/sessions/{id}` GET (session history). Replace the W15 skeleton with the real implementation.

##### Tasks

**Task:** Implement the full chat API: `/v1/chat` POST creates a `chat_sessions` row (with `user_id`, `material_id` or `course_id`, `title` auto-generated from the first message). `/v1/chat/{session_id}/message` POST accepts `{message}`, returns an SSE stream: calls `RetrievalService.retrieve` → `RAGService.generate_answer` (streaming via LiteLLM) → streams tokens to the client. After completion, saves the message to `chat_messages` table.
**Why:** Roadmap W17 sprint requires "RAG chat API + streaming + chat UI; `/v1/chat` SSE streaming; session persistence; chat interface with history, streaming, source panel." Tech Spec Section 22.1 mandates WebSocket/SSE for streaming; Section 25.2 mandates streaming for perceived responsiveness.
**Expected Output:** `app/api/v1/chat.py` (full implementation); `app/services/chat_service.py`; SSE handler tests.
**Dependencies:** Chat API skeleton (W15); retrieval + RAG (W14–W15); auth (W5).
**Handoff:** Pod C-Lead wires the chat UI to this endpoint; IM-7 verification by Pod D.
**Definition of Done:** POST creates a session; POST message returns an SSE stream; tokens render progressively; session history persists; tests pass.

**Task:** Implement `/v1/chat/sessions` GET (paginated list of user's sessions, newest first) and `/v1/chat/sessions/{id}` GET (session + messages, paginated). RBAC enforced (user can only see their own sessions).
**Why:** Tech Spec Section 20.2 lists chat history management; Pod C's SessionList component (W13) needs these endpoints.
**Expected Output:** `app/api/v1/chat.py::list_sessions`, `get_session`; tests.
**Dependencies:** Chat API (above); auth (W5).
**Handoff:** Pod C-Lead wires SessionList to list endpoint; Pod C-1 wires session detail view.
**Definition of Done:** Endpoints return paginated sessions; RBAC enforced; tests pass.

**Task:** Implement the student flow integration (IM-7): verify the full flow works end-to-end — student registers → logs in → enrolls in a course → views course materials → uploads a PDF → waits for OCR → chats with the material → receives cited answer. Fix any integration bugs.
**Why:** Roadmap W17 sprint requires "Student flow integration; Student enrolls → sees course → uploads → chats; E2E Playwright test." IM-7 milestone.
**Expected Output:** Bug fixes across the stack; integration test verifying the full flow.
**Dependencies:** All W5–W16 work.
**Handoff:** Pod D writes the formal E2E Playwright test (TM-5).
**Definition of Done:** Full flow works on staging without errors; ready for E2E test.

#### AI/ML & Data Pod

##### Objective
Optimize the RAG prompt based on W16 eval results. Implement streaming LLM response via the LiteLLM gateway. Begin multi-document RAG design (W18 ships it).

##### Tasks

**Task:** Implement streaming LLM response: update `LiteLLMReasoningProvider` to support `generate_stream(prompt, context)` that yields tokens one at a time (using LiteLLM's streaming API). Update `RAGService.generate_answer` to optionally stream. Update the chat API (Pod A W17) to consume the stream.
**Why:** Roadmap W17 sprint requires "SSE streaming." Tech Spec Section 25.2 mandates streaming for perceived responsiveness.
**Expected Output:** Updated `LiteLLMReasoningProvider`; updated `RAGService`; unit tests with mock stream.
**Dependencies:** LiteLLM gateway (W7); RAG service (W15).
**Handoff:** Pod A-Lead wires SSE in the chat API; Pod C-Lead renders streaming tokens.
**Definition of Done:** Mock LLM stream yields tokens; RAG service forwards them; tests pass.

**Task:** Apply PB-02 fixes if W16 eval triggered: implement the chosen branch (A: increase reranker weight; B: switch to stronger LLM; C: restrict to single-doc; D: "I don't know" prompt). Re-run eval. Document before/after.
**Why:** PB-02 default branch (A + D combined) — must be implemented within 1 week of trigger.
**Expected Output:** Updated RAG service + prompt; before/after eval report.
**Dependencies:** PB-02 decision (W16); RAG eval harness (W15).
**Handoff:** Pod A-Lead deploys; Pod C-Lead verifies citations still render.
**Definition of Done:** Eval metrics improve to ≥ 0.7 (or escalate to PB-02 branch B/C).

**Task:** Begin multi-document RAG design (W18 ships it): plan the retrieval flow when a student asks a question that should span all materials in a course (not just one material). Design doc-level filters (course-level retrieval, then filter by material). Plan context assembly with multi-material citations.
**Why:** Roadmap W18 sprint requires "Multi-document RAG (single-course); Retrieval spans all docs in a course; doc-level filters." Tech Spec Section 12.2 retrieval process supports filters.
**Expected Output:** `docs/plans/multi-doc-rag.md` design doc.
**Dependencies:** Retrieval service (W14); RAG service (W15).
**Handoff:** Pod B-1 implements in W18.
**Definition of Done:** Design doc reviewed; implementation plan clear.

#### Frontend Pod

##### Objective
Wire the chat UI to the full chat API. Build the chat session list (history) + session detail view. Validate the student flow end-to-end with Pod D's E2E test.

##### Tasks

**Task:** Wire the chat UI to the full chat API: update `/chat` to require auth (redirect to `/login` if no token). On submit, POST to `/v1/chat` to create a session, then POST message to `/v1/chat/{session_id}/message` and consume the SSE stream. Render streaming tokens. Save session to the SessionList.
**Why:** Roadmap W17 sprint requires "Chat works in browser via curl and UI." Tech Spec Section 20.2 lists RAG Chat Interface.
**Expected Output:** Updated `/chat` page with auth + SSE + session persistence; integration tests.
**Dependencies:** Chat API (Pod A W17); streaming (Pod B W17); chat UI components (W9–W16).
**Handoff:** Pod C-Lead demos in W17 Friday demo; Pod D writes E2E test.
**Definition of Done:** Auth works; SSE stream renders progressively; session saved; tests pass.

**Task:** Build the chat session list + detail view: SessionList component (W13 skeleton) wired to `/v1/chat/sessions`. Clicking a session opens the detail view at `/chat/{session_id}` showing the message history + a continued chat input.
**Why:** Tech Spec Section 20.2 lists chat history management.
**Expected Output:** Updated SessionList; `frontend/src/app/chat/[session_id]/page.tsx` detail view.
**Dependencies:** Chat sessions API (Pod A W17); SessionList (W13).
**Handoff:** Pod C-Lead demos in W17 Friday demo.
**Definition of Done:** Session list renders; clicking opens detail; history loads; continued chat works.

**Task:** Polish the student flow for the W17 demo: register → login → enroll in a demo course → view materials → upload a PDF → wait for OCR → chat with the material. Each step should have clear loading + success + error states. Ensure no dead-ends.
**Why:** IM-7 verification; v0.5 prep.
**Expected Output:** Polished flow; bug fixes.
**Dependencies:** All W5–W17 work.
**Handoff:** Pod D writes the formal E2E Playwright test.
**Definition of Done:** Flow is smooth; no dead-ends; demo-ready.

#### DevOps / QA Pod

##### Objective
Write the E2E Playwright test (TM-5) covering the full student flow. Run on staging nightly + on every release tag. Monitor chat API performance.

##### Tasks

**Task:** Implement TM-5: E2E Playwright test covering the full student flow — register → login → enroll in course → upload PDF → wait for OCR → chat with material → verify cited answer. Run on staging nightly + on every release tag. Run time target: < 15 min.
**Why:** Roadmap TM-5 (W17) requires "E2E test (Playwright) for student flow; 1 E2E test green on staging." Roadmap §Testing Strategy mandates E2E tests on staging nightly.
**Expected Output:** `frontend/tests/e2e/student-flow.spec.ts`; CI integration (nightly + on tag).
**Dependencies:** Full chat API (Pod A W17); chat UI (Pod C W17); staging environment.
**Handoff:** Pod D runs nightly; failures wake on-call.
**Definition of Done:** Test passes on staging; runs in < 15 min; CI integration works.

**Task:** Monitor chat API performance: add Grafana panels for chat API request rate, P50/P95 latency, error rate, SSE stream duration. Configure alert: P95 > 5s triggers review.
**Why:** v0.5 + Tier 1 Freeze (W20) requires the chat API to be production-grade; R-09 (DB performance) mitigation.
**Expected Output:** `infra/grafana/dashboards/chat-api.json`; alert rule.
**Dependencies:** Chat API (Pod A W17); Grafana (W6).
**Handoff:** Pod A-Lead monitors; addresses bottlenecks before W20.
**Definition of Done:** Dashboard renders; alert fires on synthetic slow request.

**Task:** Run integration tests for the chat API: register → login → create session → send message → verify SSE stream → verify session history. Add to CI integration-test job.
**Why:** TM-2 (W8) coverage ≥ 80% on auth + course CRUD; chat API needs similar coverage.
**Expected Output:** `backend/tests/integration/test_chat_api.py`; coverage report.
**Dependencies:** Chat API (Pod A W17).
**Handoff:** Pod D runs in CI on every PR.
**Definition of Done:** Tests pass; coverage ≥ 80% on chat module.

#### Cross-Pod Integration

- **Backend ↔ Frontend:** Chat API + chat UI fully wired. SSE stream end-to-end.
- **Backend ↔ AI/ML:** Chat API calls retrieval + RAG service. Streaming LLM response.
- **AI/ML ↔ DevOps/QA:** PB-02 fixes (if triggered); RAG eval monitoring.
- **End-to-end (IM-7):** Register → login → enroll → upload → chat → cited answer. E2E Playwright test green (TM-5).

#### Week 17 Definition of Done

1. Full chat API shipped: `/v1/chat`, `/v1/chat/{session_id}/message` (SSE), `/v1/chat/sessions`, `/v1/chat/sessions/{id}`.
2. Streaming LLM response via LiteLLM gateway works.
3. PB-02 fixes applied (if triggered); eval metrics ≥ 0.7.
4. Multi-doc RAG design doc merged.
5. Chat UI wired to full API; auth + SSE + session persistence work.
6. Chat session list + detail view built.
7. Student flow polished for demo.
8. TM-5 met: E2E Playwright test passes on staging; runs in < 15 min.
9. Chat API Grafana dashboard live; alert configured.
10. Chat API integration tests pass in CI; coverage ≥ 80%.

---

### Week 18 — Multi-Document RAG + Tier 1 Freeze Draft

#### Roadmap Context

- **Phase:** P2 AI Pipeline
- **Milestone:** Multi-document RAG (single-course) + Tier 1 Freeze draft; ADRs 1–15 complete; interface contracts frozen; freeze review meeting
- **Release:** v0.5 prep
- **Primary Objective:** Ship multi-document RAG (retrieval spans all materials in a course, with doc-level filters). Draft all 15 Tier 1 ADRs. Begin the Tier 1 Architecture Freeze review process.

#### Backend Pod

##### Objective
Ship multi-document RAG API support. Finalize the Tier 1 interface contracts (1–5) with Pod B. Begin ADRs 12–15 (final batch before Tier 1 Freeze).

##### Tasks

**Task:** Update the retrieval service + chat API to support multi-document RAG: when a student asks a question in a course context (no specific material), retrieval spans all materials in the course. Add `course_id` filter to the Qdrant search. Add doc-level filters to the chat API (`?material_id=X` to restrict to one material). Citations include `material_id` + `material_title` so the UI can distinguish sources.
**Why:** Roadmap W18 sprint requires "Multi-document RAG (single-course); Retrieval spans all docs in a course; doc-level filters." Per OOS-7, cross-course RAG is out of scope, but within-course multi-doc is in scope.
**Expected Output:** Updated `RetrievalService.retrieve` (supports course-level retrieval); updated chat API; integration tests.
**Dependencies:** Retrieval service (W14); chat API (W17); Qdrant filters.
**Handoff:** Pod C-1 updates the chat UI to show doc-level citation badges; Pod B-Lead evaluates multi-doc retrieval quality.
**Definition of Done:** A question in a course context retrieves from all materials; doc-level filters work; citations include material info.

**Task:** Draft ADRs 12–15 (final batch for Tier 1):
- ADR-012: API versioning strategy (`/v1/` prefix, breaking changes require `/v2/`).
- ADR-013: Env management (Pydantic Settings, `.env` per environment, secrets in GitHub Actions).
- ADR-014: Deployment topology (Docker Compose staging, k3s prod, single-node — per C-11 resolution).
- ADR-015: Pod ownership boundaries (Pod A owns Backend + Qdrant ops; Pod B owns AI/ML algorithms; Pod C owns Frontend; Pod D owns DevOps + eval harness — per Roadmap §Pod Responsibilities).
Mark all `Proposed`; target `Accepted` by W19.
**Why:** Roadmap DM-8 (W19) requires "ADRs 1–15 complete." Tier 1 Freeze (W20) requires all 15 ADRs merged.
**Expected Output:** 4 ADR markdown files.
**Dependencies:** ADRs 1–11 (W1–W14).
**Handoff:** Pod leads review in W18; merge by W19.
**Definition of Done:** 4 ADRs opened; reviewed by all pod leads; ready for W19 merge.

**Task:** Co-author the Tier 1 interface contracts doc with Pod B: `docs/contracts/tier-1.md` listing all 5 contracts (OCR output schema, chunk schema, embedding I/O, vector DB query API, RAG request/response) with examples + JSON schemas.
**Why:** Roadmap §Frozen Interface Contracts: "All 5 Tier 1 interface contracts documented with examples" is a Gate 2 sign-off criterion.
**Expected Output:** `docs/contracts/tier-1.md` (single doc) or 5 separate `docs/contracts/01-05-*.md` files.
**Dependencies:** Contracts 1–5 drafts (W9–W15); ADRs 7–11.
**Handoff:** All pod leads + TPM sign at W20 Tier 1 Freeze.
**Definition of Done:** All 5 contracts documented with examples; reviewed by A-Lead + B-Lead + C-Lead.

#### AI/ML & Data Pod

##### Objective
Implement multi-document retrieval. Run RAG eval on multi-doc queries. Finalize ADRs 7–11 (OCR choice, embedding choice, chunking strategy, embedding I/O contract, vector DB query API contract).

##### Tasks

**Task:** Implement multi-document retrieval: update `RetrievalService.retrieve` to accept `course_id` (instead of `material_id`) and retrieve from all materials in the course. Apply course-level metadata filter to Qdrant. Re-rank across materials. Update citations to include `material_id` + `material_title`.
**Why:** Roadmap W18 sprint requires multi-doc RAG. Pod A exposes the API; Pod B implements the retrieval logic.
**Expected Output:** Updated `RetrievalService`; integration tests.
**Dependencies:** Retrieval service (W14); Qdrant filters.
**Handoff:** Pod A-Lead updates the chat API; Pod C-1 updates the UI.
**Definition of Done:** Multi-doc retrieval returns citations from multiple materials; tests pass.

**Task:** Run RAG eval on multi-doc queries: extend the golden set with 10 multi-doc Q&A pairs (questions that require context from multiple materials in a course). Measure faithfulness + relevance. Compare to single-doc performance.
**Why:** Multi-doc RAG is riskier (more context, potential for cross-material noise); R-14 (cross-course noise) mitigation (within-course is in scope, but quality must be verified).
**Expected Output:** Extended golden set; multi-doc eval report.
**Dependencies:** RAG eval harness (W15); multi-doc retrieval (above).
**Handoff:** Pod B-Lead iterates if quality drops; TPM reviews.
**Definition of Done:** Multi-doc faithfulness + relevance ≥ 0.7 (or PB-02 escalation).

**Task:** Finalize ADRs 7–11: move status from `Proposed` to `Accepted` after pod-lead review. Ensure each ADR has: Context, Decision, Alternatives, Consequences, Open Questions (per Roadmap ADR template).
**Why:** Tier 1 Freeze (W20) requires all 15 ADRs merged and reviewed.
**Expected Output:** 5 ADRs marked `Accepted` and merged.
**Dependencies:** ADR drafts (W5–W14); pod-lead reviews.
**Handoff:** TPM publishes the ADR index `docs/adr/README.md`.
**Definition of Done:** 5 ADRs merged; index updated.

#### Frontend Pod

##### Objective
Update the chat UI to support multi-document citations. Polish the chat interface for the v0.5 demo.

##### Tasks

**Task:** Update the chat UI to display doc-level citation badges: each citation `[1]` shows the material title in the source panel. Add a filter dropdown in the chat UI to restrict retrieval to a specific material (default: all materials in the course).
**Why:** Tech Spec Section 12.1 mentions citation grounding; multi-doc citations need material distinction for the user.
**Expected Output:** Updated `SourcePanel.tsx` with material title; `MaterialFilter.tsx` dropdown.
**Dependencies:** Multi-doc chat API (Pod A W18); chat UI (W17).
**Handoff:** Pod C-Lead demos in W18 Friday demo.
**Definition of Done:** Citations show material titles; filter dropdown works; UI is clean.

**Task:** Polish the chat interface for the v0.5 demo: ensure the chat page works smoothly on staging. Add a "demo mode" banner. Test with the demo PDF set (15–30 PDFs from W15). Ensure 5 demo questions work reliably.
**Why:** v0.5 (W20) is the full MVP demo to the advisor; polish matters.
**Expected Output:** Polished chat UI; demo script draft.
**Dependencies:** Multi-doc RAG (Pod B W18); chat UI (W17).
**Handoff:** Pod C-Lead demos in W20 Friday demo (v0.5).
**Definition of Done:** Chat works smoothly; demo script committed; 5 questions reliable.

#### DevOps / QA Pod

##### Objective
Validate TM-6 (coverage ≥ 40% on critical paths). Continue monitoring. Begin the Tier 1 Freeze review process.

##### Tasks

**Task:** Validate TM-6: run `pytest --cov=app --cov-report=term` and confirm coverage ≥ 40% on critical paths (auth, course CRUD, materials, OCR pipeline, retrieval, RAG, chat API). If below, pair with Pod A + Pod B to add tests.
**Why:** Roadmap TM-6 (W20) requires "Coverage ≥ 40% on critical paths; Measured in CI." This is the W20 gate target; measure now to identify gaps.
**Expected Output:** Coverage report; test additions if needed.
**Dependencies:** All W5–W18 work.
**Handoff:** Pod D finalizes at W20 (TM-6 sign-off).
**Definition of Done:** Coverage ≥ 40% on critical paths (or test additions planned for W19–W20).

**Task:** Begin the Tier 1 Architecture Freeze review process: circulate the 5 Tier 1 interface contracts (Pod A W18) + 15 ADRs to all pod leads. Schedule the W20 freeze review meeting. Prepare the sign-off doc `docs/gates/gate-2-tier-1-freeze.md`.
**Why:** Roadmap W19 sprint requires "Tier 1 Architecture Freeze review." W20 signs the freeze.
**Expected Output:** Review schedule; sign-off doc draft.
**Dependencies:** Tier 1 contracts (Pod A W18); ADRs 1–15.
**Handoff:** TPM runs the W20 freeze review meeting; all pod leads + TPM sign.
**Definition of Done:** Review meeting scheduled; sign-off doc drafted; all pod leads have reviewed the contracts.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Multi-doc retrieval implementation is joint.
- **Backend ↔ Frontend:** Multi-doc chat API + UI integration.
- **AI/ML ↔ DevOps/QA:** Multi-doc RAG eval; coverage validation.
- **TPM ↔ All Pods:** Tier 1 Freeze review process begins.

#### Week 18 Definition of Done

1. Multi-document RAG shipped: course-level retrieval + doc-level filters + material-aware citations.
2. ADRs 12–15 drafted (final batch).
3. Tier 1 interface contracts doc (1–5) co-authored with Pod B.
4. Multi-doc retrieval implemented; RAG eval on multi-doc queries passes (≥ 0.7).
5. ADRs 7–11 marked `Accepted` and merged.
6. Chat UI updated for multi-doc citations + material filter.
7. Chat UI polished for v0.5 demo; demo script drafted.
8. TM-6 prep: coverage ≥ 40% on critical paths (or test additions planned).
9. Tier 1 Freeze review meeting scheduled; sign-off doc drafted.

---

### Week 19 — Polish + Bug Fixes + Tier 1 Freeze Review

#### Roadmap Context

- **Phase:** P2 AI Pipeline
- **Milestone:** Polish + bug fixes + Tier 1 Architecture Freeze review; address top-20 bugs from W17 demo; all pod leads sign Tier 1
- **Release:** v0.5 prep (final week)
- **Primary Objective:** Fix top-20 bugs from the W17 demo. Merge ADRs 12–15. Complete the Tier 1 Architecture Freeze review. Sign the freeze at the end of the week (formal sign-off is W20, but review concludes here).

#### Backend Pod

##### Objective
Fix top backend bugs. Merge ADRs 12–15. Finalize the Tier 1 interface contracts. Prep the v0.5 demo.

##### Tasks

**Task:** Fix top-10 backend bugs from the W17 demo (TPM triages the top-20 across all pods; Pod A gets ~10). Common issues: chat API SSE edge cases, RBAC on multi-doc retrieval, race conditions in async job status updates, error handling on LLM gateway timeouts.
**Why:** Roadmap W19 sprint requires "Address top-20 bugs from W17 demo." Quality gate for v0.5.
**Expected Output:** Bug fixes; updated tests covering each bug.
**Dependencies:** W17 demo bug list (TPM).
**Handoff:** Pod D re-runs E2E tests to verify fixes.
**Definition of Done:** Top-10 backend bugs fixed; tests pass; bug count ≤ 5 open P1s by EOD W19.

**Task:** Merge ADRs 12–15 (after pod-lead review). Update the ADR index `docs/adr/README.md`. All 15 ADRs now `Accepted`.
**Why:** Roadmap DM-8 (W19) requires "ADRs 1–15 complete."
**Expected Output:** 4 ADRs merged; index updated.
**Dependencies:** ADR drafts (W18); pod-lead reviews.
**Handoff:** TPM announces ADRs complete; Tier 1 Freeze can proceed.
**Definition of Done:** 15 ADRs merged; index complete; all marked `Accepted`.

**Task:** Finalize the Tier 1 interface contracts doc: incorporate review feedback from W18. Ensure each contract has: schema (JSON Schema or Pydantic), example request + response, error cases, version. Publish to `docs/contracts/tier-1.md`.
**Why:** Gate 2 sign-off requires "All 5 Tier 1 interface contracts documented with examples."
**Expected Output:** Final `docs/contracts/tier-1.md`.
**Dependencies:** Contracts draft (W18); review feedback.
**Handoff:** All pod leads + TPM sign at W20 freeze meeting.
**Definition of Done:** All 5 contracts finalized; examples complete; ready for sign-off.

#### AI/ML & Data Pod

##### Objective
Fix top AI/ML bugs. Finalize the RAG design doc. Prep the v0.5 demo with 5 known-good multi-doc questions.

##### Tasks

**Task:** Fix top-5 AI/ML bugs from the W17 demo: RAG prompt edge cases (empty retrieval, single chunk), reranker timeouts on long queries, multi-doc retrieval noise, Arabic content quality. Re-run RAG eval after each fix.
**Why:** Roadmap W19 sprint requires addressing top-20 bugs; AI/ML gets ~5.
**Expected Output:** Bug fixes; updated eval results.
**Dependencies:** W17 demo bug list; RAG eval harness (W15).
**Handoff:** Pod D re-runs eval in CI to verify improvements.
**Definition of Done:** Top-5 AI/ML bugs fixed; eval metrics ≥ 0.7.

**Task:** Finalize the RAG design doc (`docs/rag.md`, DM-7 — was drafted W15, finalize now with multi-doc additions): add multi-doc retrieval section, citation format for multi-material, eval methodology for multi-doc.
**Why:** DM-7 was due W15; finalize with multi-doc learnings.
**Expected Output:** Final `docs/rag.md`.
**Dependencies:** Multi-doc RAG (W18).
**Handoff:** TPM publishes; Docusaurus updated.
**Definition of Done:** Doc merged; reviewed by B-Lead + D-Lead.

**Task:** Prep 5 known-good multi-doc demo questions for v0.5: questions that span multiple materials in the demo course. Test each on staging; document expected answers + which materials are cited.
**Why:** v0.5 demo (W20) requires reliable multi-doc questions.
**Expected Output:** `docs/demo-scripts/v0.5-questions.md`.
**Dependencies:** Multi-doc RAG (W18); demo PDF set (W15).
**Handoff:** TPM uses for W20 demo.
**Definition of Done:** 5 multi-doc questions return reliable answers; doc committed.

#### Frontend Pod

##### Objective
Fix top frontend bugs. Polish the UI for the v0.5 demo. Finalize user-facing docs.

##### Tasks

**Task:** Fix top-5 frontend bugs from the W17 demo: SSE stream rendering edge cases, source panel scroll, mobile responsiveness (best-effort per OOS-8), accessibility issues (keyboard navigation, screen reader).
**Why:** Roadmap W19 sprint; Pod C gets ~5 bugs.
**Expected Output:** Bug fixes; updated Storybook stories.
**Dependencies:** W17 demo bug list.
**Handoff:** Pod D re-runs E2E tests.
**Definition of Done:** Top-5 frontend bugs fixed; Lighthouse a11y ≥ 90 on critical paths.

**Task:** Polish the v0.5 demo UI: ensure the full student flow (register → login → enroll → upload → chat) is visually clean. Add transitions between steps. Ensure the demo "tells a story" (each step demonstrates a capability).
**Why:** v0.5 is the full MVP demo to the advisor; polish matters.
**Expected Output:** Polished UI; demo script.
**Dependencies:** All W5–W19 work.
**Handoff:** Pod C-Lead demos in W20 Friday demo.
**Definition of Done:** Demo flows smoothly; visual polish complete.

#### DevOps / QA Pod

##### Objective
Re-run E2E + integration tests after bug fixes. Validate TM-6 (coverage ≥ 40%). Finalize the Tier 1 Freeze sign-off doc.

##### Tasks

**Task:** Re-run the E2E Playwright test (TM-5) + integration tests after bug fixes. Verify all pass. If any fail, escalate to the relevant pod.
**Why:** W19 bug fixes must not regress W17 tests.
**Expected Output:** Test results report; bug fixes if regressed.
**Dependencies:** Bug fixes (Pod A + Pod B + Pod C W19).
**Handoff:** Pod D signs off on test stability for v0.5.
**Definition of Done:** E2E + integration tests pass on staging.

**Task:** Validate TM-6: coverage ≥ 40% on critical paths. Run final coverage report. If below, escalate to TPM (may trigger a small descope or a W20 test sprint).
**Why:** Roadmap TM-6 (W20) is a Gate 2 sign-off criterion.
**Expected Output:** Coverage report; sign-off or escalation.
**Dependencies:** All W5–W19 work.
**Handoff:** TPM includes in Gate 2 sign-off.
**Definition of Done:** Coverage ≥ 40% on critical paths (or escalation documented).

**Task:** Finalize the Tier 1 Architecture Freeze sign-off doc `docs/gates/gate-2-tier-1-freeze.md`: list all 12 sign-off criteria (per Roadmap Gate 2), mark each as met/pending, include the 5 contract references + 15 ADR references + architecture diagram (W20 task below). Circulate to all pod leads + TPM for signature.
**Why:** Roadmap W20 signs Tier 1 Freeze. The doc must be ready by start of W20.
**Expected Output:** Final sign-off doc.
**Dependencies:** Tier 1 contracts (Pod A W19); ADRs 1–15 (Pod A W19); coverage report (above).
**Handoff:** TPM runs the W20 freeze review meeting; all pod leads + TPM sign.
**Definition of Done:** Doc finalized; all criteria marked; ready for W20 signature.

#### Cross-Pod Integration

- **All Pods:** Bug fixing sprint. Top-20 bugs triaged and assigned across pods.
- **TPM ↔ All Pods:** Tier 1 Freeze review process; sign-off doc preparation.
- **DevOps/QA ↔ All Pods:** Test re-runs verify fixes; coverage validation.

#### Week 19 Definition of Done

1. Top-20 bugs from W17 demo addressed (≤ 5 P1s open by EOD W19).
2. ADRs 12–15 merged; all 15 ADRs marked `Accepted` (DM-8).
3. Tier 1 interface contracts doc finalized.
4. Top-5 AI/ML bugs fixed; RAG eval metrics ≥ 0.7.
5. RAG design doc finalized (DM-7).
6. 5 known-good multi-doc demo questions documented.
7. Top-5 frontend bugs fixed; Lighthouse a11y ≥ 90.
8. v0.5 demo UI polished.
9. E2E + integration tests pass on staging after bug fixes.
10. TM-6 met: coverage ≥ 40% on critical paths (or escalation).
11. Tier 1 Freeze sign-off doc finalized; ready for W20 signature.

---

### Week 20 — v0.5 Full MVP + Tier 1 Architecture Freeze (GATE 2)

#### Roadmap Context

- **Phase:** P2 AI Pipeline (final week)
- **Milestone:** **v0.5 + Tier 1 Architecture Freeze (GATE 2)**; architecture diagram v1; demo to advisor; GPM-0 (demo backlog started); DDM-1 (demo PDF set chosen — done W15, confirm)
- **Release:** v0.5 (tag `v0.5.0`)
- **Primary Objective:** Ship v0.5 (the full MVP). Sign the Tier 1 Architecture Freeze. Begin the 22-week graduation prep runway (GPM-0). This is the most important gate — if missed, every subsequent date slips.

#### Backend Pod

##### Objective
Ship v0.5. Sign the Tier 1 Architecture Freeze (Contract 1–5 frozen). Publish the architecture diagram v1 (DM-9). Begin P3 prep.

##### Tasks

**Task:** Verify v0.5 demo flow end-to-end on staging: register → login → enroll → upload PDF → OCR → chat with cited answer (multi-doc). Fix any last-minute bugs. Prepare demo script.
**Why:** Roadmap v0.5 milestone (Dec 19, 2026 = W20) — Gate 2.
**Expected Output:** Demo script; bug fixes.
**Dependencies:** All W5–W19 work.
**Handoff:** TPM runs the W20 Friday demo (advisor invited).
**Definition of Done:** Demo passes on staging; advisor demoed.

**Task:** Sign the Tier 1 Architecture Freeze: all pod leads + TPM sign `docs/gates/gate-2-tier-1-freeze.md`. Contracts 1–5 are now frozen. Post-freeze changes require a new ADR + migration plan + TPM approval + 2 pod leads' review.
**Why:** Roadmap Gate 2 sign-off. The most important gate.
**Expected Output:** Signed sign-off doc; contracts 1–5 marked frozen.
**Dependencies:** Sign-off doc (Pod D W19); all 12 Gate 2 criteria met.
**Handoff:** TPM announces Tier 1 Freeze; P3 starts W21 with frozen interfaces.
**Definition of Done:** All pod leads + TPM sign; contracts 1–5 frozen; post-freeze change protocol active.

**Task:** Co-author the architecture diagram v1 (DM-9) with TPM: single-page system diagram showing all components (Next.js, FastAPI, PG, Qdrant, Neo4j, MinIO, Redis, Celery, LiteLLM, Langfuse, Grafana stack). Use Mermaid or draw.io. Publish to `docs/architecture.md`.
**Why:** Roadmap DM-9 (W20) requires "Architecture diagram v1; Single-page system diagram." Gate 2 sign-off criterion #11.
**Expected Output:** `docs/architecture.md` with diagram + description.
**Dependencies:** All W1–W19 work.
**Handoff:** TPM publishes; all engineers reference; Docusaurus updated.
**Definition of Done:** Diagram renders; reviewed by all pod leads; published.

**Task:** Tag `v0.5.0` on `main` after Friday demo + Tier 1 Freeze sign-off. Cut a GitHub Release with release notes referencing: full MVP (auth + courses + uploads + OCR + chunking + embeddings + Qdrant + hybrid retrieval + reranker + RAG with citations + multi-doc + chat API with SSE + session persistence), 15 ADRs, 5 frozen interface contracts, architecture diagram v1.
**Why:** Roadmap v0.5 milestone — Gate 2.
**Expected Output:** Git tag `v0.5.0`; GitHub Release published.
**Dependencies:** All W5–W20 DoD items + Gate 2 sign-off.
**Handoff:** TPM announces v0.5; P3 (Knowledge & Cognition) starts W21.
**Definition of Done:** Tag exists; release notes complete; advisor notified; demo video recorded.

#### AI/ML & Data Pod

##### Objective
Finalize v0.5 RAG quality. Confirm DDM-1 (demo PDF set). Begin P3 KG design (W21 starts KG schema ADR). Begin graduation prep (GPM-0: demo backlog).

##### Tasks

**Task:** Run the final RAG eval on the v0.5 endpoint: 50 Q&A pairs (single-doc + multi-doc). Confirm faithfulness ≥ 0.7, relevance ≥ 0.7. Document the v0.5 baseline metrics for future regression comparison.
**Why:** v0.5 is the full MVP; RAG quality must be verified before the freeze. PB-02 trigger metric final check.
**Expected Output:** v0.5 RAG eval report; baseline metrics.
**Dependencies:** RAG eval harness (W15); v0.5 endpoint.
**Handoff:** Pod D monitors for regression in CI; Pod B-Lead references in W24 KG-backed retrieval boost.
**Definition of Done:** Eval passes; baseline metrics committed.

**Task:** Confirm DDM-1 (demo PDF set): verify the 15–30 PDFs chosen in W15 are committed + OCR-able + cover 3 courses. Hand off to Pod D for W24 ingestion.
**Why:** Roadmap DDM-1 (W20) requires the demo PDF set confirmed.
**Expected Output:** Confirmed manifest.
**Dependencies:** Demo PDF set (W15).
**Handoff:** Pod D ingests in W24 (DDM-2).
**Definition of Done:** Manifest confirmed; all PDFs OCR-able.

**Task:** Begin KG schema design (W21 ships ADR-016): research concept/relation extraction approaches (spaCy NER, LLM-based extraction with JSON mode, GLiNER). Draft the KG data model (concepts: id, name, description, difficulty; relations: source_concept_id, target_concept_id, type [is-a, prerequisite-of, part-of], provenance: chunk_id). Plan the extraction pipeline (W23 ships it).
**Why:** Roadmap W21 sprint requires "KG schema ADR + demo backlog started; ADR-016: KG data model." Tech Spec Section 13.1 specifies concept/relation types.
**Expected Output:** `docs/plans/kg-schema-design.md` design doc.
**Dependencies:** Tech Spec Section 13.
**Handoff:** Pod B-Lead implements ADR-016 in W21; Pod B-1 implements extraction pipeline in W23.
**Definition of Done:** Design doc reviewed; ready for W21 ADR.

**Task:** Begin GPM-0 (graduation prep): list "moments that would make good demo beats" — e.g., "upload PDF → see OCR working in real time", "ask question → get cited answer", "take quiz → see mastery update", "system recommends next concept". Commit to `docs/graduation/demo-backlog.md`.
**Why:** Roadmap GPM-0 (W20) requires "Demo backlog started." 22-week graduation prep runway begins.
**Expected Output:** `docs/graduation/demo-backlog.md` with 10+ beats.
**Dependencies:** All P0–P2 work (potential demo moments).
**Handoff:** TPM + advisor review at W24 (GPM-1: top-10 selected).
**Definition of Done:** 10+ beats listed; TPM acknowledges.

#### Frontend Pod

##### Objective
Finalize the v0.5 demo UI. Begin P3 UI prep: KG visualization research (W24 ships KG viz).

##### Tasks

**Task:** Finalize the v0.5 demo UI: ensure all flows are polished (register, login, enroll, upload, chat with multi-doc citations). Record a 5-min demo video (fallback for the advisor demo). Commit the video to `docs/demo-videos/v0.5.mp4`.
**Why:** v0.5 is the full MVP demo to the advisor; a fallback video is required per Roadmap §Graduation Preparation (GPM-9 references the final fallback video at W41, but per-version videos are good practice).
**Expected Output:** Final UI; demo video.
**Dependencies:** All W5–W19 work.
**Handoff:** TPM uses the video if the live demo fails.
**Definition of Done:** Demo video recorded; UI polished.

**Task:** Begin KG visualization research: evaluate Cytoscape.js vs D3.js vs vis.js for interactive concept graph rendering. Considerations: performance with 200+ nodes, mastery color-coding (green/yellow/red), edge type styling (is-a vs prerequisite-of vs part-of), zoom/filter/navigation. Plan the KG viz component (W24 ships it).
**Why:** Roadmap W24 sprint requires "KG viz UI; interactive concept graph (react-flow or d3)." Tech Spec Section 20.2 lists KG Visualizer as a primary frontend module.
**Expected Output:** `docs/plans/kg-viz-research.md` with library choice + rationale.
**Dependencies:** Tech Spec Section 20.2.
**Handoff:** Pod C-1 implements in W24.
**Definition of Done:** Research doc merged; library chosen.

#### DevOps / QA Pod

##### Objective
Finalize TM-6 sign-off (coverage ≥ 40%). Run the v0.5 release validation. Begin on-call rotation prep (W20 starts the 22-week graduation runway; on-call becomes real).

##### Tasks

**Task:** Sign off TM-6: coverage ≥ 40% on critical paths. Post the coverage report to the v0.5 release. If below, escalate to TPM (may delay Tier 1 Freeze).
**Why:** Roadmap TM-6 (W20) is a Gate 2 sign-off criterion.
**Expected Output:** Coverage report; TM-6 sign-off.
**Dependencies:** Coverage validation (W19).
**Handoff:** TPM includes in Gate 2 sign-off.
**Definition of Done:** Coverage ≥ 40% confirmed; TM-6 signed off.

**Task:** Run the v0.5 release validation: full E2E test on staging; smoke tests on the public URL; verify all Gate 2 criteria (Roadmap §Gate 2 sign-off criteria, 12 items). Document in `docs/releases/v0.5-validation.md`.
**Why:** Gate 2 sign-off requires all 12 criteria verified.
**Expected Output:** Validation report.
**Dependencies:** All W5–W20 work.
**Handoff:** TPM includes in Gate 2 sign-off; advisor notified.
**Definition of Done:** All 12 criteria verified; validation report committed.

**Task:** Begin on-call rotation prep: define the on-call schedule (rotating weekly across Pod D engineers + 1 cross-trained Pod A/B/C engineer as backup). Write the on-call runbook skeleton `docs/runbooks/on-call.md` (full runbook in W39). Configure PagerDuty (free tier) or Slack-based paging.
**Why:** Roadmap §Team Organization mentions on-call; Roadmap DM-14 (W39) requires "Runbooks: deploy, rollback, DR, on-call." On-call becomes real once v0.5 ships (production-grade system).
**Expected Output:** On-call schedule; runbook skeleton; paging configured.
**Dependencies:** v0.5 deploy; cross-training (W4–W20).
**Handoff:** On-call rotation starts W21; Pod D leads first week.
**Definition of Done:** Schedule published; runbook skeleton exists; paging tested.

#### Cross-Pod Integration

- **All Pods:** v0.5 + Tier 1 Freeze sign-off. All 12 Gate 2 criteria verified.
- **TPM ↔ All Pods:** Tier 1 Freeze signed; v0.5 tagged; architecture diagram v1 published; graduation prep runway (GPM-0) begins.
- **DevOps/QA ↔ All Pods:** TM-6 sign-off; release validation; on-call prep.
- **End-to-end (IM-7 + v0.5):** Full student flow works on staging public URL; advisor demoed.

#### Week 20 Definition of Done

1. **v0.5.0 tagged; Gate 2 (Tier 1 Architecture Freeze) signed by all pod leads + TPM.**
2. v0.5 demo to advisor passes on staging public URL.
3. All 5 Tier 1 interface contracts frozen (Contracts 1–5).
4. All 15 ADRs merged and marked `Accepted` (DM-8).
5. Architecture diagram v1 published (DM-9).
6. RAG eval v0.5 baseline metrics committed (faithfulness ≥ 0.7, relevance ≥ 0.7).
7. DDM-1 confirmed (demo PDF set).
8. KG schema design doc merged (prep for W21 ADR-016).
9. GPM-0: demo backlog started (10+ beats).
10. KG viz research doc merged (prep for W24).
11. TM-6 met: coverage ≥ 40% on critical paths.
12. v0.5 release validation report committed; all 12 Gate 2 criteria verified.
13. On-call rotation schedule + runbook skeleton ready.
14. Friday demo (v0.5) passes; advisor in attendance.
15. P3 (Knowledge & Cognition) starts W21 with frozen interfaces + 4 weeks of critical-path slack remaining.

---



### Week 21 — KG Schema ADR + Demo Backlog Started

#### Roadmap Context

- **Phase:** P3 Knowledge & Cognition
- **Milestone:** KG schema ADR + demo backlog started; holiday — light maintenance
- **Release:** Post-v0.5 (no tag this week)
- **Primary Objective:** Land ADR-016 (KG data model). Begin the concept extraction spike prep. Light maintenance week due to December holidays (capacity is lower; plan intentionally lighter).

#### Backend Pod

##### Objective
Begin the KG API design (W24 ships the API). Light maintenance: monitor v0.5 stability, fix any P1 bugs that surface.

##### Tasks

**Task:** Design the KG API: `/v1/kg/concepts` (list, filter by material/course), `/v1/kg/concepts/{id}` (detail + relations), `/v1/kg/relations` (list, filter by type). Plan RBAC (students read; instructors read + trigger re-extraction; admins manage). Plan pagination + filtering. Draft the API design doc.
**Why:** Roadmap W24 sprint requires "KG API + KG viz UI; `/v1/kg/concepts`, `/v1/kg/relations` endpoints." Tech Spec Section 22.3 lists `/knowledge-graph/{material_id}`.
**Expected Output:** `docs/plans/kg-api-design.md` design doc.
**Dependencies:** KG schema (Pod B W21); Tier 1 Freeze (W20).
**Handoff:** Pod A-Lead implements in W24; Pod C-1 builds KG viz consuming the API.
**Definition of Done:** Design doc reviewed; ready for W24 implementation.

**Task:** Light maintenance: monitor v0.5 on staging; triage any P1 bugs from the W20 demo; ensure on-call rotation is functioning. If no P1s, address tech debt from the P2 register.
**Why:** Roadmap W21 sprint: "Holiday — light maintenance; Bug triage; tech debt cleanup; Open bug count ≤ 10."
**Expected Output:** Bug fixes; tech debt burn-down.
**Dependencies:** v0.5 (W20).
**Handoff:** Pod D includes status in weekly retro.
**Definition of Done:** Open bug count ≤ 10; no P1s open.

#### AI/ML & Data Pod

##### Objective
Ship ADR-016 (KG schema). Begin concept extraction spike prep. Begin graduation outline v0 (W22 ships it, but prep starts).

##### Tasks

**Task:** Implement ADR-016 (KG data model): concepts table (`id`, `material_id`, `name`, `description`, `difficulty_level`, `created_at`), relations table (`id`, `source_concept_id`, `target_concept_id`, `type` [is-a, prerequisite-of, part-of], `provenance_chunk_id`, `confidence`, `created_at`). Plan Neo4j migration (or NetworkX for dev per Tech Spec Section 13.2). Mark ADR `Accepted`.
**Why:** Roadmap W21 sprint requires "ADR-016: KG data model (concepts, relations, provenance); demo backlog list started." Tier 2 Freeze (W30) freezes Contract 6 (KG concept/relation schema). Tech Spec Section 13.1 specifies concept/relation types.
**Expected Output:** `docs/adr/016-kg-schema.md` (Accepted); `docs/contracts/06-kg-schema.md`; Alembic migration for concepts + relations tables.
**Dependencies:** Tech Spec Section 13.
**Handoff:** Pod B-1 implements extraction pipeline in W23; Pod D deploys Neo4j in W23.
**Definition of Done:** ADR merged; contract doc published; migration runs.

**Task:** Begin concept extraction spike prep: research candidate approaches — (1) spaCy NER (rule-based + statistical), (2) LLM-based extraction with JSON mode (Qwen 2.5 / GPT-4o), (3) GLiNER (open-source NER), (4) KeyBERT (keyword extraction). Plan evaluation: precision/recall on 3 sample docs (manually labeled concepts). Plan the LLM prompt for relation extraction (few-shot with example triples per Tech Spec Section 13.1).
**Why:** Roadmap W22 sprint requires "Concept extraction spike; Compare spaCy + LLM-based extraction on 3 docs." Spike must be ready to run in W22.
**Expected Output:** `docs/plans/concept-extraction-spike.md` design doc.
**Dependencies:** ADR-016 (above); LiteLLM gateway (W7).
**Handoff:** Pod B-1 runs the spike in W22; Pod B-Lead implements pipeline in W23.
**Definition of Done:** Design doc merged; spike ready to run.

**Task:** Begin graduation outline v0 (GPM-2 is W26, but prep starts): draft the story arc — Problem → Solution → Architecture → Demo → AI Depth → Engineering Process → Future → Q&A. Reference the Roadmap §Presentation Structure.
**Why:** Roadmap GPM-2 (W26) requires "Presentation outline v0 (story arc)." 22-week graduation runway is active (GPM-0 started W20).
**Expected Output:** Draft outline `docs/graduation/outline-v0.md`.
**Dependencies:** GPM-0 (W20); Roadmap §Presentation Structure.
**Handoff:** TPM finalizes at W26.
**Definition of Done:** Outline draft exists; TPM acknowledges.

#### Frontend Pod

##### Objective
Light maintenance + KG viz component prep. Build the KG viz component skeleton (W24 ships the full viz).

##### Tasks

**Task:** Build the KG viz component skeleton: install Cytoscape.js (or D3.js per W20 research). Create `frontend/src/features/kg/components/KGGraph.tsx` that renders a mock graph (10 nodes, 15 edges) with mastery color-coding (green/yellow/red placeholders). Plan the API integration for W24.
**Why:** Roadmap W24 sprint requires "KG viz UI; interactive concept graph." Skeleton now lets W24 focus on API integration + real data.
**Expected Output:** `KGGraph.tsx` skeleton; Storybook story with mock data.
**Dependencies:** KG viz research (W20); Cytoscape.js install.
**Handoff:** Pod C-1 wires to KG API in W24.
**Definition of Done:** Mock graph renders in Storybook; zoom + pan work; nodes are color-coded.

**Task:** Light maintenance: monitor v0.5 frontend on staging; fix any P1 visual bugs; address tech debt (Storybook stories missing, accessibility issues from W19 Lighthouse report).
**Why:** Roadmap W21 sprint: "Holiday — light maintenance."
**Expected Output:** Bug fixes; Storybook story additions.
**Dependencies:** v0.5 (W20).
**Handoff:** Pod D includes status in retro.
**Definition of Done:** No P1 frontend bugs open; Lighthouse a11y ≥ 90 on critical paths.

#### DevOps / QA Pod

##### Objective
Light maintenance + Neo4j deploy prep. Continue on-call rotation. Continue cross-training.

##### Tasks

**Task:** Neo4j deploy prep: write `infra/docker-compose.staging.yml` Neo4j Community Edition service (port 7687 Bolt, 7474 HTTP), persistent volume, password auth. Plan backup script (daily snapshot to MinIO). Plan restore procedure.
**Why:** Roadmap W23 sprint requires "Neo4j deployed; schema; import script." Prep now so W23 focuses on integration. Tech Spec Section 13.2 lists Neo4j.
**Expected Output:** Neo4j compose spec; backup script plan.
**Dependencies:** Staging infra.
**Handoff:** Pod D deploys in W23; Pod B-1 imports KG in W23.
**Definition of Done:** Compose spec reviewed; ready for W23 deploy.

**Task:** On-call rotation: Pod D engineer on-call W21. Monitor v0.5 stability. Triage any Sentry errors. Document the on-call handoff process.
**Why:** On-call rotation started W20 (post-v0.5). Roadmap §Team Organization mentions on-call.
**Expected Output:** On-call log; handoff doc.
**Dependencies:** On-call schedule (W20).
**Handoff:** Next on-call engineer (W22) receives handoff.
**Definition of Done:** On-call week completes; no unpaged P1 incidents.

**Task:** Continue cross-training: Pod B engineer continues Qdrant ops shadowing (now also Neo4j ops). Document in `docs/cross-training.md`.
**Why:** Roadmap §Pod Cross-Training Plan continues through W20; now extending to Neo4j.
**Dependencies:** Neo4j deploy prep (above).
**Handoff:** Pod B engineer can triage Neo4j issues by W24.
**Definition of Done:** Pod B engineer performs Neo4j backup + restore under supervision.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** KG API design informs KG schema; both Pods coordinate on Contract 6.
- **AI/ML ↔ Frontend:** KG schema informs KG viz component design.
- **DevOps/QA ↔ AI/ML:** Neo4j deploy prep supports Pod B's W23 KG implementation.
- **TPM ↔ All Pods:** Light maintenance week; bug count ≤ 10.

#### Week 21 Definition of Done

1. KG API design doc merged (prep for W24).
2. Open bug count ≤ 10; no P1s open.
3. ADR-016 (KG schema) marked `Accepted`; Alembic migration for concepts + relations.
4. Concept extraction spike prep design doc merged.
5. Graduation outline v0 draft started.
6. KG viz component skeleton built (Storybook with mock data).
7. Neo4j deploy prep complete (compose spec + backup plan).
8. On-call rotation functioning; W21 handoff complete.
9. Pod B engineer cross-trained on Neo4j ops.

---

### Week 22 — Concept Extraction Spike + Graduation Outline v0

#### Roadmap Context

- **Phase:** P3 Knowledge & Cognition
- **Milestone:** Concept extraction spike; graduation outline v0; holiday — light maintenance
- **Release:** No tag
- **Primary Objective:** Run the concept extraction spike (spaCy vs LLM-based). Finalize the graduation outline v0. Light maintenance (holidays).

#### Backend Pod

##### Objective
Light maintenance + KG API implementation prep. Continue bug triage.

##### Tasks

**Task:** Begin KG API implementation skeleton: `app/api/v1/kg.py` with route stubs for `/v1/kg/concepts`, `/v1/kg/concepts/{id}`, `/v1/kg/relations`. Add Pydantic schemas for `Concept`, `Relation`. Plan the Neo4j repository (`app/repositories/kg_repository.py`) — for now, just the interface; implementation in W24 after Neo4j is deployed.
**Why:** Roadmap W24 sprint requires the KG API. Skeleton now lets W24 focus on Neo4j integration.
**Expected Output:** `app/api/v1/kg.py` skeleton; `app/domain/kg.py` Pydantic schemas; `app/repositories/kg_repository.py` interface.
**Dependencies:** KG schema (W21); Tier 1 Freeze (W20).
**Handoff:** Pod A-Lead implements in W24 after Neo4j deploy.
**Definition of Done:** Routes exist (return 501); schemas validate; ready for W24.

**Task:** Light maintenance: continue bug triage from W21. Address any tech debt items in the P2 register. Monitor v0.5 stability.
**Why:** Roadmap W22 sprint: "Holiday — light maintenance; Continue triage."
**Expected Output:** Bug fixes; tech debt burn-down.
**Dependencies:** W21 work.
**Handoff:** Pod D includes in retro.
**Definition of Done:** Bug count stable or decreasing; no new P1s.

#### AI/ML & Data Pod

##### Objective
Run the concept extraction spike. Compare spaCy vs LLM-based extraction on 3 sample docs. Produce a recommendation ADR-017 draft.

##### Tasks

**Task:** Run the concept extraction spike per `docs/plans/concept-extraction-spike.md`: process 3 sample docs (1 English ML textbook chapter, 1 Arabic document, 1 mixed) through (1) spaCy NER + custom rules, (2) LLM-based extraction with JSON mode (Qwen 2.5 via LiteLLM), (3) GLiNER (optional). Manually label ~30 concepts per doc as ground truth. Measure precision, recall, F1 for each approach. Measure latency + cost (for LLM).
**Why:** Roadmap W22 sprint requires "Concept extraction spike; Compare spaCy + LLM-based extraction on 3 docs." Tech Spec Section 13.1 specifies LLM-assisted extraction with JSON mode + few-shot prompting.
**Expected Output:** Filled `docs/spikes/concept-extraction-spike.md` with results; recommendation.
**Dependencies:** Spike prep (W21); LiteLLM gateway (W7); 3 sample docs.
**Handoff:** Pod B-Lead implements pipeline in W23 based on the recommendation.
**Definition of Done:** 3 docs processed; precision/recall/F1 measured; recommendation is LLM-based with JSON mode (typically wins on educational content).

**Task:** Draft ADR-017 (concept extraction approach): LLM-based extraction with JSON mode + few-shot prompting (per spike recommendation). Mark `Proposed`. Reference Tech Spec Section 13.1.
**Why:** Tier 2 Freeze (W30) requires the extraction approach documented.
**Expected Output:** `docs/adr/017-concept-extraction.md` (Proposed).
**Dependencies:** Spike results (above).
**Handoff:** Pod B-Lead finalizes in W23; freezes at W30.
**Definition of Done:** ADR opened; reviewed by B-Lead + D-Lead.

**Task:** Finalize graduation outline v0 (GPM-2): complete the story arc draft from W21. Add timing per section (2 min Problem, 3 min Solution, 4 min Architecture, 8 min Demo, 5 min AI Depth, 4 min Engineering Process, 2 min Future, 2 min Q&A). Reference Roadmap §Presentation Structure.
**Why:** Roadmap GPM-2 (W26) requires "Presentation outline v0 (story arc)." Finalize now (ahead of schedule due to holiday light week).
**Expected Output:** Final `docs/graduation/outline-v0.md`.
**Dependencies:** Outline draft (W21).
**Handoff:** TPM acknowledges; GPM-3 (W30 demo script skeleton) builds on this.
**Definition of Done:** Outline finalized; timing per section; TPM + advisor review at W26.

#### Frontend Pod

##### Objective
Continue KG viz component development. Build the concept detail view (W24 ships full integration).

##### Tasks

**Task:** Build the concept detail view: `frontend/src/app/(student)/kg/[conceptId]/page.tsx` showing a concept's name, description, difficulty, related concepts (prerequisite-of, is-a, part-of edges), and source chunks (provenance). Use mock data for now.
**Why:** Tech Spec Section 20.2 lists KG Visualizer as a primary module; concept detail supports navigation.
**Expected Output:** Concept detail page; Storybook story with mock data.
**Dependencies:** KG viz component skeleton (W21); design tokens (W2).
**Handoff:** Pod C-1 wires to KG API in W24.
**Definition of Done:** Page renders with mock data; related concepts clickable (placeholder navigation); provenance chunks listed.

**Task:** Light maintenance: continue bug triage. Polish any visual issues from W20 demo feedback.
**Why:** Roadmap W22 sprint: "Holiday — light maintenance."
**Expected Output:** Bug fixes; polish.
**Dependencies:** W21 work.
**Handoff:** Pod D includes in retro.
**Definition of Done:** No P1 frontend bugs open.

#### DevOps / QA Pod

##### Objective
Deploy Neo4j to staging (ahead of W23 KG implementation). Continue on-call rotation. Continue cross-training.

##### Tasks

**Task:** Deploy Neo4j to staging using the W21 compose spec. Create the constraints + indexes for the KG schema (Concept name unique, Relation type indexed). Verify the Bolt driver connects from the backend. Backup script tested.
**Why:** Roadmap W23 sprint requires "Neo4j deployed; schema; import script." Deploying a week early (light week) lets W23 focus on integration.
**Expected Output:** Neo4j running on staging; constraints + indexes created; backup script tested.
**Dependencies:** Neo4j deploy prep (W21).
**Handoff:** Pod B-1 imports KG data in W23.
**Definition of Done:** Neo4j reachable at `staging:7687`; backend connects; backup + restore tested.

**Task:** On-call rotation: Pod D engineer on-call W22. Continue monitoring v0.5. Document any incidents.
**Why:** On-call continues.
**Expected Output:** On-call log.
**Dependencies:** W21 handoff.
**Handoff:** Next on-call engineer (W23).
**Definition of Done:** No unpaged P1 incidents.

**Task:** Continue cross-training: Pod B engineer performs Neo4j Cypher query practice (read queries, simple traversals). Document.
**Why:** Roadmap §Pod Cross-Training Plan continues.
**Dependencies:** Neo4j deployed (above).
**Handoff:** Pod B engineer can independently query Neo4j by W24.
**Definition of Done:** Pod B engineer writes + runs 5 Cypher queries.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** KG API skeleton + concept extraction approach coordinated.
- **AI/ML ↔ DevOps/QA:** Neo4j deploy supports W23 KG implementation.
- **Frontend ↔ AI/ML:** KG viz + concept detail view align with KG schema.
- **TPM ↔ All Pods:** Graduation outline v0 finalized (GPM-2, ahead of schedule).

#### Week 22 Definition of Done

1. KG API skeleton + Pydantic schemas + repository interface committed.
2. Bug count stable or decreasing; no new P1s.
3. Concept extraction spike complete; recommendation documented.
4. ADR-017 (concept extraction) opened.
5. Graduation outline v0 finalized (GPM-2, ahead of schedule).
6. Concept detail view built (mock data).
7. Neo4j deployed to staging; backup + restore tested.
8. On-call W22 complete; no unpaged P1s.
9. Pod B engineer cross-trained on Neo4j Cypher queries.

---

### Week 23 — Concept Extraction Pipeline + Neo4j KG Storage

#### Roadmap Context

- **Phase:** P3 Knowledge & Cognition
- **Milestone:** Concept extraction pipeline + KG storage (Neo4j); DM-10 (KG design doc)
- **Release:** No tag
- **Primary Objective:** Ship the concept extraction pipeline: async job that takes chunks → extracts concepts + relations via LLM → stores in Neo4j. Populate KG with 200+ concepts from 5 sample docs. DM-10 (KG design doc) due.

#### Backend Pod

##### Objective
Implement the KG API (full version). Wire the concept extraction worker to write to Neo4j. Support Pod B's pipeline.

##### Tasks

**Task:** Implement the KG API (full version): `/v1/kg/concepts` GET (paginated, filter by material_id/course_id/difficulty), `/v1/kg/concepts/{id}` GET (detail + relations + provenance chunks), `/v1/kg/relations` GET (paginated, filter by type/source_concept/target_concept). Implement `app/repositories/kg_repository.py` using `neo4j` Python driver. RBAC enforced.
**Why:** Roadmap W24 sprint requires "KG API; `/v1/kg/concepts`, `/v1/kg/relations` endpoints." Building now (week ahead) lets W24 focus on KG viz UI integration.
**Expected Output:** Full `app/api/v1/kg.py`; `app/services/kg_service.py`; `app/repositories/kg_repository.py` (Neo4j).
**Dependencies:** KG API skeleton (W22); Neo4j (Pod D W22); KG schema (W21).
**Handoff:** Pod C-1 wires KG viz to these endpoints in W24.
**Definition of Done:** Endpoints return paginated concepts + relations; RBAC enforced; tests pass.

**Task:** Wire the concept extraction worker to write to Neo4j: when the extraction pipeline (Pod B W23) produces concepts + relations, the worker writes them to Neo4j via `KgRepository.store_concepts(concepts)` + `KgRepository.store_relations(relations)`. Handle duplicates (same concept name in same material → merge). Update material status to `kg_ready`.
**Why:** Tech Spec Section 13.2 specifies Neo4j as the KG storage backend.
**Expected Output:** Updated worker; integration tests verifying concepts + relations in Neo4j.
**Dependencies:** Concept extraction pipeline (Pod B W23); Neo4j (Pod D W22); KG API (above).
**Handoff:** Pod B-Lead populates KG with 200+ concepts from 5 docs (W23 task below).
**Definition of Done:** Worker writes concepts + relations to Neo4j; duplicates merged; status updated.

#### AI/ML & Data Pod

##### Objective
Ship the concept extraction pipeline. Populate the KG with 200+ concepts from 5 sample docs. Co-author the KG design doc (DM-10).

##### Tasks

**Task:** Implement the concept extraction pipeline: `app/workers/tasks/kg.py::extract_concepts(material_id)` that: (1) loads all chunks for a material, (2) for each chunk, calls `ReasoningInterface.extract_concepts(chunk_text)` via the PAL (using the LLM-based approach from the W22 spike), (3) parses the structured JSON output (concepts + relations with type + provenance), (4) batches writes to Neo4j via `KgRepository`, (5) updates material status to `kg_ready`. Apply few-shot prompting with example triples per Tech Spec Section 13.1.
**Why:** Roadmap W23 sprint requires "Concept extraction pipeline + KG storage (Neo4j); Async job: chunks → concepts + relations; LLM-assisted; Neo4j deployed; schema; import script." Tech Spec Section 13.1 specifies LLM-assisted extraction with JSON mode.
**Expected Output:** `app/workers/tasks/kg.py`; `app/services/kg_extraction_service.py`; integration tests.
**Dependencies:** LiteLLM gateway (W7); ADR-017 (W22); Neo4j (Pod D W22); chunks table (W10).
**Handoff:** Pod B-Lead populates KG with 5 sample docs (below).
**Definition of Done:** Pipeline runs on a sample doc; produces 30+ concepts + 50+ relations; writes to Neo4j; tests pass.

**Task:** Populate the KG with 5 sample docs (from the demo PDF set): run the extraction pipeline on each. Target ≥ 200 concepts total + ≥ 400 relations. Verify KG sanity: no orphan concepts (every concept has at least 1 relation), no self-loops, no duplicate concept names within a material. Document in `docs/p3/kg-population-w23.md`.
**Why:** Roadmap W23 sprint requires "5 docs → 200+ concepts; KG populated." Tech Spec Section 13.1.
**Expected Output:** Populated KG; sanity report.
**Dependencies:** Concept extraction pipeline (above); 5 sample docs.
**Handoff:** Pod D writes KG sanity tests (TM-7 prep) in W24; Pod C-1 builds KG viz consuming the populated KG.
**Definition of Done:** 200+ concepts in Neo4j; sanity checks pass; report committed.

**Task:** Co-author the KG design doc (`docs/kg.md`, DM-10 due W23) with Pod A-Lead: extraction pipeline (LLM-based with JSON mode), Neo4j schema (constraints, indexes), provenance tracking, sanity checks, fallback F-2 (JSONB in Postgres).
**Why:** Roadmap DM-10 (W23) requires `docs/kg.md`.
**Expected Output:** `docs/kg.md` (5+ pages).
**Dependencies:** KG implementation (W23); ADR-016 (W21); ADR-017 (W22).
**Handoff:** TPM publishes; all engineers reference.
**Definition of Done:** Doc merged; reviewed by A-Lead + D-Lead; in Docusaurus.

#### Frontend Pod

##### Objective
Continue KG viz development. Build the relations list view (W24 ships full viz integration).

##### Tasks

**Task:** Build the relations list view: `frontend/src/features/kg/components/RelationsList.tsx` showing all relations in a material, filterable by type (is-a, prerequisite-of, part-of). Each relation shows source concept → target concept + type badge + provenance chunk link. Mock data for now.
**Why:** Tech Spec Section 20.2 lists KG Visualizer; relations list complements the graph view for users who prefer tabular data.
**Expected Output:** `RelationsList.tsx`; Storybook story.
**Dependencies:** KG viz skeleton (W21); design tokens (W2).
**Handoff:** Pod C-1 wires to KG API in W24.
**Definition of Done:** Component renders with mock data; filters work; type badges render.

**Task:** Begin the KG viz API integration prep: plan the data fetching (TanStack Query hooks for `/v1/kg/concepts`, `/v1/kg/relations`), the graph layout algorithm (Cytoscape `cose` or `breadthfirst`), the mastery color-coding integration (when student mastery data is available in W28). Mock the API responses.
**Why:** Roadmap W24 sprint requires "KG browsable; frontend can query KG." Prep now lets W24 focus on real data.
**Expected Output:** `docs/plans/kg-viz-integration.md`; mock API responses in `frontend/src/features/kg/api/mocks.ts`.
**Dependencies:** KG viz skeleton (W21); KG API (Pod A W23).
**Handoff:** Pod C-1 implements in W24.
**Definition of Done:** Plan reviewed; mocks committed.

#### DevOps / QA Pod

##### Objective
Begin KG sanity tests (TM-7 prep). Monitor Neo4j performance. Continue on-call + cross-training.

##### Tasks

**Task:** Begin TM-7 prep: write KG sanity tests `backend/tests/integration/test_kg_sanity.py` covering: schema validation (every concept has required fields), cycle detection (no prerequisite cycles — A prereq B prereq A), orphan detection (every concept has ≥ 1 relation), duplicate detection (no same-name concepts in same material). Tests run against the populated KG.
**Why:** Roadmap TM-7 (W24) requires "KG sanity tests; Schema validation; cycle detection." R-04 (KG noisy/incorrect relations, score 9) mitigation requires sanity tests.
**Expected Output:** `backend/tests/integration/test_kg_sanity.py`; tests pass on the populated KG (200+ concepts).
**Dependencies:** KG populated (Pod B W23); Neo4j (W22).
**Handoff:** Pod D finalizes TM-7 sign-off in W24.
**Definition of Done:** Tests pass; sanity report committed.

**Task:** Monitor Neo4j performance: add Grafana panels for Neo4j query latency (P50/P95), storage usage, node/edge count, slow queries. Configure alert: Neo4j down > 2h triggers F-2 evaluation per R-11 mitigation.
**Why:** R-11 (Neo4j ops too heavy, score 9) mitigation requires monitoring; F-2 trigger ("Neo4j ops too heavy OR KG schema not converging").
**Expected Output:** `infra/grafana/dashboards/neo4j.json`; alert rule.
**Dependencies:** Neo4j (W22); Grafana (W6).
**Handoff:** Pod D monitors; if alert fires, D-Lead evaluates F-2 within 48h.
**Definition of Done:** Dashboard renders; alert fires when Neo4j is stopped (test by stopping the container).

**Task:** On-call rotation + cross-training: continue weekly rotation. Pod B engineer performs a Neo4j index rebuild + verifies KG queries still work.
**Why:** Roadmap §Pod Cross-Training Plan continues.
**Dependencies:** Neo4j (W22); populated KG (Pod B W23).
**Handoff:** Pod B engineer can independently triage Neo4j issues by W24.
**Definition of Done:** On-call W23 complete; Pod B engineer performs index rebuild.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** KG API + extraction worker + Neo4j storage — joint implementation.
- **Backend ↔ Frontend:** KG API + KG viz API integration prep.
- **AI/ML ↔ DevOps/QA:** KG sanity tests; Neo4j monitoring.
- **End-to-end (IM-8 prep):** OCR → chunks → concept extraction → KG populated with 200+ concepts.

#### Week 23 Definition of Done

1. KG API (full version) implemented; Neo4j repository works.
2. Concept extraction worker writes to Neo4j; duplicates merged.
3. Concept extraction pipeline runs on 5 sample docs; 200+ concepts + 400+ relations populated.
4. KG sanity report committed (no orphans, no self-loops, no duplicates).
5. KG design doc (`docs/kg.md`) merged (DM-10).
6. Relations list view built (mock data).
7. KG viz API integration plan + mocks committed.
8. TM-7 prep: KG sanity tests written; pass on populated KG.
9. Neo4j Grafana dashboard + alert configured.
10. On-call W23 complete; Pod B engineer performs Neo4j index rebuild.

---

### Week 24 — KG API + KG Viz UI + Demo Dataset v1 + Concept Extraction Spike Concludes

#### Roadmap Context

- **Phase:** P3 Knowledge & Cognition
- **Milestone:** KG API + KG viz UI + demo dataset v1 (DDM-2); TM-7 (KG sanity tests); GPM-1 (demo backlog top-10 selected); IM-8 (OCR → Concept extraction → KG)
- **Release:** v0.6 prep
- **Primary Objective:** Ship the KG API + KG viz UI end-to-end. Verify IM-8 (KG populated from new upload). Ingest the demo dataset v1 (all demo PDFs). TM-7 sign-off. GPM-1 (top-10 demo beats selected).

#### Backend Pod

##### Objective
Finalize the KG API. Support DDM-2 (demo dataset ingestion). Verify IM-8.

##### Tasks

**Task:** Finalize the KG API: polish pagination, filtering, RBAC. Add `/v1/kg/materials/{material_id}/concepts` GET (concepts for a specific material). Ensure OpenAPI docs are complete. Add integration tests covering all endpoints.
**Why:** Roadmap W24 sprint requires "KG API + KG viz UI; `/v1/kg/concepts`, `/v1/kg/relations` endpoints." Final version.
**Expected Output:** Finalized KG API; integration tests; OpenAPI docs updated.
**Dependencies:** KG API (W23); Neo4j (W22).
**Handoff:** Pod C-1 wires to KG viz.
**Definition of Done:** All endpoints work; tests pass; OpenAPI complete.

**Task:** Support DDM-2 (demo dataset ingestion): provide a script `scripts/ingest_demo_dataset.py` that ingests all demo PDFs (15–30 from W15) into staging — upload to MinIO, trigger OCR + chunking + embedding + KG extraction for each. Verify all PDFs process successfully. Document in `docs/p3/demo-dataset-v1.md`.
**Why:** Roadmap DDM-2 (W24) requires "Demo dataset v1: all demo PDFs ingested, OCR'd, embedded, in staging." Joint with Pod B + Pod D.
**Expected Output:** Ingestion script; demo dataset v1 report.
**Dependencies:** Demo PDF set (W15); full ingestion pipeline (W9–W23).
**Handoff:** Pod D verifies on staging; TPM notes for graduation prep.
**Definition of Done:** All 15–30 demo PDFs ingested; OCR + chunks + embeddings + KG in staging.

**Task:** Verify IM-8: upload a fresh PDF → OCR → chunks → concept extraction → KG populated. Verify the new concepts appear in the KG API. Document in `docs/p3/im-8-verification.md`.
**Why:** Roadmap IM-8 (W24) requires "OCR → Concept extraction → KG; KG populated from new upload."
**Expected Output:** IM-8 verification doc.
**Dependencies:** Full pipeline (W9–W23); KG API (above).
**Handoff:** TPM reviews at Friday demo.
**Definition of Done:** Fresh upload produces KG concepts; verified via API.

#### AI/ML & Data Pod

##### Objective
Finalize KG-backed retrieval boost design (W25 ships it). Continue concept extraction refinement (filter noise, improve precision). Co-author GPM-1 (top-10 demo beats).

##### Tasks

**Task:** Design the KG-backed retrieval boost (W25 ships it): plan the prerequisite-aware query expansion per Tech Spec Section 13.3. When a student asks about "Principal Component Analysis", query the KG for prerequisites (Linear Algebra, Variance, Eigenvalues, Covariance), expand the retrieval to include chunks related to these prerequisite concepts. Plan the integration with `RetrievalService.retrieve`. Plan the Adaptive Engine integration (when mastery of prereqs is strong, skip expansion; when weak, expand broadly — but Adaptive Engine isn't ready until W31, so v0.6 just expands always).
**Why:** Roadmap W25 sprint requires "KG-backed retrieval boost; Use concept matches to reweight retrieval; Eval set faithfulness ↑ ≥ 5%." Tech Spec Section 13.3 specifies prerequisite-aware query expansion.
**Expected Output:** `docs/plans/kg-retrieval-boost.md` design doc.
**Dependencies:** KG populated (W23); retrieval service (W14).
**Handoff:** Pod B-Lead implements in W25.
**Definition of Done:** Design doc reviewed; ready for W25 implementation.

**Task:** Refine concept extraction quality: review the 200+ concepts from W23. Filter noise (low-confidence concepts, generic terms like "the", "and"). Improve precision by adding a post-extraction filtering step (LLM-based: "Is this a meaningful educational concept? yes/no"). Re-run extraction on the 5 sample docs with the improved pipeline.
**Why:** R-04 (KG noisy/incorrect relations, score 9) mitigation requires quality filtering. Tech Spec Section 13.1 mentions post-extraction filtering as a fallback.
**Expected Output:** Updated extraction pipeline with filtering; re-populated KG (cleaner); before/after quality report.
**Dependencies:** Concept extraction pipeline (W23); KG populated (W23).
**Handoff:** Pod D re-runs KG sanity tests (TM-7) on the cleaner KG.
**Definition of Done:** Noisy concepts filtered; precision improved (manual sample shows > 80% meaningful concepts); KG re-populated.

**Task:** Co-author GPM-1 (top-10 demo beats) with TPM: from the demo backlog (GPM-0, W20), select the top 10 moments that would make the best demo beats. Prioritize: upload → OCR (visual), chat with citations (clear value), KG visualization (impressive), quiz → mastery update (cognitive model visible), adaptive recommendation (intelligence). Commit to `docs/graduation/demo-beats-top-10.md`.
**Why:** Roadmap GPM-1 (W24) requires "Demo backlog reviewed; top-10 beats selected."
**Expected Output:** Top-10 demo beats doc.
**Dependencies:** Demo backlog (W20); all P0–P3 work.
**Handoff:** TPM + advisor review; informs the demo script (GPM-3 at W30).
**Definition of Done:** 10 beats selected; TPM + advisor sign off.

#### Frontend Pod

##### Objective
Ship the KG viz UI (full integration with KG API). Build the KG page at `/kg` showing the interactive concept graph. Demo dataset visible in UI.

##### Tasks

**Task:** Ship the KG viz UI: integrate `KGGraph.tsx` (W21 skeleton) with the KG API (`/v1/kg/concepts`, `/v1/kg/relations`). Render the interactive graph with Cytoscape.js: nodes color-coded by mastery (placeholder green for now — real mastery in W28), edges styled by type (is-a: solid, prerequisite-of: dashed, part-of: dotted). Zoom, pan, click-to-select a concept (opens concept detail view).
**Why:** Roadmap W24 sprint requires "KG viz UI; interactive concept graph (react-flow or d3); KG browsable; frontend can query KG." Tech Spec Section 20.2 lists KG Visualizer.
**Expected Output:** `frontend/src/app/(student)/kg/page.tsx`; integrated `KGGraph.tsx`; `useConcepts` + `useRelations` TanStack Query hooks.
**Dependencies:** KG API (Pod A W23–W24); KG viz skeleton (W21); Cytoscape.js (W21).
**Handoff:** Pod C-Lead demos in W24 Friday demo.
**Definition of Done:** Graph renders with real data (200+ concepts); zoom/pan/click work; concept detail opens; edge types styled.

**Task:** Build the materials list page showing demo dataset v1: a page at `/courses/demo/materials` listing all 15–30 demo PDFs with their processing status (all should be `kg_ready`). Allow students to browse + select a material to view its KG.
**Why:** DDM-2 (demo dataset) needs a UI surface; supports the W26 v0.6 demo.
**Expected Output:** `frontend/src/app/(student)/courses/demo/materials/page.tsx`.
**Dependencies:** Demo dataset (Pod A W24); materials list API (W7).
**Handoff:** Pod C-Lead demos in W26 (v0.6).
**Definition of Done:** Page lists all demo PDFs; status badges show `kg_ready`; clicking opens the material's KG.

#### DevOps / QA Pod

##### Objective
Sign off TM-7 (KG sanity tests). Verify DDM-2 (demo dataset on staging). Continue monitoring + cross-training.

##### Tasks

**Task:** Sign off TM-7: run KG sanity tests on the populated + refined KG. Verify schema validation, cycle detection, orphan detection, duplicate detection all pass. Document in `docs/p3/tm-7-results.md`. If any test fails, escalate to Pod B.
**Why:** Roadmap TM-7 (W24) requires "KG sanity tests; Schema validation; cycle detection."
**Expected Output:** TM-7 results doc; sign-off.
**Dependencies:** KG sanity tests (W23); refined KG (Pod B W24).
**Handoff:** TPM includes in W24 monthly review (Jan 2027: "KG taking shape").
**Definition of Done:** All sanity tests pass; TM-7 signed off.

**Task:** Verify DDM-2: confirm all 15–30 demo PDFs are ingested on staging (OCR + chunks + embeddings + KG). Run smoke tests on each. Document in `docs/p3/ddm-2-verification.md`.
**Why:** Roadmap DDM-2 (W24) requires "Demo dataset v1: all demo PDFs ingested, OCR'd, embedded, in staging."
**Expected Output:** DDM-2 verification doc.
**Dependencies:** Demo dataset ingestion (Pod A W24); staging environment.
**Handoff:** TPM notes; demo data track continues (DDM-3 at W30).
**Definition of Done:** All demo PDFs `kg_ready` on staging; smoke tests pass.

**Task:** Continue on-call rotation + cross-training. Pod B engineer writes a Cypher query that traverses prerequisite chains (e.g., "find all prerequisites of PCA").
**Why:** Roadmap §Pod Cross-Training Plan continues.
**Dependencies:** Populated KG (W23–W24).
**Handoff:** Pod B engineer can independently query Neo4j for debugging by W25.
**Definition of Done:** Pod B engineer writes + runs the prerequisite traversal query.

#### Cross-Pod Integration

- **Backend ↔ Frontend:** KG API + KG viz UI fully integrated. Real data flowing.
- **Backend ↔ AI/ML:** Demo dataset ingestion is joint.
- **AI/ML ↔ TPM:** GPM-1 (top-10 demo beats) co-authored.
- **DevOps/QA ↔ All Pods:** TM-7 sign-off; DDM-2 verification.
- **End-to-end (IM-8):** Upload → OCR → chunks → concept extraction → KG populated; KG browsable in UI.

#### Week 24 Definition of Done

1. KG API finalized; OpenAPI docs complete; integration tests pass.
2. Demo dataset v1 ingested on staging (15–30 PDFs, all `kg_ready`).
3. IM-8 verified: fresh upload populates KG.
4. KG-backed retrieval boost design doc merged.
5. Concept extraction refined (noise filtered, precision > 80%).
6. GPM-1: top-10 demo beats selected; TPM + advisor signed off.
7. KG viz UI shipped (interactive graph with real data, edge types styled, concept detail).
8. Demo materials list page built.
9. TM-7 met: KG sanity tests pass; sign-off.
10. DDM-2 verified: all demo PDFs ingested on staging.
11. On-call W24 complete; Pod B engineer writes prerequisite traversal query.
12. Monthly milestone review (Jan 2027: "KG taking shape") passes.

---

### Week 25 — KG-Backed Retrieval Boost + Cognitive Model Spike Begins

#### Roadmap Context

- **Phase:** P3 Knowledge & Cognition
- **Milestone:** KG-backed retrieval boost; cognitive model research spike begins (W25–W27 spike)
- **Release:** v0.6 prep
- **Primary Objective:** Ship the KG-backed retrieval boost (faithfulness ↑ ≥ 5%). Begin the cognitive model research spike (BKT vs IRT vs rolling average). Note: capacity is starting to drop (university semester is in full swing; exam crunch 1 begins late Jan / W25–W27). Plan is intentionally lighter on parallelism.

#### Backend Pod

##### Objective
Support Pod B's KG-backed retrieval boost. Begin the quiz API design (W26 ships quiz generation; W27 ships mastery estimator). Light capacity week.

##### Tasks

**Task:** Design the quiz API: `/v1/materials/{id}/quizzes` POST (instructor generates a quiz from a material), `/v1/quizzes/{id}` GET (quiz detail + questions), `/v1/quizzes/{id}/submit` POST (student submits answers, returns score + mastery update), `/v1/students/me/mastery` GET (student's mastery per concept). Plan the `quizzes` + `questions` + `quiz_attempts` tables.
**Why:** Roadmap W26 sprint requires "Quiz UI + grading; Take quiz, submit, see score." W27 requires "Mastery estimator v1." W28 requires "Quiz integration end-to-end + mastery UI." Design now lets W26–W28 focus on implementation.
**Expected Output:** `docs/plans/quiz-api-design.md`; table schema drafts.
**Dependencies:** KG schema (W21); Tier 1 Freeze (W20).
**Handoff:** Pod A-Lead implements in W26; Pod C-Lead builds quiz UI in W26.
**Definition of Done:** Design doc reviewed; ready for W26.

**Task:** Light capacity: monitor v0.5 stability; address any P1 bugs; tech debt burn-down. University semester is in full swing; capacity is dropping. Plan intentionally lighter.
**Why:** Roadmap capacity model: Semester 1 (Oct–mid-Jan) = 7 active members, 8 hrs/wk = ~56 effective hrs/wk. W25 is the start of the Jan exam crunch (W25–W27).
**Expected Output:** Bug fixes; tech debt items closed.
**Dependencies:** v0.5 (W20).
**Handoff:** Pod D includes in retro.
**Definition of Done:** No new P1s; tech debt burn-down on track.

#### AI/ML & Data Pod

##### Objective
Ship the KG-backed retrieval boost (faithfulness ↑ ≥ 5%). Begin the cognitive model research spike (W25–W27).

##### Tasks

**Task:** Implement the KG-backed retrieval boost: update `RetrievalService.retrieve` to: (1) extract concepts from the query (via the LLM), (2) query the KG for prerequisite concepts, (3) expand the retrieval to include chunks related to these prerequisites, (4) re-weight the merged results (boost chunks that match both the query concepts + prerequisites). Run RAG eval before/after; verify faithfulness ↑ ≥ 5%.
**Why:** Roadmap W25 sprint requires "KG-backed retrieval boost; Use concept matches to reweight retrieval; Eval set faithfulness ↑ ≥ 5%." Tech Spec Section 13.3 specifies prerequisite-aware query expansion.
**Expected Output:** Updated `RetrievalService`; before/after eval report.
**Dependencies:** KG populated (W23); retrieval service (W14); RAG eval harness (W15).
**Handoff:** Pod A-Lead deploys; Pod C-Lead verifies chat still works.
**Definition of Done:** Faithfulness improves by ≥ 5% on the 50-Q golden set; no regression on relevance.

**Task:** Begin the cognitive model research spike (W25–W27): research BKT (Bayesian Knowledge Tracing, Corbett & Anderson 1995), IRT (Item Response Theory, Wainer et al.), rolling average (simple heuristic). Compare on paper: data requirements, cold-start behavior, computational cost, implementation complexity. Plan a simulated evaluation (10 personas × 20 quizzes each — TM-9 will use this in W33).
**Why:** Roadmap W25 sprint requires "Cognitive model research spike begins; spike on IRT vs Bayesian vs rolling average." Roadmap critical path: "Cognitive model spike (W25–W27) [research]." R-03 (adaptive engine, score 12) + R-13 (cognitive model meaningless mastery, score 9) mitigation.
**Expected Output:** `docs/spikes/cognitive-model-spike.md` (started; W27 concludes with ADR-017).
**Dependencies:** Tech Spec Section 14 (SKM); pyBKT + py-irt libraries.
**Handoff:** Pod B-Lead concludes in W27 with ADR-017 (cognitive model choice).
**Definition of Done:** Spike started; literature review of BKT/IRT/rolling average complete.

**Task:** Begin quiz generation v1 (non-adaptive): plan the LLM prompt for generating MCQs from chunks. Each MCQ has: question text, 4 options, correct answer, explanation, difficulty (easy/medium/hard), concept tags. Plan the `Question` Pydantic schema per Tech Spec Section 21.2 ER diagram.
**Why:** Roadmap W25 sprint requires "Quiz generation v1 (non-adaptive); LLM generates MCQ from chunks; answer key; metadata." Tech Spec Section 7 (Layer 7 — Generation & Simulation) specifies MCQ generation.
**Expected Output:** `docs/plans/quiz-generation-design.md`; draft `Question` schema.
**Dependencies:** LiteLLM gateway (W7); KG (W23 — for concept tagging).
**Handoff:** Pod B-1 implements in W25 (continues in W27).
**Definition of Done:** Design doc merged; schema drafted.

#### Frontend Pod

##### Objective
Begin the quiz UI design (W26 ships it). Light capacity week.

##### Tasks

**Task:** Begin the quiz UI design: plan the quiz-taking interface (question display, option selection, navigation between questions, submit button, score display, mastery update visualization). Plan the quiz creation interface for instructors (select material, number of questions, difficulty). Mock the UI in Storybook.
**Why:** Roadmap W26 sprint requires "Quiz UI + grading; Take quiz, submit, see score." Prep now lets W26 focus on real data.
**Expected Output:** `docs/plans/quiz-ui-design.md`; Storybook mockups.
**Dependencies:** Design tokens (W2); KG viz (W24 — for concept context).
**Handoff:** Pod C-2 implements in W26.
**Definition of Done:** Design doc + Storybook mockups committed.

**Task:** Light capacity: continue KG viz polish (based on W24 demo feedback); fix any visual bugs.
**Why:** Roadmap capacity model; W25 is start of exam crunch.
**Expected Output:** Polish; bug fixes.
**Dependencies:** KG viz (W24).
**Handoff:** Pod D includes in retro.
**Definition of Done:** No P1 frontend bugs; KG viz polished.

#### DevOps / QA Pod

##### Objective
Monitor KG-backed retrieval boost in Grafana. Continue on-call + cross-training. Begin exam crunch comms (PB-05 prep).

##### Tasks

**Task:** Add KG-backed retrieval boost metrics to Grafana: panels for retrieval latency (with KG expansion vs without), faithfulness trend (last 50 queries), prerequisite expansion frequency. Compare to W14 baseline.
**Why:** R-02 (RAG quality) mitigation; verify the boost improves quality without unacceptable latency cost.
**Expected Output:** Updated `infra/grafana/dashboards/retrieval-quality.json`.
**Dependencies:** Retrieval service (Pod B W25); Grafana (W6).
**Handoff:** Pod B-Lead monitors; TPM reviews at monthly review.
**Definition of Done:** Dashboard shows before/after metrics; faithfulness trend visible.

**Task:** Begin exam crunch comms (PB-05 prep): TPM sends "exam mode" communication to the team — capacity is expected to drop to ~12 hrs/wk during W25–W27 (per Roadmap capacity model). Plan is sized to absorb this. Pod leads confirm their pod's capacity. If Pod B throughput < 30% of plan for 2 consecutive weeks, PB-05 triggers.
**Why:** Roadmap PB-05 (R-16, exam crunch, score 16) mitigation requires proactive comms. Roadmap §Operating Assumptions: "We do not assume exam crunches are survivable without planned downtime. W25–W27 and late-April are explicitly low-capacity."
**Expected Output:** Exam mode comms sent; pod capacity confirmed.
**Dependencies:** Roadmap capacity model.
**Handoff:** TPM monitors throughput; triggers PB-05 if metric met.
**Definition of Done:** Comms sent; pod leads acknowledge; capacity tracking active.

**Task:** Continue on-call + cross-training. Pod B engineer continues Neo4j ops shadowing.
**Why:** Roadmap §Pod Cross-Training Plan continues.
**Dependencies:** Neo4j (W22).
**Handoff:** Pod B engineer can independently triage Neo4j by W30.
**Definition of Done:** On-call W25 complete; cross-training logged.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Quiz API design informs quiz generation; KG-backed retrieval boost integrated.
- **AI/ML ↔ DevOps/QA:** Retrieval boost monitoring; exam crunch comms.
- **TPM ↔ All Pods:** Exam mode comms; capacity tracking.
- **End-to-end (IM-9 prep):** KG → RAG retrieval boost; faithfulness improves.

#### Week 25 Definition of Done

1. Quiz API design doc merged.
2. No new P1 backend bugs; tech debt burn-down on track.
3. KG-backed retrieval boost shipped; faithfulness ↑ ≥ 5% on golden set.
4. Cognitive model research spike started (W25–W27).
5. Quiz generation design doc merged; Question schema drafted.
6. Quiz UI design doc + Storybook mockups committed.
7. KG viz polished; no P1 frontend bugs.
8. Retrieval boost metrics in Grafana; before/after visible.
9. Exam mode comms sent; pod capacity confirmed; PB-05 monitoring active.
10. On-call W25 complete; Pod B cross-training continues.

---



### Week 26 — v0.6 Tag + Quiz UI + Cognitive Model Spike Continues

#### Roadmap Context

- **Phase:** P3 Knowledge & Cognition
- **Milestone:** v0.6 tag + small demo (KG + concept browse + first quiz); quiz UI + grading; cognitive model spike continues; GPM-2 (presentation outline v0 — done W22, confirm)
- **Release:** v0.6 (tag `v0.6.0`)
- **Primary Objective:** Ship v0.6 (KG populated, concept browse, first quiz). Continue the cognitive model spike. Note: exam crunch 1 is in full swing (capacity ~12 hrs/wk); plan is intentionally lighter.

#### Backend Pod

##### Objective
Ship the quiz API (W25 design). Implement the quiz CRUD + submission + scoring. Tag v0.6.

##### Tasks

**Task:** Implement the quiz API: `/v1/materials/{id}/quizzes` POST (instructor generates a quiz: select material, number of questions, difficulty), `/v1/quizzes/{id}` GET (quiz detail + questions), `/v1/quizzes/{id}/submit` POST (student submits answers, returns score + per-question results + mastery update), `/v1/students/me/mastery` GET (student's mastery per concept). Add `quizzes` + `questions` + `quiz_attempts` + `quiz_answers` tables per the W25 design.
**Why:** Roadmap W26 sprint requires "Quiz UI + grading; Take quiz, submit, see score." Tech Spec Section 21.2 ER diagram defines `QUIZ_ATTEMPT` + `QUESTION`.
**Expected Output:** Quiz API endpoints; Alembic migrations; tests ≥ 80% coverage.
**Dependencies:** Quiz API design (W25); quiz generation (Pod B W25–W26); auth (W5).
**Handoff:** Pod C-2 wires quiz UI to these endpoints; Pod B-1 implements mastery update on submit (W27).
**Definition of Done:** Instructor can generate a quiz; student can take + submit; score + per-question results returned; tests pass.

**Task:** Tag `v0.6.0` on `main` after Friday demo. Cut a GitHub Release with release notes referencing: KG (200+ concepts, populated from 5+ docs), KG API, KG viz UI, KG-backed retrieval boost, demo dataset v1 (15–30 PDFs), quiz generation v1, quiz API, quiz UI.
**Why:** Roadmap v0.6 milestone (Jan 30, 2027 = W26).
**Expected Output:** Git tag `v0.6.0`; GitHub Release published.
**Dependencies:** All W21–W26 DoD items.
**Handoff:** TPM announces v0.6; P3 continues toward W30 Tier 2 Freeze.
**Definition of Done:** Tag exists; release notes complete; advisor notified.

#### AI/ML & Data Pod

##### Objective
Ship quiz generation v1 (non-adaptive, LLM-generated MCQs with answer keys + metadata). Continue the cognitive model spike (W27 concludes with ADR-017).

##### Tasks

**Task:** Implement quiz generation v1: `app/services/quiz_generation_service.py::generate_quiz(material_id, num_questions, difficulty)` that: (1) selects relevant chunks from the material (using retrieval service to find diverse, informative chunks), (2) for each chunk, calls `ReasoningInterface.generate_questions(chunk_text, params)` via the PAL (LLM prompt: "Generate {num_questions} MCQs at {difficulty} difficulty from this text. Return JSON with question, 4 options, correct_answer, explanation, concept_tags"), (3) parses + validates the structured output, (4) stores questions in the `questions` table linked to the material. Handle LLM JSON parsing failures gracefully (retry once with a stricter prompt).
**Why:** Roadmap W25 sprint started quiz generation; W26 ships it for the v0.6 demo. Tech Spec Section 7 (Layer 7) specifies MCQ generation; Section 13.1 mentions concept_tags.
**Expected Output:** `app/services/quiz_generation_service.py`; `app/workers/tasks/quiz_generation.py` (async); tests verifying 10 MCQs generate from a sample material.
**Dependencies:** LiteLLM gateway (W7); retrieval service (W14); KG (W23 — for concept tagging).
**Handoff:** Pod A-Lead exposes via quiz API (above); Pod C-2 builds quiz UI.
**Definition of Done:** 10 MCQs generate from a demo material in < 30s (NFR-2); answer keys + explanations + concept tags present; tests pass.

**Task:** Continue the cognitive model spike (W25–W27): implement a prototype of each candidate model: (1) rolling average (simple `Mastery = Correct / Total`), (2) weighted moving average (`Mastery = weighted_avg(recent_answers, decay=0.9)`), (3) BKT (using `pyBKT` library, 4 parameters: P(L0), P(T), P(G), P(S)). Run on simulated student data (10 personas × 20 quizzes — prepared in W25). Compare mastery estimates vs ground truth.
**Why:** Roadmap W25–W27 spike requires comparing IRT vs Bayesian vs rolling average. Tech Spec Section 14.2 evolution strategy: heuristic → WMA → BKT.
**Expected Output:** Updated `docs/spikes/cognitive-model-spike.md` with prototype results.
**Dependencies:** Spike start (W25); `pyBKT` + `py-irt` libraries.
**Handoff:** Pod B-Lead concludes in W27 with ADR-017 (cognitive model choice).
**Definition of Done:** All 3 prototypes run on simulated data; mastery estimates compared; recommendation drafted.

#### Frontend Pod

##### Objective
Ship the quiz UI: take quiz, submit, see score. Build the instructor quiz creation page.

##### Tasks

**Task:** Build the quiz-taking UI: `/quizzes/{id}` page showing one question at a time (or all questions on one page — design decision), option selection (radio buttons), navigation between questions, "Submit" button. On submit, POST to `/v1/quizzes/{id}/submit`, display score + per-question results (correct/incorrect, explanation). Use shadcn/ui `RadioGroup`, `Button`, `Card`.
**Why:** Roadmap W26 sprint requires "Quiz UI + grading; Take quiz, submit, see score; Student completes a quiz." Tech Spec Section 20.2 lists Assessment interfaces.
**Expected Output:** `frontend/src/app/(student)/quizzes/[id]/page.tsx`; `frontend/src/features/quiz/components/QuestionCard.tsx`, `QuizResults.tsx`.
**Dependencies:** Quiz API (Pod A W26); design tokens (W2).
**Handoff:** Pod C-2 demos in W26 Friday demo (v0.6).
**Definition of Done:** Student can take a quiz, submit, see score + explanations; works on staging.

**Task:** Build the instructor quiz creation page: `/instructor/materials/{id}/quizzes/new` — form with: number of questions (slider 5–20), difficulty (easy/medium/hard radio), optional concept tags (multi-select from material's KG concepts). On submit, POST to `/v1/materials/{id}/quizzes`. Show generation progress (the LLM call takes ~30s).
**Why:** Instructor flow for v0.6 demo.
**Expected Output:** `frontend/src/app/(instructor)/materials/[id]/quizzes/new/page.tsx`.
**Dependencies:** Quiz API (Pod A W26); quiz generation (Pod B W26).
**Handoff:** Pod C-2 demos in W26 Friday demo.
**Definition of Done:** Instructor can generate a quiz; progress shown; quiz appears in the materials list.

#### DevOps / QA Pod

##### Objective
Monitor quiz generation cost + latency. Continue on-call. Light capacity week (exam crunch).

##### Tasks

**Task:** Monitor quiz generation in Grafana: panels for generation latency (P50/P95), LLM token cost per quiz, error rate (JSON parse failures), question quality (manually sample 10 generated questions per week for factual accuracy). Configure alert: cost > $1 per quiz triggers review (R-06 mitigation).
**Why:** R-06 (LLM cost overruns, score 9) mitigation; NFR-2 (10 MCQ < 30s) compliance.
**Expected Output:** Updated `infra/grafana/dashboards/quiz-generation.json`; alert rule.
**Dependencies:** Quiz generation (Pod B W26); Langfuse (W7).
**Handoff:** Pod B-Lead monitors; Pod D reviews at monthly milestone.
**Definition of Done:** Dashboard renders; alert tested; cost baseline documented.

**Task:** Continue on-call rotation. Light capacity week — only critical issues paged.
**Why:** Roadmap capacity model: exam crunch W25–W27.
**Expected Output:** On-call log.
**Dependencies:** On-call schedule (W20).
**Handoff:** Next on-call engineer (W27).
**Definition of Done:** On-call W26 complete; no unpaged P1 incidents.

#### Cross-Pod Integration

- **Backend ↔ Frontend:** Quiz API + quiz UI integration.
- **Backend ↔ AI/ML:** Quiz API + quiz generation service.
- **AI/ML ↔ DevOps/QA:** Quiz generation cost + quality monitoring.
- **End-to-end (IM-10 prep):** Quiz generation → quiz UI → (W28: mastery update).

#### Week 26 Definition of Done

1. Quiz API shipped (CRUD + submit + scoring); coverage ≥ 80%.
2. v0.6.0 tagged; release notes published.
3. Quiz generation v1 ships: 10 MCQs from a demo material in < 30s.
4. Cognitive model spike continues; 3 prototypes (rolling avg, WMA, BKT) run on simulated data.
5. Quiz-taking UI built; student can complete a quiz.
6. Instructor quiz creation page built.
7. Quiz generation Grafana dashboard live; alert configured.
8. On-call W26 complete; no unpaged P1s.
9. Friday demo (v0.6) passes: KG browse + first quiz.

---

### Week 27 — Cognitive Model Spike Concludes + Mastery Estimator v1

#### Roadmap Context

- **Phase:** P3 Knowledge & Cognition
- **Milestone:** Cognitive model spike concludes → ADR-017; mastery estimator v1; quiz generation v1 (continued); DM-11 (cognitive model design doc)
- **Release:** No tag
- **Primary Objective:** Conclude the cognitive model spike with ADR-017 (choice: BKT vs IRT vs rolling average, per the Tech Spec evolution strategy + roadmap constraint that v1.0 starts with rolling average and adds IRT in v0.8 if data supports). Ship mastery estimator v1. DM-11 (cognitive model design doc). Final week of exam crunch 1.

#### Backend Pod

##### Objective
Implement the mastery schema (Contract 8 draft). Support Pod B's mastery estimator v1.

##### Tasks

**Task:** Implement the mastery schema: `mastery_records` table per Contract 8 (drafted now, frozen at W30): `id UUID PK`, `student_id FK`, `concept_id FK`, `mastery_score FLOAT [0-1]`, `bkt_p_know FLOAT`, `bkt_transit FLOAT`, `bkt_guess FLOAT`, `bkt_slip FLOAT`, `interaction_count INT`, `last_updated TIMESTAMP`, `created_at TIMESTAMP`. Add SQLAlchemy model + Pydantic schema. Plan the `/v1/students/me/mastery` endpoint (already in W26 quiz API; ensure schema alignment).
**Why:** Roadmap W27 sprint requires "Mastery estimator v1; Update mastery from quiz results; store per (student, concept); rolling average." Tier 2 Freeze (W30) freezes Contract 8 (student mastery schema). Tech Spec Section 14.3 specifies BKT 4-parameter model; Tech Spec Section 21.2 ER diagram defines `SKM_RECORD`.
**Expected Output:** Alembic migration; `app/domain/mastery.py`; `app/repositories/mastery_repository.py`.
**Dependencies:** Quiz API (W26); KG concepts (W23).
**Handoff:** Pod B-1 implements mastery estimator (below); Pod A exposes via the mastery endpoint.
**Definition of Done:** Migration runs; model + schema validate; tests pass.

**Task:** Implement the mastery update hook: when a quiz is submitted (`/v1/quizzes/{id}/submit`), call `MasteryService.update_mastery(student_id, concept_ids, quiz_results)`. The service (implemented by Pod B) updates `mastery_records` for each concept tagged in the quiz questions.
**Why:** Tech Spec Section 14.1: "SKM updates the mastery estimate after each student interaction." Tech Spec Section 17 data flow: quiz → SKM_Update.
**Expected Output:** Updated quiz submit endpoint; integration test verifying mastery updates after submit.
**Dependencies:** Mastery schema (above); mastery service (Pod B W27).
**Handoff:** Pod C-2 displays mastery in UI (W28); Pod B-Lead finalizes BKT in W28.
**Definition of Done:** Submitting a quiz updates mastery_records for relevant concepts; test passes.

#### AI/ML & Data Pod

##### Objective
Conclude the cognitive model spike with ADR-017. Ship mastery estimator v1 (rolling average per Roadmap constraint; BKT scaffolded for v0.7+). Co-author DM-11 (cognitive model design doc).

##### Tasks

**Task:** Conclude the cognitive model spike: based on W25–W27 prototype results, draft ADR-017 (cognitive model choice). Per Roadmap constraint + Tech Spec evolution strategy: v1.0 starts with weighted moving average (WMA, the Tech Spec's v0.5.1 stage); BKT is added when sufficient data (≥ 10 interactions per concept per student); IRT is added in v0.8 only if quiz data supports. Mark ADR `Accepted`.
**Why:** Roadmap W27 sprint requires "ADR-017: IRT vs Bayesian vs simple mastery; choice." Roadmap critical path: "Cognitive model spike concludes → ADR (W27)." Roadmap §Structural Descopes #7: "Cognitive model starts as rolling average: IRT is added in v0.8 only if quiz data supports it."
**Expected Output:** `docs/adr/017-cognitive-model.md` (Accepted); `docs/contracts/08-student-mastery-schema.md` (draft).
**Dependencies:** Spike results (W25–W27); Tech Spec Section 14.
**Handoff:** Pod B-1 implements mastery estimator v1 (below); Tier 2 Freeze (W30) freezes Contract 8.
**Definition of Done:** ADR merged; recommendation is WMA v1 + BKT v0.7 + IRT v0.8 (conditional).

**Task:** Implement mastery estimator v1 (WMA): `app/services/mastery_service.py::update_mastery(student_id, concept_ids, quiz_results)` that: (1) loads existing `mastery_records` for the (student, concept) pairs, (2) for each concept, updates mastery using weighted moving average (`Mastery = weighted_avg(recent_answers, decay=0.9)` per Tech Spec Section 14.2 v0.5.1), (3) handles cold-start (no existing record → initialize with `Mastery = Correct / Total` heuristic per Tech Spec v0.5.0), (4) increments `interaction_count`, (5) writes back to `mastery_records`. Scaffold the BKT update method (TODO: implement in W28 with pyBKT).
**Why:** Roadmap W27 sprint requires "Mastery estimator v1; Update mastery from quiz results; store per (student, concept); rolling average." Tech Spec Section 14.2 v0.5.1 WMA.
**Expected Output:** `app/services/mastery_service.py`; unit tests with simulated quiz results.
**Dependencies:** Mastery schema (Pod A W27); ADR-017 (above).
**Handoff:** Pod A-Lead wires to quiz submit endpoint (above); Pod C-2 displays in W28.
**Definition of Done:** Submitting a quiz updates mastery_records; WMA calculation correct; cold-start handled; tests pass.

**Task:** Co-author DM-11 (cognitive model design doc, due W27): `docs/student-model.md` covering: SKM purpose, evolution strategy (heuristic → WMA → BKT), BKT 4-parameter model, IRT for question difficulty, cold-start handling, confidence intervals, sanity checks. Reference Tech Spec Section 14 + ADR-017.
**Why:** Roadmap DM-11 (W27) requires `docs/student-model.md`.
**Expected Output:** `docs/student-model.md` (5+ pages).
**Dependencies:** ADR-017 (above); Tech Spec Section 14.
**Handoff:** TPM publishes; all engineers reference.
**Definition of Done:** Doc merged; reviewed by B-Lead + D-Lead; in Docusaurus.

#### Frontend Pod

##### Objective
Begin the mastery UI (W28 ships full integration). Light capacity week.

##### Tasks

**Task:** Build the mastery UI skeleton: `/dashboard/mastery` page showing a list of concepts the student has been quizzed on, with mastery score (0–1) as a progress bar + numeric value. Color-coded: green (≥ 0.85 mastered), yellow (0.5–0.85 partial), red (< 0.5 weak). Mock data for now.
**Why:** Roadmap W28 sprint requires "Mastery UI; student sees mastery per concept; instructor sees cohort." Tech Spec Section 20.2 lists Profile Management UI with mastery vector.
**Expected Output:** `frontend/src/app/(student)/dashboard/mastery/page.tsx`; `frontend/src/features/mastery/components/MasteryBar.tsx`; Storybook story.
**Dependencies:** Design tokens (W2); KG viz (W24 — for concept context).
**Handoff:** Pod C-2 wires to `/v1/students/me/mastery` endpoint in W28.
**Definition of Done:** Page renders with mock data; color-coding works; progress bars render.

**Task:** Light capacity: continue quiz UI polish; fix any visual bugs from W26 demo.
**Why:** Exam crunch final week.
**Expected Output:** Polish; bug fixes.
**Dependencies:** Quiz UI (W26).
**Handoff:** Pod D includes in retro.
**Definition of Done:** No P1 frontend bugs.

#### DevOps / QA Pod

##### Objective
Light capacity week. Continue on-call. Monitor mastery updates. Begin exam crunch recovery planning (W28 returns to higher capacity).

##### Tasks

**Task:** Monitor mastery updates: add Grafana panels for mastery update latency, mastery_records count, distribution of mastery scores (histogram). Verify mastery updates fire on quiz submit.
**Why:** Sanity check on the new mastery service.
**Expected Output:** Updated Grafana dashboard.
**Dependencies:** Mastery service (Pod B W27); Grafana (W6).
**Handoff:** Pod B-Lead monitors.
**Definition of Done:** Dashboard renders; updates visible on quiz submit.

**Task:** Continue on-call. Plan exam crunch recovery: W28 returns to ~72 hrs/wk effective capacity (Feb break). Pod leads confirm their pod's capacity is recovering. If Pod B throughput < 30% for 2 consecutive weeks (W25 + W26), PB-05 triggers — TPM decides branch (A: pause KG, focus cognitive model; B: defer Tier 2 by 2 weeks; C: descope KG).
**Why:** Roadmap PB-05 (R-16) trigger metric: "Pod B throughput < 30% of plan for 2 consecutive weeks in W25–W27."
**Expected Output:** PB-05 decision doc if triggered; else, recovery plan.
**Dependencies:** Capacity tracking (W25).
**Handoff:** TPM informs team if PB-05 triggers.
**Definition of Done:** PB-05 status documented (triggered or not); recovery plan committed.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Mastery schema + mastery service + quiz submit hook — joint.
- **Backend ↔ Frontend:** Mastery endpoint + mastery UI skeleton.
- **AI/ML ↔ TPM:** ADR-017 (cognitive model choice); DM-11 (design doc).
- **DevOps/QA ↔ All Pods:** Mastery monitoring; PB-05 status.

#### Week 27 Definition of Done

1. Mastery schema (`mastery_records` table) migrated; Contract 8 draft.
2. Mastery update hook fires on quiz submit.
3. ADR-017 (cognitive model) marked `Accepted`; choice is WMA v1 + BKT v0.7 + IRT v0.8 (conditional).
4. Mastery estimator v1 (WMA) implemented; cold-start handled; tests pass.
5. DM-11 (cognitive model design doc, `docs/student-model.md`) merged.
6. Mastery UI skeleton built (mock data).
7. Quiz UI polished; no P1 frontend bugs.
8. Mastery monitoring in Grafana.
9. PB-05 status documented (triggered or not); exam crunch recovery plan committed.
10. Friday demo: take quiz → mastery updates (visible in Grafana + DB).

---

### Week 28 — Quiz Integration E2E + Mastery UI + Cognitive Model Hardening

#### Roadmap Context

- **Phase:** P3 Knowledge & Cognition
- **Milestone:** Quiz integration end-to-end + mastery UI; IM-10 (Quiz generation → Quiz UI → Mastery update); TM-8 (Quiz + mastery E2E test)
- **Release:** v0.7 prep
- **Primary Objective:** Ship the full quiz + mastery loop end-to-end (IM-10). Display mastery in UI (student sees per-concept mastery; instructor sees cohort). Cognitive model hardening (cold-start, confidence intervals, BKT scaffold). Capacity is recovering (Feb break, ~72 hrs/wk effective).

#### Backend Pod

##### Objective
Complete IM-10 integration. Implement the instructor cohort mastery endpoint. Begin BKT implementation with Pod B (for v0.7).

##### Tasks

**Task:** Complete IM-10 integration: verify the full flow — instructor generates quiz → student takes quiz → submits → mastery updates → student sees mastery → instructor sees cohort mastery. Fix any integration bugs. Add the `/v1/instructor/courses/{id}/cohort-mastery` GET endpoint (instructor-only, returns mastery aggregated across enrolled students per concept).
**Why:** Roadmap W28 sprint requires "Quiz integration end-to-end + mastery UI; Quiz assigned → student takes → graded → mastery updated; student sees mastery per concept; instructor sees cohort; E2E test." IM-10 milestone.
**Expected Output:** Bug fixes; cohort mastery endpoint; integration tests.
**Dependencies:** Quiz API (W26); mastery service (W27); quiz UI (W26); mastery UI skeleton (W27).
**Handoff:** Pod D writes TM-8 E2E test; Pod C-2 finalizes mastery UI.
**Definition of Done:** Full flow works on staging; cohort endpoint returns aggregated mastery; tests pass.

**Task:** Begin BKT implementation with Pod B: scaffold `app/services/bkt_service.py` using `pyBKT` library. Implement the 4-parameter model (P(L0), P(T), P(G), P(S)). Plan the upgrade path: when a student has ≥ 10 interactions on a concept, upgrade from WMA to BKT (per ADR-017). Don't activate yet — v0.7 keeps WMA as primary; BKT activates in v0.8 if data supports.
**Why:** Roadmap W28 sprint requires "Cognitive model hardening; cold-start handling; confidence intervals; sanity checks." Tech Spec Section 14.3 specifies BKT. ADR-017 (W27) scaffolds BKT for v0.7+.
**Expected Output:** `app/services/bkt_service.py` scaffold; unit tests with simulated data.
**Dependencies:** ADR-017 (W27); `pyBKT` library; mastery schema (W27).
**Handoff:** Pod B-Lead activates BKT in v0.8 (W34) if quiz data supports (≥ 5 interactions per question for IRT; ≥ 10 per concept for BKT).
**Definition of Done:** BKT scaffold compiles; unit tests pass on simulated data; not yet wired to mastery service (W34 activation).

#### AI/ML & Data Pod

##### Objective
Harden the cognitive model: cold-start handling, confidence intervals, sanity checks. Implement BKT scaffold (with Pod A). Begin adaptive engine research spike prep (W29 starts the spike).

##### Tasks

**Task:** Harden the cognitive model: (1) cold-start: when a new student registers, initialize P(L0) per concept based on their CSP (education level, past test results) per Tech Spec Section 14.3 — advanced student gets higher P(L0). (2) Confidence intervals: compute + store a confidence value alongside mastery (low confidence when interaction_count < 5). (3) Sanity checks: mastery should correlate with quiz performance (if a student gets 90% correct, mastery should be > 0.7); flag anomalies.
**Why:** Roadmap W28 sprint requires "Cognitive model hardening; cold-start handling; confidence intervals; sanity checks." Tech Spec Section 14.3 specifies P(L0) initialization from CSP. R-13 (cognitive model meaningless mastery, score 9) mitigation.
**Expected Output:** Updated `app/services/mastery_service.py` with cold-start + confidence + sanity checks; unit tests.
**Dependencies:** Mastery service (W27); CSP (W6); ADR-017 (W27).
**Handoff:** Pod C-2 displays confidence in UI (low confidence = gray mastery bar).
**Definition of Done:** Cold-start initializes P(L0) from CSP; confidence computed; sanity checks flag anomalies; tests pass.

**Task:** Begin adaptive engine research spike prep (W29 starts the spike, W31 concludes): research candidate approaches — (1) rule-based (if mastery < 0.4, recommend easiest concept; if > 0.7, recommend hardest), (2) priority scoring (mastery deficit + prerequisite readiness + goal alignment + time efficiency per Tech Spec Section 16.2), (3) ML-based (reinforcement learning on simulated trajectories). Plan a simulated evaluation (10 personas × 20 quizzes — same data as cognitive model spike).
**Why:** Roadmap W29 sprint requires "Adaptive engine research spike begins." Roadmap critical path: "Adaptive spike (W29–W31) [research, parallel]." R-03 (adaptive engine, score 12) mitigation.
**Expected Output:** `docs/spikes/adaptive-engine-spike.md` (started; W31 concludes with ADR-018).
**Dependencies:** Tech Spec Section 16; cognitive model (W27).
**Handoff:** Pod B-Lead concludes in W31 with ADR-018.
**Definition of Done:** Spike started; literature review of rule-based / priority scoring / ML approaches complete.

**Task:** Implement the quiz pool with concept + difficulty tags (DDM-4 prep, due W34): generate 100+ quiz questions across the demo PDF set, tag each with concept_id + difficulty (easy/medium/hard). Store in the `questions` table. Plan to use these for the v0.8 adaptive engine + W34 demo quiz pool.
**Why:** Roadmap W29 sprint requires "Quiz bank with concept + difficulty tags ≥ 100 items." Roadmap DDM-4 (W34) requires "Demo quiz pool: 20 quizzes with known-good answers, tagged by concept."
**Expected Output:** 100+ questions in the `questions` table with concept + difficulty tags; generation script.
**Dependencies:** Quiz generation (W26); KG (W23).
**Handoff:** Pod B-Lead uses for v0.8 adaptive engine; Pod D uses for DDM-4 (W34).
**Definition of Done:** 100+ questions tagged; script reproducible.

#### Frontend Pod

##### Objective
Ship the mastery UI (full integration). Build the instructor cohort mastery view.

##### Tasks

**Task:** Ship the mastery UI (full integration): wire `/dashboard/mastery` to `/v1/students/me/mastery`. Display concepts as a list or grid with mastery bars (green/yellow/red color-coded per W27 design). Show confidence indicator (gray bar if low confidence). Show interaction count. Add a "Review concept" button (links to the KG viz for that concept — prepares for adaptive recommendations in W32).
**Why:** Roadmap W28 sprint requires "Mastery UI; student sees mastery per concept." Tech Spec Section 20.2.
**Expected Output:** Final `frontend/src/app/(student)/dashboard/mastery/page.tsx`; `useMastery` TanStack Query hook.
**Dependencies:** Mastery endpoint (W26 quiz API); mastery UI skeleton (W27).
**Handoff:** Pod C-2 demos in W28 Friday demo.
**Definition of Done:** Page renders real mastery data; color-coding + confidence indicator + interaction count work; "Review concept" links to KG.

**Task:** Build the instructor cohort mastery view: `/instructor/courses/{id}/cohort-mastery` page showing aggregated mastery across enrolled students per concept. Display as a table (concept × student, cells color-coded by mastery) or a heatmap (Recharts/Nivo). Filter by concept, by student.
**Why:** Roadmap W28 sprint requires "instructor sees cohort." Tech Spec Section 20.2 lists Analytics Dashboard with mastery heatmap (full version is W34, but cohort mastery is W28).
**Expected Output:** `frontend/src/app/(instructor)/courses/[id]/cohort-mastery/page.tsx`; heatmap component.
**Dependencies:** Cohort mastery endpoint (Pod A W28); Recharts (W2 stack).
**Handoff:** Pod C-2 demos in W28 Friday demo.
**Definition of Done:** Page renders cohort mastery; heatmap works; filters function.

#### DevOps / QA Pod

##### Objective
Write TM-8 E2E test (quiz + mastery). Monitor the full loop. Continue on-call + cross-training.

##### Tasks

**Task:** Implement TM-8: E2E Playwright test covering quiz + mastery — instructor generates quiz → student takes quiz → submits → mastery updates → student sees mastery → instructor sees cohort mastery. Run on staging nightly. Assert mastery_records updated correctly.
**Why:** Roadmap TM-8 (W28) requires "Quiz + mastery E2E test; Student takes quiz, mastery updates, assertion."
**Expected Output:** `frontend/tests/e2e/quiz-mastery.spec.ts`; CI integration.
**Dependencies:** Full quiz + mastery loop (W26–W28).
**Handoff:** Pod D runs nightly; failures wake on-call.
**Definition of Done:** Test passes on staging; runs in < 15 min; CI integration works.

**Task:** Monitor the quiz + mastery loop in Grafana: panels for quiz submission rate, mastery update latency, cohort mastery query latency, error rate. Verify no race conditions in concurrent quiz submissions.
**Why:** R-09 (DB performance) mitigation; concurrent quiz submissions could cause race conditions in mastery updates.
**Expected Output:** Updated Grafana dashboard; concurrency test.
**Dependencies:** Quiz + mastery loop (W28); Grafana (W6).
**Handoff:** Pod A-Lead addresses any race conditions found.
**Definition of Done:** Dashboard renders; concurrency test passes (10 concurrent submissions, no inconsistencies).

**Task:** Continue on-call + cross-training. Pod B engineer begins learning basic CI/CD + Sentry triage (per Roadmap §Pod Cross-Training Plan: "W31–W38: One Pod C engineer learns basic CI/CD and Sentry triage" — but Pod B can start early).
**Why:** Roadmap §Pod Cross-Training Plan; Feature Freeze (W38) requires 3 DevOps-capable people.
**Dependencies:** Sentry (W5); GitHub Actions (W1).
**Handoff:** Pod B engineer continues through W38.
**Definition of Done:** Pod B engineer triages a Sentry error under Pod D supervision.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Mastery schema + BKT scaffold + cognitive model hardening — joint.
- **Backend ↔ Frontend:** Mastery endpoint + mastery UI + cohort mastery endpoint + cohort mastery view.
- **AI/ML ↔ Frontend:** Confidence indicator displayed in UI.
- **End-to-end (IM-10):** Quiz generation → quiz UI → submit → mastery update → mastery UI → cohort mastery view. E2E Playwright test green (TM-8).

#### Week 28 Definition of Done

1. IM-10 verified: full quiz + mastery loop works end-to-end on staging.
2. Cohort mastery endpoint implemented.
3. BKT scaffold implemented (not yet activated).
4. Cognitive model hardened: cold-start, confidence intervals, sanity checks.
5. Adaptive engine spike prep started.
6. 100+ quiz questions generated with concept + difficulty tags.
7. Mastery UI shipped (full integration with backend).
8. Instructor cohort mastery view built (heatmap).
9. TM-8 met: E2E Playwright test passes; runs nightly.
10. Quiz + mastery monitoring in Grafana; concurrency test passes.
11. Pod B engineer begins CI/CD + Sentry triage cross-training.

---

### Week 29 — Cognitive Model Hardening + Adaptive Engine Spike Begins + Mastery UI

#### Roadmap Context

- **Phase:** P3 Knowledge & Cognition (final week of P3 prep before Tier 2 Freeze at W30)
- **Milestone:** Cognitive model hardening + adaptive engine research spike begins + mastery UI + quiz pool
- **Release:** v0.7 prep
- **Primary Objective:** Finalize cognitive model hardening. Begin the adaptive engine spike (W29–W31). Polish mastery UI. Prepare the Tier 2 Architecture Freeze review process (W30 signs it).

#### Backend Pod

##### Objective
Finalize the Tier 2 interface contracts (6–9) with Pod B. Begin the recommendation API design (W32 ships it). Begin the analytics aggregation queries design (W34 ships the dashboard).

##### Tasks

**Task:** Finalize the Tier 2 interface contracts (6–9) with Pod B:
- Contract 6: KG concept/relation schema (node types, edge types, provenance).
- Contract 7: Quiz schema (question types, metadata, scoring).
- Contract 8: Student mastery schema (per student-concept record).
- Contract 9: Adaptive engine I/O (input: student state; output: next action).
Document each with JSON schemas + examples in `docs/contracts/tier-2.md`. Plan the W30 freeze review meeting.
**Why:** Roadmap W30 signs Tier 2 Freeze (Gate 3). All 4 contracts must be documented with examples.
**Expected Output:** `docs/contracts/tier-2.md` (or 4 separate files); freeze review meeting scheduled.
**Dependencies:** KG schema (W21); quiz schema (W26); mastery schema (W27); adaptive I/O (Pod B W29 spike).
**Handoff:** All pod leads + TPM sign at W30 freeze meeting.
**Definition of Done:** All 4 contracts documented; ready for W30 sign-off.

**Task:** Begin the recommendation API design: `/v1/recommendations/today` GET (returns the adaptive engine's recommendation for the student: next concept to study, suggested format, suggested duration, review items due). Plan the response schema per Tech Spec Section 16.2 (concept selection + difficulty calibration + modality selection + scheduling). Plan the integration with the Adaptive Engine service (Pod B W31).
**Why:** Roadmap W32 sprint requires "Recommendation API + UI; `/v1/recommendations`; 'Recommended next' panel." Tech Spec Section 22.3 lists `/recommendations/today`.
**Expected Output:** `docs/plans/recommendation-api-design.md` design doc.
**Dependencies:** Adaptive engine spike (Pod B W29–W31); Tier 2 contracts (above).
**Handoff:** Pod A-Lead implements in W32; Pod C-1 builds recommendation UI.
**Definition of Done:** Design doc reviewed; ready for W32.

**Task:** Begin the analytics aggregation queries design: cohort mastery distribution, quiz pass rates, student engagement (chat messages, quizzes taken, time spent), mastery heatmap data, exam readiness scores. Plan the `/v1/analytics/dashboard` + `/v1/analytics/heatmap` endpoints. Plan the query optimization (indexes, materialized views for expensive aggregations).
**Why:** Roadmap W34 sprint requires "Learning analytics dashboard (backend + UI); Aggregation queries: cohort mastery, quiz pass rates, engagement." Tech Spec Section 22.3 lists `/analytics/dashboard` + `/analytics/heatmap`. NFR-1 (P95 < 2s under 50 users) requires optimized queries.
**Expected Output:** `docs/plans/analytics-queries-design.md` design doc.
**Dependencies:** Mastery records (W27); quiz attempts (W26); cohort mastery (W28).
**Handoff:** Pod A-Lead implements in W34; Pod C-Lead builds dashboard UI.
**Definition of Done:** Design doc reviewed; query optimization plan clear.

#### AI/ML & Data Pod

##### Objective
Run the adaptive engine spike (W29–W31). Finalize cognitive model hardening. Continue quiz pool generation (target 100+ by W34).

##### Tasks

**Task:** Run the adaptive engine spike per `docs/spikes/adaptive-engine-spike.md`: implement prototypes of (1) rule-based (if mastery < 0.4, recommend easiest concept with prereqs met; if > 0.7, recommend hardest), (2) priority scoring (mastery deficit + prerequisite readiness + goal alignment + time efficiency per Tech Spec Section 16.2), (3) ML-based (simple policy gradient on simulated trajectories). Run on the simulated student data (10 personas × 20 quizzes from W25). Measure: does the policy improve learning (mastery gain over 20 quizzes) vs random selection?
**Why:** Roadmap W29 sprint requires "Adaptive engine research spike begins." Roadmap critical path: "Adaptive spike (W29–W31) [research, parallel]." R-03 (adaptive engine, score 12) mitigation. Tech Spec Section 16 specifies the 4-step decision process.
**Expected Output:** Updated `docs/spikes/adaptive-engine-spike.md` with prototype results.
**Dependencies:** Cognitive model (W27); simulated student data (W25).
**Handoff:** Pod B-Lead concludes in W31 with ADR-018.
**Definition of Done:** 3 prototypes run; priority scoring typically wins (per Tech Spec Section 16.2); recommendation drafted.

**Task:** Finalize cognitive model hardening: ensure cold-start, confidence intervals, and sanity checks are robust. Add a "mastery drift" detector (if mastery drops > 0.2 in a week, flag for review — may indicate forgetting or noisy data). Document the final behavior in `docs/student-model.md` (DM-11, due W27 — update with hardening details).
**Why:** Roadmap W28–W29 sprint requires cognitive model hardening. R-13 mitigation.
**Expected Output:** Updated `docs/student-model.md`; drift detector.
**Dependencies:** Mastery service (W27); cognitive model hardening (W28).
**Handoff:** Pod B-Lead references in ADR-018 (adaptive engine).
**Definition of Done:** Hardening finalized; drift detector tested; doc updated.

**Task:** Continue quiz pool generation: target 100+ questions by W34 (DDM-4). Generate questions across the demo PDF set, tag with concept + difficulty. Verify question quality (manual sample of 10 questions per week for factual accuracy).
**Why:** Roadmap W29 sprint requires "Quiz bank with concept + difficulty tags ≥ 100 items." DDM-4 (W34).
**Expected Output:** 50+ additional questions (building toward 100+ by W34); quality report.
**Dependencies:** Quiz generation (W26); KG (W23).
**Handoff:** Pod D uses for DDM-4 (W34); Pod B-Lead uses for v0.8 adaptive.
**Definition of Done:** 50+ questions added; quality > 80% (manual sample).

#### Frontend Pod

##### Objective
Polish the mastery UI. Begin the recommendation UI skeleton (W32 ships it). Begin the analytics dashboard skeleton (W34 ships it).

##### Tasks

**Task:** Polish the mastery UI: based on W28 demo feedback, improve the visual design. Add a "Mastery over time" trend chart (Recharts line chart showing mastery per concept over the last 30 days — placeholder data for now, real data in W34). Add filters (by concept, by mastery level).
**Why:** Tech Spec Section 20.2 lists Analytics Dashboard; mastery trend supports the v0.7 demo + W34 analytics.
**Expected Output:** Updated mastery UI with trend chart + filters.
**Dependencies:** Mastery UI (W28); Recharts (W2 stack).
**Handoff:** Pod C-2 demos in W29 Friday demo.
**Definition of Done:** Trend chart renders; filters work; UI polished.

**Task:** Begin the recommendation UI skeleton: `/dashboard` page with a "Recommended next" panel showing a placeholder recommendation (mock data). Plan the integration with `/v1/recommendations/today` (W32). Plan the "Review schedule" panel showing due review items (SM-2 algorithm — Pod B W31).
**Why:** Roadmap W32 sprint requires "Recommendation UI; 'Recommended next' panel." Tech Spec Section 20.2 lists Profile Management UI.
**Expected Output:** `frontend/src/app/(student)/dashboard/page.tsx` skeleton; `frontend/src/features/recommendations/components/RecommendationPanel.tsx` (mock).
**Dependencies:** Design tokens (W2); mastery UI (W28).
**Handoff:** Pod C-1 wires to recommendation API in W32.
**Definition of Done:** Dashboard page renders with placeholder recommendation; layout clean.

#### DevOps / QA Pod

##### Objective
Begin the Tier 2 Freeze review process. Continue on-call + cross-training. Monitor the cognitive model + adaptive spike.

##### Tasks

**Task:** Begin the Tier 2 Architecture Freeze review process: circulate the 4 Tier 2 contracts (Pod A W29) + ADR-017 (cognitive model). Schedule the W30 freeze review meeting. Prepare the sign-off doc `docs/gates/gate-3-tier-2-freeze.md`.
**Why:** Roadmap W30 signs Tier 2 Freeze (Gate 3). Review process starts W29.
**Expected Output:** Review schedule; sign-off doc draft.
**Dependencies:** Tier 2 contracts (Pod A W29); ADR-017 (W27).
**Handoff:** TPM runs the W30 freeze review meeting; all pod leads + TPM sign.
**Definition of Done:** Review meeting scheduled; sign-off doc drafted; all pod leads have reviewed the contracts.

**Task:** Continue on-call + cross-training. Pod C engineer begins CI/CD + Sentry triage cross-training (per Roadmap §Pod Cross-Training Plan: "W31–W38: One Pod C engineer learns basic CI/CD and Sentry triage" — start early in W29).
**Why:** Roadmap §Pod Cross-Training Plan; Feature Freeze (W38) requires 3 DevOps-capable people.
**Dependencies:** Sentry (W5); GitHub Actions (W1).
**Handoff:** Pod C engineer continues through W38.
**Definition of Done:** Pod C engineer triages a Sentry error + reads a CI log under Pod D supervision.

**Task:** Monitor the cognitive model + adaptive spike: ensure the spike doesn't break production (it should be on a separate branch / feature flag). Add Grafana panels for mastery service health (update latency, error rate, drift detector flags).
**Why:** Spike work shouldn't break v0.6 stability.
**Expected Output:** Updated Grafana dashboard; spike isolated.
**Dependencies:** Mastery service (W27); Grafana (W6).
**Handoff:** Pod B-Lead monitors spike impact.
**Definition of Done:** Dashboard renders; spike isolated from production.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Tier 2 contracts (6–9) co-authored; recommendation API design informs adaptive engine.
- **Backend ↔ Frontend:** Recommendation API design informs recommendation UI skeleton.
- **AI/ML ↔ DevOps/QA:** Adaptive spike monitoring; cognitive model hardening verified.
- **TPM ↔ All Pods:** Tier 2 Freeze review process begins.

#### Week 29 Definition of Done

1. Tier 2 interface contracts (6–9) documented with examples.
2. Recommendation API design doc merged.
3. Analytics aggregation queries design doc merged.
4. Adaptive engine spike running; 3 prototypes tested.
5. Cognitive model hardening finalized; drift detector added; `docs/student-model.md` updated.
6. 50+ additional quiz questions generated (building toward 100+ by W34).
7. Mastery UI polished (trend chart + filters).
8. Recommendation UI skeleton built (mock data).
9. Tier 2 Freeze review meeting scheduled; sign-off doc drafted.
10. Pod C engineer begins CI/CD + Sentry triage cross-training.

---

### Week 30 — v0.7 + Tier 2 Architecture Freeze (GATE 3)

#### Roadmap Context

- **Phase:** P3 Knowledge & Cognition (final week)
- **Milestone:** **v0.7 + Tier 2 Architecture Freeze (GATE 3)**; demo: quiz + mastery + KG end-to-end; DDM-3 (5 demo student accounts with seeded mastery); GPM-3 (demo script skeleton)
- **Release:** v0.7 (tag `v0.7.0`)
- **Primary Objective:** Ship v0.7 (quiz + mastery + KG end-to-end). Sign the Tier 2 Architecture Freeze (Contract 6–9 frozen). Create 5 demo student accounts with seeded mastery states (DDM-3). Begin the demo script skeleton (GPM-3).

#### Backend Pod

##### Objective
Ship v0.7. Sign Tier 2 Freeze. Support DDM-3 (demo student accounts). Begin P4 prep.

##### Tasks

**Task:** Verify v0.7 demo flow end-to-end on staging: instructor creates course + uploads PDF → KG populated → instructor generates quiz → student takes quiz → mastery updates → student sees mastery + KG → instructor sees cohort mastery. Fix any last-minute bugs.
**Why:** Roadmap v0.7 milestone (Feb 27, 2027 = W30) — Gate 3. Demo: quiz + mastery + KG end-to-end.
**Expected Output:** Demo script; bug fixes.
**Dependencies:** All W21–W29 work.
**Handoff:** TPM runs the W30 Friday demo (advisor invited).
**Definition of Done:** Demo passes on staging; advisor demoed.

**Task:** Sign the Tier 2 Architecture Freeze: all pod leads + TPM sign `docs/gates/gate-3-tier-2-freeze.md`. Contracts 6–9 are now frozen. Post-freeze changes require a new ADR + migration + TPM approval + 2 pod leads' review.
**Why:** Roadmap Gate 3 sign-off. Tier 2 Freeze.
**Expected Output:** Signed sign-off doc; contracts 6–9 marked frozen.
**Dependencies:** Sign-off doc (Pod D W29); all Gate 3 criteria met.
**Handoff:** TPM announces Tier 2 Freeze; P4 starts W31 with frozen interfaces.
**Definition of Done:** All pod leads + TPM sign; contracts 6–9 frozen; post-freeze change protocol active.

**Task:** Support DDM-3 (demo student accounts): create 5 demo student accounts with seeded mastery states — (1) novice (low mastery across all concepts), (2) intermediate (mixed mastery), (3) advanced (high mastery), (4) struggling (low mastery on specific concepts), (5) recovering (mastery improving over time). Write a seeding script `scripts/seed_demo_students.py` that creates the accounts + inserts mastery_records for each. Verify on staging.
**Why:** Roadmap DDM-3 (W30) requires "5 demo student accounts created with seeded mastery states." Used for v0.8+ adaptive engine demo + graduation demo.
**Expected Output:** Seeding script; 5 demo accounts on staging.
**Dependencies:** Mastery schema (W27); demo dataset (W24).
**Handoff:** Pod D verifies; TPM notes for graduation prep.
**Definition of Done:** 5 accounts created with realistic mastery states; seeding script reproducible.

**Task:** Tag `v0.7.0` on `main` after Friday demo + Tier 2 Freeze sign-off. Cut a GitHub Release with release notes referencing: KG (200+ concepts, KG API, KG viz, KG-backed retrieval boost), cognitive model (WMA v1, mastery UI, cohort mastery), quiz generation v1, quiz API + UI, 5 demo student accounts, ADR-017, 4 Tier 2 frozen contracts.
**Why:** Roadmap v0.7 milestone — Gate 3.
**Expected Output:** Git tag `v0.7.0`; GitHub Release published.
**Dependencies:** All W21–W30 DoD items + Gate 3 sign-off.
**Handoff:** TPM announces v0.7; P4 (Adaptation & Analytics) starts W31.
**Definition of Done:** Tag exists; release notes complete; advisor notified.

#### AI/ML & Data Pod

##### Objective
Finalize ADR-018 (adaptive engine choice) draft. Continue the adaptive spike (concludes W31). Co-author GPM-3 (demo script skeleton).

##### Tasks

**Task:** Draft ADR-018 (adaptive engine choice) based on W29 spike results: priority scoring (mastery deficit + prerequisite readiness + goal alignment + time efficiency) as the v1.0 policy, with rule-based as fallback (F-7). Plan the productionization (W31). Mark `Proposed`; target `Accepted` W31.
**Why:** Roadmap W31 sprint requires "Adaptive engine productionization + spike concludes → ADR; ADR-018: next-best-concept policy; difficulty adjustment rule; productionization of spike prototype." Tier 2 Freeze (W30) freezes Contract 9 (adaptive engine I/O) — the I/O is frozen, not the algorithm.
**Expected Output:** `docs/adr/018-adaptive-engine.md` (Proposed); `docs/contracts/09-adaptive-engine-io.md` (draft, frozen this week).
**Dependencies:** Adaptive spike (W29–W30); Tech Spec Section 16.
**Handoff:** Pod B-Lead finalizes + productionizes in W31; Contract 9 frozen at W30.
**Definition of Done:** ADR opened; Contract 9 draft published.

**Task:** Continue the adaptive spike (W29–W31): refine the priority scoring prototype. Add the difficulty adjustment rule (per Tech Spec Section 16.5: CAT simulator starts at medium difficulty, adjusts based on performance — but full CAT is v0.8; for v0.7, just the priority scoring is implemented). Run on more simulated data. Verify the policy improves learning vs random.
**Why:** Roadmap W29–W31 spike; R-03 mitigation.
**Expected Output:** Updated spike doc; refined prototype.
**Dependencies:** Spike start (W29); simulated data (W25).
**Handoff:** Pod B-Lead concludes in W31 with ADR-018.
**Definition of Done:** Priority scoring prototype improves learning on simulated data; ready for W31 productionization.

**Task:** Co-author GPM-3 (demo script skeleton) with TPM: draft the demo script — what to click, what to say, for each of the top-10 demo beats (GPM-1, W24). Reference the graduation outline (GPM-2, W22). Plan the 8-minute live demo section.
**Why:** Roadmap GPM-3 (W30) requires "Demo script skeleton (what to click, what to say)."
**Expected Output:** `docs/graduation/demo-script-skeleton.md`.
**Dependencies:** Top-10 demo beats (W24); graduation outline (W22).
**Handoff:** TPM fills in details in W34 (GPM-5: demo script v1).
**Definition of Done:** Skeleton committed; 8-minute demo flow outlined.

#### Frontend Pod

##### Objective
Finalize the v0.7 demo UI. Begin P4 UI prep: adaptive recommendation UI design (W32 ships it).

##### Tasks

**Task:** Finalize the v0.7 demo UI: ensure the full flow (KG browse → quiz → mastery → cohort mastery) is polished. Record a 5-min demo video. Commit to `docs/demo-videos/v0.7.mp4`.
**Why:** v0.7 is the Gate 3 demo to the advisor.
**Expected Output:** Polished UI; demo video.
**Dependencies:** All W21–W29 work.
**Handoff:** TPM uses the video if the live demo fails.
**Definition of Done:** Demo video recorded; UI polished.

**Task:** Begin the adaptive recommendation UI design: plan the "Recommended next" panel (concept name, rationale, suggested duration, suggested format, "Start studying" button). Plan the "Review schedule" panel (due review items per SM-2). Plan the difficulty adjustment visualization (quiz difficulty badge that changes based on mastery). Plan the dashboard layout.
**Why:** Roadmap W32 sprint requires "Recommendation UI; 'Recommended next' panel." Tech Spec Section 20.2.
**Expected Output:** `docs/plans/recommendation-ui-design.md`; Storybook mockups.
**Dependencies:** Recommendation UI skeleton (W29); design tokens (W2).
**Handoff:** Pod C-1 implements in W32.
**Definition of Done:** Design doc merged; mockups committed.

#### DevOps / QA Pod

##### Objective
Finalize Tier 2 Freeze sign-off. Run v0.7 release validation. Verify DDM-3.

##### Tasks

**Task:** Finalize the Tier 2 Architecture Freeze sign-off doc `docs/gates/gate-3-tier-2-freeze.md`: list all Gate 3 sign-off criteria (per Roadmap): v0.7 demoed, ADR-017 merged, Tier 2 contracts documented with examples, KG populated with ≥ 200 concepts, KG sanity tests pass (TM-7), Quiz + mastery E2E test green (TM-8), all pod leads + TPM sign. Circulate for signature.
**Why:** Roadmap W30 signs Tier 2 Freeze (Gate 3).
**Expected Output:** Final sign-off doc.
**Dependencies:** All W21–W30 work.
**Handoff:** All pod leads + TPM sign at W30 freeze meeting.
**Definition of Done:** Doc finalized; all criteria met; signed.

**Task:** Run the v0.7 release validation: full E2E test on staging; smoke tests; verify all Gate 3 criteria. Document in `docs/releases/v0.7-validation.md`.
**Why:** Gate 3 sign-off requires validation.
**Expected Output:** Validation report.
**Dependencies:** All W21–W30 work.
**Handoff:** TPM includes in Gate 3 sign-off; advisor notified.
**Definition of Done:** All criteria verified; report committed.

**Task:** Verify DDM-3: confirm the 5 demo student accounts are created with seeded mastery states on staging. Run smoke tests on each account (login, view mastery, take a quiz, verify mastery updates from the seeded baseline). Document in `docs/p3/ddm-3-verification.md`.
**Why:** Roadmap DDM-3 (W30) verification.
**Expected Output:** DDM-3 verification doc.
**Dependencies:** Demo student accounts (Pod A W30); staging environment.
**Handoff:** TPM notes; demo data track continues (DDM-4 at W34).
**Definition of Done:** 5 accounts functional; seeded mastery visible; smoke tests pass.

#### Cross-Pod Integration

- **All Pods:** v0.7 + Tier 2 Freeze sign-off. All Gate 3 criteria verified.
- **TPM ↔ All Pods:** Tier 2 Freeze signed; v0.7 tagged; GPM-3 (demo script skeleton) co-authored.
- **DevOps/QA ↔ All Pods:** Gate 3 sign-off; release validation; DDM-3 verification.
- **End-to-end (v0.7):** Quiz + mastery + KG end-to-end on staging public URL; advisor demoed.

#### Week 30 Definition of Done

1. **v0.7.0 tagged; Gate 3 (Tier 2 Architecture Freeze) signed by all pod leads + TPM.**
2. v0.7 demo to advisor passes on staging public URL.
3. All 4 Tier 2 interface contracts frozen (Contracts 6–9).
4. ADR-017 (cognitive model) merged; ADR-018 (adaptive engine) drafted.
5. 5 demo student accounts created with seeded mastery states (DDM-3).
6. GPM-3: demo script skeleton committed.
7. v0.7 demo video recorded.
8. Recommendation UI design doc merged (prep for W32).
9. v0.7 release validation report committed; all Gate 3 criteria verified.
10. DDM-3 verified: 5 demo accounts functional on staging.
11. Friday demo (v0.7) passes; advisor in attendance.
12. P4 (Adaptation & Analytics) starts W31 with frozen interfaces + 2 weeks of critical-path slack remaining in this segment.

---



### Week 31 — Adaptive Engine Productionization + ADR-018

#### Roadmap Context

- **Phase:** P4 Adaptation & Analytics
- **Milestone:** Adaptive engine productionization + spike concludes → ADR-018; DM-12 (adaptive engine design doc)
- **Release:** v0.8 prep
- **Primary Objective:** Productionize the adaptive engine based on the W29–W31 spike. Ship ADR-018. Co-author DM-12 (adaptive engine design doc). Capacity is recovering (Feb break, ~72 hrs/wk effective).

#### Backend Pod

##### Objective
Implement the recommendation API (W32 ships the UI). Begin the admin API design (W35 ships admin dashboard).

##### Tasks

**Task:** Implement the recommendation API: `/v1/recommendations/today` GET (returns the adaptive engine's recommendation for the authenticated student: next concept to study, rationale, suggested duration, suggested format, review items due). Calls `AdaptiveEngineService.recommend(student_id)` which fuses SKM + CSP + KG per Tech Spec Section 16. RBAC enforced (student-only). Caching: cache for 5 minutes per student (Redis) to avoid recomputing on every page load.
**Why:** Roadmap W32 sprint requires "Recommendation API + UI; `/v1/recommendations`; 'Recommended next' panel." Tech Spec Section 22.3 lists `/recommendations/today`. NFR-1 (P95 < 2s) requires caching.
**Expected Output:** `app/api/v1/recommendations.py::get_today`; `app/services/recommendation_service.py`; tests.
**Dependencies:** Adaptive engine (Pod B W31); mastery service (W27); KG (W23); Redis (W5).
**Handoff:** Pod C-1 wires recommendation UI to this endpoint in W32.
**Definition of Done:** Endpoint returns a recommendation in < 500ms (cached) / < 2s (uncached); RBAC enforced; tests pass.

**Task:** Implement the review schedule endpoint: `/v1/reviews/scheduled` GET (returns review items due today + upcoming, per SM-2 algorithm). Plan the `review_items` table per Tech Spec Section 21.2 ER diagram.
**Why:** Tech Spec Section 22.3 lists `/reviews/scheduled`. Section 16.4 specifies SM-2 algorithm.
**Expected Output:** `app/api/v1/reviews.py::scheduled`; `review_items` table migration; `app/services/review_service.py` (SM-2 implementation).
**Dependencies:** Mastery records (W27); SM-2 algorithm (Pod B W31).
**Handoff:** Pod C-1 displays in the recommendation UI; Pod B-1 implements SM-2.
**Definition of Done:** Endpoint returns due review items; SM-2 scheduling correct; tests pass.

**Task:** Begin the admin API design: `/v1/admin/users` (list, filter, deactivate), `/v1/admin/courses` (list, audit), `/v1/admin/system-health` (DB connections, queue depth, error rate, uptime). Plan RBAC (admin-only). Plan the audit log (CLI tool only per OOS-9).
**Why:** Roadmap W35 sprint requires "Admin dashboard (minimal); User/course management, system health." Tech Spec Section 22.2 mentions Admin role.
**Expected Output:** `docs/plans/admin-api-design.md` design doc.
**Dependencies:** Auth (W5); RBAC (W6).
**Handoff:** Pod A-2 implements in W35; Pod C-2 builds admin dashboard UI.
**Definition of Done:** Design doc reviewed; ready for W35.

#### AI/ML & Data Pod

##### Objective
Productionize the adaptive engine based on the W29–W31 spike. Ship ADR-018. Co-author DM-12 (adaptive engine design doc). Implement SM-2 spaced repetition.

##### Tasks

**Task:** Productionize the adaptive engine: implement `app/services/adaptive_engine_service.py::recommend(student_id)` per ADR-018 (priority scoring). The 4-step decision process per Tech Spec Section 16.2: (1) Candidate Generation (concepts where mastery < 0.85), (2) Prerequisite Check (KG query for prereqs; deprioritize concepts whose prereqs are unmet), (3) Priority Scoring (mastery deficit + prerequisite readiness + goal alignment + time efficiency), (4) Recommendation Production (top-scored concept + rationale + suggested duration + suggested format from CSP). Include the rule-based fallback (F-7) if priority scoring fails.
**Why:** Roadmap W31 sprint requires "Adaptive engine productionization + spike concludes → ADR; ADR-018: next-best-concept policy; difficulty adjustment rule; productionization of spike prototype." Tech Spec Section 16 specifies the 4-step process. R-03 (adaptive engine, score 12) mitigation.
**Expected Output:** `app/services/adaptive_engine_service.py`; unit tests with simulated student states; integration test verifying a recommendation.
**Dependencies:** Adaptive spike (W29–W31); ADR-018 (below); mastery service (W27); KG (W23); CSP (W6).
**Handoff:** Pod A-Lead exposes via recommendation API (above); Pod C-1 builds UI in W32.
**Definition of Done:** Engine returns a recommendation for any student state; rule-based fallback works; tests pass.

**Task:** Finalize ADR-018 (adaptive engine choice): mark `Accepted`. Document the priority scoring formula, the rule-based fallback (F-7), the difficulty adjustment rule (for v0.8 CAT — simplified: if mastery < 0.4, easier questions; if > 0.7, harder). Reference Tech Spec Section 16.
**Why:** Roadmap W31 sprint requires ADR-018.
**Expected Output:** `docs/adr/018-adaptive-engine.md` (Accepted); `docs/contracts/09-adaptive-engine-io.md` (finalized, frozen at W30).
**Dependencies:** Spike results (W29–W31); Tech Spec Section 16.
**Handoff:** Pod B-Lead productionizes; Contract 9 already frozen at W30.
**Definition of Done:** ADR merged; Contract 9 finalized.

**Task:** Implement SM-2 spaced repetition: `app/services/spaced_repetition_service.py::schedule_review(concept_id, student_id, quality_rating)` per Tech Spec Section 16.4. Each concept has a `review_items` record: `next_review` date, `interval_days`, `ease_factor`. On successful recall (quality ≥ 4), interval × ease_factor (default 2.5); on failure (quality < 3), reset to 1 day, decrease ease by 0.2. Hook into the mastery service: when mastery updates, schedule the next review.
**Why:** Tech Spec Section 16.4 specifies SM-2. Roadmap §Project Scope includes "Adaptive engine (next-best-concept recommendation, difficulty adjustment)" — SM-2 is part of the scheduling optimization output.
**Expected Output:** `app/services/spaced_repetition_service.py`; `review_items` table (already migrated by Pod A W31); unit tests verifying SM-2 logic.
**Dependencies:** Mastery service (W27); `review_items` table (Pod A W31).
**Handoff:** Pod A-Lead exposes via `/v1/reviews/scheduled`; Pod C-1 displays in UI.
**Definition of Done:** SM-2 scheduling correct; review_items updated on mastery change; tests pass.

**Task:** Co-author DM-12 (adaptive engine design doc, due W31): `docs/adaptive.md` covering: 4-step decision process, priority scoring formula, rule-based fallback, SM-2 scheduling, difficulty adjustment, integration with SKM + CSP + KG. Reference Tech Spec Section 16 + ADR-018.
**Why:** Roadmap DM-12 (W31) requires `docs/adaptive.md`.
**Expected Output:** `docs/adaptive.md` (5+ pages).
**Dependencies:** ADR-018 (above); Tech Spec Section 16.
**Handoff:** TPM publishes; all engineers reference.
**Definition of Done:** Doc merged; reviewed by B-Lead + D-Lead; in Docusaurus.

#### Frontend Pod

##### Objective
Begin the recommendation UI (W32 ships full integration). Begin the slide deck template (GPM-4).

##### Tasks

**Task:** Build the recommendation UI (full integration): `/dashboard` page with a "Recommended next" panel showing the next concept (name, rationale, suggested duration, suggested format, "Start studying" button) + "Review schedule" panel (due review items per SM-2). Wire to `/v1/recommendations/today` + `/v1/reviews/scheduled`. Loading + error states.
**Why:** Roadmap W32 sprint requires "Recommendation UI; 'Recommended next' panel." Tech Spec Section 20.2.
**Expected Output:** `frontend/src/app/(student)/dashboard/page.tsx` (full); `frontend/src/features/recommendations/components/RecommendationPanel.tsx`, `ReviewSchedulePanel.tsx`.
**Dependencies:** Recommendation API (Pod A W31); recommendation UI skeleton (W29); review schedule endpoint (Pod A W31).
**Handoff:** Pod C-1 demos in W32 Friday demo (IM-11).
**Definition of Done:** Dashboard renders real recommendation + review schedule; loading/error states work.

**Task:** Begin the slide deck template (GPM-4 is W32, but prep starts W31): choose the slide template (e.g., reveal.js, Slidev, or PowerPoint template). Match the app design tokens. Draft the first 5 slides (title, problem, solution, architecture overview, demo intro). Reference the graduation outline (GPM-2).
**Why:** Roadmap GPM-4 (W32) requires "Slide template chosen; first 5 slides drafted."
**Expected Output:** Slide deck template + first 5 slides.
**Dependencies:** Graduation outline (W22); design tokens (W2).
**Handoff:** TPM reviews; continues in W36 (GPM-6: full deck v1).
**Definition of Done:** Template chosen; 5 slides drafted.

#### DevOps / QA Pod

##### Objective
Monitor the adaptive engine + recommendation API. Continue on-call + cross-training. Begin the adaptation eval harness prep (TM-9 is W33).

##### Tasks

**Task:** Monitor the adaptive engine + recommendation API: add Grafana panels for recommendation latency (P50/P95), cache hit rate, adaptive engine error rate, review schedule query latency. Configure alert: recommendation latency P95 > 2s triggers review.
**Why:** NFR-1 (P95 < 2s under 50 users) compliance; R-03 mitigation.
**Expected Output:** `infra/grafana/dashboards/adaptive-engine.json`; alert rule.
**Dependencies:** Recommendation API (Pod A W31); Grafana (W6).
**Handoff:** Pod B-Lead monitors; Pod A-Lead addresses bottlenecks.
**Definition of Done:** Dashboard renders; alert tested.

**Task:** Begin the adaptation eval harness prep (TM-9 is W33): plan the simulated student trajectories (10 personas × 20 quizzes each — same data as cognitive model spike). Plan the metrics: does the adaptive policy improve learning (mastery gain over 20 quizzes) vs random selection? Plan the regression baseline (v0.8 metrics for comparison in v0.9+).
**Why:** Roadmap TM-9 (W33) requires "Adaptation eval harness; Simulated trajectories; regression baseline." R-03 mitigation requires measurable evaluation.
**Expected Output:** `docs/plans/adaptation-eval-harness.md` design doc.
**Dependencies:** Adaptive engine (Pod B W31); simulated data (W25).
**Handoff:** Pod B-1 implements the harness in W33.
**Definition of Done:** Design doc merged; ready for W33 implementation.

**Task:** Continue on-call + cross-training. Pod C engineer continues CI/CD + Sentry triage. Pod B engineer continues vector DB ops (Qdrant + Neo4j).
**Why:** Roadmap §Pod Cross-Training Plan continues.
**Dependencies:** Sentry (W5); Qdrant (W12); Neo4j (W22).
**Handoff:** Pod C engineer can independently triage CI failures by W38.
**Definition of Done:** Cross-training logged; progress toward 3 DevOps-capable people by W38.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Recommendation API + adaptive engine + review schedule — joint.
- **Backend ↔ Frontend:** Recommendation API + recommendation UI integration.
- **AI/ML ↔ DevOps/QA:** Adaptive engine monitoring; adaptation eval harness prep.
- **TPM ↔ All Pods:** ADR-018; DM-12; GPM-4 (slide deck template).

#### Week 31 Definition of Done

1. Recommendation API (`/v1/recommendations/today`) implemented with caching.
2. Review schedule endpoint (`/v1/reviews/scheduled`) implemented; SM-2 algorithm works.
3. Admin API design doc merged (prep for W35).
4. Adaptive engine productionized: priority scoring + rule-based fallback (F-7).
5. ADR-018 (adaptive engine) marked `Accepted`; Contract 9 finalized.
6. SM-2 spaced repetition implemented.
7. DM-12 (adaptive engine design doc, `docs/adaptive.md`) merged.
8. Recommendation UI built (full integration with backend).
9. Slide deck template chosen; first 5 slides drafted (GPM-4).
10. Adaptive engine Grafana dashboard + alert configured.
11. Adaptation eval harness design doc merged (prep for W33).
12. On-call W31 complete; cross-training continues.

---

### Week 32 — Recommendation API + UI + Difficulty Adjustment

#### Roadmap Context

- **Phase:** P4 Adaptation & Analytics
- **Milestone:** Recommendation API + UI + difficulty adjustment; IM-11 (Mastery → Adaptive engine → Recommendation UI); GPM-4 (slide template + first 5 slides)
- **Release:** v0.8 prep
- **Primary Objective:** Ship the recommendation UI end-to-end (IM-11). Implement difficulty adjustment (quiz difficulty adapts to mastery). Continue the slide deck.

#### Backend Pod

##### Objective
Support difficulty adjustment (IM-12 prep). Implement the `/v1/quizzes/{id}/next-question` endpoint for adaptive quizzes.

##### Tasks

**Task:** Implement the adaptive quiz endpoint: `/v1/quizzes/{id}/next-question` GET (returns the next question for an in-progress adaptive quiz, selected based on the student's current mastery of the relevant concepts). Difficulty adjustment rule per ADR-018: if mastery < 0.4, select easy questions; if 0.4–0.7, medium; if > 0.7, hard. Calls `AdaptiveEngineService.select_next_question(student_id, concept_ids, current_mastery)`.
**Why:** Roadmap W32 sprint requires "difficulty adjustment; quiz difficulty tuned to current mastery." Roadmap W33 sprint requires "Recommendation engine v1 + adaptation eval harness." IM-12 (W33) verifies difficulty adapts.
**Expected Output:** `app/api/v1/quizzes.py::next_question`; `app/services/adaptive_quiz_service.py`; tests.
**Dependencies:** Adaptive engine (W31); quiz pool (Pod B W29); mastery service (W27).
**Handoff:** Pod C-2 updates quiz UI to support adaptive mode in W33.
**Definition of Done:** Endpoint returns a question at appropriate difficulty; tests pass.

**Task:** Begin the analytics aggregation queries implementation (W34 ships the dashboard): implement `/v1/analytics/dashboard` GET (cohort mastery distribution, quiz pass rates, student engagement) + `/v1/analytics/heatmap` GET (mastery heatmap data: student × concept matrix). Optimize with indexes + materialized views for expensive aggregations. Plan the 30-day window constraint (OOS-10: no time-series > 30 days).
**Why:** Roadmap W34 sprint requires "Learning analytics dashboard (backend + UI); Aggregation queries: cohort mastery, quiz pass rates, engagement." Tech Spec Section 22.3 lists `/analytics/dashboard` + `/analytics/heatmap`. Per C-12 resolution: 4 chart types, 30-day window.
**Expected Output:** `app/api/v1/analytics.py`; `app/services/analytics_service.py`; optimized queries; tests.
**Dependencies:** Mastery records (W27); quiz attempts (W26); cohort mastery (W28).
**Handoff:** Pod C-Lead builds dashboard UI in W34.
**Definition of Done:** Endpoints return aggregated data in < 1s (with indexes); tests pass.

#### AI/ML & Data Pod

##### Objective
Implement difficulty adjustment logic. Continue the adaptation eval harness (TM-9 ships W33). Continue quiz pool generation (target 100+ by W34).

##### Tasks

**Task:** Implement difficulty adjustment logic in the adaptive engine: `AdaptiveEngineService.select_next_question(student_id, concept_ids, current_mastery)` that selects a question from the quiz pool at the appropriate difficulty (easy/medium/hard) based on mastery. If no question at the exact difficulty exists, fall back to the nearest. If IRT is activated (v0.8 if data supports — per C-9 resolution), use IRT to select a question with ~50% expected correctness (maximum information gain per Tech Spec Section 16.5). For v1.0 without IRT, use the simplified Easy → Medium → Hard progression.
**Why:** Roadmap W32 sprint requires "difficulty adjustment; quiz difficulty tuned to current mastery." Tech Spec Section 16.5 specifies CAT. C-9 resolution: IRT activated in v0.8 only if data supports.
**Expected Output:** Updated `AdaptiveEngineService`; unit tests verifying difficulty selection.
**Dependencies:** Adaptive engine (W31); quiz pool (W29); ADR-018 (W31).
**Handoff:** Pod A-Lead exposes via the adaptive quiz endpoint (above).
**Definition of Done:** Difficulty adjusts based on mastery; tests pass.

**Task:** Implement the adaptation eval harness (TM-9 prep, ships W33): `backend/app/eval/evaluators/adaptation_evaluator.py` (extends Pod D's `BaseEvaluator`). Runs 10 simulated student personas × 20 quizzes each through the adaptive engine. Measures: mastery gain over 20 quizzes vs random selection baseline. Outputs a metrics JSON. Plan CI integration (runs on every PR touching adaptive code).
**Why:** Roadmap TM-9 (W33) requires "Adaptation eval harness; Simulated trajectories; regression baseline." PB-03 trigger metric: "Simulated trajectories in W31 spike show no learning improvement vs. random policy" — but the formal harness is W33.
**Expected Output:** `backend/app/eval/evaluators/adaptation_evaluator.py`; simulated data; CI integration.
**Dependencies:** Adaptation eval harness design (W31); adaptive engine (W31).
**Handoff:** Pod D runs in CI from W33 onward; Pod B-Lead iterates based on results.
**Definition of Done:** Harness runs 10 × 20 = 200 simulated quizzes; produces mastery gain metric; CI integration works.

**Task:** Continue quiz pool generation: target 100+ questions by W34 (DDM-4). Verify question quality (manual sample). Tag with concept + difficulty. Ensure coverage across the demo PDF set.
**Why:** Roadmap W29 sprint continues; DDM-4 (W34).
**Expected Output:** 80+ questions (building toward 100+ by W34).
**Dependencies:** Quiz generation (W26); KG (W23).
**Handoff:** Pod D uses for DDM-4; Pod B-Lead uses for v0.8 adaptive.
**Definition of Done:** 80+ questions; quality > 80%; concept + difficulty tags present.

#### Frontend Pod

##### Objective
Ship the recommendation UI (IM-11). Begin the adaptive quiz UI (W33 ships it). Continue the slide deck.

##### Tasks

**Task:** Ship the recommendation UI (IM-11): verify the full flow — student logs in → sees "Recommended next" panel → clicks "Start studying" → navigates to the recommended concept → studies → takes a quiz → mastery updates → next recommendation refreshes. Fix any integration bugs. Demo on Friday.
**Why:** Roadmap IM-11 (W32) requires "Mastery → Adaptive engine → Recommendation UI; Student sees a recommendation."
**Expected Output:** Bug fixes; demo script.
**Dependencies:** Recommendation API (Pod A W31); recommendation UI (W31); mastery service (W27).
**Handoff:** Pod C-1 demos in W32 Friday demo (IM-11).
**Definition of Done:** Full flow works on staging; recommendation refreshes after quiz; demo passes.

**Task:** Begin the adaptive quiz UI: update the quiz-taking page to support adaptive mode. When a quiz is adaptive, fetch the next question via `/v1/quizzes/{id}/next-question` after each answer. Display the current difficulty badge (easy/medium/hard) and show how it changes. Plan the UI for "quiz complete" (show final score + mastery updates).
**Why:** Roadmap W33 sprint requires "Recommendation engine v1 + adaptation eval harness." IM-12 (W33) verifies difficulty adapts.
**Expected Output:** Updated quiz UI; adaptive mode toggle.
**Dependencies:** Adaptive quiz endpoint (Pod A W32); quiz UI (W26).
**Handoff:** Pod C-2 demos in W33 Friday demo (IM-12).
**Definition of Done:** Adaptive quiz UI renders; difficulty badge updates; "quiz complete" works.

**Task:** Continue the slide deck (GPM-4): draft slides 6–10 (live demo intro, AI depth, engineering process). Reference the graduation outline.
**Why:** Roadmap GPM-4 (W32) requires "Slide template chosen; first 5 slides drafted" — extend to 10 for momentum.
**Expected Output:** Slides 6–10.
**Dependencies:** Slide deck template (W31); graduation outline (W22).
**Handoff:** TPM reviews; continues in W36 (GPM-6: full deck v1).
**Definition of Done:** 10 slides drafted; TPM acknowledges.

#### DevOps / QA Pod

##### Objective
Monitor the recommendation API + adaptive quiz. Continue on-call + cross-training. Begin load test planning (W39 TM-12, but baseline measurements now).

##### Tasks

**Task:** Monitor the recommendation API + adaptive quiz: add Grafana panels for adaptive quiz endpoint latency, difficulty distribution (how often easy/medium/hard are selected), recommendation click-through rate (when students click "Start studying"). Verify the adaptation eval harness (Pod B W32) runs in CI.
**Why:** R-03 mitigation requires observability; verifies the adaptive engine behaves as expected.
**Expected Output:** Updated Grafana dashboard.
**Dependencies:** Recommendation API (W31); adaptive quiz (W32); Grafana (W6).
**Handoff:** Pod B-Lead monitors; TPM reviews at monthly review.
**Definition of Done:** Dashboard renders; metrics visible.

**Task:** Continue on-call + cross-training. Pod C engineer triages CI failures under supervision. Pod B engineer performs Qdrant + Neo4j ops independently (no supervision needed).
**Why:** Roadmap §Pod Cross-Training Plan; Feature Freeze (W38) requires 3 DevOps-capable people.
**Dependencies:** Sentry (W5); Qdrant (W12); Neo4j (W22).
**Handoff:** Pod C engineer continues through W38.
**Definition of Done:** Pod C engineer triages 1 CI failure independently.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Adaptive quiz endpoint + difficulty adjustment logic — joint.
- **Backend ↔ Frontend:** Recommendation API + recommendation UI (IM-11); adaptive quiz endpoint + adaptive quiz UI.
- **AI/ML ↔ DevOps/QA:** Adaptation eval harness; monitoring.
- **End-to-end (IM-11):** Mastery → Adaptive engine → Recommendation UI. Student sees a recommendation.

#### Week 32 Definition of Done

1. Adaptive quiz endpoint (`/v1/quizzes/{id}/next-question`) implemented.
2. Analytics aggregation queries + endpoints implemented (prep for W34).
3. Difficulty adjustment logic implemented (mastery-based; IRT conditional per C-9).
4. Adaptation eval harness implemented (10 × 20 simulated quizzes); CI integration.
5. 80+ quiz questions in the pool.
6. Recommendation UI shipped end-to-end (IM-11 verified).
7. Adaptive quiz UI built (difficulty badge, adaptive mode).
8. Slide deck at 10 slides (GPM-4 extended).
9. Recommendation + adaptive quiz monitoring in Grafana.
10. On-call W32 complete; Pod C engineer triages CI independently.

---

### Week 33 — Recommendation Engine v1 + Adaptation Eval Harness + Demo Script v1

#### Roadmap Context

- **Phase:** P4 Adaptation & Analytics
- **Milestone:** Recommendation engine v1 + adaptation eval harness + demo script v1 (skeleton); TM-9 (adaptation eval harness); IM-12 (Adaptive engine → Quiz difficulty)
- **Release:** v0.8 prep
- **Primary Objective:** Ship the recommendation engine v1 (content + peer recommendations per Roadmap OOS-6 constraint — v1 only, rule-based + content-based). Run TM-9 (adaptation eval harness). Verify IM-12 (quiz difficulty adapts). Draft the demo script v1 skeleton (GPM-5 is W34, but skeleton starts W33).

#### Backend Pod

##### Objective
Implement the recommendation engine v1 (content-based + simple rule-based; per OOS-6, no peer recommendations or collaborative filtering). Support IM-12 verification.

##### Tasks

**Task:** Implement the recommendation engine v1: `app/services/recommendation_engine_service.py::get_recommendations(student_id, top_k=3)` that returns top-3 recommendations using: (1) content-based (concepts similar to the student's interests from CSP), (2) rule-based (concepts with low mastery + prereqs met + goal-aligned), (3) ranking (weighted combination). Per OOS-6: NO peer recommendations, NO collaborative filtering. Expose via `/v1/recommendations` GET (returns top-3, distinct from `/v1/recommendations/today` which returns the single best).
**Why:** Roadmap W33 sprint requires "Recommendation engine v1; Content + peer recommendations; ranking; Top-3 recommendations shown." Per C-8 resolution: v1.0 ships rule-based + content-based only; peer/collaborative filtering is deferred (OOS-6).
**Expected Output:** `app/services/recommendation_engine_service.py`; `/v1/recommendations` endpoint; tests.
**Dependencies:** Adaptive engine (W31); mastery service (W27); KG (W23); CSP (W6).
**Handoff:** Pod C-1 displays top-3 in the recommendation UI; Pod B-Lead iterates based on adaptation eval.
**Definition of Done:** Endpoint returns 3 distinct recommendations; content + rule-based combined; tests pass.

**Task:** Support IM-12 verification: ensure the adaptive quiz endpoint (`/v1/quizzes/{id}/next-question`) demonstrably adjusts difficulty based on mastery. Add a debug field in the response showing the mastery level used + the difficulty selected. Verify on staging with a demo student (one with low mastery, one with high mastery).
**Why:** Roadmap IM-12 (W33) requires "Adaptive engine → Quiz difficulty; Quiz difficulty adapts."
**Expected Output:** Updated endpoint with debug field; IM-12 verification doc.
**Dependencies:** Adaptive quiz endpoint (W32); demo student accounts (W30).
**Handoff:** Pod D verifies IM-12 at W33 Friday demo.
**Definition of Done:** Difficulty demonstrably adapts (low-mastery student gets easy questions, high-mastery gets hard); verification doc committed.

#### AI/ML & Data Pod

##### Objective
Run TM-9 (adaptation eval harness). Verify the adaptive engine improves learning vs random. Continue quiz pool generation (target 100+ by W34).

##### Tasks

**Task:** Run TM-9 (adaptation eval harness): execute the harness (W32) on the adaptive engine. Measure mastery gain over 20 quizzes for 10 personas. Compare to random selection baseline. Document results in `docs/p4/tm-9-results.md`. If the adaptive policy shows no learning improvement vs random, invoke PB-03 playbook (default: branch B — simplified policy: pick concept with lowest mastery that has prereqs met).
**Why:** Roadmap TM-9 (W33) requires "Adaptation eval harness; Simulated trajectories; regression baseline." PB-03 trigger: "Simulated trajectories in W31 spike show no learning improvement vs. random policy" — formal verification at W33.
**Expected Output:** TM-9 results doc; PB-03 decision doc if triggered.
**Dependencies:** Adaptation eval harness (W32); adaptive engine (W31).
**Handoff:** If PB-03 triggers, B-Lead implements the chosen branch by EOD W34; TPM informs team.
**Definition of Done:** Eval results committed; adaptive policy shows > 10% mastery gain vs random (or PB-03 invoked with decision).

**Task:** Continue quiz pool generation: target 100+ questions by W34 (DDM-4). Verify quality. Ensure coverage across difficulty levels (33% easy, 33% medium, 33% hard) + across concepts.
**Why:** Roadmap W29 sprint continues; DDM-4 (W34).
**Expected Output:** 100+ questions; quality + coverage report.
**Dependencies:** Quiz generation (W26); KG (W23).
**Handoff:** Pod D uses for DDM-4; Pod B-Lead uses for v0.8 adaptive.
**Definition of Done:** 100+ questions; coverage balanced; quality > 80%.

**Task:** Co-author the demo script v1 skeleton (GPM-5 is W34, but skeleton starts W33) with TPM: fill in the demo script skeleton (GPM-3, W30) with specific clicks + narration for each of the top-10 demo beats. Reference the demo student accounts (DDM-3) + demo PDF set (DDM-1).
**Why:** Roadmap GPM-5 (W34) requires "Demo script v1 (filled in)."
**Expected Output:** `docs/graduation/demo-script-v1.md` (started W33, finalized W34).
**Dependencies:** Demo script skeleton (W30); demo student accounts (W30); demo PDF set (W15).
**Handoff:** TPM finalizes in W34.
**Definition of Done:** Skeleton started; 5 of 10 beats filled in.

#### Frontend Pod

##### Objective
Update the recommendation UI to show top-3. Polish the adaptive quiz UI. Continue the slide deck.

##### Tasks

**Task:** Update the recommendation UI to show top-3: extend the `RecommendationPanel` to display 3 recommendations (not just 1). Each card shows: concept name, rationale, suggested duration, "Start studying" button. The #1 recommendation is highlighted.
**Why:** Roadmap W33 sprint requires "Top-3 recommendations shown."
**Expected Output:** Updated `RecommendationPanel.tsx`; Storybook story.
**Dependencies:** Recommendation engine v1 (Pod A W33); recommendation UI (W32).
**Handoff:** Pod C-1 demos in W33 Friday demo.
**Definition of Done:** 3 recommendations render; #1 highlighted; click works.

**Task:** Polish the adaptive quiz UI: ensure the difficulty badge updates smoothly during an adaptive quiz. Add a visual indicator when difficulty changes (e.g., a subtle animation). Test with the demo student accounts (low + high mastery).
**Why:** IM-12 (W33) verification requires the UI to clearly show difficulty adaptation.
**Expected Output:** Polished adaptive quiz UI.
**Dependencies:** Adaptive quiz UI (W32); demo student accounts (W30).
**Handoff:** Pod C-2 demos in W33 Friday demo (IM-12).
**Definition of Done:** Difficulty badge updates smoothly; animation works; demo passes.

**Task:** Continue the slide deck: draft slides 11–15 (future, Q&A, appendix). Reference the graduation outline.
**Why:** GPM-4 momentum; full deck v1 due W36 (GPM-6).
**Expected Output:** Slides 11–15.
**Dependencies:** Slide deck (W31–W32).
**Handoff:** TPM reviews; full deck v1 by W36.
**Definition of Done:** 15 slides drafted.

#### DevOps / QA Pod

##### Objective
Verify IM-12. Monitor the recommendation engine. Continue on-call + cross-training.

##### Tasks

**Task:** Verify IM-12: run the adaptive quiz on staging with a low-mastery demo student + a high-mastery demo student. Confirm the low-mastery student gets easy questions + the high-mastery gets hard. Document in `docs/p4/im-12-verification.md`.
**Why:** Roadmap IM-12 (W33) requires "Adaptive engine → Quiz difficulty; Quiz difficulty adapts."
**Expected Output:** IM-12 verification doc.
**Dependencies:** Adaptive quiz (W32); demo student accounts (W30).
**Handoff:** TPM reviews at Friday demo.
**Definition of Done:** Difficulty demonstrably adapts; verification committed.

**Task:** Monitor the recommendation engine: add Grafana panels for recommendation engine latency, top-3 click-through rate, recommendation diversity (how often different concepts are recommended). Verify no bias toward always recommending the same concept.
**Why:** R-03 mitigation; quality verification.
**Expected Output:** Updated Grafana dashboard.
**Dependencies:** Recommendation engine (Pod A W33); Grafana (W6).
**Handoff:** Pod B-Lead monitors.
**Definition of Done:** Dashboard renders; diversity metric visible.

**Task:** Continue on-call + cross-training. Pod C engineer triages CI failures + Sentry errors. Pod B engineer performs vector DB ops independently.
**Why:** Roadmap §Pod Cross-Training Plan; Feature Freeze (W38) requires 3 DevOps-capable people.
**Dependencies:** Sentry (W5); Qdrant (W12); Neo4j (W22).
**Handoff:** Pod C engineer continues through W38.
**Definition of Done:** Pod C engineer triages 2 CI failures + 1 Sentry error independently.

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Recommendation engine v1 + adaptive quiz debug field — joint.
- **Backend ↔ Frontend:** Recommendation engine + top-3 UI; adaptive quiz + difficulty badge.
- **AI/ML ↔ TPM:** Demo script v1 skeleton co-authored.
- **DevOps/QA ↔ All Pods:** IM-12 verified; TM-9 results.
- **End-to-end (IM-12):** Adaptive engine → Quiz difficulty adapts. Verified on staging.

#### Week 33 Definition of Done

1. Recommendation engine v1 implemented (content + rule-based; no peer per OOS-6).
2. IM-12 verified: quiz difficulty adapts based on mastery (debug field + verification doc).
3. TM-9 met: adaptation eval harness runs; adaptive policy shows > 10% mastery gain vs random (or PB-03 invoked).
4. 100+ quiz questions in the pool (DDM-4 prep complete).
5. Demo script v1 skeleton started (5/10 beats filled).
6. Recommendation UI shows top-3.
7. Adaptive quiz UI polished (difficulty badge + animation).
8. Slide deck at 15 slides.
9. Recommendation engine monitoring in Grafana.
10. On-call W33 complete; Pod C engineer triages CI + Sentry independently.

---

### Week 34 — Learning Analytics Dashboard + v0.8 Tag

#### Roadmap Context

- **Phase:** P4 Adaptation & Analytics
- **Milestone:** Learning analytics dashboard (backend + UI) + v0.8 tag; DDM-4 (demo quiz pool); GPM-5 (demo script v1)
- **Release:** v0.8 (tag `v0.8.0`)
- **Primary Objective:** Ship the learning analytics dashboard (4 chart types, 30-day window per C-12). Tag v0.8. Finalize the demo quiz pool (DDM-4). Finalize the demo script v1 (GPM-5).

#### Backend Pod

##### Objective
Finalize the analytics endpoints. Support the dashboard UI. Verify IRT activation decision (per C-9: activate if quiz data supports).

##### Tasks

**Task:** Finalize the analytics endpoints: polish `/v1/analytics/dashboard` + `/v1/analytics/heatmap` (implemented W32). Add `/v1/analytics/quiz-pass-rates` (per-course, per-quiz pass rates over 30 days) + `/v1/analytics/engagement` (chat messages, quizzes taken, time spent per student). Optimize queries (indexes, materialized views). Ensure 30-day window enforced (OOS-10).
**Why:** Roadmap W34 sprint requires "Learning analytics dashboard (backend + UI); Aggregation queries: cohort mastery, quiz pass rates, engagement; instructor dashboard with charts (Recharts/Visx)." Per C-12 resolution: 4 chart types, 30-day window.
**Expected Output:** Finalized analytics endpoints; optimized queries; tests.
**Dependencies:** Analytics endpoints (W32); mastery + quiz + chat data.
**Handoff:** Pod C-Lead builds dashboard UI.
**Definition of Done:** All 4 analytics endpoints return data in < 1s; 30-day window enforced; tests pass.

**Task:** Verify IRT activation decision (per C-9 resolution): check if quiz data supports IRT (≥ 5 interactions per question across all students). If yes, activate IRT in the adaptive engine (replace simplified Easy → Medium → Hard with IRT-based item selection per Tech Spec Section 16.5). If no, document the decision + defer to v1.1.
**Why:** Roadmap v0.8 milestone: "IRT if data supports." C-9 resolution: IRT activated in v0.8 only if data supports.
**Expected Output:** IRT activation decision doc; if activated, IRT integration in adaptive engine.
**Dependencies:** Quiz attempts data (W26+); `py-irt` library; BKT scaffold (W28).
**Handoff:** Pod B-Lead implements if activated; otherwise documents deferral.
**Definition of Done:** Decision documented; IRT activated or deferred with rationale.

**Task:** Tag `v0.8.0` on `main` after Friday demo. Cut a GitHub Release with release notes referencing: adaptive engine (priority scoring + rule-based fallback F-7), recommendation engine v1 (content + rule-based), recommendation API + UI, adaptive quiz with difficulty adjustment, SM-2 spaced repetition, learning analytics dashboard (4 charts, 30-day window), IRT activation decision, 100+ quiz questions, ADR-018, adaptation eval harness (TM-9).
**Why:** Roadmap v0.8 milestone (Mar 27, 2027 = W34).
**Expected Output:** Git tag `v0.8.0`; GitHub Release published.
**Dependencies:** All W31–W34 DoD items.
**Handoff:** TPM announces v0.8; P4 continues toward W38 Feature Freeze.
**Definition of Done:** Tag exists; release notes complete; advisor notified.

#### AI/ML & Data Pod

##### Objective
Finalize the demo quiz pool (DDM-4). Finalize the demo script v1 (GPM-5). Continue IRT evaluation.

##### Tasks

**Task:** Finalize the demo quiz pool (DDM-4): verify 20 quizzes with known-good answers, tagged by concept, in the demo dataset. Each quiz has 10 questions, all manually verified for factual accuracy. Commit the pool to `tests/data/demo_quiz_pool/` with a manifest.
**Why:** Roadmap DDM-4 (W34) requires "Demo quiz pool: 20 quizzes with known-good answers, tagged by concept."
**Expected Output:** 20 verified quizzes; manifest.
**Dependencies:** Quiz generation (W26); demo PDF set (W15).
**Handoff:** Pod D verifies; TPM notes for graduation prep.
**Definition of Done:** 20 quizzes verified; manifest committed.

**Task:** Finalize the demo script v1 (GPM-5): complete all 10 demo beats with specific clicks + narration. Reference the demo student accounts (DDM-3) + demo quiz pool (DDM-4) + demo PDF set (DDM-1). Time the demo to 8 minutes.
**Why:** Roadmap GPM-5 (W34) requires "Demo script v1 (filled in)."
**Expected Output:** `docs/graduation/demo-script-v1.md` (final).
**Dependencies:** Demo script skeleton (W30); demo quiz pool (above); demo student accounts (W30).
**Handoff:** TPM reviews; dry-run #0 at W40 (GPM-8).
**Definition of Done:** All 10 beats filled; demo timed to 8 minutes; TPM + advisor review.

**Task:** Continue IRT evaluation (per C-9): if activated, integrate `py-irt` with the adaptive engine. Run IRT parameter estimation on the quiz attempts data. Verify IRT-based item selection produces ~50% expected correctness (maximum information per Tech Spec Section 16.5). If not activated, document the data volume required for future activation.
**Why:** C-9 resolution: IRT activated in v0.8 only if data supports.
**Expected Output:** IRT integration (if activated) OR deferral doc with data requirements.
**Dependencies:** IRT activation decision (Pod A W34); `py-irt` library.
**Handoff:** Pod B-Lead finalizes; TPM notes for v1.0 release.
**Definition of Done:** IRT either integrated + verified OR deferred with clear rationale.

#### Frontend Pod

##### Objective
Ship the learning analytics dashboard UI (4 chart types per C-12). Build the instructor dashboard. Polish the v0.8 demo.

##### Tasks

**Task:** Ship the learning analytics dashboard UI: `/instructor/courses/{id}/analytics` page with 4 chart types (per C-12 resolution): (1) cohort mastery heatmap (Recharts/Nivo heatmap: student × concept), (2) quiz pass rates over 30 days (line chart), (3) student engagement (bar chart: chat messages, quizzes taken, time spent per student), (4) mastery distribution (histogram). 30-day window enforced (OOS-10). Filter by course, by student.
**Why:** Roadmap W34 sprint requires "instructor dashboard with charts (Recharts/Visx)." Per C-12 resolution: 4 chart types, 30-day window.
**Expected Output:** `frontend/src/app/(instructor)/courses/[id]/analytics/page.tsx`; 4 chart components.
**Dependencies:** Analytics endpoints (Pod A W34); Recharts + Nivo (W2 stack).
**Handoff:** Pod C-Lead demos in W34 Friday demo (v0.8).
**Definition of Done:** 4 charts render with real data; filters work; 30-day window enforced; Lighthouse perf ≥ 70.

**Task:** Polish the v0.8 demo: ensure the full flow (login → recommendation → study → adaptive quiz → mastery update → analytics dashboard) is polished. Record a 5-min demo video.
**Why:** v0.8 is the P4 demo to the advisor.
**Expected Output:** Polished UI; demo video.
**Dependencies:** All W31–W34 work.
**Handoff:** TPM uses the video if the live demo fails.
**Definition of Done:** Demo video recorded; UI polished.

#### DevOps / QA Pod

##### Objective
Verify DDM-4. Monitor the analytics dashboard performance. Continue on-call + cross-training.

##### Tasks

**Task:** Verify DDM-4: confirm 20 quizzes with known-good answers, tagged by concept, are in the demo dataset on staging. Run smoke tests on each quiz (instructor generates → student takes → grading correct). Document in `docs/p4/ddm-4-verification.md`.
**Why:** Roadmap DDM-4 (W34) verification.
**Expected Output:** DDM-4 verification doc.
**Dependencies:** Demo quiz pool (Pod B W34); staging environment.
**Handoff:** TPM notes; demo data track continues (DDM-5 at W36).
**Definition of Done:** 20 quizzes verified; smoke tests pass.

**Task:** Monitor the analytics dashboard performance: add Grafana panels for analytics endpoint latency (P50/P95), query execution time per chart, dashboard load time. Configure alert: P95 > 2s triggers review (NFR-1 compliance).
**Why:** NFR-1 (P95 < 2s under 50 users) compliance; R-09 (DB performance) mitigation.
**Expected Output:** Updated Grafana dashboard; alert rule.
**Dependencies:** Analytics endpoints (Pod A W34); Grafana (W6).
**Handoff:** Pod A-Lead addresses bottlenecks before W39 load test.
**Definition of Done:** Dashboard renders; alert tested.

**Task:** Continue on-call + cross-training. Pod C engineer continues CI/CD + Sentry triage. Pod B engineer continues vector DB ops. Verify ≥ 2 people are now cross-trained on DevOps tasks (target: 3 by W38).
**Why:** Roadmap §Pod Cross-Training Plan; Feature Freeze (W38) requires 3 DevOps-capable people.
**Dependencies:** Sentry (W5); Qdrant (W12); Neo4j (W22); GitHub Actions (W1).
**Handoff:** Pod C engineer continues through W38.
**Definition of Done:** 2 people cross-trained (Pod D × 2 + Pod B engineer + Pod C engineer in progress).

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** IRT activation decision joint; analytics endpoints consume mastery + quiz data.
- **Backend ↔ Frontend:** Analytics endpoints + dashboard UI integration.
- **AI/ML ↔ TPM:** DDM-4 + GPM-5 (demo script v1).
- **DevOps/QA ↔ All Pods:** DDM-4 verification; analytics monitoring.
- **End-to-end (v0.8):** Adaptive engine + recommendation engine + analytics dashboard. Demo to advisor.

#### Week 34 Definition of Done

1. Analytics endpoints finalized (4 endpoints, 30-day window, optimized).
2. IRT activation decision documented (activated or deferred per C-9).
3. v0.8.0 tagged; release notes published.
4. Demo quiz pool (20 quizzes) verified (DDM-4).
5. Demo script v1 finalized (GPM-5).
6. Learning analytics dashboard UI shipped (4 chart types per C-12).
7. v0.8 demo video recorded.
8. DDM-4 verified: 20 quizzes on staging.
9. Analytics dashboard monitoring in Grafana; alert configured.
10. ≥ 2 people cross-trained on DevOps tasks.
11. Friday demo (v0.8) passes; advisor in attendance.

---



### Week 35 — Admin Dashboard + Notifications + Demo Student Accounts

#### Roadmap Context

- **Phase:** P4 Adaptation & Analytics
- **Milestone:** Admin dashboard (minimal) + notification system (basic) + demo student accounts created (DDM-3 done W30, confirm); IM-13 (Analytics dashboard ↔ real DB data)
- **Release:** v0.9 prep
- **Primary Objective:** Ship the admin dashboard (minimal: user list, course list, system health per Roadmap §Structural Descopes #3). Ship basic notifications. Verify IM-13 (analytics dashboard ↔ real DB data).

#### Backend Pod

##### Objective
Implement the admin API (W31 design). Implement the notification system (basic). Verify IM-13.

##### Tasks

**Task:** Implement the admin API: `/v1/admin/users` GET (list users, filter by role, paginate, deactivate), `/v1/admin/courses` GET (list courses, audit), `/v1/admin/system-health` GET (DB connections, queue depth, error rate, uptime, Qdrant + Neo4j + Redis status). RBAC enforced (admin-only). Audit log via CLI tool only (per OOS-9: no audit log UI).
**Why:** Roadmap W35 sprint requires "Admin dashboard (minimal); User/course management, system health." Per Roadmap §Structural Descopes #3: "Admin dashboard is minimal: user list, course list, system health. No audit log UI." Tech Spec Section 22.2 mentions Admin role.
**Expected Output:** `app/api/v1/admin.py`; `app/services/admin_service.py`; tests.
**Dependencies:** Admin API design (W31); auth (W5); RBAC (W6); observability stack (W6).
**Handoff:** Pod C-2 builds admin dashboard UI; Pod D monitors system health via the endpoint.
**Definition of Done:** Endpoints work; RBAC enforced; tests pass.

**Task:** Implement the notification system (basic): in-app notifications for key events (quiz graded, mastery updated, new recommendation, material processing complete). Add a `notifications` table (`id`, `user_id`, `type`, `message`, `read`, `created_at`). `/v1/notifications` GET (list, filter by read/unread), `/v1/notifications/{id}/read` POST (mark as read). WebSocket push for real-time notifications (extend the W7 WS foundation). Email notifications are a stretch (best-effort; if time permits, use SendGrid free tier; otherwise defer).
**Why:** Roadmap W35 sprint requires "notification system (basic); in-app + email notifications for key events." Per Roadmap §Descope candidates #2: "Notification system (skip; demo without)" is a descope candidate if buffer is consumed.
**Expected Output:** `app/api/v1/notifications.py`; `app/services/notification_service.py`; `notifications` table migration; WS push integration.
**Dependencies:** WebSocket foundation (W7); auth (W5).
**Handoff:** Pod C-2 builds notification bell UI; Pod D monitors notification delivery.
**Definition of Done:** In-app notifications fire on key events; WS push works; email deferred (or stretch).

**Task:** Verify IM-13: ensure the analytics dashboard (W34) displays real DB data, not mock data. Run the dashboard on staging with the demo student accounts (DDM-3) + demo quiz pool (DDM-4). Verify cohort mastery, quiz pass rates, engagement metrics reflect real activity.
**Why:** Roadmap IM-13 (W35) requires "Analytics dashboard ↔ real DB data; Instructor sees real cohort metrics."
**Expected Output:** IM-13 verification doc.
**Dependencies:** Analytics dashboard (W34); demo data (W30, W34).
**Handoff:** TPM reviews at Friday demo.
**Definition of Done:** Dashboard shows real data; verification committed.

#### AI/ML & Data Pod

##### Objective
Continue recommendation engine iteration based on TM-9 results. Continue quiz pool maintenance. Begin demo data curation (DDM-5 prep, due W36).

##### Tasks

**Task:** Iterate on the recommendation engine based on TM-9 results (W33): if PB-03 triggered (adaptive policy shows no learning improvement), apply the chosen branch (default: branch B — simplified policy: pick concept with lowest mastery that has prereqs met). Re-run TM-9. Document before/after.
**Why:** PB-03 default branch (B) must be implemented if triggered.
**Expected Output:** Updated recommendation engine; before/after TM-9 report.
**Dependencies:** TM-9 results (W33); recommendation engine (W33).
**Handoff:** Pod A-Lead deploys; Pod C-Lead verifies UI still works.
**Definition of Done:** TM-9 metrics improve (or escalate to PB-03 branch C: defer adaptive engine to v1.1).

**Task:** Begin demo data curation (DDM-5 prep, due W36): identify 5 known-good RAG questions that reliably produce cited answers from the demo PDF set. Test each on staging with the demo student accounts. Document expected answers + citations.
**Why:** Roadmap DDM-5 (W36) requires "5 known-good RAG questions identified and validated (golden demo set)." Used for the graduation demo (GPM-7 at W38).
**Expected Output:** Draft of 5 known-good RAG questions + expected answers.
**Dependencies:** RAG service (W15); demo PDF set (W15); demo student accounts (W30).
**Handoff:** Pod D verifies in W36 (DDM-5).
**Definition of Done:** 5 questions drafted; tested on staging; answers reliable.

**Task:** Continue quiz pool maintenance: verify the 100+ questions are still accurate (LLM-generated questions can drift if the underlying model changes). Re-generate any that fail manual review. Ensure question quality > 80% on a fresh manual sample.
**Why:** Question quality affects demo + adaptive engine accuracy.
**Expected Output:** Quality report; re-generated questions if needed.
**Dependencies:** Quiz pool (W34).
**Handoff:** Pod D uses for DDM-4 verification (ongoing).
**Definition of Done:** Quality > 80%; report committed.

#### Frontend Pod

##### Objective
Build the admin dashboard UI (minimal). Build the notification bell. Polish the UI for v0.9.

##### Tasks

**Task:** Build the admin dashboard UI: `/admin` page with 3 sections: (1) Users (table with email, role, status, deactivate button), (2) Courses (table with title, owner, material count, audit link), (3) System health (DB connections, queue depth, error rate, uptime, Qdrant + Neo4j + Redis status cards). RBAC enforced (redirect to `/403` if not admin).
**Why:** Roadmap W35 sprint requires "Admin dashboard (minimal)." Per Roadmap §Structural Descopes #3: minimal.
**Expected Output:** `frontend/src/app/(admin)/admin/page.tsx`; `frontend/src/features/admin/components/UsersTable.tsx`, `CoursesTable.tsx`, `SystemHealth.tsx`.
**Dependencies:** Admin API (Pod A W35); design tokens (W2); RBAC (W6).
**Handoff:** Pod C-2 demos in W35 Friday demo.
**Definition of Done:** Admin dashboard renders; users + courses + system health visible; RBAC enforced.

**Task:** Build the notification bell: a bell icon in the topnav showing unread count. Clicking opens a dropdown with recent notifications. "Mark all as read" button. WS push updates the count in real time.
**Why:** Roadmap W35 sprint requires notifications. Tech Spec Section 20.2.
**Expected Output:** `frontend/src/components/layout/NotificationBell.tsx`; integration with WS + notification API.
**Dependencies:** Notification API (Pod A W35); WebSocket (W7); topnav (W7).
**Handoff:** Pod C-2 demos in W35 Friday demo.
**Definition of Done:** Bell renders; unread count updates via WS; dropdown works; mark-as-read works.

**Task:** Polish the UI for v0.9: address any visual issues from W34 demo. Ensure all flows (student, instructor, admin) are polished. Test accessibility (WCAG 2.1 AA on critical paths per Roadmap §Testing Strategy).
**Why:** v0.9 is the Feature Freeze gate; polish matters.
**Expected Output:** Polished UI; accessibility fixes.
**Dependencies:** All W5–W34 work.
**Handoff:** Pod C-Lead demos in W38 (v0.9).
**Definition of Done:** Lighthouse a11y ≥ 90 on critical paths; no visual bugs.

#### DevOps / QA Pod

##### Objective
Monitor the admin dashboard + notifications. Continue on-call + cross-training. Begin bug bash #1 prep (TM-10 is W36).

##### Tasks

**Task:** Monitor the admin dashboard + notifications: add Grafana panels for admin API latency, notification delivery rate, WS connection count. Verify the system health endpoint reports accurate data.
**Why:** Admin dashboard is the operational surface; monitoring ensures it works when needed.
**Expected Output:** Updated Grafana dashboard.
**Dependencies:** Admin API (Pod A W35); Grafana (W6).
**Handoff:** Pod D uses the system health endpoint during on-call.
**Definition of Done:** Dashboard renders; system health accurate.

**Task:** Begin bug bash #1 prep (TM-10 is W36): plan the 90-minute bug bash. Define the scope (all user flows: student, instructor, admin). Prepare a bug reporting template. Recruit 5+ testers (all pod members + advisor if available). Schedule for W36.
**Why:** Roadmap TM-10 (W36) requires "Bug bash #1; Top-50 bugs triaged; P1s assigned." Prep now lets W36 focus on execution.
**Expected Output:** Bug bash plan; reporting template; schedule.
**Dependencies:** All W5–W35 work.
**Handoff:** Pod D runs the bug bash in W36.
**Definition of Done:** Plan committed; testers recruited; schedule confirmed.

**Task:** Continue on-call + cross-training. Pod C engineer continues CI/CD + Sentry triage. Verify ≥ 3 people cross-trained on DevOps tasks (target for Feature Freeze W38).
**Why:** Roadmap §Pod Cross-Training Plan; Feature Freeze (W38) requires 3 DevOps-capable people.
**Dependencies:** Sentry (W5); GitHub Actions (W1); Qdrant (W12); Neo4j (W22).
**Handoff:** Pod C engineer continues through W38.
**Definition of Done:** ≥ 3 people cross-trained (Pod D × 2 + Pod B engineer + Pod C engineer).

#### Cross-Pod Integration

- **Backend ↔ Frontend:** Admin API + admin dashboard UI; notification API + notification bell.
- **Backend ↔ AI/ML:** Recommendation engine iteration (PB-03 if triggered).
- **AI/ML ↔ DevOps/QA:** Demo data curation (DDM-5 prep); quiz pool maintenance.
- **DevOps/QA ↔ All Pods:** IM-13 verified; bug bash #1 prep.
- **End-to-end (IM-13):** Analytics dashboard ↔ real DB data. Instructor sees real cohort metrics.

#### Week 35 Definition of Done

1. Admin API implemented (users, courses, system health; RBAC enforced).
2. Notification system (basic) implemented: in-app notifications fire on key events; WS push works.
3. IM-13 verified: analytics dashboard shows real DB data.
4. Recommendation engine iterated (PB-03 branch B if triggered); TM-9 metrics improved.
5. 5 known-good RAG questions drafted (DDM-5 prep).
6. Quiz pool quality verified (> 80%).
7. Admin dashboard UI built (minimal: users, courses, system health).
8. Notification bell built (WS push).
9. UI polished for v0.9; Lighthouse a11y ≥ 90.
10. Admin + notification monitoring in Grafana.
11. Bug bash #1 plan committed (TM-10 prep).
12. ≥ 3 people cross-trained on DevOps tasks.

---

### Week 36 — UX Polish + Bug Bash #1 + Demo Script v2 + DDM-5

#### Roadmap Context

- **Phase:** P4 Adaptation & Analytics
- **Milestone:** UX polish pass + bug bash #1 + demo script v2; TM-10 (bug bash #1); DDM-5 (5 known-good RAG questions); GPM-6 (full deck v1 reviewed by advisor); DM-13 (instructor + student quickstarts)
- **Release:** v0.9 prep
- **Primary Objective:** Run bug bash #1 (TM-10). Polish UX based on W35 demo feedback. Finalize the demo script v2. Validate 5 known-good RAG questions (DDM-5). Review the full deck v1 with the advisor (GPM-6). Publish user-facing quickstarts (DM-13).

#### Backend Pod

##### Objective
Fix top bugs from bug bash #1. Continue monitoring. Light capacity week (exam crunch 2 begins late Apr / W39–W40, but W36 is the last full-capacity week before it).

##### Tasks

**Task:** Fix top backend bugs from bug bash #1 (TM-10): triage all backend bugs from the W36 bash. Fix P1s immediately; assign P2s to W37–W38. Common issues: edge cases in the recommendation engine (empty mastery, no prereqs met), admin API errors, notification delivery failures.
**Why:** Roadmap W36 sprint requires "Bug bash #1; Top-50 bugs triaged; P1s assigned." Roadmap W37 sprint requires "Close P1/P2 bugs from bash." TM-10 (W36) is the bug bash milestone.
**Expected Output:** Bug fixes; updated tests covering each bug.
**Dependencies:** Bug bash #1 results (Pod D W36).
**Handoff:** Pod D re-runs E2E tests to verify fixes.
**Definition of Done:** Top backend bugs fixed; P1 count reduced; tests pass.

**Task:** Co-author DM-13 (instructor + student quickstarts, due W36): `docs/quickstarts/instructor.md` + `docs/quickstarts/student.md` covering: how to register, create a course, upload a PDF, generate a quiz, view analytics (instructor); how to register, enroll, take a quiz, chat with materials, view mastery + recommendations (student). Include screenshots.
**Why:** Roadmap DM-13 (W36) requires "Instructor quickstart + student quickstart; User-facing docs."
**Expected Output:** 2 quickstart docs.
**Dependencies:** All W5–W35 work.
**Handoff:** TPM publishes; Docusaurus updated.
**Definition of Done:** Docs merged; screenshots included; reviewed by C-Lead.

#### AI/ML & Data Pod

##### Objective
Validate 5 known-good RAG questions (DDM-5). Co-author GPM-6 (full deck v1 reviewed by advisor). Continue recommendation engine iteration.

##### Tasks

**Task:** Validate 5 known-good RAG questions (DDM-5): test each on staging with the demo PDF set + demo student accounts. Verify each produces a cited answer with ≥ 2 citations pointing to real chunks. Document expected answers + citations. Commit to `tests/data/demo_rag_questions/`.
**Why:** Roadmap DDM-5 (W36) requires "5 known-good RAG questions identified and validated (golden demo set)." Used for the graduation demo (GPM-7 at W38).
**Expected Output:** 5 validated questions + expected answers; manifest.
**Dependencies:** 5 known-good questions draft (W35); RAG service (W15); demo PDF set (W15).
**Handoff:** Pod D verifies; TPM notes for graduation prep.
**Definition of Done:** 5 questions validated; each produces cited answers; manifest committed.

**Task:** Co-author GPM-6 (full deck v1 reviewed by advisor) with TPM: complete the slide deck (15+ slides from W31–W33). Schedule a review meeting with the advisor. Incorporate feedback. Target: advisor-approved deck v1 by EOD W36.
**Why:** Roadmap GPM-6 (W36) requires "Full deck v1 reviewed by advisor."
**Expected Output:** Final deck v1; advisor feedback incorporated.
**Dependencies:** Slide deck (W31–W33); graduation outline (W22).
**Handoff:** TPM schedules advisor review; continues to deck v2 at W43 (GPM-11).
**Definition of Done:** Deck v1 reviewed; advisor feedback incorporated.

**Task:** Continue recommendation engine iteration: based on ongoing TM-9 monitoring + W35 demo feedback, refine the priority scoring formula. Improve diversity (avoid always recommending the same concept). Improve cold-start (new students with no mastery).
**Why:** R-03 mitigation; recommendation quality for the demo.
**Expected Output:** Updated recommendation engine; before/after metrics.
**Dependencies:** Recommendation engine (W33); TM-9 monitoring (W33).
**Handoff:** Pod A-Lead deploys; Pod C-Lead verifies UI.
**Definition of Done:** Diversity improved; cold-start handled; metrics improved.

#### Frontend Pod

##### Objective
UX polish pass based on W35 demo feedback. Address top frontend bugs from bug bash #1.

##### Tasks

**Task:** UX polish pass: address top UX issues from W35 demo. Common issues: empty states (what does a new student see?), loading states (skeleton loaders vs spinners), error states (friendly messages + retry), mobile responsiveness (best-effort per OOS-8). Accessibility: keyboard navigation, screen reader, color contrast.
**Why:** Roadmap W36 sprint requires "UX polish pass; Address top UX issues from W35 demo."
**Expected Output:** Polish fixes; accessibility improvements.
**Dependencies:** All W5–W35 work.
**Handoff:** Pod C-Lead demos in W36 Friday demo.
**Definition of Done:** Empty/loading/error states polished; Lighthouse a11y ≥ 90; keyboard nav works.

**Task:** Fix top frontend bugs from bug bash #1: triage all frontend bugs. Fix P1s immediately; assign P2s to W37–W38. Common issues: SSE stream rendering edge cases, citation rendering bugs, dashboard chart rendering issues.
**Why:** Roadmap W36–W37 sprint requires addressing bug bash findings.
**Expected Output:** Bug fixes; updated tests.
**Dependencies:** Bug bash #1 results (Pod D W36).
**Handoff:** Pod D re-runs E2E tests.
**Definition of Done:** Top frontend bugs fixed; P1 count reduced.

#### DevOps / QA Pod

##### Objective
Run bug bash #1 (TM-10). Verify DDM-5. Continue on-call + cross-training. Begin Feature Freeze prep (W38).

##### Tasks

**Task:** Run bug bash #1 (TM-10): 90-minute bash with 5+ testers. Scope: all user flows (student, instructor, admin). Each tester files bugs in GitHub Issues with severity (P1/P2/P3), pod assignment, reproduction steps. Triage all findings; assign P1s immediately. Target: top-50 bugs triaged.
**Why:** Roadmap TM-10 (W36) requires "Bug bash #1; Top-50 bugs triaged; P1s assigned."
**Expected Output:** Bug bash report; 50+ bugs triaged; P1s assigned to pods.
**Dependencies:** All W5–W35 work; testers recruited (W35 prep).
**Handoff:** Pod A + Pod B + Pod C fix bugs in W36–W37.
**Definition of Done:** 50+ bugs triaged; P1s assigned; report committed.

**Task:** Verify DDM-5: confirm 5 known-good RAG questions produce cited answers on staging. Run each via the chat UI + via curl. Document in `docs/p4/ddm-5-verification.md`.
**Why:** Roadmap DDM-5 (W36) verification.
**Expected Output:** DDM-5 verification doc.
**Dependencies:** 5 validated questions (Pod B W36); staging environment.
**Handoff:** TPM notes; demo data track continues (DDM-6 at W38).
**Definition of Done:** 5 questions verified; smoke tests pass.

**Task:** Begin Feature Freeze prep (W38): draft the Feature Freeze sign-off doc `docs/gates/gate-4-feature-freeze.md` listing all Gate 4 criteria (per Roadmap): v0.9 demoed, all P1 bugs from bug bash #1 closed or waived, coverage ≥ 60% on critical paths (TM-11), ≥ 3 people cross-trained on DevOps, deck v1 reviewed by advisor (GPM-6), demo data curated + validated (DDM-5). Plan the W38 freeze review meeting.
**Why:** Roadmap W38 signs Feature Freeze (Gate 4). Prep now lets W38 focus on sign-off.
**Expected Output:** Sign-off doc draft; review meeting scheduled.
**Dependencies:** All W5–W36 work.
**Handoff:** TPM runs the W38 freeze review meeting; all pod leads + TPM sign.
**Definition of Done:** Sign-off doc drafted; all criteria tracked; meeting scheduled.

#### Cross-Pod Integration

- **All Pods:** Bug bash #1 findings distributed across pods for fixing.
- **AI/ML ↔ TPM:** GPM-6 (full deck v1 reviewed by advisor); DDM-5 validated.
- **DevOps/QA ↔ All Pods:** TM-10 (bug bash #1); DDM-5 verified; Feature Freeze prep.
- **TPM ↔ All Pods:** DM-13 (quickstarts); GPM-6 (deck v1).

#### Week 36 Definition of Done

1. Top backend bugs from bash #1 fixed; P1 count reduced.
2. DM-13: instructor + student quickstarts published.
3. 5 known-good RAG questions validated (DDM-5).
4. GPM-6: full deck v1 reviewed by advisor; feedback incorporated.
5. Recommendation engine iterated (diversity + cold-start).
6. UX polish pass complete; Lighthouse a11y ≥ 90.
7. Top frontend bugs from bash #1 fixed.
8. TM-10 met: bug bash #1 run; 50+ bugs triaged; P1s assigned.
9. DDM-5 verified: 5 questions produce cited answers.
10. Feature Freeze sign-off doc drafted; review meeting scheduled.

---

### Week 37 — Bug Fixing Sprint + Accessibility Pass + Demo Dataset Finalized

#### Roadmap Context

- **Phase:** P4 Adaptation & Analytics
- **Milestone:** Bug fixing sprint + accessibility pass + demo dataset finalized; DDM-6 (demo data snapshot)
- **Release:** v0.9 prep (final week)
- **Primary Objective:** Close all P1 + P2 bugs from bug bash #1. Pass WCAG 2.1 AA on critical paths. Finalize the demo dataset (DDM-6). Note: exam crunch 2 begins (late Apr; capacity ~12 hrs/wk for W39–W40, but W37 is still ~56 hrs/wk). Front-load hardening tasks per R-17 mitigation.

#### Backend Pod

##### Objective
Close all P1 backend bugs. Begin DB performance optimization (W39 ships the perf pass). Front-load hardening.

##### Tasks

**Task:** Close all P1 backend bugs from bug bash #1: every P1 must be fixed or formally waived (with rationale). P2 bugs: fix high-impact ones; defer low-impact to W39+ tech debt. Update tests for each fix.
**Why:** Roadmap W37 sprint requires "Close P1/P2 bugs from bash." Roadmap §Gate 4 sign-off: "All P1 bugs from bug bash #1 closed or waived."
**Expected Output:** Bug fixes; updated tests; waiver docs if any.
**Dependencies:** Bug bash #1 results (W36).
**Handoff:** Pod D re-runs E2E tests; TPM verifies P1 count = 0 (or waived).
**Definition of Done:** 0 open P1s (or formally waived with TPM approval); P2s triaged.

**Task:** Begin DB performance optimization (W39 ships the full pass): identify slow queries (from the slow query log + Grafana). Add indexes where missing (e.g., on `mastery_records.student_id`, `quiz_attempts.student_id`, `chunks.material_id`). Plan connection pool tuning (default 10 may be too low for 50 concurrent users).
**Why:** Roadmap W39 sprint requires "Performance pass + DB optimization; P95 latency < 2s on RAG; load test; indexes; query plans; connection pool tuning." R-09 (DB performance) mitigation. Front-loading per R-17 mitigation.
**Expected Output:** Index migrations; slow query report; connection pool tuning plan.
**Dependencies:** All W5–W36 work; slow query log.
**Handoff:** Pod A-Lead finalizes in W39; Pod D runs the load test.
**Definition of Done:** Indexes added; slow queries identified; tuning plan ready for W39.

#### AI/ML & Data Pod

##### Objective
Close all P1 AI/ML bugs. Finalize the recommendation engine for v0.9. Continue demo data curation (DDM-6 prep).

##### Tasks

**Task:** Close all P1 AI/ML bugs from bug bash #1: common issues — recommendation engine edge cases (no concepts with prereqs met, empty mastery), RAG prompt failures on certain query types, quiz generation JSON parse errors. Fix each; update the RAG eval / adaptation eval to cover the edge cases.
**Why:** Roadmap W37 sprint requires closing P1s.
**Expected Output:** Bug fixes; updated eval harnesses.
**Dependencies:** Bug bash #1 results (W36); RAG eval (W15); adaptation eval (W33).
**Handoff:** Pod D re-runs evals in CI.
**Definition of Done:** 0 open P1 AI/ML bugs; evals pass.

**Task:** Finalize the recommendation engine for v0.9: ensure the engine produces reliable, diverse recommendations for the demo student accounts (DDM-3). Test each of the 5 demo students + verify the recommendations make pedagogical sense. Document in `docs/p4/recommendation-engine-v1-final.md`.
**Why:** v0.9 is the Feature Freeze gate; recommendation engine must be demo-ready.
**Expected Output:** Finalization report.
**Dependencies:** Recommendation engine (W33–W36); demo student accounts (W30).
**Handoff:** Pod C-Lead verifies UI; TPM notes for demo.
**Definition of Done:** 5 demo students produce sensible recommendations; report committed.

**Task:** Begin DDM-6 prep (demo data snapshot, due W38): plan the demo data snapshot — a script that exports the current staging data (users, courses, materials, chunks, embeddings, KG, mastery, quizzes, recommendations) into a restorable format. Plan the restore procedure (tested in W38).
**Why:** Roadmap DDM-6 (W38) requires "Demo data snapshot created; restore script tested." Used for prod deployment + dry-runs.
**Expected Output:** Snapshot + restore script plan.
**Dependencies:** All W5–W37 work.
**Handoff:** Pod D implements + tests in W38 (DDM-6).
**Definition of Done:** Plan committed; ready for W38 implementation.

#### Frontend Pod

##### Objective
Close all P1 frontend bugs. Pass WCAG 2.1 AA on critical paths. Polish for v0.9.

##### Tasks

**Task:** Close all P1 frontend bugs from bug bash #1: common issues — SSE stream rendering, citation rendering, dashboard chart rendering, keyboard navigation, screen reader announcements. Fix each; update Storybook stories + React Testing Library tests.
**Why:** Roadmap W37 sprint requires closing P1s + "WCAG 2.1 AA on critical paths."
**Expected Output:** Bug fixes; updated tests + stories.
**Dependencies:** Bug bash #1 results (W36).
**Handoff:** Pod D re-runs E2E + accessibility tests.
**Definition of Done:** 0 open P1 frontend bugs; Lighthouse a11y ≥ 90.

**Task:** Pass WCAG 2.1 AA on critical paths: run `axe-core` on the critical paths (login, register, course list, upload, chat, quiz, mastery, dashboard, admin). Fix all violations. Verify keyboard navigation works on all interactive elements. Verify screen reader announcements for dynamic content (chat streaming, mastery updates).
**Why:** Roadmap W37 sprint requires "WCAG 2.1 AA on critical paths; axe-core clean on key flows." Roadmap §Gate 4 sign-off references accessibility (via "demo polish" implicit). Roadmap §Success Criteria #4: "Maintain engineering rigor throughout: ≥ 60% coverage on critical paths, ADRs for every major decision, runbooks for operations."
**Expected Output:** Accessibility fixes; axe-core report (0 violations on critical paths).
**Dependencies:** All W5–W36 work; `axe-core` library.
**Handoff:** Pod D includes in W38 Feature Freeze validation.
**Definition of Done:** axe-core clean on critical paths; keyboard nav works; screen reader tested.

#### DevOps / QA Pod

##### Objective
Verify P1 bug closure. Run accessibility validation. Continue on-call + cross-training. Finalize Feature Freeze prep.

##### Tasks

**Task:** Verify P1 bug closure: re-run all E2E + integration tests after bug fixes. Confirm 0 open P1s across all pods (or formally waived). Document in `docs/p4/p1-closure-w37.md`.
**Why:** Roadmap §Gate 4 sign-off: "All P1 bugs from bug bash #1 closed or waived."
**Expected Output:** P1 closure report.
**Dependencies:** Bug fixes (Pod A + Pod B + Pod C W37).
**Handoff:** TPM includes in Feature Freeze sign-off (W38).
**Definition of Done:** 0 open P1s (or waived); report committed.

**Task:** Run accessibility validation: execute `axe-core` on staging critical paths. Verify WCAG 2.1 AA compliance. Document violations (should be 0 after Pod C fixes).
**Why:** Roadmap W37 sprint requires "axe-core clean on key flows."
**Expected Output:** Accessibility validation report.
**Dependencies:** Accessibility fixes (Pod C W37); `axe-core`.
**Handoff:** TPM includes in Feature Freeze sign-off.
**Definition of Done:** 0 violations on critical paths; report committed.

**Task:** Finalize Feature Freeze prep: complete the sign-off doc `docs/gates/gate-4-feature-freeze.md` with all criteria status. Confirm TM-11 (coverage ≥ 60%) is on track (or escalate). Confirm 3 people cross-trained on DevOps. Confirm GPM-6 (deck v1 reviewed). Confirm DDM-5 validated. Schedule the W38 freeze review meeting.
**Why:** Roadmap W38 signs Feature Freeze (Gate 4).
**Expected Output:** Finalized sign-off doc; meeting scheduled.
**Dependencies:** All W5–W37 work.
**Handoff:** TPM runs the W38 freeze review meeting; all pod leads + TPM sign.
**Definition of Done:** Sign-off doc finalized; all criteria tracked; meeting scheduled.

#### Cross-Pod Integration

- **All Pods:** P1 bug closure sprint.
- **DevOps/QA ↔ All Pods:** P1 closure verification; accessibility validation.
- **TPM ↔ All Pods:** Feature Freeze prep; DDM-6 plan.

#### Week 37 Definition of Done

1. 0 open P1 backend bugs (or waived); P2s triaged.
2. DB performance optimization started (indexes added; slow queries identified).
3. 0 open P1 AI/ML bugs; evals pass.
4. Recommendation engine finalized for v0.9; 5 demo students produce sensible recommendations.
5. DDM-6 (snapshot + restore) plan committed.
6. 0 open P1 frontend bugs; Lighthouse a11y ≥ 90.
7. WCAG 2.1 AA passed on critical paths (axe-core clean).
8. P1 closure report committed.
9. Accessibility validation report committed.
10. Feature Freeze sign-off doc finalized; review meeting scheduled.

---

### Week 38 — v0.9 + Feature Freeze (GATE 4)

#### Roadmap Context

- **Phase:** P4 Adaptation & Analytics (final week)
- **Milestone:** **v0.9 + Feature Freeze (GATE 4)**; demo to advisor; deck v1 reviewed by advisor (GPM-6 done W36, confirm); DDM-6 (demo data snapshot); GPM-7 (demo data curated)
- **Release:** v0.9 (tag `v0.9.0`)
- **Primary Objective:** Ship v0.9 (feature-complete). Sign the Feature Freeze (no new features after this point, only fixes). Demo to advisor. Create the demo data snapshot (DDM-6). Note: exam crunch 2 is in full swing (capacity ~12 hrs/wk); plan is intentionally lighter. Hard rule: no new features after W38 even if v0.9 is incomplete (R-20 mitigation).

#### Backend Pod

##### Objective
Ship v0.9. Sign Feature Freeze. Support DDM-6. Begin P5 prep (hardening).

##### Tasks

**Task:** Verify v0.9 demo flow end-to-end on staging: full student flow + instructor flow + admin flow + analytics + recommendations + adaptive quiz. Fix any last-minute P1 bugs. Prepare demo script.
**Why:** Roadmap v0.9 milestone (Apr 24, 2027 = W38) — Gate 4. Demo: feature-complete.
**Expected Output:** Demo script; bug fixes.
**Dependencies:** All W5–W37 work.
**Handoff:** TPM runs the W38 Friday demo (advisor invited).
**Definition of Done:** Demo passes on staging; advisor demoed.

**Task:** Sign the Feature Freeze: all pod leads + TPM sign `docs/gates/gate-4-feature-freeze.md`. Post-freeze: no new features, no new APIs, no new UI screens. Bug fixes, perf improvements, docs, test coverage, accessibility fixes, security fixes, demo polish are allowed. Post-freeze change protocol: any new feature requires TPM + Tech Lead joint approval + explicit descope decision + demo script update.
**Why:** Roadmap Gate 4 sign-off. Feature Freeze. Roadmap §Feature Freeze: "No new features, no new APIs, no new UI screens."
**Expected Output:** Signed sign-off doc; Feature Freeze active.
**Dependencies:** Sign-off doc (Pod D W37); all Gate 4 criteria met.
**Handoff:** TPM announces Feature Freeze; P5 (Hardening) starts W39.
**Definition of Done:** All pod leads + TPM sign; Feature Freeze active; post-freeze protocol enforced.

**Task:** Support DDM-6 (demo data snapshot): provide the data export tooling — `scripts/export_demo_data.py` that exports all staging data (users, courses, materials, chunks, embeddings, KG, mastery, quizzes, recommendations) into a restorable format (SQL dump + MinIO bucket snapshot + Qdrant collection snapshot + Neo4j dump). Support Pod D's restore testing.
**Why:** Roadmap DDM-6 (W38) requires "Demo data snapshot created; restore script tested."
**Expected Output:** Export script; documentation.
**Dependencies:** All W5–W37 work.
**Handoff:** Pod D tests restore in W38 (DDM-6).
**Definition of Done:** Export script runs; produces a complete snapshot.

**Task:** Tag `v0.9.0` on `main` after Friday demo + Feature Freeze sign-off. Cut a GitHub Release with release notes referencing: adaptive engine + recommendation engine v1 + adaptive quiz + SM-2 + analytics dashboard (4 charts) + admin dashboard (minimal) + notifications + 5 demo student accounts + 100+ quiz questions + 5 known-good RAG questions + accessibility (WCAG 2.1 AA) + ADR-018 + DM-12 + DM-13.
**Why:** Roadmap v0.9 milestone — Gate 4.
**Expected Output:** Git tag `v0.9.0`; GitHub Release published.
**Dependencies:** All W31–W38 DoD items + Gate 4 sign-off.
**Handoff:** TPM announces v0.9; P5 (Hardening) starts W39.
**Definition of Done:** Tag exists; release notes complete; advisor notified.

#### AI/ML & Data Pod

##### Objective
Finalize v0.9 AI/ML. Co-author GPM-7 (demo data curated). Light capacity week (exam crunch).

##### Tasks

**Task:** Finalize v0.9 AI/ML: verify the adaptive engine + recommendation engine + RAG + quiz generation all work reliably on staging with the demo data. Run final evals (RAG + adaptation). Document v0.9 baseline metrics for regression comparison in P5.
**Why:** v0.9 is the Feature Freeze gate; AI/ML must be stable.
**Expected Output:** v0.9 AI/ML baseline metrics doc.
**Dependencies:** All W31–W37 work.
**Handoff:** Pod D monitors for regression in P5.
**Definition of Done:** Evals pass; baseline metrics committed.

**Task:** Co-author GPM-7 (demo data curated) with TPM: confirm the demo data is clean, predictable, reproducible — 3 courses × 5–10 PDFs each (DDM-1), 5 demo student accounts with seeded mastery (DDM-3), 20 quizzes with known-good answers (DDM-4), 5 known-good RAG questions (DDM-5). Ensure all demo data is committed + restorable.
**Why:** Roadmap GPM-7 (W38) requires "Demo data curated (clean, predictable, reproducible)."
**Expected Output:** Demo data curation report.
**Dependencies:** DDM-1 (W15), DDM-3 (W30), DDM-4 (W34), DDM-5 (W36).
**Handoff:** Pod D creates the snapshot (DDM-6); TPM notes for graduation.
**Definition of Done:** Demo data curated; all DDM items verified.

#### Frontend Pod

##### Objective
Finalize the v0.9 demo UI. Record demo video. Begin P5 prep (docs completion + demo assets).

##### Tasks

**Task:** Finalize the v0.9 demo UI: ensure all flows (student, instructor, admin) are polished. Record a 5-min demo video covering the key features. Commit to `docs/demo-videos/v0.9.mp4`.
**Why:** v0.9 is the Gate 4 demo to the advisor.
**Expected Output:** Polished UI; demo video.
**Dependencies:** All W5–W37 work.
**Handoff:** TPM uses the video if the live demo fails.
**Definition of Done:** Demo video recorded; UI polished.

**Task:** Begin P5 prep (docs completion + demo assets): identify docs gaps (ADRs needing updates, missing runbooks, incomplete quickstarts). Plan the W41 docs completion sprint. Plan the fallback demo video (GPM-9, W41).
**Why:** Roadmap W41 sprint requires "docs completion + fallback demo video recorded." Prep now lets W41 focus on execution.
**Expected Output:** Docs gap list; demo asset plan.
**Dependencies:** All W5–W37 work.
**Handoff:** Pod C-Lead finalizes in W41.
**Definition of Done:** Gap list committed; plan ready for W41.

#### DevOps / QA Pod

##### Objective
Validate TM-11 (coverage ≥ 60%). Verify DDM-6 (snapshot + restore). Run v0.9 release validation. Sign Feature Freeze.

##### Tasks

**Task:** Validate TM-11 (coverage ≥ 60% on critical paths): run final coverage report. If below 60%, escalate to TPM (Feature Freeze cannot sign if TM-11 fails — Roadmap §Gate 4 sign-off criterion #3). Pair with Pod A + Pod B + Pod C to add tests if needed.
**Why:** Roadmap TM-11 (W38) is a Gate 4 sign-off criterion: "Coverage ≥ 60% on critical paths; Measured in CI; gate for Feature Freeze."
**Expected Output:** Coverage report; TM-11 sign-off.
**Dependencies:** All W5–W37 work.
**Handoff:** TPM includes in Gate 4 sign-off.
**Definition of Done:** Coverage ≥ 60% on critical paths; TM-11 signed off.

**Task:** Verify DDM-6 (snapshot + restore): test the restore procedure (Pod A W38 export script) on a fresh staging environment. Verify all data restores correctly (users, courses, materials, chunks, embeddings, KG, mastery, quizzes, recommendations). Document in `docs/p4/ddm-6-verification.md`.
**Why:** Roadmap DDM-6 (W38) requires "Demo data snapshot created; restore script tested."
**Expected Output:** DDM-6 verification doc.
**Dependencies:** Export script (Pod A W38); fresh staging env.
**Handoff:** TPM notes; demo data frozen at W42 (DDM-8).
**Definition of Done:** Restore succeeds; all data verified; report committed.

**Task:** Run the v0.9 release validation: full E2E test on staging; smoke tests; verify all Gate 4 criteria. Document in `docs/releases/v0.9-validation.md`.
**Why:** Gate 4 sign-off requires validation.
**Expected Output:** Validation report.
**Dependencies:** All W5–W38 work.
**Handoff:** TPM includes in Gate 4 sign-off; advisor notified.
**Definition of Done:** All criteria verified; report committed.

**Task:** Sign the Feature Freeze: all pod leads + TPM sign `docs/gates/gate-4-feature-freeze.md`. Confirm all 7 Gate 4 criteria: v0.9 demoed, P1 bugs closed/waived, coverage ≥ 60% (TM-11), ≥ 3 people cross-trained, deck v1 reviewed (GPM-6), demo data curated (DDM-5), all pod leads + TPM sign.
**Why:** Roadmap Gate 4 sign-off.
**Expected Output:** Signed sign-off doc.
**Dependencies:** All W5–W38 work.
**Handoff:** TPM announces Feature Freeze; P5 starts W39.
**Definition of Done:** All pod leads + TPM sign; Feature Freeze active.

#### Cross-Pod Integration

- **All Pods:** v0.9 + Feature Freeze sign-off. All Gate 4 criteria verified.
- **TPM ↔ All Pods:** Feature Freeze signed; v0.9 tagged; GPM-7 (demo data curated).
- **DevOps/QA ↔ All Pods:** TM-11 sign-off; DDM-6 verification; release validation; Feature Freeze sign-off.
- **End-to-end (v0.9):** Feature-complete system on staging public URL; advisor demoed.

#### Week 38 Definition of Done

1. **v0.9.0 tagged; Gate 4 (Feature Freeze) signed by all pod leads + TPM.**
2. v0.9 demo to advisor passes on staging public URL.
3. Feature Freeze active: no new features post-W38.
4. Demo data snapshot created + restore tested (DDM-6).
5. GPM-7: demo data curated (clean, predictable, reproducible).
6. v0.9 AI/ML baseline metrics committed.
7. v0.9 demo video recorded.
8. Docs gap list committed (prep for W41).
9. TM-11 met: coverage ≥ 60% on critical paths.
10. DDM-6 verified: snapshot + restore works.
11. v0.9 release validation report committed; all Gate 4 criteria verified.
12. Friday demo (v0.9) passes; advisor in attendance.
13. P5 (Hardening) starts W39 with Feature Freeze active. 1 week of critical-path slack remaining in this segment (hard: 0 weeks post-W38).

---



### Week 39 — Performance Pass + DB Optimization + Load Test

#### Roadmap Context

- **Phase:** P5 Hardening
- **Milestone:** Performance pass + DB optimization; TM-12 (load test: 50 concurrent users, P95 < 2s); DM-14 (runbooks: deploy, rollback, DR, on-call)
- **Release:** v1.0-rc prep
- **Primary Objective:** Ship the performance pass: P95 < 2s on RAG under 50 concurrent users (TM-12). Optimize the DB. Write the runbooks (DM-14). Note: exam crunch 2 is in full swing (capacity ~12 hrs/wk); plan is intentionally lighter. Per R-17 mitigation: front-load hardening into W37 (done) + treat W39–W40 as bonus.

#### Backend Pod

##### Objective
Optimize the backend for the load test. Fix performance bottlenecks. Implement caching for hot paths.

##### Tasks

**Task:** Optimize the backend for TM-12 (load test): profile the RAG pipeline under load (k6 script simulating 50 concurrent users). Identify bottlenecks: retrieval latency, LLM call latency, DB query latency, connection pool exhaustion. Apply fixes: (1) cache popular retrieval results in Redis (5-min TTL), (2) optimize DB queries (indexes from W37 prep), (3) tune connection pool (asyncpg max_connections=50), (4) parallelize independent operations (e.g., BM25 + vector search in parallel, not sequentially).
**Why:** Roadmap W39 sprint requires "Performance pass + DB optimization; P95 latency < 2s on RAG; load test; indexes; query plans; connection pool tuning." Roadmap TM-12 (W39) requires "50 concurrent users; P95 < 2s." Roadmap Engineering Success #5: "P95 latency < 2s on RAG under 50 concurrent users." R-09 (DB performance) mitigation.
**Expected Output:** Performance optimizations; before/after load test report.
**Dependencies:** DB optimization prep (W37); Redis (W5); Grafana (W6).
**Handoff:** Pod D runs the formal TM-12 load test.
**Definition of Done:** P95 < 2s on RAG under 50 concurrent users (or bottlenecks identified + fix plan if not met).

**Task:** Implement caching for hot paths: (1) `/v1/recommendations/today` — already cached (W31); verify 5-min TTL is sufficient under load. (2) `/v1/analytics/dashboard` — cache for 5 min per course (instructors often refresh). (3) `/v1/kg/concepts` — cache for 1 hour (KG changes infrequently). (4) Popular retrieval results — cache the top-100 queries per course for 5 min. Use Redis with proper invalidation (event-based on data change).
**Why:** NFR-1 (P95 < 2s) compliance; R-09 mitigation.
**Expected Output:** Caching layer in `app/services/cache_service.py`; cache invalidation hooks.
**Dependencies:** Redis (W5); analytics endpoints (W34); KG API (W24).
**Handoff:** Pod D verifies cache hit rate in Grafana.
**Definition of Done:** Cache hit rate > 70% for hot paths; latency improved.

#### AI/ML & Data Pod

##### Objective
Optimize the RAG pipeline for the load test. Optimize LLM call latency. Verify embedding batch performance.

##### Tasks

**Task:** Optimize the RAG pipeline for the load test: profile the 4-stage retrieval (query embedding → hybrid search → reranker → context assembly → LLM generation). Identify bottlenecks: reranker is typically the slowest (cross-encoder on 20 candidates). Apply fixes: (1) batch the reranker call (process all 20 candidates in one forward pass instead of 20 separate calls), (2) cache query embeddings (popular queries), (3) parallelize BM25 + vector search, (4) consider reducing reranker top-K from 20 to 15 (smaller precision hit, big latency gain).
**Why:** TM-12 (P95 < 2s) compliance. R-02 mitigation requires the RAG pipeline to be fast.
**Expected Output:** Optimized retrieval service; before/after latency report.
**Dependencies:** Retrieval service (W14); reranker (W13); Grafana (W6).
**Handoff:** Pod A-Lead integrates with caching (above).
**Definition of Done:** Reranker latency reduced by ≥ 30%; RAG P95 improved.

**Task:** Optimize LLM call latency: configure the LiteLLM gateway to use a faster model for non-critical paths (e.g., GPT-4o-mini for quiz generation; GPT-4o for RAG only). Enable streaming (already done W17). Configure timeout (10s) + retry (once with backoff). Verify under load the LLM doesn't become the bottleneck.
**Why:** NFR-1 compliance; R-06 (LLM cost) + R-07 (LLM provider) mitigation.
**Expected Output:** Updated LiteLLM config; latency report.
**Dependencies:** LiteLLM gateway (W7); Langfuse (W7).
**Handoff:** Pod D monitors LLM latency in Grafana.
**Definition of Done:** LLM P95 < 1.5s under load; fallback model configured.

**Task:** Verify embedding batch performance: ensure the BGE-M3 provider can handle batch embedding (100 chunks) in < 5s. If too slow, consider switching to OpenAI text-embedding-3-small (F-3 trigger: "Self-hosted BGE-M3 too slow OR GPU unavailable").
**Why:** NFR-3 (100-page PDF processing < 60s) compliance; embedding is part of the ingestion pipeline.
**Expected Output:** Embedding batch performance report; F-3 decision if triggered.
**Dependencies:** BGE-M3 provider (W6); OpenAI embedding provider (W6).
**Handoff:** Pod D monitors; Pod B-Lead decides F-3 if needed.
**Definition of Done:** Batch embedding < 5s for 100 chunks (or F-3 invoked with decision).

#### Frontend Pod

##### Objective
Optimize frontend performance: bundle size, code splitting, SSR. Address Lighthouse performance issues. Light capacity week (exam crunch).

##### Tasks

**Task:** Optimize frontend performance: run Lighthouse on critical pages (login, dashboard, chat, quiz, analytics). Address issues: (1) bundle size — code split heavy libraries (Cytoscape.js, Recharts, Nivo) via dynamic import, (2) SSR — ensure Next.js SSR is working (view page source shows server-rendered HTML), (3) image optimization — use `next/image` for any images, (4) font loading — use `next/font` with `display: swap`. Target: Lighthouse performance ≥ 80 on critical pages.
**Why:** Roadmap R-10 (Frontend bundle too large, score 6) mitigation. Roadmap §Engineering Success implies performance matters.
**Expected Output:** Performance optimizations; before/after Lighthouse report.
**Dependencies:** All W5–W38 work; Lighthouse.
**Handoff:** Pod D includes Lighthouse in CI.
**Definition of Done:** Lighthouse performance ≥ 80 on critical pages; bundle size reduced.

#### DevOps / QA Pod

##### Objective
Run TM-12 (load test: 50 concurrent users, P95 < 2s). Write runbooks (DM-14). Continue on-call + cross-training.

##### Tasks

**Task:** Run TM-12 (load test): k6 script simulating 50 concurrent users hitting the RAG pipeline (`/v1/chat` + `/v1/rag/query`) for 10 minutes. Measure P50/P95/P99 latency, error rate, resource utilization (CPU, memory, DB connections, Redis, Qdrant, Neo4j). Target: P95 < 2s on RAG. Document in `docs/p5/tm-12-load-test.md`.
**Why:** Roadmap TM-12 (W39) requires "50 concurrent users; P95 < 2s." Roadmap Engineering Success #5. NFR-1 (strict per C-5 resolution).
**Expected Output:** Load test report; k6 script `scripts/load-test-rag-50users.js`.
**Dependencies:** Performance optimizations (Pod A + Pod B W39); staging environment.
**Handoff:** Pod A-Lead addresses any bottlenecks found; TPM reviews at monthly review.
**Definition of Done:** P95 < 2s on RAG under 50 concurrent users (or bottlenecks identified + fix plan).

**Task:** Write the runbooks (DM-14, due W39 — but exam crunch may push to W41; start now):
- `docs/runbooks/deploy.md`: how to deploy to staging + prod (Docker Compose, k3s, manual approval workflow).
- `docs/runbooks/rollback.md`: how to rollback to a previous tag (automated on smoke test failure).
- `docs/runbooks/dr.md`: disaster recovery — DB restore from backup, Qdrant restore, Neo4j restore, MinIO restore. RTO < 1h, RPO < 24h.
- `docs/runbooks/on-call.md`: on-call rotation, escalation path, common incident response procedures.
**Why:** Roadmap DM-14 (W39) requires "Runbooks: deploy, rollback, DR, on-call." Roadmap §Gate 5 sign-off: "Runbooks complete (DM-14)."
**Expected Output:** 4 runbook docs.
**Dependencies:** All W5–W38 work; on-call rotation (W20).
**Handoff:** TPM publishes; all engineers reference during on-call.
**Definition of Done:** 4 runbooks committed; reviewed by D-Lead; tested (at least the deploy + rollback runbooks).

**Task:** Continue on-call + cross-training. Verify ≥ 3 people cross-trained on DevOps tasks (Feature Freeze was W38; this should be confirmed). If < 3, escalate (Feature Freeze criterion).
**Why:** Roadmap §Gate 4 sign-off criterion #4: "At least 3 people cross-trained on DevOps tasks." Should be confirmed at W38; W39 verifies.
**Dependencies:** Cross-training (W4–W38).
**Handoff:** Pod D confirms; TPM notes.
**Definition of Done:** ≥ 3 people cross-trained (Pod D × 2 + Pod B engineer + Pod C engineer).

#### Cross-Pod Integration

- **Backend ↔ AI/ML:** Performance optimization joint (caching + retrieval optimization + LLM latency).
- **Backend ↔ Frontend:** Backend performance + frontend bundle optimization.
- **DevOps/QA ↔ All Pods:** TM-12 load test; runbooks; cross-training verification.
- **End-to-end (TM-12):** 50 concurrent users on RAG; P95 < 2s.

#### Week 39 Definition of Done

1. Backend optimized for load: caching, indexes, connection pool tuned, parallel operations.
2. RAG pipeline optimized: reranker batched, parallel retrieval, LLM latency reduced.
3. LLM call latency P95 < 1.5s under load; fallback model configured.
4. Embedding batch performance verified (< 5s for 100 chunks) or F-3 invoked.
5. Frontend performance: Lighthouse ≥ 80 on critical pages; bundle size reduced.
6. TM-12 met: 50 concurrent users; P95 < 2s on RAG (or fix plan).
7. DM-14: 4 runbooks written (deploy, rollback, DR, on-call).
8. ≥ 3 people cross-trained on DevOps tasks (confirmed).

---

### Week 40 — Security Review + Auth Hardening + Dry-Run #0

#### Roadmap Context

- **Phase:** P5 Hardening
- **Milestone:** Security review + auth hardening + dry-run #0 (internal); TM-13 (security review); GPM-8 (dry-run #0); DDM-7 (demo data on prod-like env)
- **Release:** v1.0-rc prep
- **Primary Objective:** Pass the security review (TM-13): OWASP top 10, SAST clean, no high vulns. Harden auth. Run dry-run #0 (internal, no advisor). Load demo data on prod-like env (DDM-7). Note: exam crunch 2 final week (capacity ~12 hrs/wk).

#### Backend Pod

##### Objective
Pass the security review. Harden auth. Fix any SAST/dependency vulnerabilities.

##### Tasks

**Task:** Pass the security review (TM-13): (1) OWASP top 10 audit — verify each vulnerability class is mitigated (injection, broken auth, sensitive data exposure, XXE, broken access control, security misconfiguration, XSS, insecure deserialization, known vulns, insufficient logging). (2) SAST (Semgrep) clean — run `semgrep --config=auto` on the backend; fix all high/medium findings. (3) Dependency scan — `pip-audit` or `safety check`; update any vulnerable dependencies. (4) Pen test — manual pen test of the auth + RBAC + API endpoints. Document in `docs/p5/tm-13-security-review.md`.
**Why:** Roadmap TM-13 (W40) requires "OWASP top 10; SAST clean; no high vulns." Roadmap §Gate 5 sign-off: "Security review complete; no critical/high vulns (TM-13)." Roadmap §Engineering Success #4: "No critical or high security vulnerabilities are open at Code Freeze."
**Expected Output:** Security review report; SAST/dependency fixes; pen test report.
**Dependencies:** All W5–W39 work; Semgrep; pip-audit.
**Handoff:** Pod D verifies; TPM includes in Gate 5 sign-off.
**Definition of Done:** 0 critical/high vulns; SAST clean; OWASP top 10 mitigated; report committed.

**Task:** Harden auth: (1) rate limiting on `/v1/auth/login` + `/v1/auth/register` (max 5 attempts per minute per IP — prevents brute force). (2) Refresh token rotation (already in ADR-006; verify implemented). (3) MFA optional (TOTP via `pyotp`; not required for v1.0, but scaffold for v1.1). (4) Password strength enforcement (already in W5; verify). (5) Session timeout (24h access, 7d refresh — already in ADR-006; verify).
**Why:** Roadmap W40 sprint requires "auth hardening; rate limiting; refresh rotation; MFA optional." Tech Spec Section 24.1 specifies bcrypt + HTTPS + JWT.
**Expected Output:** Auth hardening; rate limiting middleware; MFA scaffold.
**Dependencies:** Auth (W5); ADR-006 (W8).
**Handoff:** Pod D verifies in security review.
**Definition of Done:** Rate limiting works; refresh rotation verified; MFA scaffolded; password strength enforced.

#### AI/ML & Data Pod

##### Objective
Address any AI/ML security concerns: prompt injection, data leakage via LLM, KG poisoning. Light capacity week.

##### Tasks

**Task:** Address AI/ML security concerns: (1) prompt injection — add input sanitization on user queries (strip prompt-injection patterns like "ignore previous instructions"). (2) Data leakage via LLM — verify the RAG prompt doesn't leak system prompts or other users' data. (3) KG poisoning — verify concept extraction doesn't accept malicious input (e.g., a PDF with deliberately misleading concepts). Document mitigations in `docs/p5/ai-ml-security.md`.
**Why:** Security review includes AI/ML-specific threats. Tech Spec Section 24 mentions security architecture.
**Expected Output:** AI/ML security report; mitigations.
**Dependencies:** RAG service (W15); concept extraction (W23).
**Handoff:** Pod D includes in TM-13 report.
**Definition of Done:** Prompt injection mitigated; data leakage verified absent; KG poisoning mitigated.

**Task:** Support DDM-7 (demo data on prod-like env): verify the demo data snapshot (DDM-6) loads correctly on a prod-like environment. Run smoke tests. Document any issues.
**Why:** Roadmap DDM-7 (W40) requires "Demo data loaded on prod-like env; smoke-tested." Joint with Pod D.
**Dependencies:** DDM-6 snapshot (W38); prod-like env (Pod D W40).
**Handoff:** Pod D verifies; TPM notes for dry-runs.
**Definition of Done:** Demo data loads on prod-like env; smoke tests pass.

#### Frontend Pod

##### Objective
Address frontend security: XSS, CSRF, CSP. Support dry-run #0 (GPM-8). Light capacity week.

##### Tasks

**Task:** Address frontend security: (1) XSS — verify React's default escaping is working; no `dangerouslySetInnerHTML` without sanitization. (2) CSRF — verify cookies are `SameSite=Strict` (or `Lax`); verify POST requests require CSRF token (or use `Authorization` header instead). (3) CSP — configure Content-Security-Policy header in `next.config.ts` (restrict scripts to same-origin + trusted CDN). (4) SAST — run `semgrep --config=auto` on the frontend; fix findings.
**Why:** Security review includes frontend. Tech Spec Section 24 mentions transport + auth security.
**Expected Output:** Frontend security fixes; CSP header; SAST clean.
**Dependencies:** All W5–W39 work; Semgrep.
**Handoff:** Pod D includes in TM-13 report.
**Definition of Done:** XSS mitigated; CSRF protected; CSP configured; SAST clean.

**Task:** Support dry-run #0 (GPM-8, internal): participate in the internal dry-run of the graduation demo. Practice the demo script (GPM-5). Identify UI issues (slow loading, visual glitches, dead-ends). Fix critical issues; log non-critical for W41.
**Why:** Roadmap GPM-8 (W40) requires "Dry-run #0 (internal, no advisor); First end-to-end rehearsal; identify gaps."
**Expected Output:** Dry-run feedback; critical UI fixes.
**Dependencies:** Demo script v1 (W34); demo data (W38); staging environment.
**Handoff:** TPM logs dry-run findings; Pod C-Lead addresses critical issues.
**Definition of Done:** Dry-run completed; critical UI issues fixed; findings logged.

#### DevOps / QA Pod

##### Objective
Run TM-13 (security review). Run dry-run #0 (GPM-8). Verify DDM-7. Continue on-call.

##### Tasks

**Task:** Run TM-13 (security review): coordinate the OWASP top 10 audit (Pod A), SAST (Semgrep on backend + frontend), dependency scan (`pip-audit` + `npm audit`), pen test (manual). Document all findings in `docs/p5/tm-13-security-review.md`. Verify 0 critical/high vulns.
**Why:** Roadmap TM-13 (W40) requires "OWASP top 10; SAST clean; no high vulns."
**Expected Output:** TM-13 security review report.
**Dependencies:** Security work (Pod A + Pod B + Pod C W40).
**Handoff:** TPM includes in Gate 5 sign-off.
**Definition of Done:** 0 critical/high vulns; SAST clean; OWASP top 10 mitigated; report committed.

**Task:** Run dry-run #0 (GPM-8): coordinate the internal dry-run. All pod members participate. TPM runs the demo script (GPM-5). Identify gaps in the demo flow, timing, narration. Log findings. Schedule follow-up fixes for W41.
**Why:** Roadmap GPM-8 (W40) requires "Dry-run #0 (internal, no advisor)."
**Expected Output:** Dry-run #0 report; fix list for W41.
**Dependencies:** Demo script v1 (W34); demo data (W38); all pod members.
**Handoff:** Pod C-Lead addresses critical UI issues (W40); Pod A + Pod B address any backend/AI issues (W41).
**Definition of Done:** Dry-run completed; findings logged; critical fixes scheduled.

**Task:** Verify DDM-7 (demo data on prod-like env): set up a prod-like environment (mirror of prod configuration). Load the demo data snapshot (DDM-6). Run smoke tests (login, chat, quiz, analytics). Document in `docs/p5/ddm-7-verification.md`.
**Why:** Roadmap DDM-7 (W40) requires "Demo data loaded on prod-like env; smoke-tested."
**Expected Output:** DDM-7 verification doc.
**Dependencies:** DDM-6 snapshot (W38); prod-like env.
**Handoff:** TPM notes; ready for dry-runs + prod deployment.
**Definition of Done:** Demo data loads; smoke tests pass; report committed.

**Task:** Continue on-call rotation. Monitor for any security incidents.
**Why:** On-call continues; security review may surface issues.
**Expected Output:** On-call log.
**Dependencies:** On-call schedule (W20).
**Handoff:** Next on-call engineer (W41).
**Definition of Done:** On-call W40 complete; no unpaged P1 incidents.

#### Cross-Pod Integration

- **All Pods:** Security review (TM-13) — each pod addresses its security surface.
- **DevOps/QA ↔ All Pods:** TM-13 coordination; dry-run #0; DDM-7 verification.
- **TPM ↔ All Pods:** Dry-run #0; demo script practice.

#### Week 40 Definition of Done

1. TM-13 met: 0 critical/high vulns; SAST clean; OWASP top 10 mitigated.
2. Auth hardened: rate limiting, refresh rotation, MFA scaffold, password strength.
3. AI/ML security: prompt injection mitigated, data leakage verified absent, KG poisoning mitigated.
4. Frontend security: XSS mitigated, CSRF protected, CSP configured, SAST clean.
5. Dry-run #0 (GPM-8) completed; findings logged; critical fixes scheduled.
6. DDM-7 verified: demo data loads on prod-like env; smoke tests pass.
7. On-call W40 complete; no unpaged P1s.

---

### Week 41 — Bug Bash #2 + Docs + DR Drill + Fallback Demo Video

#### Roadmap Context

- **Phase:** P5 Hardening
- **Milestone:** Bug bash #2 + docs completion + backup + DR drill + fallback demo video recorded; TM-14 (bug bash #2: ≤ 3 P1s open); GPM-9 (fallback demo video); DDM-8 (demo data frozen); DM-15 (final architecture diagram + ADR index); DM-16 (README polish + demo recording)
- **Release:** v1.0-rc prep (final week)
- **Primary Objective:** Run bug bash #2 (TM-14: ≤ 3 P1s open). Complete docs (DM-15 + DM-16). Run the DR drill. Record the fallback demo video (GPM-9). Freeze demo data (DDM-8). Capacity is recovering (post-exam).

#### Backend Pod

##### Objective
Fix bugs from bash #2. Complete the final architecture diagram + ADR index (DM-15). Support the DR drill.

##### Tasks

**Task:** Fix bugs from bash #2 (TM-14): triage all backend bugs from the W41 bash. Fix P1s immediately. Target: ≤ 3 P1s open across all pods by EOD W41 (Roadmap §Gate 5 sign-off criterion #2).
**Why:** Roadmap W41 sprint requires "Bug bash #2; 2-hour bash; close everything." Roadmap TM-14 (W41) requires "≤ 3 P1s open."
**Expected Output:** Bug fixes; updated tests.
**Dependencies:** Bug bash #2 results (Pod D W41).
**Handoff:** Pod D verifies; TPM confirms ≤ 3 P1s.
**Definition of Done:** Backend P1s fixed; ≤ 3 P1s open across all pods.

**Task:** Complete DM-15 (final architecture diagram + ADR index): update the architecture diagram (W20 v1) to reflect the actual code (any changes since W20 — multi-doc RAG, KG, cognitive model, adaptive engine, analytics, admin, notifications). Update the ADR index `docs/adr/README.md` to list all 18 ADRs with status. Publish to Docusaurus.
**Why:** Roadmap DM-15 (W41) requires "Final architecture diagram + ADR index; Updated to reflect actual code." Roadmap §Gate 5 sign-off criterion #7.
**Expected Output:** Final architecture diagram; ADR index.
**Dependencies:** All W1–W40 work.
**Handoff:** TPM publishes; all engineers reference.
**Definition of Done:** Diagram reflects actual code; ADR index complete; published.

**Task:** Support the DR drill: participate in Pod D's DR drill — verify DB restore, Qdrant restore, Neo4j restore, MinIO restore. Time the restore (RTO target < 1h). Document any issues.
**Why:** Roadmap W41 sprint requires "backup + DR drill; restore DB from backup; verify; DR drill completes < 1h." Roadmap §Gate 5 sign-off criterion #6.
**Dependencies:** Runbooks (Pod D W39); backups (ongoing).
**Handoff:** Pod D runs the drill; Pod A supports.
**Definition of Done:** DR drill completes < 1h; all data restored; report committed.

#### AI/ML & Data Pod

##### Objective
Fix AI/ML bugs from bash #2. Finalize the RAG eval + adaptation eval baselines. Support the fallback demo video.

##### Tasks

**Task:** Fix AI/ML bugs from bash #2: triage AI/ML bugs. Fix P1s. Verify RAG eval + adaptation eval still pass after fixes. Re-run baselines.
**Why:** Roadmap W41 sprint requires closing bugs.
**Expected Output:** Bug fixes; updated eval baselines.
**Dependencies:** Bug bash #2 results (Pod D W41); eval harnesses (W15, W33).
**Handoff:** Pod D verifies; TPM confirms.
**Definition of Done:** AI/ML P1s fixed; evals pass; baselines updated.

**Task:** Finalize the RAG eval + adaptation eval baselines for v1.0: run the final evals on the production-ready system. Document the v1.0 baseline metrics (faithfulness, relevance, mastery gain vs random). These are the graduation defense metrics.
**Why:** v1.0-rc is the Code Freeze candidate; baselines must be documented for the defense.
**Expected Output:** v1.0 AI/ML baseline metrics doc.
**Dependencies:** RAG eval (W15); adaptation eval (W33); production-ready system.
**Handoff:** TPM references in the graduation presentation (AI depth section).
**Definition of Done:** Baselines committed; metrics documented.

**Task:** Support the fallback demo video (GPM-9): provide the 5 known-good RAG questions (DDM-5) + demo student accounts (DDM-3) for the video recording. Be available during recording to handle any AI/ML issues.
**Why:** Roadmap GPM-9 (W41) requires "Fallback demo video recorded." Used if the live demo fails on graduation day.
**Dependencies:** Demo data (W38); 5 known-good questions (W36).
**Handoff:** Pod C-Lead records; Pod B-Lead supports.
**Definition of Done:** Fallback demo video recorded; AI/ML works throughout.

#### Frontend Pod

##### Objective
Fix frontend bugs from bash #2. Complete README polish + demo recording (DM-16). Record the fallback demo video (GPM-9).

##### Tasks

**Task:** Fix frontend bugs from bash #2: triage frontend bugs. Fix P1s. Verify E2E tests pass after fixes.
**Why:** Roadmap W41 sprint requires closing bugs.
**Expected Output:** Bug fixes; updated tests.
**Dependencies:** Bug bash #2 results (Pod D W41).
**Handoff:** Pod D verifies.
**Definition of Done:** Frontend P1s fixed; E2E tests pass.

**Task:** Complete DM-16 (README polish + demo recording): update `README.md` with final setup instructions, architecture overview, links to all docs (Docusaurus, ADRs, runbooks, quickstarts). Include badges (CI status, coverage, license). Record a 5-min demo video showcasing the v1.0 system.
**Why:** Roadmap DM-16 (W42 — but start W41 due to capacity recovery) requires "README polish + demo recording; `README.md` final + 5-min demo video." Roadmap §Gate 5 sign-off criterion #8.
**Expected Output:** Final `README.md`; 5-min demo video.
**Dependencies:** All W1–W40 work.
**Handoff:** TPM publishes; all engineers reference.
**Definition of Done:** README polished; demo video recorded; badges added.

**Task:** Record the fallback demo video (GPM-9): a full 8-minute demo using the demo script (GPM-5) + demo data. Record in 4K if possible (for the advisor's projection). Save to `docs/demo-videos/v1.0-fallback.mp4`. Upload to a backup location (Google Drive / GitHub Release).
**Why:** Roadmap GPM-9 (W41) requires "Fallback demo video recorded." Used if the live demo fails on graduation day (R-15 mitigation).
**Expected Output:** Fallback demo video.
**Dependencies:** Demo script v1 (W34); demo data (W38); staging environment.
**Handoff:** TPM uses as fallback on graduation day.
**Definition of Done:** Video recorded; uploaded; accessible.

#### DevOps / QA Pod

##### Objective
Run bug bash #2 (TM-14). Run the DR drill. Verify DDM-8 (demo data frozen). Continue on-call.

##### Tasks

**Task:** Run bug bash #2 (TM-14): 2-hour bash with all pod members. Scope: all user flows + edge cases + performance under load. Triage all findings. Target: ≤ 3 P1s open across all pods by EOD W41. Document in `docs/p5/tm-14-bug-bash-2.md`.
**Why:** Roadmap TM-14 (W41) requires "≤ 3 P1s open." Roadmap §Gate 5 sign-off criterion #2.
**Expected Output:** Bug bash #2 report; P1 count.
**Dependencies:** All W5–W40 work.
**Handoff:** Pod A + Pod B + Pod C fix P1s.
**Definition of Done:** ≤ 3 P1s open; report committed.

**Task:** Run the DR drill: simulate a production disaster — delete the staging DB, Qdrant collection, Neo4j data, MinIO bucket. Restore from backups using the runbooks. Time the restore (RTO target < 1h). Verify all data restored correctly. Document in `docs/p5/dr-drill-w41.md`.
**Why:** Roadmap W41 sprint requires "backup + DR drill; restore DB from backup; verify; DR drill completes < 1h." Roadmap §Gate 5 sign-off criterion #6.
**Expected Output:** DR drill report; RTO measured.
**Dependencies:** Runbooks (W39); backups (ongoing); staging environment.
**Handoff:** Pod A supports; TPM verifies.
**Definition of Done:** DR drill completes < 1h; all data restored; report committed.

**Task:** Verify DDM-8 (demo data frozen): confirm the demo data is frozen — no changes after W41. Document in `docs/p5/ddm-8-verification.md`. Lock the demo data in version control (a `demo-data-v1.0.tar.gz` committed to the repo or stored in MinIO with versioning).
**Why:** Roadmap DDM-8 (W42 — but verify W41) requires "Demo data frozen; no changes after this point." Roadmap §Gate 5 sign-off criterion #9.
**Expected Output:** DDM-8 verification doc; frozen demo data.
**Dependencies:** Demo data (W38).
**Handoff:** TPM confirms; no changes post-W41.
**Definition of Done:** Demo data frozen; lock documented; report committed.

#### Cross-Pod Integration

- **All Pods:** Bug bash #2 (TM-14); DR drill.
- **AI/ML ↔ TPM:** v1.0 AI/ML baseline metrics for the graduation defense.
- **DevOps/QA ↔ All Pods:** TM-14; DR drill; DDM-8 verification.
- **TPM ↔ All Pods:** DM-15 (architecture diagram + ADR index); DM-16 (README + demo video); GPM-9 (fallback video).

#### Week 41 Definition of Done

1. ≤ 3 P1s open across all pods (TM-14).
2. DM-15: final architecture diagram + ADR index published.
3. DR drill completes < 1h; all data restored.
4. v1.0 AI/ML baseline metrics committed.
5. Fallback demo video recorded (GPM-9).
6. DM-16: README polished + 5-min demo video recorded.
7. Bug bash #2 report committed.
8. DDM-8 verified: demo data frozen.
9. On-call W41 complete.

---

### Week 42 — v1.0-rc + Code Freeze + Dry-Run #1 with Advisor (GATE 5)

#### Roadmap Context

- **Phase:** P5 Hardening (final week)
- **Milestone:** **v1.0-rc + Code Freeze (GATE 5)** + dry-run #1 with advisor; TM-15 (smoke tests on prod-like env); GPM-10 (dry-run #1 with advisor)
- **Release:** v1.0-rc (tag `v1.0.0-rc`)
- **Primary Objective:** Ship v1.0-rc. Sign the Code Freeze (no new code merges except P0/P1 fixes with TPM + D-Lead approval). Run dry-run #1 with the advisor (GPM-10). Verify TM-15 (smoke tests on prod-like env).

#### Backend Pod

##### Objective
Ship v1.0-rc. Sign Code Freeze. Support dry-run #1.

##### Tasks

**Task:** Verify v1.0-rc: ensure the full system works on staging. Run all E2E + integration + unit tests. Verify all Gate 5 criteria (per Roadmap): v1.0-rc tagged + deployed to staging, bug bash #2 complete (≤ 3 P1s), security review complete (0 critical/high), performance pass complete (P95 < 2s), runbooks complete (DM-14), backup + DR drill complete, final architecture diagram + ADR index published (DM-15), README polished + demo recording (DM-16), demo data frozen (DDM-8).
**Why:** Roadmap v1.0-rc milestone (May 22, 2027 = W42) — Gate 5.
**Expected Output:** Validation report; any final fixes.
**Dependencies:** All W5–W41 work.
**Handoff:** TPM runs the W42 Friday demo (dry-run #1 with advisor).
**Definition of Done:** All Gate 5 criteria verified; v1.0-rc ready.

**Task:** Sign the Code Freeze: all pod leads + TPM sign `docs/gates/gate-5-code-freeze.md`. Post-freeze: no new code merges to `main` except critical fixes (P0/P1) with TPM + D-Lead approval + smoke tests re-run before + after merge. No new dependencies. No schema migrations. No infra changes.
**Why:** Roadmap Gate 5 sign-off. Code Freeze. Roadmap §Code Freeze: "No new code merges to `main` except critical fixes. No new dependencies. No schema migrations. No infra changes."
**Expected Output:** Signed sign-off doc; Code Freeze active.
**Dependencies:** All Gate 5 criteria met.
**Handoff:** TPM announces Code Freeze; P6 (Graduation) starts W43.
**Definition of Done:** All pod leads + TPM sign; Code Freeze active; post-freeze protocol enforced.

**Task:** Tag `v1.0.0-rc` on `main` after Friday demo + Code Freeze sign-off. Cut a GitHub Release with release notes referencing: full v1.0 feature set, performance (P95 < 2s under 50 users), security (0 critical/high), DR drill (< 1h RTO), runbooks, final architecture + ADR index, README + demo video, frozen demo data, all 18 ADRs.
**Why:** Roadmap v1.0-rc milestone — Gate 5.
**Expected Output:** Git tag `v1.0.0-rc`; GitHub Release published.
**Dependencies:** All W5–W42 DoD items + Gate 5 sign-off.
**Handoff:** TPM announces v1.0-rc; P6 (Graduation) starts W43.
**Definition of Done:** Tag exists; release notes complete; advisor notified.

#### AI/ML & Data Pod

##### Objective
Finalize v1.0 AI/ML. Support dry-run #1 with the advisor. Be available for any AI/ML issues during the dry-run.

##### Tasks

**Task:** Finalize v1.0 AI/ML: ensure the RAG + adaptive engine + recommendation engine + quiz generation all work reliably. Verify the eval baselines (W41) are reproducible. Be available during dry-run #1 to handle any AI/ML issues.
**Why:** v1.0-rc is the Code Freeze candidate; AI/ML must be stable.
**Expected Output:** Final AI/ML stability report.
**Dependencies:** All W31–W41 work.
**Handoff:** TPM references in dry-run #1.
**Definition of Done:** AI/ML stable; baselines reproducible; ready for dry-run.

**Task:** Participate in dry-run #1 (GPM-10) with the advisor: run the demo script (GPM-5) end-to-end. Collect advisor feedback on AI depth (RAG eval results, adaptation examples, what worked, what didn't). Incorporate feedback into the demo script + slide deck.
**Why:** Roadmap GPM-10 (W42) requires "Dry-run #1 with advisor; Collect advisor feedback; refine deck and script."
**Expected Output:** Dry-run #1 feedback; updated demo script + deck.
**Dependencies:** Demo script v1 (W34); demo data (W38); slide deck v1 (W36).
**Handoff:** TPM continues to deck v2 at W43 (GPM-11).
**Definition of Done:** Dry-run completed; feedback incorporated.

#### Frontend Pod

##### Objective
Finalize v1.0 UI. Support dry-run #1. Polish the demo flow.

##### Tasks

**Task:** Finalize v1.0 UI: ensure all UI surfaces are polished + accessible. Verify Lighthouse scores (performance ≥ 80, a11y ≥ 90). Be available during dry-run #1 to handle any UI issues.
**Why:** v1.0-rc is the Code Freeze candidate; UI must be polished.
**Expected Output:** Final UI stability report.
**Dependencies:** All W5–W41 work.
**Handoff:** TPM references in dry-run #1.
**Definition of Done:** UI stable; Lighthouse scores met; ready for dry-run.

**Task:** Polish the demo flow: based on dry-run #0 (W40) + dry-run #1 (W42) feedback, polish the demo flow. Ensure transitions between demo beats are smooth. Verify the demo script (GPM-5) is executable end-to-end without errors.
**Why:** Dry-run feedback incorporation.
**Expected Output:** Polished demo flow; updated demo script.
**Dependencies:** Dry-run #0 (W40) + #1 (W42) feedback.
**Handoff:** TPM uses for dry-run #2 (W43) + #3 (W44).
**Definition of Done:** Demo flow polished; script executable.

#### DevOps / QA Pod

##### Objective
Verify TM-15 (smoke tests on prod-like env). Run dry-run #1 (GPM-10). Sign Code Freeze.

##### Tasks

**Task:** Verify TM-15 (smoke tests on prod-like env): run all smoke tests on the prod-like environment (W40 DDM-7). Verify all critical paths (login, register, upload, chat, quiz, mastery, recommendation, analytics, admin) are green. Document in `docs/p5/tm-15-smoke-tests.md`.
**Why:** Roadmap TM-15 (W42) requires "Smoke tests on prod-like env; All critical paths green." Roadmap §Gate 5 sign-off.
**Expected Output:** TM-15 smoke test report.
**Dependencies:** Prod-like env (W40); demo data (W38).
**Handoff:** TPM includes in Gate 5 sign-off.
**Definition of Done:** All critical paths green; report committed.

**Task:** Run dry-run #1 (GPM-10) with the advisor: coordinate the dry-run. TPM runs the demo script. All pod members attend. Collect advisor feedback. Document in `docs/p5/dry-run-1-w42.md`.
**Why:** Roadmap GPM-10 (W42) requires "Dry-run #1 with advisor."
**Expected Output:** Dry-run #1 report; feedback log.
**Dependencies:** Demo script (W34); demo data (W38); slide deck v1 (W36); advisor availability.
**Handoff:** TPM incorporates feedback; continues to dry-run #2 (W43).
**Definition of Done:** Dry-run completed; feedback documented; fixes scheduled for W43.

**Task:** Sign the Code Freeze: finalize `docs/gates/gate-5-code-freeze.md` with all 10 Gate 5 criteria verified. All pod leads + TPM sign.
**Why:** Roadmap Gate 5 sign-off.
**Expected Output:** Signed sign-off doc.
**Dependencies:** All W5–W42 work.
**Handoff:** TPM announces Code Freeze; P6 starts W43.
**Definition of Done:** All pod leads + TPM sign; Code Freeze active.

#### Cross-Pod Integration

- **All Pods:** v1.0-rc + Code Freeze sign-off. All Gate 5 criteria verified.
- **TPM ↔ All Pods:** Dry-run #1 with advisor; feedback incorporated.
- **DevOps/QA ↔ All Pods:** TM-15 sign-off; Code Freeze sign-off.
- **End-to-end (v1.0-rc):** Production-ready system on prod-like env; advisor dry-run #1.

#### Week 42 Definition of Done

1. **v1.0.0-rc tagged; Gate 5 (Code Freeze) signed by all pod leads + TPM.**
2. All 10 Gate 5 criteria verified.
3. Code Freeze active: no new code merges except P0/P1 with TPM + D-Lead approval.
4. TM-15 met: smoke tests green on prod-like env.
5. Dry-run #1 (GPM-10) with advisor completed; feedback incorporated.
6. v1.0 AI/ML baseline stable + reproducible.
7. UI finalized; Lighthouse scores met.
8. Demo flow polished based on dry-run feedback.
9. Friday demo (v1.0-rc dry-run #1) passes with advisor.
10. P6 (Graduation) starts W43 with Code Freeze active. 0 weeks of critical-path slack remaining (hard).

---



### Week 43 — Production Deployment + Dry-Run #2 + Slide Deck v2

#### Roadmap Context

- **Phase:** P6 Graduation
- **Milestone:** Production deployment + dry-run #2; IM-15 (Production deployment end-to-end); GPM-11 (slide deck v2 + dry-run #2 + prod deployment stable)
- **Release:** v1.0 prep
- **Primary Objective:** Deploy v1.0-rc to production (public URL with TLS). Verify IM-15. Run dry-run #2 with advisor (GPM-11). Finalize slide deck v2. Capacity is at full push (~160 hrs/wk effective).

#### Backend Pod

##### Objective
Deploy v1.0-rc to production. Verify the production deployment. Be on standby for hotfixes.

##### Tasks

**Task:** Deploy v1.0-rc to production: provision the prod environment (per the W31 admin API design + W39 deploy runbook). Configure DNS (the public URL). Configure TLS (Let's Encrypt or cloud provider). Deploy Docker Compose / k3s stack (FastAPI, Next.js, Postgres, Redis, Qdrant, Neo4j, MinIO, LiteLLM, Langfuse, Grafana stack). Run smoke tests on prod. Load the frozen demo data (DDM-8).
**Why:** Roadmap W43 sprint requires "Production deployment + dry-run #2; Deploy v1.0-rc to prod; smoke tests; DNS + TLS; dry-run #2." Roadmap IM-15 (W43) requires "Production deployment end-to-end; v1.0 live on prod URL."
**Expected Output:** Production deployment; public URL accessible; smoke tests pass.
**Dependencies:** v1.0-rc (W42); deploy runbook (W39); frozen demo data (W41); DNS + TLS config.
**Handoff:** TPM announces the prod URL; advisor + graduation committee notified.
**Definition of Done:** Prod URL accessible from outside the team; HTTPS enforced; smoke tests pass; demo data loaded.

**Task:** Be on hotfix standby: monitor production for any P0/P1 issues. If any surface, apply hotfixes per the Code Freeze exception protocol (TPM + D-Lead approval; smoke tests re-run before + after merge). Document any hotfixes in `docs/p6/hotfixes-w43.md`.
**Why:** Roadmap §Code Freeze: "Critical bug fixes (P0/P1) with TPM + D-Lead approval." Production deployment may surface issues not caught in staging.
**Expected Output:** Hotfix log (if any).
**Dependencies:** Prod deployment (above); on-call rotation.
**Handoff:** Pod D monitors; Pod A applies hotfixes.
**Definition of Done:** No P0/P1 issues (or hotfixes applied + documented).

#### AI/ML & Data Pod

##### Objective
Verify AI/ML works on production. Support dry-run #2. Be on standby for hotfixes.

##### Tasks

**Task:** Verify AI/ML works on production: run the 5 known-good RAG questions (DDM-5) on prod. Verify the RAG + adaptive engine + recommendation engine + quiz generation all work. Compare to staging baselines (W41). Document in `docs/p6/prod-ai-ml-verification-w43.md`.
**Why:** Production environment may differ from staging (different hardware, network, LLM API latency). AI/ML must work on prod.
**Expected Output:** Prod AI/ML verification report.
**Dependencies:** Prod deployment (Pod A W43); 5 known-good questions (W36).
**Handoff:** TPM verifies at dry-run #2.
**Definition of Done:** AI/ML works on prod; baselines within 10% of staging.

**Task:** Support dry-run #2 (GPM-11): participate in the dry-run with the advisor. Run the demo script (GPM-5, updated post-W42). Be available to handle any AI/ML issues during the dry-run.
**Why:** Roadmap GPM-11 (W43) requires "Dry-run #2; Timing tuned; prod deployment stable."
**Dependencies:** Prod deployment (Pod A W43); demo script (W42).
**Handoff:** TPM collects feedback; continues to dry-run #3 (W44).
**Definition of Done:** Dry-run #2 completed; AI/ML stable throughout.

**Task:** Be on hotfix standby: monitor AI/ML on prod. If any P0/P1 issues (e.g., RAG quality drops, adaptive engine fails), apply hotfixes per the Code Freeze exception protocol.
**Why:** Production AI/ML may surface issues.
**Expected Output:** Hotfix log (if any).
**Dependencies:** Prod deployment (Pod A W43).
**Handoff:** Pod D monitors via Grafana.
**Definition of Done:** No P0/P1 AI/ML issues (or hotfixes applied).

#### Frontend Pod

##### Objective
Verify the frontend works on production. Finalize slide deck v2 (GPM-11). Support dry-run #2.

##### Tasks

**Task:** Verify the frontend works on production: run Lighthouse on prod critical paths. Verify SSR, bundle size, accessibility. Compare to staging. Document any issues.
**Why:** Production may have different CDN, TLS, DNS configuration that affects frontend performance.
**Expected Output:** Prod frontend verification report.
**Dependencies:** Prod deployment (Pod A W43).
**Handoff:** Pod A addresses any issues.
**Definition of Done:** Lighthouse scores met on prod; no issues.

**Task:** Finalize slide deck v2 (GPM-11): incorporate dry-run #1 (W42) feedback. Finalize all slides (15+). Add the "what worked, what didn't" section (Roadmap §Presentation Structure #6 — non-negotiable). Time the presentation to 30 minutes. Review with TPM.
**Why:** Roadmap GPM-11 (W43) requires "Slide deck v2."
**Expected Output:** Slide deck v2.
**Dependencies:** Slide deck v1 (W36); dry-run #1 feedback (W42).
**Handoff:** TPM uses for dry-run #2 (W43) + #3 (W44).
**Definition of Done:** Deck v2 finalized; 30-minute timing; "what worked, what didn't" section included.

**Task:** Support dry-run #2: participate in the dry-run. Run the UI portion of the demo. Be available to handle any UI issues.
**Why:** Dry-run #2 is the final rehearsal before graduation.
**Dependencies:** Prod deployment (Pod A W43); demo script (W42).
**Handoff:** TPM collects feedback.
**Definition of Done:** Dry-run #2 completed; UI stable throughout.

#### DevOps / QA Pod

##### Objective
Deploy + monitor production. Run dry-run #2. Verify IM-15. On-call for graduation.

##### Tasks

**Task:** Deploy + monitor production (with Pod A): execute the deploy runbook. Configure monitoring (Grafana dashboards + alerts on prod). Verify the prod environment is stable. Document in `docs/p6/prod-deployment-w43.md`.
**Why:** Roadmap W43 sprint requires prod deployment.
**Expected Output:** Prod deployment report; monitoring configured.
**Dependencies:** Deploy runbook (W39); v1.0-rc (W42).
**Handoff:** TPM verifies; on-call monitors.
**Definition of Done:** Prod deployed; monitoring live; stable.

**Task:** Verify IM-15 (production deployment end-to-end): confirm v1.0-rc is live on the prod URL. Run smoke tests. Verify DNS + TLS. Document in `docs/p6/im-15-verification.md`.
**Why:** Roadmap IM-15 (W43) requires "Production deployment end-to-end; v1.0 live on prod URL."
**Expected Output:** IM-15 verification doc.
**Dependencies:** Prod deployment (above).
**Handoff:** TPM announces; advisor + committee notified.
**Definition of Done:** Prod URL live; smoke tests pass; verification committed.

**Task:** Run dry-run #2 (GPM-11) with the advisor: coordinate the dry-run. TPM runs the demo script + slide deck v2. All pod members attend. Collect advisor feedback. Tune timing. Document in `docs/p6/dry-run-2-w43.md`.
**Why:** Roadmap GPM-11 (W43) requires "Dry-run #2; Timing tuned; prod deployment stable."
**Expected Output:** Dry-run #2 report; feedback log; timing adjustments.
**Dependencies:** Prod deployment (above); demo script (W42); slide deck v2 (Pod C W43); advisor availability.
**Handoff:** TPM incorporates feedback; continues to dry-run #3 (W44, dress rehearsal).
**Definition of Done:** Dry-run completed; feedback documented; timing tuned.

**Task:** On-call for graduation: Pod D is on-call throughout W43 + W44. Monitor prod for any issues. Be ready to apply hotfixes or invoke the fallback demo video (GPM-9) if needed.
**Why:** Graduation day is W44; prod must be stable.
**Dependencies:** Prod deployment (above); fallback demo video (W41).
**Handoff:** Pod D continues on-call through W44.
**Definition of Done:** Prod stable throughout W43; on-call ready.

#### Cross-Pod Integration

- **All Pods:** Production deployment (IM-15). Dry-run #2 (GPM-11).
- **DevOps/QA ↔ All Pods:** Deploy + monitor; dry-run coordination.
- **TPM ↔ All Pods:** Slide deck v2 (GPM-11); dry-run #2.
- **End-to-end (IM-15):** v1.0-rc live on prod URL; smoke tests pass.

#### Week 43 Definition of Done

1. v1.0-rc deployed to production (public URL, TLS, monitoring).
2. IM-15 verified: prod URL live; smoke tests pass.
3. AI/ML works on prod; baselines within 10% of staging.
4. Frontend works on prod; Lighthouse scores met.
5. Slide deck v2 finalized (GPM-11); 30-minute timing; "what worked, what didn't" section.
6. Dry-run #2 with advisor completed; feedback incorporated; timing tuned.
7. No P0/P1 issues on prod (or hotfixes applied).
8. Pod D on-call for graduation; monitoring active.
9. Friday demo (dry-run #2) passes with advisor.
10. Ready for W44 (dress rehearsal + graduation).

---

### Week 44 — Dry-Run #3 + v1.0 + Graduation Presentation

#### Roadmap Context

- **Phase:** P6 Graduation (final week)
- **Milestone:** Dry-run #3 (dress rehearsal) + **v1.0 + graduation presentation**; GPM-12 (dry-run #3 + submit artifacts)
- **Release:** v1.0 (tag `v1.0.0`)
- **Primary Objective:** Run the dress rehearsal (dry-run #3). Tag v1.0. Deliver the graduation presentation. Submit all artifacts. Capacity is at full push (~160 hrs/wk).

#### Backend Pod

##### Objective
Tag v1.0. Be on standby during the graduation presentation. Ensure prod is stable.

##### Tasks

**Task:** Tag `v1.0.0` on `main` after the dress rehearsal (dry-run #3) passes. Cut the final GitHub Release with release notes referencing: the full v1.0 system, production deployment, all 18 ADRs, all 10 frozen interface contracts, runbooks, documentation, demo data, graduation presentation. This is the final tag.
**Why:** Roadmap v1.0 milestone (Jun 5, 2027 = W44) — **Final**.
**Expected Output:** Git tag `v1.0.0`; GitHub Release published.
**Dependencies:** Dry-run #3 passes (W44); Code Freeze (W42).
**Handoff:** TPM announces v1.0; graduation committee notified.
**Definition of Done:** Tag exists; release notes complete; final.

**Task:** Be on standby during the graduation presentation: monitor prod. If any P0/P1 issue surfaces during the live demo, apply a hotfix immediately (or invoke the fallback demo video — GPM-9). Have the rollback runbook ready.
**Why:** Roadmap R-15 (production deployment fails on graduation day, score 10) mitigation. Fallback demo video (GPM-9, W41) is the last resort.
**Expected Output:** Standby log; hotfix or fallback invocation if needed.
**Dependencies:** Prod deployment (W43); fallback demo video (W41); rollback runbook (W39).
**Handoff:** Pod D coordinates; Pod A applies hotfixes.
**Definition of Done:** Presentation delivered without prod issues (or fallback invoked successfully).

#### AI/ML & Data Pod

##### Objective
Be on standby during the presentation. Ensure AI/ML works during the live demo. Finalize the AI depth section of the presentation.

##### Tasks

**Task:** Be on standby during the graduation presentation: monitor AI/ML on prod. If the RAG fails during the live demo (e.g., LLM API rate limit, retrieval quality drops), be ready to switch to the fallback demo video (GPM-9) or use the 5 known-good questions (DDM-5) which are pre-verified.
**Why:** R-15 mitigation. Live demos are risky; AI/ML is the highest-risk component.
**Expected Output:** Standby log.
**Dependencies:** Prod deployment (W43); 5 known-good questions (W36); fallback demo video (W41).
**Handoff:** Pod D coordinates.
**Definition of Done:** AI/ML works throughout the presentation (or fallback invoked).

**Task:** Finalize the AI depth section of the presentation: deliver the 5-minute "AI depth" section (RAG eval results, adaptation examples, what worked, what didn't). Reference the v1.0 AI/ML baselines (W41). Be honest about failures (Roadmap §Presentation Structure: "advisors respect honesty about failures more than claims of perfection").
**Why:** Roadmap §Presentation Structure #5: "AI depth — RAG eval results; adaptation examples; what worked, what didn't."
**Expected Output:** Finalized AI depth section.
**Dependencies:** v1.0 AI/ML baselines (W41); slide deck v2 (W43).
**Handoff:** Pod B-Lead delivers this section during the presentation.
**Definition of Done:** Section finalized; honest about failures; 5-minute timing.

#### Frontend Pod

##### Objective
Be on standby during the presentation. Ensure the UI works during the live demo. Finalize the demo flow.

##### Tasks

**Task:** Be on standby during the graduation presentation: monitor the frontend on prod. If any UI issue surfaces during the live demo (e.g., page doesn't load, SSE stream fails), be ready to switch to the fallback demo video (GPM-9).
**Why:** R-15 mitigation.
**Expected Output:** Standby log.
**Dependencies:** Prod deployment (W43); fallback demo video (W41).
**Handoff:** Pod D coordinates.
**Definition of Done:** UI works throughout the presentation (or fallback invoked).

**Task:** Finalize the demo flow: ensure the 8-minute live demo (Roadmap §Presentation Structure #4) is rehearsed + polished. Use the demo script (GPM-5, updated through W43) + demo data (DDM-8, frozen). Practice transitions between demo beats.
**Why:** Roadmap §Presentation Structure #4: "Live demo — student flow + instructor flow + analytics + adaptation."
**Expected Output:** Finalized demo flow.
**Dependencies:** Demo script (W43); demo data (W41); slide deck v2 (W43).
**Handoff:** Pod C-Lead delivers the demo during the presentation.
**Definition of Done:** Demo flow finalized; 8-minute timing; transitions smooth.

#### DevOps / QA Pod

##### Objective
Run dry-run #3 (dress rehearsal). Submit all graduation artifacts. Be on-call during the presentation.

##### Tasks

**Task:** Run dry-run #3 (GPM-12, dress rehearsal): full rehearsal with all pod members + advisor (if available). Run the entire 30-minute presentation + 8-minute demo. Time every section. Identify any remaining issues. Apply final fixes (Code Freeze exceptions require TPM + D-Lead approval). Document in `docs/p6/dry-run-3-w44.md`.
**Why:** Roadmap GPM-12 (W44) requires "Dry-run #3 (dress rehearsal); submit artifacts."
**Expected Output:** Dry-run #3 report; final fixes.
**Dependencies:** Slide deck v2 (W43); demo script (W43); prod deployment (W43); all pod members.
**Handoff:** TPM incorporates any final feedback; ready for the actual presentation.
**Definition of Done:** Dry-run #3 completed; all sections timed; no critical issues; ready for presentation.

**Task:** Submit all graduation artifacts: (1) code repository (GitHub, tagged v1.0.0), (2) documentation (Docusaurus site, ADRs, runbooks, quickstarts), (3) presentation (slide deck v2, demo script), (4) demo video (5-min + fallback), (5) production deployment (public URL), (6) any other artifacts required by the graduation committee. Document submission in `docs/p6/artifact-submission-w44.md`.
**Why:** Roadmap §Graduation Success criterion #5: "All graduation artifacts (code, docs, presentation, demo video) are submitted." Roadmap GPM-12.
**Expected Output:** Artifact submission report; confirmation from the committee.
**Dependencies:** All W1–W44 work.
**Handoff:** TPM confirms submission; committee acknowledges.
**Definition of Done:** All artifacts submitted; committee confirms receipt.

**Task:** Be on-call during the graduation presentation: monitor prod. Be ready to invoke the fallback demo video (GPM-9) if the live demo fails. Have the rollback runbook ready. Coordinate with Pod A (hotfixes) + Pod B (AI/ML) + Pod C (UI) for any issues.
**Why:** R-15 mitigation. The presentation is the culmination; prod must be stable.
**Dependencies:** Prod deployment (W43); fallback demo video (W41); rollback runbook (W39).
**Handoff:** Pod D coordinates; all pods on standby.
**Definition of Done:** Presentation delivered without prod issues (or fallback invoked successfully).

#### Cross-Pod Integration

- **All Pods:** Dry-run #3 (dress rehearsal). Graduation presentation delivery. Standby for any issues.
- **DevOps/QA ↔ All Pods:** Dry-run #3 coordination; artifact submission; on-call during presentation.
- **TPM ↔ All Pods:** v1.0 tag; artifact submission; presentation delivery.
- **End-to-end (v1.0):** Production deployment live; presentation delivered; artifacts submitted. **Graduation success.**

#### Week 44 Definition of Done

1. Dry-run #3 (dress rehearsal) completed; all sections timed; no critical issues.
2. **v1.0.0 tagged; final GitHub Release published.**
3. All graduation artifacts submitted (code, docs, presentation, demo video, prod URL).
4. Graduation presentation delivered (30 min + 8-min demo).
5. Live demo works on prod (or fallback demo video invoked).
6. AI depth section delivered (honest about failures).
7. Pod D on-call throughout; no prod issues (or fallback invoked).
8. All Gate 1–5 criteria were met on schedule.
9. All 44 weeks of the plan executed.
10. **Graduation delivered. 🎓**

---



## 6. 44-Week Master Summary

This table is a concise overview. The detailed weekly sections (Section 5) remain the authoritative task definitions. "Focus" columns summarize the headline task per pod per week; consult the weekly section for the full task breakdown (Task / Why / Expected Output / Dependencies / Handoff / Definition of Done).

| Week | Phase | Milestone | Backend Focus | AI/ML & Data Focus | Frontend Focus | DevOps/QA Focus | Integration Goal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W1 | P0 | Kickoff + stack lock | FastAPI skeleton; Alembic init; ADRs 1–5 draft | PAL skeleton; 20-PDF golden set; LiteLLM plan | Next.js 16 skeleton; shadcn/ui; Storybook | CI scaffold; 3 envs; risk register seeded | Repo + CI + envs + OOS signed |
| W2 | P0 | MVP sign-off + skeletons | OpenAPI; SQLAlchemy async; auth scaffold | OCR/embedding spike methodologies; demo PDF chosen | Design tokens; Next.js staging deploy | Eval harness scaffold; pytest + Vitest configured | MVP doc signed; staging URLs reachable |
| W3 | P0 | Hello world on real URL | `users` migration; FastAPI deploy; auth scaffold | OCR/embedding installs; demo PDF smoke test | Next.js Dockerfile; app shell route groups | Staging deploy workflow; PG provisioned | Both apps deployed to staging HTTPS |
| W4 | P0 | ADRs + risk register + v0.1 | ADRs 1–5 merged; CONTRIBUTING; tech debt register | Spike template; LiteLLM pre-pull; demo PDF smell test | Login page; Storybook + Chromatic | Eval harness in CI; risk register v1; v0.1 tag | **v0.1 tagged** |
| W5 | P1 | Auth + OCR/embedding spikes | Register/login/JWT; ADR-006 draft | OCR spike; embedding spike; PaddleOCRProvider | Register/login pages; protected routes | Redis + Celery + Flower; Loki/Prometheus/Sentry | Auth works on staging; spikes produce ADRs |
| W6 | P1 | User mgmt + Course CRUD + v0.1 | Profile CRUD; RBAC; course CRUD; file upload | Tesseract + DocAI providers; BGE + OpenAI providers; LiteLLM provider | Course list/create/edit; profile page | MinIO; Grafana dashboard; v0.1 tag (if not W4) | **v0.1 tagged; IM-1 (auth ↔ DB)** |
| W7 | P1 | Async jobs + observability + LLM gateway | Async enqueue; WS progress; materials list | OCR worker skeleton; chunking refinement; ADR-009 | App shell; course detail page | LiteLLM gateway deploy; Langfuse; async pipeline tests | LLM gateway live; async jobs work |
| W8 | P1 | Integration + v0.2 | IM-2 integration; ADR-006 freeze (Contract 10); API reference | OCR worker 5-PDF smoke; RAG eval harness design; ADR-010 | Docusaurus; upload UI polish; E2E test | TM-2 (≥80% auth+course coverage); v0.2 tag; cross-training | **v0.2 tagged; IM-2; Contract 10 frozen** |
| W9 | P2 | OCR pipeline v1 | `documents` table; `/v1/documents/{id}`; Qdrant prep | OCR pipeline v1; WS event; chunking refinement | Extracted text viewer; chat UI scaffold | OCR integration tests (5 PDFs); Qdrant backup script; cross-training | OCR pipeline processes 5 PDFs end-to-end |
| W10 | P2 | OCR hardening + document model | Idempotency; documents metadata; chunks table | 20-PDF golden set; Document AI escalation; Arabic preprocessing | Citation component; chat message list | OCR integration in CI; OCR quality dashboard | ≥90% OCR success on 20-PDF golden set |
| W11 | P2 | Chunking strategy + ADR | `/v1/documents/{id}/chunks`; embedding batch prep; OCR doc | ADR-009 accepted; chunking doc; embedding batch skeleton | Chunks viewer; source panel | Chunking metrics; baseline load test | Chunking strategy frozen (ADR-009) |
| W12 | P2 | v0.3 + embedding batch | v0.3 demo flow; Qdrant deploy; Qdrant provider | Embedding batch job (1000 chunks); TM-3; hybrid retrieval design | Chat input component; v0.3 demo polish | TM-3 sign-off; cost monitoring; cross-training | **v0.3 tagged; 1000 chunks embedded** |
| W13 | P2 | Vector DB + search API | `/v1/search`; embedding write path; ADR-011 | IM-4 verification; BM25; reranker provider | Search UI; chat session list | Qdrant monitoring; full pipeline CI test; cross-training | IM-4: full ingestion pipeline end-to-end |
| W14 | P2 | Hybrid retrieval + reranker | `/v1/retrieve`; chat API design | Hybrid retrieval (BM25+vector); reranker; RAG prompt design; quality baseline | Streaming chat message; source panel integration | Retrieval quality dashboard; Langfuse tracing | Hybrid retrieval beats pure vector |
| W15 | P2 | RAG prompt + eval harness + IM-5 | `/v1/rag/query`; chat API skeleton; RAG doc | RAG service; RAG eval harness v1 (50 Q&A); IM-5; DDM-1 | Citation rendering wired; chat UI polish | TM-4 (RAG eval in CI); RAG load test; RAG quality dashboard | IM-5: query returns cited answer via curl |
| W16 | P2 | **v0.4 Thin MVP (GATE 1)** | Thin MVP endpoint; deploy; v0.4 tag | PB-02 check; RAG iteration; 5 demo questions | Chat UI wired to thin MVP; polish | Gate 1 validation; demo monitoring; smoke test | **v0.4 tagged; GATE 1 signed** |
| W17 | P2 | Full chat API + E2E | Full chat API (SSE); sessions API; IM-7 | Streaming LLM; PB-02 fixes; multi-doc design | Chat UI wired; session list; student flow polish | TM-5 (E2E test); chat API monitoring; integration tests | IM-7: full student flow E2E green |
| W18 | P2 | Multi-doc RAG + Tier 1 draft | Multi-doc API; ADRs 12–15; Tier 1 contracts | Multi-doc retrieval; multi-doc eval; ADRs 7–11 accepted | Multi-doc citations; chat polish | TM-6 prep; Tier 1 freeze review prep | Multi-doc RAG works; ADRs 1–15 ready |
| W19 | P2 | Polish + Tier 1 review | Top-10 backend bugs; ADRs merged; contracts final | Top-5 AI/ML bugs; RAG doc final; 5 multi-doc questions | Top-5 frontend bugs; v0.5 polish | E2E re-run; TM-6 sign-off; Tier 1 sign-off doc | Bug count ≤ 5 P1s; Tier 1 ready |
| W20 | P2 | **v0.5 + Tier 1 Freeze (GATE 2)** | v0.5 demo; Tier 1 sign; architecture diagram; v0.5 tag | Final RAG eval; DDM-1 confirm; KG design; GPM-0 | v0.5 demo UI; KG viz research; demo video | TM-6 sign-off; v0.5 validation; on-call prep | **v0.5 tagged; GATE 2 signed; 22-week graduation runway begins** |
| W21 | P3 | KG schema ADR + demo backlog | KG API design; light maintenance | ADR-016 (KG schema); concept extraction spike prep; graduation outline | KG viz skeleton; light maintenance | Neo4j deploy prep; on-call; cross-training | KG schema frozen (ADR-016) |
| W22 | P3 | Concept extraction spike + outline v0 | KG API skeleton; light maintenance | Concept extraction spike; ADR-017 draft; outline v0 final | Concept detail view; light maintenance | Neo4j deploy; on-call; cross-training | Spike produces recommendation |
| W23 | P3 | Concept extraction pipeline + Neo4j | KG API full; KG worker Neo4j writes | Extraction pipeline; 200+ concepts; DM-10 (KG doc) | Relations list; KG viz API prep | TM-7 prep (KG sanity); Neo4j monitoring; cross-training | KG populated with 200+ concepts |
| W24 | P3 | KG API + KG viz + demo dataset v1 | KG API final; DDM-2 ingestion; IM-8 verification | KG retrieval boost design; extraction refinement; GPM-1 | KG viz UI shipped; demo materials list | TM-7 sign-off; DDM-2 verification; cross-training | IM-8: KG populated from new upload; KG browsable |
| W25 | P3 | KG retrieval boost + cognitive spike | Quiz API design; light capacity | KG-backed retrieval boost (faithfulness ↑5%); cognitive spike begins; quiz gen design | Quiz UI design; KG viz polish | Retrieval boost metrics; exam crunch comms (PB-05); cross-training | KG retrieval boost ships; spike starts |
| W26 | P3 | v0.6 + quiz UI + cognitive spike | Quiz API; v0.6 tag | Quiz generation v1; cognitive spike continues | Quiz-taking UI; instructor quiz creation | Quiz generation monitoring; on-call | **v0.6 tagged; quiz works** |
| W27 | P3 | Cognitive spike concludes + mastery v1 | Mastery schema; mastery update hook | ADR-017 accepted; mastery estimator v1 (WMA); DM-11 | Mastery UI skeleton; quiz polish | Mastery monitoring; PB-05 status; cross-training | ADR-017 accepted; mastery updates on quiz |
| W28 | P3 | Quiz E2E + mastery UI + hardening | IM-10 integration; cohort mastery; BKT scaffold | Cognitive hardening; adaptive spike prep; quiz pool | Mastery UI shipped; cohort mastery view | TM-8 (E2E); concurrency test; cross-training | IM-10: quiz → mastery E2E; TM-8 green |
| W29 | P3 | Cognitive hardening + adaptive spike + mastery UI | Tier 2 contracts; recommendation API design; analytics design | Adaptive spike; cognitive hardening final; quiz pool | Mastery UI polish; recommendation UI skeleton | Tier 2 freeze prep; cross-training | Tier 2 contracts ready; adaptive spike running |
| W30 | P3 | **v0.7 + Tier 2 Freeze (GATE 3)** | v0.7 demo; Tier 2 sign; DDM-3; v0.7 tag | ADR-018 draft; adaptive spike continues; GPM-3 | v0.7 demo UI; recommendation UI design | Tier 2 sign-off; v0.7 validation; DDM-3 verification | **v0.7 tagged; GATE 3 signed; contracts 6–9 frozen** |
| W31 | P4 | Adaptive engine + ADR-018 | Recommendation API; review schedule; admin API design | Adaptive engine productionized; ADR-018 accepted; SM-2; DM-12 | Recommendation UI; slide deck template | Adaptive monitoring; adaptation eval prep; cross-training | Adaptive engine ships; ADR-018 accepted |
| W32 | P4 | Recommendation API + UI + difficulty | Adaptive quiz endpoint; analytics queries | Difficulty adjustment; adaptation eval harness; quiz pool | Recommendation UI shipped (IM-11); adaptive quiz UI; slides 6–10 | Monitoring; cross-training | IM-11: recommendation shown to student |
| W33 | P4 | Recommendation engine v1 + adaptation eval | Recommendation engine v1; IM-12 debug field | TM-9 (adaptation eval); quiz pool 100+; demo script skeleton | Top-3 recommendations; adaptive quiz polish; slides 11–15 | IM-12 verification; recommendation monitoring; cross-training | IM-12: quiz difficulty adapts; TM-9 met |
| W34 | P4 | Analytics dashboard + v0.8 | Analytics endpoints final; IRT decision; v0.8 tag | DDM-4 (quiz pool); GPM-5 (demo script v1); IRT eval | Analytics dashboard UI (4 charts); v0.8 demo video | DDM-4 verification; analytics monitoring; cross-training | **v0.8 tagged; analytics dashboard works** |
| W35 | P4 | Admin dashboard + notifications | Admin API; notification system; IM-13 verification | Recommendation iteration; DDM-5 prep; quiz pool maintenance | Admin dashboard UI; notification bell; v0.9 polish | Admin monitoring; bug bash #1 prep; cross-training | IM-13: analytics ↔ real DB data |
| W36 | P4 | UX polish + bug bash #1 + demo script v2 | Top backend bugs; DM-13 (quickstarts) | DDM-5 validation; GPM-6 (deck v1 advisor); recommendation iteration | UX polish; top frontend bugs | TM-10 (bug bash #1); DDM-5 verification; Feature Freeze prep | TM-10 met; 50+ bugs triaged |
| W37 | P4 | Bug fixing + accessibility + demo dataset | P1 closure; DB perf prep | P1 closure; recommendation final; DDM-6 prep | P1 closure; WCAG 2.1 AA pass | P1 closure verification; accessibility validation; Feature Freeze prep | 0 P1s; axe-core clean |
| W38 | P4 | **v0.9 + Feature Freeze (GATE 4)** | v0.9 demo; Feature Freeze sign; DDM-6 export; v0.9 tag | v1.0 AI/ML baselines; GPM-7 (demo data curated) | v0.9 demo UI; P5 docs prep | TM-11 (≥60% coverage); DDM-6 verification; v0.9 validation; Feature Freeze sign | **v0.9 tagged; GATE 4 signed; Feature Freeze active** |
| W39 | P5 | Perf pass + DB optimization | Backend optimization; caching | RAG pipeline optimization; LLM latency; embedding perf | Frontend performance; Lighthouse ≥80 | TM-12 (50 users, P95<2s); DM-14 (runbooks); cross-training | TM-12 met; 4 runbooks written |
| W40 | P5 | Security review + auth hardening + dry-run #0 | TM-13 security; auth hardening | AI/ML security; DDM-7 support | Frontend security; dry-run #0 support | TM-13 sign-off; dry-run #0 (GPM-8); DDM-7 verification; on-call | TM-13 met; dry-run #0 completed |
| W41 | P5 | Bug bash #2 + docs + DR drill + fallback video | Bugs from bash #2; DM-15 (architecture + ADR index); DR drill support | Bugs from bash #2; v1.0 AI/ML baselines; fallback video support | Bugs from bash #2; DM-16 (README + demo video); fallback video recorded | TM-14 (≤3 P1s); DR drill (<1h); DDM-8 verification; on-call | ≤3 P1s; DR drill <1h; fallback video recorded |
| W42 | P5 | **v1.0-rc + Code Freeze (GATE 5)** | v1.0-rc verify; Code Freeze sign; v1.0-rc tag | AI/ML finalize; dry-run #1 support | UI finalize; demo flow polish | TM-15 (smoke tests); dry-run #1 (GPM-10); Code Freeze sign | **v1.0-rc tagged; GATE 5 signed; Code Freeze active** |
| W43 | P6 | Prod deployment + dry-run #2 | Prod deploy; hotfix standby | Prod AI/ML verify; dry-run #2 support | Prod frontend verify; slide deck v2; dry-run #2 support | Prod deploy + monitor; IM-15 verification; dry-run #2 (GPM-11); on-call | IM-15: prod live; dry-run #2 completed |
| W44 | P6 | **Dry-run #3 + v1.0 + graduation** | v1.0 tag; presentation standby | AI depth section; presentation standby | Demo flow finalize; presentation standby | Dry-run #3 (GPM-12); artifact submission; on-call during presentation | **v1.0 tagged; graduation delivered 🎓** |

---

## 7. Backend Pod — 44-Week Index

| Week | Tasks | Deliverables | Dependencies |
| --- | --- | --- | --- |
| W1 | FastAPI skeleton; Alembic init; ADRs 1–5 draft | `backend/` repo; `/health` endpoint; 5 ADR PRs | GitHub org |
| W2 | OpenAPI; SQLAlchemy async; auth scaffold | `/docs` live; `get_db` dependency; auth module stubs | FastAPI skeleton |
| W3 | `users` migration; FastAPI deploy; auth scaffold | `users` table; staging deploy; auth route stubs | SQLAlchemy async |
| W4 | ADRs 1–5 merged; CONTRIBUTING; tech debt register | 5 accepted ADRs; `CONTRIBUTING.md`; `docs/tech-debt.md` | ADR drafts; TPM collaboration |
| W5 | Register/login/JWT; ADR-006 draft | Auth endpoints; JWT service; ADR-006 PR | Users table; fastapi-users |
| W6 | Profile CRUD; RBAC; course CRUD; file upload | Profile + courses + materials endpoints; MinIO upload | Auth; MinIO |
| W7 | Async enqueue; WS progress; materials list | Task queue pattern; WS endpoint; `/v1/courses/{id}/materials` | Celery + Redis; materials table |
| W8 | IM-2 integration; ADR-006 freeze; API reference | E2E flow works; Contract 10 frozen; OpenAPI published | All W5–W7 |
| W9 | `documents` table; `/v1/documents/{id}`; Qdrant prep | Documents migration; document endpoint; Qdrant spec | Materials table |
| W10 | Idempotency; documents metadata; chunks table | Content hash check; expanded documents schema; chunks migration | Documents table |
| W11 | `/v1/documents/{id}/chunks`; embedding batch prep; OCR doc | Chunks endpoint; embedding design doc; `docs/ocr.md` | Chunks table |
| W12 | v0.3 demo; Qdrant deploy; Qdrant provider | Demo passes; Qdrant on staging; `QdrantVectorDBProvider` | Embedding batch (Pod B) |
| W13 | `/v1/search`; embedding write path; ADR-011 | Search endpoint; auto-embed flow; ADR-011 | Qdrant; BGE provider |
| W14 | `/v1/retrieve`; chat API design | Retrieve endpoint; chat API design doc | Retrieval service (Pod B) |
| W15 | `/v1/rag/query`; chat API skeleton; RAG doc | RAG endpoint; chat skeleton; `docs/rag.md` | RAG service (Pod B) |
| W16 | Thin MVP endpoint; deploy; v0.4 tag | Thin MVP works on staging; **v0.4 tagged** | RAG service; demo PDF |
| W17 | Full chat API (SSE); sessions API; IM-7 | Chat + sessions endpoints; IM-7 verified | Streaming LLM (Pod B) |
| W18 | Multi-doc API; ADRs 12–15; Tier 1 contracts | Multi-doc retrieval; 4 ADRs; contracts doc | Retrieval service |
| W19 | Top-10 backend bugs; ADRs merged; contracts final | 0 P1s; 15 ADRs accepted; contracts finalized | Bug list; ADR reviews |
| W20 | v0.5 demo; Tier 1 sign; architecture diagram; v0.5 tag | **v0.5 tagged; GATE 2 signed**; `docs/architecture.md` | All W5–W19 |
| W21 | KG API design; light maintenance | KG API design doc; bug count ≤10 | KG schema (Pod B) |
| W22 | KG API skeleton; light maintenance | KG route stubs; Pydantic schemas; repository interface | KG schema |
| W23 | KG API full; KG worker Neo4j writes | Full KG API; worker writes to Neo4j | Neo4j (Pod D); KG schema |
| W24 | KG API final; DDM-2 ingestion; IM-8 verification | KG API polished; demo dataset ingested; IM-8 doc | Extraction pipeline (Pod B) |
| W25 | Quiz API design; light capacity | Quiz API design doc | KG schema; Tier 1 Freeze |
| W26 | Quiz API; v0.6 tag | Quiz endpoints; **v0.6 tagged** | Quiz generation (Pod B) |
| W27 | Mastery schema; mastery update hook | `mastery_records` table; hook on quiz submit | Mastery service (Pod B) |
| W28 | IM-10 integration; cohort mastery; BKT scaffold | Full quiz+mastery loop; cohort endpoint; BKT scaffold | Mastery service; quiz UI |
| W29 | Tier 2 contracts; recommendation API design; analytics design | Tier 2 contracts doc; 2 design docs | KG/quiz/mastery schemas |
| W30 | v0.7 demo; Tier 2 sign; DDM-3; v0.7 tag | **v0.7 tagged; GATE 3 signed**; 5 demo accounts | All W21–W29 |
| W31 | Recommendation API; review schedule; admin API design | `/v1/recommendations/today`; `/v1/reviews/scheduled`; admin design | Adaptive engine (Pod B) |
| W32 | Adaptive quiz endpoint; analytics queries | `/v1/quizzes/{id}/next-question`; analytics endpoints | Adaptive engine; quiz pool |
| W33 | Recommendation engine v1; IM-12 debug field | `/v1/recommendations`; difficulty debug field | Recommendation engine (Pod B) |
| W34 | Analytics endpoints final; IRT decision; v0.8 tag | 4 analytics endpoints; IRT decision; **v0.8 tagged** | Mastery + quiz + chat data |
| W35 | Admin API; notification system; IM-13 verification | Admin endpoints; notifications; IM-13 doc | Auth; RBAC; WS |
| W36 | Top backend bugs; DM-13 (quickstarts) | Bugs fixed; 2 quickstart docs | Bug bash #1 results |
| W37 | P1 closure; DB perf prep | 0 P1s; indexes added; slow query report | Bug bash #1 results |
| W38 | v0.9 demo; Feature Freeze sign; DDM-6 export; v0.9 tag | **v0.9 tagged; GATE 4 signed**; export script | All W5–W37 |
| W39 | Backend optimization; caching | P95<2s; cache layer; indexes tuned | Redis; Grafana |
| W40 | TM-13 security; auth hardening | 0 critical/high vulns; rate limiting; MFA scaffold | All W5–W39 |
| W41 | Bugs from bash #2; DM-15; DR drill support | P1s fixed; final architecture + ADR index; DR drill <1h | Bug bash #2 results |
| W42 | v1.0-rc verify; Code Freeze sign; v1.0-rc tag | **v1.0-rc tagged; GATE 5 signed** | All W5–W41 |
| W43 | Prod deploy; hotfix standby | Prod URL live; smoke tests pass | v1.0-rc; deploy runbook |
| W44 | v1.0 tag; presentation standby | **v1.0 tagged**; presentation delivered | Dry-run #3 passes |

---

## 8. AI/ML & Data Pod — 44-Week Index

| Week | Tasks | Deliverables | Dependencies |
| --- | --- | --- | --- |
| W1 | PAL skeleton; 20-PDF golden set; LiteLLM plan | 7 PAL interfaces; `tests/data/golden_pdfs/`; gateway plan | Backend skeleton |
| W2 | OCR/embedding spike methodologies; demo PDF chosen | 2 methodology docs; `tests/data/demo_pdf/v0.4.pdf` | Golden set |
| W3 | OCR/embedding installs; demo PDF smoke test | Install scripts; smoke output | PaddleOCR; BGE-M3; OpenAI |
| W4 | Spike template; LiteLLM pre-pull; demo PDF smell test | `docs/templates/research-spike.md`; image cached; 3 Q&A smell test | Methodologies |
| W5 | OCR spike; embedding spike; PaddleOCRProvider | ADR-007 + ADR-008 drafts; first PAL provider | Spike methodologies |
| W6 | Tesseract + DocAI providers; BGE + OpenAI providers; LiteLLM provider | 5 PAL providers; priority chain config | PaddleOCRProvider; spikes |
| W7 | OCR worker skeleton; chunking refinement; ADR-009 | Worker skeleton; semantic chunking; ADR-009 draft | Async job infra; BGE |
| W8 | OCR worker 5-PDF smoke; RAG eval harness design; ADR-010 | 5-PDF report; eval design doc; ADR-010 draft | OCR worker; eval scaffold |
| W9 | OCR pipeline v1; WS event; chunking refinement | OCR worker full; `material.ready` event; semantic chunking | Documents table; PAL OCR |
| W10 | 20-PDF golden set; Document AI escalation; Arabic preprocessing | ≥90% success; escalation path; Arabic processor | OCR pipeline v1 |
| W11 | ADR-009 accepted; chunking doc; embedding batch skeleton | ADR-009 accepted; `docs/chunking.md`; batch skeleton | Chunking refinement |
| W12 | Embedding batch job (1000 chunks); TM-3; hybrid retrieval design | 1000 chunks in <10min; TM-3 report; design doc | BGE; Qdrant |
| W13 | IM-4 verification; BM25; reranker provider | IM-4 doc; BM25 service; `BGERerankerProvider` | Search API (Pod A) |
| W14 | Hybrid retrieval; reranker; RAG prompt design; quality baseline | Hybrid retrieval; reranker integrated; prompt draft; baseline | Search API; BM25; reranker |
| W15 | RAG service; RAG eval harness v1 (50 Q&A); IM-5; DDM-1 | RAG service; 50 Q&A golden set; IM-5 doc; demo PDF set | Retrieval service; LiteLLM |
| W16 | PB-02 check; RAG iteration; 5 demo questions | Eval results; PB-02 decision if triggered; 5 questions doc | RAG eval harness |
| W17 | Streaming LLM; PB-02 fixes; multi-doc design | Streaming provider; fixes applied; multi-doc design doc | LiteLLM gateway; PB-02 decision |
| W18 | Multi-doc retrieval; multi-doc eval; ADRs 7–11 accepted | Multi-doc retrieval; 10 multi-doc Q&A; 5 ADRs accepted | Retrieval service |
| W19 | Top-5 AI/ML bugs; RAG doc final; 5 multi-doc questions | Bugs fixed; `docs/rag.md` final; 5 questions doc | Bug list |
| W20 | Final RAG eval; DDM-1 confirm; KG design; GPM-0 | v0.5 baseline metrics; DDM-1 confirmed; KG design doc; demo backlog | RAG service |
| W21 | ADR-016 (KG schema); concept extraction spike prep; graduation outline | ADR-016 accepted; spike prep doc; outline draft | Tech Spec Section 13 |
| W22 | Concept extraction spike; ADR-017 draft; outline v0 final | Spike results; ADR-017 draft; outline finalized | ADR-016; LiteLLM |
| W23 | Extraction pipeline; 200+ concepts; DM-10 (KG doc) | Pipeline; 200+ concepts + 400+ relations; `docs/kg.md` | Neo4j; ADR-017 |
| W24 | KG retrieval boost design; extraction refinement; GPM-1 | Boost design doc; refined KG; top-10 demo beats | KG populated |
| W25 | KG-backed retrieval boost; cognitive spike begins; quiz gen design | Faithfulness ↑5%; spike started; quiz gen design doc | KG; retrieval service |
| W26 | Quiz generation v1; cognitive spike continues | 10 MCQs in <30s; spike prototypes (rolling avg, WMA, BKT) | LiteLLM; retrieval |
| W27 | ADR-017 accepted; mastery estimator v1 (WMA); DM-11 | ADR-017 accepted; WMA mastery service; `docs/student-model.md` | Mastery schema (Pod A) |
| W28 | Cognitive hardening; adaptive spike prep; quiz pool (50+) | Cold-start + confidence + sanity; spike prep; 50+ questions | Mastery service; CSP |
| W29 | Adaptive spike; cognitive hardening final; quiz pool (80+) | 3 prototypes; hardening final; 80+ questions | Cognitive model; simulated data |
| W30 | ADR-018 draft; adaptive spike continues; GPM-3 | ADR-018 draft; refined prototype; demo script skeleton | Spike results |
| W31 | Adaptive engine productionized; ADR-018 accepted; SM-2; DM-12 | Adaptive engine; ADR-018 accepted; SM-2; `docs/adaptive.md` | Mastery; KG; CSP |
| W32 | Difficulty adjustment; adaptation eval harness; quiz pool | Difficulty logic; eval harness (10×20); 80+ questions | Adaptive engine; quiz pool |
| W33 | TM-9 (adaptation eval); quiz pool 100+; demo script skeleton | TM-9 results; 100+ questions; demo script skeleton | Adaptation eval harness |
| W34 | DDM-4 (quiz pool); GPM-5 (demo script v1); IRT eval | 20 verified quizzes; demo script v1; IRT decision | Quiz pool; demo data |
| W35 | Recommendation iteration; DDM-5 prep; quiz pool maintenance | Improved recommendations; 5 RAG questions draft; quality report | TM-9 results |
| W36 | DDM-5 validation; GPM-6 (deck v1 advisor); recommendation iteration | 5 validated questions; deck v1 reviewed; improved engine | Demo data |
| W37 | P1 closure; recommendation final; DDM-6 prep | 0 P1s; final recommendation engine; DDM-6 plan | Bug bash #1 results |
| W38 | v1.0 AI/ML baselines; GPM-7 (demo data curated) | Baselines committed; demo data curated | All W31–W37 |
| W39 | RAG pipeline optimization; LLM latency; embedding perf | Reranker batched; LLM P95<1.5s; embedding perf report | Retrieval service; LiteLLM |
| W40 | AI/ML security; DDM-7 support | AI/ML security doc; DDM-7 supported | RAG service; extraction |
| W41 | Bugs from bash #2; v1.0 AI/ML baselines; fallback video support | P1s fixed; baselines committed; video supported | Bug bash #2 results |
| W42 | AI/ML finalize; dry-run #1 support | AI/ML stable; dry-run #1 supported | All W31–W41 |
| W43 | Prod AI/ML verify; dry-run #2 support; hotfix standby | Prod verification; dry-run #2 supported | Prod deployment |
| W44 | AI depth section; presentation standby | AI depth delivered; presentation delivered | Slide deck v2 |

---

## 9. Frontend Pod — 44-Week Index

| Week | Tasks | Deliverables | Dependencies |
| --- | --- | --- | --- |
| W1 | Next.js 16 skeleton; shadcn/ui; Storybook | `frontend/` repo; base components; Storybook on :6006 | GitHub repo |
| W2 | Design tokens; Next.js staging deploy | Tailwind config; staging URL | shadcn/ui |
| W3 | Next.js Dockerfile; app shell | Dockerfile; sidebar + topnav + breadcrumbs | Design tokens |
| W4 | Login page; Storybook + Chromatic | Polished login page; visual regression in CI | App shell |
| W5 | Register page; login page wiring | Register + login work on staging | Auth API (Pod A) |
| W6 | Course list/create/edit; profile page | Course CRUD UI; profile page | Course API; profile API |
| W7 | App shell complete; course detail page | Full app shell; course detail with materials tab | Design tokens |
| W8 | Docusaurus; upload UI polish; E2E test | Docusaurus live; polished upload UI; Playwright test | API reference |
| W9 | Extracted text viewer; chat UI scaffold | Loading/ready/failed states; `/chat` scaffold | Documents API; WS |
| W10 | Citation component; chat message list | `CitationLink.tsx`; markdown rendering + streaming | Chat UI scaffold |
| W11 | Chunks viewer; source panel | Paginated chunks viewer; source panel with API | Chunks API |
| W12 | Chat input component; v0.3 demo polish | Auto-resize input; v0.3 demo ready | Chat UI |
| W13 | Search UI; chat session list | Search bar + results; session list placeholder | Search API |
| W14 | Streaming chat message; source panel integration | SSE rendering; multi-citation source panel | Chat API design |
| W15 | Citation rendering wired; chat UI polish | Citations render from RAG response; demo-ready | RAG response schema |
| W16 | Chat UI wired to thin MVP; polish | `/chat` works end-to-end; demo-ready | Thin MVP endpoint |
| W17 | Chat UI wired to full API; session list + detail; student flow polish | Full chat works; session history; polished flow | Full chat API |
| W18 | Multi-doc citations; chat polish | Doc-level badges; material filter; polished | Multi-doc API |
| W19 | Top-5 frontend bugs; v0.5 polish | Bugs fixed; v0.5 demo-ready | Bug list |
| W20 | v0.5 demo UI; KG viz research; demo video | v0.5 demo polished; KG viz research doc; demo video | All W5–W19 |
| W21 | KG viz skeleton; light maintenance | `KGGraph.tsx` skeleton; Storybook; no P1s | KG viz research |
| W22 | Concept detail view; light maintenance | Concept detail page (mock data); no P1s | KG viz skeleton |
| W23 | Relations list; KG viz API integration prep | `RelationsList.tsx`; integration plan + mocks | KG viz skeleton |
| W24 | KG viz UI shipped; demo materials list | Interactive graph with real data; materials list | KG API (Pod A) |
| W25 | Quiz UI design; KG viz polish | Quiz UI design doc + mockups; KG polished | Quiz API design |
| W26 | Quiz-taking UI; instructor quiz creation | Student quiz UI; instructor creation page | Quiz API; quiz generation |
| W27 | Mastery UI skeleton; quiz polish | `/dashboard/mastery` with mock data; quiz polished | Mastery endpoint |
| W28 | Mastery UI shipped; cohort mastery view | Mastery UI with real data; heatmap view | Mastery endpoint; cohort endpoint |
| W29 | Mastery UI polish; recommendation UI skeleton | Trend chart + filters; recommendation UI mock | Mastery UI |
| W30 | v0.7 demo UI; recommendation UI design | v0.7 polished; recommendation UI design doc | All W21–W29 |
| W31 | Recommendation UI; slide deck template | Dashboard with recommendation panel; 5 slides | Recommendation API |
| W32 | Recommendation UI shipped (IM-11); adaptive quiz UI; slides 6–10 | IM-11 verified; adaptive quiz UI; 10 slides | Recommendation API; adaptive quiz endpoint |
| W33 | Top-3 recommendations; adaptive quiz polish; slides 11–15 | Top-3 UI; polished adaptive quiz; 15 slides | Recommendation engine v1 |
| W34 | Analytics dashboard UI (4 charts); v0.8 demo video | 4 charts; demo video | Analytics endpoints |
| W35 | Admin dashboard UI; notification bell; v0.9 polish | Admin UI; notification bell; polished | Admin API; notification API |
| W36 | UX polish; top frontend bugs | Lighthouse a11y ≥90; bugs fixed | Bug bash #1 results |
| W37 | P1 closure; WCAG 2.1 AA pass | 0 P1s; axe-core clean | Bug bash #1 results |
| W38 | v0.9 demo UI; P5 docs prep | v0.9 polished; docs gap list | All W5–W37 |
| W39 | Frontend performance; Lighthouse ≥80 | Bundle split; Lighthouse perf ≥80 | All W5–W38 |
| W40 | Frontend security; dry-run #0 support | XSS/CSRF/CSP fixed; dry-run #0 supported | Semgrep |
| W41 | Bugs from bash #2; DM-16 (README + demo video); fallback video recorded | P1s fixed; README polished; fallback video | Bug bash #2 results |
| W42 | UI finalize; demo flow polish | UI stable; demo flow polished | Dry-run feedback |
| W43 | Prod frontend verify; slide deck v2; dry-run #2 support | Lighthouse met on prod; deck v2; dry-run #2 supported | Prod deployment |
| W44 | Demo flow finalize; presentation standby | Demo flow finalized; presentation delivered | Demo script; slide deck v2 |

---

## 10. DevOps / QA Pod — 44-Week Index

| Week | Tasks | Deliverables | Dependencies |
| --- | --- | --- | --- |
| W1 | CI scaffold; 3 envs; risk register seeded | `.github/workflows/ci.yml`; staging URL; 32 risks | Both skeletons |
| W2 | Eval harness scaffold; pytest + Vitest configured | `app/eval/` skeleton; `docs/eval-harness.md`; test infra | Backend + frontend |
| W3 | Staging deploy workflow; PG provisioned; smoke test | Deploy workflow; PG on staging; smoke script | Both Dockerfiles |
| W4 | Eval harness in CI; risk register v1; v0.1 tag | CI eval job; risk register reviewed; **v0.1 tagged** | Eval scaffold |
| W5 | Redis + Celery + Flower; Loki/Prometheus/Sentry; auth integration tests | Async job infra; observability; auth tests | Staging infra |
| W6 | MinIO; Grafana dashboard; v0.1 tag (if not W4); cross-training | MinIO + buckets; staging dashboard; cross-training log | Staging infra |
| W7 | LiteLLM gateway deploy; Langfuse; async pipeline tests | LiteLLM live; Langfuse live; pipeline tests | LiteLLM plan |
| W8 | TM-2 (≥80% coverage); v0.2 tag; cross-training | TM-2 signed; **v0.2 tagged**; Pod A shadowing | All W5–W8 |
| W9 | OCR integration tests (5 PDFs); Qdrant backup script; cross-training | 5-PDF tests; backup script; Pod B shadowing Qdrant | OCR pipeline |
| W10 | OCR integration in CI; OCR quality dashboard | CI OCR job; Grafana OCR dashboard | OCR integration tests |
| W11 | Chunking metrics; baseline load test | Chunking panels; load test report | Chunks table |
| W12 | TM-3 sign-off; cost monitoring; cross-training | TM-3 signed; cost alert; Pod B Qdrant ops | Embedding batch |
| W13 | Qdrant monitoring; full pipeline CI test; cross-training | Qdrant dashboard + alert; pipeline CI test; Pod B re-index | Qdrant |
| W14 | Retrieval quality dashboard; Langfuse tracing | Retrieval dashboard; LLM traces | Retrieval service |
| W15 | TM-4 (RAG eval in CI); RAG load test; RAG quality dashboard | TM-4 met; load test report; RAG dashboard | RAG eval harness |
| W16 | Gate 1 validation; demo monitoring; smoke test | Gate 1 signed; monitoring report; smoke test | Thin MVP |
| W17 | TM-5 (E2E test); chat API monitoring; integration tests | TM-5 met; chat dashboard; chat tests | Full chat API |
| W18 | TM-6 prep; Tier 1 freeze review prep | Coverage report; review schedule | All W5–W18 |
| W19 | E2E re-run; TM-6 sign-off; Tier 1 sign-off doc | Tests pass; TM-6 signed; sign-off doc | Bug fixes |
| W20 | TM-6 sign-off; v0.5 validation; on-call prep | TM-6 signed; validation report; on-call schedule | All W5–W20 |
| W21 | Neo4j deploy prep; on-call; cross-training | Neo4j compose spec; on-call log; Pod B Neo4j shadowing | Staging infra |
| W22 | Neo4j deploy; on-call; cross-training | Neo4j on staging; Pod B Cypher practice | Neo4j prep |
| W23 | TM-7 prep (KG sanity); Neo4j monitoring; on-call; cross-training | KG sanity tests; Neo4j dashboard; Pod B index rebuild | KG populated |
| W24 | TM-7 sign-off; DDM-2 verification; cross-training | TM-7 signed; DDM-2 verified; Pod B prerequisite query | KG populated |
| W25 | Retrieval boost metrics; exam crunch comms (PB-05); cross-training | Retrieval dashboard; PB-05 comms; cross-training log | Retrieval boost |
| W26 | Quiz generation monitoring; on-call | Quiz dashboard; on-call log | Quiz generation |
| W27 | Mastery monitoring; PB-05 status; cross-training | Mastery dashboard; PB-05 doc; cross-training log | Mastery service |
| W28 | TM-8 (E2E); concurrency test; cross-training | TM-8 met; concurrency passes; Pod C CI triage | Quiz + mastery loop |
| W29 | Tier 2 freeze prep; cross-training | Sign-off doc draft; Pod C Sentry triage | Tier 2 contracts |
| W30 | Tier 2 sign-off; v0.7 validation; DDM-3 verification; on-call | **GATE 3 signed**; validation report; DDM-3 verified | All W21–W30 |
| W31 | Adaptive monitoring; adaptation eval prep; cross-training | Adaptive dashboard; eval design doc; cross-training log | Adaptive engine |
| W32 | Monitoring; cross-training | Updated dashboards; Pod C CI independently | Recommendation API |
| W33 | IM-12 verification; recommendation monitoring; cross-training | IM-12 verified; recommendation dashboard; Pod C CI+Sentry | Adaptive quiz |
| W34 | DDM-4 verification; analytics monitoring; cross-training | DDM-4 verified; analytics dashboard; ≥2 cross-trained | Demo quiz pool |
| W35 | Admin monitoring; bug bash #1 prep; cross-training | Admin dashboard; bug bash plan; ≥3 cross-trained | Admin API |
| W36 | TM-10 (bug bash #1); DDM-5 verification; Feature Freeze prep | TM-10 met; DDM-5 verified; sign-off doc draft | All W5–W35 |
| W37 | P1 closure verification; accessibility validation; Feature Freeze prep | P1 closure report; a11y report; sign-off doc finalized | Bug fixes |
| W38 | TM-11 (≥60% coverage); DDM-6 verification; v0.9 validation; Feature Freeze sign | **GATE 4 signed**; DDM-6 verified; validation report | All W5–W37 |
| W39 | TM-12 (50 users, P95<2s); DM-14 (runbooks); cross-training | TM-12 met; 4 runbooks; ≥3 cross-trained | Perf optimizations |
| W40 | TM-13 sign-off; dry-run #0 (GPM-8); DDM-7 verification; on-call | TM-13 met; dry-run #0 report; DDM-7 verified | Security work |
| W41 | TM-14 (≤3 P1s); DR drill (<1h); DDM-8 verification; on-call | TM-14 met; DR drill report; DDM-8 verified | Bug bash #2 |
| W42 | TM-15 (smoke tests); dry-run #1 (GPM-10); Code Freeze sign | TM-15 met; dry-run #1 report; **GATE 5 signed** | Prod-like env |
| W43 | Prod deploy + monitor; IM-15 verification; dry-run #2 (GPM-11); on-call | Prod live; IM-15 verified; dry-run #2 report | v1.0-rc |
| W44 | Dry-run #3 (GPM-12); artifact submission; on-call during presentation | Dry-run #3 report; artifacts submitted; presentation delivered | All W1–W43 |

---

## 11. Cross-Pod Handoff Matrix

Only meaningful handoffs are included. Each handoff specifies the producer (From), consumer (To), the artifact, and the acceptance criteria the consumer uses to verify the handoff.

| Week | From | To | Handoff | Required Artifact | Acceptance Criteria |
| --- | --- | --- | --- | --- | --- |
| W1 | Backend | AI/ML | PAL directory layout | `backend/app/pal/interfaces/` with 7 ABCs | Pod B can import all 7 interfaces |
| W1 | DevOps/QA | All Pods | CI scaffold + 3 envs | `.github/workflows/ci.yml` + staging URL | CI green on dummy PR; staging reachable |
| W2 | TPM | All Pods | MVP definition | `docs/mvp.md` | All pod leads sign; no objections after 48h |
| W3 | DevOps/QA | Backend | Staging Postgres | PG 16 on staging + connection string | `psql $STAGING_DB_URL` works |
| W3 | DevOps/QA | Backend, Frontend | Staging deploy workflow | `.github/workflows/deploy-staging.yml` | Merge to `main` deploys both apps in <5min |
| W4 | Backend | All Pods | ADRs 1–5 accepted | 5 merged ADRs + index | All marked `Accepted`; index published |
| W5 | Backend | Frontend | Auth API (register/login/JWT) | `/v1/auth/register` + `/v1/auth/login` + ADR-006 | Register + login work on staging; tokens persist |
| W5 | AI/ML | Backend, DevOps/QA | PAL OCR provider (PaddleOCR) | `PaddleOCRProvider` class + tests | Provider returns text + bounding boxes |
| W6 | Backend | Frontend | Course CRUD API + file upload | `/v1/courses` CRUD + `/v1/materials/upload-url` | Instructor can create course + upload PDF |
| W6 | AI/ML | Backend, DevOps/QA | 5 PAL providers | PaddleOCR + Tesseract + DocAI + BGE + OpenAI providers | All pass unit tests; priority chain configured |
| W7 | DevOps/QA | Backend, AI/ML | Async job infra (Celery + Redis) | Worker container + Flower dashboard | Sample task completes |
| W7 | DevOps/QA | AI/ML | LiteLLM gateway | Gateway on staging + 2 providers configured | Test prompt returns response |
| W8 | Backend | Frontend, AI/ML | Tier 1 Contract 10 (auth token format) frozen | `docs/contracts/10-auth-token-format.md` | All pod leads sign; post-freeze protocol active |
| W8 | Backend | Frontend | API reference v1 | OpenAPI spec at `docs.openlearn.ai/api/v1` | Spec renders; CI checks up-to-date |
| W8 | Frontend | All Pods | Docusaurus site | Public docs URL | Site accessible; sidebar configured |
| W9 | Backend | AI/ML | `documents` table | Migration + Pydantic schema | Worker writes text + layout JSON |
| W9 | Backend | Frontend | `/v1/documents/{id}` endpoint | Document detail (paginated text + metadata) | Pod C viewer renders |
| W10 | AI/ML | Backend, DevOps/QA | 20-PDF golden set OCR results | `docs/p2/ocr-hardening-results.md` | ≥90% success; PB-01 status documented |
| W11 | AI/ML | Backend | ADR-009 (chunking strategy) accepted | ADR + Contract 2 draft | Schema frozen post-W20 |
| W11 | Backend | Frontend | `/v1/documents/{id}/chunks` endpoint | Paginated chunks with filters | Chunks viewer renders |
| W12 | AI/ML | Backend | Embedding batch job | Worker + 1000 chunks in Qdrant | Search API can query |
| W12 | Backend | DevOps/QA | v0.3 tag | Git tag + release | Tag exists |
| W13 | Backend | AI/ML | Qdrant deployed + `QdrantVectorDBProvider` | Collection `openlearn_chunks` (1024-dim) | Provider store/search works |
| W13 | Backend | Frontend | `/v1/search` endpoint | Top-k results with filters | Search UI renders |
| W13 | AI/ML | Backend | IM-4 verification | `docs/p2/im-4-verification.md` | Full pipeline runs in <15min |
| W14 | Backend | AI/ML | `/v1/retrieve` endpoint | Re-ranked top-5 chunks with scores | Endpoint returns in <1s |
| W14 | AI/ML | Backend | Hybrid retrieval + reranker | `RetrievalService.retrieve` | Beats pure vector on precision@5 |
| W15 | Backend | AI/ML, Frontend | `/v1/rag/query` endpoint | Answer + citations via curl | Returns cited answer in <3s |
| W15 | AI/ML | DevOps/QA, Backend | RAG eval harness v1 (50 Q&A) | `rag_evaluator.py` + golden set | TM-4 runs in CI; metrics posted |
| W15 | AI/ML | TPM | DDM-1 (demo PDF set) | 15–30 PDFs + manifest | All OCR-able |
| W16 | Backend | Frontend | Thin MVP endpoint | `/v1/chat/thin-mvp` returns answer + citations | 5 questions work without crash |
| W16 | AI/ML | TPM, DevOps/QA | PB-02 status | Eval results + decision doc | Faithfulness ≥0.7 or PB-02 invoked |
| W16 | DevOps/QA | All Pods | Gate 1 sign-off | `docs/gates/gate-1-v0.4-thin-mvp.md` | All 7 criteria verified; signed |
| W17 | Backend | Frontend | Full chat API (SSE) | `/v1/chat` + `/v1/chat/{id}/message` (SSE) | Stream renders progressively |
| W17 | AI/ML | Backend | Streaming LLM provider | `LiteLLMReasoningProvider.generate_stream` | Tokens yield progressively |
| W17 | DevOps/QA | All Pods | TM-5 (E2E test) | Playwright test + CI integration | Test passes on staging in <15min |
| W18 | Backend | AI/ML | Multi-doc chat API | Course-level retrieval + doc-level filters | Citations include material info |
| W18 | Backend | All Pods | Tier 1 contracts (1–5) doc | `docs/contracts/tier-1.md` | All 5 documented with examples |
| W19 | Backend | All Pods | ADRs 1–15 complete | 15 accepted ADRs + index | All marked `Accepted` |
| W20 | Backend | All Pods | Tier 1 Freeze signed + architecture diagram | `docs/gates/gate-2-tier-1-freeze.md` + `docs/architecture.md` | All pod leads + TPM sign |
| W20 | AI/ML | TPM | GPM-0 (demo backlog) | `docs/graduation/demo-backlog.md` | 10+ beats listed |
| W21 | AI/ML | Backend, Frontend | ADR-016 (KG schema) | ADR + Contract 6 draft + migration | Concepts + relations tables exist |
| W22 | AI/ML | Backend | ADR-017 (concept extraction) draft | ADR + extraction approach | LLM-based with JSON mode recommended |
| W22 | TPM | All Pods | GPM-2 (graduation outline v0) | `docs/graduation/outline-v0.md` | Story arc + timing finalized |
| W23 | DevOps/QA | AI/ML | Neo4j deployed | Neo4j on staging + Bolt driver | Backend connects; backup tested |
| W23 | AI/ML | Backend, Frontend, DevOps/QA | KG populated (200+ concepts) | Neo4j collection + sanity report | No orphans/self-loops/duplicates |
| W23 | AI/ML | TPM | DM-10 (KG design doc) | `docs/kg.md` | Reviewed by A-Lead + D-Lead |
| W24 | Backend | Frontend | KG API (full) | `/v1/kg/concepts` + `/v1/kg/relations` | KG viz renders real data |
| W24 | AI/ML | TPM | GPM-1 (top-10 demo beats) | `docs/graduation/demo-beats-top-10.md` | TPM + advisor sign off |
| W24 | DevOps/QA | All Pods | TM-7 (KG sanity) sign-off + DDM-2 verification | TM-7 results + DDM-2 doc | All sanity tests pass; demo PDFs ingested |
| W25 | AI/ML | Backend | KG-backed retrieval boost | Updated `RetrievalService` | Faithfulness ↑ ≥5% |
| W25 | TPM | All Pods | Exam crunch comms (PB-05 prep) | Comms sent + capacity tracking | Pod leads acknowledge |
| W26 | Backend | Frontend | Quiz API | `/v1/materials/{id}/quizzes` + `/v1/quizzes/{id}` + submit | Quiz UI works |
| W26 | AI/ML | Backend | Quiz generation v1 | `quiz_generation_service.py` | 10 MCQs in <30s |
| W26 | DevOps/QA | All Pods | v0.6 tag | Git tag + release | Tag exists |
| W27 | Backend | AI/ML | Mastery schema (`mastery_records`) | Migration + Pydantic schema | Worker writes mastery |
| W27 | AI/ML | Backend | ADR-017 (cognitive model) accepted | ADR + Contract 8 draft | WMA v1 + BKT v0.7 + IRT v0.8 (conditional) |
| W27 | AI/ML | TPM | DM-11 (cognitive model doc) | `docs/student-model.md` | Reviewed by B-Lead + D-Lead |
| W28 | Backend | Frontend | Cohort mastery endpoint | `/v1/instructor/courses/{id}/cohort-mastery` | Cohort view renders |
| W28 | DevOps/QA | All Pods | TM-8 (quiz + mastery E2E) | Playwright test + CI | Test passes on staging |
| W29 | Backend | All Pods | Tier 2 contracts (6–9) doc | `docs/contracts/tier-2.md` | All 4 documented with examples |
| W30 | Backend | All Pods | Tier 2 Freeze signed | `docs/gates/gate-3-tier-2-freeze.md` | All pod leads + TPM sign |
| W30 | Backend | TPM | DDM-3 (5 demo student accounts) | Seeding script + 5 accounts | Seeded mastery visible |
| W30 | AI/ML | Backend | ADR-018 (adaptive engine) draft + Contract 9 final | ADR + contract | Priority scoring + rule-based fallback |
| W30 | TPM | All Pods | GPM-3 (demo script skeleton) | `docs/graduation/demo-script-skeleton.md` | 8-min demo flow outlined |
| W31 | Backend | Frontend | Recommendation API | `/v1/recommendations/today` + `/v1/reviews/scheduled` | UI renders recommendation + review schedule |
| W31 | AI/ML | Backend, TPM | ADR-018 accepted + DM-12 (adaptive doc) | ADR + `docs/adaptive.md` | Reviewed by B-Lead + D-Lead |
| W32 | Backend | Frontend | Adaptive quiz endpoint | `/v1/quizzes/{id}/next-question` | Difficulty badge updates |
| W32 | AI/ML | DevOps/QA | Adaptation eval harness | `adaptation_evaluator.py` + simulated data | TM-9 runs in CI |
| W33 | Backend | Frontend | Recommendation engine v1 | `/v1/recommendations` (top-3) | Top-3 UI renders |
| W33 | AI/ML | TPM | Demo script v1 skeleton | `docs/graduation/demo-script-v1.md` (started) | 5/10 beats filled |
| W33 | DevOps/QA | All Pods | IM-12 verified + TM-9 met | IM-12 doc + TM-9 results | Difficulty adapts; mastery gain >10% vs random |
| W34 | Backend | Frontend | Analytics endpoints (4) | `/v1/analytics/dashboard` + `/heatmap` + 2 more | 4 charts render |
| W34 | AI/ML | TPM, DevOps/QA | DDM-4 (20 demo quizzes) + GPM-5 (demo script v1) | Quiz pool + manifest + demo script | 20 quizzes verified; script finalized |
| W35 | Backend | Frontend | Admin API + notification API | `/v1/admin/*` + `/v1/notifications` | Admin UI + notification bell render |
| W35 | AI/ML | TPM | DDM-5 prep (5 known-good RAG questions) | Draft questions + expected answers | Tested on staging |
| W36 | AI/ML | TPM, DevOps/QA | DDM-5 validated + GPM-6 (deck v1 advisor) | 5 validated questions + deck v1 | Advisor feedback incorporated |
| W36 | DevOps/QA | All Pods | TM-10 (bug bash #1) + DDM-5 verified | Bug bash report + DDM-5 doc | 50+ bugs triaged; P1s assigned |
| W37 | DevOps/QA | All Pods | P1 closure + a11y validation reports | 2 reports | 0 P1s; axe-core clean |
| W38 | Backend | All Pods | Feature Freeze signed + DDM-6 export | Sign-off doc + export script | All Gate 4 criteria verified |
| W38 | AI/ML | TPM | v1.0 AI/ML baselines + GPM-7 (demo data curated) | Baselines doc + curation report | Stable + reproducible |
| W38 | DevOps/QA | All Pods | TM-11 (≥60% coverage) + DDM-6 verified + Feature Freeze sign | TM-11 + DDM-6 + sign-off | All met |
| W39 | Backend | DevOps/QA | Backend optimized (P95<2s) | Performance report + cache layer | TM-12 passes |
| W39 | AI/ML | DevOps/QA | RAG pipeline optimized | Optimization report | Reranker batched; LLM P95<1.5s |
| W39 | DevOps/QA | All Pods | TM-12 (50 users, P95<2s) + DM-14 (4 runbooks) | TM-12 report + 4 runbooks | P95<2s; runbooks tested |
| W40 | DevOps/QA | All Pods | TM-13 (security) + dry-run #0 + DDM-7 | TM-13 report + dry-run #0 report + DDM-7 doc | 0 critical/high; dry-run completed; demo data on prod-like |
| W41 | DevOps/QA | All Pods | TM-14 (≤3 P1s) + DR drill (<1h) + DDM-8 | TM-14 report + DR drill report + DDM-8 doc | ≤3 P1s; DR <1h; demo data frozen |
| W41 | Frontend | TPM | DM-16 (README + demo video) + GPM-9 (fallback video) | README + 2 videos | Polished; videos recorded |
| W42 | Backend | All Pods | Code Freeze signed + v1.0-rc tag | Sign-off doc + tag | All Gate 5 criteria verified |
| W42 | DevOps/QA | All Pods | TM-15 (smoke tests) + dry-run #1 (GPM-10) | TM-15 report + dry-run #1 report | All green; advisor feedback incorporated |
| W43 | Backend | All Pods, TPM | Production deployment + IM-15 | Prod URL + IM-15 doc | Prod live; smoke tests pass |
| W43 | Frontend | TPM | Slide deck v2 | Deck v2 | 30-min timing; "what worked, what didn't" included |
| W43 | DevOps/QA | All Pods | Dry-run #2 (GPM-11) | Dry-run #2 report | Timing tuned; prod stable |
| W44 | Backend | All Pods | v1.0 tag | Git tag + release | Tag exists |
| W44 | DevOps/QA | All Pods | Dry-run #3 + artifact submission | Dry-run #3 report + submission confirmation | All artifacts submitted; presentation delivered |

---



## 12. Milestone → Task Traceability

This section maps every major roadmap milestone to the concrete weekly tasks that implement it. For each milestone, the table identifies the relevant weeks, each Pod's contribution, the integration point, and the expected milestone deliverable. No major roadmap milestone disappears into the weekly plan.

### 12.1 Version Milestones

| Milestone | Target | Relevant Weeks | Backend Contribution | AI/ML Contribution | Frontend Contribution | DevOps/QA Contribution | Integration Point | Expected Deliverable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **v0.1 (Skeleton)** | W6 | W1–W6 | FastAPI skeleton; users table; auth scaffold; deploy | PAL skeleton; OCR/embedding installs | Next.js skeleton; design tokens; login page | CI scaffold; 3 envs; staging deploy; MinIO | Staging URL with both apps + `/health` + login page | v0.1.0 tagged; CI green; 5 ADRs; OOS signed |
| **v0.2 (Foundations)** | W8 | W5–W8 | Auth (register/login/JWT); RBAC; course CRUD; file upload; Contract 10 frozen | OCR/embedding spikes; 5 PAL providers | Course UI; profile page; Docusaurus; upload UI | Async job infra; observability; LiteLLM gateway; TM-2 (≥80% coverage) | IM-2: instructor creates course + uploads PDF | v0.2.0 tagged; auth + course CRUD + upload work |
| **v0.3 (Ingestion)** | W12 | W9–W12 | `documents` + `chunks` tables; `/v1/documents/{id}` + chunks endpoint; Qdrant deploy | OCR pipeline v1; chunking (ADR-009); embedding batch job (1000 chunks) | Extracted text viewer; chunks viewer; chat UI scaffold | OCR integration tests; TM-3 (5-PDF); cost monitoring | IM-4: full ingestion pipeline end-to-end | v0.3.0 tagged; OCR + chunking + embeddings work |
| **v0.4 (Thin MVP) — GATE 1** | W16 | W13–W16 | `/v1/search`; `/v1/retrieve`; `/v1/rag/query`; thin MVP endpoint; deploy | Hybrid retrieval (BM25+vector); reranker; RAG service; RAG eval harness v1 (50 Q&A); DDM-1 (demo PDF set) | Search UI; chat UI; citation rendering; chat UI wired to thin MVP | TM-4 (RAG eval in CI); Gate 1 validation | IM-5: query returns cited answer via curl; IM-6: chat in browser | **v0.4.0 tagged; GATE 1 signed** |
| **v0.5 (Full MVP) + Tier 1 Freeze — GATE 2** | W20 | W17–W20 | Full chat API (SSE); multi-doc API; ADRs 12–15; Tier 1 contracts (1–5) frozen; architecture diagram | Streaming LLM; PB-02 fixes; multi-doc retrieval; ADRs 7–11 accepted; KG design; GPM-0 (demo backlog) | Chat UI wired; session list; multi-doc citations; v0.5 demo UI | TM-5 (E2E); TM-6 (≥40% coverage); Tier 1 sign-off; on-call prep | IM-7: full student flow E2E green | **v0.5.0 tagged; GATE 2 signed; 22-week graduation runway begins** |
| **v0.6 (Knowledge layer)** | W26 | W21–W26 | KG API; quiz API | KG schema (ADR-016); concept extraction (ADR-017); KG populated (200+ concepts); KG-backed retrieval boost; quiz generation v1 | KG viz UI; quiz UI; demo materials list | TM-7 (KG sanity); DDM-2 (demo dataset v1); Neo4j deploy | IM-8: KG populated from new upload; IM-9: KG → RAG retrieval boost | v0.6.0 tagged; KG + first quiz work |
| **v0.7 (Cognition) + Tier 2 Freeze — GATE 3** | W30 | W27–W30 | Mastery schema; quiz submit hook; cohort mastery; BKT scaffold; Tier 2 contracts (6–9) frozen; DDM-3 (5 demo students) | ADR-017 (cognitive model) accepted; mastery estimator v1 (WMA); cognitive hardening; adaptive spike (W29–W31); GPM-3 (demo script skeleton) | Mastery UI; cohort mastery view; recommendation UI design | TM-8 (quiz + mastery E2E); Tier 2 sign-off; v0.7 validation; DDM-3 verification | IM-10: quiz → mastery update E2E | **v0.7.0 tagged; GATE 3 signed; contracts 6–9 frozen** |
| **v0.8 (Adaptation)** | W34 | W31–W34 | Recommendation API; adaptive quiz endpoint; analytics endpoints; IRT decision | Adaptive engine (priority scoring + F-7 fallback); ADR-018 accepted; SM-2; recommendation engine v1; difficulty adjustment; adaptation eval harness (TM-9); DDM-4 (20 quizzes); GPM-5 (demo script v1) | Recommendation UI (IM-11); adaptive quiz UI; analytics dashboard (4 charts); slide deck (GPM-4) | Adaptive monitoring; TM-9 sign-off; DDM-4 verification; analytics monitoring | IM-11: recommendation shown; IM-12: quiz difficulty adapts | v0.8.0 tagged; adaptive engine + analytics work |
| **v0.9 (Analytics) + Feature Freeze — GATE 4** | W38 | W35–W38 | Admin API; notification system; DDM-6 export; Feature Freeze sign | Recommendation iteration; DDM-5 (5 RAG questions); GPM-6 (deck v1 advisor); v1.0 AI/ML baselines; GPM-7 (demo data curated) | Admin dashboard UI; notification bell; UX polish; WCAG 2.1 AA; v0.9 demo UI | TM-10 (bug bash #1); TM-11 (≥60% coverage); DDM-6 verification; Feature Freeze sign | IM-13: analytics ↔ real DB data | **v0.9.0 tagged; GATE 4 signed; Feature Freeze active** |
| **v1.0-rc (Hardening) + Code Freeze — GATE 5** | W42 | W39–W42 | Backend optimization (P95<2s); security (TM-13); auth hardening; DR drill support; Code Freeze sign; v1.0-rc tag | RAG pipeline optimization; LLM latency; AI/ML security; v1.0 baselines; dry-run #1 support | Frontend performance; frontend security; DM-16 (README + demo video); GPM-9 (fallback video); UI finalize | TM-12 (50 users, P95<2s); TM-13 (security); TM-14 (≤3 P1s); TM-15 (smoke tests); DM-14 (4 runbooks); DR drill (<1h); DDM-8 (demo data frozen); dry-run #1 (GPM-10); Code Freeze sign | IM-14: full system under load on staging | **v1.0.0-rc tagged; GATE 5 signed; Code Freeze active** |
| **v1.0 (Graduation) — FINAL** | W44 | W43–W44 | Prod deploy; hotfix standby; v1.0 tag | Prod AI/ML verify; dry-run #2 support; AI depth section; presentation standby | Prod frontend verify; slide deck v2; demo flow finalize; presentation standby | Prod deploy + monitor; IM-15 verification; dry-run #2 (GPM-11); dry-run #3 (GPM-12); artifact submission; on-call during presentation | IM-15: prod live end-to-end | **v1.0.0 tagged; graduation delivered 🎓** |

### 12.2 Quality Gate Traceability

| Gate | Target | Sign-off Criteria | Relevant Weeks | Pod Contributions |
| --- | --- | --- | --- | --- |
| G1 — v0.4 Thin MVP | W16 | 7 criteria (pre-loaded PDF, OCR run, embeddings in vector DB, chat UI, cited answer, public URL, survives 5 questions) | W9–W16 | All Pods (Pod B leads AI pipeline; Pod A + Pod C wire thin MVP; Pod D validates) |
| G2 — v0.5 + Tier 1 Freeze | W20 | 12 criteria (student can register/login/enroll; instructor creates course + uploads PDF; OCR <5min; chunks + embeddings; cited answer; public URL; CI ≥40%; survives 10-min demo; 15 ADRs; 5 contracts; architecture diagram; pod leads sign) | W5–W20 | All Pods |
| G3 — v0.7 + Tier 2 Freeze | W30 | 6 criteria (v0.7 demoed; ADR-017 merged; 4 Tier 2 contracts documented; KG ≥200 concepts + TM-7; quiz+mastery E2E TM-8; pod leads sign) | W21–W30 | All Pods (Pod B leads KG + cognitive model) |
| G4 — v0.9 + Feature Freeze | W38 | 7 criteria (v0.9 demoed; P1 bugs closed/waived; coverage ≥60% TM-11; ≥3 cross-trained; deck v1 reviewed GPM-6; demo data curated DDM-5; pod leads sign) | W31–W38 | All Pods |
| G5 — v1.0-rc + Code Freeze | W42 | 10 criteria (v1.0-rc tagged + staging; bug bash #2 ≤3 P1s TM-14; security TM-13; perf TM-12; runbooks DM-14; DR drill; architecture + ADR index DM-15; README + demo DM-16; demo data frozen DDM-8; pod leads sign) | W39–W42 | All Pods (Pod D leads hardening) |

### 12.3 Integration Milestone Traceability

| IM | Week | Components | Relevant Pod Tasks (Week) |
| --- | --- | --- | --- |
| IM-1 | W6 | Frontend ↔ Auth ↔ DB | Pod A W5–W6 (auth); Pod C W5 (auth UI); Pod D W3 (PG) |
| IM-2 | W8 | Frontend ↔ Course API ↔ Storage | Pod A W6–W8 (course CRUD + upload + integration); Pod C W6–W8 (course UI + upload UI); Pod D W6 (MinIO) |
| IM-3 | W10 | Upload → OCR job → DB | Pod B W9–W10 (OCR pipeline); Pod A W9 (documents table) |
| IM-4 | W13 | OCR → Chunking → Embeddings → VectorDB | Pod B W9–W13 (full pipeline); Pod A W12–W13 (Qdrant) |
| IM-5 | W15 | VectorDB → Reranker → RAG | Pod B W13–W15 (reranker + RAG); Pod A W15 (`/v1/rag/query`) |
| IM-6 | W16 | RAG ↔ Chat API ↔ Chat UI (thin MVP) | Pod A W16 (thin MVP endpoint); Pod C W9–W16 (chat UI); Pod B W14–W16 (RAG) |
| IM-7 | W17 | Full student flow (auth → course → upload → chat) | Pod A W5–W17 (full backend); Pod C W5–W17 (full UI); Pod D W17 (E2E test TM-5) |
| IM-8 | W24 | OCR → Concept extraction → KG | Pod B W23–W24 (extraction); Pod A W23–W24 (KG API) |
| IM-9 | W25 | KG → RAG retrieval boost | Pod B W25 (KG-backed retrieval); Pod A W14 (retrieval service) |
| IM-10 | W28 | Quiz generation → Quiz UI → Mastery update | Pod A W26–W28 (quiz API + mastery hook); Pod B W26–W28 (quiz gen + mastery service); Pod C W26–W28 (quiz UI + mastery UI) |
| IM-11 | W32 | Mastery → Adaptive engine → Recommendation UI | Pod B W31–W32 (adaptive engine); Pod A W31 (recommendation API); Pod C W31–W32 (recommendation UI) |
| IM-12 | W33 | Adaptive engine → Quiz difficulty | Pod B W32–W33 (difficulty adjustment); Pod A W32 (adaptive quiz endpoint); Pod C W32–W33 (adaptive quiz UI) |
| IM-13 | W35 | Analytics dashboard ↔ real DB data | Pod A W32, W34 (analytics endpoints); Pod C W34 (analytics dashboard UI) |
| IM-14 | W41 | Full system on staging under load | Pod D W39 (TM-12 load test); Pod A + Pod B W39 (perf optimization); Pod C W39 (frontend perf) |
| IM-15 | W43 | Production deployment end-to-end | Pod D W43 (prod deploy + monitor); Pod A W43 (prod deploy + hotfix standby); Pod B + Pod C W43 (prod verification + standby) |

### 12.4 Testing Milestone Traceability

| TM | Week | Milestone | Relevant Pod Tasks (Week) |
| --- | --- | --- | --- |
| TM-1 | W4 | Unit test infra in CI | Pod D W2–W4 (pytest + Vitest + eval harness in CI) |
| TM-2 | W8 | Auth + course CRUD ≥80% coverage | Pod A W5–W8 (auth + course tests); Pod D W8 (TM-2 sign-off) |
| TM-3 | W12 | OCR pipeline integration tests | Pod B W9 (5-PDF tests); Pod D W9–W12 (CI integration + TM-3 sign-off) |
| TM-4 | W15 | RAG golden set v1 (50 Q&A) | Pod B W15 (eval harness + golden set); Pod D W15 (CI integration) |
| TM-5 | W17 | E2E Playwright student flow | Pod D W17 (E2E test); Pod A + Pod C W17 (full student flow integration) |
| TM-6 | W20 | Coverage ≥40% critical paths | Pod D W18–W20 (coverage validation + sign-off) |
| TM-7 | W24 | KG sanity tests | Pod D W23–W24 (KG sanity tests + sign-off); Pod B W23 (populated KG) |
| TM-8 | W28 | Quiz + mastery E2E | Pod D W28 (E2E test); Pod A + Pod B + Pod C W26–W28 (quiz + mastery loop) |
| TM-9 | W33 | Adaptation eval harness | Pod B W32–W33 (eval harness); Pod D W33 (CI integration + sign-off) |
| TM-10 | W36 | Bug bash #1 | Pod D W35–W36 (bug bash prep + execution); All Pods W36–W37 (bug fixing) |
| TM-11 | W38 | Coverage ≥60% critical paths | Pod D W37–W38 (coverage validation + sign-off) |
| TM-12 | W39 | Load test (50 users, P95<2s) | Pod D W39 (load test); Pod A + Pod B W39 (perf optimization) |
| TM-13 | W40 | Security review | Pod D W40 (TM-13 coordination); Pod A + Pod B + Pod C W40 (security fixes) |
| TM-14 | W41 | Bug bash #2 (≤3 P1s) | Pod D W41 (bug bash); All Pods W41 (P1 fixing) |
| TM-15 | W42 | Smoke tests prod-like env | Pod D W42 (smoke tests + sign-off) |

### 12.5 Documentation Milestone Traceability

| DM | Week | Artifact | Owner | Relevant Pod Tasks (Week) |
| --- | --- | --- | --- | --- |
| DM-1 | W2 | `docs/mvp.md` | TPM | TPM W2 (MVP sign-off) |
| DM-2 | W4 | ADRs 001–005 | TPM | Pod A W1–W4 (ADR drafts + merge) |
| DM-3 | W4 | `CONTRIBUTING.md` + `README.md` | TPM | Pod A W4 (co-author) |
| DM-4 | W8 | API reference v1 (OpenAPI) | A-Lead | Pod A W2 (OpenAPI config) + W8 (publish) |
| DM-5 | W8 | Docusaurus site | C-Lead | Pod C W8 (Docusaurus build + deploy) |
| DM-6 | W11 | `docs/ocr.md` + `docs/chunking.md` | B-Lead | Pod A + Pod B W11 (co-author) |
| DM-7 | W15 | `docs/rag.md` | B-Lead | Pod A + Pod B W15 (co-author; finalized W19) |
| DM-8 | W19 | ADRs 1–15 complete | TPM | Pod A W1–W19 (ADR drafts + reviews + merge) |
| DM-9 | W20 | Architecture diagram v1 | TPM | Pod A W20 (co-author) |
| DM-10 | W23 | `docs/kg.md` | B-Lead | Pod A + Pod B W23 (co-author) |
| DM-11 | W27 | `docs/student-model.md` | B-Lead | Pod B W27 (author) |
| DM-12 | W31 | `docs/adaptive.md` | B-Lead | Pod B W31 (author) |
| DM-13 | W36 | Instructor + student quickstarts | C-Lead | Pod A + Pod C W36 (co-author) |
| DM-14 | W39 | Runbooks (deploy, rollback, DR, on-call) | D-Lead | Pod D W39 (author) |
| DM-15 | W41 | Final architecture diagram + ADR index | TPM | Pod A W41 (co-author) |
| DM-16 | W42 | README polish + demo recording | TPM + C-Lead | Pod C W41 (co-author; finalized W42) |

---

## 13. Release Execution Plan

For each release defined in the Master Roadmap Version Roadmap table, this section identifies the release goal, included functionality, contributing weeks, Pod responsibilities, integration requirements, testing requirements, release validation, and Definition of Done. No releases are invented.

### 13.1 v0.1 (Skeleton) — W6

- **Release goal:** Establish the project foundation: repo, CI, dev env, empty Next.js + FastAPI, auth scaffold, hello-world deploy.
- **Included functionality:** Empty FastAPI app with `/health`; empty Next.js app with login page; Postgres with `users` table; CI scaffold; 3 environments; 5 ADRs; OOS list signed.
- **Contributing weeks:** W1–W6 (P0 Pre-Flight, with W5–W6 spilling into early P1).
- **Pod responsibilities:** Pod A (FastAPI + DB + auth scaffold); Pod B (PAL skeleton + spike prep); Pod C (Next.js + design tokens + login page); Pod D (CI + envs + MinIO); TPM (OOS + ADRs + MVP definition).
- **Integration requirements:** Both apps deployed to staging; Postgres reachable from backend; CI green on `main`.
- **Testing requirements:** CI scaffold green on dummy PR; smoke test on staging.
- **Release validation:** Staging URL accessible; `/health` returns 200; login page renders.
- **Definition of Done:** Git tag `v0.1.0` exists; GitHub Release published; advisor notified.

### 13.2 v0.2 (Foundations) — W8

- **Release goal:** Ship the boring-but-required backbone: auth, user management, course management, file upload, basic UI shell.
- **Included functionality:** Register/login/JWT; RBAC (3 roles); profile CRUD; course CRUD; file upload to MinIO; async job infra; LiteLLM gateway; observability stack; Docusaurus site; API reference v1; Contract 10 (auth token format) frozen.
- **Contributing weeks:** W5–W8 (P1 Foundations).
- **Pod responsibilities:** Pod A (auth + RBAC + course CRUD + upload + Contract 10); Pod B (spikes + PAL providers + LiteLLM provider); Pod C (course UI + profile + Docusaurus); Pod D (async infra + observability + MinIO + LiteLLM gateway deploy + TM-2).
- **Integration requirements:** IM-2 (frontend ↔ course API ↔ storage); auth token format frozen; API reference published.
- **Testing requirements:** TM-2 (≥80% auth + course CRUD coverage); E2E Playwright test for upload flow.
- **Release validation:** IM-2 verified; TM-2 met; coverage report posted.
- **Definition of Done:** Git tag `v0.2.0` exists; GitHub Release published; advisor notified.

### 13.3 v0.3 (Ingestion) — W12

- **Release goal:** Ship the OCR + chunking + embedding pipeline. PDF parsed, text visible in UI.
- **Included functionality:** OCR pipeline v1 (PaddleOCR + Tesseract + Document AI fallback, Arabic preprocessing); `documents` + `chunks` tables; `/v1/documents/{id}` + chunks endpoint; Qdrant deployed; embedding batch job (1000 chunks); ADR-009 (chunking strategy) accepted.
- **Contributing weeks:** W9–W12 (P2 AI Pipeline, first 4 weeks).
- **Pod responsibilities:** Pod A (documents/chunks tables + endpoints + Qdrant deploy); Pod B (OCR pipeline + chunking + embedding batch + 20-PDF golden set + ADR-009); Pod C (extracted text viewer + chunks viewer + chat UI scaffold); Pod D (OCR integration tests + TM-3 + cost monitoring).
- **Integration requirements:** IM-4 (full ingestion pipeline end-to-end); Qdrant collection created.
- **Testing requirements:** TM-3 (5-PDF integration tests); ≥90% OCR success on 20-PDF golden set; cost < $0.50 per 1000 chunks.
- **Release validation:** IM-4 verified; TM-3 met; demo passes on staging.
- **Definition of Done:** Git tag `v0.3.0` exists; GitHub Release published.

### 13.4 v0.4 (Thin MVP) — W16 — GATE 1

- **Release goal:** Prove the AI pipeline works end-to-end. Pre-loaded PDF + chat UI; cited answer in browser.
- **Included functionality:** `/v1/search`; `/v1/retrieve`; `/v1/rag/query`; thin MVP chat endpoint; hybrid retrieval (BM25 + vector); reranker (bge-reranker-v2-m3); RAG service with citations; RAG eval harness v1 (50 Q&A); DDM-1 (demo PDF set); ADRs 7–11 drafted; ADR-010 (embedding I/O) drafted.
- **Contributing weeks:** W13–W16 (P2 AI Pipeline, weeks 5–8).
- **Pod responsibilities:** Pod A (search/retrieve/rag endpoints + thin MVP endpoint + deploy); Pod B (hybrid retrieval + reranker + RAG service + eval harness + IM-5 + DDM-1 + PB-02 check); Pod C (search UI + chat UI + citation rendering + chat UI wired to thin MVP); Pod D (TM-4 in CI + Gate 1 validation + RAG load test + monitoring).
- **Integration requirements:** IM-5 (query returns cited answer via curl); IM-6 (RAG ↔ chat API ↔ chat UI).
- **Testing requirements:** TM-4 (RAG eval in CI with faithfulness/relevance thresholds); PB-02 trigger check; 5 demo questions survive without crash.
- **Release validation:** Gate 1 sign-off (7 criteria); demo monitoring report; smoke test.
- **Definition of Done:** Git tag `v0.4.0` exists; **Gate 1 signed by all pod leads + TPM**; advisor notified; if v0.4 doesn't ship, PB-06 triggers.

### 13.5 v0.5 (Full MVP) + Tier 1 Architecture Freeze — W20 — GATE 2

- **Release goal:** Ship the full MVP: auth + courses + uploads + RAG with citations + multi-doc + chat API with SSE + session persistence. Sign Tier 1 Architecture Freeze.
- **Included functionality:** Full chat API (SSE + sessions); multi-doc RAG (single-course); ADRs 1–15 complete; 5 Tier 1 interface contracts frozen; architecture diagram v1; TM-5 (E2E test); TM-6 (≥40% coverage); GPM-0 (demo backlog); on-call rotation.
- **Contributing weeks:** W17–W20 (P2 AI Pipeline, final 4 weeks).
- **Pod responsibilities:** Pod A (full chat API + multi-doc API + ADRs 12–15 + Tier 1 contracts + architecture diagram + v0.5 tag); Pod B (streaming LLM + PB-02 fixes + multi-doc retrieval + ADRs 7–11 accepted + KG design + GPM-0); Pod C (chat UI wired + session list + multi-doc citations + v0.5 demo UI + KG viz research); Pod D (TM-5 + TM-6 + Tier 1 sign-off + v0.5 validation + on-call prep).
- **Integration requirements:** IM-7 (full student flow E2E green); 22-week graduation runway begins.
- **Testing requirements:** TM-5 (E2E Playwright); TM-6 (≥40% coverage); bug count ≤ 5 P1s.
- **Release validation:** Gate 2 sign-off (12 criteria); v0.5 validation report.
- **Definition of Done:** Git tag `v0.5.0` exists; **Gate 2 signed by all pod leads + TPM**; Tier 1 Freeze active; advisor notified. **This is the most important gate — if missed, every subsequent date slips.**

### 13.6 v0.6 (Knowledge layer) — W26

- **Release goal:** Ship the KG: concept extraction, KG API + viz, KG-backed retrieval boost, first quiz.
- **Included functionality:** KG schema (ADR-016); concept extraction pipeline (ADR-017); Neo4j deployed; KG populated (200+ concepts); KG API + KG viz UI; KG-backed retrieval boost (faithfulness ↑5%); quiz generation v1; quiz API + UI; DDM-2 (demo dataset v1); GPM-2 (graduation outline v0).
- **Contributing weeks:** W21–W26 (P3 Knowledge & Cognition, first 6 weeks; includes Dec holiday lull).
- **Pod responsibilities:** Pod A (KG API + quiz API + v0.6 tag); Pod B (KG schema + extraction + retrieval boost + quiz generation + cognitive spike + GPM-2); Pod C (KG viz UI + quiz UI + concept detail); Pod D (TM-7 + DDM-2 + Neo4j deploy + cross-training).
- **Integration requirements:** IM-8 (KG populated from new upload); IM-9 (KG → RAG retrieval boost).
- **Testing requirements:** TM-7 (KG sanity tests); faithfulness ↑5% on golden set.
- **Release validation:** TM-7 signed; DDM-2 verified.
- **Definition of Done:** Git tag `v0.6.0` exists; advisor notified.

### 13.7 v0.7 (Cognition) + Tier 2 Architecture Freeze — W30 — GATE 3

- **Release goal:** Ship the cognitive model: mastery estimator v1 (WMA), quiz + mastery end-to-end. Sign Tier 2 Architecture Freeze.
- **Included functionality:** Mastery schema; mastery estimator v1 (WMA); ADR-017 accepted; cognitive model hardening; BKT scaffold; quiz + mastery E2E; cohort mastery; 4 Tier 2 interface contracts frozen; DDM-3 (5 demo students); GPM-3 (demo script skeleton).
- **Contributing weeks:** W27–W30 (P3 Knowledge & Cognition, final 4 weeks; includes Jan exam crunch W25–W27).
- **Pod responsibilities:** Pod A (mastery schema + quiz submit hook + cohort mastery + BKT scaffold + Tier 2 contracts + DDM-3 + v0.7 tag); Pod B (ADR-017 + mastery estimator + cognitive hardening + adaptive spike + GPM-3); Pod C (mastery UI + cohort mastery view + recommendation UI design + v0.7 demo UI); Pod D (TM-8 + Tier 2 sign-off + v0.7 validation + DDM-3 verification).
- **Integration requirements:** IM-10 (quiz generation → quiz UI → mastery update).
- **Testing requirements:** TM-8 (quiz + mastery E2E); PB-05 status (exam crunch).
- **Release validation:** Gate 3 sign-off (6 criteria); v0.7 validation report.
- **Definition of Done:** Git tag `v0.7.0` exists; **Gate 3 signed by all pod leads + TPM**; Tier 2 Freeze active; advisor notified.

### 13.8 v0.8 (Adaptation) — W34

- **Release goal:** Ship the adaptive engine: next-best-concept recommendation, difficulty adjustment, SM-2 spaced repetition, learning analytics dashboard (4 charts, 30-day window).
- **Included functionality:** Recommendation API + UI; adaptive engine (priority scoring + F-7 fallback); ADR-018 accepted; SM-2; recommendation engine v1 (content + rule-based); adaptive quiz with difficulty adjustment; adaptation eval harness (TM-9); analytics dashboard (4 charts); IRT activation decision (conditional per C-9); DDM-4 (20 quizzes); GPM-5 (demo script v1); GPM-4 (slide deck template + first 5 slides); DM-12 (adaptive doc).
- **Contributing weeks:** W31–W34 (P4 Adaptation & Analytics, first 4 weeks).
- **Pod responsibilities:** Pod A (recommendation API + adaptive quiz endpoint + analytics endpoints + IRT decision + v0.8 tag); Pod B (adaptive engine + ADR-018 + SM-2 + recommendation engine + difficulty adjustment + adaptation eval + DDM-4 + GPM-5); Pod C (recommendation UI + adaptive quiz UI + analytics dashboard UI + slide deck + v0.8 demo video); Pod D (TM-9 + DDM-4 verification + analytics monitoring + cross-training).
- **Integration requirements:** IM-11 (mastery → adaptive engine → recommendation UI); IM-12 (adaptive engine → quiz difficulty).
- **Testing requirements:** TM-9 (adaptation eval harness); mastery gain >10% vs random (or PB-03).
- **Release validation:** TM-9 met; DDM-4 verified.
- **Definition of Done:** Git tag `v0.8.0` exists; advisor notified.

### 13.9 v0.9 (Analytics) + Feature Freeze — W38 — GATE 4

- **Release goal:** Ship feature-complete: admin dashboard (minimal), notifications, accessibility (WCAG 2.1 AA), bug bash #1 closed. Sign Feature Freeze.
- **Included functionality:** Admin API + UI; notification system; DDM-5 (5 RAG questions); GPM-6 (deck v1 reviewed); v1.0 AI/ML baselines; GPM-7 (demo data curated); DDM-6 (demo data snapshot); TM-10 (bug bash #1); TM-11 (≥60% coverage); Feature Freeze active.
- **Contributing weeks:** W35–W38 (P4 Adaptation & Analytics, final 4 weeks).
- **Pod responsibilities:** Pod A (admin API + notification system + DB perf prep + Feature Freeze sign + DDM-6 export + v0.9 tag); Pod B (recommendation iteration + DDM-5 + GPM-6 + baselines + GPM-7); Pod C (admin UI + notification bell + UX polish + WCAG 2.1 AA + v0.9 demo UI); Pod D (TM-10 + TM-11 + DDM-6 verification + Feature Freeze sign).
- **Integration requirements:** IM-13 (analytics ↔ real DB data).
- **Testing requirements:** TM-10 (bug bash #1, 50+ bugs triaged); TM-11 (≥60% coverage); 0 P1s (or waived); axe-core clean.
- **Release validation:** Gate 4 sign-off (7 criteria); v0.9 validation report.
- **Definition of Done:** Git tag `v0.9.0` exists; **Gate 4 signed by all pod leads + TPM**; Feature Freeze active; advisor notified. Hard rule: no new features after W38 even if v0.9 is incomplete (R-20 mitigation).

### 13.10 v1.0-rc (Hardening) + Code Freeze — W42 — GATE 5

- **Release goal:** Ship the hardened release candidate: perf (P95 < 2s under 50 users), security (0 critical/high), DR drill (<1h), runbooks, final architecture + ADR index, README polish, demo video, frozen demo data. Sign Code Freeze.
- **Included functionality:** Performance optimizations (caching, indexes, connection pool, reranker batching); security hardening (rate limiting, MFA scaffold, CSP, SAST clean); DR drill; 4 runbooks; final architecture diagram + ADR index; README + demo video; fallback demo video (GPM-9); DDM-7 (demo data on prod-like); DDM-8 (demo data frozen); TM-12 (load test); TM-13 (security); TM-14 (bug bash #2 ≤3 P1s); TM-15 (smoke tests); dry-run #0 (GPM-8); dry-run #1 (GPM-10); Code Freeze active.
- **Contributing weeks:** W39–W42 (P5 Hardening).
- **Pod responsibilities:** Pod A (backend optimization + security + auth hardening + DM-15 + DR drill support + Code Freeze sign + v1.0-rc tag); Pod B (RAG optimization + AI/ML security + v1.0 baselines + dry-run #1 support); Pod C (frontend performance + frontend security + DM-16 + GPM-9 + UI finalize + demo flow polish); Pod D (TM-12 + TM-13 + TM-14 + TM-15 + DM-14 + DR drill + DDM-7 + DDM-8 + dry-run #0 + dry-run #1 + Code Freeze sign).
- **Integration requirements:** IM-14 (full system under load on staging).
- **Testing requirements:** TM-12 (50 users, P95 < 2s); TM-13 (0 critical/high); TM-14 (≤3 P1s); TM-15 (smoke tests green).
- **Release validation:** Gate 5 sign-off (10 criteria); v1.0-rc validation report.
- **Definition of Done:** Git tag `v1.0.0-rc` exists; **Gate 5 signed by all pod leads + TPM**; Code Freeze active; advisor notified. Post-freeze: only P0/P1 fixes with TPM + D-Lead approval.

### 13.11 v1.0 (Graduation) — W44 — FINAL

- **Release goal:** Deploy to production, deliver the graduation presentation, submit all artifacts.
- **Included functionality:** Production deployment (public URL, TLS, monitoring); IM-15 verified; dry-run #2 (GPM-11); dry-run #3 (GPM-12 dress rehearsal); slide deck v2; artifact submission; graduation presentation delivered.
- **Contributing weeks:** W43–W44 (P6 Graduation).
- **Pod responsibilities:** Pod A (prod deploy + hotfix standby + v1.0 tag); Pod B (prod AI/ML verify + dry-run support + AI depth section + presentation standby); Pod C (prod frontend verify + slide deck v2 + demo flow finalize + presentation standby); Pod D (prod deploy + monitor + IM-15 verification + dry-run #2 + dry-run #3 + artifact submission + on-call during presentation).
- **Integration requirements:** IM-15 (production deployment end-to-end).
- **Testing requirements:** Smoke tests on prod; dry-run #3 passes.
- **Release validation:** All Graduation Success criteria met (Roadmap §Success Criteria): live deployed v1.0 at public URL; presentation delivered with live demo that does not crash; MVP loop works end-to-end on demo data; at least one adaptive behavior demonstrated; all graduation artifacts submitted; defensible "what would you do differently" answer informed by retrospectives.
- **Definition of Done:** Git tag `v1.0.0` exists; GitHub Release published; production URL live; presentation delivered; all artifacts submitted; graduation committee confirms receipt. **Graduation success. 🎓**

---

## 14. Critical Path

The critical path is the longest chain of dependent tasks that determines the minimum project duration. Any slip on the critical path slips the graduation date. The critical path below is derived from the Master Roadmap §Critical Path and mapped to the weekly tasks in this plan.

### 14.1 Critical Path Chain

```
Stack lock (W1)
  → OCR pipeline (W9–W10)
    → Chunking (W11)
      → Embeddings (W12)
        → Vector DB (W13)
          → RAG (W14–W15)
            → v0.4 Thin MVP (W16)  [GATE 1 — early warning]
              → Full student flow (W17–W18)
                → Tier 1 Architecture Freeze (W20)  [GATE 2]
                  → Concept extraction (W23)
                    → KG (W24)
                      → Cognitive model spike (W25–W27)  [research]
                        → Cognitive model impl (W28)
                          → Tier 2 Architecture Freeze (W30)  [GATE 3]
                            → Adaptive spike (W29–W31)  [research, parallel]
                              → Adaptive engine (W31–W33)
                                → Feature Freeze (W38)  [GATE 4]
                                  → Hardening (W39–W41)
                                    → Code Freeze (W42)  [GATE 5]
                                      → Prod deploy (W43)
                                        → Graduation (W44)  [FINAL]
```

### 14.2 Critical Path Slack Analysis

| Segment | Planned Duration | Allowable Slip Before Graduation Slips | Trigger if Slip Exceeds |
| --- | --- | --- | --- |
| Stack lock → Tier 1 Freeze (W1–W20) | 19 weeks | 1 week | Switch Qdrant to pgvector (F-1); switch BGE-M3 to OpenAI embeddings (F-3); descope multi-doc RAG |
| Tier 1 Freeze → Tier 2 Freeze (W20–W30) | 10 weeks | **2 weeks** (improved by research spikes) | Descope KG depth; defer Tier 2 by 2 weeks; trigger PB-05 |
| Tier 2 Freeze → Feature Freeze (W30–W38) | 8 weeks | 1 week | Descope recommendation engine v2 features; trigger PB-03 |
| Feature Freeze → Code Freeze (W38–W42) | 4 weeks | 0 weeks (hard) | Cut hardening scope to must-haves |
| Code Freeze → Graduation (W42–W44) | 2 weeks | 0 weeks (hard) | Use recorded demo fallback (GPM-9) |

**Total critical path slack: ~4 weeks.**

### 14.3 Critical Path Drivers (Why Each Task Can Affect the Schedule)

- **Stack lock (W1):** If the stack isn't locked by EOD W1, every downstream decision is at risk. ADRs 1–5 are the binding lock. **Slip here cascades to all of P1 and P2.**
- **OCR pipeline (W9–W10):** Every downstream AI component depends on having text. If OCR fails on real PDFs, everything stalls. **Mitigated by PB-01 (W10 trigger) and F-6 (Document AI fallback).** If PB-01 triggers and is not resolved by W11, the entire AI pipeline slips.
- **Chunking (W11):** Embeddings depend on chunks. If chunking is delayed, embeddings are delayed, vector DB is empty, RAG has nothing to retrieve. **Slip here delays W12 embeddings, W13 vector DB, W14 retrieval, W15 RAG, W16 thin MVP.**
- **Embeddings (W12):** Vector DB depends on embeddings. If BGE-M3 is too slow or unavailable, F-3 (OpenAI embeddings) triggers — a 1-day swap. **Slip here delays W13 vector DB, W14 retrieval, W15 RAG, W16 thin MVP.**
- **Vector DB (W13):** RAG depends on working retrieval. If Qdrant ops are too heavy, F-1 (pgvector) triggers — a 1-day swap. **Slip here delays W14 retrieval, W15 RAG, W16 thin MVP.**
- **RAG (W14–W15):** The thin MVP (W16) depends on RAG. If RAG quality is unacceptable, PB-02 triggers — must be resolved by EOD W17 (default branch A+D combined). **Slip here delays W16 thin MVP (Gate 1).**
- **v0.4 Thin MVP (W16):** The early warning gate. If it doesn't ship, PB-06 triggers and the entire P2/P3 timeline is replanned. **This is the single most important date in the plan.**
- **Full student flow (W17–W18):** v0.5 depends on the full flow working. **Slip here delays W20 Tier 1 Freeze.**
- **Tier 1 Architecture Freeze (W20):** Without frozen interfaces, P3 thrashes as Pod B "improves" the chunk schema and breaks Pod A's ingestion service. **Slip here delays all of P3 and risks P4.**
- **Concept extraction (W23):** KG depends on extraction. **Slip here delays W24 KG, W25 retrieval boost, W28 cognitive model (which uses KG for prereqs).**
- **KG (W24):** Cognitive model uses KG for prereqs. Adaptive engine uses KG for concept selection. **Slip here delays W28 cognitive model, W31 adaptive engine.**
- **Cognitive model spike (W25–W27):** Adaptive engine depends on mastery estimates. The spike reduces research risk before commitment. **Slip here delays W28 cognitive model impl, W30 Tier 2 Freeze.**
- **Cognitive model impl (W28):** Adaptive engine depends on mastery. **Slip here delays W31 adaptive engine, W33 adaptation eval, W34 v0.8.**
- **Tier 2 Architecture Freeze (W30):** Without frozen Tier 2 interfaces, P4 thrashes as Pod B iterates on the mastery schema and breaks the adaptive engine's input. **Slip here delays all of P4.**
- **Adaptive spike (W29–W31):** Reduces research risk before adaptive engine productionization. If the spike fails, F-7 (rule-based adaptive) triggers — 0-day swap. **Slip here delays W31 adaptive engine, W33 adaptation eval.**
- **Adaptive engine (W31–W33):** The latest-starting critical component. Most exposed to upstream slips. **Slip here delays W34 v0.8, W38 Feature Freeze.**
- **Feature Freeze (W38):** Hard rule: no new features after W38. If v0.8 is not done by W34, v0.9 scope is cut. **Slip here delays W39–W42 hardening, W42 Code Freeze.**
- **Hardening (W39–W41):** Perf, security, DR, docs. Front-loaded per R-17 mitigation. **Slip here delays W42 Code Freeze.**
- **Code Freeze (W42):** Hard gate. Only P0/P1 fixes after this. **Slip here delays W43 prod deploy, W44 graduation.**
- **Prod deploy (W43):** Must happen in W43, not W44, to leave W44 for the dress rehearsal + presentation. **Slip here risks W44 graduation.**
- **Graduation (W44):** The hard deadline. Cannot slip.

### 14.4 Near-Critical Path (Parallel Chains)

These are not on the critical path but become critical if they slip badly:

- **Auth + course CRUD (W5–W8):** Must be done by W8 or P2 starts late. (IM-1, IM-2)
- **Chat UI + citation rendering (W15–W16):** Must be done by W17 or v0.5 demo fails.
- **Quiz UI (W26):** Must be done by W27 or cognitive model has no input data.
- **Analytics dashboard (W34–W35):** Must be done by W36 or Feature Freeze slips.
- **Documentation (continuous):** Must be ≥80% by W41 or Code Freeze slips.

---

## 15. Risk Register

This risk register is sourced from the Master Roadmap §Risk Register (32 risks) plus risks identified during the planning of this 44-week execution plan. Roadmap-defined risks are marked `[Roadmap]`; planning-identified risks are marked `[Planning]`.

| ID | Risk | Source | Affected Weeks | Affected Pods | Impact | Mitigation |
| --- | --- | --- | --- | --- | --- | --- |
| R-01 | OCR quality too low on real-world PDFs (scanned, rotated, mixed-language) | [Roadmap] L4×I4=16 🔴 | W5 (spike), W9–W10 (pipeline) | Pod B | Major — blocks AI pipeline | Spike in W5; PaddleOCR + Document AI fallback (F-6); 20-PDF golden set; A/B test by W10; PB-01 trigger if <90% success |
| R-02 | RAG quality unacceptable (hallucinations, wrong citations) | [Roadmap] L4×I4=16 🔴 | W14–W16, W17 eval | Pod B | Major — blocks thin MVP + full MVP | Hybrid retrieval + reranker; eval harness from W15; prompt iteration; guardrails; PB-02 trigger if faithfulness <0.7 |
| R-03 | Adaptive engine algorithm fails to converge or behaves erratically | [Roadmap] L3×I4=12 🔴 | W29–W33 | Pod B | Major — blocks v0.8 | Research spike W29–W31; simulated eval harness (TM-9); simple policy first (priority scoring), then ML; F-7 fallback (rule-based); PB-03 trigger |
| R-04 | Knowledge Graph construction produces noisy/incorrect relations | [Roadmap] L3×I3=9 🟡 | W23–W24 | Pod B | Moderate — affects retrieval boost + cognitive model | LLM-assisted extraction with human-in-loop sampling; provenance tracking; KG sanity tests (TM-7); post-extraction filtering (W24) |
| R-05 | Vector DB (Qdrant) ops too heavy for Pod D to maintain | [Roadmap] L3×I3=9 🟡 | W12+ (continuous) | Pod D + Pod B | Moderate — affects retrieval | Cross-train Pod B engineer; F-1 fallback (pgvector); monitoring from W13 |
| R-06 | LLM API cost overruns | [Roadmap] L3×I3=9 🟡 | Continuous | Pod D | Moderate — budget risk | LiteLLM proxy with cost tracking; per-user quota; cache common queries; F-4 fallback (cheaper model); alert if cost > $5/day |
| R-07 | LLM API provider changes terms / deprecates model | [Roadmap] L3×I4=12 🔴 | Continuous | Pod B | Major — affects RAG + quiz gen + extraction | LiteLLM gateway abstracts provider; ≥2 providers configured; ADR for fallback model |
| R-08 | Embedding model dim mismatch after Architecture Freeze | [Roadmap] L2×I4=8 🟡 | Post-W20 | Pod B | Moderate — requires re-embedding | Freeze model choice at W12 (ADR-008); versioned embeddings with model_id field |
| R-09 | Database performance collapses under load | [Roadmap] L3×I3=9 🟡 | W39 (load test), continuous | Pod A + Pod D | Moderate — affects NFR-1 | Indexes from W37; load test at W39 (TM-12); connection pooling; read replicas if needed |
| R-10 | Frontend bundle too large; first load >5s | [Roadmap] L3×I2=6 🟡 | W34+, W39 | Pod C | Minor — affects UX | Code splitting; lazy loading; bundle analysis in CI; Next.js SSR; Lighthouse in CI |
| R-11 | Neo4j ops too heavy; team can't maintain | [Roadmap] L3×I3=9 🟡 | W22+ (continuous) | Pod D + Pod B | Moderate — affects KG | F-2 fallback (JSONB in Postgres); ADR documents both paths; cross-train Pod B engineer |
| R-12 | Pod D bus factor | [Roadmap] L2×I4=8 🟡 (reduced from 16) | Continuous | Pod D | Major if both unavailable | 2-person Pod D from day one; cross-training plan; documented runbooks; PB-04 if both unavailable |
| R-13 | Cognitive model produces meaningless mastery scores (cold start, sparse data) | [Roadmap] L3×I3=9 🟡 | W27–W34 | Pod B | Moderate — affects adaptive engine | Simple mastery v1 (WMA); research spike W25–W27; add BKT in v0.7 if data supports; add IRT in v0.8 only if data supports (C-9); confidence intervals |
| R-14 | Multi-document RAG retrieval returns cross-course noise | [Roadmap] L3×I2=6 🟡 | W18+ | Pod B | Minor — affects RAG quality | Course-level metadata filter; reranker; A/B test (single-course only in v1.0 per OOS-7) |
| R-15 | Production deployment fails on graduation day | [Roadmap] L2×I5=10 🟡 | W43–W44 | Pod D | Severe — graduation at risk | Deploy W43 (not W44); smoke tests; fallback to staging URL; recorded demo video (GPM-9) |
| R-16 | Exam crunch 1 (late Jan) collapses capacity more than expected | [Roadmap] L4×I4=16 🔴 | W25–W27 | All Pods (Pod B most) | Major — delays P3 | Plan P3 with 50% capacity buffer; defer KG depth to Feb; explicit "exam mode" comms (W25); PB-05 if Pod B throughput <30% |
| R-17 | Exam crunch 2 (late Apr–early May) eats into hardening | [Roadmap] L3×I4=12 🔴 | W39–W40 | All Pods (Pod D most) | Major — delays Code Freeze | Front-load hardening tasks into W37; treat W39–W40 as bonus |
| R-18 | v0.5 (MVP) slips past W20 | [Roadmap] L3×I5=15 🔴 | W14–W20 | All Pods | Severe — every subsequent date slips | v0.4 thin MVP at W16 is the early warning gate; Tier 1 Freeze can be signed even if v0.5 is "demoable but rough"; PB-06 if v0.4 slips |
| R-19 | Tier 1 Architecture Freeze slips past W20 | [Roadmap] L2×I5=10 🟡 | W18–W20 | All Pods | Major — P3 thrashes | Force a "soft freeze" in W19; full freeze in W20 even if some ADRs are still "Proposed" |
| R-20 | Feature Freeze slips past W38 | [Roadmap] L3×I4=12 🔴 | W31–W38 | All Pods | Major — hardening compressed | Hard rule: no new features after W38 even if v0.9 is incomplete; demos show what's done |
| R-21 | A key team member drops out or is unavailable for >4 weeks | [Roadmap] L3×I4=12 🔴 | Continuous | All Pods | Major — capacity loss | Cross-training; pod redundancy (Pod D has 2 people); documented runbooks; firefighter role; advisor escalation |
| R-22 | Pod B (AI/ML) overloaded — too much critical-path work for 3 people | [Roadmap] L3×I4=12 🔴 | W9–W34 | Pod B | Major — AI pipeline at risk | Pod B owns 7 components (not 9); vector DB ops moved to Pod A; eval harness moved to Pod D; firefighter floats to Pod B in P2/P3; pair-program |
| R-23 | Skill gap: junior members can't contribute to AI work | [Roadmap] L3×I3=9 🟡 | Continuous | Pod B | Moderate — capacity loss | Pair-programming; spike-first learning; assign junior to data curation / eval harness first |
| R-24 | Burnout during P5 final push | [Roadmap] L3×I3=9 🟡 | W39–W44 | All Pods | Moderate — capacity loss | Cap hours at 30/wk in P5; mandatory 1 day off per week; rotate on-call |
| R-25 | Team conflict / communication breakdown | [Roadmap] L2×I4=8 🟡 | Continuous | All Pods | Major — collaboration fails | Biweekly retros; explicit norms doc; TPM mediation; advisor escalation |
| R-26 | Advisor expectations misaligned with delivery reality | [Roadmap] L3×I3=9 🟡 | Continuous | TPM | Moderate — surprises at reviews | Monthly advisor demo; written status reports; explicit descope comms |
| R-27 | Cloud provider outage / billing issue | [Roadmap] L2×I4=8 🟡 | Continuous | Pod D | Major — prod down | Multi-AZ; backups; budget alerts; Hetzner fallback |
| R-28 | LLM API rate limits during load test or demo | [Roadmap] L3×I3=9 🟡 | W39 (load test), W44 (demo) | Pod B | Moderate — affects NFR-1 + demo | Quota increase request; caching; multiple API keys; fallback model |
| R-29 | Third-party dependency (LangChain, LiteLLM, etc.) breaking change | [Roadmap] L3×I3=9 🟡 | Continuous | Pod B | Moderate — affects pipeline | Pin versions; integration tests; ADR for swap-out path |
| R-30 | Graduation committee changes requirements mid-project | [Roadmap] L2×I4=8 🟡 | Continuous | TPM | Major — scope change | Monthly advisor check-ins; written scope doc signed at start |
| R-31 | Data privacy / regulatory issue (student data) | [Roadmap] L2×I4=8 🟡 | Continuous | Pod D | Major — legal risk | Data minimization; encryption at rest; PII handling ADR; privacy doc |
| R-32 | Open-source license conflict (e.g., AGPL component in commercial path) | [Roadmap] L2×I3=6 🟡 | Continuous | Pod D | Minor — legal risk | License scan in CI; ADR for licensing strategy |
| R-33 | Hybrid AI / Local-First principle conflicts with v1.0 production deployment (Hybrid mode with cloud LLM) | [Planning] | W7 (LiteLLM), W43 (prod deploy) | Pod B + Pod D | Moderate — philosophical conflict | Resolved per C-2: LiteLLM gateway implements PAL `ReasoningInterface`; local Ollama for dev/demo predictability; cloud for prod quality; PAL priority chain allows fallback |
| R-34 | Conflict between Roadmap (English-only UI per OOS-11) and Tech Spec (Arabic+English bilingual vision) causes confusion | [Planning] | W2 (design tokens), W9 (Arabic OCR), continuous | Pod B + Pod C | Moderate — scope ambiguity | Resolved per C-7: UI is English-only in v1.0; content pipeline (OCR, embeddings, RAG) is Arabic-capable; documented in Section 2.2 + Section 16 |
| R-35 | IRT activation in v0.8 depends on quiz data volume that may not exist | [Planning] | W34 | Pod B | Minor — IRT may be deferred | Resolved per C-9: IRT scaffolding built by W30; activated in v0.8 only if ≥5 interactions per question; otherwise simplified Easy→Medium→Hard progression (Tech Spec primary fallback) |
| R-36 | Demo data drift between staging and prod could cause demo-day surprises | [Planning] | W38 (DDM-6 snapshot), W43 (prod deploy) | Pod D | Moderate — demo risk | DDM-6 snapshot + restore tested; DDM-7 loaded on prod-like env; DDM-8 frozen; smoke tests on both |
| R-37 | Cross-training target (3 DevOps-capable by W38) may not be met if exam crunch disrupts W25–W27 or W39–W40 shadowing | [Planning] | W25–W27, W39–W40, W38 (gate) | Pod D + Pod B + Pod C | Moderate — Feature Freeze criterion at risk | Cross-training front-loaded in W4–W8 + W9–W20; Pod C engineer starts early in W29; documented in `docs/cross-training.md`; if <3 by W38, escalate (Feature Freeze criterion) |

### 15.1 Top Red Risks (Score ≥ 12) and Their Active Mitigations

These 11 risks collectively determine whether the project ships on time. Every one of them has a mitigation that starts in P0 or P1 — *before* the risk materializes:

- **R-01** (OCR quality, 16) — PB-01 (W10 trigger, W11 decision deadline)
- **R-02** (RAG quality, 16) — PB-02 (W16 trigger, W17 decision deadline)
- **R-16** (exam crunch 1, 16) — PB-05 (W25–W27 buffer + exam mode comms)
- **R-18** (MVP slip, 15) — PB-06 (W16 v0.4 thin MVP as early warning)
- **R-03** (adaptive engine, 12) — PB-03 (W31 spike trigger, immediate decision)
- **R-07** (LLM provider change, 12) — structural mitigation via LiteLLM gateway (W7)
- **R-17** (exam crunch 2, 12) — front-loaded hardening (W37)
- **R-20** (Feature Freeze slip, 12) — hard rule: no new features after W38
- **R-21** (member dropout, 12) — cross-training + firefighter role
- **R-22** (Pod B overload, 12) — Pod B restructured to 7 components; firefighter floats to Pod B
- **R-33** (Hybrid AI conflict, planning) — resolved per C-2; LiteLLM gateway as PAL implementation

---

## 16. Gaps & Ambiguities

This section identifies requirements that are ambiguous or missing in the source documents. Per the conflict resolution protocol (Section 2.3), gaps are NOT silently filled with invented decisions; they are flagged for clarification.

### 16.1 Clearly Defined

These requirements are sufficiently specified in the source documents and are implemented as written in this plan:

- **Project phases, weeks, milestones, releases:** Roadmap §Project Phases, §Version Roadmap, §Sprint Timeline.
- **Five quality gates + sign-off criteria:** Roadmap §Quality Gates.
- **Pod structure, headcount, rotating roles:** Roadmap §Team Organization.
- **Capacity model (1,820 usable hours):** Roadmap §Capacity Model.
- **Out-of-Scope list (15 items):** Roadmap §Out of Scope.
- **Tech stack (binding per Section 2.2):** Roadmap §Technology Stack.
- **Eight-layer system architecture:** Tech Spec Section 6.
- **Provider Abstraction Layer (7 interfaces):** Tech Spec Section 8.
- **AI/ML algorithms (BKT, IRT, SM-2, Half-Life Regression, VARK):** Tech Spec Sections 14, 15, 16.
- **SKM evolution strategy:** Tech Spec Section 14.2.
- **Data models, ER schema, API endpoints:** Tech Spec Sections 21, 22.
- **NFRs (with C-5 resolution: Roadmap stricter targets win for graduation gates):** Tech Spec Section 25 + Roadmap.
- **Frozen interface contracts (10):** Roadmap §Frozen Interface Contracts.
- **Risk register (32 risks) + 6 playbooks + 7 fallbacks:** Roadmap §Risk Register + §Risk Mitigation Strategy.
- **Testing strategy + test pyramid + TM-1 through TM-15:** Roadmap §Testing Strategy + §Milestones.
- **CI/CD pipeline + branch protection + environments:** Roadmap §CI/CD Strategy + §Git Workflow.
- **Documentation strategy + docs-first workflow + DM-1 through DM-16:** Roadmap §Documentation Strategy + §Milestones.
- **Graduation prep runway (GPM-0 through GPM-12) + demo data track (DDM-1 through DDM-8):** Roadmap §Graduation Preparation.
- **Critical path + slack analysis:** Roadmap §Critical Path.

### 16.2 Ambiguous

These requirements need clarification. Where this plan made an interpretation, it is documented; otherwise the ambiguity is preserved.

| # | Ambiguity | Source | Interpretation in This Plan | Confidence |
| --- | --- | --- | --- | --- |
| A-1 | **v0.1 tag week:** Roadmap Version Roadmap table lists v0.1 at W6, but Roadmap P0 exit (W4) requires v0.1 tag if criteria met. | Roadmap §Version Roadmap vs §Sprint Timeline (W4 sprint "v0.1 tag + demo") | Tag at W4 if criteria met (per Sprint Timeline); if not, tag at W6 (per Version Roadmap). Plan accommodates both. | Medium |
| A-2 | **Recommendation engine v1 scope:** Roadmap W33 sprint mentions "Content + peer recommendations" but OOS-6 excludes peer recommendations. | Roadmap W33 sprint vs OOS-6 | Per C-8: v1.0 ships rule-based + content-based only; peer/collaborative filtering deferred. | High (per C-8) |
| A-3 | **IRT activation timing:** Roadmap says "IRT v0.8 if data supports"; Tech Spec includes IRT in SKM v0.5.2 stage alongside BKT. | Roadmap §Structural Descopes #7 vs Tech Spec Section 14.2 | Per C-9: IRT scaffolding built by W30; activated in v0.8 only if ≥5 interactions per question. | High (per C-9) |
| A-4 | **Analytics dashboard chart count:** Roadmap says "4 chart types"; Tech Spec describes full dashboard (heatmap, readiness, time distribution, goal tracking). | Roadmap §Structural Descopes #2 vs Tech Spec Section 20.2 | Per C-12: v1.0 ships 4 chart types, 30-day window. Specific 4 chosen: cohort mastery heatmap, quiz pass rates, engagement, mastery distribution. | Medium (specific 4 not enumerated in source) |
| A-5 | **Admin dashboard depth:** Roadmap says "minimal: user list, course list, system health. No audit log UI." Tech Spec Section 22.2 mentions Admin role + audit logging. | Roadmap §Structural Descopes #3 + OOS-9 vs Tech Spec | Per Roadmap: minimal admin dashboard; audit log via CLI tool only. | High |
| A-6 | **Notification system scope:** Roadmap W35 sprint mentions "in-app + email notifications"; Roadmap §Descope candidates #2 lists "Notification system (skip; demo without)" as a descope candidate. | Roadmap W35 sprint vs §Descope candidates | In-app notifications ship in v1.0 (basic); email is a stretch (best-effort; if time permits, use SendGrid; otherwise defer). If buffer is consumed, notifications are descoped first. | Medium |
| A-7 | **CAT (Computerized Adaptive Testing) scope:** Tech Spec Section 16.5 describes full CAT with IRT-driven item selection; Roadmap mentions "adaptive difficulty" but doesn't specify CAT. | Tech Spec Section 16.5 vs Roadmap §Project Scope | Full CAT is v1.0 scope per Tech Spec, but conditional on IRT activation (per C-9). If IRT is not activated, simplified Easy → Medium → Hard sequential progression (Tech Spec primary fallback). | Medium |
| A-8 | **Half-Life Regression implementation:** Tech Spec Section 16.4 mentions Half-Life Regression for forgetting prediction; Roadmap doesn't explicitly mention it. | Tech Spec Section 16.4 (referencing Settles & Meeder, 2016) vs Roadmap | Half-Life Regression is in scope per Tech Spec (it's part of the Adaptive Engine's scheduling optimization). Pod B implements it in W31 (SM-2 + Half-Life Regression together). If time-constrained, simplified Ebbinghaus formula (Tech Spec ultimate fallback) is acceptable. | Medium |
| A-9 | **CSP profile (Pod D) fields in v1.0:** Tech Spec Section 15.1 defines 13 CSP fields. Roadmap §Structural Descopes doesn't explicitly reduce this. | Tech Spec Section 15.1 vs Roadmap | v1.0 ships a subset of CSP fields (education_level, major, university, preferred_language, learning_style_vark, daily_available_minutes) per W6 Pod A task. Full 13 fields is post-v1.0. This interpretation is documented but not explicitly in the source. | Low — flag for advisor confirmation |
| A-10 | **Local-First / Offline mode in v1.0:** Tech Spec Section 4.2 lists "Local First" and "Offline Friendly" as design principles. Roadmap §Structural Descopes doesn't address this. | Tech Spec Section 4.2 vs Roadmap | Per C-2: v1.0 production deployment uses Hybrid mode (cloud LLM via LiteLLM). Local-First is a Tech Spec design principle that informs architecture (PAL enables local providers) but does not change the v1.0 deployment topology. NFR-7 (100% offline operation) is partially met (PAL enables it; v1.0 doesn't ship a fully offline deployment). | Medium — flag for advisor confirmation |
| A-11 | **Demo PDF language:** DDM-1 requires "3 courses × 5–10 PDFs each, all clean, all OCR-able." Doesn't specify language. Given the Tech Spec's Arabic emphasis but Roadmap's English-only UI (OOS-11). | Roadmap DDM-1 vs Tech Spec Arabic emphasis vs Roadmap OOS-11 | Demo PDFs are primarily English (matches English-only UI); 1–2 Arabic PDFs included to demonstrate Arabic pipeline capability. Documented in W15 task. | Medium |
| A-12 | **Pod B firefighter allocation:** Roadmap says "firefighter floats to Pod B in P2/P3." Doesn't specify which weeks. | Roadmap §Pod Allocation Per Phase | Firefighter is explicitly allocated to Pod B during P2 (W9–W20) and P3 (W21–W30) per Roadmap §Pod Allocation Per Phase. Pod D during P0 + P5; Pod C during P4. | High |

### 16.3 Missing

Information needed for reliable implementation planning that is not in the source documents. These are flagged as assumptions (Section 17) where this plan made an interpretation; otherwise they are open questions for the team.

| # | Missing Item | Impact | How This Plan Handles It |
| --- | --- | --- | --- |
| M-1 | **Specific LLM model choice for production** (Roadmap says "OpenAI / Anthropic / GLM" but doesn't pick one) | Affects cost + quality | Assumption A-1: v1.0 production uses GPT-4o-mini for non-critical paths (quiz gen, concept extraction) + GPT-4o for RAG (quality-critical). LiteLLM gateway allows swap. |
| M-2 | **Cloud provider choice** (Roadmap says "Hetzner (cheaper) or AWS (ecosystem)") | Affects cost + ops | Assumption A-2: Hetzner for cost (student budget); AWS only if Hetzner lacks a needed feature. |
| M-3 | **Specific 4 analytics chart types** (Roadmap says "4 chart types" but doesn't enumerate) | Affects Pod C implementation | Assumption A-3: cohort mastery heatmap, quiz pass rates over 30 days, student engagement bar chart, mastery distribution histogram. |
| M-4 | **Specific 5 demo student personas** (DDM-3 says "5 demo student accounts with seeded mastery states" but doesn't define personas) | Affects demo narrative | Assumption A-4: novice, intermediate, advanced, struggling, recovering. |
| M-5 | **On-call rotation schedule** (Roadmap mentions on-call but doesn't specify rotation) | Affects team workload | Assumption A-5: weekly rotation across Pod D engineers + 1 cross-trained backup; starts W21 (post-v0.5). |
| M-6 | **Specific demo PDF titles** (DDM-1 says "3 courses × 5–10 PDFs") | Affects demo + content | Assumption A-6: 3 courses — Intro to Machine Learning, Data Structures & Algorithms, Linear Algebra. |
| M-7 | **Email notification provider** (if email notifications ship) | Affects implementation | Assumption A-7: SendGrid free tier if time permits; otherwise in-app only. |
| M-8 | **CSP profile subset for v1.0** (Tech Spec defines 13 fields; Roadmap doesn't specify subset) | Affects Pod A + Pod C | Assumption A-8: 6 fields (education_level, major, university, preferred_language, learning_style_vark, daily_available_minutes). Flagged in A-9 for advisor confirmation. |
| M-9 | **Performance test k6 script details** (TM-12 says "50 concurrent users; P95 < 2s" but doesn't specify the script) | Affects load test execution | Assumption A-9: k6 script simulating 50 VUs hitting `/v1/chat` + `/v1/rag/query` for 10 minutes, ramping up over 1 minute. |
| M-10 | **Graduation presentation slide count** (Roadmap §Presentation Structure outlines 8 sections but doesn't specify slide count) | Affects slide deck | Assumption A-10: 15–20 slides covering the 8 sections; 30-minute timing. |

---

## 17. Planning Assumptions

This section distinguishes explicit requirements (from source documents), strongly implied requirements (inferred from context), and planning assumptions (made by this plan where source documents are silent).

| # | Assumption | Source | Confidence | Impact if Wrong |
| --- | --- | --- | --- | --- |
| A-1 | v1.0 production uses GPT-4o-mini for non-critical paths + GPT-4o for RAG | [Planning] M-1 | Medium | Cost + quality affected; mitigated by LiteLLM gateway swap (F-4) |
| A-2 | Hetzner for cloud provider (cost) | [Planning] M-2 | High | Minor cost impact; AWS swap is straightforward |
| A-3 | 4 analytics chart types: cohort mastery heatmap, quiz pass rates, engagement, mastery distribution | [Planning] M-3 | Medium | Pod C rework if different charts chosen |
| A-4 | 5 demo student personas: novice, intermediate, advanced, struggling, recovering | [Planning] M-4 | Medium | Demo narrative changes; minimal rework |
| A-5 | On-call rotation: weekly across Pod D + 1 cross-trained backup; starts W21 | [Planning] M-5 | High | Team workload affected |
| A-6 | 3 demo courses: Intro to ML, Data Structures & Algorithms, Linear Algebra | [Planning] M-6 | Medium | Demo data changes; minimal rework |
| A-7 | SendGrid free tier for email notifications (if shipped) | [Planning] M-7 | Low | Email notifications may be deferred (descope candidate) |
| A-8 | CSP v1.0 subset: 6 fields (education_level, major, university, preferred_language, learning_style_vark, daily_available_minutes) | [Planning] M-8 | Low | Pod A + Pod C rework if full 13 fields required; flag for advisor (A-9) |
| A-9 | k6 load test: 50 VUs hitting `/v1/chat` + `/v1/rag/query` for 10 min, 1-min ramp | [Planning] M-9 | High | Test may not catch all bottlenecks; can be adjusted |
| A-10 | Graduation presentation: 15–20 slides, 30-minute timing | [Planning] M-10 | High | Slide deck rework if count differs |
| A-11 | At least 8 of 9 team members are active from W2 onward (Roadmap §Operating Assumptions) | [Explicit] Roadmap | High | If <8, descope protocol triggers (Roadmap §Operating Assumptions #4) |
| A-12 | LLM API access is available (any one of OpenAI / Anthropic / DeepSeek / GLM) (Roadmap §Operating Assumptions) | [Explicit] Roadmap | High | If only free-tier OSS models, RAG quality drops (R-07) |
| A-13 | Team has working laptops, GitHub org, Slack/Discord (Roadmap §Operating Assumptions) | [Explicit] Roadmap | High | Project cannot start |
| A-14 | At least one member can provision a cloud account (Roadmap §Operating Assumptions) | [Explicit] Roadmap | High | Production deployment at risk |
| A-15 | Advisor is available for monthly reviews + final dry-runs (Roadmap §Operating Assumptions) | [Explicit] Roadmap | High | Graduation prep runway disrupted |
| A-16 | The team does NOT assume all 9 members are active every week (Roadmap §Non-Assumptions) | [Explicit] Roadmap | High | Firefighter role absorbs 1 unavailable member |
| A-17 | The team does NOT assume AI components work first try (Roadmap §Non-Assumptions) | [Explicit] Roadmap | High | Spikes + playbooks mitigate |
| A-18 | The team does NOT assume the LLM API provider is stable (Roadmap §Non-Assumptions) | [Explicit] Roadmap | High | LiteLLM gateway abstracts providers |
| A-19 | The team does NOT assume exam crunches are survivable without planned downtime (Roadmap §Non-Assumptions) | [Explicit] Roadmap | High | W25–W27 + W39–W40 are explicitly low-capacity |
| A-20 | The team does NOT assume v1.0 ships "everything" (Roadmap §Non-Assumptions) | [Explicit] Roadmap | High | OOS list is part of the contract |
| A-21 | Qdrant is the v1.0 vector DB (Roadmap stack lock); ChromaDB in Tech Spec is the dev default (C-1 resolution) | [Strongly Implied] C-1 | High | F-1 fallback (pgvector) if Qdrant fails |
| A-22 | LiteLLM gateway is the implementation of the PAL `ReasoningInterface` (C-2 resolution) | [Strongly Implied] C-2 | High | PAL architecture + LiteLLM gateway coexist |
| A-23 | BGE-M3 is the v1.0 embedding default; OpenAI text-embedding-3-small is F-3 fallback | [Explicit] Roadmap + Tech Spec | High | F-3 swap is 1-day config change |
| A-24 | JWT + refresh tokens + Google OAuth + bcrypt(12) is the v1.0 auth implementation (C-10 resolution) | [Explicit] Roadmap + Tech Spec | High | `fastapi-users` library |
| A-25 | Docker Compose for dev/staging; k3s for prod (single-node, NOT full K8s) (C-11 resolution) | [Explicit] Roadmap | High | Pod D does not deploy full Kubernetes |
| A-26 | 3 user roles in v1.0: student, instructor, admin (C-6 resolution); Guest + Contributor are post-v1.0 | [Strongly Implied] C-6 | High | Pod A RBAC enforces 3 roles |
| A-27 | UI is English-only in v1.0 (OOS-11); content pipeline is Arabic-capable (C-7 resolution) | [Explicit] Roadmap + C-7 | High | Pod C builds English UI; Pod B builds Arabic-capable pipeline |
| A-28 | Recommendation engine v1 is rule-based + content-based only (C-8 resolution); peer/collaborative filtering is post-v1.0 | [Explicit] OOS-6 + C-8 | High | Pod B implements rule-based + content-based |
| A-29 | Test coverage target is ≥60% on critical paths (Roadmap gate, TM-11); internal stretch is 70% on core modules (Tech Spec NFR-10) (C-4 resolution) | [Explicit] Roadmap + C-4 | High | Pod D targets 60% for gate; 70% as stretch |
| A-30 | RAG latency target is P95 < 2s under 50 concurrent users (Roadmap Engineering Success #5, TM-12); NFR-1's <3s single-user is a relaxed lower bound (C-5 resolution) | [Explicit] Roadmap + C-5 | High | Pod A + Pod B + Pod D optimize for P95 < 2s |

---

## 18. Final Validation

This section verifies the internal consistency of this 44-week execution plan against the requirements in the user's task description.

### 18.1 Week Coverage

- [x] Week 1 exists (P0 Pre-Flight, Kickoff + Stack Lock)
- [x] Week 2 exists (P0, MVP Sign-off + Skeletons)
- [x] Week 3 exists (P0, Hello World on Real URL + DB Baseline)
- [x] Week 4 exists (P0, ADRs + Risk Register + v0.1 Tag)
- [x] Week 5 exists (P1, Auth + Spikes Begin)
- [x] Week 6 exists (P1, User Mgmt + Course CRUD + v0.1 Tag)
- [x] Week 7 exists (P1, Async Jobs + Observability + LLM Gateway)
- [x] Week 8 exists (P1, Integration + v0.2 Tag)
- [x] Week 9 exists (P2, OCR Pipeline v1 + Chat UI Scaffold)
- [x] Week 10 exists (P2, OCR Hardening + Document Model)
- [x] Week 11 exists (P2, Chunking Strategy + ADR)
- [x] Week 12 exists (P2, v0.3 Tag + Embedding Batch Job)
- [x] Week 13 exists (P2, Vector DB + Search API)
- [x] Week 14 exists (P2, Hybrid Retrieval + Reranker)
- [x] Week 15 exists (P2, RAG Prompt + Eval Harness + IM-5)
- [x] Week 16 exists (P2, v0.4 Thin MVP — GATE 1)
- [x] Week 17 exists (P2, Full Chat API + E2E Student Flow)
- [x] Week 18 exists (P2, Multi-Document RAG + Tier 1 Freeze Draft)
- [x] Week 19 exists (P2, Polish + Tier 1 Freeze Review)
- [x] Week 20 exists (P2, v0.5 + Tier 1 Freeze — GATE 2)
- [x] Week 21 exists (P3, KG Schema ADR + Demo Backlog Started)
- [x] Week 22 exists (P3, Concept Extraction Spike + Outline v0)
- [x] Week 23 exists (P3, Concept Extraction Pipeline + Neo4j)
- [x] Week 24 exists (P3, KG API + KG Viz + Demo Dataset v1)
- [x] Week 25 exists (P3, KG Retrieval Boost + Cognitive Spike Begins)
- [x] Week 26 exists (P3, v0.6 Tag + Quiz UI + Cognitive Spike Continues)
- [x] Week 27 exists (P3, Cognitive Spike Concludes + Mastery v1)
- [x] Week 28 exists (P3, Quiz E2E + Mastery UI + Cognitive Hardening)
- [x] Week 29 exists (P3, Cognitive Hardening + Adaptive Spike Begins + Mastery UI)
- [x] Week 30 exists (P3, v0.7 + Tier 2 Freeze — GATE 3)
- [x] Week 31 exists (P4, Adaptive Engine Productionization + ADR-018)
- [x] Week 32 exists (P4, Recommendation API + UI + Difficulty Adjustment)
- [x] Week 33 exists (P4, Recommendation Engine v1 + Adaptation Eval + Demo Script v1)
- [x] Week 34 exists (P4, Analytics Dashboard + v0.8 Tag)
- [x] Week 35 exists (P4, Admin Dashboard + Notifications + Demo Student Accounts)
- [x] Week 36 exists (P4, UX Polish + Bug Bash #1 + Demo Script v2)
- [x] Week 37 exists (P4, Bug Fixing + Accessibility + Demo Dataset Finalized)
- [x] Week 38 exists (P4, v0.9 + Feature Freeze — GATE 4)
- [x] Week 39 exists (P5, Performance Pass + DB Optimization + Load Test)
- [x] Week 40 exists (P5, Security Review + Auth Hardening + Dry-Run #0)
- [x] Week 41 exists (P5, Bug Bash #2 + Docs + DR Drill + Fallback Video)
- [x] Week 42 exists (P5, v1.0-rc + Code Freeze — GATE 5)
- [x] Week 43 exists (P6, Production Deployment + Dry-Run #2 + Slide Deck v2)
- [x] Week 44 exists (P6, Dry-Run #3 + v1.0 + Graduation Presentation)

**All 44 weeks present. No week skipped.**

### 18.2 Pod Coverage

Every week contains all four Pods:
- [x] Week 1: Backend, AI/ML & Data, Frontend, DevOps/QA — all present
- [x] Week 2: all present
- [x] Week 3: all present
- [x] Week 4: all present
- [x] Week 5: all present
- [x] Week 6: all present
- [x] Week 7: all present
- [x] Week 8: all present
- [x] Week 9: all present
- [x] Week 10: all present
- [x] Week 11: all present
- [x] Week 12: all present
- [x] Week 13: all present
- [x] Week 14: all present
- [x] Week 15: all present
- [x] Week 16: all present
- [x] Week 17: all present
- [x] Week 18: all present
- [x] Week 19: all present
- [x] Week 20: all present
- [x] Week 21: all present
- [x] Week 22: all present
- [x] Week 23: all present
- [x] Week 24: all present
- [x] Week 25: all present
- [x] Week 26: all present
- [x] Week 27: all present
- [x] Week 28: all present
- [x] Week 29: all present
- [x] Week 30: all present
- [x] Week 31: all present
- [x] Week 32: all present
- [x] Week 33: all present
- [x] Week 34: all present
- [x] Week 35: all present
- [x] Week 36: all present
- [x] Week 37: all present
- [x] Week 38: all present
- [x] Week 39: all present
- [x] Week 40: all present
- [x] Week 41: all present
- [x] Week 42: all present
- [x] Week 43: all present
- [x] Week 44: all present

**All 4 Pods present in all 44 weeks. Some Pods have lighter weeks (e.g., Pod B during exam crunch W25–W27) but no Pod is absent.**

### 18.3 Roadmap Coverage

Every major milestone and release from the Master Roadmap is represented:

- [x] **v0.1** (W6 target, tagged W4 or W6) — represented in W1–W6
- [x] **v0.2** (W8) — represented in W5–W8
- [x] **v0.3** (W12) — represented in W9–W12
- [x] **v0.4 Thin MVP** (W16, GATE 1) — represented in W13–W16
- [x] **v0.5 Full MVP + Tier 1 Freeze** (W20, GATE 2) — represented in W17–W20
- [x] **v0.6 Knowledge Layer** (W26) — represented in W21–W26
- [x] **v0.7 Cognition + Tier 2 Freeze** (W30, GATE 3) — represented in W27–W30
- [x] **v0.8 Adaptation** (W34) — represented in W31–W34
- [x] **v0.9 Analytics + Feature Freeze** (W38, GATE 4) — represented in W35–W38
- [x] **v1.0-rc Hardening + Code Freeze** (W42, GATE 5) — represented in W39–W42
- [x] **v1.0 Graduation** (W44, FINAL) — represented in W43–W44

**Integration Milestones IM-1 through IM-15:** all represented (see Section 12.3).
**Testing Milestones TM-1 through TM-15:** all represented (see Section 12.4).
**Documentation Milestones DM-1 through DM-16:** all represented (see Section 12.5).
**Graduation Prep Milestones GPM-0 through GPM-12:** all represented (scattered through P3–P6, per Roadmap §Graduation Preparation).
**Demo Data Milestones DDM-1 through DDM-8:** all represented (W15, W24, W30, W34, W36, W38, W40, W42).

### 18.4 Technical Coverage

Major technical components from the Technical Specification are mapped to implementation work:

- [x] **Eight-layer architecture** (Tech Spec Section 6) — each layer mapped to a Pod + phase (Section 3.1)
- [x] **Provider Abstraction Layer (7 interfaces)** (Tech Spec Section 8) — Pod B W1 (skeleton) + W5–W6 (providers)
- [x] **Three execution modes** (Tech Spec Section 9) — Pod D ships all three; Hybrid is v1.0 prod (Section 3.3)
- [x] **Document Processing Pipeline** (Tech Spec Section 11) — Pod B W9–W12 (OCR + chunking + embedding)
- [x] **Knowledge Pipeline / RAG** (Tech Spec Section 12) — Pod B W13–W15 (hybrid retrieval + reranker + RAG)
- [x] **Knowledge Graph Architecture** (Tech Spec Section 13) — Pod B W21–W24 (extraction + Neo4j + retrieval boost)
- [x] **Student Knowledge Model (BKT/IRT)** (Tech Spec Section 14) — Pod B W25–W28 (spike + mastery estimator + hardening + BKT scaffold)
- [x] **Customized Student Profile** (Tech Spec Section 15) — Pod A W6 (profile CRUD) + Pod C W6 (profile UI) + Pod B W27 (auto-estimation)
- [x] **Adaptive Learning Engine** (Tech Spec Section 16) — Pod B W29–W33 (spike + productionization + recommendation engine + difficulty adjustment)
- [x] **Learning Workflow / Feedback Loop** (Tech Spec Section 17) — Pod A + Pod B + Pod C W26–W34 (quiz → mastery → adaptive → recommendation)
- [x] **Modular Monolith** (Tech Spec Section 18) — Pod A W1 (directory structure)
- [x] **Backend Architecture (FastAPI + async)** (Tech Spec Section 19) — Pod A W1–W2 (skeleton + async)
- [x] **Frontend Architecture (Next.js 16 + App Router)** (Tech Spec Section 20) — Pod C W1–W2 (skeleton + design tokens)
- [x] **Database Design (multi-store)** (Tech Spec Section 21) — Pod A W3+ (PG) + Pod A W12 (Qdrant) + Pod D W22 (Neo4j) + Pod D W5 (Redis) + Pod D W6 (MinIO)
- [x] **API Design (REST + WebSocket)** (Tech Spec Section 22) — Pod A W2 (OpenAPI) + W7 (WS) + W17 (chat SSE)
- [x] **Infrastructure (3 deployment configs)** (Tech Spec Section 23) — Pod D W1 (envs) + W3 (deploy) + W39 (runbooks)
- [x] **Security & Privacy** (Tech Spec Section 24) — Pod A W5 (auth) + W40 (security review) + W40 (auth hardening)
- [x] **Performance & Scalability (NFRs)** (Tech Spec Section 25) — Pod D W39 (load test) + Pod A W39 (perf optimization)
- [x] **Technology Stack** (Tech Spec Section 26) — all components mapped (Section 3.5)
- [x] **Research Components (BKT, IRT, SM-2, Half-Life Regression, VARK)** (Tech Spec Section 27) — Pod B W25–W31 (spikes + implementations)

### 18.5 Dependencies

Major dependencies and handoffs are represented in the Cross-Pod Handoff Matrix (Section 11). Key dependencies verified:

- [x] Auth → Course CRUD → File Upload → OCR → Chunking → Embeddings → Vector DB → RAG (critical path)
- [x] RAG → Cognitive Model → Adaptive Engine → Recommendations
- [x] KG → RAG retrieval boost (W25)
- [x] KG → Cognitive Model prereqs (W28)
- [x] Cognitive Model → Adaptive Engine (W31)
- [x] CSP → Cognitive Model P(L0) initialization (W28)
- [x] Pod D provides CI/CD, environments, testing infra to all Pods (continuous)
- [x] Pod B provides PAL + AI services to Pod A (continuous)
- [x] Pod A provides API contracts + data to Pod C (continuous)

### 18.6 Integration

Integration work is explicitly scheduled via IM-1 through IM-15 (Section 12.3). Each IM has a verifiable outcome and is assigned to a specific week. Integration is not deferred to the end; it occurs throughout P2, P3, P4, and P6.

### 18.7 Testing

Testing exists throughout the project via TM-1 through TM-15 (Section 12.4). Testing is not a final-stage activity:

- [x] Unit test infra: W4 (TM-1)
- [x] Auth + course CRUD coverage: W8 (TM-2, ≥80%)
- [x] OCR integration: W12 (TM-3, 5 PDFs)
- [x] RAG golden set: W15 (TM-4, 50 Q&A)
- [x] E2E Playwright: W17 (TM-5)
- [x] Coverage ≥40%: W20 (TM-6)
- [x] KG sanity: W24 (TM-7)
- [x] Quiz + mastery E2E: W28 (TM-8)
- [x] Adaptation eval: W33 (TM-9)
- [x] Bug bash #1: W36 (TM-10)
- [x] Coverage ≥60%: W38 (TM-11, Feature Freeze gate)
- [x] Load test: W39 (TM-12, 50 users, P95<2s)
- [x] Security review: W40 (TM-13)
- [x] Bug bash #2: W41 (TM-14, ≤3 P1s)
- [x] Smoke tests prod-like: W42 (TM-15)

### 18.8 DevOps

DevOps work exists throughout the project. Pod D is active every week:

- [x] W1: CI scaffold, 3 envs, risk register
- [x] W2: Eval harness scaffold, pytest + Vitest
- [x] W3: Staging deploy workflow, PG provisioned
- [x] W4: Eval harness in CI, v0.1 tag
- [x] W5: Redis + Celery + Flower, observability
- [x] W6: MinIO, Grafana dashboard
- [x] W7: LiteLLM gateway, Langfuse
- [x] W8: TM-2, v0.2 tag
- [x] W9–W12: OCR integration tests, cost monitoring
- [x] W13: Qdrant monitoring
- [x] W14–W15: RAG eval in CI, RAG load test, RAG quality dashboard
- [x] W16: Gate 1 validation
- [x] W17: TM-5 E2E
- [x] W20: TM-6, Tier 1 sign-off, on-call prep
- [x] W21–W24: Neo4j deploy, TM-7, DDM-2
- [x] W25–W28: Exam crunch comms, TM-8
- [x] W29–W34: Tier 2 prep, adaptive monitoring, TM-9, DDM-4
- [x] W35–W38: TM-10, TM-11, DDM-6, Feature Freeze sign
- [x] W39–W42: TM-12, TM-13, TM-14, TM-15, DM-14 (runbooks), DR drill, DDM-8, Code Freeze sign
- [x] W43–W44: Prod deploy, IM-15, dry-runs, artifact submission

### 18.9 Traceability

Major requirements can be traced to concrete weekly tasks. The chain **Source Requirement → Phase → Week → Pod → Task → Deliverable** is documented in:

- [x] Section 12.1 (Version Milestones traceability)
- [x] Section 12.2 (Quality Gate traceability)
- [x] Section 12.3 (Integration Milestone traceability)
- [x] Section 12.4 (Testing Milestone traceability)
- [x] Section 12.5 (Documentation Milestone traceability)
- [x] Section 11 (Cross-Pod Handoff Matrix — week-by-week artifact handoffs)
- [x] Sections 7–10 (Pod-specific 44-week indexes — task + deliverable + dependency per week per Pod)

For any major requirement, the reader can answer: "Where in the 44-week plan is this requirement implemented?" by consulting the relevant table.

### 18.10 Consistency

The weekly plan, milestone matrix, Pod indexes, handoff matrix, and critical path have been cross-checked for contradictions:

- [x] **Weekly plan vs. master summary table (Section 6):** the headline task per pod per week matches.
- [x] **Weekly plan vs. Pod indexes (Sections 7–10):** each Pod's tasks per week in the index match the weekly section.
- [x] **Weekly plan vs. handoff matrix (Section 11):** each handoff in the matrix corresponds to a `Handoff` field in the relevant weekly task.
- [x] **Weekly plan vs. milestone traceability (Section 12):** each milestone's "Relevant Weeks" match the weeks where the tasks appear.
- [x] **Weekly plan vs. release plan (Section 13):** each release's "Contributing Weeks" match the weeks where the release criteria are met.
- [x] **Weekly plan vs. critical path (Section 14):** each critical-path task appears in the week specified by the critical path chain.
- [x] **Weekly plan vs. risk register (Section 15):** each risk's "Affected Weeks" match the weeks where mitigations are active.
- [x] **Conflict resolutions (Section 2.2) vs. weekly tasks:** each conflict resolution (C-1 through C-13) is reflected in the relevant weekly tasks (e.g., C-1 Qdrant choice appears in Pod A W12 + Pod D W9; C-7 English UI + Arabic pipeline appears in Pod C tasks + Pod B W10 Arabic preprocessing).
- [x] **Assumptions (Section 17) vs. weekly tasks:** each planning assumption is reflected where relevant (e.g., A-1 GPT-4o-mini for non-critical paths appears in Pod B W39 LLM optimization).

**No contradictions found between the weekly plan and the summary sections.**

### 18.11 Final Statement

This 44-Week Engineering Execution Plan is derived from the Master Roadmap (scope/timeline authority) and the Technical Specification v4.0 (architecture authority). It decomposes every roadmap-level deliverable into concrete engineering tasks owned by one of four Pods, with explicit dependencies, handoffs, and Definitions of Done. Conflicts between the two source documents are resolved explicitly (Section 2.2); ambiguities are flagged (Section 16); assumptions are documented (Section 17). The plan is detailed enough that the four Pods can use it as their weekly execution plan without having to repeatedly re-interpret the Master Roadmap or Technical Specification.

**Ship the thin MVP at W16. Everything else follows.**

---

*End of 44-WEEK-EXECUTION-PLAN.md v1.0.*
