# GLM Batch & Patch Lifecycle Rules

These rules apply to every implementation batch.

## 1. Start by verifying repository state

Your first action must be to inspect the repository:

```bash
cd OpenLearn-AI

git status
git branch --show-current
git rev-parse HEAD
git fetch origin
git rev-parse origin/frontend-redesign
```

Confirm that:

* the repository is `OpenLearn-AI`
* the branch is `frontend-redesign`
* the local HEAD is the expected latest HEAD
* the remote branch state is understood

**Do not reset, clean, rebase, pull, or otherwise modify Git history automatically.**

If the local/remote state is unexpected, stop and report it.

---

## 2. Preserve the existing Git state

The repository may contain changes that existed before your work began.

In particular, the current baseline may already contain staged changes.

Before making any edits:

* record the starting Git state
* do not unstage existing changes
* do not discard existing changes
* do not overwrite unrelated files
* do not assume the working tree is clean

Your patch must distinguish **changes introduced by this batch** from **pre-existing changes**.

---

## 3. Read the two execution-context files

Before every batch, read:

```text
frontend/docs/OpenLearn-AI_Frontend_Execution_Progress.md
frontend/docs/OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx
```

### `progress.md`

This is the **living execution ledger**.

Read it to determine:

* what has already been completed
* the current phase/batch
* previous changes
* known issues
* deviations
* decisions
* current execution state

At the end of every batch, update it with **exactly what actually happened**.

### `Integrated_Frontend_Execution_Roadmap_v1.1.docx`

This is the **primary execution roadmap**.

Use it to determine:

* what the current batch requires
* the intended scope
* dependencies
* verification requirements
* gates and sequencing

Do not silently change the roadmap.

---

## 4. Implement only the assigned batch

Work only on the batch specified in the prompt.

Do not:

* start the next batch
* implement future roadmap items
* perform unrelated refactors
* add speculative features
* expand scope without approval

If you discover something outside the batch, document it and leave it for a later decision unless it is genuinely required to complete the current batch.

---

## 5. Verify the implementation

Run the appropriate tests, checks, builds, or manual verification for the batch.

Be explicit about:

* what was run
* what passed
* what failed
* what could not be run

Never claim a check passed if it was not actually executed.

---

## 6. Update `progress.md` at the end

Before generating the patch, update:

```text
frontend/docs/OpenLearn-AI_Frontend_Execution_Progress.md
```

Record the actual batch result, including:

* batch completed
* exact changes made
* files changed/created/deleted
* verification performed
* failures or limitations
* deviations from the roadmap
* relevant decisions
* current state for the next batch

Do not rewrite history or pretend that planned work was completed if it was not.

---

## 7. Generate a complete `.patch`

At the end of every batch, create a `.patch` file containing **all changes introduced by this batch across the entire repository**.

This includes:

* source code
* configuration
* tests
* documentation
* `progress.md`
* any other files modified or created by the batch

The patch must **not** contain unrelated changes that existed before the batch.

Be especially careful with pre-existing staged changes.

A normal:

```bash
git diff
```

is not sufficient if the batch created untracked files.

The final patch must include those files as well.

---

## 8. Do not commit or push

You are the executor, not the Git publisher.

You must **not**:

* commit
* push
* merge
* rebase
* force-push
* rewrite history

Seyam will review the work, apply/upload the patch, commit it, and push it.

---

## 9. Verify that the patch is actually accessible

After creating the patch, verify that it exists and can actually be accessed.

Check at minimum:

```bash
ls -lh <patch-file>
wc -l <patch-file>
head -n 20 <patch-file>
```

Report the **exact path** of the patch.

Do not merely say "patch generated."

If the patch cannot be accessed or the environment appears to have failed to create/expose it, fix that before declaring the batch complete.

---

## 10. Final response and stop

At the end of the batch, report:

* batch completed
* changes made
* files affected
* verification results
* deviations/issues
* `progress.md` updated
* exact patch path
* confirmation that the patch is accessible
* current Git state

Then **STOP**.

Do not begin the next batch until Seyam explicitly gives the next instruction.

---

### Lifecycle

```text
VERIFY REPO
    ↓
READ ROADMAP + PROGRESS
    ↓
RECORD STARTING STATE
    ↓
IMPLEMENT ONE BATCH
    ↓
VERIFY
    ↓
UPDATE progress.md
    ↓
GENERATE COMPLETE PATCH
    ↓
VERIFY PATCH ACCESS
    ↓
REPORT
    ↓
STOP
```
