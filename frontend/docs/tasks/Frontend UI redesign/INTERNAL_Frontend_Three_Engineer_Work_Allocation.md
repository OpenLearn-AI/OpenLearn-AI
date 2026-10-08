# OpenLearn-AI Frontend — Internal Three-Engineer Work Allocation

> **UNOFFICIAL INTERNAL PLANNING DOCUMENT — DO NOT COMMIT OR PUSH.**
> This file is a team-coordination aid for the three frontend engineers. It is **not** a roadmap
> deliverable, must **not** be added to `progress.md` as batch output, and must **not** become part
> of the official execution record.

| | |
|---|---|
| Prepared | 2026-10-04 |
| Working branch at planning time | `frontend-redesign` @ `8ce12e749fdab3d486aeeaa5e293fa3128af8d3e` (in sync with `origin/frontend-redesign`, clean tree) |
| Built from (authoritative) | `frontend/docs/OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx` — the roadmap |
| | `frontend/docs/OpenLearn-AI_Frontend_Execution_Progress.md` — the execution ledger |
| Also consulted | `GLM-batch-n-patch-lifecycle-rules.md` (repo root) — the lifecycle every batch follows |
| Ledger state at planning time | All 18 batches **NOT STARTED**; no gate passed; "awaiting approval to start Batch 0.1" (verification pass of 2026-10-01; HEAD has since moved only by documentation commits `c876e6b` and `8ce12e7`) |

---

## 1. Purpose and Authority

This document exists so that three engineers can execute the eighteen official roadmap batches
without stepping on each other. The roadmap defines **what** must be done, in which order, and
under which gates; the ledger records **what was actually done**. Neither document, however,
says **who** owns each batch, when a second engineer may start, or how independently produced
patches are sequenced for review and application. That is the only gap this document fills. It
converts the roadmap's dependency structure into named ownership and a coordination rhythm the
three engineers can consult daily.

This document is an **unofficial internal planning aid**. It carries no authority over the
roadmap, over `progress.md`, or over the GLM Batch & Patch Lifecycle Rules
(`GLM-batch-n-patch-lifecycle-rules.md`). If anything here contradicts those sources, those
sources win, and the contradiction should be raised with the team lead so this file can be
corrected. Nothing in this document replaces the per-batch implementation prompt or the lifecycle
rules — every engineer still follows the full lifecycle (verify repo state → read roadmap and
ledger → record starting state → implement one batch → verify → update `progress.md` → generate a
complete patch including untracked files → verify patch access → report → stop). This document
only answers the coordination questions the lifecycle deliberately leaves open: ownership,
sequencing, prerequisites, and review responsibility.

Assignments and statuses in this document are a **snapshot of the ledger as of the planning
date**. They must be re-checked against the live ledger before any batch is started. If the
ledger shows work already completed, in progress, or blocked, the ledger — not this snapshot —
governs. Engineers must not use this document to claim work is done, to bypass a gate, or to
start a batch whose prerequisites are unsatisfied.

**Source reconciliation note.** The roadmap and the ledger were cross-checked during planning
and agree on substance: the ledger's own verification pass confirms all eighteen batches are
executable as written, with its three evidence corrections already folded into roadmap v1.1 and
two additional mislabels folded into Batch 2.2. Two non-material discrepancies were found and are
recorded in Section 9 (items A1 and A2) rather than silently resolved: the ledger's Current State
still cites the `staging` branch at `c51f3f1` while the team now works on `frontend-redesign`
(application code unchanged between the two — `c51f3f1` is an ancestor of the current HEAD), and
Batch 1.1's dependency row says "start immediately" while the phase structure places Phase 1
after Gate A.

---

## 2. Team Roles

**Engineer 1 — Sadin (team lead, hands-on implementer).** Sadin owns the plan's leadership duties
*and* a full implementation load: he runs the initial demonstration batch, takes the first
conventional code batch, holds the two highest-stakes redesign moments (application shell; detail
and forms with the CRUD regression net), and closes the roadmap with the final staging validation
and demo dry run. Between his own batches he coordinates gate readiness, reviews every patch,
acts as the single application point for patches per the lifecycle rules, and carries the
team-lead decisions the roadmap assigns to that role (Week 8 mapping confirmation, E2E
re-sequencing sign-off). Sadin's leadership role does **not** authorize him to bypass gates,
reorder batches silently, mark work complete that was not verified, or apply a patch whose
verification was not actually run. When Sadin implements, he is subject to exactly the same
lifecycle, gates, and review as the other two engineers.

**Engineer 2 — Engineer B (implementation engineer).** Engineer B owns complete batches end to
end under the standard lifecycle: reading the execution context, implementing only the assigned
batch, running and honestly reporting verification, updating the ledger, and producing a complete
patch. B's line of work is the authentication and public-surface thread (auth surface completion
in Phase 1, design tokens in Phase 3, auth screens and landing in Phase 4, the profile/global-states
closers, and test-suite alignment in Phase 5). B also serves as the advisory reviewer for
in-flight batches whose next chain position B owns — advisory only: the lifecycle's review and
application authority stays with the lead.

**Engineer 3 — Engineer C (implementation engineer).** Engineer C owns complete batches end to
end under the same lifecycle. C's line of work is the data-contract and environment thread (data
contract settlement and observability/infrastructure closure in Phase 1, demo runbook and
environment lock in Phase 2, design-system foundations in Phase 3, the dashboard and courses-list
redesign in Phase 4, and the verification runs in Phase 5). C's batches carry the heaviest
external dependencies (staging deploy window, Sentry access, the CORS answer), so C coordinates
those prerequisites with the lead early rather than discovering them mid-batch.

Engineer B and Engineer C are placeholders, as required: no names, skill levels, or individual
strengths are invented for them. Effort levels in Section 4 describe the **batches**, not the
people. Neither engineer may trade batches with another engineer without the lead recording the
swap — ownership changes must never make the ledger or this document ambiguous.

**Role-name note (do not silently resolve).** The official sources name a person called
"Seyam" as the team lead, decision owner for Open Questions 1 and 4, and — per lifecycle rule 8 —
the person who reviews, applies, commits, and pushes patches. This plan's Engineer 1 is Sadin,
per the team brief. The team should confirm the mapping once: if Sadin is the person the official
documents call "Seyam", every "team lead" duty in this document is his; if the roles are split
across two people, the lead duties described here attach to whoever actually holds the
publisher/decision role, and the affected lines in Sections 5–7 should be amended.

---

## 3. Allocation Summary

| Engineer | Assigned official batches | Main responsibility areas | Relative workload (qualitative estimate) | Key dependencies / limitations |
|---|---|---|---|---|
| **Sadin** (Engineer 1, team lead) | 0.1 Baseline verification run · 1.1 Correctness fixes on core flows · 2.2 Honest-surface settlement · 3.3 Application shell · 4.3 Course detail, forms, and delete confirmation · 5.3 Staging validation and demo dry run | Initial workflow demonstration; core-flow correctness; honest dashboard/landing content; application shell; the detail/forms/delete redesign guarded by the CRUD E2E net; final staging validation and dry run; gate coordination, patch review and application, Week 8 / E2E-re-sequencing sign-offs | About one third of implementation effort, weighted toward the widest-verification and highest-risk batches (first code batch, shell, forms, final dry run); lead duties (review, gate coordination, external sign-offs) come **on top** and are not counted as batches | Cannot start Phase 1 before Gate A; 5.3 needs the full chain plus the 2.1 runbook; coordinates but does not own the infra items (CORS fix, Sentry secrets) that several batches depend on |
| **Engineer B** | 0.2 Scope freeze · 1.2 Authentication surface completion · 3.1 Design direction and tokens · 4.1 Auth screens and landing page · 4.4 Profile, global states, responsive/RTL pass · 5.1 Test suite alignment | Scope freeze and Gate A packet; the auth-surface thread (W1/S3/S8) and its Phase 4 public-surface execution; token layer and design ADR; the Gate E closing pass (profile, global states, RTL); E2E and viewport alignment | About one third of implementation effort, weighted toward the highest-risk Phase 1 batch (1.2 touches protected Keycloak logic) and the two chain-closing batches (4.4, 5.1) | 1.2 waits for Sadin's 1.1 (shared files: `CourseForm.tsx`, `ProfileForm.tsx`); 3.1 needs Gate C; 5.1 needs Gate E; login-E2E verification needs credentials |
| **Engineer C** | 1.4 Data contract settlement · 1.3 Observability and configuration closure · 2.1 Demo journey and environment lock · 3.2 Design system foundations in code · 4.2 Dashboard and courses list · 5.2 Verification runs | Data-contract settlement (F5) and metric inventory; Docker/deploy/Sentry wiring (F1 chain, W8) and Node alignment; demo runbook, environment and dataset procedure; primitive refinement, dialog extraction, hygiene removals; dashboard/list pattern; promotion runs, a11y run, theme/direction sweep | About one third of implementation effort, weighted toward infrastructure coordination and the environment/verification thread that the demo ultimately stands on | 1.4 needs Batch 0.1's F5 answer; 1.3 needs a staging deploy window and Sentry build-time secrets; 2.1 needs the Gate B pass and the CORS answer (OQ3) for the environment decision; 5.2 needs staging deployed with the final build |

**Effort profiles per engineer (estimated, qualitative — L = low, M = medium, H = high; these
describe batch scope and risk, not hours, and are labelled estimates because the roadmap provides
no time data):**

- Sadin: 0.1 **M** · 1.1 **M** · 2.2 **M** · 3.3 **M–H** · 4.3 **H** · 5.3 **M**
- Engineer B: 0.2 **L** · 1.2 **H** · 3.1 **M** · 4.1 **M** · 4.4 **M–H** · 5.1 **M**
- Engineer C: 1.4 **L–M** · 1.3 **M** · 2.1 **L–M** · 3.2 **M–H** · 4.2 **M** · 5.2 **M**

**A note on batch counts.** The split happens to be six batches each, but that is a *consequence*
of the roadmap's structure, not a symmetry target. Thirteen of the eighteen batches sit in strict
serial chains (0.1 → 0.2; 3.1 → 3.2 → 3.3; 4.1 → 4.2 → 4.3 → 4.4; 5.1 → 5.2 → 5.3, plus 1.1 → 1.2),
so with three engineers the chain work must interleave owners almost evenly; genuine parallelism
exists only in Phase 1 (1.1 ∥ 1.4 ∥ 1.3, file-disjoint) and Phase 2 (2.1 ∥ 2.2, file-disjoint).
The design criteria actually applied were dependency safety, thread continuity (Section 4),
risk distribution, and Sadin's leadership-plus-hands-on profile — in that order. The weighted
effort and risk shapes differ by engineer even where the counts coincide, as the profiles above
show.

---

## 4. Detailed Batch Assignment Register

Every official batch appears below with its roadmap identity preserved (phase, batch ID, official
title). "Verified status" reflects the ledger at planning time; **re-check the live ledger before
starting any batch**. Objective, prerequisites, validation, and completion criteria are faithful
summaries — the roadmap sections cited remain the full specification, and the per-batch
implementation prompt plus lifecycle rules govern execution. Effort labels are estimates.

### Phase 0 — Current-State Lock

**Batch 0.1 — Baseline verification run** — roadmap Section 8
- **Verified status:** NOT STARTED; the ledger's Current State names it "next up".
- **Primary owner:** Sadin — the initial demonstration batch (rationale in Sections 5 and 11).
- **Objective / deliverable:** Re-verify the investigation's machine-checkable claims and produce
  the baseline record every later gate cites: recorded runs of lint, typecheck, unit, storybook,
  build; the 3 E2E specs with credentials; one authenticated `GET /v1/courses` (the F5 offset
  check); a CORS preflight against the staging API; baseline notes. Read-only — nothing in the
  application changes; failures are recorded and routed into Phase 1, never hot-fixed here.
- **Prerequisites:** Local stack running; E2E credentials available; staging reachable.
- **Earliest permitted start:** Immediately — no batch or gate prerequisite; this is the roadmap's
  first batch.
- **Relative effort (estimate):** Medium — no code changes, but wide verification coverage and
  environment dependence (credentials, staging, dev stack).
- **Verification / completion:** VERIFY F5 (does `created_at` carry an offset?) and VERIFY the
  staging CORS preflight answer; all six scripts exit 0 or their failures are documented as Phase 1
  inputs; completion = baseline record exists and every Bucket A item is confirmed or reclassified
  with evidence.
- **Overlap / coordination risks:** None in code (read-only). The 0.1 patch will consist of the
  ledger update plus the baseline-record note — a useful demonstration that a read-only batch still
  produces a complete patch under the lifecycle. The F5 and CORS answers unblock 1.4 and inform
  2.1, so the record must be written where the other engineers can cite it.
- **Reviewer / decision-maker:** Sadin implements; patch review/application follows the lifecycle
  (lead, or the confirmed publisher role — see the role-name note in Section 2). B and C observe as
  the designated reviewers-in-waiting for their own first batches.

**Batch 0.2 — Scope freeze** — roadmap Section 8
- **Verified status:** NOT STARTED.
- **Primary owner:** Engineer B — first batch, deliberately low-risk and documentation-only, under
  close lead review, so B also learns the lifecycle before the high-risk 1.2.
- **Objective / deliverable:** Freeze the classification (roadmap Section 3 becomes authoritative),
  the exclusion list (Section 16), and the demo journey candidate (Section 5), recorded as a short
  decision note in repo docs; no application files change.
- **Prerequisites:** Batch 0.1 results (the baseline record). The team-lead Week 8 confirmation
  (Open Question 1) is desired but explicitly not blocking.
- **Earliest permitted start:** As soon as Sadin's 0.1 baseline record exists.
- **Relative effort (estimate):** Low.
- **Verification / completion:** Every flag F1–F6, W1–W8, S1–S11 sits in exactly one bucket, defer
  entry, or exclusion; completion = **Gate A** — functional reality is known and agreed.
- **Overlap / coordination risks:** None in application code. Touches repo docs only; must not
  duplicate or rewrite the roadmap — it ratifies what the roadmap already says.
- **Reviewer / decision-maker:** Sadin reviews; Gate A readiness is coordinated by Sadin.

### Phase 1 — Minimal Functional Closure

**Batch 1.1 — Correctness fixes on core flows** — roadmap Section 9
- **Verified status:** NOT STARTED. Note the dependency nuance recorded as A2 in Section 9.
- **Primary owner:** Sadin — the first conventional code-change batch, continuing his
  demonstration with the full edit-verify-ledger-patch cycle on real code.
- **Objective / deliverable:** Close the wrong-behavior defects on demo-critical pages: F3
  (`key={course.id}` on the edit-mode CourseForm), F4 (re-key ProfileForm on profile identity), S10
  (swap `text-success-foreground` → `text-success`), F6 (align `safeRedirectTarget` with its
  comment or its behavior). Files: `courses/[id]/edit/page.tsx`, `profile/page.tsx`,
  `components/profile/ProfileForm.tsx`, `components/auth/LoginForm.tsx`.
- **Prerequisites:** Gate A passed (phase ordering; see A2 for the documented nuance). No batch
  prerequisites — the roadmap's own dependency row says "None; start immediately".
- **Earliest permitted start:** After Gate A.
- **Relative effort (estimate):** Medium — small diffs, but the full verification net runs.
- **Verification / completion:** E2E `courses-crud` and `profile-roundtrip` stay green; manual
  light **and** dark check of the success message (the current token is invisible in both themes);
  unit suite untouched. Completion: edit A→B saves B's values; profile create-then-edit re-seeds;
  success feedback readable in both themes.
- **Overlap / coordination risks:** `CourseForm.tsx` and `ProfileForm.tsx` are touched again by
  1.2 (B) and later by 4.3/4.4 — 1.1 must be applied before 1.2 starts. The 1.1 key fixes are
  protected logic in later batches.
- **Reviewer / decision-maker:** Sadin implements; B is the advisory reviewer (owns the next
  chain position).

**Batch 1.2 — Authentication surface completion** — roadmap Section 9
- **Verified status:** NOT STARTED.
- **Primary owner:** Engineer B.
- **Objective / deliverable:** Complete the auth surface: global 401 recovery (W1 — clear query
  cache, route to login with `redirectedFrom`, replacing the two forms' static session-expired
  strings), a real register flow (S3 — error, loading, null-client states, theme parity), and
  styled `(auth)` error/loading boundaries (S8). Files: `lib/query-provider.tsx`,
  `lib/auth-context.tsx`, `lib/keycloak.ts`, `app/(auth)/register/page.tsx`, new
  `app/(auth)/error.tsx` / `loading.tsx`, plus the two forms.
- **Prerequisites:** Batch 1.1 (shared files; also because 1.2 replaces strings in the forms 1.1
  just fixed).
- **Earliest permitted start:** After Sadin's 1.1 is applied.
- **Relative effort (estimate):** High — the largest Phase 1 batch, and it operates next to
  protected logic (Keycloak init options, guard consolidation, redirect-target logic, logout
  sequence — all must-NOT-change).
- **Verification / completion:** Forced token-refresh failure redirects to login; a throwaway user
  registers end to end; login E2E green; a forced render error shows the styled boundary.
  Completion: no path strands an expired user; register gives feedback in every failure mode; both
  route groups styled.
- **Overlap / coordination risks:** Forms (with 1.1); the new `(auth)/error.tsx` is restyled again
  in 4.4 — same owner (B) for continuity. Login E2E requires credentials.
- **Reviewer / decision-maker:** Sadin reviews (protected-logic adjacency makes this the most
  carefully reviewed Phase 1 patch).

**Batch 1.3 — Observability and configuration closure** — roadmap Section 9
- **Verified status:** NOT STARTED.
- **Primary owner:** Engineer C.
- **Objective / deliverable:** Close F1's deployment chain (the code layer already labels
  environments; only Docker/deploy wiring is missing): `NEXT_PUBLIC_SENTRY_ENVIRONMENT` build ARG
  in `frontend/Dockerfile`, matching build-arg in `deploy-staging.yml`, `SENTRY_ENVIRONMENT` in the
  frontend service of `infra/docker-compose.staging.yml`, missing keys in
  `infra/.env.staging.example`, `engines.node` in `package.json`; make the source-map secrets
  (`SENTRY_AUTH_TOKEN`/`SENTRY_ORG`/`SENTRY_PROJECT`, Pod D) available at build time or raise that
  as an infra task; trigger one test event and one error on staging with label, sample rate, and
  source maps confirmed.
- **Prerequisites:** None from other batches; **externally** dependent on a staging deploy window
  and Sentry access.
- **Earliest permitted start:** After Gate A (phase ordering), once the staging window and Sentry
  access are arranged — the lead coordinates these with infra/Pod D during Wave 2.
- **Relative effort (estimate):** Medium — the diffs are small and the paths are verified, but the
  external coordination dominates.
- **Verification / completion:** VERIFY the Sentry UI shows events tagged `staging` with resolved
  stack frames from uploaded maps; completion flips the closure-doc Sentry items to verified and
  documents CI/image Node compatibility.
- **Overlap / coordination risks:** `package.json` (engines) is also touched by 3.2 (dependency
  removal) and 5.3 (pinning) — different phases, no concurrency expected; the infra files are
  C's alone in Phase 1. Do not change the DSN handling model, Dockerfile build sequence, or deploy
  script order.
- **Reviewer / decision-maker:** Sadin reviews; infra/Pod D are external enablers, not reviewers.

**Batch 1.4 — Data contract settlement** — roadmap Section 9
- **Verified status:** NOT STARTED.
- **Primary owner:** Engineer C — first implementation batch, file-disjoint from the 1.1/1.2
  chain, so C can work in parallel while Sadin and B hold the forms chain.
- **Objective / deliverable:** Settle F5 from the Batch 0.1 result: if the API emits offsets, keep
  the schema and add a proving fixture; if naive ISO, accept both shapes and normalize, with a note
  to the backend pod. Also write the metric-inventory note for the dashboard (course count, profile
  completeness — no analytics endpoints exist). Files: `features/courses/schemas.ts`,
  `lib/api.test.ts` (fixtures).
- **Prerequisites:** Batch 0.1's F5 answer (available as soon as Sadin's baseline record exists)
  and Gate A.
- **Earliest permitted start:** After Gate A.
- **Relative effort (estimate):** Low–Medium.
- **Verification / completion:** Course list and detail load against the live API; unit suite
  covers both datetime shapes; the rest of the course schema, query options, mutations, and the
  apiFetch error taxonomy are must-NOT-change. Completion of 1.1+1.2+1.3+1.4 with a green local
  matrix (including E2E with credentials) closes **Gate B**.
- **Overlap / coordination risks:** Minimal — files are C's alone; the metric inventory feeds
  Sadin's 2.2, so the note must be written before 2.2 starts.
- **Reviewer / decision-maker:** Sadin reviews; the backend pod receives the normalization note if
  the naive-ISO branch fires.

### Phase 2 — Demo Surface Definition

**Batch 2.1 — Demo journey and environment lock** — roadmap Section 10
- **Verified status:** NOT STARTED.
- **Primary owner:** Engineer C — continuity with his 1.3 infrastructure work; the environment
  decision belongs with the engineer who wired it.
- **Objective / deliverable:** Lock the nine-route inventory as the redesign surface, fix the
  journey order, confirm the demo environment (staging preferred, pending the CORS answer; local
  dev is the documented fallback), and document plus rehearse the demo dataset procedure (demo
  profile and courses created through the real API; a scripted sequence of real calls is allowed —
  no seed framework, no mock data). Deliverable: a runbook a second person could follow.
- **Prerequisites:** Gate B; the Batch 0.1 CORS answer informs the environment decision (Open
  Question 3).
- **Earliest permitted start:** After Gate B; the runbook can be drafted against staging with the
  local fallback documented while the CORS answer is pending, but the environment lock waits for it.
- **Relative effort (estimate):** Low–Medium — no application code; coordination and rehearsal.
- **Verification / completion:** One full manual walk of the journey on the chosen environment with
  the dataset in place; completion = the journey runs without developer intervention beyond
  scripted setup.
- **Overlap / coordination risks:** None in application code. The runbook is consumed by Sadin's
  5.3 dry run. Must not add routes, features, or auth/data-layer changes.
- **Reviewer / decision-maker:** Sadin reviews; the environment decision is C's (Open Question 5)
  driven by the CORS answer.

**Batch 2.2 — Honest-surface settlement** — roadmap Section 10
- **Verified status:** NOT STARTED.
- **Primary owner:** Sadin.
- **Objective / deliverable:** Settle final dashboard and landing structure by removing
  placeholders and misleading affordances (S1, S2): the three Coming-soon cards and two
  Coming-soon sections become real supported content (course count, profile completeness, recent
  courses) or are removed; the mislabeled Open Chat / View Graph buttons are removed; the verified
  mislabels (the "Active Materials" stat card showing the course count; the Navbar labelling
  `/courses` as "My Materials") are fixed in the same pass; landing copy rewritten so every claim
  maps to a real capability, with future work framed as roadmap. Structural edits only — final
  visuals arrive in Phase 4. Files: `app/(app)/dashboard/page.tsx`, `app/page.tsx`,
  `components/Navbar.tsx` (label fix only; the shell redesign stays in 3.3).
- **Prerequisites:** Batch 1.4's metric inventory (C) and Gate B.
- **Earliest permitted start:** After Gate B, once 1.4 is applied.
- **Relative effort (estimate):** Medium — content decisions plus the first lockstep E2E update.
- **Verification / completion:** Zero Coming-soon strings and no mislabeled affordances on the
  surface; dashboard E2E assertions updated if heading copy changes. Data fetching on both pages,
  route behavior, schemas, and mutations are must-NOT-change. Together with 2.1's runbook this
  closes **Gate C**.
- **Overlap / coordination risks:** `components/Navbar.tsx` is redesigned in 3.3 (Sadin again) —
  2.2 must stay strictly label-level. `app/page.tsx` is visually rebuilt in 4.1 (B) — sequential,
  no concurrency.
- **Reviewer / decision-maker:** Sadin implements; B and C review (both own the next phases that
  build on the locked structure).

### Phase 3 — UI/UX Direction and Foundations

**Batch 3.1 — Design direction and tokens** — roadmap Section 11
- **Verified status:** NOT STARTED. (The ledger's verification re-scoped this batch: the token
  layer largely already exists in `app/globals.css` — see the correction table in the ledger.)
- **Primary owner:** Engineer B — B prepared for this during Phase 2 while Sadin and C held the
  two parallel Phase 2 batches.
- **Objective / deliverable:** Ratify or adjust the existing `@theme` token layer against the
  chosen design direction; add the genuinely missing groups — interaction states (hover,
  focus-visible, disabled, loading), motion principles (short, purposeful, reduced-motion aware),
  border weights; codify the RTL/logical-properties discipline; write the ADR-style
  design-decision note tied to the educational positioning. Files: `app/globals.css` (`@theme`
  block), the decision note, `docs/design-tokens.md` where touched.
- **Prerequisites:** Gate C (structure locked, so tokens are designed against real requirements).
- **Earliest permitted start:** After Gate C.
- **Relative effort (estimate):** Medium — design judgment plus ratification rather than
  creation-from-scratch.
- **Verification / completion:** Both themes render every primitive legibly via the Storybook
  background toolbar; the note answers why each token group exists. Completion: the token layer is
  ratified and stable — downstream batches reference tokens, never raw hex values.
- **Overlap / coordination risks:** `app/globals.css` is touched again by 3.2 — 3.1 must be applied
  first (already a roadmap dependency). Token names consumed by components must not change unless
  call sites move in the same batch.
- **Reviewer / decision-maker:** Sadin reviews (the design direction is a lead-visible decision);
  C advises as the owner of the consuming 3.2.

**Batch 3.2 — Design system foundations in code** — roadmap Section 11
- **Verified status:** NOT STARTED.
- **Primary owner:** Engineer C.
- **Objective / deliverable:** Refine only the primitives the real pages need and clear foundation
  hygiene: restyle primitives to tokens with consistent state styles; extract the hand-rolled
  delete confirmation from `DeleteCourseButton` into a new reusable alert-dialog primitive
  (`components/ui/dialog.tsx`) with identical semantics; restyle the async-state kit; drop the
  shadcn runtime dependency by vendoring its stylesheet (W5); remove the dead hooks alias (S7),
  the unused list-filters factory (S4), and use or delete the badge (S5); settle the S9
  keep-or-remove decision on the unreachable `(app)` loading boundary (Open Question 8 — C decides,
  trivial). Files: `components/ui/*`, `components/state/*`, new `components/ui/dialog.tsx`,
  `globals.css`, `package.json`, `components.json`, `features/courses/keys.ts`.
- **Prerequisites:** Batch 3.1's tokens.
- **Earliest permitted start:** After 3.1 is applied.
- **Relative effort (estimate):** Medium–High — many small moves with semantic-preservation
  constraints (the alertdialog extraction must keep the accessible semantics the E2E asserts).
- **Verification / completion:** All stories render and pass axe in both themes and directions;
  build green; the shadcn CLI gone from the dependency tree; no dead primitives left. Primitive
  APIs beyond styling and the axe-fail-on-violation config are must-NOT-change.
- **Overlap / coordination risks:** `globals.css` (with 3.1), `package.json` (with 1.3's engines
  line — sequential, no concurrency), and the dialog primitive that Sadin's 4.3 consumes — the
  extraction must land before 4.3 starts.
- **Reviewer / decision-maker:** Sadin reviews; B advises (4.1 consumes the restyled primitives).

**Batch 3.3 — Application shell** — roadmap Section 11
- **Verified status:** NOT STARTED.
- **Primary owner:** Sadin.
- **Objective / deliverable:** Redesign the shared protected-page structure: desktop and mobile
  navigation, user menu with logout, theme-toggle placement, page container and header pattern,
  footer, responsive breakpoints; relocate the misfiled `useUserName` hook from
  `components/UserName.tsx` into the auth feature slice as pure data access (W4), consumed through
  a presentational component. Files: `components/Navbar.tsx`, `components/UserName.tsx`,
  `components/auth/UserInfo.tsx`, `app/(app)/layout.tsx`, `app/layout.tsx`, `features/auth/`.
- **Prerequisites:** Batches 3.1 and 3.2.
- **Earliest permitted start:** After 3.2 is applied.
- **Relative effort (estimate):** Medium–High — the one surface every protected page shares, with
  strict protected logic (`useMe` query and cache key, AuthGuard position and behavior, nav link
  targets, logout sequence).
- **Verification / completion:** Shell renders on every protected route; mobile menu works at the
  smallest viewport; axe clean; the hook relocation is behavior-identical (same data, same
  fallbacks). Completion closes **Gate D**: design direction locked and proven — Phase 4 only
  composes.
- **Overlap / coordination risks:** `components/Navbar.tsx` (2.2 label fix landed earlier — same
  owner, sequential); `app/layout.tsx` is shared with 4.1's `(auth)` layout work — sequential; the
  logout placement moves from the dashboard's Session Control card into the user menu (presentation
  only, ledger-verified allowance).
- **Reviewer / decision-maker:** Sadin implements; B and C both review (every Phase 4 batch builds
  on this shell).

### Phase 4 — Full Frontend Redesign

**Batch 4.1 — Auth screens and landing page** — roadmap Section 12
- **Verified status:** NOT STARTED.
- **Primary owner:** Engineer B — continuity: B completed the register states in 1.2 and owns the
  token layer from 3.1.
- **Objective / deliverable:** Redesign the public surface: the `(auth)` layout, login, register,
  and the landing page with honest copy (Phase 2's locked direction), composed from the new
  primitives; the auth pattern is a centered card with brand and feedback states; the landing hero
  and features rebuild on the token system. Files: `app/(auth)/layout.tsx`, `login/page.tsx`,
  `register/page.tsx`, `app/page.tsx`, `components/auth/LoginForm.tsx` (presentation only).
- **Prerequisites:** Gate D.
- **Earliest permitted start:** After Gate D.
- **Relative effort (estimate):** Medium.
- **Verification / completion:** Login E2E updated and green (its `Welcome Back!` assertion follows
  the new copy); axe on the new stories; the 1.2 auth boundaries checked in the new skin.
  Must-NOT-change: `keycloak.login`/`keycloak.register` call sites and redirect targets,
  `safeRedirectTarget`, the Suspense boundary around LoginForm, the register states from 1.2.
- **Overlap / coordination risks:** `app/page.tsx` (2.2 restructured it — sequential); the register
  page B already touched in 1.2 (same owner). The E2E copy lockstep starts here and runs through
  every Phase 4 batch.
- **Reviewer / decision-maker:** Sadin reviews; C advises (owns the next chain position, 4.2).

**Batch 4.2 — Dashboard and courses list** — roadmap Section 12
- **Verified status:** NOT STARTED.
- **Primary owner:** Engineer C.
- **Objective / deliverable:** Redesign the two browse surfaces with real data and states: the
  dashboard pattern with the locked real-metric composition from 2.2, and the list pattern with
  search, card grid, and a real empty state; extract the inline filter state from
  `courses/page.tsx` into the pattern component (Bucket B). Files:
  `app/(app)/dashboard/page.tsx`, `app/(app)/courses/page.tsx`, `components/CourseCard.tsx`, new
  list-pattern component.
- **Prerequisites:** Batch 4.1.
- **Earliest permitted start:** After 4.1 is applied.
- **Relative effort (estimate):** Medium.
- **Verification / completion:** Courses E2E updated where copy changed; empty state verified with a
  fresh account; axe, both themes. Must-NOT-change: `useCourses` and its `me.isSuccess` gating (the
  split-identity mitigation), filter semantics, `courseCount` derivation, the read-only nature of
  both pages.
- **Overlap / coordination risks:** Dashboard page (2.2 content landed — sequential); the extracted
  list pattern becomes the reference for Phase 5's viewport checks.
- **Reviewer / decision-maker:** Sadin reviews (owns the next chain position, 4.3).

**Batch 4.3 — Course detail, forms, and delete confirmation** — roadmap Section 12
- **Verified status:** NOT STARTED.
- **Primary owner:** Sadin — the highest-stakes Phase 4 batch; Sadin also authored the 1.1 key
  fixes that this batch must protect.
- **Objective / deliverable:** Redesign the detail and create/edit form patterns: detail layout;
  form pattern (field rhythm, validation presentation, submit and API-error states); replace the
  hand-rolled confirm with the 3.2 dialog primitive with identical semantics; keep
  notFound-on-404, styling its presentation. Files: `courses/[id]/page.tsx`,
  `courses/new/page.tsx`, `courses/[id]/edit/page.tsx`, `components/courses/CourseForm.tsx`,
  `DeleteCourseButton.tsx`.
- **Prerequisites:** Batch 4.2; the 3.2 dialog primitive.
- **Earliest permitted start:** After 4.2 is applied.
- **Relative effort (estimate):** High — the full CRUD E2E (create, read, update, alertdialog
  delete) is the regression net for the whole form pattern.
- **Verification / completion:** Full courses-crud E2E updated and green. Must-NOT-change: Zod
  schemas and safeParse loops, mutation orchestration and cache invalidation, post-save navigation,
  status-to-message mapping, the 1.1 key fixes.
- **Overlap / coordination risks:** Forms files already touched by 1.1/1.2 (long since applied);
  the dialog primitive from 3.2 must be in place. This batch's E2E updates must not pre-empt 5.1's
  full alignment.
- **Reviewer / decision-maker:** Sadin implements; B reviews (owns 4.4, the next chain position).

**Batch 4.4 — Profile, global states, responsive/RTL pass** — roadmap Section 12
- **Verified status:** NOT STARTED.
- **Primary owner:** Engineer B.
- **Objective / deliverable:** Finish the surface: the profile pattern with create-versus-edit
  presentation settled once; global 404/error states restyled; systematic pass at both breakpoints
  and a logical-properties RTL audit using the Storybook direction toolbar. Files:
  `app/(app)/profile/page.tsx`, `components/profile/ProfileForm.tsx`, `app/not-found.tsx`,
  `app/(app)/error.tsx`, `app/(auth)/error.tsx`, `app/(app)/loading.tsx`.
- **Prerequisites:** Batch 4.3.
- **Earliest permitted start:** After 4.3 is applied.
- **Relative effort (estimate):** Medium–High — cross-route sweep discipline, not new logic.
- **Verification / completion:** Profile-roundtrip E2E updated and green; every route inspected at
  both viewports and directions; axe across the full story set. Must-NOT-change: the profile schema
  and mutation, the 404-to-null semantics, the F4 key fix, the `role="status"` success contract the
  E2E asserts. Completion closes **Gate E**.
- **Overlap / coordination risks:** `(auth)/error.tsx` was created by B in 1.2 — same owner
  restyles it (continuity, no conflict); ProfileForm carries the 1.1/1.2 lineage.
- **Reviewer / decision-maker:** Sadin reviews; C advises (owns 5.2, whose sweep builds on this).

### Phase 5 — Integration and Hardening

**Batch 5.1 — Test suite alignment** — roadmap Section 13
- **Verified status:** NOT STARTED.
- **Primary owner:** Engineer B — continuity: B authored the Phase 4 lockstep updates and the
  final surface copy.
- **Objective / deliverable:** Align the three E2E specs and the local matrix with the final UI;
  add the one missing check class — viewports: assertions updated to final copy and structure
  (prefer role-based and accessible-name selectors); a compact responsive check (a second Playwright
  project at the mobile viewport running login and list flows, or in-spec viewport assertions).
  Files: `e2e/login.spec.ts`, `e2e/courses-crud.spec.ts`, `e2e/profile-roundtrip.spec.ts`,
  `playwright.config.ts`.
- **Prerequisites:** Gate E.
- **Earliest permitted start:** After Gate E.
- **Relative effort (estimate):** Medium.
- **Verification / completion:** Full local matrix with credentials: lint, typecheck, unit,
  storybook, build, all three specs at both viewports; no spec asserts copy that no longer exists.
  Must-NOT-change: the one-test-per-flow structure, real-Keycloak login, skip-without-credentials
  behavior, worker and retry settings.
- **Overlap / coordination risks:** The specs were touched in lockstep throughout Phase 4 — this
  batch is their authoritative alignment; the duplicated login helper stays as documented.
- **Reviewer / decision-maker:** Sadin reviews; C advises (owns 5.2, which consumes this).

**Batch 5.2 — Verification runs** — roadmap Section 13
- **Verified status:** NOT STARTED.
- **Primary owner:** Engineer C — continuity with the environment/verification thread.
- **Objective / deliverable:** Execute the deferred closure-doc verification items against the
  final product: three consecutive green E2E workflow runs (`e2e.yml` via `workflow_dispatch` with
  staging variables) — the repository's own promotion gate; a green `test:storybook` a11y run; a
  recorded sweep of every story and route in light, dark, LTR, RTL with a contrast spot-check for
  S10-class token mistakes. No code changes; execution and records only.
- **Prerequisites:** Batch 5.1; staging deployed with the final build.
- **Earliest permitted start:** After 5.1 is applied and the final staging build is deployed.
- **Relative effort (estimate):** Medium — orchestration and honest record-keeping.
- **Verification / completion:** The records themselves: three green runs, a11y green, sweep notes
  with zero unresolved defects. Must-NOT-change: workflow triggers and gating design (e2e stays
  `workflow_dispatch`; making it a required PR check is a team decision outside this roadmap).
- **Overlap / coordination risks:** None in code; the promotion evidence is Gate F input alongside
  Sadin's 5.3 dry run.
- **Reviewer / decision-maker:** Sadin reviews the records; the promotion claim lands in the
  ledger as Gate F evidence.

**Batch 5.3 — Staging validation and demo dry run** — roadmap Section 13
- **Verified status:** NOT STARTED.
- **Primary owner:** Sadin — the lead closes the roadmap with the rehearsal the supervisor will
  actually see.
- **Objective / deliverable:** Prove the product on the environment the supervisor will see: final
  staging deploy; Sentry event and source-map verification repeated on the final build; demo
  dataset refreshed per the 2.1 runbook; one full dry run of the locked journey exactly as
  presented; the W6/W7 pinning hygiene (pin the six floating devDependencies in `package.json`;
  pin the Chromatic action digest in `.github/workflows/storybook.yml`).
- **Prerequisites:** Batch 5.2; the runbook from 2.1.
- **Earliest permitted start:** After 5.2's records exist.
- **Relative effort (estimate):** Medium.
- **Verification / completion:** The dry run itself: one continuous execution with zero developer
  interventions, on staging, with Sentry confirming from the correctly labeled environment.
  Must-NOT-change: deploy script sequence, compose topology, any runtime dependency version (only
  devDependencies and the one CI action digest are pinned). Completion closes **Gate F** —
  presentation ready.
- **Overlap / coordination risks:** `package.json` again (last toucher in the chain); the dry run
  depends on the whole team's output — any failure routes back to the owning batch's engineer.
- **Reviewer / decision-maker:** Sadin implements; the whole team observes the dry run; Gate F
  readiness is Sadin-coordinated by definition.

---

## 5. Recommended Execution Order

The order below is dependency-aware, not three separate wish-lists. "Applied" means the batch's
patch has been reviewed and applied to the shared branch by the lead; "implementation" means an
engineer is actively executing the batch's lifecycle. **Parallel preparation is allowed anytime;
parallel implementation only where this section explicitly marks file-disjoint tracks.** No batch
starts before its register entry's "earliest permitted start" condition holds, and no gate is
bypassed because a different engineer owns the next batch.

**Wave 0 — start now.**
- **Sadin implements Batch 0.1** (the demonstration batch — see Section 11 for why it was chosen).
- **B and C: preparation only.** Verify their repository/branch state, read the roadmap's Sections
  2–7 and the ledger's verification record, confirm the local dev stack, E2E credentials, and (C)
  staging reachability and Sentry access. No implementation — nothing else may start before Gate A,
  and 0.2 needs 0.1's output.

**Wave 1 — Gate A.**
- **B implements Batch 0.2** once Sadin's baseline record exists.
- Sadin reviews, records the team-lead sign-offs (Open Questions 1 and 4) so the Gate A packet is
  complete, and pre-arranges the staging deploy window and Sentry access C will need in Wave 2.
- **Gate A passes** when 0.1's evidence and 0.2's frozen classification both exist.

**Wave 2 — Phase 1, three file-disjoint tracks (after Gate A).**
- **Sadin implements 1.1** (forms chain).
- **C implements 1.4** (schema/fixtures — disjoint from 1.1's files; uses 0.1's F5 answer).
- **B waits on implementation** (1.2 depends on 1.1's applied changes to the shared form files) and
  instead serves as advisory reviewer of the 1.1 patch and finishes 1.2 preparation.
- C's **1.3** starts when its external enablers land (staging deploy window + Sentry access); if
  they slip, C completes 1.4 first and keeps 1.3 coordinated with infra rather than idle-blocking.
- The 1.1 patch is applied **before** B starts 1.2.

**Wave 3 — Phase 1 completion (Gate B).**
- **B implements 1.2** after 1.1 is applied.
- **C implements 1.3** when the window arrives (or continues coordinating it).
- Sadin reviews both; the local matrix must be green including E2E with credentials.
- **Gate B passes** when 1.1 + 1.2 + 1.3 + 1.4 are all complete and the closure set is verified.

**Wave 4 — Phase 2, two file-disjoint tracks (after Gate B).**
- **Sadin implements 2.2** (dashboard/landing honesty — needs 1.4's metric inventory, already
  applied by then).
- **C implements 2.1** (runbook, environment lock, dataset rehearsal; the environment *decision*
  waits on the CORS answer OQ3, with local fallback documented).
- **B: preparation for 3.1** — study the existing token layer and draft direction options. No code.
- **Gate C passes** when both the runbook (2.1) and the honest surface (2.2) exist.

**Wave 5 — Phase 3, strict chain (after Gate C): 3.1 → 3.2 → 3.3.**
- **B implements 3.1** → **C implements 3.2** → **Sadin implements 3.3.**
- Each patch is applied before the next batch starts (shared `globals.css`; primitives consumed
  downstream). The owner of the next chain position is the advisory reviewer of the in-flight patch.
- **Gate D passes** when tokens + primitives + shell exist in code, axe-clean in both themes and
  directions.

**Wave 6 — Phase 4, strict chain (after Gate D): 4.1 → 4.2 → 4.3 → 4.4.**
- **B implements 4.1** → **C implements 4.2** → **Sadin implements 4.3** → **B implements 4.4.**
- Lockstep disciplines run inside every batch: stories update with their components; E2E assertions
  update the moment copy changes. A waiting engineer's job is advisory review of the in-flight
  patch plus preparation of their own next batch — never early implementation of it.
- **Gate E passes** when all nine routes plus both groups' states run on the new system with CI
  green.

**Wave 7 — Phase 5, strict chain (after Gate E): 5.1 → 5.2 → 5.3.**
- **B implements 5.1** (test alignment + viewports) → **C implements 5.2** (promotion runs, a11y,
  sweep — needs the final staging build) → **Sadin implements 5.3** (final staging validation,
  pinning, dry run).
- **Gate F passes** on the roadmap's evidence: promotion 3/3, a11y green, sweep recorded, staging
  dry run without intervention.

**Patch review and application order** is exactly the wave order above — the same sequence as the
roadmap's dependency graph. When two tracks are in flight (Waves 2 and 4), their patches may be
reviewed in either order between the tracks, but each track's internal order is fixed, and the
lead applies them one at a time, re-reading the ledger between applications.

---

## 6. Gate Ownership and Readiness

No gate is passed today. The ledger's Current State says "none passed yet (Gate A is the first)",
and nothing in the available sources constitutes gate evidence. Every gate below is therefore
**pending / unverified** — a gate is passed only when its named evidence exists in the repository
or records, checkable by someone other than the implementer.

| Gate | Roadmap requirement (evidence required) | Readiness coordinated by | Evidence supplied by | Blocked by / conditions | Status |
|---|---|---|---|---|---|
| **A — Functional Reality** | Baseline record (0.1: six script results, 3 E2E results, F5 answer, CORS answer) + frozen classification (0.2) | Sadin | Sadin (0.1), B (0.2) | Nothing external; 0.1's environment needs (stack, credentials, staging) are preparation items | **Pending** — 0.1 is "next up", 0.2 not started |
| **B — Week 8 Closure** | Closure set closed (F3, F4, F5, W1, S3, S8, S10, F1, F6, W8, S1/S2 decisions) + local matrix green incl. E2E with credentials | Sadin | Sadin (1.1), B (1.2), C (1.3, 1.4) | 1.3's staging window + Sentry access; OQ4 sign-off should be recorded so the closure claim is worded correctly | **Pending** |
| **C — Demo Surface Locked** | Runbook (2.1) + zero Coming-soon or misleading affordances (2.2) + environment and dataset confirmed | Sadin | C (2.1), Sadin (2.2) | OQ3 CORS answer decides the demo environment (fallback: local); OQ6 decides only the optional materials stretch | **Pending** |
| **D — Design Direction Locked** | Token layer + decision note (3.1); primitives and shell restyled, axe-clean in both themes and directions (3.2, 3.3) | Sadin | B (3.1), C (3.2), Sadin (3.3) | Gate C; strict 3.1→3.2→3.3 order | **Pending** |
| **E — Redesign Complete** | All nine routes plus both groups' states on the new system; stories and E2E updated in lockstep; CI green | Sadin | B (4.1, 4.4), C (4.2), Sadin (4.3) | Gate D; strict 4.1→4.2→4.3→4.4 order | **Pending** |
| **F — Presentation Ready** | Promotion 3/3 green; a11y green; theme and direction sweep recorded; staging dry run without intervention | Sadin | B (5.1), C (5.2), Sadin (5.3) | Gate E; final staging build deployed; the 2.1 runbook | **Pending** |

Rules the team must not blur: a gate's evidence is supplied by the batch owners named above, but
**no engineer — including the lead — may declare a gate passed**; the evidence is checked against
the ledger, and the lead records the pass. Assigning a batch to an engineer is never permission to
skip the gate that precedes it. If new evidence invalidates a locked decision, the change is
written down as a new open question and the affected gate is re-evaluated explicitly — per the
roadmap, never silently.

---

## 7. Patch Coordination and Conflict Prevention

This section adds only coordination on top of the lifecycle rules — it does not restate them and
does not invent new tooling, permissions, or shared infrastructure.

1. **One accountable owner per batch.** The owner executes, verifies, updates the ledger, and
   produces the patch. Advice from the other engineers is welcome; ownership never becomes shared.
2. **Single application point, serialized.** Per lifecycle rule 8, batch owners do not commit or
   push; the lead (or the confirmed publisher role — see the role-name note in Section 2) reviews,
   applies, commits, and pushes. Patches are applied **one at a time, in the Section 5 order**,
   with the ledger re-read between applications. No two engineers' patches are ever in application
   at once.
3. **Patch order equals dependency order.** The chains (0.1→0.2; 1.1→1.2; 3.1→3.2→3.3;
   4.1→4.2→4.3→4.4; 5.1→5.2→5.3) and the file-disjoint parallel tracks (1.1 ∥ 1.4 ∥ 1.3; 2.1 ∥ 2.2)
   are applied so that no patch ever lands on top of changes it assumed absent.
4. **Overlapping-file register (highest-frequency risks):**
   - `progress.md` — touched by **every** batch (lifecycle rule 6). Mitigation: each owner edits
     only their own batch's entry and the Current State block; because patches apply serially,
     trivial context offsets are resolved at application time by the lead.
   - `app/globals.css` — 3.1 (B) then 3.2 (C): strict order, no parallel edits.
   - `CourseForm.tsx` / `ProfileForm.tsx` — 1.1 (Sadin) → 1.2 (B) → 4.3 (Sadin) / 4.4 (B): chain
     order only.
   - `components/Navbar.tsx` — 2.2 (label-level, Sadin) then 3.3 (full redesign, Sadin): same
     owner, sequential.
   - `app/page.tsx` — 2.2 (structure, Sadin) then 4.1 (visual rebuild, B): sequential.
   - `package.json` — 1.3 (engines, C), 3.2 (drop shadcn, C), 5.3 (pinning, Sadin): different
     phases, sequential.
   - `app/(auth)/error.tsx` — created in 1.2 (B), restyled in 4.4 (B): same owner by design.
   - E2E specs — lockstep updates in 1.1/1.2/4.1/4.2/4.3/4.4, authoritative alignment in 5.1: the
     lockstep rule (update the moment copy changes) keeps specs truthful between owners.
5. **Pre-existing changes.** If a working tree contains changes the engineer did not make, they are
   recorded, preserved, and excluded from the batch's patch (lifecycle rule 2). Never unstaged,
   discarded, or overwritten; if pre-existing changes collide with batch files, stop and report to
   the lead instead of resolving silently.
6. **Conflicts at application time.** If a patch fails to apply cleanly, the lead stops, reports,
   and returns the patch to its owner for regeneration against the current HEAD — the ledger is
   never "fixed up" silently to make a patch fit.
7. **Ledger truthfulness.** A batch's ledger entry is written by its owner with the actual result
   before the patch is generated (lifecycle rule 6), and it travels inside that patch. No entry is
   written for work not yet verified; no gate is recorded as passed without its evidence. This
   allocation document itself is never entered in the ledger.
8. **No concurrent edits.** The parallel tracks exist precisely because their files are disjoint.
   If reality diverges — an engineer discovers they need a file another in-flight track owns — the
   track stops and the lead re-sequences; nobody "just touches" another track's file.

---

## 8. Blocked, Conditional, and Deferred Work

Nothing in Phase 0 or the main Phase 1 line is blocked today. The items below are the ones whose
execution depends on something other than an engineer's willingness to start.

| Work | Depends on | Owner of the dependency | What happens while waiting |
|---|---|---|---|
| **Batch 1.3** (C) — staging verification portion | A staging deploy window; Sentry access; Pod D build-time secrets (`SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT`) | Lead arranges with infra / Pod D; the roadmap allows folding the secrets in here **or** raising an infra task | Code-side wiring (Dockerfile ARG, workflow, compose, env example, engines) can be prepared; the VERIFY step (Sentry UI shows labeled events with resolved maps) waits for the deploy |
| **Batch 2.1** (C) — environment lock | Open Question 3: staging CORS (compose passthrough edit + backend restart, infra-owned) | Infra owner | Runbook drafting, journey order, and dataset procedure proceed; the environment decision (OQ5) waits; local dev is the documented fallback and is fully sufficient for the locked journey |
| **Materials upload + status stretch flow** | Open Question 6: AI pod lands a working processing seam **and** an instructor test user in staging **before Gate C** | AI pod | Nothing — this stays deferred. No frontend work, no fake AI; if the trigger fires, the Gate C decision adds a minimal upload + status view; if not, it stays out |
| **Batch 5.2** (C) | Staging deployed with the final build | Lead/infra | 5.1's local matrix proceeds first; the promotion runs and sweep are staged for the final build |
| **Batch 5.3** (Sadin) | 5.2's records; the 2.1 runbook | — | Sequential by design; the dry run is the last engineering act before presentation logistics |
| **Week 8 mapping confirmation (OQ1)** | Team-lead sign-off on the recorded delta | Sadin (team lead) | Does not block any batch start; must be recorded so the Gate B closure claim lands where the 44-week plan expects it |
| **E2E promotion re-sequencing (OQ4)** | Team-lead sign-off | Sadin (team lead) | Does not block batch work; records that promotion runs belong to Gate F, not Gate B |

**Preserved roadmap exclusions (Section 16 of the roadmap — do not relitigate without new
evidence):** server-side route protection; new auth/state/form systems; materials upload UI outside
the Gate C trigger; AI chat/quiz/flashcards/knowledge-graph UI (zero AI-reachable endpoints; no
fake AI); pagination/ETags/optimistic concurrency; the backend course owner-scoping fix (flagged
upstream, not absorbed); i18n framework and full Arabic conversion (logical-properties RTL
readiness stays); coverage thresholds; analytics; new component-library dependencies (the only
dependency change is removing one, W5); coding against v4 spec §22.4; redoing any completed
modernization work.

---

## 9. Decisions and Open Questions

The roadmap's eight open questions, carried forward unchanged (answers are **not** invented
here), plus the three allocation-specific items this planning exercise surfaced.

**Roadmap open questions:**

| # | Question | Why it matters for allocation | Owner (per roadmap) | Blocked until resolved |
|---|---|---|---|---|
| 1 | Week 8 mapping — ANSWERED with evidence in the ledger; the 44-week plan's Week 8 expects an upload-to-status E2E flow the dead materials seam cannot deliver; the roadmap's closure set is the achievable frontend meaning | The Gate B closure claim's wording; nothing about batch ownership changes | Team lead (Sadin) records confirmation | Nothing; should be recorded in Wave 1 |
| 2 | Does the live API emit offset-bearing datetimes (F5)? | Decides 1.4's direction (keep schema vs. accept both shapes) | Executing dev — Sadin runs the 0.1 check; C settles it in 1.4 | 1.4's final shape (1.4 starts after 0.1 anyway) |
| 3 | Staging CORS — compose passes no `CORS_ORIGINS` to the backend; fix is an infra-owned compose passthrough edit + restart. Will infra apply it before the demo window? | Decides the demo environment (OQ5) and whether 5.2/5.3 run against staging or the local fallback | Infra owner | 2.1's environment lock; staging as demo environment |
| 4 | Is re-sequencing E2E promotion to Gate F acceptable? | Gate B vs. Gate F claim wording | Team lead sign-off | Nothing; record in Wave 1 |
| 5 | Staging or local as the demo environment? | 2.1's completion and the 5.3 dry-run venue | Executing dev (C) decides in 2.1, driven by OQ3 | 2.1 completion |
| 6 | Will the AI pod land the processing seam and an instructor test user before Gate C? | Whether the materials stretch flow is added at Gate C | AI pod | Only the optional stretch flow |
| 7 | Backend response to the course owner-scoping defect? | What demo data other accounts see; explicitly no frontend workaround | Backend pod | Nothing in the frontend plan |
| 8 | Keep or remove the unreachable `(app)` loading boundary (S9)? | Trivial scope item inside 3.2 | Executing dev (C) folds it into 3.2 | Nothing |

**Allocation-specific items (documented discrepancies / confirmations):**

**A1 — Ledger's Current State references `staging` @ `c51f3f1`; the team works on
`frontend-redesign`.** The ledger was written when the docs were verified against the staging
branch at the roadmap's baseline HEAD. The `frontend-redesign` branch adds only documentation
commits (`c876e6b`: roadmap, ledger, lifecycle rules; `8ce12e7`: LOCAL_SETUP tests guide) on top of
that same baseline — `c51f3f1` is an ancestor of the current HEAD, so there is **no application-code
drift**. Why it matters: baseline citations and the "expected latest HEAD" check in lifecycle rule
1. Resolution path: the lead updates the ledger's Current State (branch/HEAD lines) as part of the
next batch's own ledger update — not as a standalone edit now. Nothing is blocked.

**A2 — Batch 1.1's dependency row says "None; start immediately" while the phase structure places
Phase 1 after Gate A.** This plan resolves conservatively: gate ordering governs, and 1.1 starts
after Gate A; the roadmap's "start immediately" is read as "no batch-level prerequisites", not as
gate exemption. Why it matters: starting 1.1 before the scope freeze would contradict the roadmap's
own gate discipline. If the lead wants to compress the schedule by overlapping 1.1 with 0.2, that
is a **recorded team-lead decision** (explicitly noted in the ledger), not a silent bypass. Nothing
else is affected.

**A3 — Name mapping between the official sources and this plan.** The official sources assign
team-lead duties (OQ1/OQ4 decision, patch application per lifecycle rule 8) to "Seyam"; the commit
that published the execution docs (`c876e6b`) and the latest commit (`8ce12e7`) are authored by
MuhammadSeyam, and the team brief states the reference commit was reported by Sadin. This plan
treats Sadin as holding the team-lead role. If the roles are actually split across two people, the
lead duties in Sections 5–7 attach to whoever holds the publisher role. Owner: the team confirms
once. Nothing is blocked until the first patch application.

---

## 10. Operating Checklist

A coordination checklist only — the lifecycle rules and the per-batch implementation prompt remain
the authoritative execution procedure.

**Before starting a batch:**
1. Verify repository state: correct repo, branch `frontend-redesign`, HEAD matches the expected
   latest commit; unexpected local/remote state → stop and report (lifecycle rule 1).
2. Record the starting Git state; never disturb pre-existing changes (lifecycle rule 2).
3. Read the live ledger first — confirm this document's status snapshot still matches reality; if
   the ledger disagrees, the ledger wins and the lead updates this plan.
4. Read the batch's roadmap section and this document's register row for the batch.
5. Confirm the prerequisites and the gate before it are satisfied (register: "Earliest permitted
   start"); if not, stop — no self-authorization, no owner-swapping bypass.
6. Confirm you are the registered owner of this batch; if not, advise the owner instead of
   implementing.
7. Implement only the assigned batch; park discoveries outside its scope as documented notes
   (lifecycle rule 4).

**Before generating and applying a patch:**
1. Run the batch's verification exactly as its roadmap row requires; report what ran, what passed,
   what failed, what could not be run — never claim an unexecuted check passed (lifecycle rule 5).
2. Update `progress.md` with the actual result — your batch's entry and the Current State block
   only (lifecycle rule 6).
3. Generate one complete patch covering the whole repository, including untracked files, excluding
   pre-existing changes (lifecycle rule 7).
4. Verify the patch is accessible (exists, non-trivial size, readable head); report its exact path
   (lifecycle rule 9).
5. Hand off: the lead applies patches one at a time in the Section 5 order; a failed application
   goes back to the owner for regeneration against current HEAD (Section 7, item 6).
6. Report and stop; do not begin the next batch until explicitly instructed (lifecycle rule 10).

---

## 11. Final Allocation Rationale

**Why this allocation is appropriate.** It is derived almost mechanically from the roadmap's own
dependency structure rather than from preference. Thirteen of the eighteen batches sit in strict
serial chains, so the only real parallelism the roadmap offers is Phase 1's three file-disjoint
tracks (1.1 ∥ 1.4 ∥ 1.3) and Phase 2's two (2.1 ∥ 2.2) — and the assignment puts a different
engineer on each of those tracks. Ownership follows thread continuity: B takes the
authentication/public-surface thread (1.2 → 3.1 → 4.1, plus the Gate E closer 4.4 and the E2E
alignment 5.1, all of which consume work B just did); C takes the data/environment/verification
thread (1.4 → 1.3 → 2.1 → 3.2 → 4.2 → 5.2, where each batch reuses the environment knowledge of
the last); Sadin takes the correctness-critical spine (1.1, whose key fixes everything downstream
must protect), the two highest-stakes redesign moments (3.3 shell, 4.3 forms/CRUD regression net),
and the final Gate F rehearsal (5.3).

**How it balances workload and accountability.** Every batch has exactly one accountable owner;
review authority stays with the lead per the lifecycle, with the next-chain owner as advisory
reviewer so knowledge transfers along the dependency path. The weighted effort profiles
(Section 3) are comparable while having deliberately different risk shapes: Sadin carries the
widest-verification and highest-consequence batches plus uncounted lead duties; B carries the
single riskiest Phase 1 batch (protected-logic adjacency) and two chain-closers; C carries the
externally-coordinated infrastructure thread and the promotion evidence. The six-per-engineer
count is an emergent property of the chain structure, not a symmetry target — the register shows
the underlying weights differ.

**Why Sadin's initial batch is Batch 0.1 and why it was evaluated, not assumed.** The ledger
names 0.1 as "next up", all eighteen batches are verified NOT STARTED, no gate has been passed,
and 0.1 has no batch prerequisites — so it is the earliest suitable, uncompleted batch that
preserves the roadmap's sequencing. It was checked against the disqualifying conditions before
selection: it is not completed, not blocked (its needs — local stack, E2E credentials, staging
reachability — are preparation items the other two engineers confirm during Wave 0), and it is not
misaligned with its phase. It is verification-only rather than a conventional code change, and
that is precisely what makes it a strong demonstration: it exercises the entire lifecycle —
repository verification, reading the authoritative sources, recording the starting state, running
the roadmap's checks (or honestly recording what could not run, which the roadmap explicitly
permits as "failures documented as Phase 1 inputs"), writing the baseline record every later gate
cites, updating the ledger, and producing a complete patch even though application code is
untouched. The subtle interplay between a read-only batch and the patch obligation is exactly the
kind of thing the team should see demonstrated once by the lead. The alternatives fail selection:
0.2 depends on 0.1's results, and 1.1 — while unblocked at batch level — sits after Gate A in the
roadmap's phase discipline; assigning it first would teach the team to skip gates on day one.

**How the sequence minimizes rework and patch conflicts.** Every shared file has a single serial
path (Section 7's register): forms go 1.1 → 1.2 → 4.3/4.4; tokens go 3.1 → 3.2; the Navbar goes
2.2 label-fix → 3.3 redesign; `package.json` is touched once per phase at most. The parallel
tracks were chosen because their files are disjoint, and the lockstep rule (stories and E2E
updated the moment copy changes) prevents the classic redesign failure of specs drifting from the
surface they protect. No batch starts on hope: each starts only when its prerequisite patch has
been applied to the shared branch.

**Assumptions that must be revisited if the ledger changes.** Everything in this document assumes
the ledger state at planning time: all batches NOT STARTED, no gate passed, HEAD `8ce12e7` on
`frontend-redesign` with only documentation commits beyond the roadmap's baseline. If any batch
has since progressed, the ledger governs: the affected register rows and wave positions must be
re-checked, and any assignment that no longer matches reality is amended here rather than forced.
Other load-bearing assumptions: that E2E credentials and staging access remain available to the
team (0.1's demonstration and every E2E-dependent validation); that the external enablers for 1.3
and 2.1 eventually land or their documented fallbacks are accepted; and that the name mapping in
A3 holds. A change to any of these is a change to this document's Section 5 waves — recorded, not
improvised.
