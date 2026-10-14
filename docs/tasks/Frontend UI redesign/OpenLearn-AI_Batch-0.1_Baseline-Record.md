# OpenLearn-AI Frontend — Batch 0.1 Baseline Record (Evidence Log)

**Batch:** 0.1 — Baseline verification run (read-only) · **Executed:** 2026-10-14 · **Executor:** GLM (Super Z)

## 1. Repository identity

| Field | Value |
|---|---|
| Repository URL | https://github.com/OpenLearn-AI/OpenLearn-AI.git |
| Branch | `frontend-redesign` (equal to `origin/frontend-redesign`) |
| HEAD SHA | `699c496db8896e3235d8f9585a1fb801f90d98b6` (commit `frontend-redesign-FR-REB-02-full-roadmap-rewrite-week9`, 2026-10-08) |
| History position | FR-REB-02 patch commit on top of baseline `2eccad0`; contains `origin/staging @ d1ba348` (PR #78) |
| Staging containment | `git merge-base --is-ancestor origin/staging HEAD` → contained; `HEAD..origin/staging` empty |
| Working tree at start | Clean (fresh clone, no pre-existing changes) |
| Working tree at end | Clean except the ledger update (the batch's only authorized change) |

## 2. Execution environment

| Item | Value | Impact |
|---|---|---|
| Node.js | v24.21.0 / npm 11.19.0 | CI pins Node 20 — deviation recorded; all five script checks green anyway |
| TypeScript | 5.9.3 | — |
| Playwright browser | Chromium headless-shell v1243 (Chrome 153.0.8010.12) | installed locally for Storybook tests |
| Docker | **NOT AVAILABLE** | local stack (db + Keycloak containers) impossible → E2E/probe blocked |
| Python | 3.12.15 (matches CI exactly) | not needed for frontend checks |
| Network egress | General egress OK (github.com → 200); `*.duckdns.org` staging hosts **unreachable** (TLS timeouts; DNS resolves 16.170.158.155) | staging checks blocked |
| Credentials | `E2E_USERNAME` / `E2E_PASSWORD` **absent** | E2E + F5 probe blocked; none fabricated (forbidden) |

## 3. The eight checks

| # | Check | Command / request | Outcome | Evidence |
|---|---|---|---|---|
| 1 | Lint | `npm run lint` (eslint flat config) | **PASS** | exit 0, zero findings |
| 2 | Typecheck | `npm run typecheck` (`tsc --noEmit`) | **PASS** | exit 0 |
| 3 | Unit tests | `npm run test` (vitest `unit` project) | **PASS** | 22/22 tests, 3 files (12+5+5) — matches ledger counts |
| 4 | Storybook (CI's test command) | `npm run test:storybook` (vitest `storybook` project, headless Chromium, axe fail-on-violation) | **PASS** | 42/42 tests, 12 story files — matches ledger counts |
| 5 | Production build | `npm run build` with CI-documented fallback `NEXT_PUBLIC_*` env vars (no repo file created) | **PASS** | exit 0; 9 app routes + `/_not-found` |
| 6 | E2E trio (login / courses-crud / profile-roundtrip) | `npm run test:e2e` | **NOT RUN** (skipped 3/3, exit 0) | specs self-skip on absent `E2E_USERNAME`/`E2E_PASSWORD`; local Keycloak stack impossible (no Docker); staging unreachable. Missing prerequisites — not a test failure |
| 7 | F5 live API probe | authenticated `GET {API}/v1/courses` (HTTPBearer) | **BLOCKED** | no credentials + no reachable environment (Docker absent; staging timeouts). Contract fact re-confirmed: `CourseResponse.created_at` = `format: date-time`; live emission **UNVERIFIED** (Open Question #1 open) |
| 8 | Staging CORS preflight | `OPTIONS https://openlearn-api-staging.duckdns.org/v1/courses` with `Origin: https://openlearn-web-staging.duckdns.org`, `Access-Control-Request-Method: GET`, `Access-Control-Request-Headers: authorization` | **BLOCKED** | connection timed out after 15 s (no HTTP status, no CORS headers observable). Compose-level `CORS_ORIGINS` verified unchanged at file level; live confirmation (Open Question #2) open |

Conclusiveness: checks 1–5 conclusive (PASS). Checks 6–8 are **limited by unavailable prerequisites** — they are neither passes nor product failures.

## 4. Bucket A findings — re-verified present in code at `699c496`

| Finding | Verification evidence | Status |
|---|---|---|
| F3 | `app/(app)/courses/[id]/edit/page.tsx` — `<CourseForm mode="edit" …>` without `key={course.id}` | Present (reconfirmed) |
| F4 | `app/(app)/profile/page.tsx:109` — `<ProfileForm profile={…} />` not re-keyed | Present |
| F5 | `features/courses/schemas.ts:25` — `created_at: z.string().datetime({ offset: true })` | Present (schema side; live emission unverified) |
| F6 | `components/auth/LoginForm.tsx:17–30` — doc-comment claims "non-API route" filtering; code excludes only `//`, `/login`, `/register` | Present (drift) |
| S1 | `app/(app)/dashboard/page.tsx` — exactly 5 "Coming soon" strings (lines 56, 67, 78, 163, 192) | Present |
| S2 | `app/page.tsx` — markets RAG assistants, knowledge graphs, quizzes, flashcards | Present |
| S8 | `app/(auth)/` = layout.tsx + login + register only; no error.tsx/loading.tsx (`(app)` has both) | Present |
| W5 | `frontend/package.json` — `"shadcn": "^4.18.0"` in `dependencies` | Present |
| W6 | 6 devDependencies pinned to `"latest"` (@chromatic-com/storybook, @vitest/browser-playwright, @vitest/coverage-v8, playwright, vite, vitest) | Present |
| W7 | `.github/workflows/storybook.yml:28` — `uses: chromaui/action@latest` | Present |
| W8 | `frontend/package.json` — no `engines` field | Present |
| F1 chain | `frontend/Dockerfile` ARGs lack `NEXT_PUBLIC_SENTRY_ENVIRONMENT`; `deploy-staging.yml` passes DSN only; staging compose frontend service has `SENTRY_DSN` only; `infra/.env.staging.example` has `SENTRY_DSN=` only | Open (all five links) |

## 5. Blocked checks — exactly what is missing

1. **E2E trio (rerun path A — local):** Docker daemon + `scripts/setup-dev.sh` stack (db, Keycloak, backend :8000, frontend :3000) + `E2E_USERNAME=testuser` / `E2E_PASSWORD=<OPENLEARN_TEST_USER_PASSWORD from .env.local>`.
   **(rerun path B — staging):** network reachability to `openlearn-web-staging.duckdns.org` + `PLAYWRIGHT_BASE_URL` + staging credentials (`E2E_USERNAME`/`E2E_PASSWORD`).
2. **F5 probe:** a valid bearer token from a real Keycloak (local realm `openlearn` via the setup script, or staging) + reachable API. Do NOT fabricate credentials.
3. **CORS preflight:** any host with network access to `openlearn-api-staging.duckdns.org` (443). The preflight request itself is unauthenticated.

## 6. Documentation artifacts

| Artifact | Path | Change |
|---|---|---|
| Execution ledger (in-repo, authorized) | `docs/tasks/Frontend UI redesign/OpenLearn-AI_Frontend_Execution_Progress.md` | Current State → 0.1 start facts; History row; full 0.1 execution log; status-board row; next-batch pointer |
| Batch patch (lifecycle §7–§9) | `frontend-redesign-0.1-baseline-verification-run.patch` | `git diff --cached --binary` from isolated clone @ `699c496`; `git apply --check` + apply + byte-identity validated on a pristine checkout |
| This evidence record (out-of-repo copy) | `OpenLearn-AI_Batch-0.1_Baseline-Record.md` | verbatim evidence companion |

## 7. Verdict

**Batch 0.1 is PARTIALLY EXECUTED — completion criteria not yet met.** Five of the six script runs PASS conclusively; the E2E trio, the F5 live answer, and the CORS preflight confirmation (all named Gate A evidence, roadmap §21) could not be produced in this environment and are blocked, not failed. **Gate A is NOT passed.** Application files are byte-identical to `699c496`; the only in-repo change is the ledger update. Next step is Seyam's decision: rerun the three blocked checks in a capable environment, then authorize 0.2.
