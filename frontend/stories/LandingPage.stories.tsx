import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";

import { LandingPage } from "../components/landing/LandingPage";

/**
 * Landing-page stories (Batch 4.1; CTA placement corrected by the
 * follow-up).
 *
 * `LandingPage` is the presentational composition — the page wrapper
 * (`app/page.tsx`) owns the auth-aware redirect, and no hook, query, or
 * Keycloak initialization runs anywhere in this tree at REST (the
 * navbar's `OidcEntryButton` imports the Keycloak adapter dynamically,
 * at click time). The stories are therefore hermetic by construction:
 * no providers, no network.
 *
 * The play assertions pin the approved messaging structure, the
 * capability-honesty rules, and the follow-up's auth-CTA placement:
 * "Log in" / "Create account" exist ONLY as the sticky top bar's
 * actions — the hero, the closing section, and the footer repeat
 * neither.
 *
 * Accessibility: the axe checks from the a11y addon run on every story
 * (fail-on-violation configuration untouched). The identity visual is
 * `aria-hidden` — the headings carry the meaning — so no contrast or
 * naming violation is introduced by the decorative strokes.
 */

const meta = {
    title: "Landing/LandingPage",
    component: LandingPage,
    tags: ["autodocs"],
    parameters: { layout: "fullscreen" },
} satisfies Meta<typeof LandingPage>;

export default meta;

type Story = StoryObj<typeof meta>;

export const FullPage: Story = {
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Sticky top bar: brand identity + the two auth actions.
        const header = canvasElement.querySelector("header");
        await expect(header).not.toBeNull();
        // §B.1: the navbar stays visible while scrolling — position
        // sticky at the viewport top, above page content (z-40).
        await expect(header).toHaveClass("sticky");
        await expect(header).toHaveClass("top-0");
        await expect(header).toHaveClass("z-40");

        // §B.2 + §C.3: the ONLY auth actions on the page live here, and
        // they are direct Keycloak actions (buttons), not links into a
        // local form.
        const loginActions = canvas.getAllByRole("button", {
            name: "Log in",
        });
        await expect(loginActions).toHaveLength(1);
        const registerActions = canvas.getAllByRole("button", {
            name: "Create account",
        });
        await expect(registerActions).toHaveLength(1);
        for (const action of [...loginActions, ...registerActions]) {
            await expect(header).toContainElement(action);
        }

        // No leftover auth links anywhere (hero / closing / footer).
        await expect(
            canvas.queryByRole("link", { name: "Log in" }),
        ).toBeNull();
        await expect(
            canvas.queryByRole("link", { name: "Create account" }),
        ).toBeNull();

        // Hero: approved positioning copy (no CTA row).
        await expect(
            canvas.getByRole("heading", {
                level: 1,
                name: /Bring your learning together/,
            }),
        ).toBeVisible();

        // The original Product Identity Visual is implemented as part of
        // the page (a token-drawn decorative SVG — no raster screenshot).
        const visual = canvasElement.querySelector(
            "main section svg[aria-hidden='true']",
        );
        await expect(visual).not.toBeNull();

        // Section structure: how it works, capabilities, audiences,
        // future direction — each with its own heading.
        await expect(
            canvas.getByRole("heading", {
                name: "Three steps to an organized start",
            }),
        ).toBeVisible();
        await expect(
            canvas.getByRole("heading", {
                name: "Current capabilities, honestly stated",
            }),
        ).toBeVisible();
        await expect(
            canvas.getByRole("heading", {
                name: "Built for students and instructors",
            }),
        ).toBeVisible();
        await expect(
            canvas.getByRole("heading", {
                name: "What's next — clearly labeled",
            }),
        ).toBeVisible();

        // Capability honesty: future items are labeled and non-claimed.
        await expect(canvas.getByText("In development")).toBeVisible();
        const plannedChips = canvas.getAllByText("Planned");
        await expect(plannedChips.length).toBeGreaterThanOrEqual(2);

        // The vision line is explicitly separated from current capability.
        await expect(
            canvas.getByText(/not part of the product today/),
        ).toBeVisible();
    },
};
