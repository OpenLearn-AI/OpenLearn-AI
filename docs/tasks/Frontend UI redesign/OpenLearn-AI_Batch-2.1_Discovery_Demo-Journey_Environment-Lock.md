# OpenLearn-AI — Batch 2.1 Discovery Report
## Demo Journey, Page Architecture, and Environment Lock

| Field | Value |
|---|---|
| Batch | 2.1 — Demo journey and environment lock (+ instructor test user; materials-walk decision) |
| Executed | 2026-10-18 |
| Executor | GLM (Super Z), executing agent |
| Authorized by | Seyam, 2026-10-18 — owner-directed discovery instruction with five authoritative decisions (A–E) |
| Verified baseline | `60d3ba5af7c2464525784f6cabf75c2e324251f4` — `1.4-closeout-evidence-based-review`, branch `frontend-redesign` |
| Batch type | Research and documentation with one scoped provisioning change; **no application code changed** |
| Deliverables | This report (repo note + MD + PDF editions); validated patch `frontend-redesign-2.1-discovery-demo-journey-environment-lock.patch`; ledger update |

---

## 1. Executive Summary

This batch executed the owner-directed discovery for the frontend redesign's Phase 2 opener: it verified the repository state against the reported baseline, re-read the full governance context, audited every implemented frontend route against the real API contract, audited the owner's required material journey end-to-end, and produced a grounded recommendation for the demo journey, the page architecture, and the environment/dataset procedure. Everything below is evidence-based; nothing was assumed from the reported claims without checking the repository.

Six findings frame the batch:

1. **The reported baseline is verified current.** `origin/frontend-redesign` advanced exactly one commit past the previously known `92b67bd` to `60d3ba5af7c2464525784f6cabf75c2e324251f4` (`1.4-closeout-evidence-based-review`, authored by Seyam on 2026-10-17). That commit changes exactly one file — the progress ledger, +64/−9 — and its diff is **byte-identical to the Batch 1.4 closeout patch delivered by the executing agent**. The owner applied the delivered patch verbatim and committed it. Working state in this batch's research worktree: clean, detached at `60d3ba5`.

2. **The committed ledger does not record Batch 1.4 as DONE — it honestly records PARTIALLY EXECUTED, and the owner's new confirmation closes the gap.** The closeout entry (applied by `60d3ba5`) records criterion 3 ("course list and course detail continue to load against the live API") as **BLOCKED / NOT RUN** and states verbatim that "Batch 1.4 does NOT yet qualify for DONE." That was accurate when written: the execution environment has no Docker daemon, no local stack, and no credentials. The owner has now confirmed that the required live-API flow **was tested successfully on his machine** — evidence that postdates the closeout. This batch does not repeat or reopen the closeout; it provides a small, attributed ledger addendum that records the owner-confirmed verification and upgrades Batch 1.4 to EXECUTED, while stating explicitly that the executing agent did not personally perform that test and that Batch 1.2's owner validation and 1.3's Sentry runtime verification remain outstanding (Gate B is therefore still not claimable).

3. **The frontend route inventory is exactly nine routes, confirmed at `60d3ba5`** — landing, login, register, dashboard, courses list, courses/new, courses/[id], courses/[id]/edit, profile — plus the two route-group layouts, both groups' `error.tsx`/`loading.tsx` (Batch 1.2's S8 completion verified in code), a root layout, and `not-found.tsx`. All recorded S1/S2 dishonesty findings were re-verified present in code: the hard-coded "Student Dashboard" heading, three "Coming soon" stat cards, two "Coming soon" sections with mislabeled "Open Chat"/"View Graph" buttons, the "Active Materials" card that actually counts courses, the Navbar's "My Materials" label pointing at `/courses`, and the landing page marketing RAG chat, quizzes, flashcards, and a knowledge graph. There is **no materials code in the frontend at all** — no feature slice, no route, no component; the four grep hits for "material" are the mislabeled strings themselves.

4. **The material journey is API-complete but is not a working user journey today.** The backend contract carries all four material operations (presigned upload-url, registration returning `202 {material_id, job_id}`, per-course listing, and status polling across the four-value literal `pending → processing → ready | failed`), and the pipeline behind them is staging-proven (AI Weeks 7–8). But the frontend surface that would make this a *journey* is Batch 4.3's scheduled scope, and the plain local development stack cannot exercise the pipeline at all: the dev compose runs only `db` + `keycloak` (+ a one-shot Keycloak bootstrap) — there is **no S3-compatible storage service, no Redis, and no Celery worker locally**, so `POST .../materials/upload-url` fails on an unconfigured storage client and a registered material would sit `pending` forever. The journey therefore stays in the target demo exactly as the owner directed — as a designed segment with honest readiness ratings, its implementation dependencies named (Batch 4.3 plus an environment decision), and no claim that it works today.

5. **The owner's local-first decision reverses the roadmap's recorded default and needs formal reconciliation.** Roadmap v2.0 §14 (Batch 2.1) says "staging confirmed as demo environment pending the 0.1 CORS preflight (local dev is the documented fallback)", Batch 4.3's validation walks materials "on staging", Batch 5.3 is titled "Staging validation and demo dry run", and the dependencies table calls the instructor test user a "staging credential." The owner has decided local is the default development **and** primary demo environment, with staging optional. This batch records the decision in the permitted records (ledger + this note), lists every piece of wording that needs reconciliation, and does **not** silently rewrite the roadmap DOCX — a DOCX edit is a separate authorized batch under the lifecycle rules.

6. **The scope assessment is affirmative with boundaries.** The requested work — page inventory, information architecture, demo journey, environment and dataset lock — is precisely what roadmap v2.0 §14 defines Batch 2.1 to be ("Lock journey, page inventory, environment, and dataset procedure"), and it is the correct next step before Phase 3 design work begins. The boundary recommendation in §15 separates what must be decided now from what is documented-only future architecture, what is deferred to named later batches, and what remains out of scope entirely — within the frozen classification of Batch 0.2, which this discovery does not relitigate.

The batch's concrete outputs: this discovery/runbook note (proposed for the repository at `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-2.1_Discovery_Demo-Journey_Environment-Lock.md`), a ledger update (1.4 owner-confirmed verification record + 2.1 execution entry + refreshed Current State, Status Board, Open Questions, and Next Authorized Batch), and a small idempotent provisioning extension that adds the owner-approved instructor-role course-owner test account to the local Keycloak bootstrap — implemented but **not executed** in this sandbox (no Docker daemon), with first execution documented as an owner-machine step.

---

## 2. Preflight Verification

All checks were performed before any analysis or editing, in an isolated detached worktree; the pre-existing execution clone was not modified in any way.

| Check | Result |
|---|---|
| Repository URL | `https://github.com/OpenLearn-AI/OpenLearn-AI` — confirmed |
| Reported baseline exists | Yes — `git cat-file -t 60d3ba5…` → `commit` |
| Remote state | `git fetch origin --prune`: `origin/frontend-redesign` advanced `92b67bd..60d3ba5`; no other branch moved |
| Commit under the baseline | Subject `1.4-closeout-evidence-based-review`; author MuhammadSeyam; date 2026-10-17 22:08:09 +0300; exactly one commit ahead of `92b67bd` |
| Commit content | `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md`, +64/−9 — **byte-identical to the delivered `frontend-redesign-1.4-closeout-evidence-based-review.patch`** |
| Lineage | `699c496` → `bea19f3` → `7ebe978` → `18d8a69` → `7dc9f67` → `f87c765` → `b56be14` → `e10249f` (1.4 settlement) → `65c8a8c` + `92b67bd` (course-ownership fix, PR #79 — separate post-1.4 change) → `60d3ba5` (closeout ledger) |
| Working tree (research worktree) | Clean, detached HEAD at `60d3ba5` — created via `git worktree add` from the existing execution clone |
| Pre-existing state preserved | The execution clone (`workspace/openlearn-phase2`) is untouched: branch `frontend-redesign` at `92b67bd`, its uncommitted ledger modification (now identical to the committed `60d3ba5` content) left in place, `stash@{0}` (phase-2 ownership working-tree state) preserved |
| Staging containment | Not re-claimed this batch (nothing moved on `origin/staging`; the closeout verified containment at `92b67bd`, and `60d3ba5` is ledger-only) |
| Reset / rebase / force-push / discard | **None performed** — fetch and worktree-add only |

The research base for this batch is therefore exactly the reported baseline, with all prior artifacts preserved.

---

## 3. Source Review and Governance Context

The following sources were read in full or in the depth required by their role in this batch. The lifecycle rules' mandated execution-context trio was read first, then the two mandatory additional documents, then the application and environment sources.

**Governance documents (read in full):**

- `docs/tasks/Frontend UI redesign/GLM-batch-n-patch-lifecycle-rules.md` — batch mechanics: verify repo, preserve state, read context, implement one authorized batch, verify honestly, update the ledger, generate a complete `--binary` patch via the isolated-clone method, validate it on a pristine checkout, report, stop. The executor never commits or pushes; Seyam applies patches.
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md` (the ledger, at `60d3ba5`) — Current State (verified 2026-10-18 by the closeout), Execution Rules, Current Reality (frontend/backend/RBAC/pipeline/infra at the FR-REB-02 baseline), Week 9 integration, coverage summary, the complete execution history and log through the 1.4 closeout, the Batch Status Board, Open Questions #1–#7, and Next Authorized Batch.
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx` (in-document revision v2.0) — extracted in full with `python-docx` (99 paragraphs, 35 tables). Sections relied on heavily: §5 (capability inventories), §6 (coverage matrix), §7/§8 (current and target IA), §9 (course-detail hub), §10 (material lifecycle UX), §13 (visibility tiers), §14 (all 18 batch definitions), §15 (dependencies), §19 (demo journey), §21 (gates), §22 (non-goals), §23 (reservation), §24 (validation matrix), §25 (sequence).
- `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-0.2_Scope-Freeze_Decision-Note.md` — the frozen classification, the finding register, the F5 settlement, the environment/CORS posture at freeze time (including Open Question #4's recorded default: "staging preferred pending the staging preflight; local dev is the documented fallback"), and the frozen demo-journey candidate.
- `CONTRIBUTING.md` — no additional workflow constraints beyond the execution context; the lifecycle rules and ledger govern batch mechanics.

**Product and technical sources:**

- `docs/design/OpenLearn_AI_v4_Technical_Specification.md` (v4.1) — vision and eight system layers, the eight design principles (notably **Local First** as principle 3 and the Arabic/English-first bilingual + RTL design posture), the honest capability-status table (§5.2), the current verified learning workflow (§17.1), the target learning loop (§17.2, planned), frontend architecture including the five planned modules (§20.3 — the Material Management UI is called "most immediately unblocked"), the implemented schema (§21.2), the verified endpoint inventory (§22.3), environments (§23.1), and future vision (§29).
- `docs/openapi.json` (CI-guarded contract) — read via the ledger's contract table and cross-checked against backend source; the closeout's 32/32 backend course+contract run at `92b67bd` covers its consistency with the app, and `60d3ba5` touched no application file.
- `docs/development/LOCAL_SETUP.md` (694 lines) — the authoritative local-runbook source: prerequisites, `scripts/setup-dev.sh` phase behavior, the service topology, authentication setup, server startup, teardown notes, and troubleshooting.
- `docs/environments.md` — the pod-level environment record (Arabic): `dev` verified working (2026-08-09), `staging`/`prod` marked planning-era; explicitly stale relative to the live staging pipeline and retained here as history only.
- `planning/Roadmap/44-WEEK-EXECUTION-PLAN .md` — skimmed for demo cadence (Friday staging demos, tags after passing demos) and Week 9–17 frontend assignments; the frontend roadmap's §12 reconciliation remains the working alignment.
- `frontend/AGENTS.md` — Next.js stub; no additional constraints relevant to a documentation batch.

**Application sources read directly (frontend at `60d3ba5`):** the complete route tree (`app/**`), both group layouts and their boundaries, `components/Navbar.tsx`, `components/AuthGuard.tsx`, `components/CourseCard.tsx`, `components/auth/*`, `components/courses/*`, `components/profile/*`, `components/state/*`, `components/ui/*`, all three feature slices (`features/auth|courses|profile`), and the dashboard/landing/courses/profile page implementations. **Backend sources read directly:** `app/services/storage.py`, `app/services/material_service.py`, `app/services/course_service.py` (post-ownership-merge state), `app/api/deps.py`, `app/workers/celery_app.py`, `infra/docker-compose.dev.yml`, `infra/dev/bootstrap-keycloak.sh`, `infra/realm-export.json`, `backend/.env.example`, and `scripts/setup-dev.sh`.

### Batch 2.1's roadmap definition (the authority for this batch)

Roadmap v2.0 §14, Table 19, quoted in full:

> **Batch 2.1 — Demo journey and environment lock.** Objective: Lock journey, page inventory, environment, and dataset procedure. Files affected: No application code; a demo runbook note; optionally a short scripted sequence of real API calls. What changes: Nine-route inventory confirmed as the redesign surface; journey order fixed; staging confirmed as demo environment pending the 0.1 CORS preflight (local dev is the documented fallback); dataset steps documented and rehearsed once; the instructor-role course-owner test user provisioned (prerequisite for the 4.3 walkthrough); the materials-walk decision recorded — whether the upload → status walk joins the locked journey. Must NOT change: No new routes, features, mock data, or auth/data-layer changes. Completion: A runbook a second person could follow; the journey completes without developer intervention beyond scripted setup.

Gate C ("Demo Surface Locked") requires: "Runbook (2.1) incl. the instructor test user and the materials-walk decision; zero Coming-soon or misleading affordances (2.2); environment and dataset confirmed."

Two roadmap phrases in that definition are directly superseded by this batch's owner decisions and are handled in §5: the staging-as-default demo environment wording, and the sequencing of the materials-walk decision (the owner has already made it: the walk is essential — §7 and §11).

---

## 4. Batch 1.4 Closeout vs the Owner's Confirmation

The tasking asked this batch to "verify that the committed progress ledger records Batch 1.4 as DONE with the owner-confirmed manual verification accurately described." The verified finding is more nuanced, and recording it accurately matters for the project's evidence discipline.

**What the committed ledger actually says (at `60d3ba5`):**

- The closeout log entry's status line: "Status: **PARTIALLY EXECUTED — UNCHANGED** (2026-10-18) … the batch is deliberately NOT marked DONE — the roadmap's live-API validation item remains BLOCKED / NOT RUN, so criterion 3 stays unsatisfied and no criterion was weakened or redefined."
- The closeout verdict, verbatim: "**Closeout verdict: Batch 1.4 does NOT yet qualify for DONE.** Implementation, unit coverage, and the sandbox matrix are verified — now twice, independently — but criterion 3 requires the live-API check that only the documented owner-machine/staging environment can perform."
- Criterion 3's recorded state: "**BLOCKED / NOT RUN (unchanged)** — the sole unsatisfied criterion; environment/credentials still unavailable, re-confirmed today with the same diagnostics as the original block" (no Docker daemon — `docker info` exit 127 — no local db/Keycloak/backend stack, no E2E credentials in the execution environment).

**Why the ledger says that:** the closeout was executed in an environment that structurally could not run the live-API check, and it refused to fabricate or assume the result. That was the honest record at the time.

**What is new:** the project owner now confirms that the required live-API flow was tested successfully on his machine. Roadmap §14's criterion 3 reads "Course list and course detail continue to load against the live API **when the documented environment and credentials are available**" — and the owner machine is exactly that documented environment (per `docs/development/LOCAL_SETUP.md`, which the closeout itself named as the completion path). The owner's confirmation therefore satisfies the criterion that the closeout could not.

**How this batch handles it (without reopening anything):**

1. The closeout work is **not repeated** and no criterion is re-derived. The closeout's evidence stands as written.
2. A small ledger addendum (included in this batch's patch) records the owner-confirmed verification in the closeout entry's terms: criterion 3 is satisfied **on the owner's confirmation** that the live-API flow passed on his machine; the executing agent did not personally perform or observe the test; specifics of the owner's run (exact timestamp, routes exercised) rest with the owner and are not invented here.
3. With criterion 3 satisfied, the addendum upgrades Batch 1.4's status to **EXECUTED** in the Status Board and Next Authorized Batch sections, keeping the distinction that 1.4's own scope (F5 settlement + metric inventory) is `e10249f` and the ownership fix (PR #79) remains a separate change.
4. **Gate B remains unclaimed.** Gate B requires the full closure set: 1.1 complete (done), 1.2 complete (owner-machine validation still pending), 1.3 complete (Sentry runtime verification still blocked), and 1.4 complete (now satisfied per the owner's confirmation). The addendum records 1.4's completion without overstating the gate.

This is the accurate description the tasking asked for: the ledger did not yet record DONE because the evidence postdated the closeout; the addendum closes that gap with correct attribution and nothing more.

---

## 5. Owner Decisions Recorded, and Roadmap Wording Needing Reconciliation

### 5.1 The five authoritative decisions (A–E) and their consequences

These are recorded as owner decisions, not open questions. Each entry states the decision, its verified implementation consequence in the repository, and where it is recorded.

**A — Local-first development and demo.** Local development is the default; the primary demo environment is the local application stack; staging remains available as an optional environment and is not the default demo dependency. *Consequences verified in-repo:* the documented local workflow (`docs/development/LOCAL_SETUP.md` + `scripts/setup-dev.sh`) genuinely supports the product's implemented surface — auth (local Keycloak realm with registration enabled, `testuser` provisioned by bootstrap), course CRUD, and profile — because all AI providers default to `mock` and no API keys are required for the consumed operations. The one gap is the material pipeline (§7). The roadmap's staging-default wording is listed for reconciliation below (§5.2). The staging CORS preflight (Open Question #2) becomes optional evidence for the optional environment, not a demo prerequisite.

**B — Redesign scope: substantial, all implemented pages; visual execution is Phase 4.** The owner expects page composition, hierarchy, shell, navbar, branding, icons, responsiveness, Arabic-first/RTL behavior, and coherence across student/instructor/admin contexts to be redesigned — not a reskin of current arrangements — while authentication, authorization, business behavior, API contracts, data ownership, mutations, and route semantics remain frozen. *Consequences:* the inventory in §6 is written to separate **content/structure recommendations** (which belong to Phase 2, chiefly Batch 2.2) from **visual execution** (Phase 4, Batches 4.1–4.4). Role-aware contexts are grounded in verified capabilities only: instructor-gated material operations, ownership-based course CRUD (no role gate on create/update/delete — ownership only), unenforced admin role. No admin UI is proposed; the redesign must not imply it.

**C — Extensible page architecture.** The owner wants the architecture to accommodate future page families without premature complexity. *Consequence:* §8's recommendation keeps the nine-route skeleton and adopts the roadmap's existing reservation mechanisms (coverage matrix, hub slots, visibility tiers) as the extension approach — route-group conventions and shared layouts only; no dynamic routing, no plugin/discovery machinery, no speculative routes. The four-category classification (§8.2) distinguishes implemented, redesign-needed, future-family, and unresolved-aspirational surfaces.

**D — The material journey is essential.** Upload → observe processing status → inspect resulting state is part of the intended demo and must remain in the target journey. *Consequence:* §7 audits it honestly (API-complete, frontend NOT READY, local environment gap), and §11's journey includes it as a designed segment with readiness ratings and named dependencies. It is **not** implemented in 2.1, and nothing in this batch claims it works today. The backend's future evolution (reasoning endpoints and other Week 9+ capabilities) is accounted for in §8/§9 without inventing contracts.

**E — Instructor test account.** Adding a dedicated instructor-role course-owner test account is approved if none exists. *Verified:* none exists — `infra/dev/bootstrap-keycloak.sh` provisions exactly one user (`testuser`, email `test@example.com`, role `student`); `infra/realm-export.json` defines the `instructor` realm role (alongside `student` and `admin`), so no realm change is needed; account creation flows through Keycloak with just-in-time local provisioning on first API call. *Consequence:* §14 specifies the repeatable, non-production provisioning added by this batch's patch (bootstrap-script extension mirroring the `testuser` pattern; password supplied via a local env var, never tracked).

### 5.2 Roadmap and record wording that needs formal reconciliation

The lifecycle rules place live statuses in the ledger and treat the roadmap DOCX as the planned source of truth, edited only by an authorized batch. This batch records the owner-directed change and lists every piece of wording that a future documentation batch should reconcile. No DOCX was modified.

| # | Source | Current wording (abridged) | Reconciliation needed |
|---|---|---|---|
| R1 | Roadmap §14 Table 19 (Batch 2.1 "What changes") | "staging confirmed as demo environment pending the 0.1 CORS preflight (local dev is the documented fallback)" | Replace with: local stack is the default demo environment (owner decision A, 2026-10-18); staging optional |
| R2 | Roadmap §14 Table 26 (Batch 4.3 validation) | "instructor-role course-owner walkthrough of upload → pending → processing → ready\|failed **on staging**" | The walkthrough environment becomes a decision recorded at 4.3 planning: extended local AI profile (preferred, per decision A) or staging fallback |
| R3 | Roadmap §14 Table 30 (Batch 5.3) | "Final staging deploy … one continuous dry run, zero developer interventions, **on staging**" | Re-title/re-scope to "Demo validation and dry run" with the environment = primary demo (local), staging optional |
| R4 | Roadmap §15 dependencies table | "Instructor-role course-owner test user (2.1) … **Staging credential** — provisioned during 2.1" | "Local/demo credential — provisioned during 2.1 (local Keycloak realm)" |
| R5 | Roadmap §24 validation matrix | "Materials upload → status walk — Manual walk **on staging**"; "Demo dry run — Runbook **on staging**" | Environment references updated per R1–R3 |
| R6 | Roadmap §19 | "finalized in 2.1" journey candidate with the materials walk conditional | The owner has adopted the materials walk (decision D); the journey conditionality is resolved (§11) |
| R7 | Batch 0.2 decision note §5, Open Question #4 default | "staging preferred pending the staging preflight; local dev is the documented fallback" | Superseded by owner decision A; the note's own amendment rule (new evidence + decision record) covers this via the ledger and this note |
| R8 | Ledger Open Questions #2 | Staging CORS live preflight "routed to Batch 2.1's environment lock" | Reclassify as optional evidence for the optional environment; closable anytime via `scripts/run-batch-0.1-local-verification.sh --with-staging-preflight` from a staging-reachable host; not a demo prerequisite |
| R9 | Ledger Status Board / 5.x batch titles | "5.3 Staging validation and demo dry run" | Title wording aligns with R3 |

Reconciliation of R1–R9 in the roadmap DOCX itself is recommended as part of the next documentation-only batch that already touches the roadmap (or a small dedicated amendment batch) — not silently, and not in 2.1.

---

## 6. Current-Page Inventory (evidence-based, verified at `60d3ba5`)

The redesign surface is confirmed as **nine routes** (nine `page.tsx` files under `frontend/app/`), matching the ledger's standing record. Every route was re-read in source for this inventory. "Post-ownership" below reflects the merged PR #79 behavior: `GET /v1/courses` and `GET /v1/courses/{id}` return only the caller's own courses (403 for another user's existing course, 404 for a missing one; uniform for student/instructor/admin; no admin override).

### 6.1 Public surface

**`/` — Landing (public).** Files: `app/page.tsx`. Purpose: product entry; hero + two feature cards. Data: none (auth state only, via `useAuth`/`useMe`). Demonstrably supported today: a working sign-in/register entry with correct authenticated-state CTA ("Go to Dashboard" vs "Get Started - Sign In"). Problems found (re-verified in code): the hero copy markets RAG assistants, dynamic knowledge graphs, generated quizzes, and flashcards — none implemented (S2); the "Interactive AI Tools" card renders **clickable tiles labeled "RAG Chat" and "Knowledge Graph"** that both navigate to `/dashboard` where the same promises appear as "Coming soon" panels — dead-affordance patterns the redesign must not preserve; the "View My Materials" button points at `/courses` (mislabeled destination). Recommendation: **remain a distinct page**; Batch 2.2 settles the copy to real capabilities (course management + materials processing working; learning surfaces explicitly future); Phase 4.1 owns composition/visuals. The honest-copy direction is already recorded in the roadmap §8 target table.

### 6.2 Authentication surface

**`/login`.** Files: `app/(auth)/login/page.tsx` + `components/auth/LoginForm.tsx`. Purpose: Keycloak hosted login entry with `redirectedFrom` return support (Suspense boundary present). Verified: functional; theme toggle present; 1.2's recovery behavior in the form (W1). No dishonesty found. Recommendation: remain; Phase 4.1 redesigns presentation around the protected call sites.

**`/register`.** Files: `app/(auth)/register/page.tsx`. Purpose: starts the Keycloak-hosted registration redirect (`keycloak.register` with `/dashboard` redirect). Verified: Batch 1.2's S3 completion is in code — explicit idle/loading/null-client/error states with `role="alert"` feedback, theme parity with login. Recommendation: remain; Phase 4.1.

### 6.3 Protected application surface (`(app)` group — single `AuthGuard`, shared Navbar + footer)

**`/dashboard`.** Files: `app/(app)/dashboard/page.tsx`. Purpose: signed-in home. Data: `useCourses` (the only live data). Verified problems (S1, all re-confirmed): hard-coded "Student Dashboard" badge on a persona-blind surface; "Active Materials" stat card that actually displays the **course count** (mislabeled — the 1.4 metric inventory flagged this and PR #79 now makes the count honest at the data layer); three "Coming soon" stat cards (RAG Sessions, Generated Quizzes, Knowledge Nodes); an "Intelligent RAG Assistant" section with a mislabeled "Open Chat →" button and a "Coming soon" strip; a "Knowledge Graph Visualizer" section with a mislabeled "View Graph →" button and a dashed "Coming soon" box; a User Profile card and a Session Control card (functional). What is genuinely supported: course count (now owner-scoped), the recent-courses list (first four courses, `CourseCard` reuse), error/loading/empty states via the async-state kit. Recommendation: **remain a distinct page**; Batch 2.2 replaces placeholders with the locked real-metric composition (course count, profile completeness, recent courses) and role-aware/neutral heading; the "profile completeness" metric requires reading the profile — currently the dashboard does not fetch the profile, so 2.2 adds that read (a data-source change 2.2 already owns per its roadmap row's file list and the 1.4 inventory). Phase 4.2 redesigns presentation.

**`/courses`.** Files: `app/(app)/courses/page.tsx`. Purpose: course list with inline client-side search/filter. Data: `useCourses` (owner-scoped list post-PR #79). Verified: functional search across title/description; real empty states (with and without a search query); create-course CTA. Problems: the Navbar labels this route "My Materials" (fixed by 2.2); the header sub-copy promises "course materials, and RAG knowledge bases" — neither exists on this page today (copy belongs to 2.2's honest-surface pass); every `CourseCard` renders an **Edit** button unconditionally — correct for the owner post-PR #79 (the list only contains the caller's own courses) but the affordance language should be part of the role-aware pass. Recommendation: remain a distinct page; 2.2 copy + 4.2 pattern redesign (search, card grid, extracted filter pattern). Post-ownership note for the demo: a student-role account that has not created courses sees an honest empty state — this is correct behavior and worth demonstrating deliberately (§11 step 9).

**`/courses/new`.** Files: `app/(app)/courses/new/page.tsx` + `components/courses/CourseForm.tsx`. Purpose: create form. Verified: functional create + post-save navigation; shared form pattern with validation and API-error presentation. Recommendation: remain; Phase 4.3 composes it into the form pattern; no structural change.

**`/courses/[id]`.** Files: `app/(app)/courses/[id]/page.tsx`. Purpose: course detail — the designated future content hub (roadmap §9). Data: `useCourse`. Verified: title, description, created date, Edit link, `DeleteCourseButton` (accessible confirmation with correct semantics), "Back to Courses"; 404-on-missing via the ApiError-status check; non-owner access now lands on the error state (403) rather than another user's data. Problems: the page is a *record* page — sparse content and no materials region (that is Batch 4.3's scheduled scope, the first big structural change); the "Course details" subtitle is filler. Recommendation: **remain a distinct route and become the hub in 4.3** — header + actions, materials region, documented (never rendered) hub slots per roadmap §9. No route change; the structure changes inside the route.

**`/courses/[id]/edit`.** Files: `app/(app)/courses/[id]/edit/page.tsx`. Purpose: edit form. Verified: Batch 1.1's F3 fix present (`key={course.id}` re-mount semantics); ownership enforced by the API (a non-owner's save attempt would fail with 403 — reachable only by typing a URL, since the list no longer shows foreign courses). Recommendation: remain; Phase 4.3 form pattern; consider whether "edit" remains a separate route or becomes a hub surface — the simplest defensible answer is to keep the route (deep-linkable, form isolation) and let 4.3 decide presentation.

**`/profile`.** Files: `app/(app)/profile/page.tsx` + `components/profile/ProfileForm.tsx`. Purpose: profile create/edit against the six-field subset. Verified: Batch 1.1's F4 fix present (`key={profile?.id ?? "new"}` so null→object re-seeds the form); create-vs-edit presentations; gradient header with user identity; S10 success-token fix in the form. Recommendation: remain a distinct page; 4.4 settles the create-vs-edit composition once; the profile-completeness metric consumed by the dashboard is 2.2's addition.

### 6.4 Shared shell and boundaries

**`(app)/layout.tsx`** — Navbar + footer + single `AuthGuard` (redirect to `/login?redirectedFrom=…`; loading state while Keycloak initializes). **`components/Navbar.tsx`** — logo (`/logo.png`, "OpenLearn AI / Adaptive Learning Platform"), links `Home | My Materials | Dashboard | Profile & Settings`, theme toggle, user chip linking to `/profile`, mobile menu. Verified problems: "My Materials" mislabel (2.2); brand treatment is minimal and the logo asset is generic — the owner's decision B explicitly opens branding/logo treatment for Phase 4; nav link targets stay unchanged (frozen by the roadmap's stability contract). **Boundaries** — `(app)` has `error.tsx`/`loading.tsx`; `(auth)` has `error.tsx`/`loading.tsx` (S8 complete, verified present); root `layout.tsx` + `not-found.tsx` exist. The recorded S9 question (the unreachable `(app)` loading boundary) is Batch 3.2's trivial decision, unchanged here. **Components/** — a small primitive set (`ui/*`), the async-state kit (`state/*`), and feature components; the redesign strategy (§16 of the roadmap: refine-and-compose) treats these as the foundation Phase 3 restyles.

### 6.5 Inventory verdict

No route should be deleted, merged away, or added in Phase 2. The nine-route skeleton is correct for the product's near-term scope (the roadmap's own §8 conclusion, re-confirmed against code): the structural changes that matter are **inside** `/courses/[id]` (the 4.3 hub composition), **on** `/dashboard` and `/` (2.2's honest settlement), and **in the shell** (3.3 role-aware presentation). Everything else is Phase 4 presentation work on stable routes. Two post-ownership UX realities are newly visible and belong in later batches' design inputs: non-owner course access now surfaces as a 403 error state (a candidate for a friendlier "not your course" treatment in 4.x), and role-gated affordances (upload) do not exist yet, so "student vs instructor" presentation is currently expressed only by absence of data, not by affordance visibility.

---

## 7. Material Journey Audit — Upload → Processing Status → Resulting State

The owner has made this journey essential (decision D). The audit distinguishes three layers that are often conflated: **API support** (does the contract carry the operations?), **environment support** (can a given stack execute them?), and **user journey support** (does the frontend make them a walkable flow?).

### 7.1 API support — EXISTS (verified)

The CI-guarded contract (`docs/openapi.json`, app v0.2.0) carries exactly the operations the journey needs, and the ledger's closeout re-verified the contract matches the application:

| Journey step | Contract operation | Auth/authorization | Return | Verified facts |
|---|---|---|---|---|
| Request upload | `POST /v1/courses/{id}/materials/upload-url` (`UploadUrlCreate{filename, title}`) | bearer + **instructor role** + course ownership | `UploadUrlResponse{upload_url, s3_key, title, course_id, expires_in}` | Presigned PUT; the client uploads directly to storage; server-generated `s3_key` (client never picks the key) |
| Register | `POST /v1/courses/{id}/materials` (`MaterialCreate{s3_key, title}`) | bearer + instructor + ownership | **202** `MaterialAcceptedResponse{material_id, job_id}` | `job_id` is log-correlation only — **not queryable**; status keys on `material_id` |
| List | `GET /v1/courses/{id}/materials` | bearer (course visibility) | `MaterialResponse[]` | Includes `status`, `title`, `uploaded_by`, `created_at` |
| Poll status | `GET /v1/materials/{id}/status` | bearer + course ownership | `MaterialStatusResponse{material_id, status}` | Status ∈ the four-value literal `pending → processing → ready \| failed` |

Behind these operations, the Celery pipeline is real and staging-proven (AI Weeks 7–8, closed): Docling ingest → PDF-only targeted OCR (Gemini `gemini-3.6-flash`, behind a 50-character text gate) → deterministic chunking (1200/150) → BGE-M3 1024-dim embeddings → pgvector upsert committed atomically with the `ready` transition; retries (3, 60 s backoff); terminal `failed` for storage/ingestion/OCR-quota/embedding/persistence failures. There is **no** retry/reprocess endpoint, **no** document-content endpoint, and no search/chat/citation/enrollment endpoint in the contract — the "inspect the resulting state" step can today show only the `ready` status plus the materials list, not document content (the extracted-text viewer is the Week 9 blocked-tier item).

### 7.2 Frontend journey support — NOT READY (verified absent)

There is no materials code in the frontend: no `features/materials` slice, no upload affordance, no status UI, no route, no component. The only "material" strings in the app are the mislabels S1/S2 ("Active Materials", "My Materials", "View My Materials"). The four material operations are **scheduled scope for Batch 4.3** ("Course detail hub, forms, delete confirmation, materials surface"), which the roadmap defines with exact flow mechanics: pick file → request presigned URL → PUT → register (202; `job_id` logged, never queried) → materials list + per-material status polling on a modest interval until a terminal state, with honest failed-state copy naming the plausible cause class (including OCR/quota failures) and no retry control while no endpoint exists.

### 7.3 Environment support — the decisive finding

`infra/docker-compose.dev.yml` defines exactly three services: `db` (`pgvector/pgvector:pg16`), `keycloak` (26.7.3, realm imported), and the one-shot `keycloak-bootstrap`. Verified consequences:

- **No S3-compatible storage service locally.** `backend/app/services/storage.py` builds a boto3 client from configured endpoint/credentials (`backend/.env.example`: `S3_ENDPOINT_URL=http://localhost:9000` with **empty** key/secret; `LOCAL_SETUP.md` states MinIO is not part of the local development stack). With nothing listening, `POST .../upload-url` cannot return a usable presigned URL and the browser PUT has no target — journey step 1 fails at the first API call. (Presigning is client-side signing, but the credentials are empty and there is no endpoint to sign against.)
- **No Redis and no Celery worker locally.** `backend/app/workers/celery_app.py` uses `CELERY_BROKER_URL` (Redis; `celery[redis]==5.6.3` in requirements), and nothing in the local setup starts a broker or a worker. Even if a material were registered by API, it would remain `pending` forever — the status vocabulary's first state, never progressing.
- **The AI stack is heavy but owner-machine-plausible.** `requirements.txt` includes the torch/docling stack (setup phase 5 warns it is a large install), BGE-M3 embeddings run locally, and the OCR gate means a text-rich PDF may skip cloud OCR entirely — so a fully local processing path is *plausible* if storage + broker + worker were provided. That is, however, **new infrastructure work** (a MinIO + Redis + worker compose profile), not something that exists today, and it would be an authorized batch of its own.
- **Staging runs the full pipeline** (staging-proven in AI Weeks 7–8; the compose carries the full AI runtime). Under owner decision A it is the optional environment, not the demo dependency.

### 7.4 Readiness verdict per journey step

| Step | Readiness | Missing for it to be demo-ready | Owning batch/work |
|---|---|---|---|
| Upload a material (file → presigned PUT → register) | **NOT READY** (frontend absent; local storage absent; API exists) | Materials upload UI; storage service + credentials for the chosen demo environment | Batch 4.3 (UI); environment decision §12.3 |
| Observe processing status (pending → processing → ready/failed) | **NOT READY** (frontend absent; local broker/worker absent; API exists; pipeline staging-proven) | Status polling UI; broker + worker running for the chosen demo environment | Batch 4.3 (UI); environment decision §12.3 |
| Inspect resulting state | **NOT READY** for content inspection (no document-content endpoint — Week 9 blocker); **PARTIALLY READY** at the API level for `ready` status + materials listing | The 4.3 ready-state presentation; extracted-text viewer only when the Week 9 contract lands | Batch 4.3 (status/list presentation); Week 9 authorized batch (text viewer) |
| Prerequisite accounts (instructor owner) | **PARTIALLY READY** — provisioning designed in this batch (§14), first execution on the owner machine | Run the bootstrap once where Docker exists | Owner-machine step in 2.1 completion |

Nothing in this batch implements, fakes, or pre-announces the journey. It stays in the target demo (§11) with its dependencies named — exactly the owner's instruction.

---

## 8. Proposed Information Architecture

### 8.1 The recommendation in one paragraph

Keep the nine-route skeleton. Do not add routes in Phase 2. Express everything the product's future needs through the three reservation mechanisms the roadmap already froze (§6 coverage matrix, §9 hub slots, §13 visibility tiers), and let Phase 4 compose pages from shared layouts and patterns rather than new navigation structure. The owner's extensibility goal is achieved not by building extension machinery now, but by (a) reserving the course-detail hub's regions per §9 and (b) following two structural conventions that cost nothing today: future **page families** attach either inside the course-detail hub (learning surfaces) or as sibling sections under `(app)` with their own route group only when a real capability justifies it.

### 8.2 The four-category classification (per the owner's requested distinction)

**Category 1 — Implemented and currently supported (the honest surface).** The nine routes plus shell as inventoried in §6: 8 of 12 contract operations consumed (auth/me, profile read/update, course CRUD ×5), Keycloak auth with completed register flow and guard, owner-scoped course listing/detail (PR #79), the four-value material status vocabulary available at API level, async-state kit, delete confirmation primitive.

**Category 2 — Implemented routes that need a substantial presentation redesign (Phase 4, with 2.2's content settlement first).** Every one of the nine routes is in scope for redesign per owner decision B, with the structural center of gravity at: `/` and `/dashboard` (2.2 settles content honesty first — hero copy, real metrics, role-aware heading, truthful nav label), `/courses/[id]` (4.3 composes the hub: header + actions, materials region, reserved slots), the shell (3.3: navigation, user menu, branding, container/header pattern), and the two auth screens + profile (4.1/4.4). The important discipline: 2.2 changes *what surfaces claim*; Phase 4 changes *how they are composed and look*; neither changes route semantics, auth, or contracts.

**Category 3 — Future page families supported by the technical vision; documentation-only now.** Detailed in §9. Each is IA-reserved (hub slot or coverage-matrix row) and becomes a real route/surface only when its contract lands in `docs/openapi.json` and Seyam authorizes the batch. No routes, no placeholders, no speculative clients.

**Category 4 — Aspirational capabilities with unresolved feasibility or product requirements.** Admin UI (the `admin` role is unenforced — `require_admin` has zero call sites; no capability exists to expose); knowledge graph / quizzes / mastery / analytics UI (W21+ per the 44-week plan; no contracts); full i18n/Arabic localization (excluded unless the plan's bilingual-UI scope W37/W41 makes it a frontend requirement — RTL-readiness via logical properties stays); server-side route protection (excluded architecture decision); enrollment-scoped views (W17 dependency). None of these may be represented in the UI or the page map as more than a coverage-matrix row.

### 8.3 What can be structured now at near-zero cost

Three things, all consistent with the roadmap's frozen scope and none requiring new routes or code in 2.1:

1. **Hub-slot reservation discipline (already designed — keep it).** Roadmap §9's region table for `/courses/[id]` is the architecture's most valuable extensibility device: extracted text (W9), search (W10), chunks (W11), citations (W13–14), chat (W15–16), and enrollment entry (W17) each have a named region that Batch 4.3 documents in the batch note and the 3.1 design ADR, and never renders. This is exactly the owner's "future page families without real routes" — it survives contact with the anti-overengineering test because it is documentation, not machinery.
2. **Route-group conventions for future siblings.** If a future family ever needs its own navigation context (e.g., a student learning space distinct from course management), the Next.js App Router answer is a new route group with its own layout — a zero-dependency convention the codebase already uses (`(app)`, `(auth)`). Documenting this as the extension convention (rather than building anything) is sufficient now. Nav link targets do not change until a real capability justifies structure (the roadmap's role-simple navigation rule).
3. **Shared-layout patterns over per-page composition.** The redesign's refine-and-compose strategy (§16) — pattern components proven once and reused (list, form, detail, dashboard) — is itself the architecture: future families compose the same patterns instead of bespoke screens. This is already roadmap doctrine; the IA proposal simply names it as the structural answer to the owner's question.

### 8.4 What would be premature abstraction (explicitly rejected)

A dynamic plugin/discovery system, a generic routing framework, a "feature flag registry," speculative route stubs, empty "coming soon" pages for future families, or any abstraction that consumes the reservation mechanisms' job — all rejected. The frozen §23 sentence remains the test: "if a capability's contract disappeared tomorrow, nothing rendered in the product would change." Nothing proposed here adds rendered surface for unimplemented capability.

---

## 9. Future Page Families (documentation-only until contracts land)

Each family below states why it may be needed, the spec/plan basis, current capability status, its dependencies, and its representation **now** (which is, in every case, documentation-only — no route, no placeholder UI, no client code).

| Family | Why / basis | Capability today | Dependencies | Representation now |
|---|---|---|---|---|
| Extracted-text viewer (per document/page) | Week 9's explicit frontend assignment; v4 spec §20.3 Material Management UI includes document viewing | **None** — no document-content endpoint exists | Backend status-surface expansion (W9); contract shape TBD | Coverage-matrix C row + hub slot (§9); the 2.1 journey's "inspect result" step notes it as future |
| Reprocess control (failed materials) | W9 schedules `POST /materials/{id}/process` (shape TBD) | **None** | Endpoint + role decision | Coverage-matrix C row; failed-state copy in 4.3 names the cause class without a retry button |
| Retrieval search UI | W10 retrieval service; spec §12.2 target RAG pipeline | **None** | Retrieval API + eval set | Hub slot; coverage-matrix C (W10) |
| Chunk inspection panel | W11 chunk-inspection surface | **None** | Chunk read API from `vector_records` provenance | Hub slot; C (W11) |
| Ranked citations / RAG cited answers | W13–W14 contracts; spec §17.2 learning loop | **None** | Ranking provider + RAG contract | Hub slots; C (W13–14) |
| Chat sessions + streaming | W15–16 sessions API + WS protocol (ADR-0009 event protocol); spec §20.3 RAG Chat Interface design | **None** — zero AI-consumer endpoints; LiteLLM is worker-internal | Sessions API + WS contract; Gate 1 at W16 | Hub slot (AI assistant); C (W15–16) |
| Enrollment + student learning flow | W17 enrollment API + permissions; spec §17.1's dormant `enrollments` table exists unused | Model exists; **no API, no authorization use** | Enrollment scoping + chat permissions (W17) | Hub slot (learning entry); student-flow polish C (W17) |
| Student knowledge model / adaptive surfaces (mastery, recommendations, review schedules, adaptive exams) | Spec §14–§16, §17.2 — the product's differentiating core | **None** — research foundations defined (§27), no implementation | SKM/CSP/adaptive engine backends (W21+) | Coverage-matrix Future tier; never UI-reserved beyond that |
| Analytics dashboard | Spec §20.3 Analytics Dashboard design; W34–35 | **None** | Analytics API surface | No reservation needed now (roadmap §8 note); Future tier |
| Admin contexts | v4 spec mentions admin role; roadmap §22 excludes admin UI | Role unenforced; `require_admin` unused; no admin capabilities defined | Backend must define + enforce first | Excluded (tier E); revisit only on backend evidence |

The families' IA placement is deliberate: **everything learning-shaped attaches to the course-detail hub** (the §9 design), because that is where the user already is when material content becomes consumable. Nothing needs a top-level route until a family grows enough to warrant its own navigation context (§8.3's convention).

---

## 10. Design References — Shortlist for Owner Review

### 10.1 What the repository documents today

**No design-reference or inspiration-project selection exists in the repository's curated documentation.** `docs/research/README.md` states the curated research set is OCR.md only, and that the topic stubs (including *CompetitorAnalysis*) were removed in the 2026-08-16 foundation cleanup. A raw, explicitly non-authoritative AI-generated competitive snapshot exists at `docs/research/raw/ai-reports/Competitive analysis/Competitive Analysis for OpenLearn AI.md` (research snapshot 2026-08-07) listing adaptive-courseware vendors (Carnegie Learning, Knewton, ALEKS, CENTURY, Area9, Cerego, Sana), AI tutors (Khanmigo, Quizlet AI, Duolingo Max), and open infrastructure (OLI Torus, OATutor, ASSISTments, Moodle) — its own header says "Research documents inform decisions; they are not implementation authority," and it is positioned as raw material. **No inspiration project was selected by the owner in any tracked record**, and nothing here claims otherwise.

### 10.2 Recommended shortlist (five references; the owner finalizes the set)

The shortlist is chosen for what this redesign actually needs in Phases 2–4: an honest content architecture for course + document workflows, a role-aware shell, and an Arabic-first/RTL-ready education product. Each entry names the precise pattern worth studying, the OpenLearn need it addresses, what not to copy, and any capability dependence.

1. **LearnHouse** — open-source LMS; https://github.com/learnhouse/learnhouse (docs: https://www.learnhouse.app/). *Stack twin:* Next.js + FastAPI + PostgreSQL (+ Redis), MIT-licensed, self-hostable. *Pattern worth studying:* how a modern Next.js LMS organizes course management versus learning activity, and its dashboard/course-shell composition for instructor versus student roles; also useful as a reality check on API-driven LMS IA at OpenLearn's scale. *OpenLearn need:* course/list/hub IA and role-aware shell. *Do not copy:* its full LMS breadth (authoring tools, course players) — those are capabilities OpenLearn has not built; also its visual identity (the owner's decision B wants a distinct treatment). *Capability dependence:* none for the IA patterns themselves.
2. **NotebookLM** (Google) — https://notebooklm.google.com/ (feature overview: https://blog.google/innovation-and-ai/models-and-research/google-labs/notebooklm-student-features). *Pattern worth studying:* the **source-grounded document journey** — add sources → visible processing/understanding state → study surfaces (guide, FAQs, notes) grounded in those sources with citations. This is the closest mainstream analogue to OpenLearn's upload → processing → resulting-state journey, especially its honest "grounded in your sources" framing and inline-citation linking. *OpenLearn need:* the material lifecycle UX (§10 of the roadmap) and, later, the citation-grounded learning surfaces (W13–16). *Do not copy:* its chat-first composition (OpenLearn's pipeline exposes only the four-value status today; no chat endpoint exists) and any processing-progress richness beyond what the status literal supports. *Capability dependence:* citation/chat patterns depend on W13–16 contracts — study now, build later.
3. **Google Classroom** — https://classroom.google.com/. *Pattern worth studying:* **role-aware simplicity** — the same surface adapts between teacher and student contexts with minimal chrome; "Classwork"/"Materials" organization shows how upload-and-organize flows stay legible for non-technical instructors; stream-vs-classwork separation mirrors OpenLearn's "course record vs course hub" split. *OpenLearn need:* the 3.3 shell and the instructor/student presentation split (2.2/4.2/4.3). *Do not copy:* its Google-ecosystem assumptions (Drive integrations, notification fabric) and its flatness where OpenLearn needs a content hub. *Capability dependence:* none.
4. **Moodle 4.5 course page** — https://moodle.org/ (course-page pattern docs: https://docs.moodle.org/405/en/Course_page). *Pattern worth studying:* the **course page as activity hub with a course-index sidebar** and fenced activity regions — the closest open-source analogue to OpenLearn's hub-slot design; its "activity completion"/status presentation is a mature example of communicating backend state honestly. *OpenLearn need:* 4.3's hub composition and region discipline. *Do not copy:* its density and legacy visual language (the anti-cliché constraints in Phase 3 explicitly forbid that direction), nor its plugin ecosystem mindset. *Capability dependence:* none for layout patterns.
5. **Edraak** — https://www.edraak.org/ (background: https://qrf.org/en/who-we-are/affiliated-organizations/edraak). *Pattern worth studying:* **Arabic-first education at scale** — a pan-Arab MOOC (edX-based, Queen Rania Foundation, 10M+ learners) whose entire learning experience is native Arabic RTL: course cards, enrollment flow, and content layout designed RTL-first rather than mirrored LTR. *OpenLearn need:* the Arabic-first/RTL behavior the owner requires (decision B) — concrete validation that the token layer's Arabic font fallback + logical-properties discipline needs an RTL-native composition reference, not just a mirroring pass. *Do not copy:* its MOOC content model (OpenLearn has no enrollment yet) and its branding. *Capability dependence:* RTL layout patterns are usable now; enrollment flows are W17-dependent.

Two further products were considered and **not** shortlisted, with reasons recorded for transparency: **Khan Academy** (excellent mastery/progress honesty, but its mastery UI implies the SKM capabilities OpenLearn has not built — better revisited when W21+ nears) and **Canvas LMS** (mature role-aware IA, but heavyweight and its patterns are largely covered by the Moodle + Classroom entries).

How the shortlist should be used: as **inputs to Batch 3.1's design direction and the Phase 4 composition work**, not as templates to replicate; each pattern must pass the roadmap's anti-cliché constraints and the honesty rules before adoption. The final selection is the owner's.

---

## 11. Recommended Demo Journey (proposed default — owner locks the final sequence)

The journey below is the frozen 0.2 candidate (roadmap §19) extended with the owner-adopted materials walk, arranged so the material processing reads as the foundation of the learning experience rather than an isolated technical demo. Readiness ratings use the four values requested: `READY` (verified executable today against the local stack), `PARTIALLY READY` (executable but with known copy/state gaps that later batches close), `NOT READY` (a named batch must land first), `BLOCKED` (a contract or capability does not exist). The journey is the **end-state** walkthrough for Gate C/F dry runs — the first full execution realistically happens after Phase 4 (Batch 5.3's dry run), with partial rehearsals possible earlier as batches land.

**Setup (before the audience arrives; not part of the walkthrough):** start the local stack (§12), provision the instructor account (§14), and prepare the dataset (§13).

| # | Page / route | User & role | User action | Expected visible result | API / data dependency | Readiness | Prerequisite work | Success criterion (dry run) |
|---|---|---|---|---|---|---|---|---|
| 0 | — (setup) | Presenter | Stack up; accounts + dataset ready | `GET /health` 200; Keycloak discovery reachable; front end serving | Local compose + uvicorn + next dev | `READY` (verified documented path; Docker required) | One-time: setup-dev.sh + §14 bootstrap run | All health checks pass in one terminal sequence |
| 1 | `/` | Visitor (not signed in) | Read the landing page | Hero states what the product does today (course management, materials processing working; learning surfaces coming); tiles link only to real destinations | None | `NOT READY` (copy is S2-dishonest today) | Batch 2.2 | No unimplemented capability is named as available; every tile lands on a real surface |
| 2 | `/login` → `/register` | Visitor | Register a fresh account via Keycloak; land back in the app | Keycloak hosted flow; register page gives feedback in every state; auto-sign-in returns to `/dashboard` | Keycloak OIDC + PKCE; JIT local user provisioning | `READY` (1.2 completed register flow verified in code) | None | A brand-new account completes registration without developer help |
| 3 | `/dashboard` | Newly signed-in user | See the personalized home | Real metrics only: course count (0 for a fresh account), profile completeness, recent courses; heading matches the signed-in role; zero "Coming soon" strings | `GET /auth/me`; `GET /v1/courses` (owner-scoped); profile read | `NOT READY` (S1 placeholders present today) | Batch 2.2 | Dashboard shows only real data; fresh account shows honest zero/empty states |
| 4 | `/courses` → `/courses/new` | Instructor (owner) | Create the demo course | Course appears in the owner-scoped list; navbar label reads truthfully | `POST /v1/courses`; `GET /v1/courses` | `READY` for the CRUD flow; `PARTIALLY READY` for presentation (nav label + copy fixed in 2.2) | 2.2 for copy | Course created and visible in the list without developer intervention |
| 5 | `/courses/[id]` | Instructor (owner) | Open the course hub; upload a material (file + title) | Hub shows course info + materials region; upload progresses to the materials list with status `pending` | `POST …/materials/upload-url` + browser PUT to storage + `POST …/materials` (202) | `NOT READY` (materials surface = 4.3; local storage/broker/worker absent — §7.3) | Batch 4.3 + environment decision (§12.3): extended local AI profile (preferred) or staging for this segment | Material appears in the list as `pending` after one upload attempt |
| 6 | `/courses/[id]` (materials region) | Instructor (owner) | Watch processing status | Status transitions `pending → processing → ready` (or honest `failed` with cause-class copy); no fake percentages or phases | `GET /v1/materials/{id}/status` polling; Celery pipeline | `NOT READY` (UI = 4.3; worker environment per §7.3) | Batch 4.3 + environment decision | A terminal status (`ready` preferred) observed within the session; failure path shows honest copy if exercised |
| 7 | `/courses/[id]` | Instructor (owner) | Inspect the resulting state | The hub presents the ready material in context — the place where extracted text, search, and study surfaces will attach (slots documented, not rendered); narrative connects processing to the coming learning experience | Materials list; (future) document-content endpoint | `NOT READY` for content inspection (Week 9 blocker); `PARTIALLY READY` for status+list presentation | Batch 4.3; extracted text = Week 9 authorized batch | The demo narrates the learning connection without rendering any placeholder slot |
| 8 | `/profile` | Instructor (owner) | Complete the profile | Form seeds correctly (F4 fix); save shows readable success in both themes; dashboard completeness metric reflects it afterward | `GET/PUT /v1/users/me` | `PARTIALLY READY` (form works today; the completeness metric on the dashboard is 2.2) | Batch 2.2 for the metric reflection | Profile saved; dashboard shows updated completeness on return |
| 9 | `/courses` | Student (testuser, separate sign-in) | Sign in as the student role; view the course list | Honest empty state (owner-scoped listing — the student owns no courses); no upload affordance anywhere; role-aware heading/label | `GET /v1/courses` (owner-scoped, PR #79 behavior) | `PARTIALLY READY` (empty state exists; role-aware copy is 2.2) | Batch 2.2 for copy/affordances | Student sees their own (empty) list; no instructor affordance is visible or functional |
| 10 | `/courses/[id]` (+ edit, delete) | Instructor (owner) | Edit the course; exercise the delete confirmation (on a sacrificial course) | Edit form re-keyed correctly (F3); delete confirmation dialog; list updates after delete | `PUT/DELETE /v1/courses/{id}` | `READY` | None | Full CRUD loop completes; confirmation dialog appears and works |
| 11 | `/profile` (user menu) | Any | Log out | Clean session end; protected routes redirect to login with `redirectedFrom` | Keycloak logout; cache clear | `READY` | None | Logout returns to a signed-out state; back-navigation stays protected |

**Why this sequence:** it tells the product story — an honest public promise (1), a real account (2), a personalized home (3), the instructor creates and enriches a course (4–7) with the material pipeline as the bridge between "content uploaded" and "learning surfaces to come," the learner identity completes (8), a second role proves data integrity and affordance honesty (9), the CRUD loop proves the foundation (10), and a clean exit (11). The material segment (5–7) sits in the middle of the story, connecting forward to the future learning surfaces rather than ending the demo on a technical operation.

**Meaningful alternatives (for the owner's choice):**
- *Shortened 8-step variant* (time-boxed demos): steps 1→2→3→4→8→10→11, with the material walk narrated on the roadmap slide instead of performed — honest because it claims nothing unimplemented, but it loses the owner-required journey; use only if the walkthrough window cannot cover 5–7 after 4.3 lands.
- *Staging-hybrid variant*: run steps 5–7 against staging while everything else stays local — viable because staging runs the full pipeline, but it fragments the demo across two environments and makes the demo depend on staging availability, which owner decision A declines as a default. Recommended only as the 4.3-era fallback if the extended local AI profile is not yet authorized.
- *Role-reverse variant*: lead with the student account and honest emptiness, then the instructor — stronger "data integrity" narrative, weaker product story. A taste of this is already step 9.

**Remaining choices that require the owner:** (1) lock the final sequence (default proposed above); (2) approve the dataset (§13); (3) choose the material-segment environment at 4.3 planning time (extended local AI profile vs staging fallback — recommended: extended local profile, as it honors decision A); (4) approve/adjust the design-reference shortlist (§10); (5) confirm the 1.4 addendum wording (§4).

---

## 12. Environment Plan — Local-First Runbook

Everything below is from the repository's own documented setup (`docs/development/LOCAL_SETUP.md`, `scripts/setup-dev.sh`, `infra/docker-compose.dev.yml`), re-verified against the files at `60d3ba5`. No secret values are reproduced anywhere in this report; the only credentials named are the repository's intentional, non-secret local defaults.

### 12.1 Prerequisites (verified documented)

| Requirement | Version / note |
|---|---|
| Git | any recent |
| Docker + Compose v2 | Docker 24+ recommended; working daemon required (the executing sandbox has none — see §16) |
| Python | **3.12.x exact** (matches CI) |
| Node.js | ≥ 20 (CI targets Node 20; recorded execution deviations used Node 24 — noted per-batch in the ledger) |
| npm, curl, Bash | bundled / any recent |
| AI API keys | **None required** — all PAL providers default to `mock` for the operations the demo exercises |

### 12.2 Reproducible local run (owner machine)

1. **One-command setup:** `bash scripts/setup-dev.sh` from the repository root — idempotent, branch-independent, never mutates git, never destructive to data. Phases: preflight → repository check → environment files (creates `backend/.env`, `frontend/.env.local`, root `.env.local` with a generated `OPENLEARN_TEST_USER_PASSWORD` — written to the file, never printed) → Docker infrastructure → backend venv (`requirements.txt` + dev; large torch/docling install) → frontend `npm ci` → `alembic upgrade head` → verification.
2. **What keeps running:** `db` (`pgvector/pgvector:pg16` on 5432; user `openlearn`; databases `openlearn`, `openlearn_dev`, `keycloak`; named volume `postgres_data`) and `keycloak` (26.7.3 on 8080; realm `openlearn` imported from `infra/realm-export.json` on first start; console `admin`/`admin` at `http://localhost:8080/admin` — intentional dev defaults; volume `keycloak_dev_data`). The `keycloak-bootstrap` one-shot enables registration and creates/updates `testuser` (role `student`) plus — after this batch's patch — the `instructor` account (§14).
3. **Backend:** `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`; confirm `curl http://localhost:8000/health`; interactive docs at `/docs`.
4. **Frontend:** `cd frontend && npm run dev`; open `http://localhost:3000`. Configured via `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`) and the Keycloak public vars.
5. **Availability confirmation for the demo:** backend `/health` returns 200; Keycloak OIDC discovery responds; the web app loads and `testuser` can sign in (a scripted preflight already exists: `scripts/run-batch-0.1-local-verification.sh` re-verifies the same contract end to end, including the E2E trio when credentials are set).

### 12.3 Known environmental gaps and fallback behavior

- **Material pipeline services are absent locally** (no S3-compatible storage, no Redis, no worker — §7.3). Until an authorized "local AI profile" batch adds a compose profile (MinIO + Redis + worker), steps 5–6 of the journey cannot run locally; the documented fallback for that segment is staging (optional per owner decision A), and the recommended target is the extended local profile.
- **First-run heaviness:** the backend venv install is large (torch/docling); plan the demo machine setup ahead of time, not live.
- **Restart/teardown:** the setup script never drops data; `docker compose -f infra/docker-compose.dev.yml stop|start` pauses/resumes the stack; `down` removes containers but keeps both named volumes (reset behavior per §13 — full reset is an explicit, manual action).

### 12.4 Staging as the optional environment

Staging remains reachable for selective use (deployment pipeline live; CORS origin list already includes `http://localhost:3000`; the local-origin preflight passed on 2026-10-14). Under owner decision A it is never a demo prerequisite; the staging-host CORS confirmation (ledger Open Question #2) stays optional evidence, producible anytime via the existing script's `--with-staging-preflight` flag from a staging-reachable host. Staging carries **shared** state: any demo data created there must follow §13's hygiene rules (never production content, no shared-account mutation).

---

## 13. Dataset Plan (smallest realistic, non-sensitive)

Per roadmap §19 there is deliberately **no seed script**: demo data is real data created through the real product flow, with the steps documented and rehearsed. The dataset below is the minimum that supports the complete target journey (§11).

| Element | Quantity | Details |
|---|---|---|
| Demo users | 2 | `testuser` (role `student`; exists, provisioned by bootstrap; password from `OPENLEARN_TEST_USER_PASSWORD` in root `.env.local`) and `instructor` (role `instructor`; added by this batch's provisioning, §14; password from `OPENLEARN_INSTRUCTOR_USER_PASSWORD`) |
| Courses | 3 | Owned by `instructor`; meaningfully titled (e.g., a real subject the presenter can speak to). Optional variant: one Arabic-titled course to exercise the token layer's Arabic font fallback and the RTL-readiness of card/detail layouts during the demo's Q&A |
| Course–ownership relations | 3 | All courses owned by `instructor`; `testuser` owns none — this is what makes step 9's honest empty state and the PR #79 scoping visible |
| Learning materials | 1–2 | Small, non-sensitive, **text-rich PDFs** (text-rich keeps the pipeline off the OCR path via the 50-char gate and exercises Docling → chunking → local BGE-M3 embeddings). One primary material for the `ready` path; optionally a second to show list state. A scanned-PDF "honest failure" variant is possible but not recommended for the demo (the ledger records OCR quota-blocked fixtures — the failure path is not reliably reproducible) |
| Expected processing outcomes | 2–3 states | `pending` on registration; `processing` while the worker runs; `ready` for a healthy text-rich PDF; `failed` only if deliberately exercised with honest cause-class copy |
| Profile completion | 1 | `instructor` (or the walkthrough account) completes the six-field profile so step 8's completeness metric has a real transition to show |

**Setup procedure (documented, repeatable):** (1) stack up per §12.2; (2) sign in as `instructor`, create the three courses through `/courses/new`; (3) complete the profile; (4) upload the material(s) once the materials surface exists (4.3) — before 4.3, this step is impossible by design and the demo narrates it as scheduled scope. **Reset:** demo data lives in the `postgres_data` volume; per-batch reset is manual (delete created courses/materials through the UI — the CRUD loop is itself honest demo material), and the full reset is dropping the two compose volumes and re-running setup (explicit, destructive-by-intent, owner-machine only). Nothing in the dataset depends on production or shared-staging content; nothing is fabricated through back channels.

**Cannot currently be reproduced locally (documented, not worked around):** the processing pipeline execution (§7.3) — storage, broker, and worker services do not exist in the local compose until an authorized profile batch adds them.

---

## 14. Instructor Test Account — Verified State and Provisioning Design

**Verified current state (no instructor account exists):** `infra/dev/bootstrap-keycloak.sh` provisions exactly one user — `testuser` / `test@example.com`, enabled, email verified, role `student`, password set from the `OPENLEARN_TEST_USER_PASSWORD` environment variable (generated into root `.env.local` by `setup-dev.sh`, never printed, never tracked). The realm (`infra/realm-export.json`, imported on first Keycloak start) already defines the `instructor` realm role alongside `student` and `admin`, so no realm change is required. A user registered through the UI would also need a role assigned manually — which is why the scripted account is the right mechanism for a repeatable demo.

**Provisioning added by this batch's patch (idempotent, mirroring the `testuser` pattern exactly):**

1. `infra/dev/bootstrap-keycloak.sh` — after the `testuser` block, an `instructor` block: ensure user `instructor` (`instructor@example.com`, enabled, email verified), set password from `OPENLEARN_INSTRUCTOR_USER_PASSWORD`, `add-roles` `instructor`. Same kcadm mechanics, same idempotency (create-if-missing, update-if-present), same logging style.
2. `infra/docker-compose.dev.yml` — the `keycloak-bootstrap` service passes `OPENLEARN_INSTRUCTOR_USER_PASSWORD` through (same `${VAR:?…}` requirement style as the existing test-user variable).
3. `scripts/setup-dev.sh` — when creating `.env.local` fresh, a generated `OPENLEARN_INSTRUCTOR_USER_PASSWORD` is written alongside the test-user one; when `.env.local` already exists without the new variable (the owner's current machine), the script **appends a generated value and says so** — deliberately friendlier than the test-user check's hard failure, because the instructor account is new and existing setups must not break.
4. `docs/development/LOCAL_SETUP.md` — a short "demo accounts" section documenting both accounts, their purpose (instructor = course-owner for the materials journey and role-visibility checks), and the reset path (re-running bootstrap resets both passwords to the current `.env.local` values).

**Purpose and hygiene (per owner decision E):** a dedicated, repeatable, non-production local/demo account that owns the demo courses; it never touches shared staging state or production; passwords live only in the git-ignored root `.env.local`; no secret appears in this report, the patch's documentation, or any tracked file.

**Honest execution status:** the provisioning change is implemented and reviewable, but **not executed in this sandbox** (no Docker daemon — the same environmental limitation recorded since Batch 0.1). First execution is an owner-machine step: re-run `bash scripts/setup-dev.sh` (or `docker compose -f infra/docker-compose.dev.yml up keycloak-bootstrap`), then sign in as `instructor` once to trigger just-in-time local provisioning. A manual fallback (three `kcadm.sh` commands against the local console, documented in LOCAL_SETUP.md) covers any setup where the compose path is inconvenient.

---

## 15. Scope Assessment — Does This Work Belong in Phase 2?

**Verdict: yes — with explicit boundaries.** Roadmap v2.0 §14 defines Batch 2.1 as exactly this work ("Lock journey, page inventory, environment, and dataset procedure"), Phase 2's stated purpose is to lock the demo surface and make it honest, and Gate C cannot be evaluated without the runbook, the instructor test user, the materials-walk decision, and the confirmed environment/dataset. The owner's instinct to demand this discovery before page design begins matches the roadmap's own dependency table ("Gate B closure set → Phase 2 entirely" and "Batch 0.1 results → 2.1 environment choice"). The recommended boundaries:

**Must be decided now (before Phase 3 design starts):**
1. The demo environment principle: local-first (decided — decision A; reconciliation wording listed in §5.2).
2. The journey's shape and whether the materials walk joins it (decided — decision D; proposed sequence in §11 awaiting the owner's lock).
3. The redesign surface itself: the nine-route inventory as confirmed (§6) — this is what Phases 3–4 will redesign, and freezing it prevents scope drift.
4. The honest-surface direction for 2.2 (what the dashboard and landing claim: §6's per-route recommendations + the 1.4 metric inventory) — 2.2 cannot start without this.
5. The instructor test account and dataset procedure (§13/§14) — prerequisites for 4.3's walkthrough and 5.1's affordance checks, named in the roadmap's dependency table.
6. The design-reference shortlist (§10) — inputs to 3.1; the owner finalizes.

**Documented as future architecture without implementation (this batch does exactly that):**
- The future page families and their hub-slot/coverage-matrix reservations (§9) — documentation-only until contracts land.
- The route-group extension convention (§8.3) — a documented convention, not code.
- The roadmap wording reconciliation list (§5.2) — recorded now, executed in a later authorized documentation batch.

**Deferred to named later batches (already scheduled; nothing new invented):**
- Copy/content honesty: Batch 2.2 (S1, S2, role-aware copy, nav label).
- Visual execution and page composition: Batches 3.1–3.3 (tokens, primitives, shell) and 4.1–4.4 (all nine routes) — per owner decision B and the roadmap's phase split.
- The materials surface: Batch 4.3, consuming the existing contract only.
- The possible "local AI profile" (MinIO + Redis + worker compose profile) for a fully local material walk: a **new small infrastructure batch** proposed for authorization before 4.3 planning, if the owner prefers the local path over the staging fallback.
- Staging promotion and the final dry run: Batches 5.2/5.3, with titles re-scoped per §5.2/R3.

**Out of scope entirely (frozen exclusions, unchanged):** new backend capabilities or endpoints; admin UI; i18n/localization framework; plugin/discovery systems or speculative routes (§8.4); any UI implying chat, quizzes, citations, graph, or progress beyond the status literal; authentication/authorization/business-behavior changes; production or shared-staging mutations.

One honest caveat for the record: the full *lock* that Batch 2.1's completion criterion describes ("journey order fixed; dataset steps documented and rehearsed once") has two halves in this delivery — the decisions and runbook are delivered here, while the **rehearsal** requires the owner machine (Docker + first bootstrap run + a scripted walk-through). The ledger entry records exactly that split, so Batch 2.1 remains open on the rehearsal step until the owner executes it, with everything else staged for Gate C.

---

## 16. Verification Record for This Batch

**Executed in this environment (2026-10-18):**

- Git preflight: fetch, remote/HEAD verification, commit-content byte-identity against the delivered 1.4 closeout patch, worktree creation at `60d3ba5`, preservation checks on the execution clone and stash (§2). No reset/rebase/force-push/discard anywhere.
- Full read of the governance trio (lifecycle rules, ledger at `60d3ba5`, roadmap DOCX extracted via `python-docx`), the 0.2 decision note, the v4 spec's governing sections, `LOCAL_SETUP.md`, `docs/environments.md`, and targeted 44-week-plan passages.
- Source-level verification: the complete frontend route tree (nine `page.tsx` counted), all layouts/boundaries, Navbar/AuthGuard/CourseCard/auth components, dashboard/landing/courses/profile page implementations (S1/S2 findings re-confirmed present in code), feature-slice absence of any materials code (four grep hits are the mislabel strings), backend `storage.py`/`material_service.py`/`course_service.py`/`deps.py`/`celery_app.py`, dev compose service list, realm export roles, bootstrap script, `.env.example` S3 defaults, and `setup-dev.sh`'s password-handling phases.
- Web verification of the design-reference shortlist's primary sources (LearnHouse repository/site, NotebookLM official feature pages, Edraak institutional pages).

**Cited, not re-run (evidence exists at the recorded commits):** the frontend/backend test matrices (frontend unit 54/54 including the F5 file 17/17, lint/typecheck, Storybook 42/42, build 9 routes; backend course+contract 32/32; core regression 254 passed / 1 pre-existing environmental docling failure) — re-verified by the 1.4 closeout at `92b67bd` and unchanged by the ledger-only `60d3ba5`; `60d3ba5` touches no application file, so those results stand for this batch's baseline without re-execution.

**NOT RUN in this environment (honest gaps):** any Docker-dependent step — `setup-dev.sh` execution, the Keycloak bootstrap (hence the instructor account's first provisioning), a live local-stack journey rehearsal, and the backend docling-dependent test files (recorded limitation since Phase 2, unchanged). The owner-machine steps that complete Batch 2.1 are listed in §12/§14 and recorded in the ledger entry.

**Deliverables of this batch:**

1. This report — proposed into the repository as `docs/tasks/Frontend UI redesign/OpenLearn-AI_Batch-2.1_Discovery_Demo-Journey_Environment-Lock.md`, and delivered alongside it as this MD file plus a PDF edition for reading.
2. The ledger update: 1.4 owner-confirmed live-API verification addendum (status → EXECUTED with attribution), refreshed Current State, a "### 2.1 — discovery" log entry, an Execution History row, a Status Board 2.1 row, Open Question updates (#2 reclassified optional, #4 answered: local-first, #5 answered: materials walk adopted), and the Next Authorized Batch refresh.
3. The provisioning extension (bootstrap script + compose wiring + setup-dev.sh env handling + LOCAL_SETUP.md section) — implemented, not executed here.
4. The validated patch, generated by the lifecycle rules' isolated-clone method at the batch baseline: `frontend-redesign-2.1-discovery-demo-journey-environment-lock.patch` (exact path reported at delivery).

**Ledger updated:** yes (included in the patch). **No commit, no push** — Seyam reviews and applies. Per the lifecycle rules, this batch stops here; the next batch starts only on Seyam's explicit authorization (recommended next: Batch 2.2 — Honest-surface settlement, whose S1/S2 scope this report has fully grounded).

---

## 17. Open Items for Owner Decision

| # | Item | Recommendation | Where it lands |
|---|---|---|---|
| 1 | Lock the final demo journey sequence | Approve the 11-step default (§11) or adjust | 2.1 completion (runbook lock) |
| 2 | Approve the dataset | Approve §13 (2 users, 3 courses, 1–2 text-rich PDFs; optional Arabic title variant) | 2.1 completion (rehearsal) |
| 3 | Material-segment environment at 4.3 time | Authorize the "local AI profile" infra batch (preferred, honors decision A); staging as fallback | New small batch before 4.3 |
| 4 | Design-reference set | Review the five-entry shortlist (§10); finalize before 3.1 | Batch 3.1 |
| 5 | 1.4 addendum wording | Confirm the attributed owner-confirmation record (§4) | Ledger, included in this patch |
| 6 | Roadmap reconciliation (R1–R9) | Fold into the next documentation batch or a small dedicated amendment batch | Next doc-only batch |
| 7 | Outstanding owner validations | 1.2's owner-machine validation and 1.3's Sentry runtime verification remain open; Gate B still unclaimed | Owner machine, at convenience |
| 8 | Post-ownership UX treatments | "Not your course" 403 state and role-aware affordance language as named inputs to 4.x | Batches 4.2/4.3 planning |
