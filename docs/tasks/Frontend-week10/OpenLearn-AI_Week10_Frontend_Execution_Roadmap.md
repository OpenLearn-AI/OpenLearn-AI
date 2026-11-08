# OPENLEARN-AI FRONTEND

## Week 10 --- Retrieval Foundation: Frontend Execution Roadmap

**Execution model:** contract verification → authorized search batch →
small validated patches → evidence-ledger update\
**Owner pod:** Pod C --- Frontend (Ibrahim, Waseem)\
**Week:** 10 --- Retrieval Foundation\
**Status at planning time:** **PREPARATION ONLY / IMPLEMENTATION
BLOCKED** until the retrieval API contract is merged into
`docs/openapi.json` and Seyam explicitly authorizes the frontend batch.

------------------------------------------------------------------------

## 1. Purpose and Governing Rules

This roadmap translates the Week 10 task into a frontend-only execution
plan. Its deliverable is a basic search-results interface that uses the
real retrieval endpoint and displays chunk results with document
navigation wherever the merged contract provides enough provenance to
build a valid destination.

The Week 10 task is explicit: preparation may begin now, but
implementation must not begin against a draft or guessed API. The
frontend batch is unblocked only after both conditions are true:

1.  The retrieval endpoint, request/response schemas, authentication,
    ownership behavior, and filters are merged into the CI-guarded
    `docs/openapi.json`.
2.  Seyam explicitly authorizes the frontend batch.

**A merged contract alone is not authorization. Authorization alone is
not a substitute for a merged contract.**

### Non-negotiable rules

-   One authorized batch at a time.
-   One small patch at a time; validate it before starting the next
    patch.
-   Contract-first: derive request, response, validation, and UI
    assumptions from the merged OpenAPI contract.
-   Use existing `apiFetch`, Zod, TanStack Query, feature-slice, and
    async-state conventions.
-   Preserve Keycloak initialization, `AuthGuard`, protected route
    behavior, existing course/material behavior, API error mapping, and
    cache-key conventions.
-   Do not modify backend files, Keycloak configuration, vector-provider
    logic, evaluation code, CI evaluation jobs, or DevOps/AI-ML
    deliverables.
-   Do not introduce a new state-management library, API client, search
    framework, or design system.
-   No fake search results, guessed endpoint paths, invented response
    fields, arbitrary relevance scores, or mock "AI answers."
-   No hybrid retrieval, BM25, reranking, RAG/chat, WebSockets,
    chunk-inspection tools, citations, enrollment, or analytics. These
    belong to later weeks.
-   Record actual results in
    `OpenLearn-AI_Frontend_Execution_Progress.md`; never mark a patch
    complete because code was merely written or a PR was merged.

------------------------------------------------------------------------

## 2. Week 10 Frontend Objective

Deliver a minimal, accessible, responsive search experience attached to
the existing course-detail content hub, using the actual Week 10
retrieval contract.

The user should be able to: 1. Open a course they are authorized to
view. 2. Enter a query and submit it intentionally. 3. Receive search
results from the real retrieval API, constrained to the current course
where supported by the contract. 4. Understand the result content and
available provenance (for example, chunk/document identifiers and page
information only where actually returned). 5. Follow a result to its
corresponding document/content destination only if the contract and the
existing Week 9 document-content surface support a real destination. 6.
Understand loading, empty, validation, authentication/authorization, and
server/network failure states. 7. Retry a failed search without
refreshing the whole page.

The interface is a **retrieval results surface**, not a chat interface
and not a promise that a generated answer exists.

### Definition of success

-   Search calls the merged endpoint through the existing API boundary.
-   Request and response data are validated against the contract with
    the project's Zod conventions.
-   Results respect course/document filters and authorization behavior
    defined by the backend.
-   Provenance is preserved and presented without inventing metadata.
-   Search state is predictable and does not leak results between
    courses, users, or query keys.
-   All required frontend checks pass and evidence is recorded in the
    progress ledger.

------------------------------------------------------------------------

## 3. Dependency Gate --- Patch W10-FE-00

**Type:** Read-only preparation / implementation gate\
**Implementation status:** May run immediately; no product code changes.

### Tasks

1.  Confirm the working tree, branch, and HEAD. Do not switch branches
    or merge unrelated work as part of this patch.
2.  Read the current frontend execution ledger and verify the status of
    the course-detail hub and Week 9 extracted-text/document
    destination.
3.  Inspect the latest merged `docs/openapi.json` and locate the
    retrieval operation.
4.  Record the exact:
    -   HTTP method and path;
    -   query/request fields and constraints;
    -   response schema and nullable/optional fields;
    -   authentication requirements;
    -   course/document filter semantics;
    -   error responses;
    -   provenance fields available for each result;
    -   whether a result contains enough information to link to the Week
        9 document/content view.
5.  Confirm the OpenAPI drift guard has passed in the contract's merged
    state, using CI evidence or the team's accepted verification record.
6.  Obtain explicit authorization from Seyam and record who authorized
    the batch and when.
7.  If either dependency is missing, stop after documenting the blocker.
    Do not create an API client, schema, UI, endpoint constant, or
    speculative fixture.

### Files

-   Read-only: `docs/openapi.json`
-   Read-only:
    `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md`
-   Read-only: current course detail, course feature slice, API
    boundary, and document-view implementation as they exist on the
    active branch.

### Validation / completion

-   Contract details and authorization are recorded in the ledger.
-   The exact repository baseline is recorded.
-   No application code changes.
-   **Gate result:** `BLOCKED` or `AUTHORIZED`; do not infer the result.

------------------------------------------------------------------------

## 4. Patch Plan

Patch IDs below are proposed Week 10 frontend tracking IDs, not a claim
that work has started. Execute only the first eligible patch, then stop
for validation and ledger update. File paths are candidate paths based
on the roadmap's established structure; confirm them in the active
repository before editing. Do not create parallel files when an existing
equivalent is present.

### Patch W10-FE-01 --- Contract-to-Frontend Design Lock

**Prerequisite:** W10-FE-00 is `AUTHORIZED`.

**Objective:** Translate the merged retrieval contract into a small
frontend implementation plan before coding.

**Tasks** - Map the retrieval request and response types to the existing
course feature conventions. - Decide whether the query is submitted on
button/Enter, whether optional filters are exposed, and which filters
are required by the task/contract. Do not expose filters the endpoint
does not support. - Define how course scope is derived from the current
`/courses/[id]` route and passed to the API, if supported by the
contract. - Define the result display fields using only contract-backed
data. - Define link behavior: link to an existing document/content route
only when a valid destination can be constructed from supported fields;
otherwise render provenance as non-interactive text. - Decide query-key
dimensions from the actual request: course ID, normalized/submitted
query, and any supported filters. Avoid keys that can collide across
courses. - Write down the intended files and tests before editing.

**Likely files** - Existing `features/courses/*` or a retrieval/search
feature slice if the repository already has a suitable domain
boundary. - Existing course detail route/component. - Existing
API/schema/query conventions and tests.

**Must NOT change** - Backend or OpenAPI files. - Keycloak setup,
`AuthGuard`, route guards, course CRUD mutations, materials
upload/status logic, or unrelated redesign surfaces. - Any future hub
slot for Week 11+.

**Validation** - Review the mapping against the merged contract
field-by-field. - Confirm no request/response property is inferred from
the Week 10 task prose alone.

**Completion** - A short contract mapping and exact file plan are
recorded. - No runtime behavior changed unless a minimal
documentation-only note is explicitly authorized.

------------------------------------------------------------------------

### Patch W10-FE-02 --- Retrieval Schema and API Boundary

**Prerequisite:** W10-FE-01 reviewed and the batch remains authorized.

**Objective:** Add the smallest contract-backed request/response
validation and API call using existing project conventions.

**Tasks** - Add or extend Zod schemas for the actual request parameters
and response payload. - Infer TypeScript types from those schemas where
that matches current feature conventions. - Implement the retrieval call
through `apiFetch`; do not use raw `fetch` if the repository's API
boundary is the standard path. - Preserve standard `ApiError` handling
and response-validation behavior. - Pass course/document filters only
when supported by the merged contract. - Avoid logging query text or
returned document content unnecessarily. - Do not add a new global
client, token mechanism, or auth flow.

**Likely files** - `lib/api.ts` only if an existing shared API helper
must be reused or minimally extended; avoid changing shared behavior
without necessity. - `features/courses/schemas.ts` or the existing/new
appropriately scoped feature schema module. - Existing feature API
module, or a small search/retrieval API module if no current equivalent
exists. - Focused schema/API unit tests and fixtures.

**Must NOT change** - Global API error taxonomy unless a contract-backed
defect makes a change necessary and separately authorized. - Keycloak
initialization or bearer-token handling. - Existing
course/profile/material schemas unrelated to search. - Backend code or
`docs/openapi.json`.

**Validation** - TypeScript typecheck. - Focused schema/API tests for
valid response, optional/null fields, malformed response, and
representative API errors. - Verify the exact URL, method, and
serialized parameters against the merged contract. - Confirm no guessed
response field survives in code or fixtures.

**Completion** - Contract-backed retrieval API function and tests
pass. - Patch diff is limited to retrieval-related code and necessary
focused tests.

------------------------------------------------------------------------

### Patch W10-FE-03 --- Query Hook and Search-State Isolation

**Prerequisite:** W10-FE-02 is validated.

**Objective:** Connect the retrieval API to TanStack Query without
changing the application's state architecture.

**Tasks** - Add a query hook using the existing TanStack Query
patterns. - Build a stable query key from the real request dimensions,
including course ID and submitted query; include any supported filters
that affect the result. - Do not issue a request for blank/invalid input
or until the user has submitted a valid query, unless the existing
product pattern and authorization explicitly choose another behavior. -
Prefer explicit submit semantics so typing does not produce a request
per keystroke. - Keep results isolated when the user changes course or
query. - Define stale/refetch behavior conservatively; do not add
polling or realtime behavior because Week 10 search does not require
it. - Ensure retry behavior follows existing query conventions and does
not mask authorization failures.

**Likely files** - Retrieval feature hook/query module. - Existing
query-key module only if the new key belongs there under current
conventions. - Focused hook tests if the repository has a suitable
query-test pattern.

**Must NOT change** - Global QueryClient defaults. - Existing
course/profile query keys or invalidation logic. - Zustand/auth store
architecture. - Automatic polling, WebSockets, or chat/session state.

**Validation** - Tests cover blank input, submit, changed query, changed
course ID, supported filter changes, loading/error transition, and
preventing stale cross-course results. - Typecheck and focused unit
tests pass.

**Completion** - Search state is deterministic and scoped correctly; no
visible UI is required to be complete until the hook passes its focused
tests.

------------------------------------------------------------------------

### Patch W10-FE-04 --- Course-Hub Search Form and Results

**Prerequisite:** W10-FE-03 is validated.

**Objective:** Add the basic search interface to the existing
course-detail hub, reusing established UI primitives.

**Tasks** - Place the search surface in the course-detail hub in the
approved location; do not create a new route unless the merged contract
and explicit product authorization require it. - Add a clearly labelled
query input, submit button, and accessible form semantics. - Support
keyboard submission and preserve visible focus indicators. - Display
result count only if it is returned or can be accurately derived from
the returned collection; do not imply total backend matches when only a
page/top-k is returned. - Render result cards/rows using only actual
returned fields. - Present available chunk/document/page provenance in a
compact, understandable way. - Show a clear initial prompt before a
search is submitted. - Show loading, no-results, and error states with
the existing `LoadingBlock`, `ErrorState`, `EmptyState`, or equivalent
shared components. - Provide a retry action for recoverable request
failures. - Make any result-to-document link conditional on a real,
supported destination. If the Week 9 viewer or endpoint is unavailable
on this branch, do not create a dead link or a fake viewer. - Keep the
UI as search results only: no answer synthesis, chat composer,
citations, relevance score display unless explicitly returned and
approved, or "AI is thinking" language.

**Likely files** - `app/(app)/courses/[id]/page.tsx` or its existing
course-detail component. - A small search form/results component under
the existing `components/courses/` or feature-component convention. -
Shared state components only if an existing component is insufficient;
avoid broad primitive redesign.

**Must NOT change** - Course header/edit/delete behavior. - Materials
upload/register/status lifecycle. - Role/ownership enforcement
assumptions. The backend remains the authorization boundary. - Global
visual system or unrelated routes. - Week 11 chunk-inspection panel,
Week 13 ranking, Week 14 RAG citations, or Weeks 15--16 chat.

**Validation** - Manual walkthrough against a real endpoint and seeded
vectors when available. - Keyboard-only use and screen-reader labels. -
Empty query does not send a request. - Empty results differ from a
request failure. - No results or error state leaks from one course to
another. - Existing course detail and materials behavior still works.

**Completion** - A real contract-backed search can be submitted and its
results/states are usable within the course hub.

------------------------------------------------------------------------

### Patch W10-FE-05 --- Provenance and Document Navigation

**Prerequisite:** W10-FE-04 is validated; contract fields and the
existing Week 9 destination are confirmed.

**Objective:** Make chunk results navigable without inventing a document
model.

**Tasks** - Trace the actual provenance fields from the response to the
existing document/content route or component. - Add a link only when the
destination route and required identifier are real and supported. -
Include page information only when supplied by the response and
meaningful to the destination. - Keep identifiers and metadata readable
but do not expose storage keys, presigned URLs, internal provider
details, or unrelated ingestion internals. - Ensure links preserve the
current course/document context as required by existing route
conventions. - If no safe destination exists, display the available
provenance as plain text and record the missing dependency; do not block
the basic results list for an unsupported deep link.

**Likely files** - Search result component. - Existing Week 9
extracted-text viewer/document route if present. - Focused
component/story tests.

**Must NOT change** - Week 9 document API or viewer behavior. - No new
document endpoint or route invented in frontend. - No chunk-inspection
panel (Week 11), citation system (Weeks 13--14), or chat (Weeks 15--16).

**Validation** - Each rendered link resolves to a real destination and
uses the correct identifier. - No broken/dead links; no URL built from
guessed fields. - Provenance display remains correct when optional
page/document metadata is absent.

**Completion** - Result-to-document navigation is verified where
supported; unsupported navigation is explicitly recorded rather than
faked.

------------------------------------------------------------------------

### Patch W10-FE-06 --- Accessibility, Responsive Layout, and Storybook

**Prerequisite:** W10-FE-04 is validated; may be combined with W10-FE-05
only if the authorized batch owner explicitly approves that scope.

**Objective:** Bring the new search pattern to the project's existing UI
quality bar without expanding the design-system scope.

**Tasks** - Add Storybook stories for the meaningful states: initial,
loading, results, no results, validation feedback, recoverable error,
and provenance with/without a real link. - Use the existing
Storybook/axe setup; do not introduce a new accessibility framework. -
Check labels, semantic headings, keyboard order, focus visibility,
button names, and error announcement behavior. - Check narrow/mobile
layout and long Arabic/English query/result text. - Use logical CSS
properties and direction-safe layout patterns consistent with the
existing RTL-ready design. - Verify light/dark theme readability using
existing tokens, not new raw color values. - Ensure long snippets wrap
without horizontal overflow and controls remain operable at small
widths.

**Likely files** - Search component stories and colocated tests. -
Existing search component styles only. - Shared primitives only when a
genuine reusable defect is found and separately scoped.

**Must NOT change** - Global design tokens or shell styling without
separate authorization. - Full i18n framework or a broad translation
pass. - Storybook/Chromatic CI configuration unless a separately
identified failure directly blocks this batch and is authorized.

**Validation** - Storybook test/a11y checks pass. - Keyboard and mobile
checks pass. - Both themes and LTR/RTL direction are inspected. - No axe
violations introduced by the search pattern.

**Completion** - Search states are documented in stories and meet the
existing accessibility/responsive conventions.

------------------------------------------------------------------------

### Patch W10-FE-07 --- Regression, Contract Check, and Ledger Closure

**Prerequisite:** All implementation patches are individually validated.

**Objective:** Prove the new search surface does not regress protected
frontend behavior and record evidence accurately.

**Tasks** - Add/update focused unit tests for schema, API, query hook,
result rendering, and supported document links. - Add/update a Storybook
interaction test if the existing test setup supports it. - Add an E2E
assertion only if the current staging environment has the merged
endpoint and reproducible seeded vectors; avoid brittle E2E tests
dependent on unseeded external data. - Run the existing frontend quality
matrix, using the scripts actually present in `frontend/package.json`: -
lint; - typecheck; - unit tests; - Storybook tests/a11y; - production
build; - relevant Playwright E2E specs when credentials/environment are
available. - Manually re-check existing course CRUD, auth guard/redirect
behavior, and the materials surface in the course hub. - Verify no
changes landed in backend, Keycloak, unrelated route, or CI
configuration. - Update the frontend execution progress ledger with
patch IDs, changed files, test commands/results, environment, commit/PR
references, blockers, and any deferred verification. - Create a
validated binary patch/diff artifact according to the existing team
lifecycle rules. Do not claim a binary patch exists unless it was
actually generated and checked.

**Must NOT change** - Test infrastructure or workflow policy to make a
failure disappear. - Skip or weaken existing tests. - Mark staging
validation complete based only on local mocks or a merged PR.

**Validation** - All applicable checks have actual recorded outcomes. -
Any unavailable staging/E2E check is marked pending with its reason, not
passed. - Final diff is reviewed for scope, protected behavior, and
accidental changes.

**Completion** - The authorized search batch is validated and recorded
in the progress ledger. Stop after closure; do not automatically start
Week 11 work.

------------------------------------------------------------------------

## 5. Protected Behavior Checklist

Before and after the authorized batch, verify that the patch has not
changed:

-   Keycloak client construction, initialization options, PKCE/check-sso
    configuration, or login/logout/register call sites.
-   `AuthGuard` placement and behavior, auth redirects, and signed-out
    route handling.
-   `apiFetch` as the API boundary and existing `ApiError` mapping.
-   Existing Zod validation conventions.
-   TanStack Query provider/client defaults and unrelated query/cache
    keys.
-   Course list/detail ownership assumptions and course CRUD behavior.
-   Existing materials upload → register → list → status lifecycle.
-   Profile behavior and profile query/mutation semantics.
-   Existing route behavior, including not-found handling.
-   Existing visual tokens, theme strategy, and RTL conventions.
-   CI workflow triggers, deployment configuration, backend code, and
    Keycloak realm configuration.

Any required exception must be explicitly reviewed and recorded; it must
not be slipped into the search patch.

------------------------------------------------------------------------

## 6. Test and Evidence Matrix

  ----------------------------------------------------------------------------
  Area                         Required evidence       Completion rule
  ---------------------------- ----------------------- -----------------------
  Contract gate                Merged                  Both must exist before
                               `docs/openapi.json`     implementation
                               operation + explicit    
                               authorization           

  Schema/API                   Focused tests for valid Pass against the actual
                               and invalid contract    merged schema
                               payloads, request       
                               serialization, and API  
                               errors                  

  Query behavior               Query-key isolation,    No stale cross-course
                               empty-input prevention, results
                               course/query/filter     
                               changes                 

  UI states                    Initial, loading,       Distinct and truthful
                               results, empty,         states
                               validation, error,      
                               retry                   

  Provenance                   Real returned           Never infer unavailable
                               identifiers/page        fields
                               metadata                

  Navigation                   Existing route resolves No dead or speculative
                               using supported         links
                               identifiers             

  Accessibility                Keyboard, labels,       No new violations
                               focus, axe/Storybook    

  Responsive/theme/direction   Mobile width,           No overflow or unusable
                               light/dark, LTR/RTL,    controls
                               long text               

  Regression                   Existing auth, CRUD,    No protected behavior
                               materials, profile      regression
                               checks                  

  CI/build                     lint, typecheck, unit,  Actual command results
                               Storybook, build;       recorded
                               relevant E2E            

  Ledger                       Patch IDs, diff, test   Reflects observed
                               evidence, blockers,     results only
                               status                  

  Binary patch                 Generated and inspected Do not claim if not
                               patch/diff artifact     produced
  ----------------------------------------------------------------------------

------------------------------------------------------------------------

## 7. Cross-Team Dependencies and Blocker Handling

  -----------------------------------------------------------------------
  Dependency              Owner                   Frontend response
  ----------------------- ----------------------- -----------------------
  Retrieval endpoint and  Pod A / Backend         Keep implementation
  stable request/response                         blocked; record missing
  contract in                                     contract details
  `docs/openapi.json`                             

  Explicit batch          Seyam / product owner   Do not implement until
  authorization                                   received

  Stored vectors and      Pod B / AI-ML           Use for realistic
  repeatable query                                integration validation;
  fixture                                         do not substitute mock
                                                  results as staging
                                                  evidence

  Deployed retrieval      Pod D / DevOps-QA       Use for end-to-end
  endpoint and staging                            verification when
  smoke test                                      available

  Week 9 document-content Backend + existing      Link only if
  destination             frontend state          endpoint/route is real
                                                  and its identifier
                                                  contract is known
  -----------------------------------------------------------------------

Raise a blocker promptly if the Thursday merge cutoff is at risk. The
frontend can complete read-only contract review and file mapping while
waiting, but cannot implement guessed shapes to save time.

------------------------------------------------------------------------

## 8. Explicit Out of Scope

-   Backend retrieval service, endpoint, OpenAPI publication, vector
    DB/provider configuration, embedding logic, and ownership
    enforcement.
-   AI/ML corpus ingestion, evaluation manifest, evaluator, precision@5
    measurement, or OCR benchmark.
-   DevOps runner, staging smoke-test implementation, CI evaluation job,
    Sentry worker verification, or deployment changes.
-   Hybrid retrieval, BM25, reranking, ranking scores unless later
    explicitly contracted and authorized.
-   Chunk-inspection/source panel (Week 11).
-   RAG answers and citation chips (Weeks 13--14).
-   Chat sessions, streaming, WebSockets, or realtime migration (Weeks
    15--16).
-   Enrollment, analytics, knowledge graph, quizzes, or admin UI.
-   New routes, fake results, mock-only product behavior, broad
    redesign, or unrelated dependency upgrades.

------------------------------------------------------------------------

## 9. Ledger Entry Template

Use the existing ledger format if it differs; preserve its conventions
and record at least:

-   **Batch/Patch ID:** `W10-FE-00` ... `W10-FE-07`
-   **Status:** `BLOCKED` / `AUTHORIZED` / `IN PROGRESS` / `VALIDATED` /
    `DEFERRED`
-   **Baseline:** branch, HEAD, working-tree status
-   **Authorization:** who, when, evidence/link
-   **Contract:** merged operation path, schema/version/commit, OpenAPI
    drift-guard result
-   **Files changed:** exact paths
-   **Patch artifact:** location/hash, only if actually generated
-   **Validation:** exact commands, exit codes, CI run links, staging
    environment and test data
-   **Manual checks:** keyboard, mobile, theme, direction, course
    isolation, result navigation
-   **Blockers/deferred checks:** explicit reason and owner
-   **Outcome:** what works, what remains unverified, next authorized
    patch

Do not rewrite historical batch statuses to make the Week 10 work appear
complete. The ledger remains the execution record; this document is the
plan.

------------------------------------------------------------------------

## 10. Execution Sequence and Stop Rules

1.  Run W10-FE-00 and establish whether the contract and authorization
    gates are satisfied.
2.  If blocked, update the ledger and stop. Preparation is the only
    permitted work.
3.  If authorized, execute W10-FE-01, validate, and update the ledger.
4.  Execute W10-FE-02 only after W10-FE-01 is accepted; validate and
    record.
5.  Continue sequentially through W10-FE-07, one patch at a time.
6.  If a patch fails validation, fix or revert that patch before moving
    forward.
7.  If the contract changes, stop implementation, compare the changed
    schema, and re-authorize affected scope before continuing.
8.  After W10-FE-07, record the actual outcome and stop. Week 11 chunk
    inspection is a separate future batch.

**Current recommendation:** Start with **W10-FE-00 only**. Based on the
supplied Week 10 task, the search contract and explicit authorization
are prerequisites, not facts to assume.
