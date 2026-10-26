# GLM Batch & Patch Lifecycle Rules — AI Week 7–8 (`ai-week7-8`)

These rules apply to **every implementation batch** executed on branch `ai-week7-8` under the roadmap `docs/tasks/ai-week7-8/AI_WEEK_7_8_EXECUTION_ROADMAP.md`. They adapt the repository's earlier batch/patch lifecycle rules to this task. The safeguards from that earlier document are preserved: repository verification, preservation of existing Git state, reading the roadmap and ledger before each batch, one authorized batch per prompt, honest verification, complete patch generation, and stopping after reporting.

Single executor: **Seyam (AI/ML Lead)** implements every AI/ML batch personally. Backend, DevOps, and Frontend pods appear only as external dependencies, contract owners, or consumers — never as AI/ML task owners.

## Required lifecycle

Every future implementation batch must follow this lifecycle, in order:

```text
VERIFY REPOSITORY AND BRANCH
    ↓
RECORD INITIAL GIT STATE
    ↓
READ AI ROADMAP AND progress.md
    ↓
CONFIRM THE EXPLICITLY ASSIGNED BATCH
    ↓
IMPLEMENT ONLY THAT BATCH
    ↓
RUN APPROPRIATE VERIFICATION
    ↓
UPDATE progress.md WITH ACTUAL RESULTS
    ↓
GENERATE A COMPLETE, SELF-CONTAINED PATCH
    ↓
VERIFY PATCH CONTENT AND ACCESSIBILITY
    ↓
REPORT RESULTS AND STOP
```

---

## 1. Verify repository and branch

Your first action must be to inspect the repository:

```bash
cd OpenLearn-AI

git status
git branch --show-current
git rev-parse HEAD
git fetch origin
git rev-parse origin/ai-week7-8
git status -sb
```

Confirm that:

* the repository is `OpenLearn-AI` (remote `https://github.com/OpenLearn-AI/OpenLearn-AI.git`);
* the branch is `ai-week7-8`;
* the local branch tracks `origin/ai-week7-8`;
* the local HEAD and the remote branch state are understood (identical, or ahead/behind by exactly what you can explain);
* the working-tree state is understood before anything is modified.

If your execution environment already contains a repository, inspect it carefully before deciding whether it can safely be reused; otherwise clone the repository and check out `ai-week7-8`. If the branch does not exist, the repository is not the expected one, or the state is ambiguous or unexpected — **stop and report the problem**. Do not silently switch to another branch or use another branch as a substitute.

**Never reset, clean, rebase, force-push, pull with rewrite, rewrite history, or discard existing changes — automatically or otherwise.**

## 2. Record the initial Git state and preserve it

The repository may contain staged, unstaged, or untracked changes that existed before your batch began.

Before making any edits:

* record the starting state: HEAD SHA, branch, tracking/sync status, `git status --porcelain` output (or an explicit "clean"), and any pre-existing stash state relevant to the batch;
* do **not** stage, unstage, discard, or overwrite pre-existing changes;
* do **not** assume the working tree is clean;
* your patch must distinguish **changes introduced by this batch** from **pre-existing changes** (Section 8 tells you how, precisely).

## 3. Read the roadmap and the progress ledger before every batch

Before starting work, read both files in full:

```text
docs/tasks/ai-week7-8/AI_WEEK_7_8_EXECUTION_ROADMAP.md
docs/tasks/ai-week7-8/progress.md
```

From the roadmap, take: the batch specification (Section 8), its prerequisites and gate, the acceptance criteria, and the out-of-scope list (Section 11.3). From `progress.md`, take: completed work, current phase/batch, previous changes, known issues, deviations, decisions, and the **next authorized batch**.

Do not silently change the roadmap or the ledger's historical entries. If reality disagrees with the roadmap, record the deviation in `progress.md` and, when it changes future work, propose a roadmap amendment explicitly.

## 4. Confirm the explicitly assigned batch — one batch per prompt

* Implement exactly **one** batch — the one explicitly authorized in the current prompt and consistent with `progress.md`'s "next authorized batch".
* Do **not** start subsequent batches, implement future roadmap items, perform unrelated refactors, add speculative features, or expand scope without Seyam's approval.
* If you discover something outside the batch (a bug, a missing piece, a contract mismatch), document it in `progress.md` and leave it for a later decision, unless it is genuinely required to complete the current batch — in which case record it as a deviation with its reason.
* If the assigned batch's prerequisites are not satisfied (gate not passed, dependency missing), **stop and report** instead of improvising.

## 5. Respect ownership and cross-pod boundaries

* `backend/app/services/storage.py` is Backend-owned: coordinated changes only, with Backend approval recorded before the batch lands them (handoff H2).
* The enqueue contract (`app.workers.tasks.material_tasks.process_material`, args `(material_id, s3_key, course_id, owner_id)`) is stable; changing it requires a written decision and Backend agreement.
* Provider SDKs are imported only inside `backend/app/pal/` (TS §7.3, ADR-0009).
* The 11 lifecycle tests in `backend/tests/test_material_tasks.py` pin worker behavior — never weaken them to make a change pass.

## 6. Implement, then verify honestly

Run the tests, checks, and manual verification appropriate to the batch (the roadmap's batch specification lists the commands). Then report exactly:

* what was run;
* what passed;
* what failed (verbatim, not paraphrased);
* what could **not** be run, and why.

Never claim a check passed if it was not actually executed. Never claim a runtime behavior was verified unless it was actually exercised. A green local run is never staging health; repository-level evidence is never presented as runtime evidence.

## 7. Update `progress.md` at the end of the batch

Before generating the patch, append a new batch entry to `progress.md` (Section 13 template) recording:

1. batch identifier and objective;
2. starting commit and initial Git state;
3. changes actually made;
4. files created, modified, or deleted;
5. tests and commands actually executed;
6. passes, failures, and checks not run;
7. relevant output or other verification evidence;
8. deviations from the roadmap;
9. blockers, regressions, and unresolved questions;
10. final state (HEAD SHA, tree state, gate status) and the next authorized batch.

Do not rewrite history or pretend planned work was completed if it was not. Do not mark a batch completed in the status table until its acceptance criteria are actually met.

## 8. Generate a complete, self-contained `.patch` — with patch isolation

At the end of every batch, produce **one** `.patch` file containing **all changes introduced by the batch across the entire repository** — source code, configuration, tests, documentation, `progress.md`, new files, and deletions. The patch must not contain unrelated changes or pre-existing user changes.

A plain `git diff` is **not sufficient**: it misses untracked new files, and the working tree may contain pre-existing staged/unstaged changes that must stay out of the patch.

### Preferred method — isolated working clone with a known baseline

Work this way so the batch-owned change set is captured exactly, without ever staging or unstaging the user's existing changes in the real working clone:

1. In the working clone, complete the batch (no commits, no pushes) and keep an explicit **batch-owned change list**: every file created, modified, or deleted by this batch.
2. Create an isolated clone pinned to the batch's starting commit:

   ```bash
   START=$(git rev-parse HEAD)          # recorded before edits began
   git clone --no-hardlinks . /tmp/olai-patch-build   # any path outside the repository
   git -C /tmp/olai-patch-build checkout --detach "$START"
   ```

   The isolated clone contains the exact baseline and none of the pre-existing or batch changes.
3. Reproduce **only the batch-owned changes** inside the isolated clone: copy in the files created/modified by the batch, delete the files the batch deleted (`git rm` or plain `rm`), and copy nothing else. Check the result against the batch-owned change list:

   ```bash
   git -C /tmp/olai-patch-build status --porcelain
   ```

   Every line must correspond to a batch-owned change — nothing more, nothing less.
4. Generate the complete patch from the isolated clone:

   ```bash
   git -C /tmp/olai-patch-build add -A
   git -C /tmp/olai-patch-build diff --cached --binary --no-color \
       > ai-week7-8-batch-<ID>.patch
   ```

   `add -A` inside the throwaway clone is safe by construction: the clone's index started clean at the baseline, so it stages exactly the batch-owned additions, modifications, and deletions. `--binary` keeps the patch self-contained; the diff against the staged index includes new files and removals that a plain `git diff` would miss.
5. Discard the throwaway clone after the patch is validated.

Equivalent safe approaches are acceptable if they preserve a precise list of batch-owned changes and never touch the user's existing staged/unstaged state in the real working clone. **Future executors must not stage or unstage the user's existing changes merely to construct a patch, and must not commit or push in the working clone.**

### Patch validation (mandatory)

Validate the patch against the intended baseline before delivering it:

```bash
# 1. Clean-application check against a pristine baseline (another throwaway clone)
git clone --no-hardlinks . /tmp/olai-patch-verify
git -C /tmp/olai-patch-verify checkout --detach "$START"
git -C /tmp/olai-patch-verify apply --check /path/to/ai-week7-8-batch-<ID>.patch   # must exit 0

# 2. Apply for real and compare against the batch-owned change list
git -C /tmp/olai-patch-verify apply /path/to/ai-week7-8-batch-<ID>.patch
git -C /tmp/olai-patch-verify status --porcelain     # must match the change list exactly

# 3. Content summary
git apply --stat /path/to/ai-week7-8-batch-<ID>.patch
git apply --numstat /path/to/ai-week7-8-batch-<ID>.patch
```

The patch must apply cleanly to the starting commit of the batch. If it cannot be validated, disclose that limitation explicitly in the final report and in `progress.md` — never claim successful validation that did not happen.

## 9. Do not commit or push

You are the executor, not the Git publisher. You must **not** commit, push, merge, rebase, force-push, or rewrite history. Seyam reviews the work, applies the patch, commits, and pushes.

## 10. Verify the patch is actually accessible

After creating the patch, verify it exists and can actually be accessed:

```bash
ls -lh <patch-file>
wc -l <patch-file>
head -n 20 <patch-file>
```

Report the **exact absolute path** of the patch. Do not merely say "patch generated". The patch must be exposed as an actual downloadable/accessible artifact through the execution environment's supported file-output mechanism; verify that the artifact exists and that the reported path points to the real file. If the patch cannot be accessed or the environment failed to expose it, fix that before declaring the batch complete — and if the environment fundamentally cannot expose files, say so plainly and provide the safest concrete alternative for transferring the exact file instead of pretending otherwise.

## 11. Final report and stop

End every batch with a report containing:

* the batch completed;
* the changes made (files created/modified/deleted);
* verification results — executed, passed, failed, not run;
* deviations, issues, and unresolved questions;
* confirmation that `progress.md` was updated with actual results;
* the current Git state (HEAD, branch, tree, sync);
* the exact patch path and confirmation that it is accessible;
* patch validation results against the intended baseline.

Then **STOP**. Do not begin the next batch until Seyam explicitly gives the next instruction.
