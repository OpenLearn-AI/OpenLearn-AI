# ADR-0001: Modular monolith — domain modules inside the backend process

- **Status:** Accepted (2026-08-16)
- **Deciders:** Foundation cleanup task (Week 2); ratified by team review
  (Week 4, 2026-08-31)

## Context

The Tech Spec (§C4 target) and DeveloperGuide describe a system with nine
domain responsibilities (ingestion, OCR, embeddings, RAG, knowledge graph,
student model, adaptive engine, generation, analytics). Two structural options
existed for where that logic lives:

- A. Top-level `services/` directory with nine sibling folders (the original
  DeveloperGuide §3/§8 text; the deleted `scripts/setup_project_structure.sh`
  created these empty).
- B. Domain modules as Python packages inside the backend application
  (`backend/app/services/<name>/`), communicating through in-process
  interfaces.

Nothing is implemented yet (backend is a hello-world), so this is the cheapest
moment to fix placement. The repo previously contained *empty* `services/`,
`models/`, `infrastructure/` directories created by the scaffolder —
placeholder structure with no code, contradicting the real layout (`infra/`,
`backend/`).

The team is ≤9 students with no budget; operational simplicity is a stated
constraint (Tech Spec deployment profiles; AI_CONTEXT §9 "no budget for
compute at scale").

## Decision

1. OpenLearn AI is a **modular monolith**: one FastAPI process; domain modules
   communicate via direct in-process interface calls. No microservices, no
   network boundaries between domains, no message bus.
2. Domain modules live as packages under **`backend/app/services/<name>/`**,
   each exposing `interface.py` (contract) + `service.py` (implementation) +
   `models.py` + tests, per the DeveloperGuide's existing module discipline.
   There is **no top-level `services/` directory**.
3. **Do not pre-create module directories.** A module package is created when
   its first real implementation lands. Empty placeholder directories/files
   are prohibited repository-wide (foundation audit, 2026-08-16).
4. AI provider calls remain behind the Provider Abstraction Layer concept
   (spec), to be introduced **when the first real provider call is
   implemented** — not before.

## Consequences

- One deployable unit; local/hybrid/cloud deployment modes remain config
  presets as the spec intends.
- Hard interface discipline is enforced by convention and review (import
  linters can be added later if violations appear), not by process boundaries.
- If a domain ever needs to scale independently, extraction to a separate
  service is possible later because modules communicate only through
  interfaces — but that is explicitly out of scope until evidence demands it.
- The DeveloperGuide was updated (2026-08-16) to reflect this placement.

## Alternatives considered

- **Top-level `services/` siblings** — rejected: adds a second import root for
  a single-process app, and the empty-directory failure mode already occurred.
- **Microservices** — rejected: operationally impossible for a zero-budget
  student team; the spec itself mandates a modular monolith.
