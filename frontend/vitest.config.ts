import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { defineConfig } from 'vitest/config';

import { storybookTest } from '@storybook/addon-vitest/vitest-plugin';

import { playwright } from '@vitest/browser-playwright';

const dirname =
  typeof __dirname !== 'undefined' ? __dirname : path.dirname(fileURLToPath(import.meta.url));

// Two test projects:
//   - `unit`: plain node, for lib/ and feature unit tests (apiFetch,
//     key factory, etc.). No browser, no DOM — fast and CI-friendly.
//   - `storybook`: Storybook component tests (browser-driven, from the
//     existing addon-vitest setup).
export default defineConfig({
  test: {
    projects: [
      {
        // Plain node unit tests. Resolves the `@/*` path alias the same
        // way the app does (tsconfig `paths`).
        resolve: {
          alias: {
            '@': path.resolve(dirname),
          },
        },
        test: {
          name: 'unit',
          include: ['lib/**/*.test.ts', 'features/**/*.test.ts'],
          environment: 'node',
        },
      },
      {
        extends: true,
        plugins: [
          // The plugin will run tests for the stories defined in your Storybook config
          // See options at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon#storybooktest
          storybookTest({ configDir: path.join(dirname, '.storybook') }),
        ],
        test: {
          name: 'storybook',
          browser: {
            enabled: true,
            headless: true,
            provider: playwright({}),
            instances: [{ browser: 'chromium' }],
          },
        },
      },
    ],
  },
});
