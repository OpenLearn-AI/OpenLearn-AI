import * as React from "react";

import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent, waitFor, within } from "storybook/test";

import { Button } from "../components/ui/button";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "../components/ui/dialog";

/**
 * Alert-dialog primitive stories (Batch 3.2).
 *
 * The demo mirrors the DeleteCourseButton composition (trigger +
 * labelled alert dialog + async confirmation contract) without the
 * router/mutation so the primitive's own behavior is exercised:
 * opening, accessible naming, keyboard dismissal, cancellation, and
 * the no-auto-close confirm contract. The Pending and Error stories
 * show the disabled/loading and inline-error states.
 */

function AlertDialogDemo({
    defaultOpen = false,
    pending = false,
    errorMessage = null,
}: {
    defaultOpen?: boolean;
    pending?: boolean;
    errorMessage?: string | null;
}) {
    const [open, setOpen] = React.useState(defaultOpen);

    return (
        <AlertDialog
            open={open}
            onOpenChange={(nextOpen) => {
                if (!pending) {
                    setOpen(nextOpen);
                }
            }}
        >
            <AlertDialogTrigger
                render={
                    <Button
                        variant="destructive"
                        size="sm"
                        disabled={pending}
                    >
                        Delete Course
                    </Button>
                }
            />
            <AlertDialogContent aria-label="Delete course: Introduction to AI">
                <AlertDialogHeader>
                    <AlertDialogTitle>Delete this course?</AlertDialogTitle>
                    <AlertDialogDescription>
                        This will permanently delete{" "}
                        <span className="font-medium">
                            Introduction to AI
                        </span>{" "}
                        and cannot be undone.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                {errorMessage && (
                    <p
                        role="alert"
                        aria-live="assertive"
                        className="text-sm text-destructive"
                    >
                        {errorMessage}
                    </p>
                )}
                <AlertDialogFooter>
                    <AlertDialogCancel disabled={pending}>
                        Cancel
                    </AlertDialogCancel>
                    <AlertDialogAction
                        variant="destructive"
                        size="sm"
                        disabled={pending}
                    >
                        {pending ? "Deleting..." : "Yes, delete it"}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
}

const meta = {
    title: "UI/AlertDialog",
    component: AlertDialogDemo,
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof AlertDialogDemo>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Open: Story = {
    args: {
        defaultOpen: true,
    },
};

export const Pending: Story = {
    args: {
        defaultOpen: true,
        pending: true,
    },
};

export const Error: Story = {
    args: {
        defaultOpen: true,
        errorMessage: "You do not have permission to delete this course.",
    },
};

export const Interaction: Story = {
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        // The alert dialog portals into the story iframe's document —
        // NOT the manager page document the test runner sees — so all
        // dialog queries go through the canvas element's ownerDocument.
        const body = within(canvasElement.ownerDocument.body);

        // findBy* with an explicit timeout is used at every phase
        // boundary: it retries briefly, which absorbs the iframe
        // story-swap and the portal mount.
        const trigger = await canvas.findByRole(
            "button",
            { name: "Delete Course" },
            { timeout: 5000 }
        );
        await userEvent.click(trigger);

        // Accessible role and naming. The dialog itself is located by
        // role (aria-label-driven accessible-name matching is not
        // reliable in the cross-document test runner), and its naming
        // contract is asserted on the aria-label attribute directly.
        const dialog = (await body.findAllByRole("alertdialog"))[0];
        // toBeInTheDocument is used instead of jest-dom's visibility
        // heuristics: the fixed-position popup renders across the
        // test runner's document boundary, where computed-style
        // visibility checks are not reliable. Unmount-on-close is the
        // deterministic contract Base UI gives us.
        await expect(dialog).toBeInTheDocument();
        await expect(dialog).toHaveAttribute(
            "aria-label",
            "Delete course: Introduction to AI"
        );
        await expect(
            within(dialog).getByRole("heading", {
                name: "Delete this course?",
            })
        ).toBeInTheDocument();
        await expect(
            within(dialog).getByText(/permanently delete/)
        ).toBeInTheDocument();

        // The confirm action never auto-closes (async contract): the
        // caller closes the dialog on mutation success.
        await userEvent.click(
            within(dialog).getByRole("button", { name: "Yes, delete it" })
        );
        await expect(dialog).toBeInTheDocument();

        // Cancel closes.
        await userEvent.click(
            within(dialog).getByRole("button", { name: "Cancel" })
        );
        // Close unmounts after the exit animation — wait for removal.
        await waitFor(
            () => expect(body.queryAllByRole("alertdialog")).toHaveLength(0),
            { timeout: 5000 }
        );

        // Escape closes (keyboard dismissal; the dialog is modal and
        // focus-trapped while open).
        const reopenTrigger = await canvas.findByRole(
            "button",
            { name: "Delete Course" },
            { timeout: 5000 }
        );
        await userEvent.click(reopenTrigger);
        const reopened = (await body.findAllByRole("alertdialog"))[0];
        await expect(reopened).toBeInTheDocument();
        await userEvent.keyboard("{Escape}");
        await waitFor(
            () => expect(body.queryAllByRole("alertdialog")).toHaveLength(0),
            { timeout: 5000 }
        );
    },
};
