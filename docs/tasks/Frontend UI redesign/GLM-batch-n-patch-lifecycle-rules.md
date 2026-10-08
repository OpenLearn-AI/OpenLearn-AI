# GLM Batch & Patch Lifecycle Rules

These rules apply to every batch executed on branch `frontend-redesign` under the frontend execution context that lives in:

```text
docs/tasks/Frontend UI redesign/
```

They were re-baselined by batch FR-REB-00 (2026-10-08) after the branch was synchronized with `origin/staging` (AI Week 7–8 and the documentation relocation) and amended in planning scope by batch FR-REB-01 (2026-10-08, product/UX roadmap amendments A–D — documentation-only; roadmap in-document revision v1.3). The safeguards are unchanged: repository verification, preservation of existing Git state, reading the roadmap and ledger before each batch, one authorized batch per prompt, honest verification, complete patch generation, and stopping after reporting.

The active execution-context files — the only planning documents a batch needs to read — are exactly these three:

```text
docs/tasks/Frontend UI redesign/GLM-batch-n-patch-lifecycle-rules.md
                                             (this file — read first, always)
docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md
                                             (the living execution ledger)
docs/tasks/Frontend UI redesign/OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx
                                             (the primary execution roadmap — a DOCX)
```

The old internal three-engineer allocation document has been archived to `docs/tasks/Frontend UI redesign/archive/` and is **not** an active execution-context file. Do not treat it as current scope, and do not restore or modify it.

## 1. Start by verifying repository state

Your first action must be to inspect the repository:

```bash
cd OpenLearn-AI

git status
git branch --show-current
git rev-parse HEAD
git fetch origin
git rev-parse origin/frontend-redesign
git rev-parse origin/staging
git merge-base --is-ancestor origin/staging HEAD && echo "staging contained"
```

Confirm that:

* the repository is `OpenLearn-AI`
* the branch is `frontend-redesign`
* the local HEAD is the expected latest HEAD
* the remote branch state is understood
* the branch still contains the current `origin/staging` baseline (or that any divergence is explicitly explained by the batch prompt)

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
docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md
docs/tasks/Frontend UI redesign/OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx
```

These are the canonical, current paths. Older references to `frontend/docs/…` are stale — the execution context was relocated to `docs/tasks/Frontend UI redesign/` and the old location no longer exists.

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

### `OpenLearn-AI_Integrated_Frontend_Execution_Roadmap_v1.1.docx` — the roadmap is a DOCX

This is the **primary execution roadmap**. It is a binary Word document, not Markdown.

Use it to determine:

* what the current batch requires
* the intended scope
* dependencies
* verification requirements
* gates and sequencing

When you need to read it, extract its text with a DOCX-aware tool (for example `python-docx`) instead of assuming its contents. When a batch authorizes modifying it, edit it in place with a DOCX-aware library, preserving the document's styles, tables, and TOC field codes, and verify the result by re-extracting the text and opening/validating the file before generating the patch.

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
docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md
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

The patch must also be generated with `--binary`: the roadmap is a DOCX, so any batch that touches it produces a binary change that a plain text diff cannot represent. The proven method (established on the `ai-week7-8` task and adopted here) is an isolated working clone at the batch's starting commit:

1. Complete the batch in the working clone (no commits, no pushes); keep an explicit list of every file the batch created, modified, or deleted.
2. `git clone --no-hardlinks . /tmp/olai-frontend-patch-build` (any path outside the repository) and `git -C <clone> checkout --detach <start-commit>`.
3. Reproduce only the batch-owned files inside the isolated clone; `git -C <clone> status --porcelain` must show exactly the batch-owned change list.
4. `git -C <clone> add -A` and generate the patch with `git -C <clone> diff --cached --binary --no-color > <patch-file>`.
5. Validate the patch against a pristine clone of the starting commit (`git apply --check`, then apply and compare `status --porcelain` against the change list) before delivering it.

Never stage or unstage the user's pre-existing changes in the real working clone merely to construct a patch.

### Documentation-only batches

Some batches (for example the FR-REB-00 re-baselining) authorize changes only to the execution-context documents themselves. For such batches, "verification" means: the modified documents are readable and internally consistent, no document claims work that did not happen, no out-of-scope file was touched, and (when the DOCX was edited) the DOCX is still a valid, openable Word document. Running application tests is not required and must not be claimed.

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
VERIFY REPO (branch, HEAD, staging containment)
    ↓
READ LIFECYCLE RULES + ROADMAP (DOCX) + PROGRESS  [docs/tasks/Frontend UI redesign/]
    ↓
RECORD STARTING STATE
    ↓
IMPLEMENT ONE BATCH (documentation-only or implementation — as authorized)
    ↓
VERIFY (tests for code batches; readability/consistency for doc batches)
    ↓
UPDATE progress.md
    ↓
GENERATE COMPLETE --binary PATCH (isolated-clone method)
    ↓
VERIFY PATCH ACCESS
    ↓
REPORT
    ↓
STOP
```
