# OpenLearn-AI — Batch 4.5 Execution: Cross-Team Capability Integration — Materials Lifecycle Completion

**Status: EXECUTED (2026-10-26). Two user-facing capabilities delivered on the owner's explicit authorization (the Batch 4.5 investigation's proposed scope, approved): the extracted-text viewer inside the course-detail Materials region, and the reprocess control for `failed` AND `ready` materials for the owning instructor. All local checks green; the manual owner-stack walkthrough is OUTSTANDING (the standing prerequisite — no API/worker/storage stack in the execution environment). The primary roadmap DOCX is untouched (the owner's explicit deferral).**

| Field | Value |
| --- | --- |
| Batch | 4.5 — Cross-Team Capability Integration: Materials Lifecycle Completion (one cohesive implementation batch; investigation note §6's 14-element spec, authorized by Seyam) |
| Executed at | `frontend-redesign` working clone at `a1a5415c47ccc403a63a86fbf065338452694a41` ("4.5_Investigation_Cross-Team-Capability-Integration" — the owner-applied investigation commit, verified as the `origin/frontend-redesign` tip; clean tree at start) |
| Branch state | `origin/frontend-redesign` = `a1a5415`; `origin/staging` = `41cf511` (NOT merged — the known divergence: staging holds only the 3-line compose binding + PR #80; `frontend-redesign` holds backend Week 9 (PR #81) which serves this batch's three endpoints. Owner/DevOps coordination item, untouched) |
| Contract consumed | Exactly the three Week-9 operations from `docs/openapi.json` (re-verified at implementation time against the tracked spec and `backend/app/api/materials.py`): `GET /v1/materials/{id}/pages` (limit 1–500 default 100, offset ≥ 0; "a shorter page than limit means the last page"), `GET /v1/materials/{id}/pages/{page_number}` (unused — the list endpoint serves the viewer; the single-page read stays unconsumed), `POST /v1/materials/{id}/process` (202 `MaterialAcceptedResponse`; 401/403/404/409 ×2 classes/422/429) |
| Repository changes | 12 paths: 9 modified + 1 new frontend file + this batch note + the execution ledger. No backend, no `docs/openapi.json`, no CI/infra, no roadmap DOCX, no new dependency |
| Verification | typecheck PASS · lint PASS (0/0) · unit **107/107** (+14 new) · Storybook **104/104 across 26 files** (+6 new stories, axe fail-on-error intact) · production build PASS (11 routes, the documented `.env.example` build env) · Playwright collection **10 tests in 4 files** (unchanged) · rendered audit **138/138** (§8) |
| Not run (recorded honestly) | E2E execution and the manual owner-stack walkthrough — no Docker/Keycloak/API/worker/storage in the execution environment; §10 records the exact steps |

---

## 1. What was delivered

### Surface A — the extracted-text viewer (`MaterialTextViewer.tsx`, new)

A lazy disclosure inside an existing `ready` material's row in the hub's Materials region. The control ("Extracted text", `aria-expanded`/`aria-controls`, a chevron that rotates — a vertical glyph, so RTL never mirrors it wrongly) renders only on `ready` rows for ANY hub visitor (the page read is already owner-scoped; the backend's `require_owned_course` on the pages endpoint remains the boundary — presentation, never authorization). The viewer region mounts ONLY while open on a ready material — that mount IS the lazy gate ("do not fetch page content until the user opens the viewer"); a material that leaves `ready` (a reprocess returning it to the pipeline) unmounts the region, and it remounts fresh after invalidation.

- **Reading**: `GET /v1/materials/{id}/pages` through the existing `apiFetch` boundary, validated by the new Zod schemas (`materialPagesResponseSchema` / `materialPageResponseSchema`, mirroring the tracked contract exactly). Pages render as clearly labeled blocks ("Page 1", "Page 2", …) — the contract's own 1-based numbers — with `dir="auto"` on every page's text so Arabic and English each read in their own direction (verified rendered: Arabic resolves `rtl`, English resolves `ltr` under BOTH document directions — plaintext isolation), in a constrained `max-w-[60ch]` reading column with `whitespace-pre-wrap` (the stored text is presented exactly as stored).
- **Honest pagination** (`mayHaveMorePages`): the contract has NO total count, and none is invented — "Load more pages" appears ONLY when the last window came back full (exactly `limit` entries); a shorter window is the last one by contract. Each window is its own cache entry (`[...pages(materialId), offset]`), so loading more never refetches earlier windows.
- **Honest empties**: `pages: []` → "No extracted text stored for this material yet."; a page with empty `text` → "This page has no extractable text."
- **States**: the shared async-state kit — LoadingBlock while pending, ErrorState with the established retry action on failure (`describeMaterialPagesError`: 401 → the session-expiration copy for the global recovery; 403/404 plain ownership/not-found copy, no internal details), all in the region's flat hairline grammar with a `border-s` start-edge rule (verified on the inline-start side under both directions).
- **Never rendered** for queued, processing, or failed materials; no new route; no separate document-viewing subsystem.

### Surface B — the reprocess control (`MaterialProcessControl` + the row's mutation)

A quiet "Reprocess" action in the terminal material-row action area, shown to the user satisfying the existing `canManageCourse` rule (the authenticated course owner with the instructor role — the exact population the backend's `require_instructor` + `require_owned_course` accept; the existing derivation, no competing role system; NOT admin-gated — decision D2 resolved by the implementation, as the investigation recommended). Shown on **both `failed` and `ready` rows** (the owner's explicit approval — D3); never for students, non-owners, queued, or processing materials (students cannot reach the hub at all today).

- **Mutation**: `POST /v1/materials/{id}/process` through `useProcessMaterial` (the same `apiFetch` + Zod boundary). Duplicate-submit protection is the disabled state itself, with the label reading exactly "Requesting…".
- **On the 202**: the honest acceptance message ("Processing is queued — its status appears in the list."), `job_id` logged ONCE for correlation and never queried (the registration rule); the per-material status cache is seeded with the response's own `{material_id, status}` (the 4.1 onboarding seeding precedent) so the EXISTING status poll resumes from the server's answer — no second polling system, no interval change; the course's materials list is invalidated (the row returns to `pending` through the list, the single rendering source); the material's cached page windows are invalidated by prefix (a re-run may change the stored text under the Week 9 keep-more-pages rule).
- **Errors** (`describeMaterialProcessError`): both documented 409 classes surface the backend's own user-readable detail verbatim ("Material is already queued or processing (current status: …)" / "Manual retry budget exhausted (N of 3 manual retries consumed)") — the ONLY honest source of retry-budget information, since `MaterialResponse` exposes no `retry_count` and nothing is pre-computed or predicted; 429 → "Too many requests — wait a moment and try again."; 401/403/404 through the established conventions.
- **Feedback lifecycle** (derived, effect-free): the acceptance note speaks while the pipeline visibly runs and yields to the outcome the moment a terminal state lands; an error speaks while the material still sits in the state the request was made from — the 409/429 classes never change the status, so they persist until the next request, exactly as they should.
- The control itself is a purely presentational component driven by the row (visible/pending/feedback props) — the split that keeps `MaterialRow` focused and makes every state (including the 409) honestly storyable.

## 2. Files changed (exactly these paths)

- Created: `frontend/components/courses/MaterialTextViewer.tsx`; this batch note.
- Modified: `frontend/features/materials/schemas.ts` (the two Week-9 response schemas; every existing schema byte-preserved); `frontend/features/materials/keys.ts` (the `pages(materialId)` branch under `materialKeys.all`; existing keys untouched); `frontend/features/materials/flow.ts` (the viewer/reprocess copy, both error mappings, `materialPageLabel`, `mayHaveMorePages`; existing helpers untouched); `frontend/features/materials/api/useMaterials.ts` (`MATERIAL_PAGES_QUERY_LIMIT`, `materialPagesOptions`, `useMaterialPages` via `useQueries`, `useProcessMaterial`; the list/status options and polling discipline untouched); `frontend/features/materials/flow.test.ts` (+14 tests); `frontend/components/courses/CourseMaterials.tsx` (the terminal-row action area: the disclosure + the control; `canManage` threaded from the page's existing `canUpload`); `frontend/stories/CourseMaterials.stories.tsx` (6 new stories + the two 4.3-era pins updated in lockstep — see §5); `frontend/stories/CourseDetail.stories.tsx` (the no-placeholder pin's `/extracted text/i` entry retired — §5); `frontend/app/(app)/courses/[id]/page.tsx` (documentation-only: the stale "future hub slots" comment now records that extracted text is a delivered capability, realized inside the materials region; zero behavior change); the execution ledger.
- Deleted: none. No backend, contract, CI, infra, dependency, or DOCX change.

## 3. Contract cross-check (implementation-time, as required)

The three operations were re-read from `docs/openapi.json` at `a1a5415` and cross-checked against `backend/app/api/materials.py` before coding (the brief's rule: never guess a schema from an endpoint name). Confirmed exactly as the investigation reported: the page-list's `material_id`/`pages` shape with `page_number` ≥ 1 and possibly-empty `text`; `limit` 1–500 (default 100) / `offset` ≥ 0 with "a shorter page than limit means the last page"; the 202's nullable `job_id` + `status`; the two 409 detail strings ("Material is already queued or processing (current status: …)" from the in-flight branch, "Manual retry budget exhausted (N of 3 manual retries consumed)" from the exhausted branch — `MATERIAL_RETRY_LIMIT = 3`); instructor + ownership on process, ownership on pages; `limit_writes` on process. **No discrepancy was found** between the investigation's findings, the brief's stated expectations, and the tracked contract at the execution commit — nothing needed a workaround, and nothing was invented.

## 4. The single-page endpoint

`GET /v1/materials/{id}/pages/{page_number}` remains unconsumed: the list endpoint with its contract pagination serves the viewer's every state honestly (the investigation's own recommendation — "the list endpoint alone is sufficient at demo scale"), and the implementation adds no speculative second fetch path. The operation stays in the contract's unconsumed set for a future per-page lazy surface if the owner ever wants one.

## 5. Story pin updates (lockstep, documented)

Two 4.3-era Storybook pins encoded facts that Batch 4.5's authorized scope deliberately changes; both were updated in lockstep with the reasons recorded in the story code:

1. `CourseMaterials` "Owner — all four statuses": the pin `queryByRole("button", { name: /retry|reprocess/i })` → null asserted the ABSENCE of any reprocess affordance (4.3's frozen scope predates the Week 9 landing — its note §7.1 documented the control as a pending owner decision). The pin now asserts the control's PRESENCE on both terminal rows for the owner, its absence on queued/processing rows, and the viewer disclosure on the ready row only. The read-only story pins the non-owner's view: no upload, no reprocess — the disclosure remains (the viewer is not a management action).
2. `CourseDetail` "Owner — hub with materials": the no-placeholder forbidden-text list included `/extracted text/i` — a placeholder-region guard for what was then a RESERVED hub slot. The capability is now delivered (as a row-level disclosure inside the materials region, not a hub slot), so the entry is retired with an inline note; every remaining entry (coming soon, knowledge base, chat, enroll, citation) still guards genuinely-future slots.

No E2E spec, accessible name, or E2E-pinned string changed anywhere (verified: the e2e specs reference no materials-surface strings; `playwright test --list` still collects 10 tests in 4 files).

## 6. The hermetic story mechanism (new, documented here for the owner)

The three request-level story states (viewer loading, viewer read failed, reprocess in flight) cannot be expressed by a seeded cache — they need a query or mutation sitting in a pending or failed state. The stories introduce a scoped guard that is hermetic in EVERY environment: keycloak-js 26 with an object config performs NO network I/O during `init({ onLoad: "check-sso" })` — it proceeds directly to the PKCE code-challenge digest and then the login redirect — so the guard intercepts exactly `crypto.subtle.digest`: "hang" holds the token path pending (the real clicked mutation stays in flight); "fail" rejects the init so the token resolves to null and `apiFetch` fails with its honest 401 before any request is issued. No navigation, no network, and no dependence on what is running on the Keycloak or API ports — the stories behave identically in CI and on the owner's machine. The guard restores itself on unmount and releases a hung init, leaving the module state clean for the next story (the file's stories are ordered so the single hang-mode story is the file's first keycloak touch — the adapter's singleton initializes exactly once per iframe; each story is also correct in isolation). The retry-budget-exhausted 409 story renders the presentational control with the contract's own documented detail string — the full mapping path for both 409 classes is unit-tested.

## 7. Accessibility

Both surfaces ride the established primitives and semantics: the disclosure is a real button with `aria-expanded`/`aria-controls` and a stable accessible name; the viewer region is labelled by its h4 heading under the row's h3; page labels are plain text (no heading spam at 100 pages); the extracted text carries `dir="auto"` (per page) inside the document's direction; the reprocess control's acceptance is a `role="status"` polite live region and its errors a `role="alert"`, matching the upload form's grammar; every new story runs under the standing axe fail-on-error configuration (104/104 include the six new stories); the full direction × theme rendered sweep (§8) covers both new surfaces in both themes and both directions with overflow assertions.

## 8. Rendered verification (real Chromium, the 4.4 audit mechanism)

`scripts/b45_rendered_checks.js` (workspace, outside the repository) over the static Storybook build: **138/138 PASS** —

- **A. Story sweep — 120 loads, zero horizontal overflow**: the 9 CourseMaterials stories (all 4.5 states, plays executing on load so the OPEN viewer and the in-flight states are measured) plus the 3 CourseDetail stories whose pin changed, at 360/768/1280 CSS px × ltr/rtl × light/dark (360 and 1280 get all four combos; 768 gets the two diagonal ones), with the dark class applied and verified per load the way next-themes does it.
- **B. 4.5-specific pins — 18 checks**: every rendered page-block text carries `dir="auto"`; the Arabic page resolves `rtl` and the English page resolves `ltr` under BOTH document directions (plaintext isolation — each page reads in its own direction, while the blocks' `text-start` alignment follows the document); the viewer's `border-s` start-edge rule sits on the inline-start side under both directions; the empty-page copy renders; the sweep's two levers (direction global + dark class) verified before trusting the matrix. Evidence captures: `b45-evidence/viewer-open-{ltr-light, rtl-light, rtl-dark}.png`.

## 9. Validation matrix (commands from `frontend/`, Node 24.21.0 / npm 11.19.0)

| Check | Command | Result |
| --- | --- | --- |
| Type checking | `npm run typecheck` | **PASS** |
| Linting | `npm run lint` | **PASS** (0 errors, 0 warnings) |
| Unit tests | `npm test` | **PASS 107/107** (93 pre-existing + 14 new; the new cases: the Week-9 response shapes incl. empty text/empty list/rejections, the pages key branch, page labels, the honest pagination predicate, the pinned copy, both documented 409 classes, the 429/403/404/401 mappings for both new flows) |
| Storybook + axe | `npm run test:storybook` | **PASS 104/104 across 26 files** (98 pre-existing + 6 new stories; the axe fail-on-error config intact) |
| Production build | `npm run build` (with the documented `.env.example` build env) | **PASS — 11 routes** (the same route set as the 4.4 baseline) |
| Playwright collection | `npx playwright test --list` | **10 tests in 4 files** — unchanged, as the investigation recorded |
| Rendered audit | `node scripts/b45_rendered_checks.js` (workspace) | **PASS 138/138** (§8) |

**NOT RUN (the standing limitation of every prior batch):** E2E execution — no Docker/Keycloak/backend/credentials in this environment. The E2E trio remains the owner's machine; nothing in this batch touched the specs or their pins.

## 10. Manual owner-stack walkthrough (OUTSTANDING — the exact steps)

The same prerequisite as 4.3's materials walkthrough (the local stack: `setup-dev.sh` → API → `run-worker-dev.sh`). Steps, extended from the investigation note §6.11 by this batch's surfaces:

1. Open a course with a ready English PDF material.
2. Open its extracted-text viewer (the "Extracted text" disclosure) and inspect multiple pages.
3. Repeat with an Arabic PDF and verify `dir="auto"` and the RTL presentation (the rendered audit verified the mechanism; the walkthrough confirms it against real extracted Arabic).
4. Inspect an empty page or an empty page-list state if one is available (a purely graphical page, or a material processed before Week 9).
5. Open a failed material (the scanned-PDF quota case if available) and invoke reprocessing.
6. Verify the accepted response ("Processing is queued — its status appears in the list.") and observe the existing status flow returning through pending/processing/ready where the worker succeeds.
7. Verify that a ready material can also be reprocessed (the same control on the ready row).
8. Verify that the control is absent for ineligible roles or material states (a non-owner instructor account if available; queued/processing rows).
9. If practical, verify the backend's exhausted-retry 409 (three manual retries) and the rate-limit 429 (rapid requests) — both surface the backend's own detail verbatim.
10. Spot-check light/dark themes and LTR/RTL layouts on both surfaces (the in-app direction toggle).

## 11. Deviations, decisions, and observations

1. **No deviations from the authorized scope.** The two surfaces, their files, and their behavior match the investigation's §6 spec and the authorization brief, including both owner decisions exercised here (D1: the batch as proposed; D3: both terminal states; D2 followed the implementation as recommended — owner + instructor, not admin).
2. **The roadmap DOCX is untouched** (the owner's explicit deferral — investigation decision D4 resolved as "defer"). The Week-9 coverage-matrix rows and hub-slot fulfilment notes therefore remain to be reconciled in a later documentation pass; the ledger records this deferral.
3. **`useQueries`** (the TanStack core multi-query API, same library, same `queryOptions` convention) serves the viewer's independent page-list windows — the only architecture addition, chosen so "Load more pages" never refetches earlier windows and prefix invalidation stays exact. No second API boundary, no alternate query architecture, no new state-management abstraction, no new dependency.
4. **The CourseDetail "no materials in this course yet" and all other existing pins, copy, upload flow, dedup honesty, polling discipline, list-as-rendering-source rule, `notFound()` semantics, and every existing Zod schema are byte-preserved** (the two lockstep pin updates in §5 are the only story changes; the schema/key/flow additions are purely additive).
5. **Observation (no action)**: `GET /v1/materials/{id}/pages/{page_number}` remains the contract's only unconsumed operation (16 total; 15 consumed after this batch) — reserved for a possible future per-page lazy surface, not needed by this viewer.
6. **Observation (no action)**: the failed-state copy still names the plausible cause class only; with the reprocess control now present, the copy's final sentence ("The file remains stored with the course.") remains accurate — a retry does not re-upload.

## 12. Resulting state

Batch 4.5 is **EXECUTED** at the working-clone level: the implementation, its tests, its stories, and its documentation are complete and locally verified per §9; the patch is generated and validated (see the ledger's patch record). The Week 9 frontend assignment (the extracted-text viewer) is implemented to the extent supported by actual completed work; the runtime demonstration of a completed retry and of non-empty real pages remains the owner's walkthrough (§10). Per the lifecycle rules: no commit, no push, no merge, no rebase — the repository's Git state is unchanged except the uncommitted batch files listed in §2. **The next batch in the roadmap sequence is 5.1 (Test suite alignment); per the lifecycle rules it starts only on Seyam's explicit authorization.**
