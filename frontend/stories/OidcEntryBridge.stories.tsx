import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";

import { OidcEntryBridge } from "../components/auth/OidcEntryBridge";
import { AuthStateProvider } from "../lib/auth-context";

/**
 * Auth-entry bridge stories (Batch 4.1 corrective follow-up §C.4).
 *
 * The bridge's auto-redirect branch is NOT storied: it would initiate a
 * real OIDC navigation (and in this offline sandbox render its
 * connecting state forever). What IS pinned here is the branch the
 * product relies on after a Back/cancel/logout return — the explicit
 * manual state, entered through the bridge's real mechanism: a seeded
 * OIDC attempt marker (the same sessionStorage flag the flow writes),
 * plus an injected auth state (`AuthStateProvider` — the real context,
 * deterministic value) so no Keycloak adapter boots.
 *
 * The pinned strings match the E2E suite: "Sign in to your account" /
 * "Sign in with OpenLearn AI" and "Create an account" / "Create
 * account".
 */

function ManualBridge({ mode }: { mode: "login" | "register" }) {
    return (
        <AuthStateProvider value={{ isAuthenticated: false, isLoading: false }}>
            <div className="min-h-svh bg-background text-foreground flex flex-col items-center justify-center p-4">
                <div className="mb-8 text-lg font-bold">OpenLearn AI</div>
                <OidcEntryBridge mode={mode} />
            </div>
        </AuthStateProvider>
    );
}

const meta = {
    title: "Auth/OidcEntryBridge",
    component: ManualBridge,
    tags: ["autodocs"],
    parameters: { layout: "fullscreen" },
} satisfies Meta<typeof ManualBridge>;

export default meta;

type Story = StoryObj<typeof meta>;

export const LoginManualState: Story = {
    args: { mode: "login" },
    loaders: [
        async () => {
            // Seed the real attempt marker BEFORE mount, so the bridge
            // takes its manual branch (an arrival after a Back/cancel).
            window.sessionStorage.setItem("openlearn.oidc-attempt.login", "1");
            return {};
        },
    ],
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            canvas.getByRole("heading", { name: "Sign in to your account" }),
        ).toBeVisible();

        const action = canvas.getByRole("button", {
            name: "Sign in with OpenLearn AI",
        });
        await expect(action).toBeVisible();
        await expect(action).toBeEnabled();
    },
};

export const RegisterManualState: Story = {
    args: { mode: "register" },
    loaders: [
        async () => {
            window.sessionStorage.setItem(
                "openlearn.oidc-attempt.register",
                "1",
            );
            return {};
        },
    ],
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            canvas.getByRole("heading", { name: "Create an account" }),
        ).toBeVisible();

        const action = canvas.getByRole("button", { name: "Create account" });
        await expect(action).toBeVisible();
        await expect(action).toBeEnabled();
    },
};
