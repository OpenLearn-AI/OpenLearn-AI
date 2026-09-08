# Documentation Map & Authority

One authoritative source per topic. When documents conflict, this hierarchy
decides (decision recorded in [ADR-0002](adr/0002-documentation-authority.md)):

1. [`ADR`](adr/) — binding architecture decisions. **ADRs override every other
   document**, including older parts of the specification.
2. [`README.md`](../README.md) — repository entry point and developer orientation.
3. [`AI_CONTEXT.md`](../AI_CONTEXT.md) — current repository state (AI/contributor context).
4. [`design/OpenLearn_AI_v4_Technical_Specification.md`](design/OpenLearn_AI_v4_Technical_Specification.md)
   — product & technical design authority.
5. [`planning/Roadmap/44-WEEK-EXECUTION-PLAN.md`](../planning/Roadmap/44-WEEK-EXECUTION-PLAN.md)
   — schedule authority (what ships when). The
   [Master Roadmap](../planning/Roadmap/MASTER_ROADMAP.md) is strategy context;
   [ROADMAP_GUIDE_AR.md](../planning/Roadmap/ROADMAP_GUIDE_AR.md) is an Arabic
   reading companion (non-authoritative).
6. [`../experiments/OCR/OCR_BENCHMARKING_HANDBOOK.md`](../experiments/OCR/OCR_BENCHMARKING_HANDBOOK.md)
   — scientific methodology authority for OCR evaluation.
7. [Research](research/) — supporting research. **Informs decisions; never
   implementation authority.** Raw/unprocessed research input lives in
   [research/raw/](research/raw/) and is explicitly non-authoritative.

## Architecture & design

| Topic | Authority |
|---|---|
| System architecture overview | [`architecture/SystemArchitecture.md`](architecture/SystemArchitecture.md) |
| Data flow overview | [`architecture/DataFlow.md`](architecture/DataFlow.md) |
| Deployment modes & hardware profiles | [`design/OpenLearn_AI_System_Requirements_and_Deployment_Profiles.md`](design/OpenLearn_AI_System_Requirements_and_Deployment_Profiles.md) (engineering) · user-facing edition: [`design/OpenLearn_AI_User_System_Requirements_Guide.md`](design/OpenLearn_AI_User_System_Requirements_Guide.md) |
| Coding standards, git workflow, PR checklist | [`design/DeveloperGuide.md`](design/DeveloperGuide.md) |
| Repository history & decisions record | [`../CHANGELOG.md`](../CHANGELOG.md) |

## Planning

| Topic | Authority |
|---|---|
| Schedule (week-by-week) | [`../planning/Roadmap/44-WEEK-EXECUTION-PLAN.md`](../planning/Roadmap/44-WEEK-EXECUTION-PLAN.md) |
| Sprint records | [`../planning/Sprint-*.md`](../planning/) |
| Team structure & agreements | [`../planning/team-roles/TEAM_HANDBOOK_v1.1.md`](../planning/team-roles/TEAM_HANDBOOK_v1.1.md) (roadmap wins on conflict, per its own declaration) |

## Archive

[`archive/`](archive/) — historical design-phase artifacts, kept for
reference, explicitly non-authoritative.

---

### Known deferred decisions

- **Vector store default (ChromaDB vs Qdrant):** resolved — see
  [ADR-0004 (pgvector)](adr/0004-vector-store-pgvector.md) (Accepted,
  2026-08-31). The original deferral is retained for history at
  [ADR-0004 (deferred)](adr/0004-vector-store-deferred.md) (Superseded).
