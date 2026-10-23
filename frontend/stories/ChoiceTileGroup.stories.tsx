import * as React from "react";

import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent, within } from "storybook/test";

import { ChoiceTileGroup } from "../components/ui/choice-tile-group";

/**
 * ChoiceTileGroup stories (Batch 4.1 corrective follow-up §A.4).
 *
 * The tile group is the reusable single-select pattern the onboarding
 * wizard now uses for every finite, contract-backed choice. The play
 * tests pin the accessibility contract: `role="radiogroup"` with
 * labelled tiles carrying `aria-checked`, click selection, arrow-key
 * movement (selection follows focus), roving `tabIndex`, the disabled
 * state, and the error/hint rendering — plus the optional inline
 * action slot (the wizard's "Clear") staying OUTSIDE the radiogroup.
 *
 * The group is CONTROLLED (`value` + `onValueChange`), so the
 * interactive stories render through `StatefulGroup`, which owns the
 * selected value in real React state — clicking then re-renders with
 * the new checked state exactly as the wizard experiences it.
 */

const meta = {
    title: "UI/ChoiceTileGroup",
    component: ChoiceTileGroup,
    tags: ["autodocs"],
    parameters: { layout: "padded" },
} satisfies Meta<typeof ChoiceTileGroup>;

export default meta;

type Story = StoryObj<typeof meta>;

const OPTIONS = [
    { value: "visual", label: "Visual" },
    { value: "aural", label: "Aural" },
    { value: "read-write", label: "Read/Write" },
    { value: "kinesthetic", label: "Kinesthetic" },
] as const;

function StatefulGroup({
    initialValue = "",
    action,
    ...rest
}: Omit<
    React.ComponentProps<typeof ChoiceTileGroup>,
    "value" | "onValueChange" | "action"
> & {
    initialValue?: string;
    /** Render-prop so story actions (the wizard's "Clear") can drive
     * the controlled state. */
    action?: (clear: () => void) => React.ReactNode;
}) {
    const [value, setValue] = React.useState(initialValue);

    return (
        <ChoiceTileGroup
            {...rest}
            value={value}
            onValueChange={setValue}
            action={action ? action(() => setValue("")) : undefined}
        />
    );
}

export const NothingSelectedYet: Story = {
    args: {
        id: "tiles-empty",
        label: "Learning style",
        options: OPTIONS,
        value: "",
        onValueChange: () => {},
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        const group = canvas.getByRole("radiogroup", { name: "Learning style" });
        await expect(group).toBeVisible();

        const tiles = canvas.getAllByRole("radio");
        await expect(tiles).toHaveLength(4);
        for (const tile of tiles) {
            await expect(tile).toHaveAttribute("aria-checked", "false");
        }

        // Roving tabindex with nothing selected: only the FIRST tile is
        // a tab stop.
        await expect(tiles[0]).toHaveAttribute("tabindex", "0");
        await expect(tiles[1]).toHaveAttribute("tabindex", "-1");
    },
};

export const ClickSelects: Story = {
    args: {
        id: "tiles-click",
        label: "Learning style",
        options: OPTIONS,
        value: "",
        onValueChange: () => {},
    },
    render: () => (
        <StatefulGroup
            id="tiles-click"
            label="Learning style"
            options={OPTIONS}
        />
    ),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await userEvent.click(canvas.getByRole("radio", { name: "Aural" }));

        await expect(
            canvas.getByRole("radio", { name: "Aural" }),
        ).toHaveAttribute("aria-checked", "true");
        await expect(
            canvas.getByRole("radio", { name: "Visual" }),
        ).toHaveAttribute("aria-checked", "false");

        // The selected tile becomes the roving tab stop.
        await expect(
            canvas.getByRole("radio", { name: "Aural" }),
        ).toHaveAttribute("tabindex", "0");
        await expect(
            canvas.getByRole("radio", { name: "Visual" }),
        ).toHaveAttribute("tabindex", "-1");

        // Selection is exclusive: choosing another tile moves it.
        await userEvent.click(canvas.getByRole("radio", { name: "Kinesthetic" }));
        await expect(
            canvas.getByRole("radio", { name: "Kinesthetic" }),
        ).toHaveAttribute("aria-checked", "true");
        await expect(
            canvas.getByRole("radio", { name: "Aural" }),
        ).toHaveAttribute("aria-checked", "false");
    },
};

export const ArrowKeysMoveSelection: Story = {
    args: {
        id: "tiles-arrows",
        label: "Learning style",
        options: OPTIONS,
        value: "visual",
        onValueChange: () => {},
    },
    render: () => (
        <StatefulGroup
            id="tiles-arrows"
            label="Learning style"
            options={OPTIONS}
            initialValue="visual"
        />
    ),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        const first = canvas.getByRole("radio", { name: "Visual" });
        first.focus();

        // ArrowRight: selection follows focus to the next tile.
        await userEvent.keyboard("{ArrowRight}");
        await expect(
            canvas.getByRole("radio", { name: "Aural" }),
        ).toHaveAttribute("aria-checked", "true");
        await expect(
            canvas.getByRole("radio", { name: "Visual" }),
        ).toHaveAttribute("aria-checked", "false");

        // Wrap-around from the last tile back to the first.
        await userEvent.keyboard("{ArrowRight}");
        await userEvent.keyboard("{ArrowRight}");
        await userEvent.keyboard("{ArrowRight}");
        await expect(
            canvas.getByRole("radio", { name: "Visual" }),
        ).toHaveAttribute("aria-checked", "true");

        // ArrowLeft wraps backwards to the last tile.
        await userEvent.keyboard("{ArrowLeft}");
        await expect(
            canvas.getByRole("radio", { name: "Kinesthetic" }),
        ).toHaveAttribute("aria-checked", "true");
    },
};

export const ErrorIsAnnounced: Story = {
    args: {
        id: "tiles-error",
        label: "Daily study time",
        options: [
            { value: "15", label: "15 min" },
            { value: "30", label: "30 min" },
        ],
        value: "",
        onValueChange: () => {},
        error: "Daily available minutes must be at least 1",
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        const group = canvas.getByRole("radiogroup", {
            name: "Daily study time",
        });
        await expect(group).toBeVisible();

        const error = canvas.getByRole("alert");
        await expect(error).toHaveTextContent(
            "Daily available minutes must be at least 1",
        );
        // aria-describedby links the group to the error for AT users.
        await expect(group).toHaveAttribute(
            "aria-describedby",
            "tiles-error-error",
        );
    },
};

export const DisabledTiles: Story = {
    args: {
        id: "tiles-disabled",
        label: "Daily study time",
        options: [
            { value: "15", label: "15 min" },
            { value: "30", label: "30 min" },
        ],
        value: "15",
        onValueChange: () => {},
        disabled: true,
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        for (const tile of canvas.getAllByRole("radio")) {
            // Disabled tiles: pointer events are off (Tailwind's
            // disabled:pointer-events-none) — assert the state instead
            // of attempting an interaction userEvent must refuse.
            await expect(tile).toBeDisabled();
        }
        await expect(
            canvas.getByRole("radio", { name: "15 min" }),
        ).toHaveAttribute("aria-checked", "true");
    },
};

export const InlineActionStaysOutsideGroup: Story = {
    // args mirror the meta typing (CSF3); the RENDER uses StatefulGroup
    // so the Clear action drives real controlled state.
    args: {
        id: "tiles-action",
        label: "Learning style (optional)",
        options: OPTIONS,
        value: "aural",
        onValueChange: () => {},
    },
    render: () => (
        <StatefulGroup
            id="tiles-action"
            label="Learning style (optional)"
            options={OPTIONS}
            initialValue="aural"
            action={(clear) => (
                <button type="button" onClick={clear}>
                    Clear
                </button>
            )}
        />
    ),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // The action button is rendered at the label row's inline end
        // and is NOT part of the radiogroup's radio set.
        const clear = canvas.getByRole("button", { name: "Clear" });
        await expect(clear).toBeVisible();
        await expect(clear).not.toHaveAttribute("role", "radio");
        await expect(canvas.getAllByRole("radio")).toHaveLength(4);

        // The Clear action works through the controlled state.
        await userEvent.click(clear);
        for (const tile of canvas.getAllByRole("radio")) {
            await expect(tile).toHaveAttribute("aria-checked", "false");
        }
    },
};
