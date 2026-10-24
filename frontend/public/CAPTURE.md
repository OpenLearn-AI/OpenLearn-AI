# courses-preview.png — how this asset was made

`public/courses-preview.png` is a genuine screenshot of this
repository's own `/courses` page, captured from the running product and
refreshed as part of the Batch 4.2 landing redesign. It is recorded here
for the claim-verification checks: the landing page shows no imagery the
product cannot render.

- **Route shown:** `/courses` (rendered live, dark `(app)` look).
- **Environment:** an isolated capture stack (this branch's frontend
  on `:3001`, its backend on `:8001`, an isolated Keycloak on `:8180`,
  and a scratch PostgreSQL database). Nothing from the shared dev stack
  (`:3000`/`:8000`) or its data appears in the capture.
- **Session:** a tool-created user signed in with Keycloak SSO through
  the real login flow. The content shown (two courses: "Foundations of
  Course Design" and "Study Strategies Lab") was created through the
  product's own `/courses/new` flow into the scratch database, so the
  screenshot shows real application state — not a mockup or a composed
  image. No fabricated metrics, testimonials, ratings, pricing, or
  policy claims appear anywhere in the asset.
- **Capture:** 1440x900 viewport at deviceScaleFactor 2 (2880x1800 PNG),
  viewport-only (no full-page scroll), taken after the course list had
  settled. The Next.js dev-tools overlay badge was removed before the
  capture: it is a dev-mode-only debug artifact, not part of the product
  UI.
- **Refresh procedure:** rebuild this branch, run the app against a
  scratch database, sign in with a seeded capture user, create a couple
  of real courses through `/courses/new`, capture `/courses` at the
  sizes above, and replace this file (keeping the 2880x1800 dimensions
  so the landing layout stays exact).

## Keycloak theme-edit gotcha (capture stack)

Keycloak persists gzipped renditions of theme static resources under
`/opt/keycloak/data/tmp/kc-gzip-cache/` (inside the
`ol-verify-keycloak` container, backed by the `/tmp/opencode/verifystack/kcdata`
volume), and gzip requests keep serving the stale bytes after the theme
file changes — identity-encoded requests see the new content while
browsers (which send `Accept-Encoding: gzip`) see the old one. After
editing anything under `infra/keycloak/themes/openlearn/`, clear the
cache:

    docker exec ol-verify-keycloak rm -rf /opt/keycloak/data/tmp/kc-gzip-cache

A full container restart is NOT sufficient; the stale gz survives in
the persistent volume. After a Keycloak restart, also restart the
backend uvicorn so its JWKS cache is re-fetched.
