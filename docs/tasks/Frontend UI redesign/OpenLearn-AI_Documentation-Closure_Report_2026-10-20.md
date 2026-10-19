# OpenLearn-AI Frontend — Documentation Closure Report (Step 4, before Batch 2.2)

**Batch:** documentation-closure (Step 4 of the execution plan) · **Executed:** 2026-10-20 · **Type:** documentation-only (evidence-based investigation and reconciliation)
**Baseline:** `frontend-redesign` @ `60f71daced6ff6c8d930c087eb038fea734f66a7` (verified equal to `origin/frontend-redesign` by fetch — not assumed) · **Batch 2.2 was not started.**

---

## 1. Purpose and scope

This report closes the documentation phase of the execution plan: it reconciles the execution-context records (roadmap DOCX, progress ledger, 0.2 scope-freeze note, LOCAL_SETUP.md) against the actual repository state and recorded evidence, executes the R1–R9 roadmap reconciliation fixed by the Batch 2.1 Decision Lock, and hands Batch 2.2 to the project lead with an auditable go/no-go. It reviews; it does not implement. No application code, script, CI, dependency, or API-contract file was touched, and no Git operation beyond reading was performed anywhere.

Out of scope (untouched, by instruction): starting Batch 2.2; any landing-page/dashboard implementation; routes, authentication, API contracts, business logic, schemas, or provider defaults; new services or dependencies; Git history; the owner's untracked `.patch` artifacts.

## 2. What was examined (evidence base)

- **Git state:** fresh isolated clone at `60f71da`; branch and remote HEAD verified equal; clean tree; the two commits after the ledger's previous snapshot (`943c56c`) inspected hunk-by-hunk — `845d819` (the local-environment-reliability patch applied; footprint byte-matches the delivered patch) and `60f71da` ("fix: harden local environment reliability and tests": the four committed sensitive backups and two verifier snapshots deleted, `.gitignore` classes added, test-isolation fixtures (`conftest.py`, `pal/test_factory*.py`), new static guards (`test_local_minio_auth_checks.py`, `test_local_smoke_cleanup_loop.py`), authenticated `minio_mc` helper across the three scripts plus an authenticated compose healthcheck, last-wins env reading in `run-worker-dev.sh`).
- **Records:** the lifecycle rules; this ledger in full (Current State, Execution Log, Status Board, Open Questions, Next Authorized Batch); the 2.1 Decision Lock (`OpenLearn-AI_Batch-2.1_Product-Owner_Decision-Lock.md`) in full; the 2.1 discovery note's §5.2/§8/§10; the 0.2 scope-freeze note (§5 Q4 region and amendment rule); LOCAL_SETUP.md; the four setup/verification scripts; the roadmap DOCX extracted in full (99 paragraphs / 35 tables via python-docx) before and after editing.
- **Fresh sandbox verification (executed 2026-10-20 at `60f71da`):** `bash -n` PASS on all four scripts; backend no-DB subset **28/28 PASS** (minio-auth static guards, cleanup-loop static guards, redis config contract 7, celery app, config 2, material publishing 3); DB-backed `test_material_api.py` fails in the sandbox without a database (34 fail / 6 pass; a leaked sandbox `DATABASE_URL` also breaks collection) — environmental, matching the reliability batch's recorded sandbox artifacts, not code regressions. Sandbox package versions differ from the pinned requirements; recorded as an artifact, not evidence about pinned behavior.
- **Attributed (not re-executed) results:** the full-backend result reported after the test-isolation fixes — **522 passed / 2 skipped / 1 deprecation warning** — is **owner-reported**. This batch verified its plausibility against the collected suite size (463 test functions + 29 parametrize decorators ≈ 524 cases) but did not re-run it; describe it as reported, never as freshly rerun here.

## 3. Reconciliation findings

**A. Decision Lock and scope.** Decisions A (local-first), B (substantial redesign), C (scoped architecture), D (material journey essential) stand `APPROVED`; Decision E (roles/ownership) stands `CLOSED` — do not reopen. No contradiction exists between the Decision Lock, the discovery note, the amended 0.2 note, and the ledger. Of the Decision Lock §8 owner questions: Q1 is resolved as pre-authorized (first-login onboarding → **Batch 4.4**); Q2 (enum vocabularies for `education_level`/`learning_style_vark`) remains open with a documented working default — frontend-defined option lists need no backend change, and a shared vocabulary stays available as an explicitly scoped backend change if the owner wants cross-surface consistency; Q3 is settled as recommended — RTL-**ready** design in Phases 3–4, full bilingual UI depth staged with the 44-week plan's W37/W41 verification pass (the §22 i18n exclusion stands).

**B. Local environment.** The documented contributor path (LOCAL_SETUP.md + `setup-dev.sh` → documented plain-uvicorn API start → `run-worker-dev.sh` → `verify-local-environment.sh` → `run-material-smoke-test.sh`) matches the scripts at `60f71da`. One genuine documentation drift was found — the §4 phase table predated the authenticated MinIO health checks — and was corrected in documentation only (no script change was needed). The MinIO checks now authenticate through the container's own runtime credentials on every `mc` call (the image's default `local` alias has empty credentials, so unauthenticated probes cannot prove the configured credentials work), and the compose healthcheck is authenticated too. The test-isolation changes select mock AI providers **explicitly through the same settings contract the factory reads**, so real application defaults (e.g. `backend/.env` pointing embeddings at bge-m3/postgres) are preserved — tests were isolated from developer env choices, not the defaults weakened. Secrets hygiene: no `.env` value, token, or credential appears in any updated document.

**C. Practical end-to-end validation — what the evidence actually supports.** (1) The auth/course-CRUD/profile journey: E2E trio 3/3 PASS on the owner machine (ledger-recorded 0.1/1.1-completion runs). (2) The materials pipeline: staging-proven (AI Weeks 7–8), and locally runnable through the delivered scripts; commit `60f71da`'s fix narratives evidence real local runtime exercise (the RC-1/RC-3 docstrings describe observed behavior). However, **no recorded green owner-run verdict block — English and Arabic ingestion through `run-material-smoke-test.sh` with persistence checks and per-kind cleanup — exists in the repository records**; the reliability batch's fresh-clone acceptance remains honestly BLOCKED in its sandbox, and the ledger's standing request to paste the verifier + smoke verdicts is still outstanding. Accordingly, this report does **not** claim a locally tested end-to-end material journey; an individual green test or endpoint is not a green journey.

**D. Remaining requirements and risks.** R1–R9 are executed (§4). Remaining blockers/limitations are all owner-machine items, unchanged in substance: the fresh-clone acceptance run; the **MinIO credential rotation** (real values were pushed in `943c56c` via the committed `.env` backups — the files are removed from the intended state and ignored, and history purge remains an owner-only decision); 1.2's owner validation; 1.3's Sentry staging runtime verification; E2E promotion still 0/3 (Gate F item). No requirement was marked complete on the strength of a plan statement alone.

## 4. Documents changed and R1–R9 disposition

| Document | Change |
|---|---|
| `OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx` | R1–R6 executed in place (styles/structure preserved; ZIP integrity verified; full-text diff = exactly 1 inserted paragraph + 4 edited paragraphs + 12 edited cells) |
| `OpenLearn-AI_Batch-0.2_Scope-Freeze_Decision-Note.md` | R7: dated §10 amendment (the note's own lineage rule) + bracketed pointer at the superseded §5 line; original text otherwise untouched |
| `OpenLearn-AI_Frontend_Execution_Progress.md` | Current State refresh (`60f71da`); doc-closure log entry; Execution History row; status-board updates (R9 title, 4.4 assignment, 2.2 entry-criteria pointer, doc-closure row); Next Authorized Batch refresh |
| `LOCAL_SETUP.md` | §4 phase table updated for the authenticated MinIO checks (two rows) |
| `OpenLearn-AI_Documentation-Closure_Report_2026-10-20.md` | This report (new) |

| R-item | Target | Disposition |
|---|---|---|
| R1 | Roadmap §14, Batch 2.1 "What changes" | **EXECUTED** — local stack is the default development and demo environment (decision A; 0.1 local CORS preflight confirmed); staging optional |
| R2 | Roadmap §14, Batch 4.3 validation | **EXECUTED** — walkthrough environment becomes a 4.3-planning decision (extended local AI profile preferred, staging fallback) |
| R3 | Roadmap §14, Batch 5.3 | **EXECUTED** — re-titled "Demo validation and dry run" (both title cells); objective/validation re-scoped to the primary demo environment (local), staging optional |
| R4 | Roadmap §15 dependencies | **EXECUTED** — local demo credentials (testuser + instructor, local Keycloak realm) provisioned by the 2.1 bootstrap extension |
| R5 | Roadmap §24 validation matrix | **EXECUTED** — materials walk + demo dry run rows updated to the primary demo environment (local; staging optional) |
| R6 | Roadmap §19 | **EXECUTED** — journey locked/finalized in 2.1; materials walk ADOPTED (decision D) with honest readiness ratings until the environment + Batch 4.3 land |
| R7 | 0.2 note §5, Open Question #4 default | **EXECUTED** — superseded by Decision A via the note's §10 amendment |
| R8 | Ledger Open Question #2 | **VERIFIED — already reclassified** (2026-10-18); no change required |
| R9 | Ledger status-board 5.x titles | **EXECUTED** — 5.3 row re-titled to match R3 |

Additional dated reconciliation notes in the DOCX (all factual status corrections, no strategy change): §4 and §22 — course owner-scoping resolved by PR #79 (`65c8a8c` + merge `92b67bd`, ledger Open Question #7); §5.1 — F5 CLOSED (2026-10-14, offset-bearing emission verified, schema frozen by 1.4); §25 — "what should the frontend implement next" now answers Batch 2.2; §2 — a reconciliation-record paragraph pointing batch statuses to the ledger. The Batch 4.4 cell records the onboarding assignment (all six fields already supported; the step flow must PUT the **accumulated payload** because `PUT /v1/users/me` is a full-replacement upsert) and the RTL staging settlement.

## 5. Outstanding risks and owner items

1. **Security (owner action required):** rotate the local MinIO credentials pushed in `943c56c`; decide (owner-only) whether to purge Git history. The ignore rules prevent re-adding the class; rotation remains open until the owner confirms it.
2. **Fresh-clone acceptance run (owner machine):** fresh clone → `bash scripts/setup-dev.sh` twice → documented API start → `bash scripts/run-worker-dev.sh` → `bash scripts/verify-local-environment.sh` → `bash scripts/run-material-smoke-test.sh` twice; paste both verdict blocks into the ledger. Until then, the local end-to-end material journey has no recorded green run.
3. **Gate B residue:** 1.2's owner validation and 1.3's Sentry staging runtime verification.
4. **Enum vocabularies (Decision Lock §8 Q2):** open owner question; working default recorded (frontend-defined option lists).
5. Sandbox-version caveat: the fresh test evidence above ran on unpinned sandbox package versions; the pinned-behavior authority remains the owner-reported 522/2/1 and CI.

## 6. Batch 2.2 handoff (prepared, not started)

**Authoritative scope Batch 2.2 must preserve** (roadmap §14 Table 20 + Decision Lock B/D/§6): S1 dashboard settlement on the **locked real-metric composition** from the 1.4 inventory (course count — now honest at the data layer via PR #79's owner-scoped listing — and profile completeness; no analytics endpoints exist); removal of the mislabeled affordances ("Open Chat", "View Graph", "Active Materials", Navbar "My Materials" → "Courses"); S2 landing honesty (market only real capabilities; future capabilities clearly labeled upcoming); role-aware or neutral dashboard heading. Files per roadmap: `app/(app)/dashboard/page.tsx`, `app/page.tsx`, `components/Navbar.tsx` (label only). Must NOT change: data fetching, route behavior, schemas, mutations. Validation: zero Coming-soon strings; no mislabeled affordances; dashboard E2E copy assertions updated in lockstep if heading copy changes.

**Known current state (verified, cited to the ledger/Decision Lock):** nine routes; landing hero markets RAG/quizzes/flashcards/knowledge graph (S2, re-verified in code); dashboard is three-quarters placeholders (S1) with the "Active Materials" mislabel; authenticated-`/` redirect is approved direction, not implemented; persona-blind surfaces everywhere; the "My Materials" navbar label names no real destination; the materials surface is 4.3 scope and must not appear in 2.2.

**Open product/content questions (owner's, not the implementer's):** the exact replacement content for the two dashboard Coming-soon sections beyond the locked metrics (e.g., recent-courses presentation depth); the landing page's precise honest-copy wording and structure; whether the dashboard heading is role-aware or neutral in tone (both are pre-approved — the choice of voice is a design decision for 2.2's execution within the locked scope). Assumptions must be marked as assumptions; do not invent metrics, journeys, or backend capabilities.

**Evidence prerequisites before 2.2 implementation:** the 1.4 real-metric inventory (ledger); the Decision Lock §6 mislabel inventory; no new evidence is required to start 2.2 — the outstanding owner-machine items (§5 above) gate Gates B/C, not 2.2's content work, and remain tracked independently.

**Smallest sensible next unit of work:** S1-only first increment — replace the three dashboard Coming-soon cards and two Coming-soon sections with the two real metrics and honest empty/real states, remove the three mislabels, update the dashboard E2E copy assertions — leaving S2 (landing) as the second increment. Acceptance criteria: zero `Coming soon` strings in `app/(app)/dashboard/page.tsx`; no affordance rendered without a backing contract; course-count copy reflects owner-scoped reality; profile-completeness metric derives from the existing profile contract only; dashboard E2E green with the updated assertions; lint/typecheck/unit/storybook/build matrix green; no file outside the roadmap's 2.2 file list touched.

## 7. Go/no-go recommendation

**GO for Batch 2.2** — conditioned only on the project lead's explicit authorization per the lifecycle rules. The documentation phase is closed: the roadmap is reconciled with the Decision Lock and the actual repository state, R1–R9 are executed and traceable, LOCAL_SETUP.md matches tested behavior, the execution-context records are mutually consistent, and every claim in this report carries its evidence label (executed, owner-reported, or not-run). 2.2's content-honesty scope has no dependency on the outstanding runtime items; those remain recorded as owner-machine work and do not block starting 2.2. Per the lifecycle rules, the executing agent stops here and waits for Seyam's explicit authorization.
