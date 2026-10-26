# OpenLearn-AI — Batch 4.3 Batch Note: Course-Detail Hub & Materials Surface

**Status: EXECUTED (2026-10-26)** — delivered together with the nine outstanding Batch 4.2 owner corrections (A1–A9, recorded in the ledger's "Batch 4.2 follow-up corrections" entry) in one patch from `8c316dd` ("4.2-swiss-grid-dashboard-courses", the owner's applied Batch 4.2 commit). This note documents the Batch 4.3 implementation THAT EXISTS; the ledger entry carries the same facts.

## 1. What was delivered (Batch 4.3 scope, roadmap v2.0 §14 Table 25)

- **Course detail as the content hub** (`app/(app)/courses/[id]/page.tsx`, redesigned): the Swiss Editorial Grid composition — a quiet "All courses" back link, the display-scale title with the course's real metadata (mono ISO created date + the ownership line), the role-aware management actions (Edit Course / Delete Course) at the masthead's inline end, then the 12-column band with the two BUILT regions: Description (4) beside Materials (8), vertical hairline at ≥48rem content width, stacked with horizontal rules below. The 404→`notFound()` semantics, the loading/error states, and every pinned accessible name the courses-crud E2E depends on ("Edit Course", "Delete Course", the "Description" h2, the h1 title) are preserved.
- **Materials surface** (NEW `components/courses/CourseMaterials.tsx` + the `features/materials/` module): the complete scheduled materials workflow against the EXISTING contract — the three-step upload flow (presigned URL → direct-to-storage POST → registration), the 202/job_id handling, the per-course materials list, per-material status polling with terminal shutdown, and the honest status presentation. Details in §3–§5.
- **Shared course form** (`components/courses/CourseForm.tsx` + both form pages, presentation pass): the established behavior is untouched (Zod schema, `safeParse` loop, mutation orchestration, `router.push("/courses")` post-save navigation, F3 edit remount key, duplicate-submit protection); the pass adds programmatic error association (`aria-describedby` → the Field's error/hint ids), a hint on the description field, a quiet Cancel link beside submit, and the pages join the courses family (back link + editorial masthead). `components/ui/field.tsx` gained the `id` on its hint paragraph (the error paragraph already had one).
- **Delete confirmation** (`components/courses/DeleteCourseButton.tsx`): VERIFIED on the existing Batch 3.2 alert-dialog primitive — `role="alertdialog"` labelled by its title, the destructive action clearly identified, accessible Cancel/confirm, pointer-dismissal disabled while the deletion is in flight (double-submit protection), inline `role="alert"` error mapping, cache invalidation and the post-delete redirect unchanged. The only change is the trigger's size joining the masthead action row (the pinned accessible name "Delete Course" is size-independent).
- **Batch 4.2 corrections A1–A9** (see the ledger entry): sidebar order, dashboard interactivity/separation, the greeting composition, redundant-copy removals, zoom/viewport resilience, search discoverability, the logo-only mobile header with the toggle moved into the drawer, and the retired `/logo.png` references (MobileNav ×2, the favicon).

## 2. Files affected (Batch 4.3 + corrections, exactly these paths)

- **Created (5)**: `frontend/components/courses/CourseMaterials.tsx`; `frontend/features/materials/{schemas.ts,keys.ts,flow.ts,api/useMaterials.ts}`; plus stories `frontend/stories/{CourseDetail.stories.tsx,CourseMaterials.stories.tsx}` and the test `frontend/features/materials/flow.test.ts`.
- **Modified**: `app/(app)/courses/[id]/page.tsx` (hub rewrite); `app/(app)/courses/[id]/edit/page.tsx` + `app/(app)/courses/new/page.tsx` (page frames); `components/courses/CourseForm.tsx` (a11y associations + presentation); `components/courses/CoursesIndex.tsx` (A7 search treatment); `components/CourseCard.tsx` (A8 title link + resilience); `components/courses/OpenHubLink.tsx` (the shared `entryTitleLinkClass`); `components/courses/DeleteCourseButton.tsx` (trigger size only); `components/shell/{nav-config.ts,MobileNav.tsx,AppShell.tsx}` (A1/A9); `components/ui/field.tsx` (hint id); `app/layout.tsx` (favicon → `/logo.svg`); `app/(app)/dashboard/page.tsx` (A2–A5); `app/(app)/courses/page.tsx` (A6); `features/auth/user-identity.ts` (+`composeWelcomeGreeting`/`presentFirstName`); `features/auth/useUserName.test.ts`; `.storybook/next-navigation-stub.ts` (story-settable params — Storybook bundle only); `e2e/{login.spec.ts,onboarding.spec.ts}` (greeting pin lockstep); the AppShell/CourseCard/Courses/CoursesIndex/Dashboard stories (lockstep pins); the execution ledger.
- **Deleted**: none.

## 3. The API contract actually consumed (docs/openapi.json, verified against the backend)

| Operation | Request | Response | Authorization |
| --- | --- | --- | --- |
| `POST /v1/courses/{id}/materials/upload-url` | `{filename, title}` (both 1–255) | `{course_id, title, s3_key, upload_url, upload_fields, max_size_bytes, expires_in}` | bearer + instructor + course ownership; 429 write-rate-limited |
| *(browser → storage)* `POST upload_url` | `multipart/form-data`: every `upload_fields` entry, then the file LAST under `file` | non-2xx = failure | the presigned POST policy IS the authorization (no bearer; SigV4 signs host/path so the browser's Content-Type is accepted; `content-length-range` [1, max]) |
| `POST /v1/courses/{id}/materials` | `{s3_key, title}` | **202** `{material_id, status, job_id\|null}` | bearer + instructor + ownership; 404 no object / 413 too large / 409 changed-or-registered / 422 namespace / 429 |
| `GET /v1/courses/{id}/materials` | — | `MaterialResponse[]` `{id, course_id, s3_key, title, status, uploaded_by, created_at}` | bearer + course ownership |
| `GET /v1/materials/{id}/status` | — | `{material_id, status}` | bearer + course ownership |

**Critical shape correction this batch enforces:** the upload is a **presigned POST (`multipart/form-data`, the signed fields first and the file LAST)** — the roadmap's §10 prose and the batch prompt's "PUT to the returned URL" both predate the contract's final form; `UploadUrlResponse`'s own description documents the POST flow, and `backend/app/services/storage.py` builds it with `generate_presigned_post` (SigV4 forced, `content-length-range` [1, `max_upload_size_bytes`=10 MiB], `expires_in`=900s). The frontend implements exactly that (`buildUploadFormData`, unit-tested), and no PUT is ever issued.

**202 semantics (honest acceptance vs completion):** the registration response is presented as acceptance only — the UI's status line says the material "is registered; processing is queued", and the material's LIVE state comes from the list + the status poll. `job_id` is logged once for correlation (`console.info` with material_id/job_id/status — never the signed URL, never the s3_key, never tokens) and is NEVER queried (the status endpoint keys on material_id). A `null` job_id means Week 9 content dedup returned the EXISTING material — presented as "This file is already in the course — showing its current state", never as a fresh registration.

## 4. Status transitions and how they are observed

The contract's complete status set is the four-value literal `pending | processing | ready | failed` (roadmap Table 9):

- **pending → processing → ready | failed** (the Celery pipeline; the frontend observes, never drives).
- Observation: the list query renders the snapshot; each row whose snapshot is non-terminal owns a `GET /v1/materials/{id}/status` poll (5s interval) that **stops itself the moment a terminal state is observed**; a polled change patches the shared list cache so the list stays the single rendering source. Unmounting the row/course removes the query observer and the interval with it; React Query's per-key dedupe prevents overlapping polls. Unrecoverable poll errors (401/403/404) stop the interval; transient network errors keep the cadence so a blip cannot freeze the status.
- Presentation (never color alone — text always): Queued / Processing / Ready / Failed, with a small geometric indicator; **no progress percentages, phase names, or ETAs exist anywhere** (the API exposes none). The failed row carries the honest cause-class copy (OCR/quota/storage/ingestion) without claiming the exact cause, and **no retry/reprocess control is rendered**.

## 5. Limitations of the current contract (documented, not worked around)

1. **The Week 9 reprocess endpoint has landed in `docs/openapi.json` but is NOT in Batch 4.3's scope.** `POST /v1/materials/{id}/process` (owner-only, `MATERIAL_RETRY_LIMIT` manual retries, 409 while queued/processing or when the budget is exhausted) is a real, shape-stable contract — but the roadmap's Batch 4.3 table (§14 Table 25) freezes this batch's materials surface without it ("no retry/reprocess control while no endpoint exists" was written before Week 9 landed; §11 tracks the capability as buildable "the moment the endpoint stabilizes"). **Owner decision required**: authorize a follow-up batch to add the reprocess control (the UI hook point is the failed/ready row's action area).
2. **The extracted-text viewer remains a reserved hub slot**: `GET /v1/materials/{id}/pages[/{page_number}]` (Week 9) exists in the contract, but the roadmap §11 classifies the viewer Blocked/future (assigned when the document-content contract stabilizes); nothing is rendered for it.
3. No upload progress percentage, no cancel-in-flight, no delete-material, no MIME allow-list exists in the contract — none is invented (the client-side size guard uses the `max_size_bytes` the upload-url response itself returns).
4. Students cannot reach the hub at all today (the owner-scoped `GET /v1/courses/{id}`); the read-only presentation is therefore pinned at the component layer (the Viewer stories), not against a real student session.

## 6. The future content-hub slots (documentation only — nothing rendered)

Recorded in ADR-0010's Section 9 table (Batch 3.1) and restated here as the hub's deliberate composition, per the roadmap's reservation rule ("documentation, never rendered UI"):

| Region | Content | Built in |
| --- | --- | --- |
| Course header + actions | Title, description, metadata; edit/delete for the owning instructor | **4.3 (this batch — redesign of existing)** |
| Materials region | Materials list; upload affordance (owning instructor only); status presentation with honest failed-state copy | **4.3 (this batch — new, scheduled scope)** |
| Hub slot: extracted text | Document content viewer per page | Reserved — plan W9; contract landed, awaiting authorization (see §5.2) |
| Hub slot: search | Retrieval search + results with chunk→document links | Reserved — plan W10 |
| Hub slot: chunks/source | Chunk inspection panel | Reserved — plan W11 |
| Hub slot: citations | Ranked citations (W13), citation chips (W14) | Reserved — contracts pending |
| Hub slot: AI assistant | Chat on sessions API + streaming | Reserved — plan W15–16, Gate 1 |
| Hub slot: enrollment/learning entry | Student enrollment + learning entry points | Reserved — plan W17 |

The test the roadmap sets is met: if any slot's contract disappeared tomorrow, nothing rendered in the product would change. No placeholder panels, no coming-soon copy, no disabled buttons, no fake AI reasoning — pinned as ABSENCES in the CourseDetail story plays.

## 7. Owner decisions requested

1. **Reprocess control** (see §5.1): authorize a follow-up batch against the landed `POST /v1/materials/{id}/process` (409 semantics + the retry budget would need honest presentation: "N of M manual retries consumed").
2. **Extracted-text viewer** (§5.2): authorize against the landed pages contract, or keep reserved until the plan's W9 verification.
3. Batch 4.2 open items remain: Q-A/Q-B (numerals/ISO dates), Q-D (tick row), Q-J (colophon markup), and whether the Roles colophon should stay on the dashboard at all.

## 8. Tests actually executed (all commands from `frontend/`; Node 24.21.0 / npm 11.19.0)

| Check | Result |
| --- | --- |
| `npm run typecheck` (tsc --noEmit) | **PASS** |
| `npm run lint` (eslint; storybook-static moved out of the tree first — the recorded pre-existing lint-scope behavior) | **PASS** |
| `npm test` (vitest unit) | **PASS — 93/93** (83 prior + 10 new material-flow/keys cases; the greeting suite grew from 20 to 26 including the A3 composition) |
| `npm run test:storybook` (rendered chromium via addon-vitest, axe fail-on-error) | **PASS — 86/86 across 23 story files** (80 prior + 6 new: CourseDetail ×3, CourseMaterials ×3; the AppShell/Dashboard/Courses/CourseCard/CoursesIndex plays updated in lockstep for A1–A9) |
| `npm run build` (`.env.example` sourced) | **PASS — 11 routes** (incl. the dynamic `/courses/[id]` and `/courses/[id]/edit`) |
| Rendered verification (`/home/z/my-project/scripts/b43_rendered_checks.js`, real Chromium over the static Storybook build; browser zoom approximated by CSS-pixel viewport width — Ctrl +/- zoom changes exactly that measure) | **PASS — 108/108** — A1 sidebar order; A3 greeting; A4 kicker/spatial-copy removal + heading structure; A2/A8 title links; A5/A8/B1/B4 zero horizontal overflow at 360–2000px with band stacking below the 48rem content reflow; RTL; light/dark token flip; A6/A7 subtitle/search; A9 mobile header 56px with logo+hamburger only, toggle-in-drawer, drawer order, `/logo.svg` serving, `/logo.png` 404; B1 hub composition + viewer read-only; B4 statuses/failed-copy/no-percentages |
| `npx playwright test --list` | **PASS — 10 tests in 4 files collected** |
| E2E execution (`test:e2e`) | **NOT RUN — 10/10 skipped cleanly** (no `E2E_USERNAME`/`E2E_PASSWORD`, no Docker/Keycloak/backend stack in this environment — the same recorded limitation as every prior batch). The genuinely-changed pins (the greeting in login.spec + onboarding.spec ×2, documented in-file) will exercise on the owner's stack; all other courses-crud pins (Courses & Learning Hub, + Create New Course, Create/Edit Course headings, Description h2, Edit Course link, Delete Course button, the alertdialog + "Yes, delete it") are UNCHANGED and therefore already covered by the existing spec |
| The materials walkthrough (upload → pending → processing → ready \| failed) against the real pipeline | **BLOCKED in this environment** (no local AI profile, no staging stack, no Docker daemon). The workflow's code paths are covered by: the pure-flow unit tests (form-data construction, terminal predicate, error mapping), the hermetic component stories (all four statuses + upload form + read-only), and the 108-check rendered suite. The owner's stack must run the documented walkthrough: `bash scripts/setup-dev.sh` → start the API → `bash scripts/run-worker-dev.sh` → upload a PDF through the real UI as the instructor → observe queued → processing → ready (and a scanned-PDF quota case for failed). Mocked coverage is labeled as such and claims no integration pass |
