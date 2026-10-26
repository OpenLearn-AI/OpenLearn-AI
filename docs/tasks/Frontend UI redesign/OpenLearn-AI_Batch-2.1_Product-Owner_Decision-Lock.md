# OpenLearn-AI — Batch 2.1 Product-Owner Decision Lock

**Status anchor:** decision-lock record for the Batch 2.1 discovery review — documentation-only, executed 2026-10-18 against `frontend-redesign` @ `005711e`.
**Authority:** the Product Owner's (Seyam's) decision-lock prompt of 2026-10-18, cross-verified in this record against repository evidence.
**Reading rule:** every decision below carries one of five statuses — `APPROVED` (owner decision is settled), `CLOSED` (owner-confirmed acceptance is complete; do not reopen without new contradictory evidence), `DEFERRED` (deliberately assigned to a later, separately scoped batch), `PENDING EVIDENCE` (the direction is approved but the implementation contract must still be inspected/planned before the decision is fully resolved), `NEEDS OWNER DECISION` (evidence cannot settle a genuine product choice). Implementation facts are labeled as such and cite their evidence paths.

---

## 1. Purpose and Scope

This record preserves the Product Owner's decisions from the Batch 2.1 Discovery Report review (`OpenLearn-AI_Batch-2.1_Discovery_Demo-Journey_Environment-Lock.md`) as the current authoritative product direction, in a form that survives without the conversation that produced it. It is one of two deliverables of the decision-lock batch; the other is the corresponding dated entry in the execution ledger (`OpenLearn-AI_Frontend_Execution_Progress.md`). Where the discovery report proposed (journey sequence, dataset, design references), this record states what the owner actually decided, and it corrects or qualifies any proposal whose assumptions did not survive the evidence check.

The batch is **research, decision reconciliation, and documentation only**. It does not implement the frontend redesign (Phase 4 work), does not implement the local AI environment (the next implementation batch's work), does not implement onboarding or the material UI, and does not modify the roadmap DOCX. Every technical assumption that could be settled by the repository, the API contract, the technical specification, or the execution roadmaps was settled there before being documented here; anything that could not be settled is labeled `PENDING EVIDENCE` or listed as an open owner question rather than being written down as fact.

---

## 2. Repository Baseline and Evidence Reviewed

### 2.1 Baseline verification (preflight, 2026-10-18)

- Fresh isolated clone of `https://github.com/OpenLearn-AI/OpenLearn-AI`, branch `frontend-redesign`.
- `HEAD = 005711ea2659060aa50935af4aea0818782589da`, equal to `origin/frontend-redesign`; working tree clean; no stashes; tracking correct. The expected prior baseline `60d3ba5af7c2464525784f6cabf75c2e324251f4` is the direct parent.
- The single new commit `005711e` (authored by Seyam, 2026-10-17 23:19 +03) is exactly the owner's application of the delivered Batch 2.1 discovery patch: `git show --stat` = 6 files, +663/−17 — the discovery note (new, 477 lines), this ledger, `infra/dev/bootstrap-keycloak.sh`, `infra/docker-compose.dev.yml`, `scripts/setup-dev.sh`, `docs/development/LOCAL_SETUP.md`. No application code was in the commit; the discovery deliverable is now part of the tracked record.
- No reset, rebase, force-push, or history rewrite was performed anywhere in this batch.

### 2.2 Documents read in full or in their governing sections

| Document | Path | Use in this record |
|---|---|---|
| Lifecycle rules | `docs/tasks/Frontend UI redesign/GLM-batch-n-patch-lifecycle-rules.md` | Batch mechanics; documentation-only verification definition |
| Execution ledger | `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md` (786 lines at `005711e`) | Prior batch actuals; Current State; Open Questions #1–#7; Next Authorized Batch |
| Batch 2.1 discovery report | `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-2.1_Discovery_Demo-Journey_Environment-Lock.md` | The proposals this record locks, amends, or defers; R1–R9 source list |
| Batch 0.2 scope-freeze note | `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-0.2_Scope-Freeze_Decision-Note.md` | R7's stale Q4 default (verified still present, line 77) |
| 44-week execution plan | `planning/Roadmap/44-WEEK-EXECUTION-PLAN .md` (note the space before `.md`) | Product-roadmap authority: Week 6 profile subset, W9 Week 9 status-surface assignment, W17 onboarding basics, W37/W41 RTL/NFR-8, staging-demo cadence |
| Roadmap DOCX (v2.0) | `docs/tasks/Frontend UI redesign/OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx` (extracted via python-docx; 99 paragraphs / 35 tables) | Batch 2.1/2.2/4.3/5.3 definitions verbatim; R1/R3 wording confirmed unchanged; §6 coverage matrix; §9 hub slots; §13/§14 |
| Technical specification v4 | `docs/design/OpenLearn_AI_v4_Technical_Specification.md` | §15.1 six-field profile subset (verified table); §14.5/§15 profile context; implementation-status tables |
| Tracked API contract | `docs/openapi.json` + `backend/app/schemas/profile.py`, `backend/app/api/users.py`, `backend/app/services/profile_service.py` | The profile/auth contract audit (§4.4 below) |
| Frontend sources | `frontend/app/**` (9 routes), `frontend/components/**`, `frontend/features/**`, `frontend/lib/**` | Landing/auth/shell/RTL current-state verification |
| Infra sources | `infra/docker-compose.dev.yml`, `infra/dev/bootstrap-keycloak.sh`, `infra/realm-export.json`, `backend/.env.example` | Local environment gap; account provisioning; absence of any Keycloak theme |
| Dataset corpus | `experiments/OCR/ocr-benchmark/data/raw/custom/1. English born-digital/` and `…/2. Arabic born-digital/` | Dataset decision evidence (§5.2) — all 30 PDFs enumerated and text-extraction-tested |

### 2.3 Evidence not re-produced in this batch (cited, attributed)

- The frontend/backend test matrices (frontend unit 54/54, lint/typecheck, Storybook 42/42, build 9 routes; backend course+contract 32/32; core regression 254 passed / 1 environmental docling failure) were established by Batches 0.1–1.4 and the 1.4 closeout at earlier commits and are cited from the ledger; `005711e` adds documentation/provisioning files only, so they stand for this baseline without re-execution.
- The staging-proven status of the material pipeline is the recorded evidence of AI Weeks 7–8 (ledger, discovery §7.1). This batch did not run the pipeline, Docker, Keycloak, any API, or any upload — see §10.

---

## 3. The Five Core Decisions (A–E) — Statuses and Verified Consequences

### Decision A — Local-first development and environment — `APPROVED`

The local development environment is the primary environment for development and repeatable demo rehearsals. Staging remains available as a secondary environment and fallback — this decision does not abandon staging. The local AI/material-processing environment gap must be addressed in the **next implementation batch**.

Verified repository consequences (facts, not assumptions):

- `infra/docker-compose.dev.yml` defines exactly three services: `db` (`pgvector/pgvector:pg16`), `keycloak` (26.7.3, realm imported), and the one-shot `keycloak-bootstrap`. **No S3-compatible storage, no Redis, no Celery worker exists locally.** `backend/.env.example` ships `S3_ENDPOINT_URL=http://localhost:9000` with empty credentials; nothing listens there locally, so `POST …/materials/upload-url` cannot produce a usable presigned PUT target, and a registered material would remain `pending` forever with no broker/worker to move it.
- The documented local workflow (`docs/development/LOCAL_SETUP.md` + `scripts/setup-dev.sh`) genuinely supports every consumed operation (auth, course CRUD, profile) because all PAL providers default to `mock` and no API keys are required — the local-first decision is plausible without any new service for the current demo surface.
- The environment batch's mandate (owner's instruction): first inspect the 44-week execution roadmap, the technical specification, the existing Compose configuration, the storage integration (`backend/app/services/storage.py`), the worker configuration (`backend/app/workers/celery_app.py`), and the actual pipeline requirements; then determine the **smallest complete local setup** that exercises the existing material-processing flow (S3-compatible storage including MinIO where appropriate, Redis, Celery workers, and their configuration) rather than adding services by assumption. That batch implements and tests the environment; it is not a documentation exercise.
- Note recorded for honesty: the 44-week plan's own cadence (Friday staging demos) is a product-plan convention and is not contradicted by this decision; the frontend execution context's demo environment is what changed, and its DOCX wording (R1–R5) is reconciled in the documentation batch (§7).

### Decision B — Substantial product and frontend redesign — `APPROVED`

The redesign may change page composition, information hierarchy, information architecture, content, navigation, and the presence or absence of UI elements, while preserving working authentication, authorization, validation, and business logic unless a separately approved change requires otherwise. Visual execution belongs to Phase 4 (Batches 4.1–4.4) per the roadmap; Batch 2.2 settles content honesty first.

The current product direction, verified against code at `005711e`:

- A public landing page at `/` that explains the learning problem, how OpenLearn-AI helps, and the **real capabilities available today** (course management; material upload and processing once the environment and frontend work land); future capabilities presented clearly as upcoming, never as working features. Current state: the hero copy markets RAG assistants, dynamic knowledge graphs, generated quizzes, and flashcards — none implemented end to end (finding S2, re-verified in `frontend/app/page.tsx` this batch).
- **Authenticated users visiting `/` are redirected to `/dashboard`.** Current state: no redirect exists — the landing page renders a "Go to Dashboard" button for authenticated users (`frontend/app/page.tsx` lines 30–37). The redirect is approved direction and unimplemented future work; its batch assignment is recorded in §8.
- Clear `Get Started` and `Log in` calls to action. Current state: the unauthenticated CTA reads "Get Started - Sign In" and links to `/login` — the honest-copy direction is compatible with the existing entry points.
- The dashboard uses truthful, meaningful data and removes misleading metrics, fake functionality, and placeholder actions (S1 settlement — Batch 2.2's scope, grounded by the 1.4 real-metric inventory in the ledger).
- No functionality or backend support is invented to make the UI look complete. Exact page content and detailed IA are worked out in the appropriate subsequent frontend batches.

### Decision C — Maintainable, appropriately scoped architecture — `APPROVED`

Build a coherent, extensible product without premature abstraction or overengineering. No dynamic plugin/discovery framework, no speculative route families. Start from the real routes, capabilities, contracts, and permissions that already exist; document future feature reservations only where they serve a clear product or architectural purpose.

Verified alignment: the discovery report's IA recommendation (§8–§9 of that report) already implements exactly this doctrine through the roadmap's frozen reservation mechanisms — the §6 coverage matrix, the §9 course-detail hub slots (documented, never rendered), and the §13 visibility tiers. The repository contains no plugin/discovery machinery and no speculative routes (nine `page.tsx` files, re-counted at `005711e`). The frozen test sentence stands: *if a capability's contract disappeared tomorrow, nothing rendered in the product would change.*

### Decision D — Material upload and processing journey — `APPROVED`

The material journey is essential to the product demonstration: (1) an instructor creates a course; (2) the instructor uploads a learning document; (3) the document is registered and processed; (4) the UI exposes the truthful processing states `pending`, `processing`, `ready`, `failed`; (5) the user inspects the resulting state through functionality the backend actually supports.

Verification of the owner's characterization ("backend material API and pipeline are implemented; the immediate gap is local environment support and the missing frontend material journey") — **accurate, with two recorded qualifications**:

1. **Implemented and verified:** the four contract operations exist in `docs/openapi.json` and are classified Scheduled — Batch 4.3 in the roadmap's §6 matrix (upload-url; register → 202 `{material_id, job_id}` with `job_id` log-correlation-only; list; status with the four-value literal). The pipeline behind them is staging-proven (AI Weeks 7–8 evidence, ledger-recorded). Zero materials code exists in the frontend (re-verified by search at `005711e` — the only "material" strings are the S1/S2 mislabels).
2. **Qualification 1:** "the complete end-to-end flow already runs locally" is **not** claimed and is not true today — the local environment gap (Decision A) is the reason the next implementation batch exists. Staging remains the only environment where the full pipeline has ever run.
3. **Qualification 2:** "inspect the resulting state" means, today, the `ready` status plus the materials list — the contract has **no** document-content endpoint (the extracted-text viewer is the Week 9 blocked-tier item), no retry/reprocess endpoint, and no search/chat surface. The UI must not imply more.

The frontend material journey belongs to **Batch 4.3** — identifier verified verbatim in the roadmap DOCX §14 table ("Batch 4.3 — Course detail hub, forms, delete confirmation, materials surface"), so the discovery report's citation stands. It is **not** implemented in this decision-lock batch. Local infrastructure work comes next (the environment batch), and 4.3's walkthrough environment is decided at its own planning per R2.

### Decision E — Student and instructor roles and course ownership — `CLOSED`

**Resolved. Do not reopen this issue** without new contradictory evidence or a newly reported defect.

Recorded acceptance facts, labeled precisely:

- Student authentication and role assignment — **tested successfully by the Product Owner on his machine** (owner-confirmed acceptance).
- Instructor authentication and role assignment — **tested successfully by the Product Owner on his machine** (owner-confirmed acceptance; the instructor account itself was provisioned by the 2.1 patch's bootstrap extension, whose first run is an owner-machine step).
- Course ownership/isolation behavior — **tested successfully by the Product Owner and considered correct** (owner-confirmed acceptance).
- Corroborating repository evidence (separate from the owner's testing, cited not re-run): the ownership implementation is present at `005711e` — `Course.owner_id` service-level filtering in `backend/app/services/course_service.py` (`list_courses(db, owner_id)` with a `WHERE courses.owner_id = :owner_id` predicate) and `require_owned_course` guarding detail/update/delete in `backend/app/api/courses.py` (404 missing / 403 cross-owner) — and the automated suites that covered it are ledger-recorded (Phase 2 course tests 31/31 at `e10249f`; 1.4 closeout course+contract 32/32 at `92b67bd`).
- **Evidence-labeling rule:** the owner's successful testing is an acceptance result, not an independently executed automated test suite by this batch, and must not be described as one. The automated-suite evidence above belongs to the batches that ran it.
- This item is closed for the current scope; no further investigation or implementation batch is scheduled for it.
- The UI currently looking similar for both roles is a **separate future role-aware UX concern** (Batches 2.2/3.3/4.2/4.3 per the roadmap), not evidence that the underlying roles or ownership are broken. Role-aware navigation and affordances are handled in the IA/design work; authorization itself lives in the backend and is not the frontend's to enforce.

---

## 4. Navigation, Authentication, and Onboarding Decisions

### 4.1 Public landing page and authenticated entry — `APPROVED`

- `/` remains the public marketing/product-introduction page.
- Authenticated users visiting `/` are redirected to `/dashboard` (direction approved; current behavior — a button, no redirect — is recorded above; implementation belongs to the landing redesign work).
- `/login` and `/register` remain the technical entry routes, compatible with the existing authentication flow and redirect behavior (`redirectedFrom` handling in `features/auth/redirect.ts` + the `AuthGuard`); their visible experience can be redesigned in a later frontend batch.
- The established Keycloak OIDC/PKCE flow continues. **It is not bypassed or replaced** with a custom authentication implementation. Verified flow shape: `components/auth/LoginForm.tsx` calls `keycloak.login(...)`; `app/(auth)/register/page.tsx` calls `keycloak.register(...)` with the `/dashboard` redirect — both are redirects into Keycloak's hosted flow, protected logic per the roadmap.

### 4.2 Keycloak login and registration appearance — `DEFERRED`

Deferred to a later, separately scoped design/implementation batch. What this batch documented so the deferral is grounded: the frontend renders the `/login` and `/register` shells (local cards with theme toggles, feedback states, Suspense boundary); **the credential and registration forms themselves are Keycloak-hosted pages** served by the local realm (`infra/realm-export.json`; registration enabled by the bootstrap's `registrationAllowed=true`). A custom Keycloak theme may be appropriate later; nothing is themed in this batch, and the repository currently contains no Keycloak theme assets (verified — no theme directory or realm theme configuration).

### 4.3 Sidebar replacing the current navbar — `APPROVED` (direction for the redesigned application shell)

The intended direction is a learning-workspace sidebar rather than the current top navbar:

- Collapsible/expandable on desktop; a drawer or equivalent pattern on mobile.
- Contains only real, currently supported destinations and actions.
- Account and logout actions live near the bottom of the sidebar or its account area (not awkwardly embedded in dashboard content — the current dashboard's Session Control card is the pattern being replaced).
- Navigation and affordances respect actual role permissions — affordance visibility only; authorization stays in the backend.

Implementation facts recorded: the current shell is `components/Navbar.tsx` (top navbar, links `Home | My Materials | Dashboard | Profile & Settings`, theme toggle, user chip) + footer, mounted by `app/(app)/layout.tsx`. The roadmap's Batch 3.3 ("Application shell (role-aware)") is the natural home for the replacement; detailed layout and implementation belong to the appropriate frontend batches. No effort is spent repairing current navbar links/labels as a separate task when the navbar is intended to be replaced (the "My Materials" label fix rides 2.2's content pass because 2.2 touches that copy anyway, not as navbar preservation). Working auth and navigation semantics are preserved during the future replacement.

### 4.4 First-login profile onboarding — `APPROVED` as direction; contract audit **completed** this batch

The intended experience: guide a new user through profile setup before showing the dashboard, ideally one question or choice at a time, with clear progress and backward navigation. The product direction is approved. Per the owner's instruction, the contract audit was performed against the actual implementation before recording the fields as implementable. **Result: every candidate field is already supported by the backend/API — classification 1 for all six.**

Evidence base: `backend/app/schemas/profile.py` (`ProfileUpdate` / `ProfileResponse`), `backend/app/api/users.py` (`GET`/`PUT /v1/users/me`), `backend/app/services/profile_service.py` (upsert, full replacement), `backend/app/models/profile.py` (column constraints), spec §15.1 (verified six-field table), and the frontend mirror `frontend/features/profile/schemas.ts` + `frontend/components/profile/ProfileForm.tsx` (which already renders all six fields).

| Candidate field | Classification | Verified contract facts |
|---|---|---|
| Education level | **1 — already supported** | `education_level: str` required in `ProfileUpdate` (1–50 chars); nullable column `String(50)`. The spec designs an enum but defines no members, so the contract carries free-form strings — a frontend-defined option list stores valid values today; a shared enum vocabulary would be an explicitly scoped backend change (not required for onboarding to work) |
| Major / field of study | **1 — already supported** | `major: str` required (1–255 chars); nullable column `String(255)`; free text |
| Preferred language (English or Arabic) | **1 — already supported** | `preferred_language: Literal["en","ar"]` required; DB CHECK `ck_profiles_preferred_language_supported`; column non-null with server default `'en'`. The API-level constraint matches the owner's two-choice framing exactly |
| University | **1 — already supported** | `university: str \| None` optional (1–255 chars when present); nullable column |
| Learning style | **1 — already supported** | `learning_style_vark: str \| None` optional (≤20 chars); nullable column. Same enum-pending situation as education level (VARK labels such as "Reading/Writing" fit the 20-char bound) |
| Daily available study time (minutes) | **1 — already supported** | `daily_available_minutes: int` required in `ProfileUpdate` — strict int, `> 0`, `≤ 1440` mirroring DB CHECK `ck_profiles_daily_available_minutes_range`; column nullable until onboarding supplies a value |

Contract semantics the onboarding implementation must respect (facts):

- `PUT /v1/users/me` is a **full-replacement upsert**, not a patch: every required field (`education_level`, `major`, `preferred_language`, `daily_available_minutes`) must be sent on every update, and omitted optionals (`university`, `learning_style_vark`) are **cleared**. A step-by-step onboarding that PUTs after each question would erase earlier answers unless it sends the accumulated payload — a client-side accumulation pattern is sufficient; no endpoint change is required.
- `GET /v1/users/me` returns **404** when no profile row exists — this is the natural, already-supported onboarding trigger ("no profile yet") and completion signal.
- No endpoint support, persistence, required-field, or profile-completion behavior was invented here; the completeness metric itself is a frontend derivation (Batch 2.2's dashboard addition, per the 1.4 inventory).
- **Batch-assignment gap (`NEEDS OWNER DECISION`, §8):** first-run onboarding is not defined as a batch anywhere in the frontend roadmap's batch list; the 44-week plan carries "first-run onboarding basics (profile completeness prompt)" at Week 17 (W17). The reconciliation batch should assign the onboarding implementation to a named frontend batch.

### 4.5 Language preference and RTL — `APPROVED` as the intended UX policy; implementation details `PENDING EVIDENCE`

The preferred behavior, as policy: (1) respect a saved user language preference; (2) if none exists, use browser language as an initial suggestion; (3) fall back to the product default if neither is available; (4) set layout direction consistently with the selected language, including RTL for Arabic; (5) allow manual switching. This is **not assumed to be implemented** — verified current state at `005711e`:

- **Persistence home exists:** `profiles.preferred_language` (`en`/`ar`, DB CHECK enforced) — saved preference has a designed storage location reachable via the existing profile API. The `GET /auth/me` `settings` free-form JSONB blob also exists but has no settings surface and is not the designed home.
- **Nothing consumes it for direction or locale:** `frontend/app/layout.tsx` hardcodes `lang="en" dir="ltr"`; no i18n framework, no locale switching, no direction handling exists anywhere in the frontend (verified by search). `preferred_language` is read only as a form field default in `ProfileForm`.
- **RTL readiness is minimal but real:** the Noto Sans Arabic font rail is loaded in the root layout (Arabic glyphs will not fall back to a system default); no logical-property usage was found in `app/globals.css` (zero hits for `ps-`/`pe-`/`ms-`/`me-` patterns).
- **Product-plan context:** the 44-week plan schedules "RTL + bilingual verification vs NFR-8 (W37/W41)" and "RTL-readiness audit" at W37/W41; the frontend roadmap keeps a full i18n framework in tier E (intentionally not exposed) unless that scope makes it a frontend requirement. The policy above is the design target for the redesign; the mechanism (how preference, detection, fallback, direction, and manual switching are composed, and how much lands in Phase 3/4 versus aligning with the W37/W41 verification pass) is verified at planning — see §8.

---

## 5. Demo Journey and Dataset Decision

### 5.1 Demo journey — direction `APPROVED` (preserved from the owner's decision)

The owner-approved demo direction, to be demonstrated when each segment's dependencies land:

1. The public landing page and authentication.
2. Profile onboarding — once its contract is verified (done, §4.4) and implemented (batch assignment pending, §8).
3. Instructor course creation and course management.
4. The material journey — after the local environment and frontend work are complete (environment batch next; frontend surface Batch 4.3).
5. The student account's owner-scoped course view (the honest empty state made visible by PR #79's owner-scoped listing).
6. Logout from the redesigned account/navigation area.

The existing local `student` (`testuser`) and `instructor` accounts are used where appropriate; both roles and course ownership are owner-accepted (Decision E, `CLOSED`). The discovery report's detailed 11-step table (§11 of that report) with per-step readiness ratings remains the working runbook; its NOT READY ratings for the material segment remain accurate and nothing in this record upgrades them — the readiness-changing work is exactly the environment batch and Batch 4.3. The rehearsal of the READY steps (`setup-dev.sh` run + bootstrap first run + scripted walk) remains the outstanding Batch 2.1 owner-machine item.

### 5.2 Dataset — `APPROVED`, with files selected and extraction-tested this batch

Decision: choose one small English born-digital PDF and one small Arabic born-digital PDF from the existing benchmark folders. All 30 candidate files in the two folders were enumerated, opened, and text-extraction-tested locally (pypdfium2, read-only; script preserved at the executing workspace). The selections:

| Slot | Selected file | Size | Pages | Extracted text | Evidence |
|---|---|---|---|---|---|
| English | `experiments/OCR/ocr-benchmark/data/raw/custom/1. English born-digital/custom_custom_english_born_digital_005_p001.pdf` | 56,951 B | 1 | **3,501 chars** | First page of "ImageNet Classification with Deep Convolutional Neural Networks" (AlexNet) — a published, born-digital academic text; comfortably above the pipeline's 50-character OCR gate, so a text-native path (Docling ingest → chunking → local BGE-M3 embeddings) is expected, no cloud OCR |
| Arabic | `experiments/OCR/ocr-benchmark/data/raw/custom/2. Arabic born-digital/custom_custom_arabic_born_digital_003_p004.pdf` | 41,392 B | 1 | **1,797 chars** | Published Arabic literary/biographical text (al-Maʿarrī-related); smallest text-rich file in the folder; likewise far above the OCR gate |

Both files exist, are small enough for a local demo (42–57 KB), are born-digital (text extractable without OCR), contain no sensitive content, and open cleanly (no reader errors across all 30 candidates). Recorded alternates if the owner prefers: English — `…_005_p002.pdf` (121,157 B, 4,472 chars) and `…_005_p003.pdf` (61,365 B, 3,970 chars), the same paper's continuation pages; Arabic — `…_003_p002.pdf` (88,149 B, 2,162 chars) and `…_002_p001.pdf` (109,159 B, 966 chars, a university lecture page from Algiers).

Honest limitations, explicitly recorded:

- The extraction test used pypdfium2 in this sandbox. It proves the files carry substantial extractable text; it does **not** characterize how the production pipeline's Docling ingest will parse them (including Arabic visual/logical-order handling). That verification belongs to the environment batch's practical testing.
- No upload or processing rehearsal was run (no Docker here; it is also future work by decision — actual upload/processing rehearsal happens after the local environment is implemented).
- The dataset remains the discovery §13 minimum set (2 demo users, 3 instructor-owned courses, `testuser` owning none, 1–2 materials, expected states `pending → processing → ready`, one profile completion); no seed script exists per roadmap §19 — demo data is created through the real product flow.

---

## 6. Known Misleading UI and Scope Boundaries

Recorded as known redesign concerns — **not** new functionality to implement now (verified present in code at `005711e` where noted):

- The landing page advertises RAG chat, quizzes, flashcards, and a knowledge graph — none implemented end to end (`frontend/app/page.tsx` hero copy; the "Interactive AI Tools" card renders clickable "RAG Chat" / "Knowledge Graph" tiles that both navigate to `/dashboard`, where the same promises appear as "Coming soon" panels — finding S2).
- Dashboard labels and metrics are misleading where course counts are presented as materials ("Active Materials" card showing the course count; Navbar "My Materials" label — finding S1; the count itself is now honest at the data layer via PR #79's owner-scoped listing).
- Placeholder actions such as "Open Chat" and "View Graph" must not be presented as functioning features without evidence; there is no chat, graph, quiz, or citation endpoint in `docs/openapi.json` to back them.
- The current navbar is intended to be replaced (sidebar direction, §4.3); avoid unnecessary repairs to it before the replacement.

Batch 2.2 and the subsequent redesign phases define the truthful content and information hierarchy using the current implementation as evidence. Scope boundaries for this decision-lock batch (what was **not** done): no frontend redesign or application-code changes; no local environment implementation; no Compose/service changes; no Keycloak theme work; no onboarding implementation; no material-upload UI; no new features, endpoints, or speculative architecture; no reopening of the accepted roles/ownership item; no roadmap DOCX edit (the DOCX remains at its FR-REB-02 state — verified by `git log`, last change `699c496`).

---

## 7. Roadmap Reconciliation — R1–R9 Status and Disposition

The discovery report §5.2 recorded nine wording items where the roadmap/records still say staging-default. This batch re-verified each item's presence at `005711e` (the DOCX is unchanged since FR-REB-02 `699c496`; the 0.2 note and ledger were re-read) and fixes the disposition per the owner's sequencing decision: **the comprehensive documentation reconciliation follows the environment batch, not this one, and not silently.**

| # | Source (path) | Current wording (abridged, re-verified) | Status | Disposition |
|---|---|---|---|---|
| R1 | Roadmap DOCX §14, Batch 2.1 table | "staging confirmed as demo environment pending the 0.1 CORS preflight (local dev is the documented fallback)" — confirmed verbatim in the §14 table | OPEN | Reconcile in the documentation batch: local stack is the default demo environment (Decision A); staging optional |
| R2 | Roadmap DOCX §14, Batch 4.3 validation table | instructor walkthrough of upload → status "on staging" | OPEN | Environment becomes a 4.3-planning decision: extended local AI profile (preferred, honors Decision A) or staging fallback |
| R3 | Roadmap DOCX §14, Batch 5.3 table | "Final staging deploy … on staging" — title "Batch 5.3 — Staging validation and demo dry run" confirmed | OPEN | Re-title/re-scope to "Demo validation and dry run"; environment = primary demo (local), staging optional |
| R4 | Roadmap DOCX §15 dependencies table | "Staging credential — provisioned during 2.1" | OPEN | Replace with the local/demo credential provisioned by the 2.1 bootstrap extension (local Keycloak realm) |
| R5 | Roadmap DOCX §24 validation matrix | "Materials upload → status walk — on staging"; "Demo dry run — on staging" | OPEN | Environment references updated per R1–R3 |
| R6 | Roadmap DOCX §19 | journey candidate "finalized in 2.1" with the materials walk conditional | OPEN | Conditionality resolved by Decision D (materials walk adopted); journey direction locked in §5.1 |
| R7 | Batch 0.2 decision note §5, Open Question #4 default | "staging preferred pending the staging preflight; local dev is the documented fallback" (line 77, re-verified) | OPEN | Superseded by Decision A; amend via the note's own rule (new evidence + decision record — this file and the ledger entry) in the documentation batch |
| R8 | Ledger Open Question #2 | staging CORS live preflight routed to 2.1's environment lock | ALREADY RECLASSIFIED (2026-10-18, 2.1 discovery) | Optional evidence for the optional environment; closable anytime via the existing script's `--with-staging-preflight`; not a demo prerequisite |
| R9 | Ledger Status Board / 5.x batch titles | "5.3 Staging validation and demo dry run" | OPEN | Title wording aligns with R3 |

No R-item was marked reconciled in the DOCX or the 0.2 note by this batch, and none may be considered complete until the documentation batch executes the edits and the patch is applied by the owner.

---

## 8. Open Owner Questions

Genuine product/scheduling choices that repository evidence cannot settle (everything else in this record was settled by evidence):

| # | Question | Evidence context | Smallest decision needed |
|---|---|---|---|
| 1 | Which frontend batch implements first-login onboarding? | Contract audit complete (§4.4): all six fields already supported; not defined in the frontend roadmap's batch list; the 44-week plan carries onboarding basics at W17 | Assign it to a named batch (e.g., fold into 4.4 "Profile" or a new numbered batch) at the documentation reconciliation |
| 2 | Enum vocabularies for `education_level` and `learning_style_vark`? | Spec defines no enum members; the API accepts free-form strings today, so a frontend-defined option list works without any backend change; a shared enum would be an explicitly scoped backend change | Whether structured pickers use frontend-defined option lists (recommended for onboarding) or a backend vocabulary change is wanted for cross-surface consistency |
| 3 | How much of the language/RTL policy lands in Phase 3/4 versus aligning with the W37/W41 NFR-8 pass? | Persistence home exists (`profiles.preferred_language`); direction/switching/detection mechanisms do not exist (§4.5); the 44-week plan schedules RTL/bilingual verification at W37/W41 | Whether manual language switching + RTL composition is a Phase 3/4 redesign requirement now or is staged with W37/W41 (recommended: design RTL-ready in Phase 3/4, full bilingual UI depth per the plan's scope) |

Not an owner question but recorded so it is not lost: Batch 2.1's rehearsal (setup + bootstrap first run + scripted walk of the READY steps) remains outstanding on the owner machine — an execution item, unchanged by this decision lock.

---

## 9. Explicit Next-Batch Sequence

1. **Next implementation batch — local environment gap closure and practical verification.** Inspect the 44-week plan, the technical specification, the existing Compose configuration, the storage integration, the worker configuration, and the actual pipeline requirements; determine the smallest complete local setup (S3-compatible storage including MinIO where appropriate, Redis, Celery workers, configuration) that exercises the existing material-processing flow; implement it; test it practically. This is not a documentation exercise. The dataset's two PDFs (§5.2) are the natural first upload candidates once storage/broker/worker exist.
2. **Comprehensive documentation reconciliation batch** — follows the environment work and its testing. Executes R1–R9 (§7), refreshes the roadmap DOCX and related records, and resolves the §8 assignments (onboarding batch; enum vocabulary; language/RTL staging). Do not start it early.
3. **Frontend execution resumes per the roadmap** — Batch 2.2 (Honest-surface settlement) remains the next frontend authorization in the roadmap's sequence, followed by Phases 3–4; the material journey's frontend surface is Batch 4.3. Per the lifecycle rules, every batch starts only on Seyam's explicit authorization.

---

## 10. Change History and Verification Record

**Batch type:** documentation-only (decision lock). **Executed:** 2026-10-18, isolated clone at `005711e`.

**Verified in this environment (actually executed):**

- Git preflight: fresh clone; branch/HEAD/origin equality; clean tree; no stashes; parent relationship `60d3ba5 → 005711e`; `git show --stat 005711e` = the 2.1 discovery patch's exact 6-file footprint; DOCX history check (`git log` — last DOCX change `699c496`, FR-REB-02).
- Full reads: lifecycle rules; ledger (786 lines); discovery report (477 lines); 0.2 decision note (Q4 region); 44-week plan (structure + targeted passes: W6 profile subset, W9, W17, W37/W41, staging cadence, bilingual rows); spec §15.1 and its surrounding sections.
- Source-level contract audit: `backend/app/schemas/profile.py`, `backend/app/api/users.py`, `backend/app/services/profile_service.py`, `backend/app/models/profile.py`, `backend/app/schemas/auth.py`, `frontend/features/profile/schemas.ts`, `frontend/components/profile/ProfileForm.tsx`, `frontend/app/(auth)/login/page.tsx`, `frontend/app/(auth)/register/page.tsx`, `frontend/components/auth/LoginForm.tsx` (login call site), `frontend/app/page.tsx`, `frontend/app/layout.tsx`, `backend/app/services/course_service.py`, `backend/app/api/courses.py`, `infra/docker-compose.dev.yml`, `infra/dev/bootstrap-keycloak.sh`, `infra/realm-export.json` (theme absence), `backend/.env.example` (S3/credential defaults).
- Roadmap DOCX extraction via python-docx (35 tables scanned; Batch 2.1/2.2/4.3/5.3 definitions and §6/§9/§13 rows captured verbatim).
- Dataset verification: all 30 PDFs in the two born-digital folders enumerated and extraction-tested (pypdfium2; every file opened, 1 page each, per-file size/char-count/sample recorded); selections in §5.2 based on that output.
- Search-based absence proofs: no materials code in the frontend; no i18n/direction handling; no logical-property usage in `globals.css`; no Keycloak theme assets; `require_admin` still without call sites.

**NOT executed in this environment (honest gaps — none of these may be inferred as done):**

- No Docker, no Compose stack, no Keycloak, no backend/frontend runtime, no API calls, no upload, no pipeline run, no E2E or unit test re-execution (cited matrices belong to their recorded batches), no browser-based verification of any page.
- No application of the patch: per the lifecycle rules, Seyam reviews, applies, commits, and pushes.

**Files changed by this batch (exactly two, both documentation):**

1. `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-2.1_Product-Owner_Decision-Lock.md` — **new**, this record.
2. `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md` — decision-lock entry (`### 2.1 — decision lock`), Current State refresh (HEAD `005711e`), Execution History row, Status Board 2.1 row update, Next Authorized Batch refresh (environment batch).

**Consistency checks performed:** the two deliverables were cross-checked line by line — same decision statuses, same dataset selections, same R1–R9 dispositions, same next-batch sequence; the ledger entry summarizes this record and defers to it as the authoritative decision text.
