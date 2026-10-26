import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent, waitFor, within } from "storybook/test";

import { DirectionToggle } from "../components/ui/direction-toggle";
import {
    DIRECTION_STORAGE_KEY,
    applyDirection,
} from "../lib/direction";

/**
 * Layout-direction control stories (Batch 4.4).
 *
 * The toggle is the user-facing half of `lib/direction.ts` — it
 * flips the live `<html dir>` attribute (the single source of
 * truth), persists the choice, and exposes the state through
 * `aria-pressed` (never the icon alone). These interaction tests
 * run in the real browser runner (the project's storybook vitest
 * project — actual DOM, actual localStorage), and they pin the
 * acceptance contract from the batch brief:
 *
 * 1. activating the control changes the ACTUAL document direction;
 * 2. the pressed state is represented accurately and accessibly;
 * 3. the choice is persisted, and re-activating returns to LTR;
 * 4. the control remains operable and state-accurate in RTL.
 *
 * Cleanup: each test restores LTR (and the Storybook preview
 * decorator re-asserts the toolbar's direction on every story
 * mount, so no leakage between stories).
 */

const meta = {
    title: "UI/DirectionToggle",
    component: DirectionToggle,
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof DirectionToggle>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** The full interaction contract: LTR → RTL → LTR with the state,
 * the document attribute, and the persistence all verified. */
export const RoundTrip: Story = {
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        const toggle = canvas.getByRole("button", {
            name: "Right-to-left layout",
        });

        // Baseline: not pressed, document is LTR, nothing persisted.
        await expect(toggle).toHaveAttribute("aria-pressed", "false");
        await expect(document.documentElement.dir).toBe("ltr");

        // First activation: the document ACTUALLY flips, the state
        // is represented, and the choice is persisted.
        await userEvent.click(toggle);
        await expect(toggle).toHaveAttribute("aria-pressed", "true");
        await expect(document.documentElement.dir).toBe("rtl");
        await expect(localStorage.getItem(DIRECTION_STORAGE_KEY)).toBe(
            "rtl",
        );

        // Second activation: back to LTR, state and storage follow.
        await userEvent.click(toggle);
        await expect(toggle).toHaveAttribute("aria-pressed", "false");
        await expect(document.documentElement.dir).toBe("ltr");
        await expect(localStorage.getItem(DIRECTION_STORAGE_KEY)).toBe(
            "ltr",
        );

        // Restore for subsequent stories.
        applyDirection("ltr");
    },
};

/** The control operated while the layout is ALREADY RTL (the
 * in-RTL usability requirement): names, pressed state, and the
 * flip back to LTR all behave. */
export const OperableInRtl: Story = {
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Enter RTL the way the app does. This is a direct store
        // mutation (not an act-wrapped interaction), so the
        // resulting re-render is awaited explicitly.
        applyDirection("rtl");

        const toggle = canvas.getByRole("button", {
            name: "Right-to-left layout",
        });
        await waitFor(() => {
            expect(toggle).toHaveAttribute("aria-pressed", "true");
        });

        await userEvent.click(toggle);
        await expect(toggle).toHaveAttribute("aria-pressed", "false");
        await expect(document.documentElement.dir).toBe("ltr");

        // Restore for subsequent stories.
        applyDirection("ltr");
    },
};
