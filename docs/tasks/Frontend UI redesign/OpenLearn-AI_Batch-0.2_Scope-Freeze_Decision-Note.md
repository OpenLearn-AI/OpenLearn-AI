# OpenLearn-AI Frontend — Batch 0.2 Scope Freeze (Decision Note)

**Batch:** 0.2 — Scope freeze · **Executed:** 2026-10-15 · **Executor:** GLM (Super Z) · **Authorized by:** Seyam, 2026-10-14 ("let's start the next phase", after Batch 0.1 completed)

## 1. Purpose and authority

This note is the "short decision note in repo docs" that roadmap v2.0 §14 names as Batch 0.2's deliverable. Its single function is to **freeze** — to make three sections of roadmap v2.0 the authoritative, un renegotiable classification for the rest of the redesign, to give every finding ID exactly one disposition, and to record the demo journey candidate. It ratifies; it does not modify. The roadmap DOCX is untouched by this batch, and nothing in the application changes.

From the moment this note is applied:

1. **Roadmap v2.0 §6** (Backend → Frontend Coverage Matrix) is the authoritative capability classification. No batch may build a surface that the matrix does not classify, and no capability may move tiers except by the evidence-driven movement rule (§13): a contract landing in `docs/openapi.json` (verified, never assumed) or an executed, ledger-recorded batch.
2. **Roadmap v2.0 §22** (Explicit Non-Goals) is the authoritative exclusion list. Relitigating an exclusion requires new evidence and a new authorized batch — not a silent addition.
3. **Roadmap v2.0 §19** (Demo Journey) is the authoritative demo candidate, finalizable in Batch 2.1.
4. **The modernization accomplishments (§2) are permanently out of scope** — guard consolidation, API boundary, schema-driven slices, async-state kit, E2E trio, staging pipeline are protected logic the redesign changes presentation around, never behavior.

## 2. Frozen capability classification (roadmap v2.0 §6 + §13)

Every backend capability relevant to a user-facing workflow sits in exactly one classification tier:

| Tier | Contents | Count / disposition |
|---|---|---|
| **A — Consumable now** | `GET /auth/me`; profile read/update (×2); course CRUD (×5); material presigned upload, registration, listing, status (×4) | 12 operations. 8 consumed today; the 4 materials operations are scheduled scope (Batch 4.3). No tier-A item lacks a named frontend surface |
| **B — Backend exists, frontend blocked** | *(none)* | Empty — every existing user-facing capability is consumed or schedulable without blockers. Recorded deliberately: this is the cleanest possible coverage state |
| **C — Future (44-week plan)** | Extracted document text (W9), admin reprocess (W9, shape TBD), retrieval search (W10), chunk inspection (W11), v0.3 demo polish (W12), ranked citations (W13), RAG cited answers (W14), chat sessions + streaming (W15–16), enrollment + student flow (W17), knowledge graph / quizzes / mastery / analytics (W21+) | Each IA-reserved as a course-hub slot (§9) or honest-copy-only; each names its missing contract; none may be coded against until its endpoint exists in `docs/openapi.json` |
| **D — Internal / infrastructure, no UI** | `/health`, `/metrics`, Celery pipeline internals, LiteLLM gateway traffic, observability stack (Prometheus/Loki/Alloy/Grafana/Langfuse-off/Flower), MinIO storage internals, OpenAPI tooling | No user-facing UI is designed, implied, or faked — status polling through the four-value literal is the only user-visible reflection of the pipeline |
| **E — Intentionally not exposed** | Admin UI (role unenforced — `require_admin` has zero call sites), v4 spec §22.4 planned-only endpoints, server-side route protection (client guard stays; middleware excluded) | Excluded with reasons in §22; revisit only on new backend evidence |

The §13 visibility snapshot at freeze time: **Already implemented** — 8 of 12 operations, 9-route shell, auth guard, async-state kit, staging deploy. **Implement next** — the Phase 1 closure set, role-aware presentation (2.2/3.3/4.2/4.3), the materials surface (4.3). **Blocked** — extracted-text viewer and reprocess control (both W9, no contract). **Future** — search, chunks, citations, chat/streaming, enrollment, KG/quizzes/analytics.

## 3. Finding disposition register (every ID in exactly one place)

The freeze validation (roadmap §14, Batch 0.2) requires every finding `F1–F6, W1–W8, S1–S11` to sit in exactly one bucket, defer entry, or exclusion. The register below is that record. Dispositions cite the batch that owns the work; "open" status reflects the Batch 0.1 re-verification at `699c496` (baseline record §4) — every listed finding was confirmed present in code on 2026-10-14.

| ID | Finding (v1.x register definition, carried into v2.0 where open) | Disposition | Status |
|---|---|---|---|
| F1 | Sentry environment-label chain broken in deployment wiring (Dockerfile ARG, deploy build-arg + heredoc, compose, env example) | **Fix — Batch 1.3** | Open (all five links verified) |
| F2 | — | **Unassigned ID** — no finding carries F2 in the v1.3 or v2.0 register (zero occurrences in either document outside the range notation; mechanically verified) | Retired ID |
| F3 | Edit-mode `CourseForm` lacks `key={course.id}` — wrong-record write | **Fix — Batch 1.1** | Open |
| F4 | `ProfileForm` not re-keyed on profile identity (null→object never re-seeds state) | **Fix — Batch 1.1** | Open |
| F5 | `created_at` offset risk (schema demands offset-bearing datetime) | **Settled 2026-10-14 — Batch 1.4 scope reduced** (see §4) | Closed by evidence |
| F6 | `safeRedirectTarget` comment/code drift | **Fix — Batch 1.1** | Open |
| W1 | No global 401 session-recovery flow (static expired-session strings in two forms) | **Fix — Batch 1.2** | Open |
| W2 | — | **Unassigned ID** (same verification as F2) | Retired ID |
| W3 | — | **Unassigned ID** (same verification as F2) | Retired ID |
| W4 | Hook misfiled in component layer (`UserName.tsx` exports a hook) | **Refactor — Batch 3.3** (relocate to `features/auth`, logic identical) | Open |
| W5 | `shadcn` CLI shipped as a runtime dependency | **Fix — Batch 3.2** (vendor stylesheet, drop dependency) | Open |
| W6 | Six devDependencies pinned to `"latest"` | **Defer — Batch 5.3** (pin before final staging deploy; deliberate hardening-phase placement) | Open (deferred by schedule) |
| W7 | `chromaui/action@latest` unpinned in `storybook.yml` | **Defer — Batch 5.3** (pin action digest; same rationale as W6) | Open (deferred by schedule) |
| W8 | No `engines` field (Node alignment with CI/deploy) | **Fix — Batch 1.3** | Open |
| S1 | Dashboard placeholder dishonesty (5 "Coming soon" strings, mislabeled Open Chat / View Graph buttons, Active Materials mislabel) | **Settle — Batch 2.2** (real metrics: course count, profile completeness, recent courses) | Open |
| S2 | Landing markets unimplemented AI (RAG chat, quizzes, flashcards, knowledge graph) | **Settle — Batch 2.2** (honest copy) | Open |
| S3 | Register stub — silent failure, no states | **Fix — Batch 1.2** | Open |
| S4 | Unused list-filters key factory (dead code) | **Remove — Batch 3.2** | Open |
| S5 | Unused badge component | **Use or delete — Batch 3.2** | Open |
| S6 | — | **Unassigned ID** (same verification as F2) | Retired ID |
| S7 | Dead hooks alias | **Remove — Batch 3.2** | Open |
| S8 | `(auth)` route group lacks `error.tsx`/`loading.tsx` | **Fix — Batch 1.2** | Open |
| S9 | Unreachable `(app)` loading boundary — keep or remove | **Decide — Batch 3.2** (Open Question #6; trivial, no functional consequence) | Open decision |
| S10 | Success token `text-success-foreground` invisible in both themes | **Fix — Batch 1.1** (`text-success`) | Open |
| S11 | — | **Unassigned ID** (same verification as F2) | Retired ID |

Bucket totals: **20 findings with one disposition each** (5 fix-batches in Phase 1, 5 settled/removed in 3.2, 1 relocation in 3.3, 2 settlements in 2.2, 2 deliberate defers to 5.3), plus **5 retired IDs** recorded above so the ranges close cleanly. No finding sits in two places; no finding is silent.

The two upstream items the frontend explicitly does **not** absorb (recorded so they are not mistaken for omissions): the course owner-scoping defect (backend authorization defect — flagged upstream, never worked around; Open Question #7) and the Week 9 reprocess-endpoint shape (backend pod defines it; the frontend adapts only when the contract lands).

## 4. F5 settlement decision (Batch 0.1 evidence → Batch 1.4 direction)

Batch 0.1's local verification (2026-10-14, run `run-20261014-190840`) answered the question roadmap §14 left to 0.1/1.4: **the live API emits offset-bearing datetimes** — authenticated `GET /v1/courses` returned 5/5 `created_at` values with a timezone offset (sample `2026-10-14T15:52:48.551399Z`), captured through the real Keycloak browser login flow with no auth weakening. Therefore:

- `features/courses/schemas.ts` `created_at: z.string().datetime({ offset: true })` is **correct as-is and frozen** — no accept/normalize workaround is written, and no note to the backend pod is needed (the naive-emission contingency is dead).
- **Batch 1.4's scope reduces to its second half only:** the real-metric inventory for the dashboard (course count, profile completeness — no analytics endpoints exist). Unit coverage for both datetime shapes is no longer required by F5; if written, it is ordinary hardening, not settlement work.

## 5. Environment and CORS posture at freeze time

- **Open Question #1 (F5) — CLOSED** as above.
- **Open Question #2 (staging CORS live preflight) — OPEN, carried to Batch 2.1.** The LOCAL preflight is confirmed (2026-10-14: HTTP 200, origin echo for `http://localhost:3000`, `authorization` header allowed, credentials true) — the compose-provided `CORS_ORIGINS` mechanism works end to end for the local origin. Seyam scoped the 0.1 verification to the local project, so the staging-host confirmation is outstanding; it is a named input to 2.1's environment decision and can be produced anytime via `scripts/run-batch-0.1-local-verification.sh --with-staging-preflight` from a staging-reachable host.
- **Open Question #4 (demo environment) — default recorded:** staging preferred pending the staging preflight; **local dev is the documented fallback**. The actual choice is Batch 2.1's decision, made with Q2's answer in hand.
- This freeze does **not** pass Gate A on staging CORS: Gate A is passed on the strength of the local preflight confirmation plus the owner's explicit scoping decision, with the staging confirmation recorded as the one carried-over evidence item (see ledger, Gate A entry).

## 6. Frozen demo journey candidate (roadmap v2.0 §19; finalized in 2.1)

The supervisor presentation is the existing journey made coherent, not a new product. Locked candidate: **land on the public page (honest copy) → register through Keycloak (completed flow) → arrive at a role-aware dashboard with real metrics → create a course → open the detail hub → edit it → exercise the delete confirmation → visit profile (complete it — the dashboard metric reflects it) → logout.**

Standing constraints, frozen with the candidate: the materials walk (upload → pending → processing → ready, or honest failure) joins the journey only if adopted in the 2.1 decision (Open Question #5) and requires the instructor-role course-owner test user either way (provisioned in 2.1 — prerequisite for the 4.3 walkthrough); demo data is real data created through the real product flow (a handful of meaningfully titled courses, a filled profile) with the dataset steps documented and rehearsed — no seed script is added; AI chat, quizzes, citations, and knowledge-graph surfaces are never demoed as UI (§22 forbids faking them).

## 7. Exclusion list ratification (roadmap v2.0 §22)

The §22 exclusions are ratified verbatim as the authoritative list: server-side route protection (middleware); new auth/state-management/form systems; UI for capabilities without contracts (search, chat, citations, chunks, extracted text, enrollment — the no-fake-AI rule generalized); retry/reprocess UI until the Week 9 endpoint's shape stabilizes; fake progress percentages, processing phases, AI reasoning UI; AI chat/quizzes/flashcards/knowledge-graph UI; pagination/ETags/optimistic concurrency; the course owner-scoping fix; i18n framework and full Arabic conversion (RTL-readiness via logical properties stays); coverage thresholds; analytics integration; new component-library dependencies (the only dependency change is removing one — W5 — and pinning devDependencies in 5.3); coding against v4 spec §22.4; re-doing modernization work; admin UI.

One refinement is already encoded in §22 and repeated here for visibility: **"Retry/reprocess UI today — REFINED"** — the Week 9 endpoint converts the old outright exclusion into a classified, tracked capability (coverage matrix C, W9) whose UI becomes buildable only when the contract lands with a stable shape.

## 8. Freeze validation (roadmap §14, Batch 0.2)

| Validation rule | Result | Method |
|---|---|---|
| Every capability in the coverage matrix sits in exactly one tier | **PASS** — §2 table: 12 tier-A operations, tier B empty (recorded), 10 tier-C capability groups, 7 tier-D items, 3 tier-E items; each §6 row carries exactly one class letter and no frontend-relevant capability is silent | Roadmap v2.0 §6 read in full; tier assignment cross-checked against the ledger's coverage summary and `docs/openapi.json` (12 operations + 2 infrastructure endpoints) |
| Every finding F1–F6, W1–W8, S1–S11 sits in exactly one bucket, defer entry, or exclusion | **PASS** — §3 register: 20 live findings each in exactly one disposition; 5 IDs (F2, W2, W3, S6, S11) recorded as unassigned/retired | Occurrence audit across roadmap v2.0 (extracted from the DOCX), roadmap v1.3 (extracted from git history `ad64e0c`), and the repo tree; each ID's batch assignment cross-checked against §14's batch objectives and §21's Gate B closure list; all live findings re-verified present in code at `699c496` by Batch 0.1 |
| Must NOT change: the modernization accomplishments (§2) | **PASS** — no application file touched by this batch | `git status` scope check at patch generation |

## 9. Decision record

| Field | Value |
|---|---|
| Decision | Phase 0 scope is frozen as recorded in §§2–7; Gate A's functional-reality condition is satisfied |
| Authorization | Seyam, 2026-10-14 — "let's start the next phase", issued after Batch 0.1 completed (local verification run PASSED, exit 0) |
| Execution | GLM (Super Z), 2026-10-15, documentation-only, against `frontend-redesign` @ `7ebe978` |
| Effect | Phases 1–5 execute exactly this scope. Any scope change — new finding, reclassification, exclusion relitigation — requires new evidence, a decision record in this file's lineage, and Seyam's explicit authorization of the batch that carries it |
| Next | **Batch 1.1 — Correctness fixes on core flows (F3, F4, S10, F6)** — awaiting Seyam's explicit authorization per the lifecycle rules |
