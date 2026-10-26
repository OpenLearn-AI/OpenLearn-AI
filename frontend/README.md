# OpenLearn AI — Frontend

The web client for **OpenLearn AI**, an adaptive learning platform with an **English + LTR production baseline** and Arabic/RTL readiness shipped as a first-class direction control (the UI copy is English; the Arabic-capable font is render-ready and the RTL direction is a real, persisted toggle). It is a Next.js App Router application that talks to a FastAPI backend, authenticates against Keycloak via OIDC (Authorization Code + PKCE), and ships its own shared UI primitive layer on top of Tailwind 4 + Base UI.

## Two docs, two jobs

This README is the contributor onboarding path: prerequisites, local setup, environment variables, commands, the test gates, and the few grep-checkable boundaries. The codebase itself — structure, architecture and request flow, styling and tokens, testing instruments, task recipes, and the invariant list — is documented in the **[Frontend Engineering Guide](./FRONTEND_ENGINEERING_GUIDE.md)**. Read the guide first unless you are only setting up an environment.

---

## Prerequisites

The canonical, always-up-to-date list lives in [`docs/development/LOCAL_SETUP.md`](../docs/development/LOCAL_SETUP.md). The essentials for the frontend alone:

| Tool | Supported | Notes |
|---|---|---|
| Node.js | 20 or 22 (`engines: "^20 \|\| ^22"` in `package.json`) | Production images build on Node 22 (`frontend/Dockerfile`); CI runs Node 20 in `ci.yml`/`e2e.yml` and Node 22 in `storybook.yml` |
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
3. Starts PostgreSQL (with pgvector), Redis, MinIO, and Keycloak in Docker, runs Alembic migrations, and bootstraps the local dev accounts (the student `testuser` and the instructor account used by the E2E CRUD flow).
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

Open <http://localhost:3000>. Log in at `/login` (the page auto-initiates the OIDC redirect).

**Troubleshooting, port conflicts, OS-specific notes, the E2E credential exports, and the full verification checklist** all live in [`docs/development/LOCAL_SETUP.md`](../docs/development/LOCAL_SETUP.md). Reach for that document, not this README, when setup misbehaves.

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

All commands run from `frontend/`. The four test instruments are **separate classes — one command does not run them all**:

| Command | What it runs |
|---|---|
| `npm run dev` | Start the Next.js dev server on <http://localhost:3000>. |
| `npm run lint` | ESLint (Next.js + Storybook configs). Fast-failing syntax/style check. |
| `npm run typecheck` | `tsc --noEmit` under strict mode. Catches type errors without emitting. |
| `npm run test` | Vitest **unit** project (node env) — **107 tests / 9 files**: `lib/api.ts` (`apiFetch`, `ApiError`), the query-key factories, and pure feature logic (gate state, direction, session recovery, flows). |
| `npm run test:storybook` | Vitest **storybook** project in real headless Chromium (`@vitest/browser-playwright`) — **104 tests / 26 story files**, including **axe a11y enforcement at `test: 'error'`** (any violation fails the job). Needs `npx playwright install --with-deps chromium`. |
| `npm run build` | Next.js production build (**11 routes**). Produces `.next/standalone` (consumed by the Dockerfile runner stage). `withSentryConfig` runs here. |
| `npm run test:e2e` | Playwright E2E suite (**11 tests / 4 spec files**). Requires backend + Keycloak + credentials — see "Testing & quality gate" below. |
| `npm run storybook` | Start Storybook dev server on port 6006 (component development, manual toolbar sweeps; not CI). |
| `npm run build-storybook` | Build the static Storybook bundle (what the Chromatic workflow builds). |

---

## Architecture & conventions — where this README stops

The full structure map, request flow, and per-task recipes live in the [Frontend Engineering Guide](./FRONTEND_ENGINEERING_GUIDE.md) (§B, §C, §F). The boundaries that matter and are grep-checked:

- **API boundary** — every call to the backend goes through `apiFetch` + Zod schemas + `ApiError` from [`lib/api.ts`](lib/api.ts); TanStack query keys come from the `features/<domain>/keys.ts` factories (`authKeys`, `courseKeys`, `materialKeys`, `profileKeys`). The only other `fetch(` in the tree is the sanctioned **direct-to-storage presigned upload POST** in `components/courses/CourseMaterials.tsx` (no `Authorization` header — the signed fields are the authorization); TanStack's `refetch()` is a revalidation, not a data call.
- **Configuration boundary** — all `NEXT_PUBLIC_*` reads go through [`lib/config.ts`](lib/config.ts) (Zod-validated at module load). Server-only env (`SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT`) is read directly where consumed and is never inlined into the client bundle.
- **Guard chain** — `AuthProvider` (Keycloak `check-sso` + PKCE) under the query provider; then, for every `(app)` route: `AuthGuard` (authentication only) → `OnboardingGate` (profile 404 only; `/profile` exempt; errors never redirect) → `AppShell` (navigation chrome: desktop `AppSidebar` + mobile `MobileNav` from ONE `components/shell/nav-config.ts`). `/login` and `/register` auto-bridge to Keycloak via `components/auth/OidcEntryBridge`.
- **No fabricated surfaces** — navigation is identical for every signed-in user; material-management affordances are owner/instructor-gated; there is no admin surface, and the API contract of record is `docs/openapi.json` (drift-guarded by the backend's contract tests in CI).

---

## Storybook

Storybook is the component workbench and verification infrastructure (`npm run storybook`, port 6006):

- **26 story files / 104 suite tests** covering shared primitives, full surfaces (Dashboard, Courses, CourseDetail + Materials, Profile, the shell), and the negative-path auth states.
- **Dark-mode + RTL verification** — the preview syncs `.dark` from the backgrounds toolbar and `<html dir>` from the Direction toolbar (light + dark / LTR + RTL sweeps are the manual review instrument).
- **Accessibility** — `@storybook/addon-a11y` runs axe at `test: 'error'`, so any violation fails `npm run test:storybook` (the repo's own a11y evidence base).
- **Hermetic** — every story tree is wrapped in a `QueryClientProvider` with pre-seeded caches; no Keycloak initialization or live network call ever happens inside Storybook (the documented dev env values are inlined by `.storybook/main.ts`'s `viteFinal`, and `next/navigation` is aliased to a story-safe stub).
- **Chromatic** is wired (`.github/workflows/storybook.yml`, action pinned to the v18.13.3 digest) but **not enforced** — the workflow requires the `CHROMATIC_PROJECT_TOKEN` repository secret and has no run record yet.

Stories establish and verify behavior; they do not freeze visual design decisions (the redesign's token layer and conventions own that, per the guide §D).

---

## Testing & quality gate

CI (`.github/workflows/ci.yml`, frontend job) runs on every PR to `main` / `staging`:

1. `npm run lint`
2. `npm run typecheck`
3. `npx playwright install --with-deps chromium` — installs the browser binary for the Storybook browser-driven project
4. `npm run test` — unit (107 tests / 9 files)
5. `npm run test:storybook` — 104 tests / 26 story files, axe a11y enforcement at `test: 'error'`
6. `npm run build` — Next.js production build with `withSentryConfig`

### E2E suite (promotion evidence green; required-check decision open)

Four Playwright spec files (serial, Chromium-only, real Keycloak + backend — no auth or data is mocked):

1. `e2e/login.spec.ts` — login → dashboard.
2. `e2e/onboarding.spec.ts` — the first-login gate and wizard (7 tests: gate routing, validation, save failure + retry, redirect restoration).
3. `e2e/courses-crud.spec.ts` — the instructor CRUD loop (+ its in-test positive hub-affordance assertions) and the student negative-affordance flow (a non-instructor owner's hub exposes no management affordances).
4. `e2e/profile-roundtrip.spec.ts` — profile create → reload → update, verifying persistence.

Each of the three smoke flows (login, courses CRUD, profile) also ends with an in-spec compact-viewport block (360×800 shell contract on the same session — not a second Playwright project). Required environment: `E2E_USERNAME` / `E2E_PASSWORD` (student) and `E2E_INSTRUCTOR_USERNAME` / `E2E_INSTRUCTOR_PASSWORD` (instructor; absent pair ⇒ that flow skips with an explicit message, never a silent pass). Export commands and the full contract: `.github/workflows/e2e.yml` and [`docs/development/LOCAL_SETUP.md`](../docs/development/LOCAL_SETUP.md).

**Status:** the E2E workflow (`.github/workflows/e2e.yml`) runs on `workflow_dispatch` only. The Phase 6 promotion protocol is three consecutive green dispatch runs against staging:

```
Run 1/3: green — staged dispatch evidence owner-confirmed (2026-10-26)
Run 2/3: green — staged dispatch evidence owner-confirmed (2026-10-26)
Run 3/3: green — staged dispatch evidence owner-confirmed (2026-10-26)
Required CI check: NO — enabling it is a team-lead decision (kept open; e2e.yml's trigger design is unchanged)
```

The three green runs are owner-dispatched and owner-confirmed (the execution record lives with the owner, not in the repository); promoting E2E to a REQUIRED check remains the recorded team-lead decision at Gate F and has deliberately not been made by any batch.

---

## Sentry status

Sentry is configured for environment-aware observability:

- `next.config.ts` wraps the Next.js config with `withSentryConfig` (imported from the non-deprecated `@sentry/nextjs/config` subpath). Source-map upload is delegated to the SDK, which reads `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, and `SENTRY_PROJECT` from the environment at build time — never hardcoded, so they cannot leak into the build artifact. `deleteSourcemapsAfterUpload: true` keeps source maps out of the deployed bundle. Local dev builds gracefully skip upload when `SENTRY_AUTH_TOKEN` is absent.
- `sentry.client.config.ts` (env from `NEXT_PUBLIC_SENTRY_ENVIRONMENT` via `lib/config.ts`) and `sentry.server.config.ts` (`SENTRY_ENVIRONMENT` at runtime) apply the same sampling tiers: development 1.0 / staging 0.5 / production 0.1.

**Runtime verification status (unchanged; open owner-machine items):**

- Repository configuration: **verified** (build succeeds; `withSentryConfig` runs).
- Source-map upload: **configured, not runtime-verified** — the authenticated upload needs the Pod D `SENTRY_AUTH_TOKEN` secret (external dependency, not in this repository).
- Runtime Sentry event verification from a deployed, correctly labeled environment: **NOT RUN** — this is the conditional Gate F component recorded in the execution ledger (`docs/tasks/Frontend UI redesign/`); it applies when the final build deploys to staging and belongs to the owner's machine.

No Sentry credentials are committed.

---

## Common workflow

- For "where do I put this code?" and step-by-step recipes (new route, new primitive, new API domain, token/direction changes, new tests), use the [engineering guide's task table](./FRONTEND_ENGINEERING_GUIDE.md#f-common-engineering-tasks) — it is the maintained copy, and this README intentionally does not duplicate it.
- The API you code against is `docs/openapi.json` — never an endpoint absent from it.

**Run the quality gate before pushing:**

```bash
npm run lint && npm run typecheck && npm run test && npm run test:storybook && npm run build
```

If you touched E2E specs and have the stack + credentials available:

```bash
npm run test:e2e
```

---

## Further reading

- [`FRONTEND_ENGINEERING_GUIDE.md`](./FRONTEND_ENGINEERING_GUIDE.md) — the codebase itself: structure, architecture, conventions, testing, invariants.
- [`docs/development/LOCAL_SETUP.md`](../docs/development/LOCAL_SETUP.md) — canonical local setup (troubleshooting, OS notes, credential exports, verification checklist).
- [`docs/tasks/Frontend UI redesign/`](../docs/tasks/Frontend%20UI%20redesign/) — the active frontend execution context: the redesign roadmap (DOCX), the execution progress ledger, and the batch lifecycle rules.
- [`docs/tasks/Frontend Modernization/OpenLearn-AI_Frontend_Architecture_Modernization.docx`](../docs/tasks/Frontend%20Modernization/OpenLearn-AI_Frontend_Architecture_Modernization.docx) — the architecture decision study behind the feature-module conventions (historical background).
- [`docs/tasks/Frontend Modernization/OpenLearn-AI_Frontend_Modernization_Execution_Roadmap_v1.1-closure.md`](../docs/tasks/Frontend%20Modernization/OpenLearn-AI_Frontend_Modernization_Execution_Roadmap_v1.1-closure.md) — the pre-redesign modernization closure roadmap (historical background).
- [`docs/design-tokens.md`](../docs/design-tokens.md) and [`docs/adr/0010-frontend-design-direction-and-tokens.md`](../docs/adr/0010-frontend-design-direction-and-tokens.md) — token derivations and the design-direction ADR.
- `docs/openapi.json` — the tracked backend API contract (drift-guarded by the backend's contract tests in CI).
