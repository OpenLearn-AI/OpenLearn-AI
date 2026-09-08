# ADR-0004: Vector store default — pgvector

- **Status:** Accepted (2026-08-31)
- **Deciders:** @MuhammadSeyam (project lead and AI/ML lead), @0Abanoub
  (Backend & Platform lead)

## Context

The technical specification names ChromaDB as its embedded, local-first
default. The Master Roadmap names Qdrant as the default and pgvector as the
F-1 fallback. No vector-store implementation or completed comparison spike is
present in the repository.

The team needs one default before the embedding and retrieval work becomes
load-bearing. The repository already uses PostgreSQL for application data, so
the selected store should keep local development, backup, and deployment
operations proportionate to the current project stage.

## Decision

Use **pgvector in the project's PostgreSQL database** as the default vector
store.

Vector access must remain behind the Provider Abstraction Layer (PAL) vector
database interface. This keeps a future migration possible without coupling
application code to pgvector-specific calls. Qdrant and ChromaDB are not
introduced as services for the current milestone.

This decision intentionally replaces the roadmap's Qdrant default and its
pgvector-only fallback ordering.

## Consequences

- Local and cloud deployments operate one database system for relational data
  and vectors, simplifying configuration, backups, and recovery.
- Pod A owns the PostgreSQL/pgvector operational path; Pod B uses the PAL
  interface for retrieval work.
- Retrieval performance and metadata-filtering behavior must be measured when
  the embedding spike and RAG workload exist. A later ADR may replace this
  decision if evidence shows that a dedicated vector store is required.
- The roadmap and deployment documentation should be aligned with this ADR in
  their next reviewed update.

## Alternatives considered

- **Qdrant:** a capable dedicated store and the previous roadmap default, but
  it adds a separate service and operational surface before that need is
  demonstrated.
- **ChromaDB:** simple for embedded experiments, but it would introduce a
  separate persistence model alongside PostgreSQL for the planned deployment.
- **Continue deferring:** would leave the next implementation work without a
  stable operational default.
