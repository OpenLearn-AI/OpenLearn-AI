import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";

import { LandingPage } from "../components/landing/LandingPage";

/**
 * Landing-page stories (Batch 4.1; CTA placement corrected by the
 * follow-up; rebuilt for the Batch 4.2 public-direction redesign).
 *
 * `LandingPage` is the presentational composition — the page wrapper
 * (`app/page.tsx`) owns the auth-aware redirect, and no hook, query, or
 * Keycloak initialization runs anywhere in this tree at REST (the
 * navbar's `OidcEntryButton` imports the Keycloak adapter dynamically,
 * at click time). The stories are therefore hermetic by construction:
 * no providers, no network.
 *
 * The play assertions pin the redesigned structure and its honesty
 * rules: a recessed notch navbar holding ONLY auth entry points, a
 * short hero (one product screenshot instead of an invented feature
 * grid), and a compact honest status list. No fabricated metrics,
 * testimonials, ratings, pricing, or policy claims may appear.
 *
 * Accessibility: the axe checks from the a11y addon run on every story
 * (fail-on-violation configuration untouched). The decorative ambient
 * layers and the screenshot's figure are structured so no contrast or
 * naming violation is introduced.
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

        // Notch navbar: brand identity + the two auth actions.
        const header = canvasElement.querySelector("header");
        await expect(header).not.toBeNull();
        // The navbar stays pinned to the top of the viewport, above
        // the page content, while scrolling.
        await expect(header).toHaveClass("sticky");
        await expect(header).toHaveClass("top-0");
        await expect(header).toHaveClass("z-40");

        // The ONLY auth actions on the page live here, and they are
        // direct Keycloak actions (buttons), not links into a local
        // form.
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

        // No leftover auth CTAs anywhere else on the page (hero,
        // status panel, or footer).
        await expect(
            canvas.queryByRole("button", { name: "Sign in with OpenLearn AI" }),
        ).toBeNull();
        await expect(
            canvas.queryByRole("link", { name: "Log in" }),
        ).toBeNull();
        await expect(
            canvas.queryByRole("link", { name: "Create account" }),
        ).toBeNull();

        // Hero: short prose, no CTA row. The page has a one-shot
        // entrance animation (the reduced-motion guard collapses it to
        // an instant final state), so the first assertion waits for the
        // animation to settle rather than racing it.
        await canvas.findByRole("heading", {
            level: 1,
            name: /Bring your learning together/,
        });

        // The single product screenshot (a genuine capture of the real
        // /courses page, documented in public/CAPTURE.md) replaces any
        // invented feature visuals. (Next.js may serve the asset through
        // its image optimizer, so the URL is checked by containment,
        // not equality.)
        const screenshot = await canvas.findByRole("img", {
            name: /courses workspace/,
        });
        await expect(screenshot.getAttribute("src")).toContain(
            "/courses-preview.png",
        );

        // Honest status list: one heading, three line items labelled
        // Today / In development / Planned in the approved
        // capability-honesty vocabulary.
        await expect(
            await canvas.findByRole("heading", {
                name: "Where the product stands",
            }),
        ).toBeVisible();
        await expect(await canvas.findByText(/Today:/)).toBeVisible();
        await expect(await canvas.findByText(/In development:/)).toBeVisible();
        await expect(await canvas.findByText(/Planned:/)).toBeVisible();

        // No fabricated credibility elements anywhere (numbers,
        // star ratings, logos, or pricing).
        for (const banned of [
            /10,000\+ users/i,
            /trusted by/i,
            /\$.{2,}\/(mo|month)/i,
            /★★/,
        ]) {
            expect(banned.test(canvasElement.innerText)).toBe(false);
        }

        // The footer carries no auth CTAs and no long marketing copy
        // (one short identity line only).
        await expect(
            canvas.getByText("OpenLearn AI · Adaptive Learning Platform"),
        ).toBeVisible();
    },
};
