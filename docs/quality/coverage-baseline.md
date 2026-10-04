# Coverage Baseline (NFR-10)

## Policy

Coverage **must not decrease** below the recorded baseline. Raise gradually
per the NFR-10 trajectory. The coverage is measured in CI on the core test
suite (tests excluding `tests/pal` and `tests/documents`, which run in the
dedicated AI-tests job).

## Baseline Record

| Date | Scope | Coverage | Notes |
|---|---|---|---|
| 2026-10-04 | backend/app (core suite) | **67%** (1597 stmts, 521 missed) | First measurement. Measured post-W7 merge (includes material_tasks at 90%). Two config tests failed due to temp-container env limitations, not code defects. |

## Measurement Command

See the CI workflow (backend job) — coverage flags:
--cov=app --cov-report=term --cov-report=xml

## Weakest Areas (improvement candidates)

| File | Coverage | Note |
|---|---|---|
| profile_service.py | 55% | Lowest — candidate for adding tests |
| (future) ingestion chain | - | AI/ML: add tests as chain lands in W8 |
