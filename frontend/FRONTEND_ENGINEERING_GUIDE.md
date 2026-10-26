# OpenLearn AI — Frontend Engineering Guide

The current, source-verified guide to working on the frontend. It describes the application **as it exists today** (the
[UI redesign batches](#h-further-reading) are historical background, not
prerequisites). The contributor-level [README](./README.md) covers local
setup and the environment-variable tables; this guide covers the codebase
itself.

## Contents

- [A. Start here](#a-start-here)
- [B. Project structure](#b-project-structure)
- [C. Architecture and request flow](#c-architecture-and-request-flow)
- [D. UI, styling, and design tokens](#d-ui-styling-and-design-tokens)
- [E. Testing](#e-testing)
- [F. Common engineering tasks](#f-common-engineering-tasks)
- [G. Important invariants and pitfalls](#g-important-invariants-and-pitfalls)
- [H. Further reading](#h-further-reading)

---

## A. Start here

**What it is.** The web client of an adaptive learning platform: a public
landing page, Keycloak-hosted authentication (OIDC Authorization Code + PKCE),
a first-login onboarding wizard, and an authenticated app shell with a
dashboard, a course CRUD surface (including instructor-only material
upload/processing), and a profile editor. It is a Client Components frontend —
the backend (FastAPI) talks to it only over the versioned REST API.

**Verified stack** (from `package.json`):

| Layer | Technology |
|---|---|
| Framework | Next.js 16.3.1 (App Router), React 19.2.8, TypeScript strict |
| Styling | Tailwind CSS 4 (token layer in `app/globals.css`), Base UI 1.x (`@base-ui/react`) primitives in `components/ui/` |
| Data | TanStack Query 5, Zod 4, `keycloak-js` 26.2.4 |
| Observability | `@sentry/nextjs` (client + server config below the app boundary) |
| Icons / theme | lucide-react, next-themes (`class` attribute, default `dark`) |
| Component workbench | Storybook 10 (`@storybook/nextjs-vite` + a11y/vitest/chromatic addons) |
| Tests | Vitest (two projects: `unit`, `storybook`), Playwright (Chromium, E2E) |

**Commands** (all from `frontend/`; verified against `package.json`):

| Command | Runs | Needs backend? |
|---|---|---|
| `npm run dev` | Next.js dev server on <http://localhost:3000> (no stack: pages render, all API calls error honestly) | optional |
| `npm run lint` | ESLint (Next.js + Storybook configs) | no |
| `npm run typecheck` | `tsc --noEmit` (strict) | no |
| `npm run test` | Vitest **unit** project (node env, 107 tests in 9 files) | no |
| `npm run test:storybook` | Vitest **storybook** project (headless Chromium, 104 tests in 26 files, axe enforced at `error`) | no; needs Playwright Chromium (`npx playwright install --with-deps chromium`) |
| `npm run build` | Production build (11 routes) — `withSentryConfig` runs here | no |
| `npm run test:e2e` | Playwright suite (11 tests in 4 files) | **yes** — real Keycloak + backend + credentials |
| `npm run storybook` | Storybook dev server on port 6006 (component work, manual rendering checks) | no |
| `npm run build-storybook` | Static Storybook build (what the Chromatic workflow builds) | no |

Stack bring-up (`bash scripts/setup-dev.sh` from the repository root), the
env-variable tables, and troubleshooting live in
[`docs/development/LOCAL_SETUP.md`](../docs/development/LOCAL_SETUP.md).

---

## B. Project structure

```
frontend/
├── app/                            # App Router: route tree, layouts, URLs
│   ├── layout.tsx                  # Root layout — fonts, dir init script, provider chain
│   ├── page.tsx                    # /        — public landing (LandingPage)
│   ├── not-found.tsx               # Root 404
│   ├── (app)/                      # Authenticated group — AuthGuard → OnboardingGate → AppShell
│   │   ├── layout.tsx              # The three-layer guard chain (one job per layer)
│   │   ├── dashboard/page.tsx      # /dashboard
│   │   ├── profile/page.tsx        # /profile
│   │   ├── courses/page.tsx        # /courses (list/hub)
│   │   ├── courses/new/page.tsx    # /courses/new
│   │   ├── courses/[id]/page.tsx   # /courses/{id} — detail + materials hub
│   │   ├── courses/[id]/edit/page.tsx
│   │   ├── error.tsx, loading.tsx  # Group-level global states
│   │   └── ...
│   ├── (auth)/                     # /login, /register — OIDC bridge pages, no shell
│   └── onboarding/                 # /onboarding — OUTSIDE the (app) guard chain (no loop)
├── components/
│   ├── ui/                         # Shared primitives on Base UI (button, input, select,
│   │                               #   field, label, textarea, dialog, card, tooltip,
│   │                               #   choice-tile-group, theme-toggle, direction-toggle)
│   ├── shell/                      # AppShell (sidebar + mobile nav), AppSidebar, MobileNav,
│   │                               #   nav-config.ts — THE shared navigation source of truth
│   ├── state/                      # LoadingBlock, ErrorState, EmptyState (async-state kit)
│   ├── brand/                      # BrandMark, ProductIdentityVisual (landing SVG)
│   ├── AuthGuard.tsx               # Authentication-only redirect layer
│   ├── onboarding/                 # OnboardingGate, ProfileSetupWizard, journey visual
│   ├── courses/                    # CourseForm, CoursesIndex, CourseMaterials,
│   │                               #   MaterialTextViewer, DeleteCourseButton, OpenHubLink
│   ├── profile/                    # ProfileForm
│   └── landing/                    # LandingPage, Reveal
├── features/                       # Domain logic only — no visual components
│   ├── auth/                       # schemas, keys (authKeys.me), useMe, user-identity
│   │                               #   (composeWelcomeGreeting, composeUserDisplayName),
│   │                               #   oidc-attempt, redirect, useUserName
│   ├── courses/                    # schemas, keys (courseKeys), useCourses/useCourse, mutations
│   ├── materials/                  # schemas, keys (materialKeys incl. pages/status),
│   │                               #   useMaterials, flow.ts (status/flow helpers)
│   ├── profile/                    # schemas (incl. profileSchema), keys (profileKeys.current),
│   │                               #   useProfile/useProfileMutation, completeness
│   └── onboarding/                 # gate-state.ts (pure state machine, unit-tested)
├── lib/                            # Cross-cutting infrastructure
│   ├── api.ts                      # apiFetch + ApiError — the API call boundary (see §C)
│   ├── config.ts                   # Zod-validated NEXT_PUBLIC_* — THE only process.env read
│   ├── keycloak.ts                 # Keycloak singleton (PKCE S256, refresh, refresh-error hook)
│   ├── auth-context.tsx            # AuthProvider / useAuth
│   ├── query-provider.tsx          # QueryClient defaults + session-recovery wiring
│   ├── session-recovery.ts         # Forced-logout recovery → /login?redirectedFrom=…
│   ├── direction.ts                # <html dir> source of truth (RTL/LTR), localStorage-backed
│   └── utils.ts                    # cn() (clsx + tailwind-merge)
├── stories/                        # 26 Storybook files — real component fixtures, a11y-enforced
├── e2e/                            # Playwright specs (login, courses-crud, onboarding,
│                                   #   profile-roundtrip) + helpers.ts (one shared login helper)
├── .storybook/                     # main.ts (addons, inline env, navigation stub), preview.tsx
├── styles/shadcn.css               # Vendored shadcn stylesheet (CLI removed — W5)
├── next.config.ts                  # wrapped by withSentryConfig
├── sentry.client.config.ts, sentry.server.config.ts, instrumentation.ts
├── playwright.config.ts            # Chromium-only, baseURL = PLAYWRIGHT_BASE_URL
├── vitest.config.ts                # two projects: unit (node) + storybook (browser)
└── package.json
```

**Where to start** for each change type: see the [lookup table](#f-common-engineering-tasks).

---

## C. Architecture and request flow

### Routing and the two guard chains

`app/(app)/layout.tsx` composes exactly three layers, each with one job
(keep it that way):

1. **`AuthGuard`** (`components/AuthGuard.tsx`) — authentication only.
   Unauthenticated users go to `/login?redirectedFrom=<path>`.
2. **`OnboardingGate`** (`components/onboarding/OnboardingGate.tsx`) — profile
   existence only. Routes users whose `GET /v1/users/me` returns the
   backend's confirmed **404** to `/onboarding`; `/profile` is exempt; any
   other error renders an error state and **never** redirects. `/onboarding`
   sits outside `(app)` (its own layout), so no redirect loop is possible.
   The state machine is the pure, unit-tested `features/onboarding/gate-state.ts`.
3. **`AppShell`** — navigation chrome only (`AppSidebar` desktop /
   `MobileNav` mobile drawer).

`/login` and `/register` auto-bridge to Keycloak: `OidcEntryBridge`
(`components/auth/`) guarantees the OIDC redirect initiates once per tab on
arrival, with `OidcEntryButton` as the manual retry affordance. Sessions use
`onLoad: "check-sso"` — a now-authenticated (`check-sso`) user goes to
`/dashboard`.

### Provider hierarchy (root layout, `app/layout.tsx`)

```
<html dir="ltr" suppressHydrationWarning>
  <script> pre-paint direction restore (lib/direction.ts mechanism)
  ThemeProvider (next-themes, attribute="class", defaultTheme="dark")
    AppQueryProvider (staleTime 30s, retry 1, refetchOnWindowFocus false,
                      refresh-error → session recovery)
      AuthProvider (checks-sso, exposes { isAuthenticated, isLoading })
        children — public routes stop here
        (app)/layout.tsx: AuthGuard → OnboardingGate → AppShell
```

Do not reorder — `ThemeProvider` is outermost so theme/direction class and
attribute deltas never re-mount the data/auth layers (both use
`suppressHydrationWarning` policies).

### API boundary

Every HTTP call goes through **`apiFetch`** in `lib/api.ts`:

- prefixes `config.apiUrl` (`NEXT_PUBLIC_API_URL`),
- attaches a Bearer token from the Keycloak singleton
  (`getInitializedKeycloak()` — token-aware with a 30 s refresh skew),
- parses successful JSON bodies against a per-call **Zod schema**,
- throws **`ApiError { status, message, body }`** (descriptive message
  surfaced to users) on non-2xx — never a raw `Error`.

The `fetch(` census over `app/ components/ features/` shows exactly two
non-`apiFetch` shapes, both sanctioned: TanStack Query's `refetch()`
revalidations (querying the same cache again, not a new call site), and the
ONE direct `fetch` in `components/courses/CourseMaterials.tsx` — the
presigned direct-to-storage POST documented at the top of
`features/materials/flow.ts` (multipart form to `upload_url`, NO
`Authorization` header — the signed fields are the authorization). Any other
direct `fetch(` is a violation.

### Data fetching: query keys and mutations

Feature modules own a key factory plus `queryOptions`-built hooks
(`features/courses/api/useCourses.ts` pattern). Copy an existing factory when
adding a domain — do not invent a new shape:

| Factory | Shape |
|---|---|
| `authKeys` (`features/auth/keys.ts`) | `me()` |
| `courseKeys` (`features/courses/keys.ts`) | `all` / `lists()` / `details()` / `detail(id)` |
| `materialKeys` (`features/materials/keys.ts`) | `list(courseId)` / `status(id)` / `pages(id)` |
| `profileKeys` (`features/profile/keys.ts`) | `current()` |

Mutation conventions (`features/courses/api/useCourseMutations.ts`,
`useProfileMutation.ts`): only ONE active mutation per form (duplicate-submit
protection via an `isPending` gate), and the mutation invalidates the keys the
changed data affects — `lists()` after create/delete, `detail(id)` after edit,
`profileKeys.current()` after the profile save — using the server's own
response (never a client-side guess) when it seeds the cache
(e.g. the onboarding completion seeds `profileKeys.current()` before
navigating).

### Forms and validation

Zod schemas live per-domain in `features/<domain>/schemas.ts` —
`profileSchema` (and the wizard's per-step slices) in
`features/profile/schemas.ts`, course shape in `features/courses/schemas.ts`.
Forms are manual `<form>` + controlled inputs (no form framework):
`components/ui/field.tsx` associates `<label htmlFor>` with the control and
renders an error `<p role="alert" id={`${for}-error`}>`. Contract-backed
radio choices use `components/ui/choice-tile-group.tsx`
(`ChoiceTileGroup`: single-select tiles; a genuine multi-select exists for
the optional VARK field). The onboarding wizard
(`ProfileSetupWizard`) accumulates steps locally and performs a **single
full-replacement `PUT /v1/users/me`** at the end — never partial PUTs.

### Provider initialization order matters

`AuthProvider` mounts under the Query provider; `useAuth()` reads only
`{ isAuthenticated, isLoading }`. Keycloak initialization is
lazy/singleton in `lib/keycloak.ts`; nothing initializes Keycloak outside
that module — public routes (`/`, `/login`, `/register`, `/onboarding`) call
`useAuth()` only, so a signed-out visitor can never trigger an OIDC redirect.

---

## D. UI, styling, and design tokens

- **Tailwind 4** — the token layer lives in `app/globals.css`
  (`@theme`-era custom properties: `background`, `foreground`, `primary`,
  `sidebar-*`, `ring`, `warning`, `destructive`, …). The documented
  derivations and contrast rationale are in
  [`docs/design-tokens.md`](../docs/design-tokens.md) and
  [ADR-0010](../docs/adr/0010-frontend-design-direction-and-tokens.md).
  `styles/shadcn.css` is the vendored base stylesheet (there is no
  shadcn CLI dependency — W5).
- **Light/dark** — next-themes `class` strategy (default dark). The
  Storybook preview syncs the `.dark` class from its `backgrounds`
  toolbar, so both themes must be exercised per change
  (`npm run test:storybook` runs both implicitly only where stories set
  backgrounds — manual toolbar sweeps are the review instrument).
- **Direction** — `lib/direction.ts` is **layout direction only, not
  localization**: `<html dir>` is the source of truth, a pre-paint inline
  script restores the stored `openlearn-direction` preference,
  `DirectionToggle` (in the shell's account region and mobile drawer) writes
  it with `aria-pressed` state. The UI language is **English**; the
  direction control exists to exercise the design's RTL-readiness for real.
  Use logical utilities (`ms-`/`me-`, `ps-`/`pe-`, `text-start`,
  `border-e`, `start-*`) — never physical ones — and give icons that mean
  the opposite in RTL an explicit `rtl:rotate-180`. Arabic**is
  render-ready** (`Noto Sans Arabic` loaded in the root layout) but is **not
  a fully localized product**; full Arabic UI copy remains plan backlog.
- **Motion** — two small entrance animations on the landing page only
  (`ol-enter`), a one-shot onboarding SVG draw, and a global
  `prefers-reduced-motion` guard that completes all decorative motion
  instantly.
- **Responsive** — the shell flips at `md`: compact screens get the mobile
  top bar + drawer (`MobileNav`), `md+` gets the desktop sidebar
  (`AppSidebar` is `hidden md:flex`). 360×800 is the compact contract the
  E2E specs pin in-spec after each smoke flow.

---

## E. Testing

| Category | Command | Config / location | Role |
|---|---|---|---|
| Unit | `npm run test` | Vitest **unit** project (node env) — `lib/**/*.test.ts`, `features/**/*.test.ts` | apiFetch boundary, key factories, gates/flow logic (107 tests / 9 files) |
| Storybook interaction + a11y | `npm run test:storybook` | Vitest **storybook** project via `@storybook/addon-vitest`, Chromium via `@vitest/browser-playwright`; axe config `a11y.test: 'error'` in `.storybook/preview.tsx` (26 files / 104 tests) | Real component behavior, interaction plays, axes violations fail |
| Quick component view | `npm run storybook` | Storybook dev server | Manual per-story inspection incl. toolbar sweeps (theme, direction, bg) |
| E2E | `npm run test:e2e` | Playwright, Chromium-only, `playwright.config.ts`; specs in `frontend/e2e/` (11 tests / 4 files) | Real UI against a real Keycloak + backend stack |
| Production build | `npm run build` | `next.config.ts` + `withSentryConfig` | Route graph compiles to the shipped artifact (11 routes) |

**These are separate instrument classes - one command does NOT run them
all.** CI (`ci.yml`) currently runs lint → typecheck → browser install →
unit → Storybook → build per PR. The E2E workflow (`e2e.yml`) is triggered
by explicit runs (workflow-dispatch only); promotion to required status is
a team-lead decision per the roadmap (the three-green promotion evidence is
owner-recorded as of 2026-10-26).

**E2E prerequisites** (never skip-style-pretend these exist): backend and
Keycloak running (`scripts/setup-dev.sh` + the two dev servers), and the
credential pairs exported in the shell — `E2E_USERNAME`/`E2E_PASSWORD`
(student) and `E2E_INSTRUCTOR_USERNAME`/`E2E_INSTRUCTOR_PASSWORD`
(instructor; the CRUD flow skips itself with an explicit message when the
instructor pair is absent). Export paths live in
`docs/development/LOCAL_SETUP.md` and the `.github/workflows/e2e.yml`
environment contract. The specs drive the real Keycloak redirect chain and
the real UI states (no mocked auth or canned data).

> **Note on Storybook runs:** the suite uses real Playwright Chromium.
> Every story tree is hermetic — no Keycloak ever initializes (query caches
> pre-seeded with `staleTime: Infinity`), and the storybook bundle inlines
> the documented dev env values (via `.storybook/main.ts` `viteFinal`).
> Transient console noise (Base UI `nativeButton` notices, the negative-path
> Keycloak-init messages from the OIDC-error stories) is known and expected.

---

## F. Common engineering tasks

| Task | Start at |
|---|---|
| Add/modify a page or route | `app/(app)/<route>/page.tsx` — copy a sibling page; the (app) layout composes the guards; navigation destinations need `components/shell/nav-config.ts` (one shared list for desktop + mobile) |
| Change a shared UI primitive | `components/ui/<name>.tsx`; then update its `stories/<Name>.stories.tsx` (axe runs at `error`), and any stories of consumers |
| Add/modify an API call | Zod schema in `features/<domain>/schemas.ts` → hooks with `apiFetch` in `features/<domain>/api/` (query key invalidation per check-list rules) — never call `fetch` directly |
| Update form validation | The Zod schema is authoritative; wire the error text via the `Field` wrapper; E2E and the wizard step-state (gate-state tests) may pin exact messages |
| Change post-mutation cache invalidation | The slots at the BOTTOM of a hook or `useMutation` (`features/*/api/useCou*`) — the keys to invalidate are also documented in [§C. Query](#c-architecture-and-request-flow) |
| Modify theme tokens or RTL utilities | `app/globals.css` (tokens), then update in `docs/design-tokens.md` the derivations; for RTL classes verify `dir="rtl"` behavior through the Storybook direction toolbar or `lib/direction.ts`'s toggle |
| Add a Storybook story / E2E test | Storybook: `stories/*.stories.tsx` (wrap fixtures in a `QueryClientProvider`; use a pre-seeded client instead of calling `lib/config`'s hooks directly). E2E: `frontend/e2e/<topic>.spec.ts` with the helpers from `e2e/helpers.ts` — every login must be with real tenants/credentials, not mocked storage |
| Add a new UI domain or feature slice | Study `features/courses/` (a full example) and `components/courses/` (UI shell) as models; the backend contract lives in `docs/openapi.json` (CI-guarded) |

---

## G. Important invariants and pitfalls

1. **One job per guard layer.** `AuthGuard` = authentication,
   `OnboardingGate` = profile existence (404 only), `AppShell` = chrome. Do
   not merge responsibilities; a request failure inside the gate must render
   an error, not redirect.
2. **Boundaries are grep-checked, not honor-system.** No direct data call to
   the API outside `lib/api.ts` — the only other `fetch(` in the tree is the
   sanctioned presigned upload POST (see §C), and `refetch()` is TanStack
   revalidation, not a call site; no `process.env.NEXT_PUBLIC_*` outside
   `lib/config.ts` (server-only env (`SENTRY_*` at build/runtime) reads live
   where they are consumed but never reach the client bundle).
3. **No fabricated data/affordances.** Never invent an API endpoint, a
   material status outside the contract's closed four-value set
   (`["pending", "processing", "ready", "failed"]` in
   `features/materials/schemas.ts`), or role-gated UI the backend does not
   authorize: the shell renders the same navigation for every signed-in user
   (`components/shell/nav-config.ts` — the backend authorizes; the admin
   role has no enforced backend capability), the material-management
   affordances are owner/instructor-gated, and the E2E suite pins the
   student negative direction (a non-instructor owner's hub exposes no
   management affordances).
4. **Welcome-greeting contract.** `composeWelcomeGreeting`
   (`features/auth/user-identity.ts`) has two rendering variants
   (`Welcome back!` / `Welcome back, First!`) — the account always has a
   deterministic key shape; E2E pins the contract not exact copy so tests
   cannot pre-figure the backend claim shape.
5. **Global mutations own their cache.** After a mutation: invalidate the
   *actual* affected keys with the server's own response as the source. Do
   not pre-seed from client-side guesses and do not invent optimistic
   entries.
6. **Provider order is load-bearing.** Theme and Query wrapping keeps all
   consumers below them from re-mounting on direction/theme toggles.
7. **Storybook hermeticity.** Stories must not initialize Keycloak, hardcode
   live network expectations, or import from `app/` internals (only feature
   /component-level pieces). Use the inline env values from `.storybook/main.ts`.
8. **Deterministic browser tests.** Playwright-styled a11y runs in the
   Storybook suite may read computed styles from browsers whose ambient
   hover states are non-deterministic — anything a change pins via
   `getComputedStyle` should prefer **settled** values (`waitFor`) unless
   the change itself drives the state.

---

## H. Further reading

Maintained documentation (canonical paths):

- [`docs/development/LOCAL_SETUP.md`](../docs/development/LOCAL_SETUP.md) — local environment, credential exports, troubleshooting.
- [`docs/design-tokens.md`](../docs/design-tokens.md) — token derivations with composited contrast math.
- [`docs/openapi.json`](../docs/openapi.json) — the CI-guarded backend API contract (never code against an endpoint absent from it).
- [ADR-0010](../docs/adr/0010-frontend-design-direction-and-tokens.md) — design direction and its necessary sub-decisions (color tiers, focus ring, spacing).
- `README.md` [here in `frontend/`](./README.md) — quick install + environment-variable tables.

Testing configuration to reference directly when changing instruments:

- `.storybook/main.ts` / `.storybook/preview.tsx` — suite + a11y config and env injection.
- `vitest.config.ts` — unit vs Storybook project split.
- `playwright.config.ts` — E2E environment contract in its header comment.

Historical background only (not required reading; they narrate the
[redesign batches](../docs/tasks/Frontend%20UI%20redesign/OpenLearn-AI_Frontend_Execution_Progress.md)):

- [`docs/tasks/Frontend UI redesign/`](../docs/tasks/Frontend%20UI%20redesign/) — batch records, roadmap DOCX, investigation notes.
- [`docs/tasks/Frontend Modernization/`](../docs/tasks/Frontend%20Modernization/) — the pre-redesign
  modernization closure roadmap + the architecture decision study (DOCX):
  the "why" behind the feature-module conventions.
- [`docs/archive/`](../docs/archive/) — the archived v4 technical
  specification and other retired documents.
