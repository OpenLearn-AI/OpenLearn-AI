import type { Preview } from '@storybook/nextjs-vite'
import React, { useEffect } from 'react'

/**
 * Storybook preview with RTL direction support (Phase 5 D10).
 *
 * Direction is controlled via the `direction` toolbar item. LTR is the
 * default. When `rtl` is selected, the story iframe's `<html dir>`
 * attribute is set to `rtl`, causing logical CSS utilities (`ms-`,
 * `me-`, `ps-`, `pe-`, `text-start`, `text-end`) to flip correctly.
 *
 * Dark mode is preserved via the existing ThemeProvider/class strategy.
 */
function WithDirection({ Story, direction }: { Story: React.ElementType; direction: string }) {
  useEffect(() => {
    document.documentElement.dir = direction
  }, [direction])

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

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: 'todo'
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
    (Story, context) => (
      <WithDirection
        Story={Story}
        direction={context.globals?.direction ?? 'ltr'}
      />
    ),
  ],
};

export default preview;
