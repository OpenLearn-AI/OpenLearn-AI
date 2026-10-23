import type { Profile } from "../features/profile/schemas";
import { profileKeys } from "../features/profile/keys";
import { authKeys } from "../features/auth/keys";
import { ProfileSetupWizard } from "../components/onboarding/ProfileSetupWizard";

import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { expect, userEvent, within } from "storybook/test";

/**
 * Onboarding wizard stories (Batch 4.1).
 *
 * The wizard talks to two queries (`useMe`, `useProfile`) and one
 * mutation (`useUpdateProfile`). Hermeticity follows the AppShell
 * story pattern: the story seeds BOTH query caches with schema-valid
 * values and `staleTime: Infinity`, so the hooks resolve from cache
 * and no network request ever runs. The save mutation is never fired
 * in stories (a real `PUT` against the configured API URL would be a
 * live network call) — the save/failure/retry paths are covered by the
 * E2E suite's network-level coverage, and the stories own the
 * step-flow, validation, value-preservation, and prefill contracts.
 */

const me = {
    id: "00000000-0000-4000-8000-000000000001",
    email: "instructor@example.com",
    settings: {},
    roles: ["instructor"],
    keycloak: {
        issuer: "http://localhost:8080/realms/openlearn",
        subject: "storybook-user",
    },
} as const;

const existingProfile: Profile = {
    id: "00000000-0000-4000-8000-000000000010",
    user_id: "00000000-0000-4000-8000-000000000001",
    education_level: "Undergraduate",
    major: "Computer Science",
    preferred_language: "en",
    university: "OpenLearn University",
    learning_style_vark: "Visual",
    daily_available_minutes: 90,
};

function WizardDemo({
    profile,
    onSaved,
}: {
    profile: Profile | null;
    onSaved?: () => void;
}) {
    // Seeded caches: `useMe` and `useProfile` resolve without a single
    // network request (staleTime Infinity — see the AppShell story
    // precedent from Batch 3.3).
    const queryClient = new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: Infinity } },
    });
    queryClient.setQueryData(authKeys.me(), me);
    queryClient.setQueryData(profileKeys.current(), profile);

    return (
        <QueryClientProvider client={queryClient}>
            <div className="min-h-svh bg-background p-6 flex items-start justify-center">
                <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 text-card-foreground shadow-xs">
                    <h1 className="text-2xl font-bold">Set up your profile</h1>
                    <p className="mb-6 mt-1.5 text-sm text-muted-foreground">
                        A few basics so OpenLearn AI fits how you study.
                    </p>
                    <ProfileSetupWizard
                        profile={profile}
                        onSaved={onSaved ?? (() => {})}
                    />
                </div>
            </div>
        </QueryClientProvider>
    );
}

const meta = {
    title: "Onboarding/ProfileSetupWizard",
    component: WizardDemo,
    tags: ["autodocs"],
    parameters: { layout: "fullscreen" },
} satisfies Meta<typeof WizardDemo>;

export default meta;

type Story = StoryObj<typeof meta>;

export const StepOneEmpty: Story = {
    args: { profile: null },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Progress is explicit and honest: step 1 of 3, no fake bar.
        await expect(canvas.getByText(/Step 1 of 3/)).toBeVisible();
        await expect(canvas.getByLabelText("Education Level")).toHaveValue("");
        await expect(canvas.getByLabelText("Major")).toHaveValue("");
    },
};

export const ValidationBlocksEmptyContinue: Story = {
    args: { profile: null },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));

        // Per-step Zod validation from the shared profile schema; the
        // user stays on step 1 with the errors announced via role="alert"
        // (the Field wrapper renders them).
        await expect(
            canvas.getByText("Education level is required"),
        ).toBeVisible();
        await expect(canvas.getByText("Major is required")).toBeVisible();
        await expect(canvas.getByText(/Step 1 of 3/)).toBeVisible();
    },
};

export const ForwardBackPreservesValues: Story = {
    args: { profile: null },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await userEvent.type(
            canvas.getByLabelText("Education Level"),
            "Undergraduate",
        );
        await userEvent.type(canvas.getByLabelText("Major"), "Physics");
        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));

        await expect(canvas.getByText(/Step 2 of 3/)).toBeVisible();

        await userEvent.click(canvas.getByRole("button", { name: "Back" }));

        // Backward navigation never loses entered values (Q3).
        await expect(canvas.getByText(/Step 1 of 3/)).toBeVisible();
        await expect(canvas.getByLabelText("Education Level")).toHaveValue(
            "Undergraduate",
        );
        await expect(canvas.getByLabelText("Major")).toHaveValue("Physics");
    },
};

export const PrefilledFromExistingProfile: Story = {
    // A user with an existing profile (a 200 from GET /v1/users/me)
    // edits instead of erasing: every field starts from the API value.
    args: { profile: existingProfile },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(canvas.getByLabelText("Education Level")).toHaveValue(
            "Undergraduate",
        );
        await expect(canvas.getByLabelText("Major")).toHaveValue(
            "Computer Science",
        );
    },
};

export const ReviewStepShowsAccumulatedPayload: Story = {
    args: { profile: null },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Step 1 → 2
        await userEvent.type(
            canvas.getByLabelText("Education Level"),
            "Undergraduate",
        );
        await userEvent.type(canvas.getByLabelText("Major"), "Physics");
        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));

        // Step 2 → 3 (review). The minutes field starts at the wizard's
        // default "60" — clear it first so the value under test is 90.
        const minutes = canvas.getByLabelText("Daily Available Minutes");
        await userEvent.clear(minutes);
        await userEvent.type(minutes, "90");
        await userEvent.selectOptions(
            canvas.getByLabelText("Preferred Language"),
            "en",
        );
        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));

        await expect(canvas.getByText(/Step 3 of 3/)).toBeVisible();

        // The review lists exactly the values the single full-replacement
        // PUT will carry.
        await expect(
            canvas.getByText("Review your answers"),
        ).toBeVisible();
        await expect(canvas.getByText("Undergraduate")).toBeVisible();
        await expect(canvas.getByText("Physics")).toBeVisible();
        await expect(
            canvas.getByText("90 minutes / day"),
        ).toBeVisible();
        await expect(
            canvas.getByRole("button", { name: "Save profile" }),
        ).toBeVisible();
    },
};
