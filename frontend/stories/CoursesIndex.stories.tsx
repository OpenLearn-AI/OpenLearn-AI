import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent, within } from "storybook/test";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { CoursesIndex } from "../components/courses/CoursesIndex";
import { authKeys } from "../features/auth/keys";
import { courseKeys } from "../features/courses/keys";
import type { Course } from "../features/courses/schemas";

/**
 * Courses list-pattern stories (Batch 4.2, Swiss Editorial Grid).
 *
 * `CoursesIndex` consumes the real `useCourses` hook (with its
 * `me.isSuccess` gating), so the stories pre-seed the `me` and
 * courses-list query caches exactly like the AppShell full-shell
 * story: `staleTime: Infinity` + schema-valid fixtures, no network
 * request, and therefore no Keycloak initialization inside
 * Storybook.
 *
 * The interaction story pins the FROZEN filter contract at the
 * component layer (the E2E suite does not cover search): the
 * searchbox's accessible name (the visually-hidden label — the fix
 * for the previous placeholder-only defect), the live count line's
 * exact wording per state, the title-OR-description case-insensitive
 * substring semantics, and the no-results message.
 */

// Story-only fixture data — isolated, not imported into production code.
const fixtures: Course[] = [
    {
        id: "550e8400-e29b-41d4-a716-446655440010",
        owner_id: "550e8400-e29b-41d4-a716-446655440001",
        title: "Data Ethics and Society",
        description:
            "Foundations of responsible data use, privacy, and fairness in machine learning.",
        created_at: "2026-10-21T09:00:00.000Z",
    },
    {
        id: "550e8400-e29b-41d4-a716-446655440011",
        owner_id: "550e8400-e29b-41d4-a716-446655440001",
        title: "Introduction to Machine Learning",
        description: null,
        created_at: "2026-10-18T14:30:00.000Z",
    },
    {
        id: "550e8400-e29b-41d4-a716-446655440012",
        owner_id: "550e8400-e29b-41d4-a716-446655440001",
        title: "أساسيات الذكاء الاصطناعي",
        description: "مدخل شامل إلى مفاهيم التعلم الآلي وتطبيقاتها العملية.",
        created_at: "2026-10-09T08:00:00.000Z",
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

function withSeededCache(
    courses: Course[] | null,
    ui: React.ReactNode,
) {
    const queryClient = new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: Infinity } },
    });
    queryClient.setQueryData(authKeys.me(), me);
    if (courses !== null) {
        queryClient.setQueryData(courseKeys.lists(), courses);
    }
    return (
        <QueryClientProvider client={queryClient}>
            {ui}
        </QueryClientProvider>
    );
}

/** The page-level container context the component renders inside
 * (app/(app)/courses/page.tsx wraps CoursesIndex in a
 * `@container` main with this width/padding rhythm — mirrored here
 * so the container-query density and the index-bar layout behave
 * exactly as they do on the real page). */
function inPageContainer(ui: React.ReactNode) {
    return (
        <div className="@container mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            {ui}
        </div>
    );
}

const meta = {
    title: "Courses/CoursesIndex",
    component: CoursesIndex,
    tags: ["autodocs"],
    render: () =>
        withSeededCache(fixtures, inPageContainer(<CoursesIndex />)),
} satisfies Meta<typeof CoursesIndex>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // The search field has a REAL accessible name (the
        // visually-hidden label) — not a placeholder-only control.
        const search = await canvas.findByRole("searchbox", {
            name: "Search courses",
        });

        // Correction A7: the field announces itself as a search
        // control at rest — a "Search courses…" placeholder (and the
        // quiet aria-hidden magnifier pinned in the rendered checks)
        // beside the accessible name.
        await expect(search).toHaveAttribute(
            "placeholder",
            "Search courses…",
        );

        // The live count line states the total at rest.
        await expect(canvas.getByText("3 courses")).toBeVisible();

        // Every entry renders its title as an h2 (the /courses pin).
        for (const course of fixtures) {
            await expect(
                canvas.getByRole("heading", { level: 2, name: course.title }),
            ).toBeVisible();
        }
    },
};

export const SearchInteraction: Story = {
    render: () =>
        withSeededCache(fixtures, inPageContainer(<CoursesIndex />)),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const search = await canvas.findByRole("searchbox", {
            name: "Search courses",
        });

        // Frozen filter semantics: title OR description,
        // case-insensitive substring. "ethics" matches the Data Ethics
        // title (case-insensitive) and nothing else.
        await userEvent.type(search, "ETHICS");
        await expect(canvas.getByText("1 of 3 courses")).toBeVisible();
        await expect(
            canvas.getByRole("heading", {
                level: 2,
                name: "Data Ethics and Society",
            }),
        ).toBeVisible();

        // A query with no matches: the count is honest, the no-results
        // message renders, and NO create CTA appears (the list is not
        // empty — the search is).
        await userEvent.clear(search);
        await userEvent.type(search, "zzz");
        await expect(canvas.getByText("0 of 3 courses")).toBeVisible();
        await expect(
            canvas.getByText("No courses found matching your search."),
        ).toBeVisible();
        await expect(
            canvas.queryByRole("link", { name: "Create your first course" }),
        ).toBeNull();

        // Clearing the query restores the full list.
        await userEvent.clear(search);
        await expect(canvas.getByText("3 courses")).toBeVisible();
        await expect(
            canvas.getByRole("heading", { level: 2, name: "Introduction to Machine Learning" }),
        ).toBeVisible();
    },
};

export const Empty: Story = {
    render: () => withSeededCache([], inPageContainer(<CoursesIndex />)),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Honest empty count + the established empty-state copy and
        // link-only CTA (the real kit's EmptyState, flattened).
        await expect(canvas.getByText("No courses yet")).toBeVisible();
        await expect(
            canvas.getByText("You don't have any courses yet."),
        ).toBeVisible();
        const cta = canvas.getByRole("link", {
            name: "Create your first course",
        });
        await expect(cta).toHaveAttribute("href", "/courses/new");
    },
};
