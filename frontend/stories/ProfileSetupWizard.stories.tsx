import type { Profile } from "../features/profile/schemas";
import { profileKeys } from "../features/profile/keys";
import { authKeys } from "../features/auth/keys";
import { ProfileSetupWizard } from "../components/onboarding/ProfileSetupWizard";

import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { expect, userEvent, within } from "storybook/test";

/**
 * Onboarding wizard stories (Batch 4.1; rebuilt for the Batch 4.2
 * public-direction redesign).
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
 *
 * The redesign's structural changes are pinned here: education stage
 * tiles with an honest "Other" free-text input, a genuine multi-select
 * VARK toggle group (the contract field is free text), the interim
 * review step's removal, and the single-sentence step instructions.
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
            <div className="dark min-h-svh bg-background p-6 text-foreground">
                <div className="mx-auto flex w-full max-w-lg flex-col">
                    <h1 className="text-2xl font-bold">Set up your profile</h1>
                    <p className="mb-6 mt-1.5 text-sm text-muted-foreground">
                        Tell us a few basics so OpenLearn AI fits how you
                        study. You can change any of this anytime afterwards.
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

const EDUCATION_GROUP = { name: "Education Level" } as const;
const STYLE_GROUP = { name: "Learning style (optional)" } as const;

export const StepOneEmpty: Story = {
    args: { profile: null },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Progress is explicit and honest: step 1 of 3.
        await expect(canvas.getByText(/Step 1 of 3/)).toBeVisible();

        // Education level: stage tiles, nothing selected yet.
        const education = canvas.getByRole("radiogroup", EDUCATION_GROUP);
        for (const tile of within(education).getAllByRole("radio")) {
            await expect(tile).toHaveAttribute("aria-checked", "false");
        }

        // Major: still an honest text input.
        await expect(canvas.getByLabelText("Major")).toHaveValue("");
    },
};

export const ValidationBlocksEmptyContinue: Story = {
    args: { profile: null },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));

        // Per-step Zod validation from the shared profile schema; the
        // user stays on step 1 with the errors announced via role="alert".
        await expect(
            canvas.getAllByText("Education level is required"),
        ).toHaveLength(1);
        await expect(canvas.getByText("Major is required")).toBeVisible();
        await expect(canvas.getByText(/Step 1 of 3/)).toBeVisible();
    },
};

export const OtherRevealsFreeTextInput: Story = {
    // "Other" keeps the contract honest: a free-text field reveals for
    // education levels outside the canonical tiles; selecting a named
    // stage commits that value immediately.
    args: { profile: null },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            canvas.queryByLabelText("Your education level"),
        ).toBeNull();
        await userEvent.click(
            within(
            canvas.getByRole("radiogroup", EDUCATION_GROUP),
        ).getByRole("radio", { name: "Other" }),
        );
        const custom = canvas.getByLabelText("Your education level");
        await expect(custom).toHaveValue("");

        await userEvent.type(custom, "Vocational training");

        // Switching to a named stage commits its value and hides the
        // free-text input (the stale custom value is never silently
        // kept behind a named tile).
        await userEvent.click(
            within(
            canvas.getByRole("radiogroup", EDUCATION_GROUP),
        ).getByRole("radio", { name: "Undergraduate" }),
        );
        await expect(
            canvas.queryByLabelText("Your education level"),
        ).toBeNull();
        await expect(
            within(
            canvas.getByRole("radiogroup", EDUCATION_GROUP),
        ).getByRole("radio", { name: "Undergraduate" }),
        ).toHaveAttribute("aria-checked", "true");
    },
};

export const ForwardBackPreservesValues: Story = {
    args: { profile: null },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await userEvent.click(
            within(
            canvas.getByRole("radiogroup", EDUCATION_GROUP),
        ).getByRole("radio", { name: "Undergraduate" }),
        );
        await userEvent.type(canvas.getByLabelText("Major"), "Physics");
        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));

        await expect(canvas.getByText(/Step 2 of 3/)).toBeVisible();

        await userEvent.click(canvas.getByRole("button", { name: "Back" }));

        // Backward navigation never loses entered values (Q3).
        await expect(canvas.getByText(/Step 1 of 3/)).toBeVisible();
        await expect(
            within(
            canvas.getByRole("radiogroup", EDUCATION_GROUP),
        ).getByRole("radio", { name: "Undergraduate" }),
        ).toHaveAttribute("aria-checked", "true");
        await expect(canvas.getByLabelText("Major")).toHaveValue("Physics");
    },
};

export const PrefilledFromExistingProfile: Story = {
    // A user with an existing profile (a 200 from GET /v1/users/me)
    // edits instead of erasing: the education stage tile and the
    // learning-style toggles both start from the API value.
    args: { profile: existingProfile },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            within(
            canvas.getByRole("radiogroup", EDUCATION_GROUP),
        ).getByRole("radio", { name: "Undergraduate" }),
        ).toHaveAttribute("aria-checked", "true");
        await expect(canvas.getByLabelText("Major")).toHaveValue(
            "Computer Science",
        );

        // Advance to step 3: the single "Visual" token from the API is
        // the pressed state of the multi-select group.
        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));
        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));
        await expect(canvas.getByText(/Step 3 of 3/)).toBeVisible();
        await expect(
            within(
            canvas.getByRole("group", STYLE_GROUP),
        ).getByRole("button", {
                name: "Visual",
            }),
        ).toHaveAttribute("aria-pressed", "true");
        await expect(
            within(
            canvas.getByRole("group", STYLE_GROUP),
        ).getByRole("button", {
                name: "Aural",
            }),
        ).toHaveAttribute("aria-pressed", "false");

        // A returning user can clear selections; the multi-select
        // stays real (no toggle-or-forget inversion).
        await userEvent.click(
            within(
            canvas.getByRole("group", STYLE_GROUP),
        ).getByRole("button", {
                name: "Kinesthetic",
            }),
        );
        await expect(
            within(
            canvas.getByRole("group", STYLE_GROUP),
        ).getByRole("button", {
                name: "Kinesthetic",
            }),
        ).toHaveAttribute("aria-pressed", "true");
        await expect(
            canvas.getByRole("button", { name: "Clear" }),
        ).toBeVisible();
    },
};

export const CustomProfileTokensRideAlong: Story = {
    // The contract's learning_style_vark is free text: an existing
    // profile may hold values that are NOT one of the four VARK tiles.
    // They ride along unchanged and are submitted back (never
    // silently dropped by a wrong checkbox mapping).
    args: {
        profile: {
            ...existingProfile,
            learning_style_vark: "Visual,Project based",
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));
        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));
        await expect(canvas.getByText(/Step 3 of 3/)).toBeVisible();
        await expect(
            within(
            canvas.getByRole("group", STYLE_GROUP),
        ).getByRole("button", {
                name: "Visual",
            }),
        ).toHaveAttribute("aria-pressed", "true");
    },
};

export const StepTwoTilesSelectChoices: Story = {
    // The tile controls on step 2: finite, contract-backed choices are
    // single-select tiles (the language enum and minute presets); the
    // custom minutes input stays for any value 1 to 1440.
    args: { profile: null },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Advance to step 2.
        await userEvent.click(
            within(
            canvas.getByRole("radiogroup", EDUCATION_GROUP),
        ).getByRole("radio", { name: "Undergraduate" }),
        );
        await userEvent.type(canvas.getByLabelText("Major"), "Physics");
        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));
        await expect(canvas.getByText(/Step 2 of 3/)).toBeVisible();

        // Default selection: the wizard defaults to 60 minutes — the
        // "1 hour" preset tile starts checked.
        await expect(
            canvas.getByRole("radio", { name: "1 hour" }),
        ).toHaveAttribute("aria-checked", "true");

        // Choosing a preset updates the value (the custom input shows
        // the same value — one source of truth).
        await userEvent.click(canvas.getByRole("radio", { name: "30 min" }));
        await expect(
            canvas.getByRole("radio", { name: "30 min" }),
        ).toHaveAttribute("aria-checked", "true");
        await expect(
            canvas.getByRole("radio", { name: "1 hour" }),
        ).toHaveAttribute("aria-checked", "false");
        await expect(
            canvas.getByLabelText("Custom minutes per day"),
        ).toHaveValue(30);

        // A custom value outside the presets clears every tile.
        const custom = canvas.getByLabelText("Custom minutes per day");
        await userEvent.clear(custom);
        await userEvent.type(custom, "75");
        await expect(
            canvas.getByRole("radio", { name: "1 hour" }),
        ).toHaveAttribute("aria-checked", "false");

        // Language is the contract's two-value enum as tiles; Arabic is
        // selectable (and the selection is exclusive).
        await expect(
            canvas.getByRole("radio", { name: "English" }),
        ).toHaveAttribute("aria-checked", "true");
        await userEvent.click(canvas.getByRole("radio", { name: "العربية" }));
        await expect(
            canvas.getByRole("radio", { name: "العربية" }),
        ).toHaveAttribute("aria-checked", "true");
        await expect(
            canvas.getByRole("radio", { name: "English" }),
        ).toHaveAttribute("aria-checked", "false");
    },
};

export const StepThreeOptionalAndMultiStyle: Story = {
    // The interim review step is REMOVED (Batch 4.2): step 3 holds the
    // optional fields, the genuine multi-select learning-style group,
    // and goes straight to the save button.
    args: { profile: null },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Step 1 → 2 → 3.
        await userEvent.click(
            within(
            canvas.getByRole("radiogroup", EDUCATION_GROUP),
        ).getByRole("radio", { name: "High school" }),
        );
        await userEvent.type(canvas.getByLabelText("Major"), "Physics");
        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));
        await userEvent.click(canvas.getByRole("button", { name: "Continue" }));
        await expect(canvas.getByText(/Step 3 of 3/)).toBeVisible();

        // No review panel exists anymore.
        await expect(
            canvas.queryByText("Review your answers"),
        ).toBeNull();

        // Optional university field stays optional.
        await userEvent.type(
            canvas.getByLabelText("University (optional)"),
            "Cairo University",
        );

        // Genuine multi-select for the free-text VARK field.
        await userEvent.click(
            within(canvas.getByRole("group", STYLE_GROUP)).getByRole("button", {
                name: "Visual",
            })
        );
        await userEvent.click(
            within(
            canvas.getByRole("group", STYLE_GROUP),
        ).getByRole("button", {
                name: "Read/Write",
            }),
        );
        await expect(
            within(canvas.getByRole("group", STYLE_GROUP)).getByRole("button", {
                name: "Visual",
            })
        ).toHaveAttribute("aria-pressed", "true");
        await expect(
            within(canvas.getByRole("group", STYLE_GROUP)).getByRole("button", {
                name: "Read/Write",
            })
        ).toHaveAttribute("aria-pressed", "true");
        await expect(
            within(canvas.getByRole("group", STYLE_GROUP)).getByRole("button", {
                name: "Aural",
            })
        ).toHaveAttribute("aria-pressed", "false");
        await expect(canvas.getByText("Pick every style that applies to you.")).toBeVisible();

        // Straight to the save button (no review detour).
        await expect(
            canvas.getByRole("button", { name: "Save profile" }),
        ).toBeVisible();
    },
};
