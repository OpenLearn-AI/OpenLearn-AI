# Coverage Baseline (NFR-10)

## Policy

Coverage **must not decrease** below the recorded baseline. Raise gradually
per the NFR-10 trajectory. The coverage is measured in CI on the core test
suite (tests excluding `tests/pal` and `tests/documents`, which run in the
dedicated AI-tests job).

## Baseline Record

| Date | Scope | Coverage | Notes |
|---|---|---|---|
| 2026-10-04 | `backend/app` (core suite) | **67%** (1597 stmts, 521 missed) | First measurement. **Confirmed identical in CI** (263 passed, 28.54s). Weakest areas: pal/providers 20-42%, chunking 29% — AI/ML improvement targets as W8 chain lands. |

## Measurement Command

CI backend job runs: pytest with `--cov=app --cov-report=term --cov-report=xml`

## Weakest Areas (improvement candidates)

| File | Coverage | Note |
|---|---|---|
| profile_service.py | 55% | Lowest service — candidate for adding tests |
| pal/providers/* | 20-42% | AI/ML targets as W8 ingestion chain lands |
| documents/chunking.py | 29% | Will rise when W8 chain adds chunking tests |
