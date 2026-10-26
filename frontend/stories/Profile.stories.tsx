import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent, within } from "storybook/test";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import ProfilePage from "../app/(app)/profile/page";
import { authKeys } from "../features/auth/keys";
import { profileKeys } from "../features/profile/keys";
import type { Profile } from "../features/profile/schemas";

/**
 * Profile page stories (Batch 4.4, Swiss Editorial Grid).
 *
 * The page consumes the real hooks (`useMe`, `useProfile`,
 * `useUserName`) with their `me.isSuccess` gating, so the stories
 * pre-seed both query caches with schema-valid fixtures
 * (`staleTime: Infinity` — no network request, no Keycloak
 * initialization inside Storybook; the AppShell story's
 * hermeticity pattern). The save mutation is never fired (a real
 * `PUT /v1/users/me` would be a live network call — the same rule
 * as the wizard stories); what IS pinned here is everything the
 * batch owns:
 *
 * - the editorial masthead (display-scale "Profile" h1, the real
 *   identity metadata line) and the retirement of the pre-redesign
 *   language (no gradient banner, no "Account Settings" pill, no
 *   "Need Assistance?" filler — asserted as absences);
 * - the pinned create-vs-edit strings the profile-roundtrip E2E
 *   relies on ("Create Your Profile" / "Personal Information",
 *   "Create Profile" / "Save Changes") in BOTH modes;
 * - the completeness aside on the shared derivation (the same
 *   "N of 6 fields left" measure as the dashboard);
 * - the client-side validation path (Zod `safeParse` fires BEFORE
 *   any mutation — the field `role="alert"` paragraphs, the
 *   `aria-invalid` flags, and the `aria-describedby` associations
 *   are exercised with zero network involvement).
 */

// Story-only fixture data — isolated, not imported into production code.
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

/** Two of the six content fields are empty (the two nullable ones). */
const profileWithTwoMissing: Profile = {
    id: "660e8400-e29b-41d4-a716-446655440030",
    user_id: "00000000-0000-4000-8000-000000000001",
    education_level: "Undergraduate",
    major: "Computer Science",
    preferred_language: "en",
    university: null,
    learning_style_vark: null,
    daily_available_minutes: 60,
};

const completeProfile: Profile = {
    ...profileWithTwoMissing,
    university: "Cairo University",
    learning_style_vark: "Visual",
};

function withSeededCache(
    profileData: Profile | null,
    ui: React.ReactNode,
) {
    const queryClient = new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: Infinity } },
    });
    queryClient.setQueryData(authKeys.me(), me);
    queryClient.setQueryData(profileKeys.current(), profileData);
    return (
        <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    );
}

const meta = {
    title: "Pages/Profile",
    component: ProfilePage,
    tags: ["autodocs"],
    render: () =>
        withSeededCache(profileWithTwoMissing, <ProfilePage />),
} satisfies Meta<typeof ProfilePage>;

export default meta;

type Story = StoryObj<typeof meta>;

/** Edit mode — an existing profile with two fields still empty. */
export const EditMode: Story = {
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Masthead: display-scale title + the real identity line. The
        // seeded `me` carries no name claims, so `useUserName` falls
        // back to the email — the identity line must render the
        // address EXACTLY ONCE (never name-fallback + email both).
        await expect(
            canvas.getByRole("heading", {
                level: 1,
                name: "Profile",
            }),
        ).toBeVisible();
        await expect(
            canvas.getAllByText("instructor@example.com"),
        ).toHaveLength(1);

        // The pre-redesign language is retired (asserted absences).
        await expect(
            canvas.queryByText("Account Settings"),
        ).not.toBeInTheDocument();
        await expect(
            canvas.queryByText("Need Assistance?"),
        ).not.toBeInTheDocument();

        // The pinned edit-mode strings (profile-roundtrip E2E).
        await expect(
            canvas.getByRole("heading", { name: "Personal Information" }),
        ).toBeVisible();
        await expect(
            canvas.getByRole("button", { name: "Save Changes" }),
        ).toBeVisible();

        // All six contract fields render with their labels.
        for (const label of [
            "Education Level",
            "Major",
            "Preferred Language",
            "University",
            "Learning Style (VARK)",
            "Daily Available Minutes",
        ]) {
            await expect(canvas.getByLabelText(label)).toBeVisible();
        }

        // The completeness aside — the same measure as the dashboard.
        await expect(
            canvas.getByText("2 of 6 fields left"),
        ).toBeVisible();
    },
};

/** Create mode — no profile yet (the 404-to-null state). */
export const CreateMode: Story = {
    render: () => withSeededCache(null, <ProfilePage />),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // The pinned create-mode strings (profile-roundtrip E2E).
        await expect(
            canvas.getByRole("heading", {
                name: "Create Your Profile",
            }),
        ).toBeVisible();
        await expect(
            canvas.getByRole("button", { name: "Create Profile" }),
        ).toBeVisible();

        // The aside's honest not-set-up state.
        await expect(canvas.getByText("Not set up")).toBeVisible();

        // No success or error message is present before any submit.
        await expect(canvas.queryByRole("status")).not.toBeInTheDocument();
        await expect(canvas.queryByRole("alert")).not.toBeInTheDocument();
    },
};

/** A complete profile — the aside's terminal state. */
export const CompleteProfile: Story = {
    render: () => withSeededCache(completeProfile, <ProfilePage />),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        await expect(canvas.getByText("Complete")).toBeVisible();
        await expect(
            canvas.getByText("All profile fields are filled in."),
        ).toBeVisible();
    },
};

/**
 * The client-side validation path — Zod runs BEFORE any mutation
 * (no network involvement): required-field errors and the range
 * error surface as associated `role="alert"` paragraphs with
 * `aria-invalid` controls.
 */
export const ValidationErrors: Story = {
    render: () => withSeededCache(profileWithTwoMissing, <ProfilePage />),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Empty the two required text fields and break the range.
        const education = canvas.getByLabelText("Education Level");
        await userEvent.clear(education);
        const major = canvas.getByLabelText("Major");
        await userEvent.clear(major);
        const minutes = canvas.getByLabelText("Daily Available Minutes");
        await userEvent.clear(minutes);
        await userEvent.type(minutes, "0");

        await userEvent.click(
            canvas.getByRole("button", { name: "Save Changes" }),
        );

        // The field errors are announced and associated.
        await expect(
            canvas.getByText("Education level is required"),
        ).toBeVisible();
        await expect(canvas.getByText("Major is required")).toBeVisible();
        await expect(
            canvas.getByText("Daily available minutes must be at least 1"),
        ).toBeVisible();

        await expect(education).toHaveAttribute("aria-invalid", "true");
        await expect(education).toHaveAttribute(
            "aria-describedby",
            "education-level-error",
        );
        await expect(minutes).toHaveAttribute(
            "aria-describedby",
            "daily-available-minutes-error",
        );

        // No success message — the submit never reached the mutation.
        await expect(canvas.queryByRole("status")).not.toBeInTheDocument();
    },
};
