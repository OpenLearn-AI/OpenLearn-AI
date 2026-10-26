import * as React from "react";

import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent, within } from "storybook/test";

import { ChoiceTileGroup } from "../components/ui/choice-tile-group";

/**
 * ChoiceTileGroup stories (Batch 4.1 corrective follow-up §A.4; multi
 * select added in the Batch 4.2 redesign).
 *
 * The tile group is the reusable single-select pattern for finite,
 * contract-backed choices, and since the Batch 4.2 redesign also ships
 * a genuine multi-select mode (toggle-button semantics) for free-text
 * backed fields like the wizard's VARK learning-style field. Both play
 * suites pin the accessibility contract:
 *
 *   SINGLE (`role="radiogroup"`): labelled tiles carrying
 *   `aria-checked`, click selection, arrow-key movement (selection
 *   follows focus), roving `tabIndex`, the disabled state, and the
 *   error/hint rendering — plus the optional inline action slot (the
 *   wizard's "Clear") staying OUTSIDE the group.
 *
 *   MULTI (`role="group"`): tiles carrying `aria-pressed`, natural tab
 *   order (each tile its own tab stop), space toggling the focused
 *   tile, independent selections (no exclusivity), and the same
 *   error/hint rendering and inline action slot.
 *
 * Both groups are CONTROLLED (`value` + `onValueChange`), so the
 * interactive stories render through `StatefulGroup`/`StatefulMultiGroup`,
 * which own the selection in real React state — clicking then
 * re-renders with the new state exactly as the wizard experiences it.
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
}: {
    initialValue?: string;
    action?: (clear: () => void) => React.ReactNode;
}) {
    const [value, setValue] = React.useState(initialValue);

    return (
        <ChoiceTileGroup
            id="tiles-single"
            label="Daily study time"
            options={OPTIONS}
            value={value}
            onValueChange={setValue}
            action={action ? action(() => setValue("")) : undefined}
        />
    );
}

function StatefulMultiGroup({
    initialValues = [],
    action,
}: {
    initialValues?: string[];
    action?: (clear: () => void) => React.ReactNode;
}) {
    const [values, setValues] = React.useState<string[]>(initialValues);

    return (
        <ChoiceTileGroup
            id="tiles-multi"
            label="Learning style (optional)"
            options={OPTIONS}
            multiple
            value={values}
            onValueChange={setValues}
            action={action ? action(() => setValues([])) : undefined}
        />
    );
}

export const NothingSelectedYet: Story = {
    args: {
        id: "tiles-single",
        label: "Daily study time",
        options: OPTIONS,
        value: "",
        onValueChange: () => {},
    },
    render: () => <StatefulGroup />,
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        const group = canvas.getByRole("radiogroup", {
            name: "Daily study time",
        });
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
        id: "tiles-single",
        label: "Daily study time",
        options: OPTIONS,
        value: "",
        onValueChange: () => {},
    },
    render: () => <StatefulGroup />,
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
        id: "tiles-single",
        label: "Daily study time",
        options: OPTIONS,
        value: "visual",
        onValueChange: () => {},
    },
    render: () => <StatefulGroup initialValue="visual" />,
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
        id: "tiles-single",
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
            "tiles-single-error",
        );
    },
};

export const DisabledTiles: Story = {
    args: {
        id: "tiles-single",
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
    // args mirror the meta typing; the RENDER uses StatefulGroup so the
    // Clear action drives real controlled state.
    args: {
        id: "tiles-single",
        label: "Daily study time",
        options: OPTIONS,
        value: "aural",
        onValueChange: () => {},
    },
    render: () => (
        <StatefulGroup
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
        // and is NOT part of the group's tile set.
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

export const MultiSelectsIndependently: Story = {
    args: {
        id: "tiles-multi",
        label: "Learning style (optional)",
        options: OPTIONS,
        multiple: true,
        value: [],
        onValueChange: () => {},
    },
    render: () => <StatefulMultiGroup />,
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        const group = canvas.getByRole("group", {
            name: "Learning style (optional)",
        });
        await expect(group).toBeVisible();

        const tiles = canvas.getAllByRole("button", { pressed: false });
        await expect(tiles).toHaveLength(4);
        for (const tile of tiles) {
            await expect(tile).toHaveAttribute("aria-pressed", "false");
        }

        await userEvent.click(canvas.getByRole("button", { name: "Visual" }));
        await userEvent.click(canvas.getByRole("button", { name: "Kinesthetic" }));
        await expect(
            canvas.getByRole("button", { name: "Visual" }),
        ).toHaveAttribute("aria-pressed", "true");
        await expect(
            canvas.getByRole("button", { name: "Kinesthetic" }),
        ).toHaveAttribute("aria-pressed", "true");
        await expect(
            canvas.getByRole("button", { name: "Aural" }),
        ).toHaveAttribute("aria-pressed", "false");

        // Independent toggles: pressing a tile again unselects ONLY it.
        await userEvent.click(canvas.getByRole("button", { name: "Visual" }));
        await expect(
            canvas.getByRole("button", { name: "Visual" }),
        ).toHaveAttribute("aria-pressed", "false");
        await expect(
            canvas.getByRole("button", { name: "Kinesthetic" }),
        ).toHaveAttribute("aria-pressed", "true");
    },
};

export const MultiKeyboardToggles: Story = {
    args: {
        id: "tiles-multi",
        label: "Learning style (optional)",
        options: OPTIONS,
        multiple: true,
        value: [],
        onValueChange: () => {},
    },
    render: () => <StatefulMultiGroup />,
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Natural tab order: every tile is its own tab stop (no roving
        // tabindex in the multi mode).
        await userEvent.tab();
        await expect(
            canvas.getByRole("button", { name: "Visual" }),
        ).toHaveAttribute("aria-pressed", "false");

        // Space toggles the focused tile.
        await userEvent.keyboard("{ }");
        await expect(
            canvas.getByRole("button", { name: "Visual" }),
        ).toHaveAttribute("aria-pressed", "true");

        // Arrow keys do NOT steer an aria-pressed toggle group (that is
        // the radiogroup's separate contract).
        await userEvent.keyboard("{ArrowRight}");
        await expect(
            canvas.getByRole("button", { name: "Visual" }),
        ).toHaveAttribute("aria-pressed", "true");
    },
};

export const MultiErrorIsAnnounced: Story = {
    args: {
        id: "tiles-multi",
        label: "Learning style (optional)",
        options: OPTIONS,
        multiple: true,
        value: [],
        onValueChange: () => {},
        error: "Keep it under 100 characters",
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        const group = canvas.getByRole("group", {
            name: "Learning style (optional)",
        });
        await expect(group).toHaveAttribute(
            "aria-describedby",
            "tiles-multi-error",
        );

        const error = canvas.getByRole("alert");
        await expect(error).toHaveTextContent("Keep it under 100 characters");
    },
};

export const MultiInlineActionClearsAll: Story = {
    // args mirror the meta typing; the RENDER uses StatefulMultiGroup
    // so the Clear action drives real controlled state.
    args: {
        id: "tiles-multi",
        label: "Learning style (optional)",
        options: OPTIONS,
        multiple: true,
        value: ["aural", "kinesthetic"],
        onValueChange: () => {},
    },
    render: () => (
        <StatefulMultiGroup
            initialValues={["aural", "kinesthetic"]}
            action={(clear) => (
                <button type="button" onClick={clear}>
                    Clear
                </button>
            )}
        />
    ),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        const clear = canvas.getByRole("button", { name: "Clear" });
        await expect(clear).toBeVisible();
        await expect(canvas.getAllByRole("button", { pressed: true })).toHaveLength(
            2,
        );

        await userEvent.click(clear);
        for (const tile of canvas.getAllByRole("button", {
            name: /(Visual|Aural|Read\/Write|Kinesthetic)/,
        })) {
            await expect(tile).toHaveAttribute("aria-pressed", "false");
        }
    },
};
