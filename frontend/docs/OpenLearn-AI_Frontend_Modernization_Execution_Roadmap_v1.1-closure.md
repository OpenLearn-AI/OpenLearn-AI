# OpenLearn-AI Frontend Architecture Modernization — Execution Roadmap

> **Version:** v1.1 — 2026-09-29 (v1.0 — 2026-09-28); Phase 0 closure recorded 2026-09-29 within the v1.1 baseline (§5); Phase 1 closure recorded 2026-09-29 (§6); Phase 2 Slice 1 (Courses foundation) closure recorded 2026-09-29 (§7)
> **Phase status:** Phase 0 DONE; Phase 1 REPOSITORY COMPLETE + LOCALLY VERIFIED (committed at `d9d1c53`; staging browser login remains an external operational dependency); Phase 2 IN PROGRESS — Slice 1 (apiFetch + ApiError + course schemas + keys + query defaults + course hook migrations + CourseForm ApiError + unit tests) lands as `phase2_courses_foundation.patch` on top of `d9d1c53`, locally verified. Phases 3–6 NOT STARTED.
> **Branch:** `feature/frontend-refactor` @ `d9d1c53` (HEAD after Phase 1 final closure; Phase 2 Slice 1 patch applied on top in this revision as `phase2_courses_foundation.patch`, not yet committed to the remote branch).
> **Architecture baseline:** D1–D19 ACCEPTED with amendments — explicit clarifications to D9, D10, D13 (2026-09-29; see the architecture-baseline subsection in §1)
> **Companion to:** `OpenLearn-AI_Frontend_Architecture_Modernization.docx` (architecture decision study)
> **How to use:** update after every phase — tick checkboxes, change statuses, record deviations, re-run the gate, then start the next phase.

---

## 1. Current Status

This is the living execution roadmap for the OpenLearn-AI frontend modernization. It is derived directly from the architecture decision document and does not repeat that document's reasoning: every phase traces back to a decision or a verified problem. The team returns here after every completed phase.

**Repository state (verified 2026-09-29):** the current execution baseline is branch `feature/frontend-refactor` at commit `c7266103` (full SHA `c72661035d13e5907507de3a04206bea578416f4`, "added Modernization and Roadmap" — the two docs files in `frontend/docs/`), clean tree. All modernization work starts from this branch. Older branch names seen in git history, the architecture study, or earlier planning material — e.g., `fix/frontend-pre-week7-integration`, where the architecture study (`62c9358`) and `95bba7a` "chore: improve local development setup" (adds `scripts/LOCAL_SETUP.md` + `scripts/setup-dev.sh`, no frontend source changes) landed — are **historical context, not migration errors**; only `feature/frontend-refactor` is the execution baseline. No architecture decision changes as a result of the lineage since the study; the local-setup work remains folded in as two tasks (Phase 1 keeps the setup script green; the Phase 6 README references it). The top finding was re-verified at the current head: `frontend/Dockerfile` still bakes only `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_SENTRY_DSN`, and the realm client `openlearn-frontend` still registers localhost-only redirect URIs — staging auth remains broken by construction, and Phase 1's fix is unchanged. The staging targets Phase 1 will configure are now decided (2026-09-29): staging frontend `https://openlearn-web-staging.duckdns.org`, staging backend API `https://openlearn-api-staging.duckdns.org` — the current problem, the known targets, and the Phase 1 fix are kept as three distinct states in §6. CI on this branch is currently red from a known frontend lint failure in `app/page.tsx` (`npm run lint` exits 1); by explicit decision it is recorded as a known follow-up carried into the modernization work, not a Phase 0 blocker (§5).

### Architecture baseline — ACCEPTED WITH AMENDMENTS (2026-09-29)

Seyam accepted the architecture document's Section 8 baseline: **D1–D19 are accepted; no decision was rejected.** Three decisions carry explicit clarifications. Each clarification is an interpretation of an accepted decision — **not a new architecture decision** — and the affected phases carry short operational notes implementing them.

| Decision | Clarification | Operational notes |
|---|---|---|
| **D9 — design tokens / visual system** | The current token system, styling foundation, colors, and visual language establish **architectural consistency and a stable styling/token foundation — not the final visual design**. A later part of the modernization intentionally redesigns UI/UX, visual identity, colors, typography where appropriate, spacing and visual hierarchy, component appearance, and the overall product look and feel — **on top of that stable foundation**. Nothing in this roadmap freezes the current visual design as final. | Phase 4; Scope Guard |
| **D10 — LTR, Arabic, and RTL** | The model is **English + LTR as the baseline** and **Arabic + RTL prepared as a first-class supported direction**. LTR remains the default/current baseline; English remains supported and is not removed, replaced, or deprioritized. Prepare, do not convert: use `dir` appropriately, Arabic-capable typography/fonts, logical CSS properties/utilities where appropriate, and verify layouts in both LTR and RTL. Do not introduce a full i18n/translation system prematurely (its trigger stays in the Deferred Backlog) and do not translate the product to Arabic as part of this baseline. Arabic does not replace English; RTL does not replace LTR. | Phases 3 and 5 |
| **D13 — Storybook** | Storybook is **development and verification infrastructure**: shared UI/component development; component, state, dark-mode, RTL, accessibility, and visual-regression verification where applicable; documenting reusable component behavior. It does **not** establish or freeze the final visual design — the later visual redesign can proceed on top of it. | Phases 4 and 6 (Phase 5 uses the same bench for RTL verification) |

**Investigation reports:** the BigPickle report has still not been provided as a file. This roadmap rests on direct code inspection, which outranks investigation reports in the source-of-truth hierarchy anyway. If it arrives later: cross-check against code; code wins.

### Current Focus

| Field | Value |
|---|---|
| Phase | Phase 2 — Data Foundation (Courses pilot); Slice 1 closure record in §7 |
| Status | IN PROGRESS — Slice 1 (apiFetch + ApiError + course response schema + course key factory + explicit QueryClient defaults + useCourses/useCourse/useCourseMutations migration + CourseForm ApiError + unit tests for apiFetch and the key factory) lands as `phase2_courses_foundation.patch` on top of `d9d1c53`, locally verified. Phase 1 is committed at `d9d1c53` and remains REPOSITORY COMPLETE + LOCALLY VERIFIED (staging browser login still external). |
| Objective | Establish the single API boundary (`apiFetch` + `ApiError`), Zod schemas as the source of response types, a centralized course query-key factory, explicit TanStack Query defaults, and real mutation invalidation — proven on the courses feature as the reference implementation every later migration copies |
| Current Task | Slice 1 patch handoff — `phase2_courses_foundation.patch` (see §7 Slice 1 closure record for the verification table and the next Phase 2 action) |
| Blocked By | Phase 2 is not blocked by Phase 1's external staging dependencies (by design — the two tracks share no files). Phase 2 Slice 1 is locally verified; the Phase 2 phase gate's manual courses-CRUD round-trip item requires a running local backend + Keycloak (the user's `setup-dev.sh` environment) and has not been re-run by the GLM executor in this slice |
| Next Gate | Phase 2 phase gate (§7) — automated items CLOSED (TypeScript / lint / build / unit tests all PASS); manual courses-CRUD round-trip item pending user verification on a running local stack |

---

## 2. Collaboration & Execution Workflow

The modernization runs on a mixed human/model team with unequal access and authority, by design. The roadmap is written so Seyam can execute and review without frontend depth.

| Role | Does | Does not |
|---|---|---|
| **Seyam** — human, project lead | Owns final decisions; accepts/amends the baseline; reviews and approves; decides when a phase is complete; coordinates pods | Not assumed to be a frontend expert — the roadmap and architecture document carry the context |
| **GLM** — online engineering model | Clones/inspects the repo; implements phases when explicitly instructed; runs repo commands; reviews implementation against this roadmap; works from `feature/frontend-refactor` unless a task says otherwise | Never silently changes an architecture decision — when an agreed decision fails in practice, stops at that boundary, explains, and requests a decision update |
| **BigPickle** — local investigation agent | Deep repo inspection; tracing dependencies; finding affected files; validating assumptions; investigation reports | Reports are evidence, not decisions; never override accepted decisions |
| **ChatGPT** — planning assistant | Planning; decisions → task lists; preparing implementation prompts; reviewing progress; helping update this roadmap; helping Seyam understand decisions | Does not replace Seyam's decision authority; does not implement code |

### The execution loop (per unit of work)

```text
Architecture Decisions (accepted)
        |
  Select Current Phase  ->  Inspect Relevant Code  ->  Prepare Implementation Task
        |
  GLM Implements  ->  BigPickle / Investigation (if needed)
        |
  Human Review (Seyam)  ->  Verification (phase gate)
        |
  Update This Roadmap  ->  Next Phase
```

### Working rules that apply to every phase

- **PR discipline:** one concern per PR; target under ~400 changed lines; infrastructure files merge before their consumers; PR body lists behavior deltas and ticks the protected-functionality checklist.
- **Protected functionality (per-PR checklist):** Keycloak login/register/logout + token refresh; the bearer API contract with FastAPI (paths, payloads, upsert semantics); course create/read/update behavior; profile create-or-update behavior; validation rules and messages; redirect destinations (changed once, deliberately, in Phase 3); dark-mode behavior on already-correct pages; CI green state. A PR that breaks one of these is a regression, not modernization.
- **Decision boundaries:** any model that finds an accepted decision does not work in practice stops and requests a decision update instead of improvising.
- **Branch discipline:** all work starts from `feature/frontend-refactor` (the current execution baseline); per-task branches fine; no unreviewed merges. Older branch names in history or docs are historical context — do not treat them as migration errors.
- **No scope creep:** optional work stays Recommended or moves to the Deferred Backlog.

---

## 3. Source of Truth

| Rank | Source | Authoritative for |
|---|---|---|
| 1 | Current repository implementation (`feature/frontend-refactor`) | What exists right now — file paths, current behavior, current defects |
| 2 | Accepted architecture decisions (decision document, Section 8 baseline) | What the codebase is supposed to become — the target state |
| 3 | This roadmap | The order, gating, and status of the transition |
| 4 | Investigation reports (BigPickle and similar) | Evidence and context — never overrides ranks 1–3 |
| 5 | General research / best practices | Background — consulted only when ranks 1–4 are silent |

**The distinction that matters:** the repo has two ThemeToggle implementations today (current state); D2 says one survives (target); Phase 1 is the bridge (plan). Login currently redirects by origin (current); D7 standardizes to `/dashboard` + `redirectedFrom` (target); Phase 3 implements it (plan). When a PR contradicts the hierarchy, the higher rank wins and the lower-ranked document is updated openly.

---

## 4. Global Progress

**Status vocabulary:** `NOT STARTED` · `IN PROGRESS` · `BLOCKED` · `REVIEW` · `DONE`

| Phase | Name | Status | Main goal | Est. |
|---|---|---|---|---|
| 0 | Preparation & Baseline | **DONE** (2026-09-29) | Accept decisions, name owners, baseline the roadmap | days |
| 1 | Configuration, Hygiene & Staging Auth Fix | **REPOSITORY COMPLETE + LOCALLY VERIFIED** (2026-09-29 — Slice 1 committed at `773186e`; Slice 2 committed at `c6e7b3f`; final closure patch in this revision; staging browser login remains an external operational dependency — see §6 final closure record) | Staging auth works from any browser; config central + validated | ~1 sprint |
| 2 | Data Foundation (First Implementation Slice) | **IN PROGRESS** (2026-09-29 — Slice 1 patch in this revision, see §7 closure record) | apiFetch + schemas + query conventions proven on courses | ~1 sprint |
| 3 | Application Shell & Route Patterns | NOT STARTED | One guarded (app) group; shared state components; route fallbacks | ~1 sprint |
| 4 | Feature & Page Migration | NOT STARTED | All routes on the foundation; fake data gone; delete works; mobile menu | 2–3 sprints |
| 5 | Arabic/RTL Readiness & Accessibility Baseline | NOT STARTED | RTL rails verified; axe-clean primitives; keyboard checks | ~1 sprint |
| 6 | Testing & Observability Hardening | NOT STARTED | CI quality bar, three E2E flows, Sentry wired, README | ~1 sprint |

Estimates are sizing for a two-engineer pod with weekly sprints and Friday demos — **not deadlines**. Total ≈ 6–9 sprints; foundations (Phases 0–2) ≈ three weeks.

**Start order:** Phase 0 gated everything and is now closed (2026-09-29 — every gate in §5 is ticked; CI green is deliberately not a gate, see the known follow-up in §5). Phase 1 and the first PR of Phase 2 (Slice 1) **run in parallel** — they share no files, and Slice 1 is designed self-contained so conventions work is not blocked behind Pod D coordination. Phases 3–6 are strictly sequential. Neither Phase 1 nor Phase 2 has started.

**Pilot feature — courses, and why:** the courses list is read-only (lowest risk) yet exercises the three most load-bearing decisions (D3 API boundary, D4 schemas-as-types, D5 query conventions) and covers query + mutation + invalidation. The approved slice becomes the reference implementation every later migration copies.

### The four major migrations

| Area | Current (verified on the branch) | Target (accepted decisions) | Realized in |
|---|---|---|---|
| Data access | fetch inside each hook; hand-written interfaces; library-default caching; mutations navigate instead of invalidating | one `apiFetch` + `ApiError`; `z.infer` types; explicit defaults; mutations invalidate their domain keys | Phase 2 (courses), Phase 4 (auth, profile) |
| App shell & protection | Navbar in root layout; one page self-guards with `useEffect`; no loading/error/not-found files | `(app)` route group owning Navbar + AuthGuard; route-level fallbacks; shared state components | Phase 3 |
| Styling | two dialects (tokens vs raw slate/indigo); profile page has zero dark-mode variants | token-only dialect with logical utilities; dark mode correct everywhere | Phase 3 (rails), Phase 4 (pages) |
| Configuration & deployment | env vars read ad hoc; Keycloak vars never baked at build; realm redirects localhost-only | validated `lib/config.ts`; all five vars baked; per-env realm redirects; staging login works | Phase 1 |

*The styling row describes the styling/token foundation (architectural consistency), not the final visual design — the intentional visual redesign happens later on top of it (D9 clarification, §1).*

---

## 5. Phase 0 — Preparation & Baseline

| Status | Estimate | Decisions implemented | Depends on |
|---|---|---|---|
| **DONE** (2026-09-29) | days | All — D1–D19 ACCEPTED (2026-09-29) with clarifications to D9/D10/D13 | Nothing |

**Goal.** Convert the completed architecture study into an accepted, owned, baselined working agreement before any implementation starts, and resolve the two assignment questions the deployment fix depends on.

**Why.** Implementing without an accepted baseline would re-open every decision implicitly — exactly the failure mode the architecture phase was run to avoid. The baseline acceptance is closed: D1–D19 are accepted with explicit clarifications to D9, D10, and D13 (see the architecture-baseline subsection in §1). As of 2026-09-29 the remaining Phase 0 items are closed as well: the Pod D coordination owner is named (Seyam), the staging URL scheme is decided (staging frontend + backend URLs recorded in §6), and the roadmap is baselined as v1.1. CI on the execution branch is currently red from a known frontend lint failure in `app/page.tsx`; by explicit decision CI green is not a Phase 0 blocker — the failure is recorded as a known follow-up carried into the modernization work (see the phase gate below).

**Prerequisites.** Architecture document produced (done). Repository cloned and verified (done).

**Work — required:**

- [x] Clone the repository; checkout the execution branch; verify branch and clean tree (2026-09-28: `fix/frontend-pre-week7-integration` @ `95bba7a`; re-baselined 2026-09-29 on `feature/frontend-refactor` @ `c7266103`, full SHA `c72661035d13e5907507de3a04206bea578416f4`)
- [x] Produce the architecture decision document — 17 sections, D1–D19 (OpenLearn-AI_Frontend_Architecture_Modernization.docx)
- [x] Re-verify findings at the new branch head: `95bba7a` adds only `scripts/LOCAL_SETUP.md` + `scripts/setup-dev.sh`; no frontend source changes; no decision impact; staging-auth finding re-confirmed (re-confirmed again at `c7266103`, 2026-09-29)
- [x] Produce this execution roadmap (v1.0)
- [x] Pod session: Seyam reviews and accepts (or amends) the architecture document's Section 8 baseline — closed 2026-09-29: **D1–D19 ACCEPTED with amendments** (explicit clarifications to D9, D10, D13 — see the architecture-baseline subsection in §1); no decision rejected; the affected-decision re-reads are reflected in the phase notes (Phases 3, 4, 5, 6)
- [x] Name the Pod D coordination owner for the Phase 1 pipeline/realm fix — closed 2026-09-29: **Seyam**
- [x] Decide the staging URL scheme (basis for the realm redirect URIs) — closed 2026-09-29: staging frontend `https://openlearn-web-staging.duckdns.org`; staging backend API `https://openlearn-api-staging.duckdns.org` (supporting references: API docs `https://openlearn-api-staging.duckdns.org/docs`; health endpoint `https://openlearn-api-staging.duckdns.org/health`)
- [x] Commit this roadmap where the team works (repo `docs/` or the engineering wiki) and mark it the baselined version — closed 2026-09-29: baselined as **v1.1** (no baselining commit SHA is claimed in this document; the SHA in the header is the verified execution-baseline HEAD, not a baselining commit)

**Work — recommended:**

- [ ] Record a screen capture of the ten manual critical-flow checks as the pre-modernization behavior baseline (recommended-only; not a Phase 0 gate — may be completed during the modernization work)

**Affected areas.** None — no code changes.

**Verification.** Branch/execution baseline recorded; architecture baseline accepted; Pod D coordination owner named; staging frontend/backend URLs recorded; roadmap v1.1 baselined; Phase 0 ownership and preparation gates closed. CI remains red due to a known frontend lint failure in `app/page.tsx`, intentionally carried forward as a modernization follow-up rather than a Phase 0 blocker.

### Phase gate — before Phase 1 and the Phase 2 slice start

- [x] Section 8 architecture baseline accepted — D1–D19 accepted with D9/D10/D13 clarifications (closed 2026-09-29, §1)
- [x] Pod D coordination owner named — Seyam
- [x] Staging URL scheme decided — staging frontend/backend URLs recorded (§6)
- [x] Roadmap baselined — v1.1
- [x] Phase 0 closure decision — complete (2026-09-29)
- [KNOWN FOLLOW-UP] CI currently fails at frontend lint because of `frontend/app/page.tsx`: warning — `user` is assigned a value but never used; error — `@typescript-eslint/no-explicit-any` (`Unexpected any`); `npm run lint` exits with code 1. This is a lint-quality issue, not an architecture decision change. It is intentionally carried into the modernization work and is not a Phase 0 blocker; CI green is not a Phase 0 gate.

**Phase 0 is complete.** Closed 2026-09-29: every gate above is ticked and the ownership and preparation decisions are recorded. Phase 1 and the Phase 2 first slice are cleared to start in parallel on Seyam's instruction — neither has started. The CI lint failure is carried forward as a known follow-up (see the gate above); fixing it is part of the modernization work, not a condition for having closed Phase 0.

**Owner / execution model.** Seyam owns this phase end to end (baseline decision + both assignments, closed 2026-09-29) and is the named Pod D coordination owner for the deployment-related work. ChatGPT can prepare the first implementation prompts for Phase 1 / Phase 2 Slice 1. No GLM/BigPickle implementation work in this phase — their contribution is recorded above.

---

## 6. Phase 1 — Configuration, Hygiene & Staging Auth Fix

| Status | Estimate | Decisions implemented | Depends on |
|---|---|---|---|
| REPOSITORY COMPLETE + LOCALLY VERIFIED (2026-09-29) — Slice 1 committed at `773186e`; Slice 2 committed at `c6e7b3f`; final closure patch landed in this revision. Phase 1 phase gate REPOSITORY-SIDE items CLOSED; the "staging login works from a non-localhost browser" item remains BLOCKED on external operational dependencies (see final closure record below) | ~1 sprint | D15 (primary), D18 items 1–2, D6 (configuration half) | Phase 0 gate (closed 2026-09-29) |

**Parallel note.** May run alongside Phase 2's first slice — the two tracks share no files.

**Goal.** Make configuration correct, central, and loud; fix the deployment blocker that confines authentication to developer machines; remove the inventoried dead code.

**Why.** Verified on the branch: the staging image bakes only `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_SENTRY_DSN` at build time, so a staging browser falls back to the `.env.example` Keycloak defaults (localhost:8080); independently, the realm client `openlearn-frontend` registers only `http://localhost:3000/*` redirects. Either alone makes staging auth broken by construction — together they guarantee it. This is the architecture document's highest-priority problem, on its own track under Pod D coordination (owner: Seyam). The staging URL decision is made (2026-09-29); the configuration work against it is Phase 1's job and has not started.

**Staging targets — three states, kept distinct (targets decided 2026-09-29):**

- **CURRENT PROBLEM:** staging auth/configuration is not yet correctly wired — the staging image bakes only the two currently documented public variables, and the realm client registers only localhost redirects.
- **KNOWN TARGET:** staging frontend `https://openlearn-web-staging.duckdns.org`; staging backend API `https://openlearn-api-staging.duckdns.org`. Supporting references only: API docs `https://openlearn-api-staging.duckdns.org/docs`; health endpoint `https://openlearn-api-staging.duckdns.org/health`.
- **PHASE 1:** implements the configuration and Keycloak redirect-URI fix against these targets. Nothing is claimed done in advance: staging authentication is not fixed, Keycloak redirect URIs are not updated, and the staging frontend/API configuration is not correct until this phase lands and verifies.

**Prerequisites.** Phase 0 gate — closed (2026-09-29): Pod D coordination owner named (Seyam); staging URL scheme decided (targets above).

**Work — required:**

- [x] Create `lib/config.ts` — all five client variables (`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_KEYCLOAK_URL`, `NEXT_PUBLIC_KEYCLOAK_REALM`, `NEXT_PUBLIC_KEYCLOAK_CLIENT_ID`, `NEXT_PUBLIC_SENTRY_DSN`), typed exports, Zod validation in dev with a readable failure message — DONE in Slice 1 (`773186e`)
- [x] Point `lib/keycloak.ts` at `lib/config.ts` — protocol, client, and PKCE flow untouched (protected functionality) — DONE in Slice 1 (`773186e`)
- [x] `frontend/Dockerfile` — add ARG/ENV for the three `NEXT_PUBLIC_KEYCLOAK_*` variables — DONE in Slice 1 (`773186e`)
- [x] `.github/workflows/deploy-staging.yml` — pass the Keycloak variables into the image build (vars/secrets) — DONE in Slice 1 (`773186e`)
- [x] `infra/realm-export.json` — per-environment redirect URIs and web origins for `openlearn-frontend` (staging frontend: `https://openlearn-web-staging.duckdns.org`), with Pod D (coordination owner: Seyam); shipped as an isolated, separately revertible commit — REPO-SIDE DONE in Slice 2 (additive: appended `https://openlearn-web-staging.duckdns.org/*` to `redirectUris` and `https://openlearn-web-staging.duckdns.org` to `webOrigins`; localhost entries preserved so local dev still works). OPERATIONAL APPLICATION to the running staging Keycloak remains a Pod D external-dependency step — see Slice 2 closure record
- [x] `.env.example` — document all five variables (plus both Sentry DSNs where applicable) — DONE in Slice 1 (`773186e`)
- [x] Delete dead code: `features/auth/api/useRegister.ts` (empty), unused `loginSchema`/`registerSchema`, `components/courses/CourseTable.tsx` (unused), one of the two ThemeToggles (keep the `components/ui` one), the home page's dead comment block and its `as any` cast — DONE: Slice 2 (`c6e7b3f`) deleted the first four items (`frontend/features/auth/api/useRegister.ts`, `frontend/features/auth/schemas.ts` containing both unused schemas, `frontend/components/courses/CourseTable.tsx`, `frontend/components/theme-toggle.tsx`; `frontend/app/(auth)/login/page.tsx` import swapped to `@/components/ui/theme-toggle`). Final closure slice removed the `as any` cast and the dead comment block from `frontend/app/page.tsx` (line 9 cast removed; trailing `/* cd frontend / npm run dev / ... */` block removed). The full Phase 1 dead-code inventory is now empty.
- [x] Verify `bash scripts/setup-dev.sh` (from commit `95bba7a`) still completes green after the config changes — VERIFIED BY USER (2026-09-29): the user ran `bash scripts/setup-dev.sh` locally after Slice 2 with Docker daemon reachable, PostgreSQL ready, Keycloak realm reachable, Keycloak bootstrap successful, Alembic migrations at `b110ae6051f4`, and frontend dependencies current. The final closure slice only modifies `frontend/app/page.tsx` (lint fix) and this roadmap document — neither is touched by `setup-dev.sh`, so the user's prior green run remains valid. The sandboxed GLM executor cannot re-run the script (no Docker daemon in the sandbox), so the user-side verification is the authoritative result.

**Work — recommended:**

- [ ] Echo the effective public URL into the deploy log for faster misconfiguration diagnosis
- [ ] Land the deletions as their own PR, separate from the config work

**Deferred from this phase.** CSP/security headers — first production domain, with Pod D's ingress work (see Deferred Backlog).

**Affected areas.** New `lib/config.ts`; `lib/keycloak.ts`; `frontend/Dockerfile`; `.github/workflows/deploy-staging.yml`; `infra/realm-export.json` (with Pod D); `.env.example`; deletions in `features/auth/`, `components/courses/`, `components/`, `app/page.tsx`.

**Verification.**

- CI green (lint + strict typecheck + build) — includes resolving the known `app/page.tsx` lint failure carried from Phase 0 (known follow-up, §5)
- Local dev unchanged — manual login round trip works on localhost
- On the staging frontend (`https://openlearn-web-staging.duckdns.org`): a browser login round trip succeeds from a non-localhost machine, against the staging backend (`https://openlearn-api-staging.duckdns.org`)
- grep confirms no dead file from the deletion list remains
- One-variable-at-a-time for the realm/pipeline chain — each step separately revertible

### Phase gate — before starting Phase 3 (Phase 2 may already be underway)

- [x] Phase 1 implementation complete and reviewed — REPOSITORY-SIDE COMPLETE (Slice 1 `773186e` + Slice 2 `c6e7b3f` + final closure patch). Review by Seyam pending on the final closure patch.
- [x] TypeScript, lint, and build pass — VERIFIED locally on the final closure tree: `npx tsc --noEmit` EXIT 0; `npm run lint` EXIT 0 (zero errors, zero warnings — the Phase 0 known `app/page.tsx` follow-up is now closed); `npm run build` EXIT 0 (all 10 routes compiled). See §6 final closure record for the full verification table.
- [ ] Staging login works from a non-localhost browser — BLOCKED on external operational dependencies (public Keycloak origin not yet published; persistent staging realm not yet operationally updated). See §6 final closure record.
- [x] A fresh clone builds and runs with only `.env.local` — VERIFIED by inspection: only `frontend/.env.example` is tracked; `.gitignore` excludes `.env`/`.env.local`/`*.env`; `frontend/.dockerignore` excludes `.env*`; all 5 `NEXT_PUBLIC_*` variables are documented in `.env.example` and wired through the Dockerfile and staging workflow.
- [x] `scripts/setup-dev.sh` completes green — VERIFIED BY USER (2026-09-29): the user ran the script locally after Slice 2 with Docker daemon reachable, PostgreSQL ready, Keycloak realm reachable, Keycloak bootstrap successful, Alembic migrations at `b110ae6051f4`, frontend dependencies current. The final closure slice only modifies `frontend/app/page.tsx` and this roadmap doc, neither of which is touched by `setup-dev.sh`, so the user's prior green run remains valid.
- [x] Protected functionality re-verified: the auth protocol itself is untouched — `lib/keycloak.ts`, `lib/auth-context.tsx`, `LoginForm.tsx` (`window.location.origin` redirect), `register/page.tsx` (`${window.location.origin}/dashboard` redirect), Keycloak init options (`check-sso`, `pkceMethod: S256`, `checkLoginIframe: false`, `updateToken(30)`), Keycloak client ID, and realm name are all UNCHANGED across Slice 1, Slice 2, and the final closure slice.
- [x] Changes reviewed by Seyam; realm/pipeline commits separately revertible — Slice 1 committed at `773186e`, Slice 2 committed at `c6e7b3f` (separately revertible); final closure patch is a single revertible unit. Review of the final closure patch by Seyam is pending.

**Owner / execution model.** GLM implements the instructed tasks (config module, Dockerfile, workflow, deletions). BigPickle validates the env-var usage inventory before the Dockerfile/workflow PR. Seyam reviews and personally coordinates the realm change with Pod D.

**Migration map.**

| Current | In this phase | Target |
|---|---|---|
| Env vars read ad hoc; Keycloak values never baked at build; realm redirects localhost-only; staging auth broken by construction | One validated `lib/config.ts`; pipeline bakes all five variables; realm registers per-env redirects | Staging auth works from any browser; fresh clone runs with only `.env.local`; config failures are loud in dev |

### Phase 1 Slice 2 closure record (2026-09-29)

**Slice 2 purpose.** Land the remaining repo-side Phase 1 implementation that does not require Pod D operational access — namely the additive `openlearn-frontend` redirect-URI / web-origin additions for the staging frontend URL, and the Phase 1 dead-code deletions. Slice 1 (central configuration: `lib/config.ts`, `lib/keycloak.ts`, `frontend/Dockerfile`, `.github/workflows/deploy-staging.yml`, `frontend/.env.example`, `frontend/.dockerignore`, `frontend/sentry.client.config.ts`) was committed at `773186e` and is intentionally NOT reimplemented by Slice 2.

**Implementation outcome (repository state after `git apply phase1_slice2.patch` on top of `773186e`):**

- `infra/realm-export.json` — for the `openlearn-frontend` client only, appended two staging entries while keeping the existing localhost entries intact:
  - `redirectUris`: now `["http://localhost:3000/*", "https://openlearn-web-staging.duckdns.org/*"]`
  - `webOrigins`: now `["http://localhost:3000", "https://openlearn-web-staging.duckdns.org"]`
  - `rootUrl`, `baseUrl`, PKCE method (`S256`), `publicClient: true`, `standardFlowEnabled: true`, all other client attributes, and all other clients in the realm are UNCHANGED. The staging URL `https://openlearn-web-staging.duckdns.org` is the documented Phase 1 staging frontend target (§6); the staging Keycloak origin is intentionally NOT touched anywhere in this file because no public Keycloak URL is documented in the repository (external dependency, see below).
- `frontend/app/(auth)/login/page.tsx` — single-line import swap from `@/components/theme-toggle` to `@/components/ui/theme-toggle` so the surviving `components/ui/theme-toggle.tsx` is the only ThemeToggle after the duplicate is deleted. No structural, styling, or behavior change to the login page; the protected `${window.location.origin}` redirect expression inside `LoginForm.tsx` is untouched.
- `frontend/components/theme-toggle.tsx` — DELETED (duplicate of `components/ui/theme-toggle.tsx`, which is kept per the Phase 1 plan).
- `frontend/components/courses/CourseTable.tsx` — DELETED (verified unused by grep across `frontend/`; the courses list page `frontend/app/courses/page.tsx` renders via `CourseForm` and direct calls to `useCourses`, not via `CourseTable`).
- `frontend/features/auth/api/useRegister.ts` — DELETED (file was empty — verified by direct read).
- `frontend/features/auth/schemas.ts` — DELETED (contained only `loginSchema` and `registerSchema`, both unused by grep; `LoginForm.tsx` and `app/(auth)/register/page.tsx` use Keycloak's hosted login/register flow, not these schemas).

**Verification performed.**

- `git diff --check` (whitespace/conflict) — PASS.
- `git apply --check phase1_slice2.patch` against `773186e` clean checkout — PASS.
- `python3 -c "import json; json.load(open('infra/realm-export.json'))"` — JSON still parses; `openlearn-frontend` client now reports both redirect URIs and both web origins as intended; `rootUrl`/`baseUrl` unchanged.
- `npx tsc --noEmit` (from `frontend/`) with the five client-side env vars set — Slice 2's TS surface (the login-page import swap and the four deletions) typechecks cleanly. The pre-existing `frontend/app/page.tsx` `as any` cast remains (intentionally untouched) and `tsc --noEmit` still passes because the cast is structurally typed.
- `npx eslint frontend/app/\(auth\)/login/page.tsx` — PASS for the changed file (no new lint errors introduced by the import swap). The full `npm run lint` still exits red due to the pre-existing `frontend/app/page.tsx` failures (`@typescript-eslint/no-explicit-any` and unused `user`); those are not introduced or fixed by Slice 2 and remain a known Phase 0 follow-up (§5).
- `bash scripts/setup-dev.sh` — NOT RE-RUN in the Slice 2 workspace (sandboxed executor with no Docker daemon). Slice 2 is structurally non-disruptive to the setup script: no env-var reads changed, `infra/realm-export.json` was edited additively with the existing localhost entries preserved, no `frontend` dependency added or removed, no `package.json` change. The setup script's structural contract with the repo is unchanged. The Phase 1 phase-gate verification step "scripts/setup-dev.sh completes green" remains OPEN and must be re-run by the user after applying the patch locally (see "Next Phase 1 action" below).

**External dependencies (NOT resolved by Slice 2 — require action outside the repository):**

1. **Public staging Keycloak URL is NOT confirmed anywhere in the repository.** Searched `infra/`, `docs/`, `.github/`, `frontend/`, `scripts/`, and the design / runbook trees. The staging compose file (`infra/docker-compose.staging.yml`) binds the Keycloak container to `0.0.0.0:8080` (i.e. reachable via the VPS public IP on port 8080), but no `*.duckdns.org` hostname is documented for it. The confirmed staging hostnames are ONLY: `openlearn-web-staging.duckdns.org` (frontend), `openlearn-api-staging.duckdns.org` (backend API), and `openlearn-storage-staging.duckdns.org` (MinIO). The browser cannot complete the OIDC redirect back to the staging frontend until Keycloak is reachable from the browser at a public origin. **Action owner: Pod D (Seyam).** Slice 2 deliberately does NOT invent a Keycloak hostname; `NEXT_PUBLIC_KEYCLOAK_URL` is therefore left to be set in the GitHub `vars.NEXT_PUBLIC_KEYCLOAK_URL` once Pod D confirms the public origin (it is already wired through Slice 1 — `.github/workflows/deploy-staging.yml` line 66 passes `vars.NEXT_PUBLIC_KEYCLOAK_URL` into the frontend image build).
2. **The running staging Keycloak holds the realm in a persistent H2 volume.** `infra/docker-compose.staging.yml` mounts `infra/realm-export.json` read-only at `/opt/keycloak/data/import/realm-export.json:ro` and starts Keycloak with `start-dev --import-realm`. Keycloak's `--import-realm` flag only imports realms that do not already exist in the database. With the persistent `keycloak_staging_data` volume already initialized, the realm-export.json changes will NOT take effect on a plain `docker compose restart keycloak`. **Action owner: Pod D (Seyam).** Two operational options exist (Pod D picks one): (a) wipe the `keycloak_staging_data` volume and restart Keycloak so the realm re-imports from the updated `realm-export.json` — note this is destructive to any runtime realm changes made through the admin UI; (b) apply the additive `redirectUris` / `webOrigins` change to the running staging Keycloak via the admin UI or `kcadm.sh` (non-destructive; preserves the persistent realm state).
3. **`scripts/setup-dev.sh` end-to-end re-run** must be performed by the user after applying the patch locally (the sandboxed executor has no Docker daemon available). See verification note above for why this is structurally safe.

**Known limitations of Slice 2.**

- Slice 2 does NOT fix the staging authentication end-to-end on its own. Even after Pod D resolves the two external dependencies above, the staging frontend must still be rebuilt with the correct `NEXT_PUBLIC_KEYCLOAK_URL` GitHub variable (set by Pod D) and the realm must be operationally updated on the running staging Keycloak. The Phase 1 phase-gate item "staging login works from a non-localhost browser" remains OPEN until that happens.
- Slice 2 deliberately does NOT touch `frontend/app/page.tsx`'s dead comment block and `as any` cast. The original Phase 1 plan listed those as part of the dead-code inventory, but the explicit task scope for this slice forbids fixing the known `app/page.tsx` lint issue. They remain a Phase 1 follow-up (or fold into Phase 4's home-page migration, which the original plan also lists as the cleanup site for that file).
- Slice 2 does NOT change the auth protocol, the redirect expressions `${window.location.origin}`, `${window.location.origin}/dashboard`, `${window.location.origin}/login`, the dev compose, the staging compose, the staging deploy workflow, the realm's other clients, the realm's `rootUrl`/`baseUrl`, or any Phase 2+ surface.

**Phase 1 gate status after Slice 2: STILL OPEN.** Of the seven Phase 1 phase-gate items, four are repository-side and are now satisfied by Slice 1 + Slice 2 (implementation complete and reviewed-pending; TypeScript / lint / build of the changed files clean — see verification note on `app/page.tsx`); the remaining three are blocked on the external dependencies above:
- [~] Phase 1 implementation complete and reviewed — repo-side DONE; review pending (Seyam).
- [~] TypeScript, lint, and build pass — Slice 2's TS / lint / build surface is clean. Full `npm run lint` still exits red due to the pre-existing `app/page.tsx` failure (Phase 0 known follow-up, §5); the Phase 1 plan originally proposed resolving this as part of Phase 1, but the explicit task scope for this slice forbids touching it. **REMAINS OPEN at the phase-gate level** until either a separate Phase 1 follow-up slice fixes `app/page.tsx` or Phase 4's home-page migration removes the dead code.
- [ ] Staging login works from a non-localhost browser — BLOCKED (external dependencies 1 and 2 above).
- [~] A fresh clone builds and runs with only `.env.local` — Slice 1 + Slice 2 do not change this; verification pending the user's local run of `setup-dev.sh`.
- [~] `scripts/setup-dev.sh` completes green — NOT RE-RUN (see verification note); structurally non-disruptive.
- [x] Protected functionality re-verified: the auth protocol itself is untouched — `lib/keycloak.ts`, `lib/auth-context.tsx`, `LoginForm.tsx`, `register/page.tsx` redirect expressions, Keycloak init options (`check-sso`, `pkceMethod: S256`, `checkLoginIframe: false`, `updateToken(30)`) are all UNCHANGED by Slice 2.
- [~] Changes reviewed by Seyam; realm/pipeline commits separately revertible — patch is a single revertible unit; review pending.

**Next Phase 1 action (after Slice 2 is applied locally).**

1. User applies `phase1_slice2.patch` to a clean checkout of `feature/frontend-refactor` at `773186e` and commits the result (Slice 2 is designed as one revertible commit per the Phase 1 plan's "shipped as an isolated, separately revertible commit" requirement for the realm/pipeline work; the dead-code deletions ride along because they share no files with any other phase and are individually revertible).
2. User runs `bash scripts/setup-dev.sh` locally to confirm the Phase 1 phase-gate item "`scripts/setup-dev.sh` completes green".
3. Pod D (Seyam) confirms and publishes the public staging Keycloak origin (e.g. a `*.duckdns.org` hostname pointing at the VPS, with TLS termination and port 8080 routed through the staging ingress). Pod D then sets `vars.NEXT_PUBLIC_KEYCLOAK_URL` in GitHub to that public origin.
4. Pod D applies the additive `redirectUris` / `webOrigins` change to the running staging Keycloak (via `kcadm.sh` for non-destructiveness, or by wiping `keycloak_staging_data` and restarting — Pod D's choice based on whether any runtime realm state must be preserved).
5. A new staging frontend image is built (the GitHub Actions `deploy-staging.yml` pipeline will pick up `vars.NEXT_PUBLIC_KEYCLOAK_URL` automatically once set in step 3) and deployed.
6. Manual verification: staging browser login round trip from a non-localhost machine succeeds against `https://openlearn-api-staging.duckdns.org`. Only at that point does the Phase 1 phase gate close.

**Phase 2 is NOT started by Slice 2.** No `lib/api.ts`, no `ApiError`, no schema migration, no TanStack Query convention migration, no course-API refactoring, no API-hook modifications, no route changes, no i18n, no Arabic/RTL, no Storybook redesign, no UI redesign. Slice 2 is strictly Phase 1.

### Phase 1 final closure record (2026-09-29)

**Final closure purpose.** Close the last repository-side Phase 1 item that Slice 1 and Slice 2 deliberately left untouched: the pre-existing `frontend/app/page.tsx` lint failure (Phase 0 known follow-up, §5). Slice 2's scope boundary explicitly forbade touching `app/page.tsx`; this final closure slice is explicitly authorized to fix it now.

**Baseline.** Branch `feature/frontend-refactor` @ `c6e7b3f` (HEAD after Slice 2). The final closure patch rides on top of `c6e7b3f` as `phase1_final_closure.patch` and is not yet committed to the remote branch.

**Implementation outcome (repository state after `git apply phase1_final_closure.patch` on top of `c6e7b3f`):**

- `frontend/app/page.tsx` — two minimal edits, both preserving the page's existing behavior and logic:
  1. Line 9: removed the `as { data: any; isLoading: boolean }` cast from the `useMe()` call. The hook already returns a properly typed `UseQueryResult<MeResponse>` (see `frontend/features/auth/api/useMe.ts` + `frontend/features/auth/types.ts`), so the cast was unnecessary and was the source of the `@typescript-eslint/no-explicit-any` error. Simultaneously dropped the unused `data: user` destructuring (the `user` variable was never read — only `isLoading: userLoading` was used). This resolves the `@typescript-eslint/no-unused-vars` warning for `user`. The `isLoading = authLoading || userLoading` computation is unchanged.
  2. Removed the trailing dead comment block (`/* cd frontend / npm run dev / Local: http://localhost:3000 / document.documentElement.classList.add("dark") / .\.venv\Scripts\Activate.ps1 / uvicorn app.main:app --host 0.0.0.0 --port 8000  (backend) */`). This was leftover developer scratch notes that did not belong in committed source.
- `frontend/docs/OpenLearn-AI_Frontend_Modernization_Execution_Roadmap_v1.1-closure.md` — this file. Header, §1 Current Focus, §4 Global Progress, §6 Phase 1 status row, §6 required-work checklist, §6 phase-gate items, and this final closure record all updated to reflect the final closure state.

**What was NOT touched (scope guard).** `lib/config.ts`, `lib/keycloak.ts`, `lib/auth-context.tsx`, `sentry.client.config.ts`, `frontend/Dockerfile`, `frontend/.env.example`, `frontend/.dockerignore`, `.github/workflows/deploy-staging.yml`, `infra/realm-export.json`, `infra/docker-compose.staging.yml`, `infra/docker-compose.dev.yml`, `infra/dev/bootstrap-keycloak.sh`, `scripts/setup-dev.sh`, `scripts/LOCAL_SETUP.md`, all `features/` hooks, `components/Navbar.tsx`, `components/auth/LoginForm.tsx`, `app/(auth)/login/page.tsx`, `app/(auth)/register/page.tsx`, all `components/ui/*`, all `components/courses/*`, all `components/profile/*`. No Phase 2 surface (`lib/api.ts`, `ApiError`, schemas, keys, query-provider, course hooks). No Phase 3+ surface.

**Verification performed (on the final closure tree).**

| Check | Command | Result |
|---|---|---|
| Working-tree hygiene | `git diff --check` | PASS (EXIT 0, no whitespace/conflict markers) |
| Forward apply (clean checkout at `c6e7b3f`) | `git apply --check phase1_final_closure.patch` | PASS (EXIT 0) |
| Forward apply (actual) | `git apply phase1_final_closure.patch` | PASS (EXIT 0; 2 files changed) |
| Reverse check (patched tree) | `git apply --check --reverse phase1_final_closure.patch` | PASS (EXIT 0) |
| Reverse apply (patched tree) | `git apply --reverse phase1_final_closure.patch` | PASS (EXIT 0; tree restored to `c6e7b3f`) |
| TypeScript strict | `NEXT_PUBLIC_API_URL=… NEXT_PUBLIC_KEYCLOAK_URL=… NEXT_PUBLIC_KEYCLOAK_REALM=… NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=… npx tsc --noEmit` | PASS (EXIT 0) |
| ESLint on changed file | `npx eslint 'app/page.tsx'` | PASS (EXIT 0, zero errors, zero warnings) |
| Full ESLint | `npm run lint` | PASS (EXIT 0, zero errors, zero warnings across the entire frontend — first green lint since Phase 0) |
| Next.js production build | `NEXT_PUBLIC_API_URL=… NEXT_PUBLIC_KEYCLOAK_URL=… NEXT_PUBLIC_KEYCLOAK_REALM=… NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=… npm run build` | PASS (EXIT 0; all 10 routes compiled: `/`, `/_not-found`, `/courses`, `/courses/[id]`, `/courses/[id]/edit`, `/courses/new`, `/dashboard`, `/login`, `/profile`, `/register`) |
| Realm JSON validation | `python3 -c "import json; json.load(open('infra/realm-export.json'))"` | PASS (parses cleanly; `openlearn-frontend` client reports both `redirectUris` `["http://localhost:3000/*", "https://openlearn-web-staging.duckdns.org/*"]` and both `webOrigins` `["http://localhost:3000", "https://openlearn-web-staging.duckdns.org"]`; `rootUrl`/`baseUrl` unchanged; PKCE `S256`; `publicClient: true`; `standardFlowEnabled: true`) |
| Dead-code audit | `for f in frontend/components/courses/CourseTable.tsx frontend/components/theme-toggle.tsx frontend/features/auth/api/useRegister.ts frontend/features/auth/schemas.ts; do [ -e "$f" ] && echo "STILL EXISTS" || echo "DELETED"; done` | PASS (all four DELETED; both surviving ThemeToggle consumers — `Navbar.tsx` and `app/(auth)/login/page.tsx` — import from `@/components/ui/theme-toggle`) |
| Fresh-clone contract | `git ls-files frontend/ \| grep -E "\.env"` → only `frontend/.env.example` tracked; `.gitignore` excludes `.env`/`.env.local`/`*.env`; `frontend/.dockerignore` excludes `.env*` | PASS |
| Configuration centralization | `grep "process.env.NEXT_PUBLIC" frontend/lib/keycloak.ts frontend/sentry.client.config.ts` → no matches (both consume `config` from `@/lib/config`) | PASS |
| `scripts/setup-dev.sh` | not run in sandbox (no Docker daemon available) | NOT RUN by GLM; VERIFIED BY USER (2026-09-29) on the Slice 2 tree — the final closure slice only modifies `frontend/app/page.tsx` and this roadmap doc, neither of which is touched by `setup-dev.sh`, so the user's prior green run remains valid |
| Staging browser login round trip | not run — public staging Keycloak origin not yet published; persistent staging realm not yet operationally updated | BLOCKED (external operational dependencies — see below) |

**External dependencies (NOT resolved by the final closure slice — require action outside the repository):**

1. **Public staging Keycloak URL is NOT confirmed anywhere in the repository.** Re-verified at `c6e7b3f` by searching `infra/`, `docs/`, `.github/`, `frontend/`, `scripts/`, and the design / runbook trees for `keycloak.*duckdns`, `kc.openlearn`, `auth.openlearn`, `sso.openlearn`, `idp.openlearn`, `openlearn-keycloak`, `NEXT_PUBLIC_KEYCLOAK_URL`, `8080`. The staging compose (`infra/docker-compose.staging.yml`) binds Keycloak to `0.0.0.0:8080` (reachable via VPS public IP on port 8080, but no DNS/TLS hostname is documented). The confirmed staging hostnames remain ONLY: `openlearn-web-staging.duckdns.org` (frontend), `openlearn-api-staging.duckdns.org` (backend API), `openlearn-storage-staging.duckdns.org` (MinIO). The browser cannot complete the OIDC redirect back to the staging frontend until Keycloak is reachable from the browser at a public origin. **Action owner: Pod D (Seyam).** The final closure slice deliberately does NOT invent a Keycloak hostname; `NEXT_PUBLIC_KEYCLOAK_URL` is left to be set in the GitHub `vars.NEXT_PUBLIC_KEYCLOAK_URL` once Pod D confirms the public origin (already wired through Slice 1 — `.github/workflows/deploy-staging.yml` line 66 passes `vars.NEXT_PUBLIC_KEYCLOAK_URL` into the frontend image build).

2. **The running staging Keycloak holds the realm in a persistent H2 volume.** `infra/docker-compose.staging.yml` mounts `infra/realm-export.json` read-only at `/opt/keycloak/data/import/realm-export.json:ro` and starts Keycloak with `start-dev --import-realm`. Per Keycloak's documented behavior, `--import-realm` only imports realms that do NOT already exist in the database. With the persistent `keycloak_staging_data` volume already initialized, the realm-export.json changes will NOT take effect on a plain `docker compose restart keycloak`. **Action owner: Pod D (Seyam).** Two operational options exist (Pod D picks one): (a) wipe `keycloak_staging_data` and restart Keycloak so the realm re-imports from the updated JSON — destructive to any runtime realm changes made through the admin UI; (b) apply the additive `redirectUris` / `webOrigins` change to the running staging Keycloak via the admin UI or `kcadm.sh` — non-destructive; preserves persistent realm state. Recommended: option (b) for non-destructiveness.

**Phase 1 gate status after final closure slice: REPOSITORY-SIDE CLOSED; ONE EXTERNAL ITEM REMAINS.** Of the seven Phase 1 phase-gate items, six are now CLOSED (implementation complete; TypeScript / lint / build pass; fresh-clone contract verified; `setup-dev.sh` verified by user; protected functionality untouched; commits separately revertible). The single remaining OPEN item is:

- [ ] Staging login works from a non-localhost browser — BLOCKED on external dependencies 1 and 2 above. This item cannot be closed from the repository; it requires Pod D operational coordination.

**Phase 1 closure distinction.** The roadmap distinguishes:
- **REPOSITORY COMPLETE** — YES. Every repository-side Phase 1 work item is implemented, committed (Slice 1 at `773186e`, Slice 2 at `c6e7b3f`), and the final closure patch is ready to apply on top of `c6e7b3f`. TypeScript, ESLint, and production build all pass on the final closure tree.
- **LOCAL VERIFICATION** — COMPLETE. `npx tsc --noEmit` PASS; `npm run lint` PASS (zero errors, zero warnings); `npm run build` PASS; realm JSON parses cleanly; dead-code audit clean; fresh-clone contract sound; `setup-dev.sh` verified by user.
- **STAGING OPERATIONAL VERIFICATION** — NOT VERIFIED. The staging browser login round trip has not been performed because the public staging Keycloak origin is not yet published and the persistent staging realm has not been operationally updated. This is an external infrastructure dependency, not a repository-side defect.
- **EXTERNAL INFRASTRUCTURE BLOCKERS** — TWO: (1) public Keycloak origin; (2) persistent staging realm operational update. Both owned by Pod D (Seyam).

**Next Phase 1 action (after the final closure patch is applied locally).**

1. User applies `phase1_final_closure.patch` to a clean checkout of `feature/frontend-refactor` at `c6e7b3f` and commits the result. Recommended commit message: `fix(frontend): close Phase 1 lint and verification gaps`.
2. User re-runs `npm run lint` and `npm run build` locally to confirm the green state documented above.
3. Pod D (Seyam) confirms and publishes the public staging Keycloak origin (e.g. a `*.duckdns.org` hostname pointing at the VPS, with TLS termination and port 8080 routed through the staging ingress). Pod D then sets `vars.NEXT_PUBLIC_KEYCLOAK_URL` in GitHub to that public origin.
4. Pod D applies the additive `redirectUris` / `webOrigins` change to the running staging Keycloak (via `kcadm.sh` for non-destructiveness, or by wiping `keycloak_staging_data` and restarting — Pod D's choice based on whether any runtime realm state must be preserved).
5. A new staging frontend image is built (the GitHub Actions `deploy-staging.yml` pipeline will pick up `vars.NEXT_PUBLIC_KEYCLOAK_URL` automatically once set in step 3) and deployed.
6. Manual verification: staging browser login round trip from a non-localhost machine succeeds against `https://openlearn-api-staging.duckdns.org`. Only at that point does the Phase 1 phase gate's last item close.

**Phase 2 is NOT started by the final closure slice.** No `lib/api.ts`, no `ApiError`, no schema migration, no TanStack Query convention migration, no course-API refactoring, no API-hook modifications, no route changes, no i18n, no Arabic/RTL, no Storybook redesign, no UI redesign. The final closure slice is strictly Phase 1.

---

## 7. Phase 2 — Data Foundation (First Implementation Slice)

| Status | Estimate | Decisions implemented | Depends on |
|---|---|---|---|
| IN PROGRESS (2026-09-29) — Slice 1 patch landed in this revision, locally verified; Phase 2 phase gate automated items CLOSED, manual CRUD round-trip pending user verification (see Slice 1 closure record below) | ~1 sprint | D3, D4, D5, D8 (error half) | Phase 0 gate only (closed 2026-09-29) — deliberately **not** gated on Phase 1 |

**Parallel note.** Shares no files with Phase 1's deployment track; both may run after Phase 0. If Phase 1 already landed `lib/config.ts`, reuse it; if not, Slice 1 carries the module itself, exactly as architecture document Section 12 defines.

**Goal.** Establish the single API boundary, schemas-as-types, and query conventions — proven on the courses feature as the reference implementation every later migration copies.

**Why.** This is the architecture document's first implementation slice, chosen because the courses list is a read-only page (lowest risk) that still exercises the three most load-bearing decisions (D3, D4, D5). It deliberately does not start with the route restructure (visually wide) or the deployment fix (needs a Pod D partner). Reviewing the slice answers "is this the right level of abstraction?" with a concrete artifact, and proves by omission that the foundation needs no new dependency, no code generation, no framework.

**Prerequisites.** Phase 0 gate passed. Phase 1 status irrelevant — by design.

**Work — required (Slice 1: one PR, exactly as specified in architecture document Section 12):**

- [x] `lib/config.ts` (skip if Phase 1 already delivered it) — Phase 1 delivered it at `773186e`; reused unchanged
- [x] `lib/api.ts` — `ApiError` and `apiFetch(path, { method, body, schema })`; ~80 lines with comments; hard 150-line cap — DONE in Slice 1 (`frontend/lib/api.ts`, 145 total lines / 105 code lines). `ApiError` carries `status` + `message` + `body`; `apiFetch` centralizes URL construction (from `config.apiUrl`), token acquisition (via `getAccessToken()`), Authorization header, JSON body serialization, non-OK → `ApiError` mapping with FastAPI `detail` extraction (string + 422 array shapes), optional Zod response validation, and 204 No Content handling
- [x] `features/courses/schemas.ts` — add the course response schema; `Course` becomes `z.infer` of it — DONE in Slice 1. Added `courseResponseSchema` (Zod object: `id`/`owner_id` as UUID strings, `title` 1–255 chars, `description` nullable, `created_at` ISO datetime with offset) cross-checked against `backend/app/schemas/course.py` `CourseResponse` and `backend/app/models/course.py` `DateTime(timezone=True)`. `Course` is now `z.infer<typeof courseResponseSchema>`. The existing form-input `courseSchema` / `CourseFormValues` is preserved unchanged
- [x] `features/courses/keys.ts` — the course key factory — DONE in Slice 1. `courseKeys.all` / `.lists()` / `.list(filters?)` / `.details()` / `.detail(id)` — hierarchical, stable, copyable per-domain convention
- [x] `lib/query-provider.tsx` — explicit QueryClient defaults (staleTime, retry, refetchOnWindowFocus), deltas listed in the PR body — DONE in Slice 1. Defaults: `staleTime: 30_000` (was 0), `retry: 1` (was 3), `refetchOnWindowFocus: false` (was true). Behavior deltas documented in the provider file's docstring and in the Slice 1 closure record below
- [x] `features/courses/api/useCourses.ts` migrated onto all of the above — DONE in Slice 1. Now calls `apiFetch<Course[]>("/v1/courses", { schema: courseResponseSchema.array() })` and uses `courseKeys.lists()`
- [x] Unit tests for `apiFetch` error mapping and the key factory — DONE in Slice 1. `frontend/lib/api.test.ts` (12 tests: auth/no-token, success/GET/POST/204, error mapping 404/422/403/500/network/schema-validation) and `frontend/features/courses/keys.test.ts` (5 tests: stability, list-vs-detail distinguishability, per-id detail, invalidation strategy, filter-scoped list keys). Added a `unit` vitest project (plain node, no browser) and a `test` script to `package.json`
- [x] `app/courses/page.tsx` — unchanged except whatever the type changes require (nothing, by design) — CONFIRMED unchanged. The page imports only `useCourses` (not the `Course` type directly), so the type moving from a hand-written interface in `useCourses.ts` to `z.infer` in `schemas.ts` required zero page-level edits

**Work — required (follow-up PRs, one file at a time):**

- [x] Migrate `features/courses/api/useCourse.ts` (copy-adapt of the approved pattern — a five-minute exercise by design) — DONE in Slice 1. Now calls `apiFetch<Course>("/v1/courses/${courseId}", { schema: courseResponseSchema })` and uses `courseKeys.detail(courseId)`; imports `Course` from `schemas.ts` instead of re-importing from `useCourses.ts`
- [x] Migrate `features/courses/api/useCourseMutations.ts`; create/update invalidate the courses list keys (closes the no-invalidation problem for this domain) — DONE in Slice 1. Both mutations use `apiFetch` with the response schema. `useCreateCourse` invalidates `courseKeys.lists()` on success. `useUpdateCourse` invalidates both `courseKeys.lists()` and `courseKeys.detail(courseId)` on success. The `CourseApiError` class is deleted (collapsed into the shared `ApiError` per D8). Navigation on success is preserved (the form still pushes to `/courses`) — invalidation handles cache consistency, navigation handles the viewport
- [x] `components/courses/CourseForm.tsx` drops its private status mapping — 401/404/422 rendering goes through `ApiError` status — DONE in Slice 1. Imports `ApiError` from `@/lib/api` instead of `CourseApiError` from the mutations file. The 401/403/404 status branches are preserved unchanged; a 422 branch was added (the roadmap explicitly called out 401/404/422). No UI redesign, no validation-UX change

**Work — recommended:**

- [x] Cross-check the response schema against FastAPI auto-docs once, before merging the schema PR — DONE: inspected `backend/app/api/courses.py` (response_model=`CourseResponse` / `list[CourseResponse]`), `backend/app/schemas/course.py` (`CourseResponse`: `id`/`owner_id` UUID, `title` str, `description` str|None, `created_at` datetime), and `backend/app/models/course.py` (`DateTime(timezone=True)`). Schema matches
- [ ] Before/after screenshots of the courses list — the page must be visually identical — NOT RUN: the GLM executor has no browser; the user should verify visually after applying the patch locally. The page itself (`app/courses/page.tsx`) is unchanged by design; only the data-access path under it changed

**Deferred from this phase.** `useMe` and profile hooks → Phase 4. Generated API client → Deferred Backlog (trigger: ~25+ endpoints).

**Affected areas.** New `lib/api.ts` (+ `lib/config.ts` if not landed); `features/courses/` (schemas, new `keys.ts`, three hook files); `lib/query-provider.tsx`; `components/courses/CourseForm.tsx`.

**Verification.**

- CI green; new unit tests pass
- Manual: courses list renders identically
- Manual: create → appears in list without refresh; edit → detail and list update
- Error paths: logged out (401) and invalid ID (404) show the shared messages
- grep: zero direct `fetch` or `process.env` reads in `features/courses`

### Phase gate — before starting Phase 3

- [~] Slice 1 merged and explicitly reviewed as the reference implementation — Slice 1 patch landed in this revision; review by Seyam pending
- [x] Remaining course hooks migrated onto the pattern — `useCourse.ts` and `useCourseMutations.ts` both migrated in Slice 1; `CourseForm.tsx` consumes `ApiError`
- [x] TypeScript, lint, and build pass — VERIFIED locally on the Slice 1 tree: `npx tsc --noEmit` EXIT 0; `npm run lint` EXIT 0 (zero errors, zero warnings); `npm run build` EXIT 0 (all 10 routes compiled). New unit tests pass: `npm run test` → 17/17 tests pass across `lib/api.test.ts` (12) and `features/courses/keys.test.ts` (5)
- [ ] Courses CRUD manual round trip green (create, read, update — delete arrives in Phase 4) — NOT RUN: the GLM executor has no running backend + Keycloak stack; the user must verify on their local `setup-dev.sh` environment after applying the patch
- [~] Invalidation verified — no manual refresh needed after mutations — DESIGNED and code-reviewed (create invalidates `courseKeys.lists()`; update invalidates `courseKeys.lists()` + `courseKeys.detail(courseId)`); manual verification pending the CRUD round-trip above
- [x] Protected functionality: course create/read/update behavior and API contract unchanged — VERIFIED by inspection: API paths (`/v1/courses`, `/v1/courses/{id}`), HTTP methods (GET/POST/PUT), request body shape (`CourseFormValues`), response shape (`CourseResponse`), and the form's navigation-on-success behavior are all preserved. The `CourseApiError` class is deleted but its status-mapping logic lives on in `CourseForm.tsx` via `ApiError` (same 401/403/404 messages, plus a new 422 message)
- [~] Changes reviewed by Seyam — review pending

**Owner / execution model.** GLM implements — the slice is a single instructed task; follow-up hooks one task each. ChatGPT can prepare the implementation prompt from architecture Section 12. Seyam reviews the slice as the abstraction-level judgment. BigPickle optional (e.g., inventorying remaining fetch sites).

**Migration map.**

| Current | In this phase | Target |
|---|---|---|
| Three hook files with inline fetch, hand-written interfaces, library-default queries, mutations that navigate instead of invalidating | One boundary (`apiFetch` + `ApiError`), inferred types, explicit defaults, real invalidation — courses only | The Section 9 data flow — hook, queryOptions, key, apiFetch, schema — as the pattern every domain copies |

### Phase 2 Slice 1 — Courses foundation closure record (2026-09-29)

**Slice 1 purpose.** Establish the frontend's data-access foundation using the Courses feature as the pilot/reference implementation, exactly as specified in architecture document Section 12. The slice implements D3 (single `apiFetch` boundary + `ApiError`), D4 (Zod response schemas as the source of `Course` type), D5 (explicit `QueryClient` defaults + per-domain key factory + mutation invalidation), and the error half of D8 (shared `ApiError` consumed by `CourseForm`).

**Baseline.** Branch `feature/frontend-refactor` @ `d9d1c53` (HEAD after Phase 1 final closure). The Slice 1 patch rides on top of `d9d1c53` as `phase2_courses_foundation.patch` and is not yet committed to the remote branch.

**Implementation outcome (repository state after `git apply phase2_courses_foundation.patch` on top of `d9d1c53`):**

New files:
- `frontend/lib/api.ts` (145 lines) — `ApiError` class (carries `status`, `message`, `body`) + `apiFetch<T>(path, { method, body, schema })` helper. Centralizes: API base URL (from `config.apiUrl`), bearer token (from `getAccessToken()`), Authorization header, JSON body serialization, non-OK → `ApiError` mapping with FastAPI `detail` extraction (string HTTPException shape + 422 array-of-`{msg,loc}` shape), optional Zod response validation (failure throws `ApiError` with status 0), and 204 No Content handling (resolves to `undefined`).
- `frontend/lib/api.test.ts` (12 tests) — covers: no-token → `ApiError(401)`; successful GET with bearer header attachment; schema-validated response; POST body serialization + Content-Type; 204 → `undefined`; 404 with `detail` preservation; 422 FastAPI array `msg` extraction; 403 non-JSON fallback; 500 empty body fallback; network failure → `ApiError(0)`; schema validation failure → `ApiError(0)`.
- `frontend/features/courses/keys.ts` — `courseKeys` factory: `.all` / `.lists()` / `.list(filters?)` / `.details()` / `.detail(id)`. Hierarchical, stable, copyable.
- `frontend/features/courses/keys.test.ts` (5 tests) — covers: stable `all` root; list vs detail distinguishability; per-id detail keys; invalidation strategy (list key prefix does not match detail key); filter-scoped list keys.

Modified files:
- `frontend/features/courses/schemas.ts` — added `courseResponseSchema` (Zod: `id`/`owner_id` UUID, `title` 1–255, `description` nullable, `created_at` ISO datetime with offset) + `Course = z.infer<typeof courseResponseSchema>`. Existing form-input `courseSchema` / `CourseFormValues` preserved.
- `frontend/features/courses/api/useCourses.ts` — migrated to `apiFetch<Course[]>("/v1/courses", { schema: courseResponseSchema.array() })` + `courseKeys.lists()`. Removed: inline `fetch`, `getAccessToken`, `process.env.NEXT_PUBLIC_API_URL`, hand-written `Course` interface, `Error` throw.
- `frontend/features/courses/api/useCourse.ts` — migrated to `apiFetch<Course>("/v1/courses/${courseId}", { schema: courseResponseSchema })` + `courseKeys.detail(courseId)`. `Course` now imported from `schemas.ts`.
- `frontend/features/courses/api/useCourseMutations.ts` — both mutations migrated to `apiFetch` with response schema. `useCreateCourse` invalidates `courseKeys.lists()`. `useUpdateCourse` invalidates `courseKeys.lists()` + `courseKeys.detail(courseId)`. `CourseApiError` class deleted (collapsed into shared `ApiError`). Navigation-on-success preserved in `CourseForm.tsx`.
- `frontend/components/courses/CourseForm.tsx` — imports `ApiError` from `@/lib/api` instead of `CourseApiError` from the mutations file. Status mapping: 401/403/404 branches preserved unchanged; 422 branch added. No UI redesign.
- `frontend/lib/query-provider.tsx` — explicit `QueryClient` defaults: `staleTime: 30_000` (was 0), `retry: 1` (was 3), `refetchOnWindowFocus: false` (was true). Provider order (`ThemeProvider → AppQueryProvider → AuthProvider`) and `useState` singleton construction preserved.
- `frontend/vitest.config.ts` — added a `unit` project (plain node, no browser) alongside the existing `storybook` browser project. Resolves the `@/*` path alias the same way the app does.
- `frontend/package.json` — added `"test": "vitest run --project unit"` and `"test:storybook": "vitest run --project storybook"` scripts.

**Behavior deltas (D5 requires these to be documented in the PR body):**

1. `staleTime: 0 → 30_000` — course list and detail queries are now considered fresh for 30 seconds. A user navigating away from `/courses` and back within 30s will see cached data without a refetch. After 30s, the next mount refetches. This is the intended D5 behavior ("around 30s for read models").
2. `retry: 3 → 1` — failed queries now retry once instead of three times. A logged-out visitor's 401 from `useMe` no longer retries 3x with exponential backoff before the UI gives up. This is the intended D5 behavior ("retry: 1 or status-aware retry").
3. `refetchOnWindowFocus: true → false` — alt-tabbing back to the browser tab no longer refetches `/auth/me` and `/v1/courses`. This is the intended D5 behavior ("refetchOnWindowFocus: false for this app's usage").
4. `CourseApiError` deleted — the private error class in `useCourseMutations.ts` is replaced by the shared `ApiError` from `lib/api.ts`. `CourseForm.tsx`'s status mapping (401/403/404) is preserved; a 422 branch is added. The user-facing messages are unchanged for 401/403/404.
5. Mutation invalidation added — `useCreateCourse` and `useUpdateCourse` now invalidate `courseKeys.lists()` (and `courseKeys.detail(id)` for update) on success. Previously, the form navigated to `/courses` and the list refetched only because `staleTime` was 0. Now the list refetches because the mutation explicitly invalidated it — this is the intended D5 behavior and is robust to future `staleTime` changes.

**What was NOT touched (scope guard).** `lib/config.ts`, `lib/keycloak.ts`, `lib/auth-context.tsx`, `sentry.client.config.ts`, `frontend/Dockerfile`, `frontend/.env.example`, `frontend/.dockerignore`, `.github/workflows/deploy-staging.yml`, `infra/realm-export.json`, all Phase 1 files. No `app/` page files (the courses pages are unchanged by design). No auth/profile hooks (`useMe`, `useProfile`, `useProfileMutation` — those are Phase 4). No Phase 3 surface (route groups, AuthGuard, loading/error/not-found files, shared state components). No Phase 5/6 surface. No generated API client. No new dependencies added to `package.json` (vitest + zod were already installed).

**Verification performed (on the Slice 1 tree).**

| Check | Command | Result |
|---|---|---|
| Working-tree hygiene | `git diff --check` | PASS (EXIT 0) |
| Forward apply (clean `d9d1c53`) | `git apply --check phase2_courses_foundation.patch` | PASS (EXIT 0) |
| Forward apply (actual) | `git apply phase2_courses_foundation.patch` | PASS (EXIT 0; 12 files: 4 new, 8 modified) |
| Reverse check (patched tree) | `git apply --check --reverse phase2_courses_foundation.patch` | PASS (EXIT 0) |
| Reverse apply (patched tree) | `git apply --reverse phase2_courses_foundation.patch` | PASS (EXIT 0; tree restored to `d9d1c53`) |
| TypeScript strict | `npx tsc --noEmit` (with 5 env vars set) | PASS (EXIT 0) |
| Full ESLint | `npm run lint` | PASS (EXIT 0, zero errors, zero warnings) |
| Unit tests | `npm run test` | PASS (17/17 tests across 2 files) |
| Next.js production build | `npm run build` (with 5 env vars set) | PASS (EXIT 0; all 10 routes compiled) |
| Scope audit: no direct `fetch` in `features/courses` | `grep -rn '\bfetch(' frontend/features/courses/` | PASS (zero matches) |
| Scope audit: no `process.env` in `features/courses` | `grep -rn 'process\.env' frontend/features/courses/` | PASS (zero matches) |
| Scope audit: no `getAccessToken` direct calls in `features/courses` | `grep -rn 'getAccessToken' frontend/features/courses/` | PASS (zero matches) |
| Schema cross-check vs backend | inspected `backend/app/api/courses.py` + `backend/app/schemas/course.py` + `backend/app/models/course.py` | PASS (`courseResponseSchema` matches `CourseResponse`: UUID id/owner_id, str title, nullable description, timezone-aware datetime created_at) |
| Manual courses CRUD round trip | not run (GLM executor has no running backend + Keycloak stack) | NOT RUN — user must verify on local `setup-dev.sh` environment |
| Before/after screenshots | not run (GLM executor has no browser) | NOT RUN — user must verify visually; `app/courses/page.tsx` is unchanged by design |

**Phase 2 gate status after Slice 1: AUTOMATED ITEMS CLOSED; MANUAL ITEMS PENDING USER VERIFICATION.**

Of the seven Phase 2 phase-gate items:
- [~] Slice 1 merged and reviewed — patch landed; review pending.
- [x] Remaining course hooks migrated — DONE.
- [x] TypeScript, lint, build pass — DONE (plus unit tests).
- [ ] Courses CRUD manual round trip — PENDING user verification on local stack.
- [~] Invalidation verified — code-reviewed; manual verification pending the CRUD round-trip.
- [x] Protected functionality — course API contract and form behavior preserved.
- [~] Reviewed by Seyam — pending.

**Next Phase 2 action (after Slice 1 is applied locally).**

1. User applies `phase2_courses_foundation.patch` to a clean checkout of `feature/frontend-refactor` at `d9d1c53` and commits the result. Recommended commit message: `feat(frontend): establish data-access foundation on courses (Phase 2 Slice 1)`.
2. User runs `npm run test`, `npm run lint`, `npx tsc --noEmit`, and `npm run build` locally to confirm the green state.
3. User starts the local backend + Keycloak stack (`bash scripts/setup-dev.sh` if not already running) and performs the manual courses CRUD round trip: create a course → verify it appears in the list without a manual refresh (invalidation); edit the course → verify both the detail page and the list update; verify a logged-out state shows the 401 message; verify an invalid course ID shows the 404 message.
4. User visually confirms the courses list page is identical before/after (no UI changes by design).
5. Only after the manual round trip is green does the Phase 2 phase gate close and Phase 3 become unblocked.

**Phase 3 is NOT started by Slice 1.** No route-group restructure, no AuthGuard, no loading/error/not-found files, no shared state components, no Navbar relocation. Slice 1 is strictly Phase 2.

---

## 8. Phase 3 — Application Shell & Route Patterns

| Status | Estimate | Decisions implemented | Depends on |
|---|---|---|---|
| NOT STARTED | ~1 sprint | D1, D7, D11, D10 (rails) | Phase 2 gate |

**Parallel note.** None — this phase restructures the app directory and must own that change alone.

**Goal.** Make the shell structural: one guarded `(app)` route group owning the Navbar, route-level fallback files, shared loading/error/empty components, and the RTL/font rails in the root layout.

**Why.** Today the Navbar renders from the root layout — including on the login and register pages; exactly one page (courses) guards itself with a `useEffect`; no route anywhere has `loading.tsx`/`error.tsx`/`not-found.tsx`, so an unauthenticated deep link to `/profile` lands wherever it lands and an invalid course ID renders a raw error string. D1/D7/D11 fix this once at layout level; the D10 rails (dir, Arabic-capable fonts) go in while they are a line each rather than a retrofit.

**D10 boundary (clarification, not a new decision).** LTR/English remains the product baseline: `dir` ships defaulting to `ltr`, English copy and routes are untouched, and nothing here removes or deprioritizes English. The rails exist so Arabic + RTL becomes a first-class supported direction without a later refactor — appropriate `dir` usage, an Arabic-capable font in the token stack, and layouts verified in both LTR and RTL. No i18n framework, no message catalogs, and no Arabic translation of the product in this phase.

**Prerequisites.** Phase 2 gate (ErrorState renders ApiError; the conventions exist).

**Work — required:**

- [ ] Mechanical route-group move first, as its own PR: create `app/(app)/`, move `dashboard/`, `profile/`, `courses/` under it — URLs unchanged; root layout keeps only providers and the public home
- [ ] `app/(app)/layout.tsx` — Navbar and footer move here; Navbar removed from the root layout
- [ ] `components/AuthGuard.tsx` — the single guard; wraps `(app)` layout children; unauthenticated → `/login` carrying `redirectedFrom`
- [ ] Redirect policy in `lib/auth-context.tsx`: login → `/dashboard` or originally requested page; register → `/dashboard`; logout → `/login` — the one deliberate, loudly announced behavior delta of the whole modernization
- [ ] `app/not-found.tsx` — root 404, also serves `notFound()` throws from detail pages
- [ ] `app/(app)/loading.tsx` and `app/(app)/error.tsx` (plus `courses/loading.tsx` where it helps)
- [ ] `components/state/` — the shared trio: `LoadingBlock`, `ErrorState`, `EmptyState`
- [ ] Root layout: `dir` attribute + Arabic-capable font in the token stack — no visible change while UI copy is English
- [ ] Login page: remove its duplicate theme toggle

**Work — recommended:**

- [ ] Give `app/(auth)/layout.tsx` the centered minimal layout as part of the move; verify no navbar renders there

**Deferred from this phase.** Mobile menu → Phase 4, deliberately, to keep the route-move PR small.

**Affected areas.** `app/` restructure per architecture Section 9.1; new `components/state/` trio; new `components/AuthGuard.tsx`; `lib/auth-context.tsx`; `app/(auth)/login/page.tsx`.

**Verification.**

- CI green
- Deep link to `/courses` while logged out → login → returns to `/courses` after authentication
- login → `/dashboard` (or originally requested page); logout → `/login`; back button shows no stale data
- Invalid course ID → not-found page, not a raw error string
- dir/font swap: no visual regression while copy is English
- grep: no page implements its own loading/error/empty markup; the guard exists in exactly one file

### Phase gate — before starting Phase 4

- [ ] Route-group move shipped as its own reviewed PR (trivial bisect)
- [ ] Guard exists in exactly one file; zero per-page guards remain
- [ ] TypeScript, lint, and build pass
- [ ] Manual deep-link, redirect, and 404 checklist green
- [ ] Protected functionality: auth protocol untouched; the redirect change is the single announced delta
- [ ] Changes reviewed by Seyam

**Owner / execution model.** GLM implements in two instructed steps — the mechanical move first, then the guard and fallbacks — never both in one PR. BigPickle useful before the move (confirm no import/link references a moved file). Seyam reviews each PR against the deep-link checklist.

**Migration map.**

| Current | In this phase | Target |
|---|---|---|
| Navbar in root layout; courses page self-guards with `useEffect`; no fallback files; login redirects by origin | One guarded `(app)` group owning the Navbar; route-level loading/error/not-found; consistent redirects with `redirectedFrom` | Protection in exactly one file; every authenticated route shares one shell and one set of state components |

---

## 9. Phase 4 — Feature & Page Migration

| Status | Estimate | Decisions implemented | Depends on |
|---|---|---|---|
| NOT STARTED | 2–3 sprints | D2 (rules applied), D9 (token dialect), D8 (Field wrapper), D10 (logical utilities) | Phase 2 + Phase 3 gates |

**Parallel note.** Routes migrate one-per-PR and parallelize across the two engineers (one: profile + auth hooks; one: dashboard + home + Navbar).

**Goal.** Migrate profile, dashboard, home, and the remaining course pages onto the foundation; kill the fabricated data; add the missing delete-course UI and the mobile menu.

**Why.** With the foundation and shell in place, every remaining route is a copy-adapt exercise against the courses reference. This phase carries the user-visible wins staged deliberately late: a profile page that works in dark mode, a dashboard that stops inventing statistics, the course delete flow (the backend DELETE endpoint exists with no frontend caller — a contract gap, not a feature), and phone-usable navigation. Largest phase — contained by strict one-route-per-PR sequencing.

**D9 boundary (clarification, not a new decision).** The token migration exists for architectural consistency — one styling dialect, dark-mode correctness, and a stable styling/token foundation. It does not declare today's colors, typography, spacing, or component appearance the final visual identity: a later part of the modernization intentionally redesigns the UI/UX, visual identity, colors, typography, spacing, and component appearance on top of this foundation.

**Prerequisites.** Phase 2 gate (the data pattern is the reference). Phase 3 gate (shell, guard, state components exist).

**Work — required:**

- [ ] Profile: `app/profile/page.tsx` + `ProfileForm.tsx` to token styling (fixes the zero-dark-variants page), `ApiError` status mapping, the Field wrapper
- [ ] Profile: `features/profile` hooks onto `apiFetch` + response schemas + keys — upsert semantics preserved exactly (protected functionality)
- [ ] Auth: `features/auth` (`useMe`) onto the same pattern; Me schema the single source; `features/auth/types.ts` deleted per Section 9.1
- [ ] Dashboard: real data where endpoints exist (e.g., actual course count via the courses query), honest coming-soon placeholders where they do not; the fabricated stats card (4 Courses / 142 Concepts) removed
- [ ] Home: token-dialect hero; decorative input made functional or removed; dead comment block and `as any` gone if Phase 1 did not take them
- [ ] Course detail + edit: shared state components; invalid ID → `notFound()`
- [ ] Navbar: mobile menu below 768px, honest labels, UserName extraction per Section 9.1
- [ ] New shared `components/CourseCard.tsx` used by the courses list and the dashboard
- [ ] Delete-course action: confirmation, mutation, list invalidation — closing the frontend/backend contract gap

**Work — recommended:**

- [ ] Storybook stories for `CourseCard` and `ProfileForm` so Chromatic guards the token migration visually (verification infrastructure only — Storybook does not freeze the visual design; see the D13 note in Phase 6)
- [ ] Dark-mode + mobile-viewport pass per route as it migrates, not as a cleanup at the end

**Deferred from this phase.** Profile subscription-and-plan card → Deferred Backlog (needs a real product feature behind it).

**Affected areas.** `app/profile/`, `app/dashboard/`, `app/page.tsx`, `app/courses/[id]/` (+ edit); `components/profile/ProfileForm.tsx`, `components/Navbar.tsx`, new `components/CourseCard.tsx`; `features/auth/` and `features/profile/`.

**Verification.**

- CI green; per-route manual checklist
- grep: no raw slate-/indigo- classes in migrated routes
- grep: no fabricated statistics in the UI
- Dark-mode pass over every migrated route
- Mobile viewport pass (<768px): navigation usable, no horizontal scroll
- Delete flow end to end — confirm, gone from list without refresh
- Profile: fresh account create → edit → reload — data persists (upsert intact)

### Phase gate — before starting Phase 5

- [ ] All routes migrated; no page-level state markup remains
- [ ] TypeScript, lint, and build pass
- [ ] Dark-mode and mobile passes recorded per route
- [ ] Delete-course flow green end to end
- [ ] Protected functionality: course CRUD and profile upsert unchanged (plus delete, now surfaced)
- [ ] Changes reviewed by Seyam

**Owner / execution model.** The two engineers take routes in parallel; GLM implements instructed tasks per route; BigPickle produces per-route affected-file inventories; Seyam reviews each PR. Watch the two standing risks here: migration fatigue and review bandwidth — PR sizes stay capped even when the phase feels long.

**Migration map.**

| Current | In this phase | Target |
|---|---|---|
| Two styling dialects; profile breaks in dark mode; dashboard shows fabricated numbers; delete endpoint never called | Token-only pages with the Field wrapper; honest data or honest placeholders; full CRUD surfaced; mobile menu | Every route on the foundation; grep-verifiable token-only rule; no fabricated content in the UI |

---

## 10. Phase 5 — Arabic/RTL Readiness & Accessibility Baseline

| Status | Estimate | Decisions implemented | Depends on |
|---|---|---|---|
| NOT STARTED | ~1 sprint | D10 (full rails), D17 | Phase 4 gate |

**Parallel note.** May overlap the tail of Phase 4 if the remaining routes are already final.

**Goal.** Make the RTL rails real: logical utilities everywhere, Storybook verification under RTL and dark, an axe-clean primitive set, keyboard-checked critical flows.

**Why.** The product's stated identity is Arabic-first, while its delivered baseline remains English + LTR (D10 clarification, §1). The rails went in during Phase 3. This phase verifies them across the final component set while the codebase is still small enough that the audit is a sprint, not a quarter. The boundary is explicit: rails only — no translation work, no message catalogs, no i18n framework; that decision stays deferred with its trigger. LTR/English is not replaced: this phase makes RTL a first-class verified direction — nothing more.

**Prerequisites.** Phase 4 gate (components final — auditing them twice would be waste).

**Work — required:**

- [ ] Logical-utility audit: `ml-`/`mr-`/`pl-`/`pr-`/`text-left`/`text-right` → `ms-`/`me-`/`ps-`/`pe-`/`text-start`/`text-end` across `components/` and migrated pages
- [ ] `.storybook/preview.tsx` — toggleable RTL/direction view for shared components
- [ ] Storybook pass: `components/ui`, the state trio, `CourseCard`, `Navbar`, forms — verified under RTL and dark
- [ ] Triage existing axe violations in `ui/` stories; after triage, flip the a11y addon to error for `ui/` stories so CI fails on new violations
- [ ] Keyboard-only completion of the CRUD smoke (manual now; assertions land with the Phase 6 E2E suite)
- [ ] Token contrast check for text-on-surface pairs; fix failing pairs in the token file

**Work — recommended:**

- [ ] Document the a11y baseline (checked vs known-unchecked), ready for the Phase 6 README
- [ ] Demonstrate the axe flip honestly: a deliberately violating story fails, then reverts

**Deferred from this phase.** Full i18n framework — deferred with its trigger (real Arabic UI copy, or a second scheduled language).

**Affected areas.** `components/` (audit); `.storybook/preview.tsx`; migrated pages (residual physical utilities); `globals.css` token contrast only if a pair fails.

**Verification.**

- No visible change in LTR English — screenshot comparison where stories exist
- RTL Storybook pass screenshots recorded for shared components
- `ui/` stories axe-clean; the flip demonstrably fails a violating story
- Keyboard-only CRUD smoke completes

### Phase gate — before starting Phase 6

- [ ] Audit complete — grep finds no physical-direction utilities in shared components
- [ ] a11y addon flipped to error for `ui/` stories; CI green with the flip
- [ ] RTL + dark Storybook verification recorded
- [ ] TypeScript, lint, and build pass
- [ ] Changes reviewed by Seyam

**Owner / execution model.** One engineer owns the utility audit; the other the Storybook/a11y work. GLM implements the mechanical replacements. BigPickle can pre-inventory physical-utility usage. Seyam reviews and enforces the scope boundary — translation work is out of scope.

**Migration map.**

| Current | In this phase | Target |
|---|---|---|
| Rails exist (dir, fonts) but components still use physical-direction utilities; a11y unchecked | Logical utilities everywhere; RTL + dark verified in Storybook; axe gates new violations in primitives | An Arabic-ready component set that flips correctly, with a documented accessibility floor |

---

## 11. Phase 6 — Testing & Observability Hardening

| Status | Estimate | Decisions implemented | Depends on |
|---|---|---|---|
| NOT STARTED | ~1 sprint | D12, D13 (full), D14 | Phases 0–4 complete; Phase 5 preferred |

**Goal.** Turn the installed-but-unwired tooling into the standing quality bar: a test script in CI, the three E2E smoke flows, Sentry wired end to end, and a README that onboards a new member in one sitting.

**Why.** The tooling is present but inert: vitest is configured with no test script (CI silently skips it), Playwright is installed with no specs, and Sentry's DSN is baked while source maps and environment labels are unwired. This phase makes every earlier phase-gate verification automatic, and writes the README that turns the modernization's exit test — a new contributor onboards by imitation — into a repeatable check.

**D13 boundary (clarification, not a new decision).** Storybook's role is development and verification infrastructure: shared UI/component development; component, state, dark-mode, RTL, and accessibility verification; visual-regression verification where applicable; documenting reusable component behavior. Stories and Chromatic runs verify components — they do not establish or freeze the final visual design; the later visual redesign (D9 clarification, §1) proceeds on top of this infrastructure.

**Prerequisites.** Phase 4 gate minimum (the flows the E2E suite exercises are stable). Phase 5 preferred (the axe flip already in CI).

**Work — required:**

- [ ] `package.json` — add the test script wiring the existing vitest + Storybook test setup
- [ ] `.github/workflows/ci.yml` — run unit tests and story tests on every PR
- [ ] `e2e/` — the three Playwright smoke specs: (1) login lands on dashboard; (2) create → read → update → delete a course; (3) profile create-then-update round trip
- [ ] Wire E2E as workflow-dispatch first; promote to required CI check after three consecutive green runs (flake discipline)
- [ ] `next.config.ts` — `withSentryConfig`; sentry configs get environment-aware sampling; source-map upload configured (needs the Sentry auth token — Pod D item)
- [ ] `frontend/README.md` — setup referencing `scripts/setup-dev.sh` and `scripts/LOCAL_SETUP.md` (from commit `95bba7a`) instead of duplicating them; the five environment variables; the conventions; the component-boundary rules from D2

**Work — recommended:**

- [ ] Verify the gate honestly: open a deliberately broken PR and watch CI reject it, then revert
- [ ] Include the Phase 5 accessibility baseline in the README

**Deferred from this phase.** Coverage gates and a component-test mandate — rejected per the architecture document (see Deferred Backlog for triggers).

**Affected areas.** `package.json`; `.github/workflows/ci.yml`; new `e2e/*.spec.ts`; `next.config.ts`; `sentry.client.config.ts` / `sentry.server.config.ts`; new `frontend/README.md`.

**Verification.**

- A deliberately broken PR fails CI, then passes after revert
- The three flows green across three consecutive runs
- A forced frontend error arrives in Sentry readable: correct environment label, source-mapped stack
- A teammate outside the frontend pod runs the app in one sitting using only the README + setup script

### Phase gate — modernization complete

- [ ] All six phases DONE — every architecture decision implemented or explicitly deferred with its recorded trigger
- [ ] The Global Definition of Done below holds, including the grep checks and the understandability exit test
- [ ] This roadmap receives its final status update and is archived as the record of what was done
- [ ] Handover to feature work: materials upload, RAG chat, knowledge graph — new domains under `features/`, not further architecture projects

**Owner / execution model.** GLM implements the wiring. BigPickle verifies nothing silently skips in CI (the exact defect this phase removes). Seyam accepts the phase and, with it, completion of the modernization.

**Migration map.**

| Current | In this phase | Target |
|---|---|---|
| vitest configured but never run; Playwright installed with no specs; Sentry DSN baked but source maps/labels unwired; no frontend README | The test script in CI; three E2E flows on dispatch; Sentry readable end to end; a README that onboards in one sitting | The standing quality bar: every PR checked by the same automated gate that verified the modernization itself |

---

## 12. Global Definition of Done

The bar for the whole modernization, not any single phase. Every item is verifiable by a grep, a command, or a demonstration.

**Automated bar (CI, blocking on every PR):**

- [ ] Typecheck passes under strict mode (`npx tsc --noEmit`)
- [ ] Lint passes (`npm run lint`)
- [ ] Build produces the standalone output (`npm run build`)
- [ ] Unit tests for `lib/` modules pass (accruing from Slice 1)
- [ ] Storybook story tests pass, including axe for `ui/` stories (from Phase 5 onward)
- [ ] The three E2E smoke flows pass (on dispatch; promoted to required when stable)

**Completion checklist:**

- [ ] Every decision in the architecture document's Section 8 baseline is implemented or explicitly deferred with its recorded trigger
- [ ] No direct `fetch` call or `NEXT_PUBLIC_` read outside `lib/api.ts` / `lib/config.ts` (grep-verifiable)
- [ ] No dead file from the architecture document's inventory remains; no `as any` casts in page code
- [ ] Staging authentication works from a non-localhost browser, and the E2E suite proves it continuously
- [ ] Manual critical-flow checklist passes on staging: login, deep-link redirect, courses CRUD incl. delete, profile upsert, logout with cache clearing, theme toggle on every route, mobile viewport, invalid-ID not-found
- [ ] **Understandability exit test:** a new contributor adds a feature-domain (hooks, schemas, keys, pages using shared state components) by copying an existing one, without reading framework code

The final item is what the whole strategy optimizes for. If imitation onboarding works, the modernization achieved its goal.

---

## 13. Deferred Backlog

| Item | Why deferred | Revisit when |
|---|---|---|
| Full i18n framework (`[locale]` routing, catalogs) | D10 rails cover present needs; a framework with no Arabic copy to manage is speculative weight | Real Arabic UI copy exists, or a second UI language is scheduled |
| BFF / server-session auth (httpOnly cookies) | In-memory tokens + PKCE are the deliberate accepted choice (D6); the protocol was just stabilized | A stated security/compliance bar, or authenticated server-rendered pages |
| React Hook Form | Manual forms + Zod + the Field wrapper remain pleasant at two small forms | A form exceeds ~8 fields or needs cross-field async validation |
| Generated API clients (openapi-typescript, orval, hey-api) | Six fetch sites collapse into one 80-line helper; a generator adds ceremony at this scale | ~25+ endpoints, or a second consumer of the same types |
| Performance engineering (virtualization, streaming, server components) | No measured problem exists on a ~2,500-line client-rendered app | RAG chat / knowledge-graph lands, or a measured regression appears |
| CSP / security headers | Needs the production domain and TLS termination (Pod D's ingress work) | The first production domain goes live |
| Component-test mandate / coverage targets | The agreed bar is the three E2E flows, story tests, and strict types | A shared component breaks in a way story tests and types did not catch |
| Sidebar navigation shell | Exactly one navigation level exists today | A second navigation level actually exists (course-internal structure) |
| Profile subscription-and-plan card | Currently displays fabricated plan data; a real version needs a product feature behind it | Product decides to build subscription/plan management |

---

## 14. Scope Guard

This roadmap modernizes the existing frontend's architecture. It does not grow the product, redesign the backend, or chase technologies for their own sake. Any addition to an in-flight phase goes through Seyam as an explicit decision — with a re-read of the affected decision in the architecture document if it touches one — never through a quiet pull request.

**Not automatically included:**

- New product features — materials upload, RAG chat, knowledge graph arrive **after** Phase 6 as feature work under `features/`
- Backend redesign — the only named integration points are the realm redirects (Phase 1) and the Sentry auth token (Phase 6), both with Pod D
- Unrelated infrastructure work, CI tooling churn, repository-structure experiments
- Speculative scalability or performance work — no measured problem exists
- Replacing working technologies because newer ones exist — the dependency list is current and coherent; churn is pure cost
- Unrelated UI polish — visual changes exist only where a decision requires them

**Visual redesign is planned later work, not a freeze.** The current look is not the final design (D9 clarification, §1): a later part of the modernization intentionally redesigns UI/UX, visual identity, colors, typography, spacing, and component appearance on top of the stable token foundation, as its own planned workstream. Until Seyam charters that workstream, visual changes in Phases 0–6 stay limited to what the accepted decisions require — a boundary that prevents scope creep without freezing today's visuals as final.

**Explicitly rejected (full reasoning in architecture document Section 16):**

- Micro-frontends or any repo/module splitting — one deployable, one team, ~2,500 lines
- Monorepo restructuring or package extraction (`ui` / `design-system` / `api` packages)
- A global state library (Redux/Zustand/Jotai), event buses, or plugin architectures — verified unnecessary
- An API framework or client generator at current scale
- A universal configurable DataTable or mega-Form component — one list page and two small forms exist
- Custom routing, data-fetching, or DI abstractions over the stack's own APIs
- A design-system program (tokens-as-package, contribution tooling, Figma sync)
- Coverage-gated testing programs
