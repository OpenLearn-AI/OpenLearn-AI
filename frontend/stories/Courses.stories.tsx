import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import CoursesPage from "../app/(app)/courses/page";
import { authKeys } from "../features/auth/keys";
import { courseKeys } from "../features/courses/keys";
import type { Course } from "../features/courses/schemas";

/**
 * Courses page story (Batch 4.2) — pins the MASTHEAD contract the
 * courses-crud E2E spec depends on (the "Courses & Learning Hub"
 * heading and the "+ Create New Course" primary action), together
 * with the list pattern rendering underneath from seeded caches
 * (the same hermeticity pattern as the CoursesIndex stories: real
 * hooks, seeded queries, no network, no Keycloak initialization).
 *
 * The list-pattern behavior itself (search semantics, count line,
 * states) is pinned by the CoursesIndex stories.
 */

// Story-only fixture data — isolated, not imported into production code.
const courses: Course[] = [
    {
        id: "550e8400-e29b-41d4-a716-446655440040",
        owner_id: "550e8400-e29b-41d4-a716-446655440001",
        title: "Introduction to Machine Learning",
        description:
            "A gentle first pass through regression, classification, and evaluation.",
        created_at: "2026-10-21T09:00:00.000Z",
    },
    {
        id: "550e8400-e29b-41d4-a716-446655440041",
        owner_id: "550e8400-e29b-41d4-a716-446655440001",
        title: "أساسيات الذكاء الاصطناعي",
        description: null,
        created_at: "2026-10-18T14:30:00.000Z",
    },
];

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

const meta = {
    title: "Pages/Courses",
    component: CoursesPage,
    tags: ["autodocs"],
    render: () => {
        const queryClient = new QueryClient({
            defaultOptions: { queries: { retry: false, staleTime: Infinity } },
        });
        queryClient.setQueryData(authKeys.me(), me);
        queryClient.setQueryData(courseKeys.lists(), courses);
        return (
            <QueryClientProvider client={queryClient}>
                <CoursesPage />
            </QueryClientProvider>
        );
    },
} satisfies Meta<typeof CoursesPage>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // The pinned page heading and the honest subtitle (typographic
        // apostrophe — the rendered copy uses &rsquo;).
        await expect(
            canvas.getByRole("heading", {
                level: 1,
                name: "Courses & Learning Hub",
            }),
        ).toBeVisible();
        await expect(
            canvas.getByText("Courses you’ve created."),
        ).toBeVisible();

        // The primary action: a LINK with the pinned accessible name
        // and the existing creation route — the app's filled primary
        // button grammar, visibly prioritized in the masthead.
        const cta = canvas.getByRole("link", { name: "+ Create New Course" });
        await expect(cta).toHaveAttribute("href", "/courses/new");

        // The list pattern renders underneath from the seeded cache.
        await expect(canvas.getByText("2 courses")).toBeVisible();
        for (const course of courses) {
            await expect(
                canvas.getByRole("heading", { level: 2, name: course.title }),
            ).toBeVisible();
        }

        // The retired over-promising subtitle is gone (D10 — the
        // materials/RAG wording promised Batch 4.3 surfaces).
        await expect(
            canvas.queryByText(/RAG knowledge bases/i),
        ).toBeNull();
    },
};
