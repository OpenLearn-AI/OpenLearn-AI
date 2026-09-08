# ADR-0002: Documentation authority hierarchy

- **Status:** Accepted (2026-08-16)
- **Deciders:** Foundation cleanup task (Week 2); ratified by team review
  (Week 4, 2026-08-31)

## Context

The repository accumulated multiple documents that partially or fully
contradict each other (vector store, roadmap authority, requirements docs, ADR
location, doc paths). 18 empty placeholder files were linked from the README
as if they were content. Raw AI-generated research (~600 KB) sat inside
`docs/` beside authoritative specifications with nothing marking it
non-authoritative. Result: a new contributor could not tell which document to
trust — the exact failure mode the DeveloperGuide §7 warns about.

## Decision

The authority hierarchy is defined in **`docs/README.md`** (the documentation
map). In summary:

1. **ADRs (`docs/adr/`)** override every other document, including older
   Tech Spec text.
2. **README.md** — entry point/orientation.
3. **AI_CONTEXT.md** — current-state summary (must be kept truthful; stale
   claims are bugs).
4. **Tech Spec v4 (`docs/design/…Technical_Specification.md`)** — design
   authority for product/technical requirements.
5. **44-week execution plan** — schedule authority; Master Roadmap is strategy
   context; Arabic guide is a non-authoritative reading companion.
6. **OCR Benchmarking Handbook** — methodology authority for OCR evaluation.
7. **`docs/research/`** — informs decisions, never implementation authority;
   `research/raw/` is explicitly unprocessed input.

Supporting rules:

- Contradictions between documents are **recorded, not silently resolved**
  (this ADR's sibling, ADR-0004, demonstrates the pattern for deferred
  decisions).
- Empty placeholder documents are prohibited; topics get a page when real
  content exists.
- Historical/design-phase artifacts live in `docs/archive/` and raw research
  in `docs/research/raw/`, both explicitly non-authoritative.
- ADR location is **`docs/adr/`** (supersedes the DeveloperGuide's earlier
  `docs/architecture/ADR/` path; guide updated).

## Consequences

- Link rot and authority disputes have a resolution rule: check the hierarchy.
- Document moves (ai-reports → research/raw) keep git history via rename.
- Any future doc must state its place in the hierarchy or link to it.

## Alternatives considered

- **Merging all planning docs into one** — rejected: the 44-week plan and
  master roadmap serve different audiences; declaring authority is cheaper
  than merging 900 KB of content.
- **Deleting raw research** — rejected: it contains useful leads (Studyield,
  Qari-OCR, cost playbooks); archiving preserves value without lending
  authority.
