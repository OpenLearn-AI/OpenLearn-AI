# OpenLearn-AI — Batch 4.4 Batch Note: Profile Redesign, Global States, RTL/LTR Direction Control & Responsive Audit

**Status: EXECUTED (2026-10-26)** — delivered as one patch from `3d1da92` ("4.3-course-detail-hub-materials-plus-4.2-corrections", the owner's applied Batch 4.3 commit). Scope per roadmap v2.0 §14 Table 26 with the owner's recorded reassignment: first-login onboarding was already moved to Batch 4.1 and is NOT rebuilt here (regression-checked only, §7); the batch adds the owner-requested **user-facing RTL/LTR direction control** to the sidebar. This note documents what EXISTS; the ledger entry carries the same facts.

## 1. What was delivered (Batch 4.4 scope, roadmap v2.0 §14 Table 26 + the owner's direction-toggle request)

- **Profile page redesign** (`app/(app)/profile/page.tsx` + `components/profile/ProfileForm.tsx`): the last pre-redesign surface joins the Swiss Editorial Grid — the gradient hero banner, its "Account Settings" pill, the rounded-2xl card grid, and the filler "Need Assistance?" panel are retired. See §4 for the composition and the contract preservation.
- **Global states**: `app/not-found.tsx` (root 404), `app/(app)/error.tsx`, and `app/(auth)/error.tsx` restyled onto the redesign's state language; **`app/(app)/loading.tsx` created** (the roadmap's Table 26 files-affected list includes it; it completes the pair with the existing `(auth)` boundary so BOTH route groups have an honest instant loading state instead of Next.js's blank default).
- **RTL/LTR direction control** (the owner's explicit request): a real, user-facing direction toggle in the sidebar's account region (desktop expanded + collapsed rail) and the mobile drawer's account region, with persistence across navigation and reload. See §3.
- **Systematic responsive/RTL audit**: every story in the suite (98) swept across viewport × direction × theme with an overflow assertion, plus real-app checks on the production build. See §6.

## 2. Files affected (exactly these paths)

- **Created (7)**: `frontend/lib/direction.ts` (the direction module); `frontend/components/ui/direction-toggle.tsx`; `frontend/app/(app)/loading.tsx`; `frontend/features/profile/completeness.ts` (the shared derivation — extracted, see §4); stories `frontend/stories/{DirectionToggle,Profile,GlobalStates}.stories.tsx`.
- **Modified**: `app/layout.tsx` (the pre-paint direction script); `app/(app)/profile/page.tsx` (redesign); `components/profile/ProfileForm.tsx` (presentation/associations pass); `app/not-found.tsx`, `app/(app)/error.tsx`, `app/(auth)/error.tsx` (state restyle); `components/shell/AppSidebar.tsx` + `components/shell/MobileNav.tsx` (direction control in the account region); `app/(app)/dashboard/page.tsx` (imports the shared completeness derivation — rendered output unchanged); `stories/AppShell.stories.tsx` (lockstep pins for the new control); the execution ledger.
- **Deleted**: none. No backend, contract, dependency, or configuration file was touched.

## 3. The RTL/LTR direction control — mechanism, placement, state

**Mechanism** (`lib/direction.ts`, ~30 lines of logic): the `<html dir>` attribute IS the single source of truth; `applyDirection`/`toggleDirection` set the attribute, persist to `localStorage` under `openlearn-direction` (best-effort — a storage failure never blocks the flip), and dispatch a custom event; `useDirection` reads the live attribute through `useSyncExternalStore` with a static server snapshot (`"ltr"`), which is React's sanctioned pattern for adopting a client-only value with no hydration mismatch. Cross-tab consistency via the `storage` event. This deliberately mirrors the repository's existing next-themes pattern (attribute on `<html>` + localStorage + a pre-paint script) — no new dependency, no new state framework, no i18n infrastructure, no language switching (the UI stays English; the profile's `preferred_language` field is untouched data, never a direction trigger).

**No flash of wrong direction**: a tiny inline script in the root layout (the next-themes precedent; `suppressHydrationWarning` is already on `<html>` for the theme class) applies a stored preference during HTML parsing, BEFORE first paint. Verified in the rendered audit: `rtl` at `domcontentloaded`, still `rtl` after hydration and after reload, zero hydration-mismatch console errors (§6/C2).

**Placement**: immediately adjacent to the theme control in the established account-actions area — desktop expanded (grouped with `ThemeToggle` at the row's inline start, logout at the inline end), desktop collapsed rail (icon-only with a reinforcing tooltip, exactly like the theme control), and inside the mobile drawer's account region (the A9-established position). Same 36px visual grammar as `ThemeToggle` (border, radius, hover, focus ring); a deliberately distinct icon (`ArrowLeftRight` — bidirectional arrows, NOT a "languages" glyph, since this is layout direction, not language) that is horizontally symmetric so it never needs mirroring.

**State, accessibly**: `aria-pressed` + the stable accessible name "Right-to-left layout" (the WAI-ARIA toggle-button pattern) — screen readers announce the current state ("pressed"/"not pressed"), never the icon alone; the icon is `aria-hidden`. Keyboard-operable with the project's standard visible focus ring.

**What it actually changes**: the document's real `dir` attribute — verified by rendered geometry, not just the attribute: after activation the desktop sidebar (the inline-start element) occupies the viewport's RIGHT half, and the mobile drawer anchors to the RTL start edge (§6/B1/B3). Both themes and both directions verified; route behavior, authentication, and the profile flow are untouched (the E2E trio collects 10/10; runtime blocked per §8).

## 4. The profile page — how it follows the current visual direction

- **Masthead** (the courses-hub grammar): the display-scale `h1` "Profile" at the same container-query clamp, the person's real identity as a quiet mono metadata line (`useUserName`'s name with `dir="auto"`, the email with `dir="ltr"` so a Latin address never bidi-shuffles in RTL), one hairline. The email renders only when it differs from the display name — the hook's email fallback must not print the address twice (a real defect the story tests caught during development; pinned as an exactly-once assertion).
- **Content band** (the 12-column asymmetric grid): the form region (8) and a completeness aside (4) with the family's vertical hairline at ≥48rem content width, stacked with horizontal rules below; every region `min-w-0` (the A5 zoom/viewport resilience).
- **The aside is real data, not filler**: the dashboard's six-tick datum row and the "N of 6 fields left" measure, on the derivation now shared by BOTH surfaces (`features/profile/completeness.ts` — one definition of the metric, so the dashboard and the profile page can never drift; the dashboard's rendered output is unchanged). It re-renders with the invalidated query after every save.
- **The form joins the CourseForm grammar** (the 4.3 precedent): programmatic error association (`aria-describedby` → the Field's `role="alert"` error / hint ids) on all six fields; honest helper text only where justified (university and VARK marked optional with examples; the minutes hint states the schema's actual 1–1440 range); the lone filled Save button is the page's single primary action (the courses-page hierarchy rule).
- **Create-vs-edit distinction**: the pinned heading pair ("Create Your Profile" / "Personal Information") plus distinct supporting copy and the pinned submit labels ("Create Profile" / "Save Changes") — the underlying form behavior is byte-preserved: the Zod schema and `safeParse` loop, the full-replacement upsert payload (every field, always — `PUT /v1/users/me` semantics), the mutation + `profileKeys.all` invalidation, the ApiError status mapping, the `role="status"`/`role="alert"` surfaces, the F4 remount key (`key={profile?.id ?? "new"}`), and all six field labels.

## 5. The global states — presentation only, contracts preserved

- **`not-found.tsx`**: the code as a large decorative tabular numeral (aria-hidden — the h1 "Page not found" carries the meaning, the dashboard's numeral-as-datum grammar), honest copy, one filled "Back to home" action (`/`, the existing target). The 404→`notFound()` semantics elsewhere are untouched.
- **`(app)/error.tsx`**: the compact semantic indicator (the ErrorState kit's marker — never color alone), quiet heading, honest copy, "Try again" as the single primary action. The `error` + `reset` contract, the `console.error` observability hook, and the never-expose-internals rule are unchanged; no escape-hatch links were invented because the `(app)` shell (sidebar navigation) keeps rendering around this boundary.
- **`(auth)/error.tsx`**: the same contract and copy inside the auth shell's card language — now the exact card treatment of the sign-in/register entries (`max-w-md rounded-2xl border bg-card p-8 shadow-xs`; the inconsistent `shadow-xl` retired).
- **`(app)/loading.tsx`** (NEW): the shared async-state kit (the only sanctioned loading presentation) centered in the content column; the shell stays interactive around it (the App Router instant-loading contract); guards, gate, and route behavior untouched — the file only renders between navigations.

## 6. The responsive/RTL audit — actual coverage (all real Chromium)

**Route inventory** (verified from the tree): `/`, `/login`, `/register`, `/onboarding`, `/dashboard`, `/courses`, `/courses/new`, `/courses/[id]`, `/courses/[id]/edit`, `/profile` — ten page routes (the nine-route inventory predates 4.1's `/onboarding`). `/health` is the BACKEND liveness probe (tier D, no UI) — not a frontend route; nothing to render or audit there. The authenticated `(app)` pages are covered through the story compositions (below) because the runtime stack (Keycloak/backend) is unavailable here.

**A — Story sweep (981/981 PASS)**: every story in the static Storybook build (98 stories across 26 files — the full suite's compositions: pages, shell states, the wizard, the kit, the new Profile/GlobalStates/DirectionToggle stories) loaded at **360, 768, and 1280 CSS px** (mobile, the `md` breakpoint where the sidebar rail appears, desktop) across the full direction × theme matrix (ltr/rtl × light/dark at 360 and 1280; ltr/light + rtl/dark at 768) — 980 loads, each asserting **no horizontal overflow** (`scrollWidth ≤ clientWidth + 1` on the scrolling element and body). Direction drove the existing Storybook direction toolbar global; dark applied the same `.dark` class next-themes sets (verified on every dark load — the backgrounds URL global cannot express the addon's object shape, a harness detail recorded here for reproducibility). **Zero overflow defects found** — the suite's logical-properties discipline held everywhere.

**B — Direction toggle as real interaction (all PASS)**: expanded desktop shell (click → `dir=rtl`, `aria-pressed=true`, storage persisted, **sidebar geometry flipped to the right half**, second click returns to LTR); collapsed rail (control reachable and functional); mobile drawer (menu opened by its real trigger, control functional INSIDE the drawer, drawer anchors to the RTL start edge, drawer stays open).

**C — Real app on the production build (`next start`, all PASS)**: the landing renders on-origin with the favicon regression checks (`/logo.svg` 200, `/logo.png` 404); a stored RTL preference is `rtl` at `domcontentloaded` (pre-paint, no LTR flash), survives hydration and reload, zero hydration-mismatch errors; the 404 page renders with its pinned heading, honors the stored RTL preference, and has no overflow at desktop or mobile (a fresh context confirms the LTR default); `/login`, `/register`, `/onboarding` serve HTTP 200; a light-theme + RTL visitor gets both preferences composed pre-paint. Evidence captures under `b44-evidence/` (shell RTL, drawer RTL, 404 RTL, landing RTL, light+RTL).

**Environment note (recorded honestly)**: with no Keycloak reachable, the app's unchanged auth configuration (keycloak-js `check-sso` without `silentCheckSsoRedirectUri`) top-navigates every route to the identity provider's auth endpoint shortly after mount. The audit therefore served the Keycloak origin a 302-back-`error=login_required` response — exactly what a real Keycloak returns for `prompt=none` without a session — so the app settles on-origin exactly as it does in production for an anonymous visitor. Nothing in the app was modified for this; the behavior itself is pre-existing (and irrelevant whenever Keycloak is up, as in every deployed environment).

## 7. Onboarding — pre-existing, regression-checked only

First-login onboarding was REASSIGNED to Batch 4.1 (owner decision Q5, 2026-10-23) and delivered there; this batch did not rebuild, redesign, or re-touch it. Regression evidence within this batch's runs: the gate-state unit tests pass (inside the 93/93), the eight wizard stories pass inside the storybook suite (axe enforced), and the three onboarding E2E specs collect (10/10 total). Runtime E2E remains the owner's stack (§8).

## 8. Tests actually executed (all commands from `frontend/`)

| Command | Result |
| --- | --- |
| `npm run typecheck` | **PASS** |
| `npm run lint` | **PASS** (0 errors, 0 warnings) |
| `npm run test` | **PASS 93/93** (the batch adds no unit-testable pure module — the direction logic is exercised for real in the browser runs below) |
| `npm run test:storybook` | **PASS 98/98 across 26 files** (axe fail-on-error intact; +9 stories: DirectionToggle ×3 with the real round-trip/in-RTL interaction contracts, Profile ×4 incl. both E2E-pinned modes and the client-side validation path, GlobalStates ×5 incl. the reset contract) |
| `npm run build` (with the documented `NEXT_PUBLIC_*` values from `.env.example`) | **PASS — 11 routes** |
| `npx playwright test --list` | **10/10 collected** across 4 specs |
| Rendered audit (`scripts/b44_rendered_checks.js`, real Chromium) | **1001/1001 PASS** — the §6 matrix |

**NOT RUN (the standing environment limitation, same as every prior batch):** E2E execution (`npm run test:e2e`) — requires the Keycloak/backend stack and credentials (no Docker daemon here); the profile round-trip against the real API is therefore owner-machine work. The profile form's save/error paths are covered at the component level by the hermetic stories (validation, both mode contracts, the `role` surfaces), and the direction control's real-user interaction is covered by the rendered audit — but neither substitutes for the end-to-end proof.

## 9. Owner decisions requested / observations

1. **Observation (no action taken)**: the check-sso redirect behavior in §6 — every route top-navigates to Keycloak when it is unreachable (offline development only). Auth is a must-not-change surface; recorded for awareness, not acted on.
2. **Observation**: `next start` prints a warning under `output: "standalone"` (use `node .next/standalone/server.js`) but served all 11 routes correctly for the audit; the Dockerfile already uses the standalone path, so this affects only local `next start` runs.
3. **No new dependencies were added**, and the direction mechanism introduces no storage framework — one localStorage key, one custom event, the next-themes pattern.
