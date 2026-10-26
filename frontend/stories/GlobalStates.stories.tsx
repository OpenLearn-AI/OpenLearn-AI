import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import NotFoundPage from "../app/not-found";
import AppErrorBoundary from "../app/(app)/error";
import AuthErrorBoundary from "../app/(auth)/error";
import AppLoadingBoundary from "../app/(app)/loading";

/**
 * Global-state stories (Batch 4.4) — the four route-group states
 * in one file: the root 404, the `(app)` and `(auth)` error
 * boundaries, and the `(app)` loading boundary. They are one
 * deliverable (the app's global states) and share one purpose
 * here: axe coverage in the standard story run plus the direction
 * × theme sweep of the rendered checks, so the states are verified
 * in the same matrices as every other surface. One meta hosts the
 * set; each story carries its own render (the CSF pattern for a
 * deliberately grouped file).
 *
 * Contracts pinned: the not-found action routes home; both error
 * boundaries keep the Next.js App Router contract (error + reset;
 * internal details are never rendered — the fixture error's
 * message text is asserted as an ABSENCE); the reset control
 * actually invokes `reset()`. The `(auth)` story renders in the
 * auth shell's fixed-dark centered language; the `(app)` states
 * render free-standing (the sidebar shell persists around them in
 * the real app).
 */

const fixtureError = new Error(
    "Internal detail that must never reach the user",
);

/** The reset spy — module-level so the story's render and its play
 * assertion share ONE function instance. */
const resetSpy = fn();

const meta = {
    title: "Pages/Global States",
    component: NotFoundPage,
    parameters: { layout: "fullscreen" },
    tags: ["autodocs"],
} satisfies Meta<typeof NotFoundPage>;

export default meta;

type Story = StoryObj<typeof meta>;

export const NotFound: Story = {
    render: () => <NotFoundPage />,
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            canvas.getByRole("heading", { name: "Page not found" }),
        ).toBeVisible();
        // The numeral is decorative; the heading carries the state
        // (there is no second, numeral-named heading).
        await expect(
            canvas.queryByRole("heading", { name: "404" }),
        ).not.toBeInTheDocument();

        const home = canvas.getByRole("link", { name: "Back to home" });
        await expect(home).toBeVisible();
        await expect(home).toHaveAttribute("href", "/");
    },
};

export const AppError: Story = {
    render: () => (
        <AppErrorBoundary error={fixtureError} reset={() => {}} />
    ),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            canvas.getByRole("heading", { name: "Something went wrong" }),
        ).toBeVisible();
        await expect(
            canvas.getByRole("button", { name: "Try again" }),
        ).toBeVisible();
        // Internal details never reach the user.
        await expect(
            canvas.queryByText(/Internal detail/),
        ).not.toBeInTheDocument();
    },
};

/** The reset contract: the control invokes the boundary's reset. */
export const AppErrorReset: Story = {
    render: () => (
        <AppErrorBoundary error={fixtureError} reset={resetSpy} />
    ),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        await userEvent.click(
            canvas.getByRole("button", { name: "Try again" }),
        );
        await expect(resetSpy).toHaveBeenCalledTimes(1);
    },
};

export const AuthError: Story = {
    // The (auth) surface is fixed dark and centers its children.
    render: () => (
        <div className="dark flex min-h-svh items-center justify-center bg-background p-4 text-foreground">
            <AuthErrorBoundary error={fixtureError} reset={() => {}} />
        </div>
    ),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            canvas.getByRole("heading", { name: "Something went wrong" }),
        ).toBeVisible();
        await expect(
            canvas.getByRole("button", { name: "Try again" }),
        ).toBeVisible();
        await expect(
            canvas.queryByText(/Internal detail/),
        ).not.toBeInTheDocument();
    },
};

export const AppLoading: Story = {
    render: () => <AppLoadingBoundary />,
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        // The shared async-state kit is the presentation, with its
        // polite live region.
        await expect(canvas.getByRole("status")).toBeVisible();
        await expect(canvas.getByText("Loading...")).toBeVisible();
    },
};
