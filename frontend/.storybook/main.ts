import type { StorybookConfig } from '@storybook/nextjs-vite';

const config: StorybookConfig = {
  "stories": [
    "../stories/**/*.mdx",
    "../stories/**/*.stories.@(js|jsx|mjs|ts|tsx)"
  ],
  "addons": [
    "@chromatic-com/storybook",
    "@storybook/addon-vitest",
    "@storybook/addon-a11y",
    "@storybook/addon-docs"
  ],
  "framework": "@storybook/nextjs-vite",
  "staticDirs": [
    "../public"
  ]
};

/**
 * Batch 3.3: inline the client `NEXT_PUBLIC_*` configuration into the
 * Storybook Vite bundle, mirroring what Next.js does at Next build
 * time. `lib/config.ts` parses these values with Zod at import time and
 * throws when they are missing, so the shell stories — the first
 * stories to import the auth/API chain (`useMe` → `lib/api` →
 * `lib/config`, and `LogoutButton` → `lib/keycloak` → `lib/config`) —
 * need them present to render at all.
 *
 * Values are the repository's own documented development defaults from
 * `frontend/.env.example` (the same pre-existing requirement the
 * production build already has). This affects the Storybook bundle
 * only; application builds and runtime behavior are untouched, and no
 * real backend is contacted by stories (queries resolve to their
 * error state, which the shell handles via the existing fallback).
 */
config.viteFinal = async (viteConfig) => {
  viteConfig.define = {
    ...viteConfig.define,
    'process.env.NEXT_PUBLIC_API_URL': JSON.stringify('http://localhost:8000'),
    'process.env.NEXT_PUBLIC_KEYCLOAK_URL': JSON.stringify('http://localhost:8080'),
    'process.env.NEXT_PUBLIC_KEYCLOAK_REALM': JSON.stringify('openlearn'),
    'process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID': JSON.stringify('openlearn-frontend'),
    'process.env.NEXT_PUBLIC_SENTRY_DSN': JSON.stringify(''),
    'process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT': JSON.stringify('development'),
  };
  return viteConfig;
};

export default config;
