# Sprint 02 — Foundation & OCR Benchmark (Week 2, Aug 10–16, 2026)

> Live sprint record. Scope was re-baselined against actual team capacity —
> see "Deliberately descoped" below. Roadmap reference: Week 2 of the
> [44-week execution plan](Roadmap/44-WEEK-EXECUTION-PLAN.md) (schedule authority).

## Sprint goal

Make the repository a trustworthy, reproducible foundation — clean structure,
one authority per decision, healthy CI — and stand up the OCR benchmark
pipeline in the correct scientific order (ground truth → metrics → one engine
→ validate harness → more engines).

## Scope (committed)

- [x] P0 dependency fixes: curated `backend/requirements.txt`; `httpx2`
      pinned correctly (investigated: not a typo — required by starlette 1.6
      TestClient)
- [x] Repository foundation cleanup: archive raw AI research
      (`docs/research/raw/`), fill/remove empty placeholder docs, delete
      superseded scaffolder script, repair README links
- [x] Documentation authority: `docs/README.md` hierarchy; ADRs 0001–0004;
      `AI_CONTEXT.md` refreshed; `docs/repository-foundation-audit.md`
- [x] CI repair: frontend typecheck + production build added; backend
      pipeline verified locally in a clean venv
- [x] OCR benchmark scaffold (`experiments/OCR/ocr-benchmark/`): pinned uv
      project, 4-document pilot with SHA-256 provenance (rights UNKNOWN),
      roadmap-compatible manifest, annotation guideline draft
- [ ] Ground-truth pilot transcription (~6 pages) — next task, after
      guideline review
- [ ] Metrics module (raw/normalized CER, WER) with unit tests — next task
- [ ] First reproducible PaddleOCR benchmark run — after GT + metrics

## Deliberately descoped from the roadmap's Week-2 DoD (capacity)

Deferred with explicit reasons (needs team/TPM confirmation):

1. `docs/mvp.md` sign-off — needs all pod leads; text exists in the roadmap
   (§Cross-Pod Integration) and can be ratified quickly.
2. OpenAPI/CORS/`/health` + SQLAlchemy async session — backend hardening,
   valuable but not blocking the benchmark critical path; next backend task.
3. Staging deployments (backend + frontend preview URLs) — no staging
   environment exists yet.
4. Design tokens + Storybook; `embedding-spike-methodology.md` — Pod C/B
   capacity; embedding spike is W5, methodology due before it.
5. `backend/app/eval/` harness scaffold — will be seeded from the benchmark's
   `ocrbench.core` when metrics land, avoiding two competing abstractions.
6. Demo PDF selection (`tests/data/demo_pdf/v0.4.pdf`) — needs B-Lead
   confirmation it is OCR-able.

## Open decisions (blocking later work)

- Vector store default: ChromaDB vs Qdrant — deferred with evidence criteria
  in `docs/adr/0004`; must be decided before the embedding spike (W3–4).
- `OL-C-004` (`Data+Structre+lect1.pdf`) rights: obtain lecturer permission
  or replace — see `experiments/OCR/ocr-benchmark/docs/provenance.md`.
- Team-capacity re-baseline of the 44-week plan (repo progress vs the
  9-person plan).
