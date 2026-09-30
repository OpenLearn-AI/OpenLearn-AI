# OpenLearn AI — Frontend

The web client for **OpenLearn AI**, an adaptive learning platform built around an Arabic-first content model with English LTR as the production baseline and Arabic / RTL prepared as a first-class supported direction. The frontend is a Next.js App Router application that talks to a FastAPI backend, authenticates against Keycloak via OIDC (Authorization Code + PKCE), and ships its own shared UI primitive layer on top of Tailwind 4 + Base UI.

This README is the contributor onboarding path. It does **not** duplicate the architecture decision study (`docs/OpenLearn-AI_Frontend_Architecture_Modernization.docx`) or the local setup guide (`scripts/LOCAL_SETUP.md`); it points at them and documents the conventions you need to follow.

---

## Prerequisites

The canonical, always-up-to-date list lives in [`scripts/LOCAL_SETUP.md`](../scripts/LOCAL_SETUP.md). The essentials for the frontend alone:

| Tool | Required version | Notes |
|---|---|---|
| Node.js | >= 20 (CI targets Node 20) | No `engines` pin in `package.json` yet — Node 20 is the practical floor |
| npm | bundled with Node | `npm ci` is used in CI and the setup script |
| Docker | 24+ recommended | Only needed for the local backend + Keycloak stack — not for frontend-only work |

The frontend itself has no Python, PostgreSQL, or Keycloak dependency of its own. Those exist for the backend and the local dev stack (`scripts/setup-dev.sh` brings them up for you).

---

## Local setup

**Start here.** From the repository root:

```bash
bash scripts/setup-dev.sh
```

The script is branch-independent, idempotent, and never mutates your git state. It:

1. Verifies prerequisites (Git, Docker, Compose v2, Node >= 20, Python 3.12, npm, curl).
2. Creates `frontend/.env.local`, `backend/.env`, and the root `.env.local` **only if they don't already exist** — your local changes are always preserved.
3. Starts PostgreSQL (with pgvector) and Keycloak in Docker, runs Alembic migrations, and bootstraps a local `testuser` with the `student` role.
4. Runs `npm ci` in `frontend/` when `node_modules` is missing or stale.

After the script finishes, the Docker stack is running but the dev servers are not. Start them in two terminals:

```bash
# Terminal 1 — backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

Open <http://localhost:3000>. Log in at `/login` as `testuser` with the password the script generated (stored in the root `.env.local`).

**Troubleshooting, port conflicts, OS-specific notes, and the full verification checklist** all live in [`scripts/LOCAL_SETUP.md`](../scripts/LOCAL_SETUP.md). Reach for that document, not this README, when setup misbehaves.

---

## Environment variables

All client-side variables are centralized in [`lib/config.ts`](lib/config.ts) (validated with Zod at module load) and consumed via the `config` export. Do **not** read `process.env.NEXT_PUBLIC_*` from anywhere else — go through `config`.

The defaults below are for local development. See `frontend/.env.example` for the canonical commented template.

### Required for local development

| Variable | Local dev default | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL. Must be reachable from the browser. |
| `NEXT_PUBLIC_KEYCLOAK_URL` | `http://localhost:8080` | Keycloak server URL. |
| `NEXT_PUBLIC_KEYCLOAK_REALM` | `openlearn` | Keycloak realm name. |
| `NEXT_PUBLIC_KEYCLOAK_CLIENT_ID` | `openlearn-frontend` | Keycloak public client ID (OIDC Authorization Code + PKCE). |

### Optional / observability

| Variable | Default | Purpose |
|---|---|---|
| `NEXT_PUBLIC_SENTRY_DSN` | _(empty)_ | Client-side Sentry DSN. When empty, the Sentry SDK is a no-op — local dev works without a Sentry project configured. |
| `NEXT_PUBLIC_SENTRY_ENVIRONMENT` | `development` | Client-side Sentry environment label. Allowed: `development` \| `staging` \| `production`. Defaults to `development` when unset or invalid. |

### Server-side only (not in `lib/config.ts`)

These are read at runtime by `sentry.server.config.ts` (matching the backend's `SENTRY_DSN` convention in `backend/app/observability.py`). They are injected by the staging Docker Compose (`infra/docker-compose.staging.yml`) and would be injected similarly in production.

| Variable | Purpose |
|---|---|
| `SENTRY_DSN` | Server-side Sentry DSN. |
| `SENTRY_ENVIRONMENT` | Server-side Sentry environment label. **Must match `NEXT_PUBLIC_SENTRY_ENVIRONMENT`** in deployment so client and server events share the same environment label. |

### Build-time only (not committed)

These are read by the Sentry SDK's `withSentryConfig` at build time. They are **never** hardcoded in `next.config.ts` — the SDK reads them from `process.env`. The actual authenticated source-map upload only happens in an environment where these are set (CI build with the secret configured, or a deploy-time build).

| Variable | Purpose |
|---|---|
| `SENTRY_AUTH_TOKEN` | Sentry auth token for source-map upload. **Pod D external dependency** — not in this repository. |
| `SENTRY_ORG` | Sentry organization slug. |
| `SENTRY_PROJECT` | Sentry project slug. |

No credentials are committed. No production secrets are touched by frontend code.

### Staging / production

The staging frontend is `https://openlearn-web-staging.duckdns.org`; the staging API is `https://openlearn-api-staging.duckdns.org`. Deployment wiring lives in `.github/workflows/deploy-staging.yml` (image build args + runtime env injection). `NEXT_PUBLIC_*` values are inlined into the client bundle at build time — they must be present when `next build` runs (see `frontend/Dockerfile`).

---

## Commands

All commands run from `frontend/`:

| Command | What it verifies |
|---|---|
| `npm run dev` | Start the Next.js dev server on <http://localhost:3000>. |
| `npm run lint` | ESLint (Next.js + Storybook plugins). Fast-failing syntax/style check. |
| `npm run typecheck` | `tsc --noEmit` under strict mode. Catches type errors without emitting. |
| `npm run test` | Vitest unit tests (`--project unit`). Covers `lib/api.ts` (`apiFetch`, `ApiError`) + `features/courses/` (keys, query options). |
| `npm run test:storybook` | Vitest Storybook tests (`--project storybook`) in a headless Chromium via `@vitest/browser-playwright`. Includes **axe a11y enforcement at `test: 'error'`** — any axe violation fails this job. |
| `npm run build` | Next.js production build. Produces `.next/standalone` (consumed by the Dockerfile runner stage). `withSentryConfig` runs here. |
| `npm run test:e2e` | Playwright E2E suite (`frontend/e2e/*.spec.ts`). Requires backend + Keycloak + test credentials — see "Testing & quality gate" below. |
| `npm run storybook` | Start Storybook dev server on port 6006 (component development, not CI). |
| `npm run build-storybook` | Build the static Storybook bundle (used by Chromatic, not by CI today). |

---

## Architecture & conventions

This section answers the question every new contributor eventually asks: **"where do I put this code?"**

### Directory layout

```
frontend/
├── app/                     # Next.js App Router routes (convention files only)
│   ├── (app)/               # Authenticated application shell — wrapped by AuthGuard + Navbar
│   │   ├── dashboard/       # /dashboard
│   │   ├── courses/          # /courses, /courses/new, /courses/[id], /courses/[id]/edit
│   │   └── profile/          # /profile
│   ├── (auth)/               # Public auth routes — no Navbar, no AuthGuard
│   │   ├── login/            # /login (single OIDC redirect button)
│   │   └── register/         # /register (single OIDC redirect button)
│   ├── layout.tsx            # Root layout — ThemeProvider → AppQueryProvider → AuthProvider
│   ├── globals.css           # Tailwind 4 + design tokens
│   ├── not-found.tsx         # Root 404 page
│   └── ...
├── components/              # Visual components (no business logic in ui/)
│   ├── ui/                  # Shared primitives (Button, Input, Textarea, Select, Field, Label, Badge, Card, theme-toggle)
│   ├── auth/                # Auth-specific (LoginForm, LogoutButton, UserInfo)
│   ├── courses/             # Course-specific (CourseForm, DeleteCourseButton)
│   ├── profile/             # Profile-specific (ProfileForm)
│   ├── state/               # Shared state components (LoadingBlock, ErrorState, EmptyState)
│   ├── AuthGuard.tsx         # Route protection — redirects unauthenticated users to /login?redirectedFrom=...
│   ├── Navbar.tsx            # Top nav — only renders inside (app) routes
│   ├── CourseCard.tsx         # Card for a course in list/dashboard views
│   └── UserName.tsx           # Hook-based display name (email fallback)
├── features/                # Feature modules — domain logic, NOT visual components
│   ├── auth/                # /auth/me schema + useMe hook
│   ├── courses/             # /v1/courses schemas, query keys, hooks (useCourse, useCourses, mutations)
│   └── profile/             # /v1/users/me schema, keys, hooks (useProfile, useProfileMutation)
├── lib/                     # Cross-cutting infrastructure
│   ├── api.ts               # apiFetch + ApiError — THE ONLY place fetch() is called
│   ├── config.ts            # Zod-validated NEXT_PUBLIC_* config — THE ONLY place process.env.NEXT_PUBLIC_* is read
│   ├── keycloak.ts          # Keycloak singleton (lazy init, PKCE S256, token refresh)
│   ├── auth-context.tsx     # AuthProvider — exposes { isAuthenticated, isLoading }
│   └── query-provider.tsx   # TanStack Query provider (staleTime 30s, retry 1)
├── stories/                 # Storybook stories (*.stories.tsx) — one per shared UI primitive + CourseCard
├── e2e/                     # Playwright E2E specs (login, courses-crud, profile-roundtrip)
├── .storybook/              # Storybook config (main.ts, preview.tsx)
├── public/                  # Static assets served at / (only logo.png is in use)
├── next.config.ts           # Next.js config wrapped by withSentryConfig
├── sentry.client.config.ts  # Client-side Sentry.init (reads config.sentryEnvironment)
├── sentry.server.config.ts  # Server-side Sentry.init (reads SENTRY_DSN + SENTRY_ENVIRONMENT)
├── instrumentation.ts       # Next.js instrumentation hook — loads sentry.server.config in the Node runtime
├── playwright.config.ts     # Playwright E2E config (chromium-only, configurable baseURL)
├── vitest.config.ts         # Vitest config (unit + storybook projects)
└── package.json
```

### API boundary

**All HTTP calls go through `lib/api.ts`.** The `apiFetch` helper:

- Prepends `config.apiUrl` to every path.
- Attaches a `Bearer` token from `getAccessToken()` (Keycloak token refresh with 30s skew).
- Validates the response against an optional Zod schema.
- Throws `ApiError` (with `status`, `message`, `body`) on non-2xx responses — never a raw `Error`.

Do **not** call `fetch()` directly from a page, component, or feature module. The grep check `grep -rn "fetch(" frontend/app frontend/components frontend/features` (excluding `lib/api.ts`) must return zero matches.

### Configuration boundary

**All `NEXT_PUBLIC_*` reads go through `lib/config.ts`.** The `config` export is Zod-validated at module load — a missing or malformed required variable fails fast with a readable error at startup, not at first use.

Do **not** read `process.env.NEXT_PUBLIC_*` from anywhere else. The Phase 1 grep check `grep -rn "process.env.NEXT_PUBLIC" frontend/lib/keycloak.ts frontend/sentry.client.config.ts` must return zero matches — both consume `config` from `@/lib/config`.

Server-only env vars (`SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT`) are read directly where needed — they are never inlined into the client bundle.

### Feature boundaries

A feature module under `features/<domain>/` owns:

- `schemas.ts` — Zod schemas for the domain's API request/response shapes.
- `keys.ts` — TanStack Query key factory (hierarchical: `["courses"]` → `["courses", "list"]` / `["courses", "detail", id]`).
- `api/` — Hooks built on `queryOptions` + `useMutation`, all calling `apiFetch` with the domain's schemas.
- _(No visual components here — those live in `components/<domain>/`.)_

To add a new feature domain (e.g. `materials`), copy the `features/courses/` shape: `schemas.ts` → `keys.ts` → `api/useMaterials.ts` → `api/useMaterialMutations.ts`. This is the **understandability exit test** — a new contributor should be able to add a feature domain by imitation, without reading framework code.

### Authentication

Authentication is owned by `lib/keycloak.ts` + `lib/auth-context.tsx` + `components/AuthGuard.tsx`. Do **not** introduce another auth mechanism. The flow:

1. `AuthProvider` lazily initializes Keycloak with `onLoad: "check-sso"` + PKCE S256.
2. `useAuth()` exposes `{ isAuthenticated, isLoading }` — nothing else.
3. `AuthGuard` (wrapping every `(app)` route) redirects unauthenticated users to `/login?redirectedFrom=<currentPath>`.
4. `LoginForm` calls `keycloak.login({ redirectUri })` — a full OIDC redirect to the Keycloak-hosted login page (we don't host the username/password form).
5. `LogoutButton` calls `queryClient.clear()` then `keycloak.logout({ redirectUri: "/login" })`.

### Provider order

The root layout (`app/layout.tsx`) renders providers in this exact order — do **not** reorder:

```
ThemeProvider
  → AppQueryProvider
    → AuthProvider
      → children
        └── (app)/layout.tsx wraps with:
              AuthGuard → Navbar → children
```

`ThemeProvider` is outermost so theme class toggles don't cause hydration flashes in the query/auth layers. `AuthGuard` and `Navbar` live in `app/(app)/layout.tsx`, not the root, so public routes (`/login`, `/register`) render without the authenticated shell.

### Query / data fetching

Use TanStack Query via the established `queryOptions` + key-factory pattern. Defaults (set in `lib/query-provider.tsx`): `staleTime: 30_000`, `retry: 1`, `refetchOnWindowFocus: false`. Do **not** create ad-hoc caching, global state libraries (Redux/Zustand/Jotai), or custom data-fetching layers.

### Validation

Use Zod schemas (in `features/<domain>/schemas.ts`) + the `Field` wrapper (`components/ui/field.tsx`) for form fields. The `Field` component associates a `<Label htmlFor>` with the control and renders an error `<p role="alert" id="${htmlFor}-error">` when present. Do **not** introduce React Hook Form — manual forms + Zod + `Field` remain pleasant at the current scale (two small forms).

### RTL / Arabic

The baseline is English + LTR. Arabic + RTL is **prepared, not converted** — use logical CSS utilities (`ms-`, `me-`, `ps-`, `pe-`, `text-start`, `text-end`) rather than physical directional utilities (`ml-`, `mr-`, `text-left`, `text-right`). The root `<html>` is `dir="ltr"` by design; Arabic content activates the Noto Sans Arabic font fallback (loaded in `app/layout.tsx`). Do **not** introduce a full i18n framework — its trigger stays in the Deferred Backlog until real Arabic UI copy exists.

---

## Storybook

Storybook is **development and verification infrastructure**, not a frozen visual design. Per the D13 clarification:

- Shared UI component development
- Component + state verification (loading / error / empty)
- Dark-mode verification
- RTL verification (direction toolbar in the preview)
- Accessibility verification — **axe runs at `test: 'error'`**, so any violation fails `npm run test:storybook` in CI
- Visual-regression verification where applicable (Chromatic is wired but not yet enforced as a required check)

Stories live in `frontend/stories/*.stories.tsx` — one per shared UI primitive (`Button`, `Input`, `Textarea`, `Select`, `Field`, `Label`, `Badge`, `Card`) plus the shared state components (`LoadingBlock`, `ErrorState`, `EmptyState`) and `CourseCard`. Stories do **not** establish or freeze the final visual design — the later UI/UX redesign (D9 clarification) proceeds on top of this infrastructure and may change visual identity, colors, typography, spacing, and component appearance freely.

Run `npm run storybook` for local component development on port 6006.

---

## Testing & quality gate

CI (`.github/workflows/ci.yml`, `frontend` job) runs on every PR to `main` / `staging`:

1. `npm run lint`
2. `npm run typecheck`
3. `npx playwright install --with-deps chromium` — installs the browser binary for the Storybook browser-driven project
4. `npm run test` — 22 unit tests (3 files)
5. `npm run test:storybook` — 42 Storybook tests (12 story files), including axe a11y enforcement at `test: 'error'`
6. `npm run build` — Next.js production build with `withSentryConfig`

### Accessibility baseline (Phase 5)

- The Storybook axe addon is configured at `test: 'error'` in `.storybook/preview.tsx`.
- Any axe violation in any `*.stories.tsx` file fails the Storybook test job, which fails the PR.
- Forms use semantic `<label htmlFor>` associations via the `Field` wrapper.
- Error messages use `role="alert"`; loading states use `role="status"` + `aria-live="polite"`.
- RTL direction is verifiable via the Storybook toolbar.

### E2E smoke suite

Three Playwright E2E specs live in `frontend/e2e/`:

1. `login.spec.ts` — login → dashboard (real Keycloak OIDC redirect).
2. `courses-crud.spec.ts` — create → read → update → delete a course through the UI.
3. `profile-roundtrip.spec.ts` — profile create → reload → update → reload, verifying persistence.

**Status:** the E2E workflow (`.github/workflows/e2e.yml`) runs on `workflow_dispatch` **only** — it is **not** a required PR check. Per the Phase 6 promotion discipline, E2E is promoted to a required CI check only after three consecutive green `workflow_dispatch` runs. Promotion status:

```
Run 1/3: pending
Run 2/3: pending
Run 3/3: pending
Required CI: NO
```

To run E2E locally you need: a running backend at `NEXT_PUBLIC_API_URL`, a running Keycloak at `NEXT_PUBLIC_KEYCLOAK_URL`, the realm + client configured, and test credentials in `E2E_USERNAME` / `E2E_PASSWORD`. See `.github/workflows/e2e.yml` for the full environment contract.

---

## Sentry status

Sentry is configured for environment-aware observability (Phase 6 Batch 3, D14):

- `next.config.ts` wraps the Next.js config with `withSentryConfig` (imported from the non-deprecated `@sentry/nextjs/config` subpath). Source-map upload is delegated to the SDK, which reads `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, and `SENTRY_PROJECT` from the environment at build time — they are never hardcoded, so they cannot leak into the build artifact. `deleteSourcemapsAfterUpload: true` keeps source maps out of the deployed bundle. Local dev builds gracefully skip upload when `SENTRY_AUTH_TOKEN` is absent.
- `sentry.client.config.ts` reads `config.sentryEnvironment` (from `NEXT_PUBLIC_SENTRY_ENVIRONMENT` via `lib/config.ts`) and applies environment-aware sampling: development 1.0 / staging 0.5 / production 0.1.
- `sentry.server.config.ts` reads `SENTRY_ENVIRONMENT` at runtime (matching the existing `SENTRY_DSN` pattern) and applies the same sampling tiers.

**Runtime verification status:**

- Repository configuration: **PASS** (build succeeds, `withSentryConfig` runs `runAfterProductionCompile`).
- Source-map upload: **configured** but **not runtime-verified** — the actual authenticated upload requires the Pod D `SENTRY_AUTH_TOKEN` secret, which is an external dependency not present in this repository.
- Runtime Sentry event verification: **NOT RUN** — requires a real Sentry project + deployed environment. Seyam must perform this in staging/production once the Pod D secret is configured.

No Sentry credentials are committed. The `SENTRY_AUTH_TOKEN` dependency is documented in the roadmap §13 Deferred Backlog.

---

## Common workflow

**Add a new feature domain** (e.g. `materials`):

1. `features/materials/schemas.ts` — Zod schemas for the API shapes.
2. `features/materials/keys.ts` — `materialsKeys` factory (`["materials"]` → `["materials", "list"]` / `["materials", "detail", id]`).
3. `features/materials/api/useMaterials.ts` — `useMaterials()` hook built on `queryOptions` + `materialsKeys.lists()`.
4. `features/materials/api/useMaterial.ts` — `useMaterial(id)` hook.
5. `features/materials/api/useMaterialMutations.ts` — `useCreateMaterial`, `useUpdateMaterial`, `useDeleteMaterial` (invalidate `materialsKeys.lists()` / `materialsKeys.detail(id)`).
6. `components/materials/MaterialForm.tsx`, `components/materials/MaterialList.tsx`, etc.
7. `app/(app)/materials/page.tsx`, `app/(app)/materials/new/page.tsx`, `app/(app)/materials/[id]/page.tsx`, `app/(app)/materials/[id]/edit/page.tsx`.
8. If you add a new shared UI primitive: `components/ui/<name>.tsx` + `stories/<Name>.stories.tsx`.

**Run the quality gate before pushing:**

```bash
npm run typecheck && npm run lint && npm run test && npm run test:storybook && npm run build
```

If you touched E2E specs and have the runtime available:

```bash
npm run test:e2e
```

---

## Further reading

- [`scripts/LOCAL_SETUP.md`](../scripts/LOCAL_SETUP.md) — full local setup guide (troubleshooting, OS notes, verification checklist).
- [`docs/OpenLearn-AI_Frontend_Modernization_Execution_Roadmap_v1.1-closure.md`](docs/OpenLearn-AI_Frontend_Modernization_Execution_Roadmap_v1.1-closure.md) — the living execution roadmap with phase-by-phase closure records, the Global Definition of Done, and the Deferred Backlog.
- `docs/OpenLearn-AI_Frontend_Architecture_Modernization.docx` — the companion architecture decision study (D1–D19). Reach for this when you need the reasoning behind a convention, not just the rule.
