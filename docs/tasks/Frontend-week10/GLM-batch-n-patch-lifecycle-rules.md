# GLM Batch & Patch Lifecycle Rules — Week 10 Frontend

These rules govern every GLM-executed batch on the Week 10 Frontend execution context that lives in:

```text
docs/tasks/Frontend-week10/
```

They were created by the **Week 10 governance reset** (GOV-RESET-W10, 2026-11-08) at baseline `frontend-w10` @ `38fca159325ba0084e46fd5a46e9eaf4b60e8eb6` ("docs: add Week 10 frontend roadmap"), replacing — for Week 10 and subsequent frontend work — the execution mechanics of the previous rules at `docs/tasks/Frontend UI redesign/GLM-batch-n-patch-lifecycle-rules.md`. The previous rules were written for the `frontend-redesign` branch and its baseline; they are preserved as history and are no longer the active mechanics document. Their proven safeguards are carried forward unchanged in substance: repository verification, preservation of existing Git state, reading the roadmap and ledger before each batch, one authorized batch per prompt, honest verification, complete binary-capable patch generation, validation of that patch against a pristine checkout, and stopping after reporting.

## 0. The three-document distinction (memorize this)

Every batch must keep three kinds of document strictly apart:

```text
WHAT to do      →  the approved Roadmap
                   (docs/tasks/Frontend-week10/OpenLearn-AI_Week10_Frontend_Execution_Roadmap.docx
                    and its text render …_Roadmap.md — see §2 for authority)
HOW to do it    →  this file (the lifecycle rules)
WHAT HAPPENED   →  the Progress Ledger and its recorded evidence
                   (docs/tasks/Frontend-week10/OpenLearn-AI_Frontend_Execution_Progress.md)
```

- The roadmap defines the authorized scope, patch sequence, and completion criteria. It never defines execution mechanics.
- These rules define mechanics: verification, isolation, patching, validation, reporting. They never define product scope and never authorize a batch.
- The ledger records only what actually happened, with evidence. It is never a plan, and it is never edited to make planned work look complete.

A batch prompt may restate scope, but the roadmap remains the authoritative source for WHAT. If a prompt and the roadmap disagree on scope, stop and report the conflict (§4.4) instead of silently picking one.

## 1. Document authority and precedence

1. **Product authority:** `planning/Roadmap/44-WEEK-EXECUTION-PLAN .md` (note the space before `.md`). Week 10's product-level frontend item ("Basic search results UI with chunk → document linking") lives there.
2. **Week 10 execution authority (WHAT):** the Week 10 Frontend Execution Roadmap in `docs/tasks/Frontend-week10/`, in both supplied forms:
   - `OpenLearn-AI_Week10_Frontend_Execution_Roadmap.docx` — the formatted record (binary; read with a DOCX-aware tool such as python-docx; never assume its contents).
   - `OpenLearn-AI_Week10_Frontend_Execution_Roadmap.md` — the text render.
   As verified by the governance reset (2026-11-08, token-level comparison at `38fca15`), the two files are **substantively identical**; the only DOCX-only text is its table-of-contents field-code reader note and the metadata table's `Field | Value` header row. If a future edit makes them disagree, record the exact discrepancy in the ledger and report it — do not silently choose one and do not invent missing requirements.
3. **Execution mechanics (HOW):** this file.
4. **Execution record (WHAT HAPPENED):** the active ledger (§3).
5. **API contract authority:** `docs/openapi.json` — the CI-guarded, generated backend contract. Never hand-edit it; never code against endpoints it does not contain. Its drift guard is `backend/tests/test_openapi_contract.py` (structural comparison against the running app; included in the `ci.yml` backend pytest job).
6. **Historical context (read-only):** everything under `docs/tasks/Frontend UI redesign/` — the previous lifecycle rules, the previous ledger (final state: Batch 5.1.1, 2026-10-26), and the batch notes. This is preserved evidence. Do not modify it, do not delete it, and do not treat it as the active Week 10 ledger.

Precedence rule for conflicts: repository evidence > explicit current instruction > active roadmap > this file > historical documents. Never resolve a conflict by inventing a decision; report it (§13).

## 2. The active execution-context files for Week 10

A batch needs to read exactly these, every time:

```text
docs/tasks/Frontend-week10/GLM-batch-n-patch-lifecycle-rules.md        (this file — read first, always)
docs/tasks/Frontend-week10/OpenLearn-AI_Week10_Frontend_Execution_Roadmap.{docx,md}
                                                                        (the WHAT — the patch plan W10-FE-00…W10-FE-07,
                                                                         the dependency gate, the protected-behavior
                                                                         checklist, the test/evidence matrix)
docs/tasks/Frontend-week10/OpenLearn-AI_Frontend_Execution_Progress.md (the WHAT HAPPENED — the active ledger)
```

Mandatory additional reading whenever a batch touches scope, alignment, or API contracts:

```text
planning/Roadmap/44-WEEK-EXECUTION-PLAN .md   (product authority; space in the filename)
docs/openapi.json                             (the only authoritative API contract)
```

**Identifying the active ledger (rule):** the active Week 10 frontend ledger is the one in the same directory as the active Week 10 roadmap — `docs/tasks/Frontend-week10/OpenLearn-AI_Frontend_Execution_Progress.md`. The ledger under `docs/tasks/Frontend UI redesign/` is the closed record of the redesign program (through Batch 5.1.1) plus the redesign-era context; read it for history, never update it. If a future reorganization moves the roadmap, the ledger moves with it — re-derive the active ledger from the directory that contains the roadmap the current prompt authorizes, and record that determination in the ledger itself.

## 3. Start every batch by verifying the repository

Read-only first. Record and report all of it:

```bash
git status                       # clean? pre-existing changes?
git branch --show-current        # or: detached HEAD?
git rev-parse HEAD
git fetch origin                 # then re-check tips
git rev-parse origin/frontend-w10
git ls-remote --heads origin     # every relevant tip, not just the two below
git merge-base --is-ancestor <supplied-commit> HEAD && echo contained
git log --oneline --decorate -12
```

Confirm at minimum:

- the repository is `OpenLearn-AI`;
- the branch/HEAD actually match the batch's stated baseline, and the supplied commit exists **and** is an ancestor of the working HEAD;
- whether `origin/frontend-w10` (or any relevant branch) has advanced beyond the supplied reference — an advanced remote is a **finding to record**, not something to auto-merge or rebase onto;
- the working tree state before any edit (`git status --short`, `git diff --stat`), so batch-owned changes can be distinguished from pre-existing ones (§7).

**Supplied-commit semantics:** a commit supplied in a prompt is the starting reference for verification, not an assumption. If it does not exist, is not on the stated branch, or has been superseded, stop and document the discrepancy before editing anything (§13). Re-derive the correct baseline from evidence and (only if needed) ask.

## 4. Branch and baseline policy

1. **Never assume the active branch.** The old `frontend-redesign` assumption is retired. As of the governance reset, the Week 10 reference branch is `frontend-w10` (verified tip `38fca15`, containing the Retrieval commit `909d5f7` and the Week 10 roadmap), but every batch must re-verify the tip from the remote before starting (§3).
2. **Determine the baseline from evidence + explicit instruction.** The batch prompt supplies the intended reference; the repository must confirm it. When both agree, that commit (detached or on-branch) is the batch baseline.
3. **Do not switch branches, reset, clean, rebase, pull, merge, cherry-pick, or rewrite history** to make the repository fit an assumption. Read-only inspection (clones, detached worktrees of the verified commit) is always permitted and is the preferred way to inspect other branches.
4. **Branch divergence:** if the remote tip has advanced past the batch baseline, record the new commits (author, subject, files), determine whether they touch the batch's scope, and either (a) proceed only if the batch can safely be verified/implemented without changing repository state, or (b) stop and report. Never auto-sync.
5. **Missing dependencies discovered mid-batch** (absent contract, absent roadmap, absent authorization, missing environment): report them as blockers in the ledger and stop the batch. Do not fix, work around, or improvise an alternative workflow (§12).

## 5. Read the execution context before every batch

Before editing anything: read this file, the Week 10 roadmap (both forms when their agreement matters; the DOCX always via a DOCX-aware tool), and the active ledger. Determine from the ledger: what is already done, the current gate status, the next authorized patch, known issues, and standing decisions. The roadmap classifies the patch sequence `W10-FE-00 … W10-FE-07` with prerequisites — the ledger tells you where the sequence actually stands.

## 6. API contract verification

- The contract lives in `docs/openapi.json` only. Verify the exact operation on the exact branch/commit of the batch baseline: HTTP method, path, request/response schema fields (including nullable/optional), auth scheme, error responses.
- A backend implementation commit does **not** prove the contract is published; a contract in a draft/branch does **not** prove it is merged to the branch you build on. Verify the document itself, at the baseline, every time.
- Confirm the drift guard status for that state: either CI evidence (a green `ci.yml` backend job on that commit) or a locally executed `backend/tests/test_openapi_contract.py` with the repository's pinned dependency set, recorded as a local execution. Never claim CI evidence that was not retrieved.
- If the contract changes mid-sequence: stop implementation, compare the changed schema, and re-authorize affected scope before continuing (this mirrors the roadmap's stop rule).

## 7. Protect pre-existing changes

The repository may contain changes that existed before the batch began. Before any edit: record `git status --short` and `git diff --stat`; do not unstage, discard, or overwrite them. The isolated-clone patch method (§10) is what makes the batch-owned/pre-existing distinction enforceable: the patch must contain **only** batch-owned changes across the entire repository, and nothing else.

## 8. Execute exactly one authorized batch

- Work only on the patch the prompt authorizes (e.g., `W10-FE-00`), in the sequence the roadmap defines. The roadmap's "one authorized batch at a time / one small patch at a time" rule is binding.
- Do not start the next patch, implement future roadmap items, perform unrelated refactoring or cleanup, add speculative features, install packages/dependencies, or expand scope without explicit approval.
- Respect the roadmap's Protected Behavior Checklist (Keycloak/AuthGuard, `apiFetch` + `ApiError` mapping, Zod conventions, TanStack Query defaults and keys, course CRUD and ownership behavior, materials lifecycle, profile, route/not-found behavior, visual tokens/RTL, CI workflows, backend, Keycloak realm config). Any exception must be explicitly reviewed and recorded — never slipped into a patch.
- If you discover something outside the batch, document it in the ledger and leave it for a later decision, unless it is genuinely required to complete the current batch.

## 9. Verify the implementation honestly

Run the checks the roadmap requires for that patch (the Test and Evidence Matrix: lint, typecheck, unit, Storybook/a11y, build, relevant E2E, manual keyboard/theme/direction checks — using the scripts actually present in `frontend/package.json`). Be explicit about what was run, what passed, what failed, and what could not be run. **Never claim a check passed if it was not actually executed.** Documentation-only and gate batches: "verification" means the documents/gate record are accurate, internally consistent, no out-of-scope file was touched, and (for DOCX edits) the DOCX is still valid and re-extractable — application tests are not required and must not be claimed. Staging/E2E checks that are unavailable are recorded as pending with their reason, never as passed.

## 10. Generate a complete `.patch`

At the end of every batch, produce one `.patch` file containing all changes introduced by that batch across the entire repository, and nothing else. The method (proven; binary-capable because the roadmap is a DOCX):

1. Complete the batch in a working clone at the verified baseline (no commits, no pushes); keep an explicit list of every file created, modified, or deleted.
2. `git clone --no-hardlinks . <isolated-clone-path>` (a path outside the repository) and `git -C <clone> checkout --detach <start-commit>`.
3. Reproduce only the batch-owned files inside the isolated clone; `git -C <clone> status --porcelain` must show exactly the batch-owned change list.
4. `git -C <clone> add -A` and generate the patch with `git -C <clone> diff --cached --binary --no-color > <patch-file>`.
5. Never stage/unstage the user's pre-existing changes in the real working clone merely to construct the patch.

Naming: `frontend-w10-<BATCH-ID>-<description>.patch` (the active reference branch as prefix). Historical artifacts used the `frontend-redesign-` prefix (e.g., the delivered W10-FE-00 ledger patch `frontend-redesign-W10-FE-00-dependency-gate.patch`); never overwrite an existing patch. Patch artifacts are delivered outputs, not repository files (`.gitignore` already excludes `*.patch`); do not commit them.

## 11. Validate the patch against a pristine checkout

Against a pristine checkout of the exact intended baseline — a **git** checkout (`git worktree add --detach <path> <commit>` or a fresh clone checkout), never a tar/archive extraction:

```bash
git -C <pristine> apply --check <patch-file>   # must pass
git -C <pristine> apply <patch-file>           # must succeed
diff <pristine-file> <working-clone-file>      # byte-identity for every changed path
```

- **Known pitfall (from the W10-FE-00 validation, 2026-11-08):** `git apply` run against a bare archive extraction (no `.git`) silently *skips* patches whose target paths contain spaces — it exits 0 while changing nothing. Always validate inside a real git worktree/clone, and always follow with the byte-identity check; an `apply` exit code alone proves nothing.
- Confirm the patch touches only the approved scope (`git apply --stat`, plus reading the diff). Verify accessibility: `ls -lh`, `wc -l`, `head -n 20`; report the exact path. If the patch cannot be accessed, fix that before declaring the batch complete.
- For DOCX changes included in a patch: after applying, verify ZIP integrity and re-extract the text.

## 12. Blockers, safe stops, and authorization

- If a required dependency is missing (contract, authorization, roadmap, environment), record it in the ledger with the exact evidence or action required to resolve it, generate/validate the patch for whatever batch-owned changes do exist (if any), report, and **stop**. Do not fix blockers; do not improvise.
- **Authorization evidence standard:** explicit authorization means a record that Seyam (product owner) authorized the specific batch — in a repository document, ledger entry, or other verifiable project record, with who/when. A branch, a commit, a merge, a roadmap document, general discussion, or an assumption is **not** authorization. The Week 10 roadmap's own planning-time status ("PREPARATION ONLY / IMPLEMENTATION BLOCKED until … Seyam explicitly authorizes the frontend batch") is the standing statement until superseded by a recorded authorization.
- **Dependency-gate semantics (W10-FE-00 and successors):** both conditions — (A) the Retrieval API contract merged into `docs/openapi.json` on the execution branch, and (B) Seyam's explicit authorization — are required. One alone is insufficient. A gate result (`BLOCKED`/`AUTHORIZED`) is determined from evidence, never inferred.
- No batch is authorized automatically. Each batch starts only on an explicit instruction, and implementation patches start only after the gate is `AUTHORIZED`.

## 13. Report conflicts and stop safely

If the repository state, the roadmap, the ledger, and the prompt cannot be reconciled by evidence — conflicting baselines, contradicting scope, unreadable authoritative documents, unreachable requirements — stop and report the exact conflict and the evidence for each side. Do not silently reconcile, do not pick a winner, do not invent a decision.

## 14. Do not commit or push

GLM is the executor, not the Git publisher. It must not commit, push, merge, rebase, force-push, or rewrite history. The developer/owner reviews the work, applies the patch, commits, and pushes. This policy changes only on a future explicit instruction.

## 15. Update the ledger and report, then stop

Before generating the patch, update the active ledger with the actual batch result: batch ID and outcome; exact changes; files created/modified/deleted; verification performed (commands and results); failures/limitations; deviations; decisions; current state for the next batch; blockers. Record history honestly — never rewrite past batch statuses, never mark planned work complete.

Then report (batch completed; changes; files affected; verification results incl. exact commands/outcomes; deviations; ledger updated; exact patch path, size, line count; patch accessibility; current Git state) — and **STOP**. Do not begin the next batch until an explicit instruction authorizes it.

## 16. Handoff to Seyam

Every batch ends with a handoff package for Seyam's review: the validated patch (exact path), the ledger entry (what happened, evidence, blockers), and the current repository/branch state as verified. Seyam applies, commits, and pushes. Open decisions that only the owner can make (authorization, scope exceptions, environment secrets, CI evidence) are listed explicitly in the ledger so nothing depends on an unrecorded assumption.

---

### Lifecycle

```text
VERIFY REPO (remote tips, supplied commit exists & is ancestor, clean-tree record)
    ↓
READ: LIFECYCLE RULES + WEEK 10 ROADMAP (DOCX-aware) + ACTIVE LEDGER [+ 44-WEEK PLAN / OPENAPI WHEN IN SCOPE]
    ↓
RECORD STARTING STATE (status, diff --stat; pre-existing changes noted)
    ↓
EXECUTE EXACTLY ONE AUTHORIZED BATCH (respecting the gate, scope, and protected behaviors)
    ↓
VERIFY (roadmap's test/evidence matrix for the patch; honesty about NOT RUN)
    ↓
UPDATE ACTIVE LEDGER (actuals only)
    ↓
GENERATE COMPLETE --binary --no-color PATCH (isolated-clone method; new files included)
    ↓
VALIDATE ON A PRISTINE GIT CHECKOUT (apply --check → apply → byte-identity → scope check)
    ↓
VERIFY PATCH ACCESS (path, size, line count, head)
    ↓
REPORT (+ blockers, handoff to Seyam)
    ↓
STOP
```

### Historical note

The previous execution program (Phases 0–5 of the Frontend UI redesign, through Batch 5.1.1 at `1c14d5a`, branch `frontend-redesign`) is complete and recorded in `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md`. The first Week 10 dependency-gate run (W10-FE-00, 2026-11-08, at `909d5f7`) was executed under the previous rules and delivered its ledger update as the patch `frontend-redesign-W10-FE-00-dependency-gate.patch`; that patch was **not** applied upstream, so the old ledger does not contain a W10-FE-00 entry — the Week 10 gate record lives in the Week 10 ledger created by the governance reset. Both historical records are preserved and remain read-only.
