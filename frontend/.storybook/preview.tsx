import type { Preview } from '@storybook/nextjs-vite'
import React, { useEffect } from 'react'

import '../app/globals.css'

/**
 * Storybook preview with RTL direction + dark-mode sync (Phase 5 D10).
 *
 * Direction is controlled via the `direction` toolbar item. LTR is the
 * default. When `rtl` is selected, the story iframe's `<html dir>`
 * attribute is set to `rtl`, causing logical CSS utilities (`ms-`,
 * `me-`, `ps-`, `pe-`, `text-start`, `text-end`) to flip correctly.
 *
 * Dark mode is synced via the `backgrounds` toolbar. When a dark
 * background value is selected, the `.dark` class is added to
 * `document.documentElement` so Tailwind's `dark:` variant tokens
 * resolve correctly. When light is selected, the `.dark` class is
 * removed.
 */
function WithDirection({ Story, direction, isDark }: { Story: React.ElementType; direction: string; isDark: boolean }) {
  useEffect(() => {
    document.documentElement.dir = direction
  }, [direction])

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [isDark])

  return <Story />
}

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
       color: /(background|color)$/i,
       date: /Date$/i,
      },
    },

    backgrounds: {
      options: {
        light: { name: 'Light', value: '#ffffff' },
        dark: { name: 'Dark', value: '#0a0a0a' },
      },
    },

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      // Phase 5: flipped to 'error' for UI stories so CI fails on
      // new axe violations. Runtime verification still pending —
      // the user must run `npm run test:storybook` locally to
      // confirm the stories are actually axe-clean.
      test: 'error'
    }
  },

  globalTypes: {
    direction: {
      name: 'Direction',
      description: 'Component text direction (LTR/RTL)',
      defaultValue: 'ltr',
      toolbar: {
        icon: 'transfer',
        items: [
          { value: 'ltr', icon: 'arrowleft', title: 'LTR (Left-to-Right)' },
          { value: 'rtl', icon: 'arrowright', title: 'RTL (Right-to-Left)' },
        ],
      },
    },
  },

  decorators: [
    (Story, context) => {
      const backgroundValue = context.globals?.backgrounds?.value as string | undefined
      const isDark = backgroundValue ? backgroundValue === '#0a0a0a' : false
      return (
        <WithDirection
          Story={Story}
          direction={context.globals?.direction ?? 'ltr'}
          isDark={isDark}
        />
      )
    },
  ],
};

export default preview;
