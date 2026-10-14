FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm config set maxsockets 1 \
    && npm config set fetch-retries 1 \
    && npm config set fetch-timeout 30000 \
    && npm ci

COPY . .

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

ARG NEXT_PUBLIC_KEYCLOAK_URL
ENV NEXT_PUBLIC_KEYCLOAK_URL=$NEXT_PUBLIC_KEYCLOAK_URL

ARG NEXT_PUBLIC_KEYCLOAK_REALM
ENV NEXT_PUBLIC_KEYCLOAK_REALM=$NEXT_PUBLIC_KEYCLOAK_REALM

ARG NEXT_PUBLIC_KEYCLOAK_CLIENT_ID
ENV NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=$NEXT_PUBLIC_KEYCLOAK_CLIENT_ID

ARG NEXT_PUBLIC_SENTRY_DSN
ENV NEXT_PUBLIC_SENTRY_DSN=$NEXT_PUBLIC_SENTRY_DSN

ARG NEXT_PUBLIC_SENTRY_ENVIRONMENT
ENV NEXT_PUBLIC_SENTRY_ENVIRONMENT=$NEXT_PUBLIC_SENTRY_ENVIRONMENT

# Build-time source-map upload secrets for @sentry/nextjs' withSentryConfig
# (frontend/next.config.ts). They are mounted as BuildKit secrets for this
# RUN only — never written to image layers, the runtime environment, or the
# build log. The SDK reads them from the process environment; when absent
# (local dev, forks) the upload is skipped and the build still succeeds.
# SENTRY_ORG / SENTRY_PROJECT are non-secret slugs; SENTRY_AUTH_TOKEN is a
# real secret. CI supplies them via docker/build-push-action's `secrets`.
RUN --mount=type=secret,id=sentry_auth_token \
    --mount=type=secret,id=sentry_org \
    --mount=type=secret,id=sentry_project \
    SENTRY_AUTH_TOKEN="$(cat /run/secrets/sentry_auth_token 2>/dev/null || true)" \
    SENTRY_ORG="$(cat /run/secrets/sentry_org 2>/dev/null || true)" \
    SENTRY_PROJECT="$(cat /run/secrets/sentry_project 2>/dev/null || true)" \
    npm run build


FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0

RUN addgroup -S nodejs && adduser -S nextjs -G nodejs

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
