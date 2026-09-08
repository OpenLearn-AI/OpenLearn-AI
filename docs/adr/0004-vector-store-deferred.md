# ADR-0004: Vector store default (ChromaDB vs Qdrant) — DEFERRED

- **Status:** Superseded (2026-08-31) by
  [ADR-0004 (pgvector)](./0004-vector-store-pgvector.md)
- **Deciders:** Pending — AI/ML pod lead + tech lead (this ADR records the
  deferral, not a choice). Kept for historical context; the deferral was
  resolved on 2026-08-31.

## Context

The two authoritative-adjacent documents disagree on the default vector
store:

- **Tech Spec v4 §10.3** default: **ChromaDB** (embedded mode, local-first;
  ~15 mentions; Qdrant appears only as a scaling alternative, §1218 table).
- **Master Roadmap / deployment docs**: **Qdrant** as default, with fallback
  F-1 "Qdrant → pgvector".

`AI_CONTEXT.md` already flagged this as unresolved. Neither document records
an evaluation; the counts of mentions are not evidence. No vector-store code
exists anywhere in the repository, so nothing currently depends on either.

## Decision (historical)

This ADR originally **deferred the choice** and defined the evidence required
before deciding. The deferral is now **superseded** by
[ADR-0004 (pgvector)](./0004-vector-store-pgvector.md) (2026-08-31), which
selects pgvector as the project default. This record is retained so the
reasoning and evaluation criteria that led to that decision remain traceable.

### Evidence originally required before deciding

1. **Embedding spike results (W3–4)** — BGE-M3 vs OpenAI embedding quality on
   the 10–20 Arabic/English query–chunk pairs (roadmap W2 methodology doc) —
   including vector dimension and index size for a realistic course corpus
   (target: 3 courses × 5–10 PDFs).
2. **Local-mode constraint check** — ChromaDB embedded (in-process, zero
   extra services) vs Qdrant (extra container; Qdrant also offers a local
   mode that must be validated) on the Local profile's 16 GB RAM target.
3. **Metadata filtering needs** — chunk filtering by course/document/concept
   from the spec's retrieval design; compare filter capabilities and query
   ergonomics in current Python clients.
4. **Persistence/backup story** per deployment mode (Local student machines
   vs Cloud), including pgvector's appeal as a Postgres-only fallback (F-1)
   if a second storage system proves operationally expensive.
5. **Migration cost** — collection export/import between ChromaDB and Qdrant,
   since the PAL vector-DB interface means application code should not care,
   but operational tooling will.

## Consequences

- The deferral prevented a coin-flip choice from becoming load-bearing while
  evidence was gathered.
- The superseding ADR-0004 (pgvector) now selects a single default store;
  Qdrant and ChromaDB remain viable future alternatives if a dedicated store
  is later warranted.

## Alternatives considered (as of the original deferral)

- **Adopt ChromaDB now** (spec default; embedded; simplest local story) —
  considered premature at deferral time.
- **Adopt Qdrant now** (roadmap default) — considered premature at deferral
  time.
- **pgvector immediately** — attractive operationally (one datastore); this
  is the option eventually selected by the superseding ADR-0004.
