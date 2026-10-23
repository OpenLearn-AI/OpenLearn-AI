import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";

import { LandingPage } from "../components/landing/LandingPage";

/**
 * Landing-page stories (Batch 4.1).
 *
 * `LandingPage` is the presentational composition — the page wrapper
 * (`app/page.tsx`) owns the auth-aware redirect, and no hook, query, or
 * Keycloak initialization runs anywhere in this tree. The stories are
 * therefore hermetic by construction: no providers, no network.
 *
 * The play assertions pin the approved messaging structure and the
 * capability-honesty rules: the hero copy, both CTAs with their real
 * destinations, the original Product Identity Visual (no screenshot —
 * owner decision Q1/Q6), and the explicit "In development" / "Planned"
 * labeling of future items (never presented as available).
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

        // Top bar: brand identity + the two auth actions.
        const brand = canvas.getByRole("link", { name: "OpenLearn AI" });
        await expect(brand).toHaveAttribute("href", "/");

        // Hero: approved positioning + the two CTAs.
        await expect(
            canvas.getByRole("heading", {
                level: 1,
                name: /Bring your learning together/,
            }),
        ).toBeVisible();

        const registerLinks = canvas.getAllByRole("link", {
            name: "Create account",
        });
        for (const link of registerLinks) {
            await expect(link).toHaveAttribute("href", "/register");
        }
        const loginLinks = canvas.getAllByRole("link", { name: "Log in" });
        for (const link of loginLinks) {
            await expect(link).toHaveAttribute("href", "/login");
        }

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
