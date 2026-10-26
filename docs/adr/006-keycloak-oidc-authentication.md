# ADR-006: Keycloak/OIDC authentication architecture

- **Status:** Accepted (2026-09-10)
- **Deciders:** @0Abanoub (Backend & Platform lead), @MuhammadSeyam (project
  lead and AI/ML lead)

## Context

Week 5 required backend authentication for the OpenLearn API. The original
custom design stored authentication state inside the OpenLearn PostgreSQL
database:

- bcrypt password hashes
- locally issued JWTs
- refresh tokens stored in a `refresh_tokens` table
- email-verification tokens
- locally stored user roles

Some of that scaffolding was implemented during the week's first half. Before it
became load-bearing, the team reevaluated the approach. Centralizing identity in
an external IdP removes responsibility for password storage, session handling,
and email verification from the application and moves it to a purpose-built,
standards-compliant component. During **Week 5**, Abanoub Makram and
Muhammad Seyam made the decision to replace the custom authentication design
with **Keycloak/OIDC**. This supersedes the custom design described above.

## Decision

Use **Keycloak as the authentication/identity authority** and OpenID Connect
(OIDC) as the protocol between the frontend, Keycloak, and the backend.

### Component responsibilities

**Keycloak owns:**

- user accounts
- passwords
- email verification
- login sessions
- OIDC authorization (Authorization Code flow with PKCE)
- access and refresh tokens
- realm roles (`student`, `instructor`, `admin`)

**FastAPI owns:**

- validating Keycloak access tokens (signature, issuer, audience, lifetime)
- authenticating API requests
- extracting realm roles from tokens
- application authorization / RBAC
- mapping a Keycloak identity to a local application user
- application-specific user data

**OpenLearn PostgreSQL owns only application data:**

- the application user record
- preferences / settings
- preferred language
- other local application data

The OpenLearn database **must not** store password hashes, refresh tokens,
email-verification tokens, or local authentication roles. The migration chain
(`bf5c36537834` → `c8103d7a5b42`) removes the custom-auth columns and the
`refresh_tokens` table to reflect this boundary.

### Authentication flow

1. The browser/user-agent signs in at Keycloak (`realm: openlearn`) using the
   public frontend client `openlearn-frontend` (Authorization Code flow with
   PKCE, method S256; no client secret).
2. Keycloak issues an access token scoped to the API audience
   (`aud = openlearn-api`) via the client's audience mapper.
3. The frontend presents the access token as a bearer token on API requests.
4. The backend validates the token and, for routes that need identity, maps it
   to a local application user.

### Token validation responsibilities

`backend/app/services/auth/oidc.py` validates, for every token:

- RS256 signature against the realm JWKS
- issuer (`iss`)
- audience (`aud = openlearn-api`)
- subject (`sub`)
- lifetime: `exp`, `iat`
- presence of the required standard claims (`exp`, `iat`, `iss`, `aud`, `sub`)

The following are intentionally **not** required for the current trust model:

- `typ` — describes the token type and is useful defense-in-depth, but the
  audience and endpoint semantics already enforce the correct access-token
  path.
- `azp` — identifies the authorized party/client that obtained the token. In
  the current architecture this corresponds to the frontend client, but
  requiring `azp = openlearn-frontend` would couple the API validation layer
  to one specific client.

The core trust properties are the signed Keycloak token, its issuer, its
signature, its audience, its subject, and its lifetime. `aud = openlearn-api`
is the API trust boundary: a token not issued for this API is rejected
regardless of other claims.

### Identity mapping

A Keycloak identity maps to a local application user by the pair:

```
(keycloak_issuer, keycloak_subject)
```

This pair is unique and nullable-free in the `users` table. The email address
is unique but is **not** the primary identifier, because:

- `email` is not required to be stable over a user's lifetime and can change
  (e.g., address updates, accounts recreated with the same email policy).
- A Keycloak `sub` is unique per issuer and stable.
- Using `issuer + subject` prevents two identity providers or realms from
  silently colliding onto one local account.

On first authenticated request, the backend maps the identity to a new local
application user (just-in-time provisioning). The `email_verified` value is
synced from the token claims on each login so the local record stays
consistent with Keycloak. Concurrent provisioning races are handled by
re-querying after an `IntegrityError` instead of leaking a duplicate-row
failure.

### Role / RBAC handling

Roles come from the token's `realm_access` claim (`student`, `instructor`,
`admin`), not from the database. `backend/app/api/deps.py` exposes
`require_role(...)` dependencies that map a required role to 403 responses;
missing or invalid credentials produce a generic 401. Malformed `realm_access`
payloads are handled safely (no crash, no roles granted).

## Consequences

- **Keycloak becomes an authentication infrastructure dependency.** Local
  development and any deployment must run a reachable Keycloak configured with
  the `openlearn` realm and the `openlearn-frontend` public client.
- **Authentication is centralized.** Users, passwords, sessions, tokens, and
  email verification are managed by Keycloak; OpenLearn no longer manages
  password security directly.
- **The application database is simpler.** No sensitive authentication
  material is stored locally, reducing the security surface of the OpenLearn
  database.
- **The API remains responsible for authorization.** RBAC is enforced in the
  backend from token roles; this cannot be delegated to Keycloak.
- **Keycloak availability and configuration become operationally important.**
  Outages or misconfiguration directly affect login and API access.
- **The custom-auth design is superseded.** Its residual columns/tables were
  removed by migration. `typ`/`azp` are not validated, as documented above;
  this is a deliberate design choice, not an omission.

## Alternatives considered

- **Continue the custom authentication design:** gives direct control over the
  auth code, but required building and trusting our own password storage,
  session management, and token issuance — substantial, security-sensitive
  work with no demonstrated project-specific benefit.
- **Keycloak/OIDC (chosen):** self-hostable, no per-seat cost, standard OIDC
  compliance, production-grade password/session handling, and realm roles that
  map naturally to the application's RBAC needs. It adds one infrastructure
  component to operate, which the zero-budget constraint keeps acceptable
  since it runs alongside the existing PostgreSQL service.
- **A managed identity provider such as Auth0:** strong IdP features and low
  operational burden, but a managed service was not justified while the team
  can run Keycloak locally with the existing infrastructure.
- **A backend-as-a-service auth provider such as Supabase Auth:** convenient
  but couples the project to a BaaS platform and pricing model outside the
  team's stack.