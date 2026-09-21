# OpenLearn AI — Master Roadmap

| Field | Value |
|---|---|
| **Version** | 1.0 |
| **Status** | Approved — Single Source of Truth (SSOT) |
| **Planning Horizon** | 44 weeks · 3 August 2026 → 6 June 2027 |
| **Document Owner** | Senior TPM / Staff Architect |
| **Repository Path** | `MASTER_ROADMAP.md` (repo root) |
| **Review Cadence** | Monthly milestone review (last Friday of every month) |
| **Change Authority** | TPM + all pod leads (see Change Management Policy) |

---

## Executive Summary

**OpenLearn AI** is an AI-powered adaptive learning platform built by a 9-person team over 44 weeks (August 2026 → June 2027) for a graduation defense. A student or instructor uploads PDFs; the platform runs OCR, chunks and embeds the content, builds a RAG layer with citations, extracts concepts into a Knowledge Graph, models each student's cognitive state from quiz performance, and uses that model to drive personalized recommendations and adaptive quiz difficulty.

**The single most important date is W16 (21 November 2026) — the v0.4 Thin MVP.** A pre-loaded PDF, no auth, a single chat box, an answer with citations. If that ships on time, the rest of the plan has enough slack to absorb almost any problem. If it doesn't, every subsequent date is at risk.

### The Numbers

- **9 engineers** organized into 4 pods: A (Backend, 2), B (AI/ML, 3), C (Frontend, 2), D (DevOps + QA + Eval, 2), plus rotating TPM, Docs Owner, and Firefighter roles drawn from the 9.
- **1,820 usable engineering hours** (pessimistic model, after a 60% productivity multiplier for meetings, rework, context-switching, and university workload).
- **5 quality gates** that must pass or graduation slips: v0.4 Thin MVP (W16), Tier 1 Architecture Freeze (W20), Tier 2 Architecture Freeze (W30), Feature Freeze (W38), Code Freeze (W42).
- **4 weeks of critical-path slack** distributed across the plan, not concentrated at the end.
- **6 contingency playbooks** for the top red risks: OCR quality, RAG quality, adaptive engine convergence, Pod D bus factor, exam crunch collapse, MVP slip.
- **7 scoped component-level fallbacks** (e.g., Qdrant → pgvector, Neo4j → JSONB, BGE-M3 → OpenAI embeddings) — invoked independently, never as a full stack swap.
- **15 items on the signed Out-of-Scope list** (mobile app, multi-tenant, SSO/SAML, real-time collaboration, proctoring, etc.).
- **~70% delivery confidence** for v1.0 by W44 — honest for a student team building an AI product in 10 months.

### The Stack

Next.js 16 + FastAPI (Python 3.12) + PostgreSQL 16 + Qdrant + Neo4j + LiteLLM gateway. PaddleOCR for OCR. BGE-M3 for embeddings. bge-reranker-v2-m3 for hybrid retrieval. Celery + Redis for async jobs. Docker + k3s for orchestration. GitHub Actions for CI. Grafana + Prometheus + Loki + Sentry for observability.

### The Phases

| Phase | Weeks | Calendar | Headline |
|---|---|---|---|
| P0 Pre-Flight | W1–4 | Aug 2026 | v0.1 deployed; CI; 5 ADRs; OOS signed |
| P1 Foundations | W5–8 | Sep 2026 | v0.2: auth + courses + upload |
| P2 AI Pipeline | W9–20 | Oct–Dec 2026 | v0.4 Thin MVP (W16); v0.5 + Tier 1 Freeze (W20) |
| P3 Knowledge & Cognition | W21–30 | Dec–Feb | v0.7 + Tier 2 Freeze |
| P4 Adaptation & Analytics | W31–38 | Mar–Apr | v0.9 + Feature Freeze |
| P5 Hardening | W39–42 | Apr–May | v1.0-rc + Code Freeze |
| P6 Graduation | W43–44 | May–Jun | v1.0 + presentation |

### The Critical Path

Stack lock → OCR → Chunking → Embeddings → Vector DB → RAG → **v0.4 Thin MVP** → Tier 1 Freeze → Concept Extraction → Knowledge Graph → Cognitive Model → Tier 2 Freeze → Adaptive Engine → Feature Freeze → Hardening → Code Freeze → Prod Deploy → Graduation.

### How to Use This Document

- **Week 1:** Print the Version Roadmap section and stick it on the wall.
- **Every Monday:** Pod leads review the Sprint Timeline for the current week.
- **Every Friday:** Demo on staging + retrospective + next-week sprint planning.
- **Last Friday of every month:** Milestone review using the Monthly Timeline.
- **When a risk triggers:** Open the relevant playbook in Risk Mitigation Strategy.
- **When in doubt:** Optimize for working software over perfect architecture, incremental delivery over big-bang, and risk reduction over feature count.

**Ship the thin MVP at W16. Everything else follows.**

---

## Purpose

This document is the single source of truth for the OpenLearn AI project. It is the engineering plan that the team will execute from August 2026 until the graduation defense in May/June 2027. Every phase, sprint, milestone, deliverable, risk, and freeze in this document is internally consistent and intended to be followed as written.

This roadmap optimizes for **successful delivery**. It does not optimize for academic appearance, feature count, or theoretical ambition. The plan assumes conservative capacity, assumes the team will face delays, integration problems, and periods of reduced availability, and is structured so that the project still ships v1.0 even if multiple things go wrong.

This document is suitable for engineering management, the GitHub repository, weekly project meetings, sprint planning, graduation supervision, and long-term project governance. It is not a specification of *how* to build each component — that is the role of Architecture Decision Records (ADRs) and design docs. This document specifies *what* ships, *when*, by *whom*, with *what* exit criteria, and *what* happens when reality diverges from plan.

---

## Project Vision

OpenLearn AI is an AI-powered adaptive learning platform. A student or instructor uploads educational documents — PDFs, slides, images of worksheets. The platform ingests the material through an OCR pipeline, embeds the content into a vector store, and builds a retrieval-augmented generation layer on top of it. As students interact with the material — asking questions, taking quizzes — the platform builds a per-student cognitive model and uses that model to drive personalized recommendations, adaptive quiz difficulty, and a learning-analytics dashboard.

The product is engineered as a startup-grade system, not a university assignment. It deploys to a real domain with authentication, monitoring, and a runbook. The stack is selected so that the product can continue post-graduation as a real product without re-architecture.

---

## Project Objectives

1. **Ship a working v1.0 to a public URL by 6 June 2027**, with a live demo that does not crash.
2. **Prove the core value loop end-to-end**: upload PDF → OCR → embeddings → RAG with citations → student takes quiz → mastery updates → system recommends next concept.
3. **Demonstrate at least one adaptive behavior** in the graduation demo (e.g., quiz difficulty adjusts based on mastery).
4. **Maintain engineering rigor throughout**: CI/CD on every PR, ≥ 60% coverage on critical paths, ADRs for every major decision, runbooks for operations.
5. **Survive the calendar**: absorb exam crunches, holidays, and member unavailability without missing the graduation deadline.
6. **Ship a thin MVP at week 16** that proves the AI pipeline works end-to-end, six weeks before the full MVP, so integration problems surface early.
7. **Deliver a credible graduation presentation** backed by live demos on production, not screenshots.

---

## Success Criteria

### Graduation Success
The project is a graduation success if **all** of the following are true on graduation day:

1. A live, deployed v1.0 product is accessible at a public URL.
2. The graduation presentation is delivered, with a live demo that does not crash.
3. The MVP loop (upload PDF → chat with cited answers) works end-to-end on the demo data.
4. At least one adaptive behavior is demonstrated (e.g., quiz difficulty adjusts based on mastery).
5. All graduation artifacts (code, docs, presentation, demo video) are submitted.
6. The team has a defensible answer to "what would you do differently?" informed by retrospectives.

### Engineering Success
The project is an engineering success if **all** of the following are true:

1. CI/CD runs on every PR; merges to `main` are gated.
2. Test coverage ≥ 60% on critical paths.
3. All five quality gates (v0.4, Tier 1 Freeze, Tier 2 Freeze, Feature Freeze, Code Freeze) are signed on or before their target dates.
4. No critical or high security vulnerabilities are open at Code Freeze.
5. P95 latency < 2s on RAG under 50 concurrent users.
6. ≥ 15 ADRs exist in the repo, each reviewed by ≥ 2 pod leads.
7. Runbooks exist for: deploy, rollback, disaster recovery, on-call.
8. At least 3 people can do basic DevOps/QA tasks (cross-training succeeded).
9. Tech debt register is published; accepted debt has clear payoff triggers.
10. Weekly demos ran from W3 to W44 without 2 consecutive weeks of "no demo" from any pod.

### Team Success
The project is a team success if **all** of the following are true:

1. No team member burned out or withdrew from the project.
2. Every team member can explain the architecture in a 5-minute pitch.
3. Every team member shipped at least one feature that they own end-to-end.
4. Retrospectives produced ≥ 20 action items, of which ≥ 80% were closed.
5. The team would willingly work together again on a follow-up project.

### Overall Delivery Confidence
The plan targets **~70% confidence** of shipping v1.0 by W44. This is honest for a 9-person student team building an AI product in 10 months. The remaining 30% is absorbed by: six contingency playbooks, four weeks of critical-path slack, seven scoped component-level fallbacks, and the signed Out-of-Scope list.

If everything goes wrong, the team still ships something — at minimum, a working RAG MVP with authentication and course management, deployed to a real URL, with documentation. That is a credible graduation project even in the worst plausible case.

---

## Project Scope

The following are **in scope** for v1.0:

- Authentication and user management (student, instructor, admin roles).
- Course management (CRUD, ownership, enrollment).
- File upload (PDF, images) to object storage.
- OCR pipeline with multi-engine fallback (PaddleOCR → Tesseract → Google Document AI).
- Document chunking with metadata (page, section).
- Embedding pipeline (BGE-M3 self-hosted, OpenAI as fallback).
- Vector database (Qdrant primary, pgvector fallback).
- Hybrid retrieval (BM25 + vector + bge-reranker-v2-m3 cross-encoder).
- RAG chat with cited source rendering and streaming responses.
- Knowledge Graph construction (concept extraction, relations, provenance).
- Quiz generation (LLM-generated MCQs with answer keys and metadata).
- Student cognitive model (mastery estimation per student-concept pair).
- Adaptive engine (next-best-concept recommendation, difficulty adjustment).
- Learning analytics dashboard for instructors (reduced scope: 4 chart types, 30-day window).
- Admin dashboard (minimal: user list, course list, system health).
- Production deployment with TLS, monitoring, and runbooks.
- Documentation (ADRs, API reference, runbooks, user quickstarts, architecture diagram).
- Graduation presentation with live demo and fallback recording.

### Version Scope Targets

| Version | Target Date | Theme | What's New |
|---|---|---|---|
| **v0.1** | Sep 12, 2026 (W6) | Skeleton | Repo, CI, dev env, empty Next.js + FastAPI, auth scaffold, hello-world deploy |
| **v0.2** | Sep 26, 2026 (W8) | Foundations | User mgmt, course CRUD, file upload to S3/MinIO, basic UI shell |
| **v0.3** | Oct 24, 2026 (W12) | Ingestion | OCR pipeline (PDF → text + structure), chunking, raw text stored |
| **v0.4** | Nov 21, 2026 (W16) | **Thin MVP** | Pre-loaded PDF + chat UI (no auth); proves AI pipeline end-to-end |
| **v0.5** | Dec 19, 2026 (W20) | **Full MVP + Tier 1 Freeze** | RAG chat with citations, end-to-end student flow, auth + courses + uploads |
| **v0.6** | Jan 30, 2027 (W26) | Knowledge layer | KG (concept extraction, relations), KG-backed retrieval boost |
| **v0.7** | Feb 27, 2027 (W30) | Cognition + Tier 2 Freeze | Cognitive model (rolling-average mastery), quiz generation v1 |
| **v0.8** | Mar 27, 2027 (W34) | Adaptation | Adaptive engine (next-best-concept, difficulty adjustment); IRT if data supports |
| **v0.9** | Apr 24, 2027 (W38) | Analytics + Feature Freeze | Learning analytics dashboard, admin dashboard (minimal) |
| **v1.0-rc** | May 22, 2027 (W42) | Hardening + Code Freeze | Perf, security, bug bash, docs, DR drill |
| **v1.0** | Jun 5, 2027 (W44) | **Graduation** | Production deployment, final docs, graduation presentation |

---

## Out of Scope

The following items are **explicitly out of scope** for v1.0. This list is signed at project kickoff by all pod leads, the TPM, and the advisor. Adding any of them to v1.0 requires a formal scope-change ADR signed by all parties.

| ID | Item | Reason | Revisit in |
|---|---|---|---|
| OOS-1 | Mobile app (native) | Out of capacity | v2.0 (post-graduation) |
| OOS-2 | Multi-tenant / school-level isolation | Premature for graduation | v2.0 |
| OOS-3 | Real-time collaboration | Never in this scope | — |
| OOS-4 | SSO / SAML | Email + Google OAuth is enough | v2.0 |
| OOS-5 | Offline mode | Architecture not designed for it | — |
| OOS-6 | Peer recommendations / collaborative filtering | Recommendation v1 only | v2.0 |
| OOS-7 | Cross-course RAG queries | Single-course only in v1.0 | v1.1 |
| OOS-8 | Tablet/mobile-first responsive design | Desktop-first; mobile best-effort | v1.1 |
| OOS-9 | Audit log UI (CLI tool only) | Out of capacity | v1.1 |
| OOS-10 | Time-series analytics > 30 days | Storage cost + low value for demo | v2.0 |
| OOS-11 | Multi-language UI (Arabic/French) | English only | v2.0 |
| OOS-12 | SCORM / LTI integration with LMS | Out of capacity | v2.0 |
| OOS-13 | Plagiarism detection | Out of capacity | — |
| OOS-14 | Proctoring / anti-cheat | Out of capacity + ethical concerns | — |
| OOS-15 | White-labeling / theming | Out of capacity | v2.0 |

The Out-of-Scope list is reviewed at every monthly milestone review. Items can be removed (i.e., brought into scope) only via scope-change ADR.

### Structural Descopes (Built into v1.0 Scope)

To fit the 1,820-hour capacity budget, the following reductions are baked into v1.0 scope and are not considered "cuts" — they are the agreed shape of the product:

1. **Recommendation engine ships v1 only** (rule-based + simple content-based). No peer recommendations, no collaborative filtering.
2. **Analytics dashboard is halved**: 4 chart types instead of 8. No time-series deeper than 30 days.
3. **Admin dashboard is minimal**: user list, course list, system health. No audit log UI.
4. **KG visualization is simple**: list + force-directed graph. No fancy filtering, no edit-in-place.
5. **Multi-document RAG is single-course only**: cannot query across all of a student's courses.
6. **Mobile responsiveness is desktop-first**: tablet/mobile is best-effort, not supported.
7. **Cognitive model starts as rolling average**: IRT is added in v0.8 only if quiz data supports it.
8. **Authentication is email/password + Google OAuth only**: no SSO/SAML.

---

## Project Constraints

| Constraint | Value | Impact |
|---|---|---|
| Calendar window | 3 Aug 2026 → 6 Jun 2027 | 44 weeks total |
| Team size | 9 members | Realistic throughput after absences ≈ 8 active + 1 rotating firefighter |
| Hard deadline | Graduation submission, May–Jun 2027 | Cannot slip |
| University semester start | 1 Oct 2026 | Capacity drops after this date |
| Exam period 1 | Late Jan 2027 (3 weeks) | Capacity collapses to ~12 hrs/wk |
| Exam period 2 | Late Apr – early May 2027 (3 weeks) | Capacity collapses to ~12 hrs/wk |
| Skill variance | High — not all members know AI/backend | Must pair-program and assign by tier |
| Budget | Limited (student project) | Open-source first; pay only for LLM tokens and base infra |
| LLM API access | Required (any one of OpenAI / Anthropic / DeepSeek / GLM) | If only free-tier OSS models are allowed, RAG quality drops (see Risk R-07) |

### Capacity Model (Pessimistic)

The plan is built against **1,820 usable engineering hours** — the single most important number in this document.

| Phase | Window | Active members (avg) | Hrs/wk per active | Effective hrs/wk |
|---|---|---|---|---|
| Pre-semester surge | Aug–Sep 2026 (8 wks) | 8.5 (–1 firefighter) | 16 | ~136 |
| Semester 1 | Oct 2026 – mid-Jan 2027 (15 wks) | 7.0 (–1 firefighter) | 8 | ~56 |
| Exam crunch 1 | Late Jan 2027 (3 wks) | 3.0 | 4 | ~12 |
| Semester 1 break | Feb 2027 (4 wks) | 6.5 | 11 | ~72 |
| Semester 2 (light) | Mar – mid-Apr 2027 (6 wks) | 7.0 | 8 | ~56 |
| Exam crunch 2 | Late Apr – early May 2027 (3 wks) | 3.0 | 4 | ~12 |
| Final push | Mid-May – Jun 2027 (5 wks) | 8.0 | 20 | ~160 |
| **Total** | **44 wks** | — | — | **~3,040 person-hours** |

After a **60% productivity multiplier** (reflecting meetings, rework, context-switching, infra overhead, lead duties), realistic **usable engineering hours ≈ 1,820**. Every feature, spike, and bug fix in this plan draws from this budget. If the team is spending more than 1,820 hours, something is wrong — either scope is too big, or people are working unsustainable hours. This number is tracked weekly.

### Operating Assumptions

1. The team has working laptops, a GitHub organization, and Slack/Discord.
2. At least one member can provision a cloud account (AWS / GCP / Azure free tier or student credits).
3. LLM API access is available. If only free-tier OSS models are allowed, the plan still works but RAG quality drops.
4. At least 8 of 9 members are active from W2 onward. If fewer, the descope protocol triggers.
5. The advisor is available for monthly reviews and final dry-runs.

### Non-Assumptions (Things Explicitly NOT Assumed)

1. We do not assume all 9 members are active every week. The plan absorbs 1 member being effectively unavailable at any time (the "firefighter" role).
2. We do not assume AI components work first try. OCR, RAG, and the adaptive engine all have dedicated spikes and contingency playbooks.
3. We do not assume the LLM API provider is stable. LiteLLM gateway abstracts providers; at least 2 are configured.
4. We do not assume exam crunches are survivable without planned downtime. W25–W27 and late-April are explicitly low-capacity.
5. We do not assume v1.0 ships "everything." The Out-of-Scope list is part of the contract.

---

## Engineering Principles

These principles take precedence over any other consideration when making engineering decisions. They are listed in priority order — when in conflict, the earlier principle wins.

1. **Working software over perfect architecture.** A deployed v0.4 thin MVP that is ugly but works beats a beautifully architected system that exists only in slideshows.
2. **Incremental delivery over big-bang.** Every sprint ships something demoable. Every Friday has a demo on staging, not localhost.
3. **Risk reduction over feature count.** A week spent de-risking OCR or RAG is worth more than a week spent building a feature that depends on those working.
4. **Front-load the hardest work.** The hardest AI work (OCR, embeddings, RAG) is done in the first 20 weeks when capacity is highest and academic pressure is lowest.
5. **Freezes are real.** Architecture, Feature, and Code freezes are gates. Post-freeze changes require ADRs and approvals. The team stops renegotiating interfaces mid-stream.
6. **Docs-first workflow.** API contracts and design docs are written *before* implementation, then updated as code lands. Documentation is a first-class deliverable with a dedicated rotating owner and a CI gate.
7. **Cross-training is mandatory.** No single person is the sole owner of any critical-path knowledge. Pod D has 2 people from day one; at least 3 people can do basic DevOps tasks by Feature Freeze.
8. **Buffer is distributed, not concentrated.** Buffer lives at points of highest schedule risk, not at the end where it gets eaten by procrastination.
9. **Out-of-scope is a contract.** The OOS list is signed at kickoff. Items are removed only via formal scope-change ADR.
10. **Conservative estimation.** We assume delays, integration problems, and periods of reduced availability. The plan has 4 weeks of critical-path slack and 6 contingency playbooks for the top red risks.

---

## Team Organization

The team is organized into **4 pods** plus three **rotating roles**. Pods are cross-functional enough to deliver vertical slices but specialized enough to build deep competence. Each pod has a lead who is the single point of contact for that area.

### Pod Structure (9 members)

| Pod | Headcount | Lead | Primary Ownership |
|---|---|---|---|
| **A — Backend & Platform** | 2 | Backend Lead | Auth, user mgmt, course mgmt, API layer, DB schema, async jobs, **vector DB ops + search API** |
| **B — AI/ML** | 3 | AI Lead | OCR, embeddings (model), chunking, RAG (prompt + retrieval), KG (concept extraction), cognitive model, adaptive engine, recommendation engine |
| **C — Frontend & UX** | 2 | Frontend Lead | Web UI, dashboards, design system, accessibility, demo polish |
| **D — DevOps, QA & Eval** | 2 | DevOps/QA Lead | CI/CD, environments, monitoring, SLOs, security, releases, **ML eval harness**, runbooks |
| **Firefighter (rotating)** | 0 (shared) | — | The "9th member" — picks up whatever is most behind each sprint |
| **TPM (rotating)** | 0 (shared) | — | Roadmap, sprint ops, risk register, stakeholder comms |
| **Docs Owner (rotating)** | 0 (shared) | — | Owns doc completeness; 4-week rotation |

**Total: 9.** The firefighter, TPM, and docs owner are rotating roles taken on by one of the 9 engineers for a 4-week stint — not additional headcount.

### Pod Responsibilities

**Pod A — Backend & Platform (2 engineers).** Auth (JWT + refresh tokens, RBAC), user management, course CRUD, file upload pipeline (presigned uploads to S3/MinIO), document ingestion API, search API (vector + hybrid), chat API (SSE streaming), KG API, quiz API, recommendation API, analytics aggregation queries, admin API, DB schema and migrations (PostgreSQL 16 + Alembic), vector DB operations (Qdrant), DB performance optimization, auth hardening.

**Pod B — AI/ML (3 engineers).** OCR pipeline (PaddleOCR + Tesseract + Document AI fallback), chunking strategy (recursive + semantic with metadata), embedding model selection and serving (BGE-M3 self-hosted or OpenAI fallback), hybrid retrieval (BM25 + vector + bge-reranker-v2-m3 cross-encoder), RAG prompt assembly with citation rendering, RAG eval harness (golden Q&A set, faithfulness + relevance metrics), concept extraction pipeline (LLM-assisted), Knowledge Graph construction (Neo4j), quiz generation (LLM-generated MCQs), cognitive model (rolling average v1, IRT v0.8 if data supports), adaptive engine (next-best-concept, difficulty adjustment), recommendation engine v1.

**Pod C — Frontend & UX (2 engineers).** Next.js 16 application with App Router, Tailwind CSS 4, shadcn/ui component library, design tokens and Storybook, all student-facing UI (chat, quiz, mastery, recommendations), all instructor-facing UI (course mgmt, analytics dashboard, KG visualization), admin dashboard (minimal), accessibility (WCAG 2.1 AA on critical paths), demo polish, fallback demo video recording.

**Pod D — DevOps, QA & Eval (2 engineers).** GitHub Actions CI/CD pipelines, dev/staging/prod environments, monitoring stack (Grafana + Prometheus + Loki + OpenTelemetry), Sentry error tracking, ML eval harness (RAG golden set, KG sanity tests, adaptation simulated trajectories), SLOs and alerting, security review (OWASP top 10, SAST, dependency scan), performance testing and load tests, backup and disaster recovery drills, runbooks, production deployment and on-call.

### Rotating Roles

- **TPM (4-week rotation, drawn from pod leads).** Owns the roadmap, runs sprint ops (kickoff, demo, retro, planning), maintains the risk register, communicates with the advisor, drives the freeze processes. ~20% of the owner's week during their rotation.
- **Firefighter (2-week rotation, drawn from any pod).** Has no scheduled work; picks up whatever is most behind each sprint. The firefighter is the "minus one" rule made explicit — we plan as if 8 people are available, and the 9th is slack.
- **Docs Owner (4-week rotation, drawn from pod leads in round-robin).** Maintains the docs completeness dashboard (auto-generated from CI), runs the weekly 5-minute docs review at Friday demo, triages doc-related PR comments, owns the Docusaurus site. 30% of the owner's week during their rotation.

### RACI for Cross-Cutting Concerns

| Concern | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Roadmap changes | TPM | All pod leads | Advisor | Full team |
| Architecture decisions | Pod owning the component | TPM | All pod leads | Full team |
| Release management | D-Lead | TPM | Pod leads | Full team |
| Risk register | TPM | TPM | Pod leads | Full team |
| Tech debt | Pod lead owning the area | TPM | Pod leads | Full team |
| Demo readiness | C-Lead | TPM | All pods | Advisor |
| Security incidents | D-Lead | TPM | Pod leads | Advisor |

### Pod Cross-Training Plan

A single-person pod is a bus-factor risk. Cross-training is mandatory:

- **W4–W8:** One Pod A engineer spends 20% time shadowing Pod D on infra tasks.
- **W9–W20:** One Pod B engineer learns vector DB ops (Qdrant backups, index rebuilds).
- **W21–W30:** Cross-training is light (exam crunch); deferred.
- **W31–W38:** One Pod C engineer learns basic CI/CD and Sentry triage.

By W38 (Feature Freeze), at least **3 people** can do basic DevOps/QA tasks. This is a hard exit criterion for Feature Freeze.

### Pod Allocation Per Phase

| Phase | Pod A (2) | Pod B (3) | Pod C (2) | Pod D (2) | Firefighter | Docs Owner |
|---|---|---|---|---|---|---|
| **P0** (W1–4) | Skeleton, DB, env, vector DB deploy prep | Spikes: OCR, embeddings, LLM gateway | Next.js skeleton, design tokens | CI, envs, observability, eval harness scaffold | Floats to Pod D | TPM |
| **P1** (W5–8) | Auth, user mgmt, course CRUD, upload | LLM gateway hardening, OCR spike continuation | Course UI, routing, app shell | Async job infra, monitoring, eval harness v0 | Floats to Pod B | C-Lead |
| **P2** (W9–20) | Ingestion API, search API, chat API, vector DB ops | OCR pipeline, chunking, embeddings, RAG | Upload UI, chat UI, citation UI | Eval harness v1 (RAG golden set), cost monitoring | Floats to Pod B | A-Lead |
| **P3** (W21–30) | KG API, quiz API, integration tests | Concept extraction, KG, quiz gen, cognitive model (spike first) | Quiz UI, mastery UI, KG viz | Neo4j ops, eval harness v2 (KG + quiz) | Floats to Pod B (heavy) | B-Lead |
| **P4** (W31–38) | Recommendation API, analytics aggregation, admin API | Adaptive engine (spike first), recommendation engine, eval v3 | Analytics dashboard, admin dashboard, polish | Test infra, perf monitoring, feature flags | Floats to Pod C | D-Lead |
| **P5** (W39–42) | DB perf, auth hardening | Eval harness finalization, model artifact freeze | Docs completion, demo assets | Perf, security, DR drill, prod prep | Floats to Pod D | TPM |
| **P6** (W43–44) | Hotfix standby | Hotfix standby | Demo polish, fallback recording | Prod deployment, on-call | Hotfix standby | TPM |

---

## Technology Stack

The stack is locked by **end of Week 2 (Aug 15, 2026)** and revisited only at Architecture Freeze review. Flip-flopping after that point is a schedule-killer.

### Primary Stack (Production-grade)

| Layer | Choice | Rationale |
|---|---|---|
| **Frontend** | Next.js 16 (App Router) + TypeScript + Tailwind CSS 4 + shadcn/ui | Industry-standard, SSR for perf, large hiring pool, easy Vercel deploy |
| **Mobile (later)** | React Native (Expo) — *post-v1.0 only* | Shares TS skills with web; deferred until after graduation |
| **Backend API** | FastAPI (Python 3.12) + Pydantic v2 + Uvicorn | Python ecosystem for AI, async, type-safe, OpenAPI auto-generated |
| **ORM / Migrations** | SQLAlchemy 2.0 + Alembic | Mature, supports PG features (JSONB, pgvector) |
| **Primary DB** | PostgreSQL 16 | Relational + JSONB + pgvector extension |
| **Vector DB** | Qdrant (self-hosted, single node) | Purpose-built, fast, simple ops, free; pgvector is the scoped fallback (F-1) |
| **Knowledge Graph** | Neo4j Community Edition | Mature, Cypher is learnable, good viz ecosystem; JSONB-in-PG fallback (F-2) |
| **LLM Gateway** | LiteLLM (proxy) in front of OpenAI / Anthropic / GLM | Swap providers without code change; central cost control |
| **Embeddings** | `bge-m3` (open-source, multilingual) self-hosted OR OpenAI `text-embedding-3-small` (fallback F-3) | BGE for cost control; OpenAI for speed |
| **OCR** | PaddleOCR (primary) + Tesseract (fallback) + Google Document AI (for hard cases, fallback F-6) | Open-source base; managed service as escalation path |
| **Document parsing** | unstructured.io + PyMuPDF | Handles PDFs, DOCX, PPTX, images |
| **Chunking / Retrieval** | LangChain (orchestration) + BM25 hybrid + reranker (bge-reranker-v2-m3) | Hybrid retrieval beats pure vector |
| **Async jobs / Queue** | Redis 7 + Celery 5 | Standard, simple, battle-tested; Inngest fallback (F-5) |
| **Cache** | Redis (shared with queue) | Single infra component |
| **Object storage** | MinIO (self-hosted) or AWS S3 | For uploaded PDFs, images, generated artifacts |
| **Auth** | Self-hosted JWT + refresh tokens (`fastapi-users` or `supertokens`); Google OAuth | Avoid vendor lock-in |
| **Containerization** | Docker + Docker Compose (dev) | Standard |
| **Orchestration** | Docker Swarm (single-node) or k3s — **NOT full K8s** | K8s is overkill for a 9-person team |
| **CI/CD** | GitHub Actions | Free for OSS / student accounts; deep GitHub integration |
| **IaC** | Terraform (light) or simple shell scripts | IaC only for prod infra |
| **Cloud provider** | AWS (EC2 + RDS + S3) or Hetzner (cheaper) | Hetzner for cost; AWS for ecosystem |
| **Monitoring** | Grafana + Prometheus + Loki + OpenTelemetry | Self-hosted, free, industry standard |
| **Error tracking** | Sentry (free tier) | Free for small teams |
| **Frontend analytics** | PostHog (self-hosted) | Product analytics + session replay |
| **Feature flags** | Unleash (self-hosted) or simple env vars | Decouple deploy from release |
| **Test framework** | pytest (backend), Vitest + Playwright (frontend) | Standard |
| **Documentation** | Docusaurus (public docs) + Markdown ADRs in repo | Docs-as-code |
| **Project mgmt** | GitHub Projects (boards) + Linear (if budget) | Tightly coupled with code |

### Scoped Component Fallbacks

These are component-level swaps that can be invoked independently when a trigger metric is objectively met. They are **not** a full stack rewrite — they are surgical, scoped substitutions with known cost.

| Fallback ID | Trigger | What Swaps | Cost | Owner |
|---|---|---|---|---|
| **F-1** | Qdrant down > 1h unresolved OR Pod B can't maintain it | Qdrant → pgvector (Postgres extension) | 1 day (change driver config + re-index) | D-Lead |
| **F-2** | Neo4j ops too heavy OR KG schema not converging | Neo4j → JSONB in Postgres with recursive CTEs | 3 days (schema migration + query rewrite; no API change) | D-Lead + A-Lead |
| **F-3** | Self-hosted BGE-M3 too slow OR GPU unavailable | BGE-M3 → OpenAI text-embedding-3-small | 1 day (change env var; re-embed all chunks) | B-Lead |
| **F-4** | LLM API cost > $300/month | GPT-4-class → GPT-4o-mini or DeepSeek or GLM-4-flash for non-critical paths | 1 day (LiteLLM config change) | D-Lead |
| **F-5** | Celery + Redis ops too heavy | Celery → Inngest (serverless) | 1 week (rewrite job definitions; no API change) | D-Lead |
| **F-6** | PaddleOCR quality too low on real PDFs | PaddleOCR → Google Document AI (managed) | 3 days (API swap; cost increases) | B-Lead |
| **F-7** | Adaptive engine research spike fails | ML-based adaptive → rule-based adaptive (if-else) | 0 days (already a fallback branch in the spike) | B-Lead |

**Rules for invoking a fallback:**
1. The trigger metric must be objectively met (no vibes).
2. The decision owner is the listed owner; they decide within 48 hours of trigger.
3. A fallback is invoked via a single PR + ADR.
4. Once invoked, a fallback is *sticky* — it does not auto-revert. Reverting requires another ADR.

---

## High-Level Architecture

```
                       ┌──────────────────────────────────────────────────────┐
                       │                Client (Next.js 16)                    │
                       │   Student UI  ·  Instructor UI  ·  Admin UI           │
                       └───────────────────────┬──────────────────────────────┘
                                               │  HTTPS / SSE
                       ┌───────────────────────▼──────────────────────────────┐
                       │              API Gateway (FastAPI)                    │
                       │  Auth · Courses · Documents · Chat · KG · Quiz ·     │
                       │  Recommendations · Analytics · Admin                 │
                       └──┬────────┬────────┬────────┬────────┬────────┬──────┘
                          │        │        │        │        │        │
              ┌───────────▼┐  ┌────▼────┐ ┌─▼──────┐ │  ┌──────▼──┐  ┌─▼─────────┐
              │ PostgreSQL │  │ Redis + │ │ MinIO  │ │  │ Qdrant  │  │  Neo4j    │
              │  16        │  │ Celery  │ │ (S3)   │ │  │ (Vector)│  │  (KG)     │
              │ + pgvector │  │ (Queue) │ │        │ │  │         │  │           │
              └───────────┬┘  └────┬────┘ └────────┘ │  └────┬────┘  └─────┬─────┘
                           │        │                 │       │            │
                           │  ┌─────▼─────────────────▼───────▼────────────▼───┐
                           │  │           AI Pipeline (Pod B)                    │
                           │  │  OCR → Chunking → Embeddings → Hybrid Retrieval │
                           │  │  → Reranker → RAG → Concept Extraction → KG     │
                           │  │  → Quiz Gen → Cognitive Model → Adaptive Engine │
                           │  └───────────────────────┬────────────────────────┘
                           │                          │
              ┌────────────▼──────────────────────────▼─────────────┐
              │         LLM Gateway (LiteLLM proxy)                   │
              │   OpenAI  ·  Anthropic  ·  GLM  ·  DeepSeek           │
              └───────────────────────────────────────────────────────┘

  Cross-cutting:
    Monitoring:  Grafana + Prometheus + Loki + OpenTelemetry + Sentry
    CI/CD:       GitHub Actions (lint, test, build, deploy on PR + tag)
    Storage:     MinIO / S3 for uploads, model artifacts, backups
    Auth:        JWT + refresh tokens (self-hosted) + Google OAuth
```

### Data Flow (MVP Loop)

1. Instructor uploads a PDF via the Next.js UI.
2. FastAPI issues a presigned upload URL; the browser uploads directly to MinIO/S3.
3. FastAPI enqueues an OCR job on Celery/Redis.
4. The OCR worker (PaddleOCR with fallbacks) extracts text + layout JSON; stores it in PostgreSQL.
5. A chunking worker splits the text into chunks with metadata (page, section); stores in PostgreSQL.
6. An embedding worker generates embeddings via BGE-M3 (or OpenAI fallback); writes to Qdrant.
7. A concept extraction worker (LLM-assisted) extracts concepts and relations; writes to Neo4j.
8. Student asks a question via the chat UI; FastAPI `/v1/chat` endpoint receives it.
9. Hybrid retrieval (BM25 + vector + reranker) pulls top-k chunks from Qdrant.
10. The RAG prompt template assembles context + citations; LiteLLM gateway calls the LLM.
11. The response streams back to the client via SSE; citations render as clickable links to source chunks.
12. Student takes a quiz; quiz results update the cognitive model (mastery per concept).
13. The adaptive engine reads mastery state; recommends next-best-concept and adjusts quiz difficulty.

### Interface Contracts (Frozen at Architecture Freeze)

To allow parallel work, the following interface contracts are frozen by their respective freeze dates and *cannot change* without a re-architecture ADR:

1. **OCR output schema** — JSON structure of extracted text + layout.
2. **Chunk schema** — fields, metadata, IDs.
3. **Embedding I/O** — input text, output vector dim, model ID.
4. **Vector DB query API** — top-k search, filters, payload.
5. **RAG request/response** — query, filters, response with citations.
6. **KG concept/relation schema** — node types, edge types, provenance.
7. **Quiz schema** — question types, metadata, scoring.
8. **Student mastery schema** — per (student, concept) record.
9. **Adaptive engine I/O** — input: student state; output: next action.
10. **Auth token format** — JWT claims, refresh flow.

Contracts 1–5 are frozen at **Tier 1 Architecture Freeze (W20)**. Contracts 6–9 are frozen at **Tier 2 Architecture Freeze (W30)**. Contract 10 is frozen at W8.

---

## Project Phases

The 44-week plan is divided into **7 phases**. Each phase has a single theme, a single primary pod, and a hard exit gate.

| Phase | Name | Window | Weeks | Theme | Primary Pod | Exit Gate |
|---|---|---|---|---|---|---|
| **P0** | Pre-Flight | Aug 3 – Aug 30, 2026 | W1–4 | Setup, decisions, MVP definition | All pods | v0.1 deployed |
| **P1** | Foundations | Aug 31 – Sep 27, 2026 | W5–8 | Auth, courses, upload, UI shell | Pod A + C | v0.2 deployed |
| **P2** | AI Pipeline | Sep 28 – Dec 20, 2026 | W9–20 | OCR → embeddings → RAG; v0.4 thin MVP at W16; v0.5 + Tier 1 Freeze at W20 | Pod B (with A + C) | **v0.5 + Tier 1 Architecture Freeze** |
| **P3** | Knowledge & Cognition | Dec 21, 2026 – Feb 27, 2027 | W21–30 | KG + quiz + cognitive model; research spike on cognitive model in W25; Tier 2 Freeze at W30 | Pod B (light) | **v0.7 + Tier 2 Architecture Freeze** |
| **P4** | Adaptation & Analytics | Feb 28 – Apr 24, 2027 | W31–38 | Adaptive engine (research spike in W29), dashboards; Feature Freeze at W38 | Pod B + C | **v0.9 + Feature Freeze** |
| **P5** | Hardening | Apr 25 – May 23, 2027 | W39–42 | Perf, security, docs, DR | Pod D (lead) + all | **v1.0-rc + Code Freeze** |
| **P6** | Graduation | May 24 – Jun 6, 2027 | W43–44 | Demo, submission | TPM + all | **v1.0 + presentation** |

### Phase Themes

**P0 — Pre-Flight (4 weeks, high capacity).** Lock the stack, stand up repo/CI/environments, write the MVP definition, write the first 5 ADRs, build the empty Next.js + FastAPI skeleton, deploy a hello-world to a real URL. The single goal of P0 is to remove every excuse for not starting real work in P1.

**P1 — Foundations (4 weeks, high capacity).** Build the boring-but-required backbone: auth, user management, course management, file upload, basic UI shell with routing and design tokens. Nothing AI-related ships here, but Pod B uses P1 to spike OCR and embedding options in parallel so they hit the ground running in P2.

**P2 — AI Pipeline (12 weeks, mixed capacity).** This is the make-or-break phase. OCR → chunking → embeddings → vector DB → RAG. The phase ships **v0.4 (thin MVP) at W16** and ends with **v0.5 (full MVP) and Tier 1 Architecture Freeze at W20**. P2 spans the start of the university semester, so capacity drops mid-phase; the plan front-loads the hardest work (OCR + embeddings) into the first 6 weeks.

**P3 — Knowledge & Cognition (10 weeks, low capacity).** Knowledge Graph, student cognitive model, and the first version of quiz generation. This phase covers the December holiday lull and the January exam crunch, so it is intentionally lighter on parallelism and heavier on independent work-streams. A research spike on the cognitive model runs in W25–W27 to reduce uncertainty before commitment. The phase ends with **v0.7 and Tier 2 Architecture Freeze**.

**P4 — Adaptation & Analytics (8 weeks, recovering capacity).** Adaptive engine, recommendation engine, learning analytics dashboard, admin dashboard. A research spike on the adaptive engine runs in W29–W31 (overlapping with P3 close) so the team has a working prototype before productionization. The phase ends with **v0.9 and Feature Freeze** — no new features after this point, only fixes.

**P5 — Hardening (4 weeks, full capacity post-exams).** Performance pass, security review, full bug bash, documentation completion, runbooks, backup and DR drill. Ends with **v1.0-rc and Code Freeze** — only critical fixes after this point.

**P6 — Graduation (2 weeks).** Final production deployment, dry-run of the presentation, submission of artifacts, handoff to a post-graduation maintainer if continuing as a startup.

---

## Monthly Timeline

A monthly milestone is a **demoable, externally verifiable artifact**. If a month ends without hitting its milestone, the TPM triggers the descope protocol.

| Month | Calendar | Milestone | Verifiable Artifact |
|---|---|---|---|
| **Aug 2026** | W1–4 | "Hello World on a real URL" | v0.1 deployed; CI green; 5 ADRs in repo; OOS list signed |
| **Sep 2026** | W5–8 | "Foundations" | v0.2 deployed: auth + course CRUD + PDF upload |
| **Oct 2026** | W9–13 | "OCR works" | v0.3: PDF → extracted text in DB; embedding spike done |
| **Nov 2026** | W14–17 | "Retrieval works" | v0.4: thin MVP demoed; RAG skeleton |
| **Dec 2026** | W18–20 | **"MVP shipped"** | **v0.5 + Tier 1 Architecture Freeze signed** |
| **Jan 2027** | W21–24 | "KG taking shape" | KG populated with 200+ concepts (exam-crunch tolerance) |
| **Feb 2027** | W25–28 | "Quizzes + mastery" | v0.7 + Tier 2 Architecture Freeze: student takes quiz, mastery updates |
| **Mar 2027** | W29–32 | "Adaptation works" | Adaptive engine picks next concept; difficulty adjusts |
| **Apr 2027** | W33–36 | "Feature-complete" | **v0.9 + Feature Freeze**; dashboards functional |
| **May 2027** | W37–40 | "Hardened" | **v1.0-rc + Code Freeze**; perf + security passes |
| **Jun 2027** | W41–44 | **"Graduation"** | **v1.0 on prod; presentation delivered** |

### Monthly Milestone Review Protocol

On the **last Friday of every month**, the TPM runs a 90-minute **Milestone Review** with all pod leads. Agenda:

1. (15 min) Demo the milestone artifact on staging. Live, not screenshots.
2. (15 min) Compare actual progress vs. plan; surface any slip ≥ 3 days.
3. (20 min) Update risk register; add new risks; close mitigated ones.
4. (20 min) Re-plan the next 4 weeks at sprint level; rebalance pod allocations if needed.
5. (10 min) Decide any descopes — *now*, not at the next review.
6. (10 min) Communicate decisions to the full team in writing before EOD.

**Hard rule:** if a monthly milestone is missed by more than 1 week, the descope protocol is triggered automatically. There is no "we'll catch up next month."

---

## Sprint Timeline

**Sprint length: 1 week.** Each sprint runs Monday → Friday with a demo on Friday. Each sprint has **1 owner**, **1 deliverable**, and **1 exit criterion**. If the exit criterion is not met by Friday demo, the work rolls into next week's sprint *and* a risk is logged.

### Sprint Cadence

| Day | Activity | Duration |
|---|---|---|
| Monday | Sprint kickoff (pod-level) | 30 min |
| Monday–Thursday | Heads-down work; pair-programming | — |
| Tuesday | Mid-week sync (cross-pod, blockers only) | 30 min |
| Thursday | PR review push; merge to `main` | — |
| Friday 14:00 | Demo | 30 min |
| Friday 14:30 | Sprint close + retro (biweekly) | 30–60 min |
| Friday 15:30 | Sprint planning for next week | 30 min |

Additional ceremonies:
- **Daily async standup** in Slack/Discord: "Yesterday / Today / Blockers" — by 10am.
- **Biweekly retro** (Friday, alternate weeks with monthly review).
- **Monthly milestone review** (last Friday of month).
- **Quarterly architecture review** (only at Architecture Freeze and Code Freeze).

### Phase P0 — Pre-Flight (W1–W4)

| Wk | Sprint Name | Owner [Pod] | Deliverable | Exit Criterion |
|---|---|---|---|---|
| W1 | Kickoff + stack lock | TPM | Stack decision doc signed; GH org + repo created; README with team norms; **Out-of-Scope list signed** | Repo exists; PR template + CODEOWNERS in place; OOS list signed |
| W1 | CI scaffold | D-Lead | GitHub Actions workflow: lint + test on every PR | CI green on a dummy PR |
| W1 | Env provisioning | D-Lead | `dev` / `staging` / `prod` environments documented and reachable | Each env has a URL |
| W2 | MVP sign-off + team health check | TPM | MVP definition doc approved by all pod leads; ≥ 8 active members confirmed | Doc merged; no open objections after 48h; ≥ 8 active |
| W2 | Next.js skeleton | C-Lead | Empty Next.js 16 app with routing, Tailwind, shadcn/ui, Storybook | App runs locally and on Vercel/preview |
| W2 | FastAPI skeleton | A-Lead | Empty FastAPI app with health check, OpenAPI docs, CORS, env config | `/health` returns 200 on staging |
| W3 | Deploy hello-world | D-Lead | Both apps deployed to public URLs over HTTPS | URLs accessible from outside the team |
| W3 | DB + migrations baseline | A-Lead | Postgres provisioned; Alembic init; first migration creates `users` table | Migration runs on all envs |
| W3 | Design tokens + demo PDF chosen | C-Lead + B-Lead | Tailwind config + shadcn theme; Storybook shows base components; **demo PDF selected** | Tokens reviewed and locked; demo PDF committed |
| W4 | ADR-001 through ADR-005 | TPM | ADRs for: stack, repo structure, API versioning, env management, LLM gateway | 5 ADRs merged |
| W4 | Risk register v1 + eval harness scaffold | TPM + D-Lead | Risk register seeded with ≥ 15 risks; eval harness scaffolding in CI | Reviewed in W4 retro; harness skeleton in repo |
| W4 | **v0.1 tag + demo** | All | Tag `v0.1.0` in repo; demo: log in to deployed URL | Demo passes without crash |

### Phase P1 — Foundations (W5–W8)

| Wk | Sprint Name | Owner [Pod] | Deliverable | Exit Criterion |
|---|---|---|---|---|
| W5 | Auth: register + login | A-1 [A] | Email/password register, login, JWT issue/refresh; tests | Auth flow works on staging; tests ≥ 80% |
| W5 | Auth UI | C-1 [C] | Register/login pages, protected routes, session handling | User can register and reach a protected page |
| W5 | OCR spike (parallel, converges) | B-Lead [B] | Compare PaddleOCR vs Tesseract vs Document AI on 5 sample PDFs | Choice ADR drafted |
| W5 | Embedding spike (parallel, converges) | B-1 [B] | Compare BGE-M3 vs OpenAI text-embedding-3-small on quality + latency | Choice ADR drafted |
| W6 | User mgmt: profile + RBAC | A-2 [A] | Profile CRUD; roles: student/instructor/admin; middleware enforcement | RBAC tests pass |
| W6 | Course CRUD API | A-Lead [A] | `/v1/courses` CRUD; ownership checks | Postman collection + tests |
| W6 | Course UI | C-2 [C] | Course list, create, edit pages; instructor-only | Instructor can create a course |
| W6 | File upload to S3/MinIO | A-1 [A] | Presigned upload; server-side download; virus scan stub | PDF uploads to storage and is retrievable |
| W7 | Routing + nav | C-Lead [C] | App shell with sidebar, topnav, breadcrumbs, route guards | All routes exist (empty pages OK) |
| W7 | Async job infra | D-Lead [D] | Celery + Redis running; sample task; Flower dashboard | A queued job completes |
| W7 | Observability baseline | D-Lead [D] | Logs to Loki, metrics to Prometheus, Sentry for errors | A test error appears in Sentry |
| W7 | LLM gateway | B-Lead [B] | LiteLLM proxy deployed; key rotation; cost tracking | A test prompt returns a response |
| W8 | Integration: course → upload → storage | A-Lead [A] | End-to-end: instructor creates course, uploads PDF, sees it listed | E2E Playwright test passes |
| W8 | First user-facing docs | C-Lead [C] | Docusaurus site; "Getting Started" + "Instructor quickstart" | Docs deploy to a URL |
| W8 | **v0.2 tag + demo** | All | Tag `v0.2.0`; demo: instructor creates course + uploads PDF | Demo passes; exit gate met |

### Phase P2 — AI Pipeline (W9–W20) — CRITICAL PATH

| Wk | Sprint Name | Owner [Pod] | Deliverable | Exit Criterion |
|---|---|---|---|---|
| W9 | OCR pipeline v1 | B-Lead [B] | Async job: PDF → text + layout JSON; stored in DB | 5 sample PDFs processed; text extracted |
| W9 | OCR UI feedback + thin MVP chat UI scaffold | C-1 [C] | Upload progress + extracted text preview; chat UI scaffolded | User sees extraction in UI |
| W10 | OCR hardening (images, multi-page, scanned) | B-1 [B] | Handle images, scanned PDFs, multi-page; fallback to Document AI on failure | 20 PDFs processed; ≥ 90% success |
| W10 | Document model + ingestion service | A-2 [A] | `documents` table; ingestion status; idempotency | Re-uploading same PDF doesn't duplicate |
| W11 | Chunking strategy | B-Lead [B] | Recursive + semantic chunking; metadata (page, section); ADR | 1 PDF → 100+ chunks with metadata |
| W11 | Chunking API + storage | A-Lead [A] | `/v1/documents/{id}/chunks` endpoint; paginated | Frontend can fetch chunks |
| W12 | **v0.3 tag + demo** | All | Demo: upload PDF, see extracted text + chunks | v0.3 demo passes |
| W12 | Embedding batch job | B-1 [B] | Async job: chunk → embedding → store; batching; rate limit | 1,000 chunks embedded end-to-end |
| W13 | Vector DB deploy (Qdrant) + embedding write path + search API | D-Lead [D] + A-Lead [A] + A-2 [A] | Qdrant running; collection schema; backup script; embeddings written on chunk creation; `/v1/search?q=...` returns top-k | Vector DB reachable; new chunks auto-embed; endpoint returns ranked results |
| W14 | Hybrid retrieval (BM25 + vector) | B-Lead [B] | Combine BM25 + vector scores; weighting | Hybrid beats pure vector on golden set |
| W14 | Reranker integration | B-1 [B] | bge-reranker-v2-m3 cross-encoder; top-20 → top-5 | Reranker improves precision@5 |
| W15 | RAG prompt assembly + citation rendering | B-Lead [B] + C-1 [C] | Prompt template with citations; LLM gateway call; safety; clickable citations jump to source chunk | Prompt returns answer with [1], [2] cites; user can verify source |
| W16 | **v0.4 Thin MVP tag + demo** | All | Pre-loaded PDF + chat UI; demo: ask question, get cited answer | **Thin MVP demoed on staging; AI pipeline proven end-to-end** |
| W16 | RAG eval harness v1 | B-Lead [B] | Golden Q&A set (50 Qs); eval script; faithfulness + relevance scores | Eval runs in CI on every PR |
| W17 | RAG chat API + streaming + chat UI | A-Lead [A] + C-Lead [C] | `/v1/chat` SSE streaming; session persistence; chat interface with history, streaming, source panel | Chat works in browser via curl and UI |
| W17 | Student flow integration | A-2 [A] | Student enrolls → sees course → uploads → chats | E2E Playwright test |
| W18 | Multi-document RAG (single-course) + Tier 1 Freeze draft | B-1 [B] + TPM | Retrieval spans all docs in a course; doc-level filters; ADRs 1–15 complete; interface contracts frozen; freeze review meeting | E2E test green; Tier 1 ADRs ready; all pod leads sign draft |
| W19 | Polish + bug fixes + Tier 1 Architecture Freeze review | All + TPM | Address top-20 bugs from W17 demo; all pod leads sign Tier 1 | All pod leads sign Tier 1; bug list ≤ 5 open P1s |
| W20 | **v0.5 + Tier 1 Architecture Freeze** | All | Tag `v0.5.0`; sign Tier 1 Architecture Freeze; MVP demo to advisor | **Full MVP shipped; Tier 1 signed** |

### Phase P3 — Knowledge & Cognition (W21–W30)

*Note: capacity drops significantly through this phase due to holidays (W21–22) and exam crunch (W25–27). Plan is intentionally lighter on parallelism.*

| Wk | Sprint Name | Owner [Pod] | Deliverable | Exit Criterion |
|---|---|---|---|---|
| W21 | KG schema ADR + demo backlog started | B-Lead [B] + TPM | ADR-016: KG data model (concepts, relations, provenance); demo backlog list started | ADR merged; backlog exists |
| W21 | Holiday — light maintenance | All | Bug triage; tech debt cleanup | Open bug count ≤ 10 |
| W22 | Concept extraction spike + graduation outline v0 | B-1 [B] + TPM | Compare spaCy + LLM-based extraction on 3 docs; graduation presentation outline v0 | Spike done; outline exists |
| W22 | Holiday — light maintenance | All | Continue triage | — |
| W23 | Concept extraction pipeline + KG storage (Neo4j) | B-Lead [B] + D-Lead [D] | Async job: chunks → concepts + relations; LLM-assisted; Neo4j deployed; schema; import script | 5 docs → 200+ concepts; KG populated |
| W24 | KG API + KG viz UI + demo dataset v1 | A-Lead [A] + C-1 [C] + B-Lead [B] | `/v1/kg/concepts`, `/v1/kg/relations` endpoints; interactive concept graph (react-flow or d3); 3 courses loaded as demo data | KG browsable; frontend can query KG |
| W25 | KG-backed retrieval boost + cognitive model research spike begins | B-Lead [B] | Use concept matches to reweight retrieval; spike on IRT vs Bayesian vs rolling average | Eval set faithfulness ↑ ≥ 5%; spike started |
| W25 | Quiz generation v1 (non-adaptive) | B-1 [B] | LLM generates MCQ from chunks; answer key; metadata | 10 quizzes generated |
| W26 | **v0.6 tag + small demo** + cognitive model spike continues | All + B-Lead [B] | Demo: KG populated; concept browse; first quiz; spike continues | v0.6 demo passes (small) |
| W26 | Quiz UI + grading | C-Lead [C] | Take quiz, submit, see score; instructor creates quiz | Student completes a quiz |
| W27 | Cognitive model spike concludes → ADR + quiz generation v1 (continued) | B-Lead [B] + B-1 [B] | ADR-017: IRT vs Bayesian vs simple mastery; choice; LLM-generated MCQs with answer keys | Spike ADR merged |
| W27 | Mastery estimator v1 | B-1 [B] | Update mastery from quiz results; store per (student, concept); rolling average | Mastery updates after quiz |
| W28 | Quiz integration end-to-end + mastery UI | A-Lead [A] + C-2 [C] | Quiz assigned → student takes → graded → mastery updated; student sees mastery per concept; instructor sees cohort | E2E test; mastery visible in UI |
| W29 | Cognitive model hardening + adaptive engine research spike begins + mastery UI + quiz pool | B-Lead [B] + B-1 [B] + C-2 [C] | Cold-start handling; confidence intervals; sanity checks; spike prototype works; quiz bank with concept + difficulty tags ≥ 100 items | Model behaves on edge cases; spike prototype works; pool searchable |
| W30 | **v0.7 + Tier 2 Architecture Freeze** | All | Tag `v0.7.0`; sign Tier 2 Architecture Freeze (KG, quiz, mastery, adaptive I/O frozen); demo: quiz + mastery + KG end-to-end | **v0.7 shipped; Tier 2 signed** |

### Phase P4 — Adaptation & Analytics (W31–W38)

| Wk | Sprint Name | Owner [Pod] | Deliverable | Exit Criterion |
|---|---|---|---|---|
| W31 | Adaptive engine productionization + spike concludes → ADR | B-Lead [B] | ADR-018: next-best-concept policy; difficulty adjustment rule; productionization of spike prototype | Adaptive engine v1; ADR merged |
| W31 | Next-best-concept v1 | B-1 [B] | Policy: pick concept with lowest mastery + most prereqs met | Returns a recommendation |
| W32 | Recommendation API + UI + difficulty adjustment | A-Lead [A] + C-1 [C] + B-Lead [B] | `/v1/recommendations`; "Recommended next" panel; quiz difficulty tuned to current mastery | Student sees recommendation; difficulty adapts within ±1 level |
| W33 | Recommendation engine v1 + adaptation eval harness + demo script v1 (skeleton) | B-1 [B] + B-Lead [B] + TPM | Content + peer recommendations; ranking; simulated student trajectories; metrics; demo script skeleton | Top-3 recommendations shown; eval runs in CI; script exists |
| W34 | Learning analytics dashboard (backend + UI) + **v0.8 tag** | A-Lead [A] + C-Lead [C] | Aggregation queries: cohort mastery, quiz pass rates, engagement; instructor dashboard with charts (Recharts/Visx); IRT cognitive model if data supports | Dashboard renders real data; v0.8 demoed |
| W35 | Admin dashboard (minimal) + notification system (basic) + demo student accounts created | C-2 [C] + A-2 [A] + A-Lead [A] + B-Lead [B] | User/course management, system health; in-app + email notifications for key events; 5 demo student accounts with seeded mastery states | Admin can manage users; notifications fire; accounts exist |
| W36 | UX polish pass + bug bash #1 + demo script v2 | C-Lead [C] + D-Lead [D] + TPM | Address top UX issues from W35 demo; 90-min bug bash; triage all findings; filled-in demo script | Polish review approved; top-50 bugs in tracker |
| W37 | Bug fixing sprint + accessibility pass + demo dataset finalized | All + C-1 [C] + B-Lead [B] + C-Lead [C] | Close P1/P2 bugs from bash; WCAG 2.1 AA on critical paths; demo data curated and validated | ≤ 5 P1s open; axe-core clean on key flows; dataset ready |
| W38 | **v0.9 + Feature Freeze** | All | Tag `v0.9.0`; sign Feature Freeze; demo to advisor; deck v1 reviewed by advisor | **Feature Freeze signed; exit gate met** |

### Phase P5 — Hardening (W39–W42)

| Wk | Sprint Name | Owner [Pod] | Deliverable | Exit Criterion |
|---|---|---|---|---|
| W39 | Performance pass + DB optimization | D-Lead [D] + A-Lead [A] | Profile + optimize; P95 latency < 2s on RAG; load test; indexes; query plans; connection pool tuning | Load test: 50 concurrent users OK; slow query log clean |
| W40 | Security review + auth hardening + dry-run #0 (internal) | D-Lead [D] + A-Lead [A] + TPM | OWASP top 10; SAST (Semgrep); dependency scan; pen test; rate limiting; refresh rotation; MFA optional; internal dry-run | No critical/high vulns open; dry-run completed |
| W41 | Bug bash #2 + docs completion + backup + DR drill + fallback demo video recorded | All + C-Lead [C] + TPM + D-Lead [D] | 2-hour bash; close everything; runbooks, ADRs finalized, README, architecture diagram; restore DB from backup; verify; fallback demo video recorded | ≤ 3 P1s open; runbooks done; DR drill completes < 1h; video exists |
| W42 | **v1.0-rc + Code Freeze + dry-run #1 with advisor** | All + TPM | Tag `v1.0.0-rc`; sign Code Freeze; dry-run #1 with advisor | **Code Freeze signed; exit gate met** |

### Phase P6 — Graduation (W43–W44)

| Wk | Sprint Name | Owner [Pod] | Deliverable | Exit Criterion |
|---|---|---|---|---|
| W43 | Production deployment + dry-run #2 | D-Lead [D] + TPM | Deploy v1.0-rc to prod; smoke tests; DNS + TLS; dry-run #2 | Prod live; smoke tests pass; demo rehearsed |
| W44 | Dry-run #3 (dress rehearsal) + **v1.0 + graduation presentation** | TPM + All | Final dry-run; tag `v1.0.0`; submit artifacts; deliver presentation | **Graduation delivered** |

---

## Milestones

### Version Milestones

| Version | Target Date | Theme | Demoable? |
|---|---|---|---|
| v0.1 | Sep 12, 2026 (W6) | Skeleton — login page on deployed URL | Yes |
| v0.2 | Sep 26, 2026 (W8) | Foundations — instructor creates course, uploads PDF | Yes |
| v0.3 | Oct 24, 2026 (W12) | Ingestion — PDF parsed, text visible in UI | Yes |
| v0.4 | Nov 21, 2026 (W16) | **Thin MVP** — pre-loaded PDF + chat, no auth | **Yes (early warning gate)** |
| v0.5 | Dec 19, 2026 (W20) | **Full MVP** — RAG with citations, end-to-end student flow + Tier 1 Freeze | **Yes (the MVP demo)** |
| v0.6 | Jan 30, 2027 (W26) | Knowledge layer — KG + first quiz | Yes |
| v0.7 | Feb 27, 2027 (W30) | Cognition — quiz + mastery + KG end-to-end + Tier 2 Freeze | Yes |
| v0.8 | Mar 27, 2027 (W34) | Adaptation — system recommends next concept | Yes |
| v0.9 | Apr 24, 2027 (W38) | Feature-complete + **Feature Freeze** | Yes |
| v1.0-rc | May 22, 2027 (W42) | Hardened + **Code Freeze** | Yes |
| v1.0 | Jun 5, 2027 (W44) | **Graduation** — production deployment + presentation | **Yes (final)** |

### Integration Milestones

Integration is where most projects die. The following are explicit moments where two or more components must work together for the first time. Each follows the integration protocol: T-3 days both sides declare interface frozen; T-2 days stubs removed; T-1 day both sides test on staging; T-day Friday demo; T+1 day post-mortem on any failures.

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

### Testing Milestones

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

### Documentation Milestones

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

### Graduation Preparation Milestones (22-Week Runway)

Graduation prep is not a 1-week activity at the end. It is a **22-week runway** starting in W20 (the same week as Tier 1 Freeze). This long runway ensures the presentation is rehearsed, the demo data is curated, and there are no surprises in the final week.

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

### Demo Data Track (First-Class Deliverable)

Demo data is a **first-class deliverable track** running from W20 to W42. It is not an afterthought; it is the substrate on which every demo and the final presentation depend.

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

---

## Deliverables

### Code Deliverables

1. **Repository** (`github.com/openlearn-ai/openlearn`) with:
   - `frontend/` — Next.js 16 application
   - `backend/` — FastAPI application
   - `infra/` — Docker Compose, Terraform, deployment scripts
   - `docs/` — Docusaurus site source + ADRs + runbooks
   - `scripts/` — Setup, seed, and ops scripts
   - `MASTER_ROADMAP.md` (this document)
   - `README.md`, `CONTRIBUTING.md`, `CODEOWNERS`, `LICENSE`
2. **15+ ADRs** covering stack, repo structure, API versioning, env management, LLM gateway, OCR choice, embedding choice, chunking strategy, vector DB, RAG prompt design, KG schema, cognitive model, adaptive engine, retrieval strategy, security model.
3. **Test suite** with ≥ 60% coverage on critical paths; ~500+ unit tests, ~50 integration tests, ~10 E2E tests.
4. **CI/CD pipelines** for lint, test, build, deploy on every PR and tag.
5. **Runbooks** for deploy, rollback, DR, on-call.

### Deployed Deliverables

1. **Production deployment** at a public URL with TLS.
2. **Staging deployment** mirroring prod (used for demos and dry-runs).
3. **Monitoring stack**: Grafana dashboards, Prometheus metrics, Loki logs, Sentry errors.
4. **Demo data set**: 3 courses × 5–10 PDFs each, 5 seeded student accounts, 20 quizzes, 5 known-good RAG questions.

### Documentation Deliverables

1. **Docusaurus site** at a public docs URL.
2. **API reference** auto-generated from OpenAPI spec.
3. **Architecture diagram** (single-page, updated to reflect actual code).
4. **User-facing docs**: instructor quickstart, student quickstart.
5. **Engineering docs**: OCR design doc, chunking design doc, RAG design doc + eval methodology, KG design doc, cognitive model design doc, adaptive engine design doc.
6. **Runbooks**: deploy, rollback, DR, on-call.
7. **Tech debt register**: `docs/tech-debt.md` with accepted debt and payoff triggers.
8. **Final README** with setup instructions, architecture overview, and links to all docs.

### Presentation Deliverables

1. **Slide deck** (v2 by W43).
2. **Demo script** (v1 by W34, finalized by W38).
3. **Fallback demo video** (recorded W41, in case live demo fails).
4. **Final 30-minute presentation** delivered at graduation.

---

## Critical Path

The critical path is the longest chain of dependent tasks that determines the minimum project duration. Any slip on the critical path slips the graduation date.

### Critical Path Chain

```
Stack lock (W1)
  → OCR pipeline (W9–W10)
    → Chunking (W11)
      → Embeddings (W12)
        → Vector DB (W13)
          → RAG (W14–W15)
            → v0.4 Thin MVP (W16)  [early warning gate]
              → Full student flow (W17–W18)
                → Tier 1 Architecture Freeze (W20)  [gate]
                  → Concept extraction (W23)
                    → KG (W24)
                      → Cognitive model spike (W25–W27)  [research]
                        → Cognitive model impl (W28)
                          → Tier 2 Architecture Freeze (W30)  [gate]
                            → Adaptive spike (W29–W31)  [research, parallel]
                              → Adaptive engine (W31–W33)
                                → Feature Freeze (W38)  [gate]
                                  → Hardening (W39–W41)
                                    → Code Freeze (W42)  [gate]
                                      → Prod deploy (W43)
                                        → Graduation (W44)
```

### Critical Path Slack Analysis

| Segment | Planned Duration | Allowable Slip Before Graduation Slips | Trigger if Slip Exceeds |
|---|---|---|---|
| Stack lock → Tier 1 Freeze (W1–W20) | 19 weeks | 1 week | Switch Qdrant to pgvector (F-1); switch BGE-M3 to OpenAI embeddings (F-3); descope multi-doc RAG |
| Tier 1 Freeze → Tier 2 Freeze (W20–W30) | 10 weeks | **2 weeks** (improved by research spikes) | Descope KG depth; defer Tier 2 by 2 weeks; trigger PB-05 |
| Tier 2 Freeze → Feature Freeze (W30–W38) | 8 weeks | 1 week | Descope recommendation engine v2 features; trigger PB-03 |
| Feature Freeze → Code Freeze (W38–W42) | 4 weeks | 0 weeks (hard) | Cut hardening scope to must-haves |
| Code Freeze → Graduation (W42–W44) | 2 weeks | 0 weeks (hard) | Use recorded demo fallback |

**Total critical path slack: ~4 weeks.**

### Critical Path Drivers

- **OCR pipeline** — every downstream AI component depends on having text. If OCR fails on real PDFs, everything stalls. Mitigated by PB-01 and F-6.
- **Embeddings + vector DB** — RAG depends on working retrieval. No retrieval, no RAG. Mitigated by F-1, F-3.
- **Architecture Freeze (Tier 1 + Tier 2)** — without frozen interfaces, integration work in P3/P4 thrashes.
- **Cognitive model** — adaptive engine depends on mastery estimates. No mastery, no adaptation. Mitigated by research spike in W25–W27.
- **Adaptive engine** — the latest-starting critical component. Most exposed to upstream slips. Mitigated by research spike in W29–W31 and PB-03.

### Near-Critical Path (Parallel Chains)

These are not on the critical path but become critical if they slip badly:

- **Auth + course CRUD** (W5–W8) — must be done by W8 or P2 starts late.
- **Chat UI + citation rendering** (W15–W16) — must be done by W17 or v0.5 demo fails.
- **Quiz UI** (W26) — must be done by W27 or cognitive model has no input data.
- **Analytics dashboard** (W34–W35) — must be done by W36 or Feature Freeze slips.
- **Documentation** (continuous) — must be ≥ 80% by W41 or Code Freeze slips.

---

## Dependency Map

### Dependency Graph

```
                       ┌──────────────┐
                       │   Auth + RBAC │
                       └──────┬───────┘
                              │
                       ┌──────▼───────┐
                       │ Course CRUD  │
                       └──────┬───────┘
                              │
                       ┌──────▼───────┐
                       │  File Upload │
                       └──────┬───────┘
                              │
                       ┌──────▼───────┐
                       │ OCR Pipeline │ ──────┐
                       └──────┬───────┘       │
                              │               │
                       ┌──────▼───────┐       │
                       │  Chunking    │       │
                       └──────┬───────┘       │
                              │               │
                ┌─────────────┼─────────────┐ │
                ▼             ▼             ▼ │
         ┌──────────┐  ┌──────────┐  ┌────────────┐
         │Embeddings│  │ Concepts │  │  Quizzes   │
         └─────┬────┘  └─────┬────┘  └─────┬──────┘
               │             │             │
         ┌─────▼────┐  ┌─────▼────┐        │
         │ Vector DB│  │   KG     │        │
         └─────┬────┘  └─────┬────┘        │
               │             │             │
               └──────┬──────┘             │
                      ▼                    │
                ┌──────────┐               │
                │   RAG    │◄──────────────┘
                └─────┬────┘
                      │
                ┌─────▼─────┐
                │  Student  │
                │   Model   │
                └─────┬─────┘
                      │
                ┌─────▼─────┐
                │ Adaptive  │
                │  Engine   │
                └─────┬─────┘
                      │
                ┌─────▼─────┐
                │Recommend- │
                │  ations   │
                └───────────┘
```

### Dependency Matrix

| Module ↓ depends on → | Auth | Course | Upload | OCR | Chunking | Embed | VectorDB | KG | RAG | Quiz | StudentModel | Adaptive |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Course CRUD | ✓ | | | | | | | | | | | |
| File Upload | | ✓ | | | | | | | | | | |
| OCR Pipeline | | | ✓ | | | | | | | | | |
| Chunking | | | | ✓ | | | | | | | | |
| Embeddings | | | | | ✓ | | | | | | | |
| Vector DB | | | | | | ✓ | | | | | | |
| Knowledge Graph | | | | | ✓ | | | | | | | |
| RAG | | | | | | | ✓ | ✓ | | | | |
| Quiz generation | | | | | ✓ | | | ✓ | | | | |
| Student Model | | | | | | | | ✓ | | ✓ | | |
| Adaptive Engine | | | | | | | | ✓ | | ✓ | ✓ | |
| Recommendations | | | | | | | | ✓ | | ✓ | ✓ | ✓ |
| Analytics dashboard | | ✓ | | | | | | ✓ | | ✓ | ✓ | ✓ |

### Frozen Interface Contracts

The following contracts are frozen at their respective freeze dates. Post-freeze changes require a new ADR, a migration plan, TPM approval, and at least 2 pod leads' review.

**Frozen at W8:** Auth token format (JWT claims, refresh flow).

**Frozen at Tier 1 Architecture Freeze (W20):**
1. OCR output schema — JSON structure of extracted text + layout.
2. Chunk schema — fields, metadata, IDs.
3. Embedding I/O — input text, output vector dim, model ID.
4. Vector DB query API — top-k search, filters, payload.
5. RAG request/response — query, filters, response with citations.

**Frozen at Tier 2 Architecture Freeze (W30):**
6. KG concept/relation schema — node types, edge types, provenance.
7. Quiz schema — question types, metadata, scoring.
8. Student mastery schema — per (student, concept) record.
9. Adaptive engine I/O — input: student state; output: next action.

---

## Risk Register

The risk register is the single source of truth for what can go wrong. It is reviewed at every monthly milestone review and updated biweekly. Every risk has an owner, a likelihood, an impact, a mitigation, and a trigger.

**Likelihood scale:** 1 (Very Low, <10%) / 2 (Low, 10–30%) / 3 (Medium, 30–60%) / 4 (High, 60–85%) / 5 (Very High, >85%)
**Impact scale:** 1 (Trivial) / 2 (Minor) / 3 (Moderate) / 4 (Major) / 5 (Severe — graduation at risk)
**Risk score = Likelihood × Impact.** Score ≥ 12 = red; 6–11 = yellow; ≤ 5 = green.

### Technical Risks

| ID | Risk | L | I | Score | Owner | Mitigation | Trigger |
|---|---|---|---|---|---|---|---|
| R-01 | OCR quality too low on real-world PDFs (scanned, rotated, mixed-language) | 4 | 4 | **16 🔴** | B-Lead | Spike in W5; PaddleOCR + Document AI fallback; golden PDF set; A/B test on 20 PDFs by W10 | < 90% success on 20-PDF set |
| R-02 | RAG quality unacceptable (hallucinations, wrong citations) | 4 | 4 | **16 🔴** | B-Lead | Hybrid retrieval + reranker; eval harness from W17; prompt iteration; guardrails | Faithfulness < 0.7 on golden set |
| R-03 | Adaptive engine algorithm fails to converge or behaves erratically | 3 | 4 | **12 🔴** | B-Lead | Research spike in W29–W31; simulated eval harness; simple policy first (rule-based), then ML | Simulated trajectories show no learning |
| R-04 | Knowledge Graph construction produces noisy/incorrect relations | 3 | 3 | 9 🟡 | B-Lead | LLM-assisted extraction with human-in-loop sampling; provenance tracking; KG sanity tests (TM-7) | > 30% relations flagged bad on sample |
| R-05 | Vector DB (Qdrant) ops too heavy for Pod D to maintain | 3 | 3 | 9 🟡 | D-Lead | Cross-train Pod B engineer; fallback F-1 (pgvector); monitoring from W13 | Qdrant down > 1h unresolved |
| R-06 | LLM API cost overruns | 3 | 3 | 9 🟡 | D-Lead | LiteLLM proxy with cost tracking; per-user quota; cache common queries; fallback F-4 | Monthly cost > $300 |
| R-07 | LLM API provider changes terms / deprecates model | 3 | 4 | **12 🔴** | B-Lead | LiteLLM gateway abstracts provider; ≥ 2 providers configured; ADR for fallback model | Provider announces deprecation |
| R-08 | Embedding model dim mismatch after Architecture Freeze | 2 | 4 | 8 🟡 | B-Lead | Freeze model choice at W12; ADR; versioned embeddings with model_id field | — |
| R-09 | Database performance collapses under load | 3 | 3 | 9 🟡 | A-Lead | Indexes from day 1; load test at W39; connection pooling; read replicas if needed | P95 > 5s in load test |
| R-10 | Frontend bundle too large; first load > 5s | 3 | 2 | 6 🟡 | C-Lead | Code splitting; lazy loading; bundle analysis in CI; Next.js SSR | Lighthouse perf < 70 |
| R-11 | Neo4j ops too heavy; team can't maintain | 3 | 3 | 9 🟡 | D-Lead | Fallback F-2 (JSONB in Postgres); ADR documents both paths | Neo4j down > 2h |
| R-12 | Pod D bus factor (mitigated structurally — Pod D has 2 people) | 2 | 4 | 8 🟡 | TPM | 2-person Pod D from day one; cross-training plan; documented runbooks; PB-04 if both unavailable | Pod D lead unavailable > 1 week |
| R-13 | Cognitive model produces meaningless mastery scores (cold start, sparse data) | 3 | 3 | 9 🟡 | B-Lead | Simple mastery v1 (rolling average); research spike W25–W27; add IRT in v0.8 only if data supports; confidence intervals | Mastery values don't correlate with quiz performance |
| R-14 | Multi-document RAG retrieval returns cross-course noise | 3 | 2 | 6 🟡 | B-Lead | Course-level metadata filter; reranker; A/B test (single-course only in v1.0 per OOS-7) | — |
| R-15 | Production deployment fails on graduation day | 2 | 5 | **10 🟡** | D-Lead | Deploy W43 (not W44); smoke tests; fallback to staging URL; recorded demo video (GPM-9) | Prod down at T-1h |

### Schedule Risks

| ID | Risk | L | I | Score | Owner | Mitigation | Trigger |
|---|---|---|---|---|---|---|---|
| R-16 | Exam crunch (late Jan) collapses capacity more than expected | 4 | 4 | **16 🔴** | TPM | Plan P3 with 50% capacity buffer; defer KG depth to Feb; explicit "exam mode" comms; PB-05 | Pod B throughput < 30% in W25–27 |
| R-17 | Exam crunch 2 (late Apr–early May) eats into hardening | 3 | 4 | **12 🔴** | TPM | Front-load hardening tasks into W37; treat W39–40 as bonus | P5 slips > 1 week |
| R-18 | v0.5 (MVP) slips past W20 | 3 | 5 | **15 🔴** | TPM | v0.4 thin MVP at W16 is the early warning gate; Tier 1 Freeze can be signed even if v0.5 is "demoable but rough"; PB-06 | v0.4 slips past W16 |
| R-19 | Tier 1 Architecture Freeze slips past W20 | 2 | 5 | **10 🟡** | TPM | Force a "soft freeze" in W19; full freeze in W20 even if some ADRs are still "Proposed" | ADRs 1–15 not all merged by W18 |
| R-20 | Feature Freeze slips past W38 | 3 | 4 | **12 🔴** | TPM | Hard rule: no new features after W38 even if v0.9 is incomplete; demos show what's done | v0.8 not done by W34 |

### Team Risks

| ID | Risk | L | I | Score | Owner | Mitigation | Trigger |
|---|---|---|---|---|---|---|---|
| R-21 | A key team member drops out or is unavailable for > 4 weeks | 3 | 4 | **12 🔴** | TPM | Cross-training; pod redundancy (Pod D has 2 people); documented runbooks; firefighter role; advisor escalation | Any member gone > 2 weeks |
| R-22 | Pod B (AI/ML) overloaded — too much critical-path work for 3 people | 3 | 4 | **12 🔴** | TPM | Pod B owns 7 components (not 9); vector DB ops moved to Pod A; eval harness moved to Pod D; firefighter floats to Pod B in P2/P3; pair-program | Pod B slips 2 sprints in a row |
| R-23 | Skill gap: junior members can't contribute to AI work | 3 | 3 | 9 🟡 | B-Lead | Pair-programming; spike-first learning; assign junior to data curation / eval harness first | — |
| R-24 | Burnout during P5 final push | 3 | 3 | 9 🟡 | TPM | Cap hours at 30/wk in P5; mandatory 1 day off per week; rotate on-call | Member reports burnout or withdraws |
| R-25 | Team conflict / communication breakdown | 2 | 4 | 8 🟡 | TPM | Biweekly retros; explicit norms doc; TPM mediation; advisor escalation | Retro action items not progressing |
| R-26 | Advisor expectations misaligned with delivery reality | 3 | 3 | 9 🟡 | TPM | Monthly advisor demo; written status reports; explicit descope comms | Advisor surprised at monthly review |

### External Risks

| ID | Risk | L | I | Score | Owner | Mitigation | Trigger |
|---|---|---|---|---|---|---|---|
| R-27 | Cloud provider outage / billing issue | 2 | 4 | 8 🟡 | D-Lead | Multi-AZ; backups; budget alerts; Hetzner fallback | Provider outage > 4h |
| R-28 | LLM API rate limits during load test or demo | 3 | 3 | 9 🟡 | B-Lead | Quota increase request; caching; multiple API keys; fallback model | Rate limit hit in load test |
| R-29 | Third-party dependency (LangChain, LiteLLM, etc.) breaking change | 3 | 3 | 9 🟡 | B-Lead | Pin versions; integration tests; ADR for swap-out path | Breaking change in major version |
| R-30 | Graduation committee changes requirements mid-project | 2 | 4 | 8 🟡 | TPM | Monthly advisor check-ins; written scope doc signed at start | Committee announces new requirement |
| R-31 | Data privacy / regulatory issue (student data) | 2 | 4 | 8 🟡 | D-Lead | Data minimization; encryption at rest; PII handling ADR; privacy doc | — |
| R-32 | Open-source license conflict (e.g., AGPL component in commercial path) | 2 | 3 | 6 🟡 | D-Lead | License scan in CI; ADR for licensing strategy | Scan flags a component |

### Risk Heatmap

```
                    Impact
            1     2     3     4     5
         ┌─────┬─────┬─────┬─────┬─────┐
    5    │     │     │     │ R15 │ R18 │
         ├─────┼─────┼─────┼─────┼─────┤
    4    │     │ R10 │ R08 │ R01 │ R16 │
    L    │     │     │ R21 │ R02 │ R20 │
    i    │     │     │     │ R03 │ R22 │
    k    │     │     │     │ R07 │     │
    e   ├─────┼─────┼─────┼─────┼─────┤
    l   │     │ R32 │ R04 │ R05 │ R17 │
    i   │     │     │ R09 │ R06 │ R19 │
    h   │     │     │ R11 │ R12 │     │
    o   │     │     │ R13 │ R26 │     │
    o   │     │     │ R23 │ R27 │     │
    d   │     │     │ R28 │ R30 │     │
         ├─────┼─────┼─────┼─────┼─────┤
    1    │     │     │ R25 │ R29 │ R31 │
         └─────┴─────┴─────┴─────┴─────┘
```

### Top Red Risks (Score ≥ 12)

These 9 risks collectively determine whether the project ships on time. Every one of them has a mitigation that starts in P0 or P1 — *before* the risk materializes:

- **R-01** (OCR quality, 16) — PB-01
- **R-02** (RAG quality, 16) — PB-02
- **R-16** (exam crunch, 16) — PB-05
- **R-18** (MVP slip, 15) — PB-06
- **R-03** (adaptive engine, 12) — PB-03
- **R-07** (LLM provider change, 12) — structural mitigation via LiteLLM gateway
- **R-12** (Pod D bus factor, reduced from 16 to 8) — structural mitigation via 2-person Pod D
- **R-17** (exam crunch 2, 12) — front-loaded hardening
- **R-20** (Feature Freeze slip, 12) — hard rule: no new features after W38
- **R-21** (member dropout, 12) — cross-training + firefighter role
- **R-22** (Pod B overload, 12) — Pod B restructured to 7 components; firefighter floats to Pod B

---

## Risk Mitigation Strategy

Risk mitigation operates at four layers, in increasing order of escalation:

### Layer 1 — Structural Mitigations (Built into the Plan)

These are design choices that prevent risks from materializing in the first place:

- **2-person Pod D** eliminates the bus-factor risk (R-12 reduced from 16 to 8).
- **Pod B restructured to 7 components** (vector DB ops moved to Pod A, eval harness moved to Pod D) reduces overload (R-22).
- **LiteLLM gateway** abstracts LLM providers, so a provider change (R-07) is a config swap, not a rewrite.
- **v0.4 thin MVP at W16** is the early warning gate for the AI pipeline (R-18). If it doesn't ship, the team knows 6 weeks before v0.5.
- **Research spikes on cognitive model (W25–W27) and adaptive engine (W29–W31)** reduce research risk before commitment (R-03, R-13).
- **Scoped component fallbacks F-1 through F-7** let the team swap a failing component without rewriting the stack (R-01, R-05, R-06, R-07, R-11).
- **Cross-training plan** ensures at least 3 people can do basic DevOps by W38 (R-12, R-21).
- **Distributed buffer** (4 weeks of critical-path slack + per-sprint 10% slack + exam-crunch buffer) absorbs slips without cascading (R-16, R-17, R-18).

### Layer 2 — Contingency Playbooks (Top 6 Red Risks)

Each playbook specifies the trigger metric, the decision owner, the decision deadline, and 2–4 concrete branches with their cost. The playbook is invoked when the trigger metric is objectively met.

#### PB-01 — OCR Quality Too Low (R-01)

| Field | Value |
|---|---|
| **Trigger metric** | < 90% success rate on the 20-PDF golden set at W10 demo |
| **Decision owner** | B-Lead |
| **Decision deadline** | End of W11 (1 week after trigger) |
| **Branches** | (A) Invoke fallback F-6 (PaddleOCR → Google Document AI) — 3 days, increases cost. (B) Add a 2nd OCR pass (Tesseract as fallback for failures) — 1 week, no cost. (C) Restrict input to "high-quality PDFs only" (no scanned docs) — 0 days, reduces scope. |
| **Default if no decision** | Branch B (2nd OCR pass). |

#### PB-02 — RAG Quality Unacceptable (R-02)

| Field | Value |
|---|---|
| **Trigger metric** | Faithfulness < 0.7 OR relevance < 0.7 on the 50-Q golden set at W16 |
| **Decision owner** | B-Lead |
| **Decision deadline** | End of W17 (1 week after trigger) |
| **Branches** | (A) Increase reranker weight; add cross-encoder reranking on top-50 — 3 days. (B) Switch LLM to a stronger model (GPT-4o or Claude) for RAG only — 1 day, +cost. (C) Restrict RAG to single-document queries (no multi-doc) — 0 days, reduces scope. (D) Add prompt engineering: "If you don't know, say 'I don't know'" — 1 day. |
| **Default if no decision** | Branch A + D (combined). |

#### PB-03 — Adaptive Engine Fails to Converge (R-03)

| Field | Value |
|---|---|
| **Trigger metric** | Simulated trajectories in W31 spike show no learning improvement vs. random policy |
| **Decision owner** | B-Lead |
| **Decision deadline** | End of W31 (immediate, since adaptive engine is on critical path) |
| **Branches** | (A) Invoke fallback F-7 (rule-based adaptive: if mastery < 0.4, recommend easiest concept; if > 0.7, recommend hardest) — 2 days. (B) Simplify the policy: pick the concept with lowest mastery that has all prereqs met — 1 day. (C) Defer adaptive engine to v1.1; ship v1.0 with non-adaptive recommendations — 0 days, biggest scope cut. |
| **Default if no decision** | Branch B (simplest meaningful policy). |

#### PB-04 — Pod D Bus Factor (R-12)

| Field | Value |
|---|---|
| **Trigger metric** | Pod D lead unavailable > 3 days |
| **Decision owner** | TPM |
| **Decision deadline** | 24h after trigger |
| **Branches** | (A) Pod D engineer (2nd person) takes over as acting lead — 0 days. (B) If both Pod D members unavailable, invoke firefighter role + pull 1 Pod A engineer into DevOps — 1 day. (C) If critical infra is at risk, freeze deploys to prod; continue staging-only — 0 days. |
| **Default if no decision** | Branch A. |

#### PB-05 — Exam Crunch Collapses Capacity (R-16)

| Field | Value |
|---|---|
| **Trigger metric** | Pod B throughput < 30% of plan for 2 consecutive weeks in W25–W27 |
| **Decision owner** | TPM |
| **Decision deadline** | End of W27 |
| **Branches** | (A) Pause KG work; focus Pod B on cognitive model only — 1 day to re-plan. (B) Defer Tier 2 Architecture Freeze by 2 weeks (W30 → W32); accept compression in P4. (C) Descope KG to "list of concepts, no relations" — 0 days, reduces scope. |
| **Default if no decision** | Branch A. |

#### PB-06 — MVP Slips Past W20 (R-18)

| Field | Value |
|---|---|
| **Trigger metric** | v0.4 Thin MVP not demoable at W16 |
| **Decision owner** | TPM |
| **Decision deadline** | End of W16 (immediate) |
| **Branches** | (A) v0.4 slips to W18; v0.5 slips to W22; Tier 1 Freeze slips to W22; P3 compressed by 2 weeks. (B) Invoke F-3 (OpenAI embeddings instead of self-hosted) to save Pod B time — 1 day. (C) Descope v0.5: ship auth + course CRUD + RAG, but defer multi-doc RAG to v0.6. |
| **Default if no decision** | Branch A + C (combined). |

### Layer 3 — Scoped Component Fallbacks

The seven scoped fallbacks (F-1 through F-7, defined in the Technology Stack section) are surgical component-level swaps invoked when a specific trigger is met. They are not a full stack rewrite — each one has a known cost (1 day to 1 week) and a clear owner.

### Layer 4 — Descope Protocol

When buffer consumption exceeds thresholds, the descope protocol triggers automatically — the TPM does not need permission.

**Trigger thresholds:**
- Per-phase buffer consumed > 50% with > 50% of phase remaining → Yellow.
- Per-phase buffer consumed > 75% with > 25% of phase remaining → Orange.
- Per-phase buffer consumed 100% → Red → descope immediately.

**Descope decision tree:**

```
Is the slipping work on the critical path?
├── Yes → Can we reduce its scope without breaking the chain?
│        ├── Yes → Reduce scope (e.g., KG stores 100 concepts instead of 1,000)
│        └── No  → Can we parallelize more aggressively?
│                 ├── Yes → Reallocate people; trigger cross-pod borrowing
│                 └── No  → INVOKE A SCOPED FALLBACK (F-1 to F-7) OR cut a downstream feature
└── No  → Defer the slipping work to the next phase, or cut it entirely
```

**Descope candidates (in priority order — easiest to cut first):**
1. Admin dashboard (replace with raw DB queries for the demo)
2. Notification system (skip; demo without)
3. Recommendation engine v2 features (keep v1 only)
4. Analytics dashboard advanced charts (keep basic ones)
5. KG visualization richness (keep simple list view)
6. Multi-document RAG (single-doc RAG still demonstrates the core value)
7. Accessibility polish (meet minimum, not WCAG AA)
8. Mobile responsiveness (desktop-only demo)
9. Performance optimization beyond P95 < 2s (accept P95 < 5s)
10. Multi-language support (English only)

**Hard never-to-cut items (graduation-critical):**
- Auth + user management
- Course management + file upload
- OCR + RAG (the MVP)
- At least a basic quiz + mastery loop
- At least one adaptive behavior (even if simple)
- Production deployment
- Documentation (ADRs + README + runbook)
- The graduation presentation itself

### Layer 5 — Freeze Escalation Ladder

If a freeze is at risk of being missed:

| Risk Level | Trigger | Action |
|---|---|---|
| Green | On track, no concerns | Continue |
| Yellow | ≤ 1 week slip predicted | TPM reallocates resources; descopes 1 non-critical item |
| Orange | 1–2 week slip predicted | Descope protocol triggered; advisor informed |
| Red | > 2 week slip predicted | Emergency replan; invoke scoped fallbacks; advisor + committee informed |

---

## Quality Gates

Five quality gates anchor the schedule. Each gate is a hard pass/fail — passing requires explicit sign-off from all pod leads and the TPM. After a gate, the scope of what can change is dramatically narrowed.

### Gate 1 — v0.4 Thin MVP (W16)

The early warning gate. If v0.4 does not ship at W16, PB-06 triggers and the entire P2/P3 timeline is replanned.

**Sign-off criteria:**
1. A specific PDF is pre-loaded (chosen by Pod B in W3).
2. OCR has run on it; text + chunks are in the DB.
3. Embeddings are in the vector DB.
4. A simple chat UI (single page, no auth) accepts a question.
5. The system returns an answer with at least 2 citations.
6. Deployed to a public URL.
7. The demo survives 5 questions without crashing.

### Gate 2 — v0.5 Full MVP + Tier 1 Architecture Freeze (W20)

The most important gate in the entire roadmap. If we miss it, every subsequent date slips.

**Sign-off criteria:**
1. A student can register, log in, and be enrolled in a course.
2. An instructor can create a course and upload a PDF (≤ 50 MB).
3. The PDF is processed by OCR within 5 minutes and the extracted text is visible in the UI.
4. The extracted text is chunked, embedded, and stored in the vector DB.
5. The student can ask a natural-language question about the PDF and get an answer with at least 2 source citations pointing to specific chunks.
6. The system is deployed to a public URL (not localhost).
7. CI passes on `main` with ≥ 40% line coverage on critical paths.
8. The system survives a 10-minute demo without crashing.
9. An ADR exists for every major component (ADRs 1–15 merged and reviewed).
10. All 10 Tier 1 interface contracts documented with examples.
11. Architecture diagram v1 published.
12. All pod leads + TPM sign a single-page "Tier 1 Architecture Freeze" doc.

### Gate 3 — v0.7 + Tier 2 Architecture Freeze (W30)

**Sign-off criteria:**
1. v0.7 demoed: quiz + mastery + KG end-to-end.
2. Cognitive model ADR (ADR-017) merged and reviewed.
3. Tier 2 interface contracts (KG, quiz, mastery, adaptive I/O) documented with examples.
4. KG populated with ≥ 200 concepts; KG sanity tests pass (TM-7).
5. Quiz + mastery E2E test green (TM-8).
6. All pod leads + TPM sign a single-page "Tier 2 Architecture Freeze" doc.

### Gate 4 — v0.9 + Feature Freeze (W38)

**Sign-off criteria:**
1. v0.9 demoed and accepted.
2. All P1 bugs from bug bash #1 closed or waived.
3. Coverage ≥ 60% on critical paths (TM-11).
4. At least 3 people cross-trained on DevOps tasks.
5. Graduation presentation deck v1 reviewed by advisor (GPM-6).
6. Demo data curated and validated (DDM-5).
7. All pod leads + TPM sign a single-page "Feature Freeze" doc.

### Gate 5 — v1.0-rc + Code Freeze (W42)

**Sign-off criteria:**
1. v1.0-rc tagged and deployed to staging.
2. Bug bash #2 complete; ≤ 3 P1s open (TM-14).
3. Security review complete; no critical/high vulns (TM-13).
4. Performance pass complete; P95 < 2s on RAG (TM-12).
5. Runbooks complete (DM-14).
6. Backup + DR drill complete.
7. Final architecture diagram + ADR index published (DM-15).
8. README polished + demo recording (DM-16).
9. Demo data frozen (DDM-8).
10. All pod leads + TPM sign a single-page "Code Freeze" doc.

---

## Testing Strategy

Testing is not a phase; it is continuous. The test pyramid governs the distribution of tests:

```
                  /\
                 /  \        E2E (Playwright) — ~10 tests, slow, fragile
                /----\
               /      \      Integration (API ↔ DB ↔ jobs) — ~50 tests
              /--------\
             /          \    Unit (pytest + Vitest) — ~500+ tests
            /____________\
```

- **Unit tests** run in < 60s; gate every PR.
- **Integration tests** run in < 5 min; gate every PR to `main`.
- **E2E tests** run nightly on staging and on every release tag.

### Test Pyramid Details

**Unit tests (Pod A + B + C):**
- Backend: pytest with fixtures; ≥ 80% coverage on auth, course CRUD, ingestion API.
- Frontend: Vitest with React Testing Library; ≥ 70% coverage on critical UI components.
- AI: pytest on chunking, prompt assembly, eval harness.
- Run time: < 60 seconds total.

**Integration tests (Pod A + B + D):**
- API ↔ DB: every endpoint tested against a real Postgres + Qdrant + Neo4j.
- Async jobs: OCR → chunking → embeddings pipeline tested end-to-end on sample PDFs.
- Run time: < 5 minutes total.

**E2E tests (Pod D + C):**
- Playwright tests for the student flow (register → enroll → upload → chat → quiz → mastery → recommendation).
- Run nightly on staging and on every release tag.
- Run time: < 15 minutes total.

### Test Data Strategy

- **Synthetic data** for unit tests (deterministic, fast).
- **Anonymized real data** for integration tests (10 sample PDFs curated by Pod B in W3).
- **Golden Q&A set** for RAG eval (50 questions with expected answers + acceptable sources).
- **Simulated student trajectories** for adaptation eval (10 personas × 20 quizzes each).
- **Demo data set** (3 courses × 5–10 PDFs each, 5 seeded student accounts, 20 quizzes, 5 known-good RAG questions) — managed as a first-class deliverable track (DDM-1 through DDM-8).

### Coverage Targets

| Module | Coverage Target | Gate |
|---|---|---|
| Auth, course CRUD, ingestion API | ≥ 80% | W8 (TM-2) |
| Critical paths overall | ≥ 40% | W20 (TM-6) |
| Critical paths overall | ≥ 60% | W38 (TM-11, Feature Freeze gate) |

### Specialized Testing

- **RAG eval harness**: 50 Q&A pairs; faithfulness + relevance scores; runs in CI on every PR from W17 onward.
- **KG sanity tests**: schema validation; cycle detection; > 30% bad relations triggers R-04.
- **Adaptation eval harness**: simulated student trajectories; regression baseline; runs in CI from W33.
- **Load test**: 50 concurrent users; P95 < 2s on RAG; runs at W39 (TM-12).
- **Security review**: OWASP top 10; SAST (Semgrep); dependency scan; pen test; at W40 (TM-13).

---

## Documentation Strategy

Documentation is a **first-class deliverable** using a **docs-first workflow**: API contracts and design docs are written *before* implementation, then updated as code lands.

### Docs-First Workflow

For every new component:

1. **Before code:** Open a PR with a design doc (1–3 pages) describing the component, its interfaces, and its failure modes. Get review from at least 1 other pod lead.
2. **During code:** Update the doc as the implementation reveals constraints.
3. **After code:** The doc lives next to the code; CI checks that every module has a corresponding `README.md` or design doc.

### Rotating Docs Owner

A **rotating dedicated Docs Owner** role ensures documentation always has an owner:

- **Rotation:** 4 weeks per owner, drawn from pod leads (TPM, A-Lead, B-Lead, C-Lead, D-Lead) in round-robin.
- **Time commitment:** 30% of the owner's week during their rotation.
- **Responsibilities:**
  - Maintain the docs completeness dashboard (auto-generated from CI).
  - Run the weekly 5-minute docs review at Friday demo.
  - Triage doc-related PR comments.
  - Own the Docusaurus site.

### CI Documentation Gate

Every PR that adds a new endpoint, schema, ADR, or component **must** also add or update a doc file. The CI check uses a simple file-existence rule (e.g., `docs/api/<endpoint>.md` must exist if `app/api/<endpoint>.py` is added). PRs failing this check are blocked.

### ADR Template

Every Architecture Decision Record follows this template:

```markdown
# ADR-NNN: Title

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-MMM
**Date:** YYYY-MM-DD
**Authors:** name(s)

## Context
(Why is this decision needed? What constraints?)

## Decision
(What did we decide?)

## Alternatives considered
(What else did we consider? Why rejected?)

## Consequences
(Positive, negative, neutral)

## Open questions
(Things to revisit later)
```

### Documentation Deliverables Timeline

Documentation milestones (DM-1 through DM-16) are defined in the Milestones section. Key deliverables:

- **W2:** MVP definition (`docs/mvp.md`).
- **W4:** First 5 ADRs + team norms + contributing guide.
- **W8:** API reference v1 (auto-generated OpenAPI) + Docusaurus site live.
- **W11–W23:** OCR, chunking, RAG, KG design docs.
- **W27–W31:** Cognitive model + adaptive engine design docs.
- **W36:** User-facing quickstarts.
- **W39:** Runbooks (deploy, rollback, DR, on-call).
- **W41:** Final architecture diagram + ADR index.
- **W42:** README polish + demo recording.

### Tech Debt Register

Technical debt is **explicitly tracked**, not hidden. Every tech debt item is a GitHub issue tagged `tech-debt` with:
- **Type:** Code debt / design debt / architecture debt / test debt / doc debt.
- **Interest rate:** High (will block future work) / Medium (slows future work) / Low (cosmetic).
- **Principal:** Estimated hours to pay off.
- **Owner:** Pod lead responsible.

**Tech debt budget:** Every sprint, each pod allocates **10% of capacity** to tech debt payoff. This is non-negotiable. If a pod has no tech debt items, they pick up items from another pod or improve tests.

**Tech debt milestones:**
- W12: First tech debt sweep (pay down debt accumulated in P0–P1).
- W20: Pre-Tier 1-Freeze debt audit (pay down anything that would block P3).
- W30: Mid-project debt audit.
- W38: Feature Freeze debt audit — anything not paid down by now is documented as "accepted debt" with a payoff plan for post-graduation.
- W42: Final debt register published as `docs/tech-debt.md`.

**The "tech debt wall":** A physical (or virtual — Miro/FigJam) wall where the team posts tech debt items as they accrue. Visible to everyone. The wall is reviewed at every monthly milestone review. A wall with 30 sticky notes by W20 is a warning sign; a wall with 5 is healthy.

---

## CI/CD Strategy

### Pipeline Stages

Every PR triggers:

1. **Lint** (ruff for Python, ESLint + Prettier for TypeScript).
2. **Unit tests** (pytest + Vitest).
3. **Integration tests** (against a real Postgres + Qdrant + Neo4j in CI containers).
4. **Build** (Docker images for backend + frontend).
5. **Documentation check** (CI gate: every new endpoint/schema/ADR has a corresponding doc).
6. **License scan** (CI gate: no AGPL or conflicting licenses).
7. **Coverage report** (posted as PR comment; ≥ 60% on critical paths required for merge to `main`).

Merges to `main` additionally trigger:

8. **Deploy to staging** (automatic).
9. **E2E tests on staging** (nightly).
10. **Smoke tests** (after every deploy).

Tags (`v0.x.x`, `v1.0.0-rc`, `v1.0.0`) trigger:

11. **Deploy to production** (manual approval required).
12. **Smoke tests on production** (after deploy).

### Branch Protection Rules

- `main` requires:
  - 1 approving review (2 for changes to frozen interfaces).
  - All CI checks green.
  - Branch is up to date before merge.
  - No force pushes.
  - No direct commits (must go through PR).
- `release/*` branches (created at Code Freeze) require:
  - 2 approving reviews.
  - TPM + D-Lead approval for any merge after Code Freeze.

### Environments

| Environment | Purpose | Data | Refresh Cadence |
|---|---|---|---|
| `dev` (local) | Developer machines | Synthetic | On demand |
| `staging` | Demos, integration testing, E2E tests | Anonymized real + demo data | Auto-deploy on every `main` merge |
| `prod` | Live system | Real user data + demo data | Manual deploy on tag |

### Release Process

1. Code is merged to `main` via PR.
2. `main` auto-deploys to staging.
3. Smoke tests run on staging.
4. A release tag (`v0.x.x`) is cut.
5. Tag triggers a manual approval workflow.
6. Approved deploy to prod.
7. Smoke tests on prod.
8. If smoke tests fail: rollback to previous tag (automated).

---

## Git Workflow

### Branching Model (Trunk-Based with Short-Lived Feature Branches)

- **`main`**: Always deployable. Always green. The source of truth.
- **`feature/<short-description>`**: Short-lived (≤ 1 week) branches for individual features. Merged via PR.
- **`spike/<short-description>`**: Branches for research spikes. Can be force-pushed; merged or discarded.
- **`release/v<x.y.z>`**: Created at Code Freeze. Only critical fixes are cherry-picked to release branches after Code Freeze.
- **`hotfix/<short-description>`**: Branches off `main` for critical fixes after Code Freeze. Merged to both `main` and the active release branch.

### Commit Conventions

Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `perf`, `build`.

Examples:
- `feat(auth): add refresh token rotation`
- `fix(rag): handle empty retrieval results`
- `docs(adr): add ADR-016 KG schema`

### PR Rules

- Every PR has a description with: what changed, why, how to test, screenshots (for UI).
- Every PR is linked to a GitHub issue or sprint task.
- Every PR is reviewed by at least 1 person (2 for changes to frozen interfaces).
- PRs are squash-merged to keep `main` history clean.
- PRs that fail CI are not merged (no "I'll fix it in the next PR").
- PRs that touch documentation-requiring code (new endpoint, schema, ADR, component) must also touch the corresponding doc file or CI blocks.

### Code Review Checklist

Reviewers check for:
- [ ] Does the code do what the PR description says?
- [ ] Are there tests? Do they cover the new behavior?
- [ ] Is the code readable? Are names clear?
- [ ] Does this break any frozen interface? If yes, is there an ADR?
- [ ] Does this introduce tech debt? If yes, is it logged?
- [ ] Does this need a doc update? If yes, is the doc updated?
- [ ] Does this need a migration? If yes, is the migration reversible?

---

## Definition of Done

A task, sprint, or feature is "done" when **all** of the following are true:

### For a Single Task

1. Code is written and committed to a feature branch.
2. Unit tests are written and pass.
3. PR is opened with a clear description.
4. PR is reviewed and approved by ≥ 1 person (≥ 2 for frozen interface changes).
5. CI is green (lint, tests, docs check, license scan).
6. Code is merged to `main`.
7. Feature is demoable on staging at the next Friday demo.
8. Documentation is updated (if applicable).
9. Tech debt is logged (if any was introduced).

### For a Sprint

1. The sprint's exit criterion is met.
2. A demo was given on Friday (on staging, not localhost).
3. CI is green on `main` at end of sprint.
4. Risk register is reviewed and updated.
5. Sprint planning for next sprint is complete.
6. Retro action items (if retro week) are logged as GitHub issues with owners and due dates.

### For a Version Release (e.g., v0.5)

1. All sprint exit criteria since the last version are met.
2. The version's exit gate (defined in Quality Gates) is satisfied.
3. Tag is cut and pushed.
4. Release notes are written (`CHANGELOG.md`).
5. Demo is delivered to the team (and advisor, for major versions).
6. All pod leads + TPM sign off.

### For the Final Graduation Delivery (v1.0)

1. All Graduation Success criteria are met (see Success Criteria section).
2. All Engineering Success criteria are met.
3. v1.0 is deployed to production at a public URL.
4. Demo data is loaded and validated.
5. Dry-run #3 (dress rehearsal) is completed.
6. All graduation artifacts (code, docs, presentation, demo video) are submitted.
7. The presentation is delivered.

---

## Architecture Freeze

Architecture Freeze is split into **two tiers** to reflect that the hardest architectural decisions span P2 and P3.

### Tier 1 Architecture Freeze (W20)

**What freezes:** Interface contracts 1–5 (OCR output schema, chunk schema, embedding I/O, vector DB query API, RAG request/response), plus the technology stack, the data model for the P2 components, the deployment topology, and the pod ownership boundaries.

**What does NOT freeze:** Implementation details inside a module, UI design, ML model choices (as long as the I/O contract holds), test strategies.

**Sign-off criteria:**
- All 15 ADRs merged and reviewed.
- All 5 Tier 1 interface contracts documented with examples.
- v0.5 (MVP) shipped and demoed.
- Architecture diagram v1 published.
- All pod leads + TPM sign a single-page "Tier 1 Architecture Freeze" doc.

**Post-freeze change protocol:** Any change to a frozen interface requires:
1. A new ADR explaining why.
2. A migration plan (data, code, tests).
3. TPM approval.
4. At least 2 pod leads' review.

**Why this matters:** Without Tier 1 Freeze, P3 thrashes endlessly as Pod B "improves" the chunk schema and breaks Pod A's ingestion service. The freeze is the only thing that prevents this.

### Tier 2 Architecture Freeze (W30)

**What freezes:** Interface contracts 6–9 (KG concept/relation schema, quiz schema, student mastery schema, adaptive engine I/O).

**What does NOT freeze:** Implementation details inside KG, quiz, cognitive model, or adaptive engine. ML model choices (as long as the I/O contract holds).

**Sign-off criteria:**
- v0.7 demoed (quiz + mastery + KG end-to-end).
- Cognitive model ADR (ADR-017) merged and reviewed.
- All 4 Tier 2 interface contracts documented with examples.
- KG populated with ≥ 200 concepts; KG sanity tests pass.
- Quiz + mastery E2E test green.
- All pod leads + TPM sign a single-page "Tier 2 Architecture Freeze" doc.

**Post-freeze change protocol:** Same as Tier 1.

**Why this matters:** The cognitive model and adaptive engine are the highest-research-risk components. Without Tier 2 Freeze, P4 thrashes as Pod B iterates on the mastery schema and breaks the adaptive engine's input. The freeze locks the interface so Pod B can iterate on the *implementation* without breaking the contract.

---

## Feature Freeze

**Date:** W38 (end of P4).

**What freezes:** No new features, no new APIs, no new UI screens. The product's feature set for graduation is locked.

**What does NOT freeze:** Bug fixes, performance improvements, documentation, test coverage, accessibility fixes, security fixes, demo polish.

**Sign-off criteria:**
1. v0.9 demoed and accepted.
2. All P1 bugs from bug bash #1 closed or waived.
3. Coverage ≥ 60% on critical paths (TM-11).
4. At least 3 people cross-trained on DevOps tasks.
5. Graduation presentation deck v1 reviewed by advisor (GPM-6).
6. Demo data curated and validated (DDM-5).
7. All pod leads + TPM sign a single-page "Feature Freeze" doc.

**Post-freeze change protocol:** Any new feature requires:
1. TPM + Tech Lead joint approval.
2. Explicit decision on what gets descoped to make room.
3. Update to the graduation demo script.

**Why this matters:** Without Feature Freeze, the team keeps adding "one more thing" until the day before graduation, and never spends time on hardening or demo polish. Both are required for a credible presentation.

---

## Code Freeze

**Date:** W42 (end of P5).

**What freezes:** No new code merges to `main` except critical fixes. No new dependencies. No schema migrations. No infra changes.

**What does NOT freeze:** Critical bug fixes (P0/P1) with TPM + D-Lead approval. Demo data fixes. Documentation typos.

**Sign-off criteria:**
1. v1.0-rc tagged and deployed to staging.
2. Bug bash #2 complete; ≤ 3 P1s open (TM-14).
3. Security review complete; no critical/high vulns (TM-13).
4. Performance pass complete; P95 < 2s on RAG (TM-12).
5. Runbooks complete (DM-14).
6. Backup + DR drill complete.
7. Final architecture diagram + ADR index published (DM-15).
8. README polished + demo recording (DM-16).
9. Demo data frozen (DDM-8).
10. All pod leads + TPM sign a single-page "Code Freeze" doc.

**Post-freeze change protocol:** Any merge to `main` requires:
1. TPM + D-Lead (DevOps) joint approval.
2. Classification as P0 or P1 (graduation-blocking).
3. Smoke tests re-run before and after merge.

**Why this matters:** The week before graduation is for rehearsing the demo, not for debugging a regression introduced by a "quick fix." Code Freeze gives the team a stable target.

---

## Buffer Periods

Buffer is **not** "extra time at the end." Buffer at the end gets eaten by procrastination and scope creep. Instead, buffer is **distributed** across the schedule at points of highest schedule risk.

### Buffer Allocation

| Buffer Type | Amount | Where It Lives | How It's Used |
|---|---|---|---|
| **Per-sprint slack** | 10% of every sprint | Inside each week | Absorbs underestimation |
| **Per-phase buffer** | 1 week per phase | End of each phase | Absorbs phase-level slips |
| **Critical-path buffer** | 2 weeks | Spread across P2 and P4 | Absorbs slips on the critical chain |
| **Exam-crunch buffer** | 2 weeks of explicit "do nothing" | W25–W27 (Jan exam) and W39 (Apr exam) | Lets team study without guilt |
| **Final buffer** | 1 week | W43 (before graduation) | Absorbs last-minute surprises |
| **Total buffer** | ~6.5 weeks (≈ 15% of 44 weeks) | Distributed | — |

### Buffer Consumption Rules

1. **Buffer is not feature time.** A pod cannot consume buffer to add a feature. Buffer is for absorbing slips, not for expanding scope.
2. **Buffer consumption is tracked.** The TPM maintains a "buffer burn-down" chart, updated weekly. If buffer burn rate exceeds plan, the descope protocol triggers.
3. **Critical-path buffer is reserved.** Only critical-path slips can consume the 2-week critical-path buffer. Non-critical work that slips must be descoped, not buffered.
4. **Exam-crunch buffer is non-negotiable.** The team is *expected* to do minimal work during exam weeks. This is not "slacking" — it is planned. The plan is sized to absorb this.

### Critical Path Slack Summary

| Segment | Slack |
|---|---|
| Stack lock → Tier 1 Freeze (W1–W20) | 1 week |
| Tier 1 Freeze → Tier 2 Freeze (W20–W30) | 2 weeks |
| Tier 2 Freeze → Feature Freeze (W30–W38) | 1 week |
| Feature Freeze → Code Freeze (W38–W42) | 0 weeks (hard) |
| Code Freeze → Graduation (W42–W44) | 0 weeks (hard) |
| **Total critical path slack** | **~4 weeks** |

---

## Graduation Preparation

Graduation prep is a **22-week runway** starting at W20 (the same week as Tier 1 Architecture Freeze). It runs in parallel with the engineering work and ensures the presentation is rehearsed, the demo data is curated, and there are no surprises in the final week.

### Graduation Prep Calendar

(See GPM-0 through GPM-12 in the Milestones section.)

### Demo Data Track

(See DDM-1 through DDM-8 in the Milestones section.)

### Presentation Structure

A 30-minute graduation presentation follows this arc:

1. **(2 min) Problem** — why adaptive learning matters.
2. **(3 min) Solution** — what OpenLearn AI does.
3. **(4 min) Architecture** — system diagram + key tech choices + ADR highlights.
4. **(8 min) Live demo** — student flow + instructor flow + analytics + adaptation.
5. **(5 min) AI depth** — RAG eval results; adaptation examples; what worked, what didn't.
6. **(4 min) Engineering process** — CI/CD, testing, freezes, retros, what we'd do differently.
7. **(2 min) Future** — post-graduation path as a product.
8. **(2 min) Q&A** buffer.

The "what worked, what didn't" section is **non-negotiable** — advisors respect honesty about failures more than claims of perfection.

### Demo Data Strategy

- Use a **fixed, curated dataset** for the demo (not random user uploads).
- Pre-load 3 courses with 5–10 PDFs each, all OCR'd and embedded.
- Pre-create 5 student accounts with realistic mastery states.
- Have a script of 5 questions to ask the RAG that are known to produce good answers.
- **Never** demo with production user data.
- **Fallback demo video** is recorded at W41 in case the live demo fails on graduation day.

### Dry-Run Schedule

| Dry-Run | Week | Audience | Purpose |
|---|---|---|---|
| #0 | W40 | Internal team only | First end-to-end rehearsal; identify gaps |
| #1 | W42 | Advisor | Collect advisor feedback; refine deck and script |
| #2 | W43 | Advisor (or full team) | Timing tuned; prod deployment stable |
| #3 | W44 | Full team (dress rehearsal) | Final rehearsal; submit artifacts |

---

## Version Roadmap (v0.1 → v1.0)

| Version | Target Date | Week | Theme | Key Capability | Gate |
|---|---|---|---|---|---|
| **v0.1** | Sep 12, 2026 | W6 | Skeleton | Repo, CI, dev env, empty Next.js + FastAPI, auth scaffold, hello-world deploy | — |
| **v0.2** | Sep 26, 2026 | W8 | Foundations | User mgmt, course CRUD, file upload, basic UI shell | — |
| **v0.3** | Oct 24, 2026 | W12 | Ingestion | OCR pipeline, chunking, raw text stored | — |
| **v0.4** | Nov 21, 2026 | W16 | **Thin MVP** | Pre-loaded PDF + chat UI; AI pipeline proven end-to-end | **Gate 1** |
| **v0.5** | Dec 19, 2026 | W20 | **Full MVP + Tier 1 Freeze** | RAG with citations, end-to-end student flow, Tier 1 Architecture Freeze | **Gate 2** |
| **v0.6** | Jan 30, 2027 | W26 | Knowledge layer | KG (concepts + relations), KG-backed retrieval boost | — |
| **v0.7** | Feb 27, 2027 | W30 | Cognition + Tier 2 Freeze | Cognitive model (rolling-average mastery), quiz generation v1, Tier 2 Architecture Freeze | **Gate 3** |
| **v0.8** | Mar 27, 2027 | W34 | Adaptation | Adaptive engine (next-best-concept, difficulty adjustment); IRT if data supports | — |
| **v0.9** | Apr 24, 2027 | W38 | Analytics + Feature Freeze | Learning analytics dashboard, admin dashboard (minimal), Feature Freeze | **Gate 4** |
| **v1.0-rc** | May 22, 2027 | W42 | Hardening + Code Freeze | Perf, security, bug bash, docs, DR drill, Code Freeze | **Gate 5** |
| **v1.0** | Jun 5, 2027 | W44 | **Graduation** | Production deployment, final docs, graduation presentation | **Final** |

### MVP Statement

> **A logged-in student can upload a PDF, the platform extracts its text and images, embeds the content, and the student can chat with the document and get cited answers — all deployed to a real URL.**

That is v0.5. Everything before it is scaffolding; everything after it is depth.

### Thin MVP Statement (v0.4)

> **A pre-loaded PDF is already in the system. A user (no auth required) asks a question in a text box and gets an answer with citations.**

The thin MVP proves the AI pipeline works end-to-end (OCR → chunking → embeddings → vector DB → RAG → chat UI) without depending on backend foundations being complete. If the thin MVP ships at W16, the team has 4 weeks to add auth + courses + uploads for v0.5. If the thin MVP does not ship at W16, the team knows the AI pipeline is the bottleneck — before investing further in backend work.

### Thin MVP Exit Criteria

1. A specific PDF is pre-loaded (chosen by Pod B in W3).
2. OCR has run on it; text + chunks are in the DB.
3. Embeddings are in the vector DB.
4. A simple chat UI (single page, no auth) accepts a question.
5. The system returns an answer with at least 2 citations.
6. Deployed to a public URL.
7. The demo survives 5 questions without crashing.

---

## Decision Review Process

### Decision Tiers

Decisions are classified into three tiers based on their blast radius. Each tier has a defined review path, approval authority, and maximum time-to-decision.

| Tier | Scope | Examples | Review Forum | Approvers | Max Time-to-Decision |
|---|---|---|---|---|---|
| **T1 — Tactical** | Single-pod, no cross-pod impact, reversible | Variable naming, minor refactor, test addition, bug fix approach | Pod-level sync | Pod lead | 2 business days |
| **T2 — Architectural** | Cross-pod impact, affects interfaces or data model, reversible only with effort | New API endpoint, schema change within a frozen contract boundary, library upgrade, fallback invocation | Weekly cross-pod sync | TPM + 2 pod leads | 1 week |
| **T3 — Strategic** | Project-wide impact, affects graduation delivery, not reversible without re-plan | Scope change, freeze exception, stack change, OOS list amendment, timeline slip | Monthly milestone review (emergency session if needed) | TPM + all pod leads + advisor | 2 weeks |

### Decision Workflow

Every T2 and T3 decision follows this workflow:

1. **Proposal.** The decision owner opens an ADR draft containing: context, decision, alternatives considered, consequences, open questions.
2. **Review.** The ADR is circulated to the relevant approvers. Reviewers must respond within the tier's max time-to-decision. Silence is not approval.
3. **Decision.** Approvers sign the ADR (GitHub PR review approval is sufficient). Dissent is recorded in the ADR; the TPM has tie-breaking authority for T2 and final escalation authority for T3.
4. **Recording.** The ADR is merged to `docs/adr/` with status `Accepted`. The decision is logged in the Revision History of this roadmap if it affects the plan.
5. **Implementation.** The decision owner executes; the ADR status moves to `Superseded` only if a later ADR replaces it.

### Decision Logs

- All T2 and T3 decisions are recorded as ADRs in `docs/adr/`.
- ADRs are numbered sequentially (`ADR-001`, `ADR-002`, …).
- A live ADR index is maintained at `docs/adr/README.md`.
- The TPM maintains a decision log in the project management tool with: ADR number, date, owner, status, summary.

### Escalation

If a decision cannot be resolved at its tier within the max time-to-decision:

- T1 → escalate to TPM.
- T2 → escalate to TPM + advisor.
- T3 → escalate to advisor + graduation committee.

Escalation is **expected, not exceptional**. A pod lead who escalates a stuck decision is acting correctly; a pod lead who lets a decision drift past its deadline without escalating is not.

### Anti-patterns

- Decisions made in private chat and not recorded in an ADR.
- "Let's just try it and see" without an ADR — this is a T2 decision disguised as a T1.
- ADRs written after the decision was already made and shipped (post-hoc rationalization).
- Silence treated as approval — silence is silence; explicit sign-off is required.

---

## Change Management Policy

### What Constitutes a Change

A change is any modification to:

1. This roadmap (any section).
2. A frozen interface contract (see Architecture Freeze, Feature Freeze, Code Freeze).
3. The signed Out-of-Scope list.
4. The Technology Stack decisions.
5. The team pod structure or ownership boundaries.
6. The sprint timeline or milestone dates.

Changes to implementation details inside a module — code, tests, internal data structures — are **not** changes under this policy. They follow standard PR review.

### Change Categories

| Category | Description | Approval Path | Documentation |
|---|---|---|---|
| **Minor** | Typo fix, clarification, internal cross-reference fix | TPM review | Direct edit; noted in Revision History |
| **Substantive** | New content consistent with existing plan (e.g., adding a risk to the register, adding a sprint deliverable that fits the existing theme) | TPM + relevant pod lead | Direct edit; new Revision History entry |
| **Major** | Change to dates, scope, pod structure, stack, or freeze terms | TPM + all pod leads | New ADR + Revision History entry |
| **Critical** | Change to graduation deliverables, OOS list, or freeze gates | TPM + all pod leads + advisor | New ADR + advisor sign-off + Revision History entry |

### Change Process

1. **Change request.** Opened as a GitHub issue tagged `roadmap-change`. The issue contains: what changes, why, what section, what category, what alternatives were considered.
2. **Triage.** TPM categorizes the change within 3 business days. Category may be upgraded (not downgraded) during triage.
3. **Review.** For Major and Critical changes, an ADR is drafted. Reviewers are the approvers defined for the category.
4. **Decision.** Approvals are recorded in the ADR. TPM updates this roadmap in a PR that references the ADR.
5. **Communication.** Approved changes are announced in the team channel and reviewed at the next weekly demo. All team members are expected to acknowledge the announcement within 48 hours.

### Freeze Exceptions

Changes to frozen items follow a stricter path:

- **Architecture Freeze exception:** Requires a new ADR + migration plan + TPM approval + 2 pod leads' review.
- **Feature Freeze exception:** Requires TPM + Tech Lead joint approval + explicit decision on what gets descoped to make room + update to graduation demo script.
- **Code Freeze exception:** Requires TPM + D-Lead joint approval + classification as P0 or P1 (graduation-blocking) + smoke tests re-run before and after merge.

Freeze exceptions are **rare and rationed**. The default answer to a freeze exception request is "no." The burden of proof is on the requester.

### Change Authority Matrix

| Change Type | TPM | Pod Leads | Advisor | Graduation Committee |
|---|---|---|---|---|
| Minor | Approves | Informed | — | — |
| Substantive | Approves | 1+ approves | Informed | — |
| Major | Approves | All approve | Informed | — |
| Critical | Approves | All approve | Approves | Informed |
| Freeze exception | Approves | 2+ approve (Arch) / joint (Feat / Code) | Informed | — |

### Anti-patterns

- Stealth edits to the roadmap without a Revision History entry.
- Verbal agreements that do not get written into an ADR.
- Approving a change without checking what else it affects (cascading impact).
- Skipping the change process "because it's urgent" — the process exists precisely for urgent cases.

---

## Roadmap Maintenance Rules

### Living Document Principle

This roadmap is a **living document**. It is not a one-time artifact. It is updated whenever reality diverges from plan, whenever a decision is made that affects the plan, and whenever new information arrives that changes the assumptions the plan is built on.

However, "living" does not mean "fluid." The structure (sections, tables, gates, freezes) is stable. The content within those structures is what gets updated.

### Update Cadence

| Update Type | Trigger | Owner | Cadence |
|---|---|---|---|
| **Sprint-level** | Sprint completes; exit criterion status changes | TPM | Weekly (Friday after sprint close) |
| **Risk register** | New risk identified, risk score changes, risk closed | Risk owner | Biweekly (at minimum); immediately for new red risks |
| **Milestone status** | Monthly milestone review completes | TPM | Monthly (last Friday) |
| **Phase exit** | Phase gate signed | TPM | At each phase boundary (W4, W8, W20, W30, W38, W42, W44) |
| **ADR-driven** | ADR is merged that affects the plan | ADR owner | Within 1 week of ADR merge |
| **Emergency** | Critical risk triggers; playbook invoked | TPM | Within 24 hours |

### What Gets Updated

- **Sprint Timeline:** Status of each sprint's exit criterion (met / at risk / missed).
- **Milestones:** Status of each milestone (on track / slipped / descoped).
- **Risk Register:** Likelihood and impact scores; new risks; closed risks; playbook invocations.
- **Buffer Periods:** Buffer burn-down chart; consumed buffer.
- **Revision History:** Every update — major or minor — gets an entry.

### What Does NOT Get Updated Without a Major Change

- **Project Vision, Objectives, Success Criteria** — these are the contract with the advisor and graduation committee; changing them requires Critical-category approval.
- **Out-of-Scope list** — items can be removed (brought into scope) only via scope-change ADR; items cannot be silently added.
- **Freeze terms** — once a freeze is signed, the frozen items cannot change without a freeze exception (see Change Management Policy).
- **Pod structure** — changes require Major-category approval and a re-allocation plan.

### Versioning

- This document uses semantic versioning: `MAJOR.MINOR`.
- **MAJOR** version increments when a Critical or Major change is merged (e.g., scope change, phase slip, freeze exception). Example: 1.0 → 2.0.
- **MINOR** version increments when a Substantive change is merged (e.g., new risk added, new sprint deliverable, clarifying edit). Example: 1.0 → 1.1.
- Minor changes (typo fixes) do not increment the version; they are noted in the Revision History only.
- The version number in the metadata table at the top of this document is the current version.

### Review Cadence

- **Weekly:** TPM reviews sprint-level updates at the Friday sprint close.
- **Biweekly:** Pod leads review the risk register at the biweekly retrospective.
- **Monthly:** Full team reviews the roadmap at the monthly milestone review.
- **At each phase exit:** All pod leads sign off that the roadmap reflects reality.
- **At Code Freeze (W42):** The roadmap is **frozen** along with the code. No further updates except Revision History entries for post-freeze decisions, until v1.0 is shipped.

### Anti-patterns

- Letting the roadmap go stale ("we'll update it later" — later never comes).
- Updating the roadmap without updating the Revision History.
- Updating the roadmap without communicating the change to the team.
- Treating the roadmap as a historical artifact ("this is what we planned") rather than a living commitment ("this is what we are doing").

---

## Revision History

| Version | Date | Author | Change Summary |
|---|---|---|---|
| **1.0** | 2026-08-03 | Senior TPM / Staff Architect | Initial approved version. Single source of truth for the OpenLearn AI project, committed to the GitHub repository as `MASTER_ROADMAP.md`. Establishes: 44-week plan (W1–W44), 7 phases (P0–P6), 9-person team across 4 pods, 5 quality gates (v0.4, Tier 1, Tier 2, Feature, Code), 32-risk register with 6 contingency playbooks, 7 scoped component-level fallbacks, signed Out-of-Scope list (15 items), 1,820-hour pessimistic capacity budget, 22-week graduation prep runway, and the engineering principles of working software over perfect architecture, incremental delivery over big-bang, and risk reduction over feature count. |

---

*End of MASTER_ROADMAP.md v1.0.*
