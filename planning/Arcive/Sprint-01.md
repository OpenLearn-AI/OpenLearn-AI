# Sprint 01 — Repository & Governance Setup (Week 1, Aug 3–9, 2026)

> Retrospective record, reconstructed 2026-08-16 from git history (evidence in
> parentheses). No live sprint log was kept during the week — that itself was
> a process gap, fixed from Sprint 02 onward.

## What actually happened (per git log)

- Repo governance: CODEOWNERS, PR template, CI workflow — backend (lint +
  pytest) and conditional frontend jobs (PR #1, #2; `9c88693`, `4a792c7`).
- Dependency repairs: requirements.txt re-encoded UTF-16 → UTF-8, Windows-only
  `pywin32` removed (commit `20649d6`); `httpx2` added for starlette
  TestClient (commit `6c809e1`, unpinned at the time).
- Dev environment: `infra/docker-compose.dev.yml` (backend + postgres) +
  backend Dockerfile, verified working (commit `1f5e458`).
- Frontend scaffold: Next.js 16 + shadcn initialized (commits `c86338a`,
  `aa6aa9f`).
- Planning: 44-week execution plan committed (`571049a`).
- Backend skeleton: FastAPI hello-world + smoke test, CI frontend-test fix
  (PR #3, #4).

## Planned vs. delivered

Not delivered from the W1 plan: the 20-PDF golden set + `manifest.json`
(`tests/data/golden_pdfs/`) and `docs/mvp.md`. The golden set slipped into
Week 2 work (started as the OCR benchmark pilot — see
`experiments/OCR/ocr-benchmark/`).

## Carried into Sprint 02

- OCR benchmark dataset + ground-truth pipeline (Week 2 focus).
- `docs/mvp.md` sign-off, backend hardening items, staging deploys —
  re-scoped in Sprint 02 against actual capacity.
