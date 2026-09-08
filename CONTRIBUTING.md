# Contributing to OpenLearn AI

OpenLearn AI is pre-alpha and spec-first. Start with the documented plan and
keep each change small, reviewable, and safe to integrate.

## Sources of truth

1. The [44-week execution plan](planning/Roadmap/44-WEEK-EXECUTION-PLAN.md)
   is the schedule and scope authority.
2. [`docs/README.md`](docs/README.md) identifies which document is
   authoritative for what.
3. The [ADR index](docs/adr/README.md) records accepted architecture
   decisions. Add or update an ADR when a change affects architecture or a
   cross-pod contract.

## Branches and commits

We use trunk-based development. Branch from the current `main`, use a
short-lived branch, open a focused pull request, and merge it promptly after
review and CI succeed. Do not commit directly to `main`.

Use one of these branch prefixes:

```text
feature/<scope>-<description>
bugfix/<scope>-<description>
docs/<description>
chore/<description>
```

Use Conventional Commits. Examples:

```text
feat: add course upload endpoint
fix: reject expired refresh tokens
docs: add ADR index
test: cover invalid login requests
refactor: simplify database session handling
chore: update development dependency
```

## Pull requests and review

Keep pull requests scoped to one purpose. Complete the PR template, link the
relevant issue or sprint item, and ensure the relevant CODEOWNER is requested
for review.

- A normal PR needs **one reviewer**.
- A change to a frozen interface needs **two reviewers**, including the
  relevant pod lead. Frozen interfaces include published API contracts,
  database schema or migrations, shared models, and agreed inter-pod data
  contracts. Ask before changing one; update an ADR when the change is
  architectural.

Before requesting review, confirm:

- [ ] The change is focused and follows project conventions.
- [ ] Tests are added or updated where applicable and pass locally.
- [ ] Documentation and contracts are updated when behavior changes.
- [ ] No secrets, credentials, or `.env` values are committed.
- [ ] CI is green and CODEOWNER review is requested.

Reviewers check correctness, tests, security, documentation, compatibility,
and whether the change stays within its declared scope.

## Run checks locally

### Backend

```bash
cd backend
python -m venv .venv
# Activate .venv using your platform's standard command.
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m ruff check .
python -m pytest
```

### Frontend

```bash
cd frontend
npm ci
npm run lint
npx tsc --noEmit
npm run build
npm run test -- --run  # when a test script exists
```

### Other local workflows

```bash
# OCR benchmark
cd experiments/OCR/ocr-benchmark
uv sync

# Full development stack
docker compose -f infra/docker-compose.dev.yml up
```

CI runs the backend lint and test commands plus frontend lint, typecheck, and
build checks. Run the checks that apply to your change before opening a PR.

## Add a backend module

Create a module only when there is implementation work for it. Following
ADR-0001, place a new domain module under
`backend/app/services/<module-name>/` and keep its interface, service logic,
models, and tests together. Then:

1. Define the boundary and dependencies; use the relevant provider interface
   instead of importing another domain's internals.
2. Add routes or integration points only after agreeing their API contract
   with consuming pods.
3. Add focused tests and any required migration or configuration changes.
4. Update the appropriate documentation and ADR when the module creates or
   changes a cross-pod architectural decision.
5. Run the backend checks and open a focused PR.

Nothing under `experiments/` may be imported by `backend/` or `frontend/`;
benchmark data is evaluation-only.

## Reporting issues

Include the expected result, the actual result, and the smallest reproducible
case. Check [Development Status](README.md#development-status) first: many
planned capabilities are intentionally not implemented yet.
