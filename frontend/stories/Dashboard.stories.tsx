import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import DashboardPage from "../app/(app)/dashboard/page";
import { authKeys } from "../features/auth/keys";
import { courseKeys } from "../features/courses/keys";
import type { Course } from "../features/courses/schemas";
import { profileKeys } from "../features/profile/keys";
import type { Profile } from "../features/profile/schemas";

/**
 * Dashboard stories (Batch 4.2, Swiss Editorial Grid).
 *
 * The page consumes the real hooks (`useCourses`, `useProfile`,
 * `useMe`, `useUserName`) with their `me.isSuccess` gating, so the
 * stories pre-seed all three query caches with schema-valid fixtures
 * (`staleTime: Infinity` — no network request, no Keycloak
 * initialization inside Storybook; the same hermeticity pattern as
 * the AppShell full-shell story).
 *
 * Batch 4.2 corrections (A3/A4): the greeting is composed as
 * "Welcome back, <Name>!" (exclamation after the name) — pinned
 * here in its no-name fallback "Welcome back!" because Storybook
 * never initializes Keycloak (the personalized variant is pinned by
 * the `composeWelcomeGreeting` unit tests); the Email section is
 * GONE (asserted as an absence — no `Email:` text anywhere on the
 * page), the redundant "Courses" region kicker and the spatially
 * inaccurate "The courses you own. Browse them below." helper are
 * REMOVED, and the recent entries' titles are the links to their
 * hubs (A2).
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

const courses: Course[] = [
    {
        id: "550e8400-e29b-41d4-a716-446655440020",
        owner_id: "550e8400-e29b-41d4-a716-446655440001",
        title: "Introduction to Machine Learning",
        description:
            "A gentle first pass through regression, classification, and evaluation.",
        created_at: "2026-10-21T09:00:00.000Z",
    },
    {
        id: "550e8400-e29b-41d4-a716-446655440021",
        owner_id: "550e8400-e29b-41d4-a716-446655440001",
        title: "أساسيات الذكاء الاصطناعي",
        description: "مدخل شامل إلى مفاهيم التعلم الآلي وتطبيقاتها العملية.",
        created_at: "2026-10-18T14:30:00.000Z",
    },
    {
        id: "550e8400-e29b-41d4-a716-446655440022",
        owner_id: "550e8400-e29b-41d4-a716-446655440001",
        title: "Data Ethics and Society",
        description: null,
        created_at: "2026-10-09T08:00:00.000Z",
    },
    {
        id: "550e8400-e29b-41d4-a716-446655440023",
        owner_id: "550e8400-e29b-41d4-a716-446655440001",
        title: "Statistical Thinking",
        description:
            "From distributions to decisions: estimation, uncertainty, and common traps.",
        created_at: "2026-09-27T11:15:00.000Z",
    },
];

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
    coursesData: Course[],
    profileData: Profile | null,
    ui: React.ReactNode,
) {
    const queryClient = new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: Infinity } },
    });
    queryClient.setQueryData(authKeys.me(), me);
    queryClient.setQueryData(courseKeys.lists(), coursesData);
    queryClient.setQueryData(profileKeys.current(), profileData);
    return (
        <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    );
}

const meta = {
    title: "Pages/Dashboard",
    component: DashboardPage,
    tags: ["autodocs"],
    render: () =>
        withSeededCache(
            courses,
            profileWithTwoMissing,
            <DashboardPage />,
        ),
} satisfies Meta<typeof DashboardPage>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Correction A3: the greeting reads "Welcome back, <Name>!" —
        // the no-name fallback renders the plain "Welcome back!"
        // (the story's Keycloak-free environment), with the
        // exclamation in place and no dangling comma.
        await expect(
            canvas.getByRole("heading", { name: "Welcome back!" }),
        ).toBeVisible();

        // Correction D: the Email section is REMOVED — no `Email:`
        // text renders anywhere on the dashboard.
        await expect(canvas.queryByText(/Email:/)).toBeNull();

        // Correction A4: the redundant "Courses" region kicker is
        // REMOVED (the count numeral + unit already say what the
        // region is) and the spatially inaccurate helper copy is
        // gone — the remaining kickers are Profile and Recently
        // created (the h1→h2→h3 sequence is preserved; the courses
        // region intentionally carries no heading).
        for (const kicker of ["Profile", "Recently created"]) {
            await expect(
                canvas.getByRole("heading", { level: 2, name: kicker }),
            ).toBeVisible();
        }
        await expect(
            canvas.queryByRole("heading", { level: 2, name: "Courses" }),
        ).toBeNull();
        await expect(
            canvas.queryByText("The courses you own. Browse them below."),
        ).toBeNull();

        // The count numeral IS the link to /courses, in the locked
        // wording (singular/plural handled).
        const countLink = canvas.getByRole("link", { name: "4 courses" });
        await expect(countLink).toHaveAttribute("href", "/courses");

        // The locked profile measure, worded exactly as established.
        const profileLink = canvas.getByRole("link", {
            name: "2 of 6 fields left",
        });
        await expect(profileLink).toHaveAttribute("href", "/profile");

        // The four most-recent courses render as h3 entries (the API's
        // DESC order is the fixture order), and (A2) each entry's
        // title is now the link to its hub.
        for (const course of courses) {
            const title = canvas.getByRole("heading", {
                level: 3,
                name: course.title,
            });
            await expect(title).toBeVisible();
            const titleLink = within(title).getByRole("link", {
                name: course.title,
            });
            await expect(titleLink).toHaveAttribute(
                "href",
                `/courses/${course.id}`,
            );
        }

        // The account colophon renders the session's real roles (from
        // the seeded /auth/me data — no hard-coded role wording).
        await expect(canvas.getByText("Role:")).toBeVisible();
        await expect(canvas.getByText("instructor")).toBeVisible();

        // The retired hero/banner chrome stays retired.
        await expect(canvas.queryByText("Dashboard")).toBeNull();
        await expect(
            canvas.queryByText("Manage your courses and keep your profile up to date."),
        ).toBeNull();
    },
};

export const EmptyCourses: Story = {
    render: () =>
        withSeededCache([], profileWithTwoMissing, <DashboardPage />),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Zero courses: the numeral still links to /courses and the
        // established empty-state copy + link-only CTA render.
        await expect(
            canvas.getByRole("link", { name: "0 courses" }),
        ).toBeVisible();
        await expect(
            canvas.getByText("Create your first course to get started."),
        ).toBeVisible();
        await expect(
            canvas.getByText("You don't have any courses yet."),
        ).toBeVisible();
        const cta = canvas.getByRole("link", {
            name: "Create your first course",
        });
        await expect(cta).toHaveAttribute("href", "/courses/new");
    },
};

export const ProfileComplete: Story = {
    render: () => withSeededCache(courses, completeProfile, <DashboardPage />),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // The complete profile renders the locked "Complete" wording.
        await expect(
            canvas.getByRole("link", { name: "Complete" }),
        ).toBeVisible();
        await expect(
            canvas.getByText("All profile fields are filled in."),
        ).toBeVisible();
    },
};
