import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import CourseDetailPage from "../app/(app)/courses/[id]/page";
// The dynamic-segment page reads `useParams().id`. Two Storybook
// pipelines resolve `next/navigation` differently, and the story
// provides the fixture id through BOTH mechanisms (Storybook-only;
// the application is untouched):
// - the STATIC build (build-storybook) serves the REAL next/navigation,
//   whose useParams reads the framework RouterDecorator's AppRouter/
//   PathParams contexts — fed from `parameters.nextjs.navigation.segments`
//   below;
// - the vitest storybook runner serves the aliased local stub
//   (.storybook/main.ts), whose useParams ignores contexts — fed via
//   the guarded `setStorybookParams` call in `withSeededCache`.
import * as storybookNavigation from "next/navigation";
import { authKeys } from "../features/auth/keys";
import type { Me } from "../features/auth/schemas";
import { courseKeys } from "../features/courses/keys";
import type { Course } from "../features/courses/schemas";
import { materialKeys } from "../features/materials/keys";
import type { Material } from "../features/materials/schemas";

/**
 * Course-detail hub stories (Batch 4.3) — the content hub page with
 * its real hooks (`useCourse`, `useMe`, `useMaterials`) reading
 * seeded caches (`staleTime: Infinity` — no network, no Keycloak; the
 * same hermeticity pattern as the Dashboard stories).
 *
 * The plays pin the hub contract the courses-crud E2E spec depends
 * on — the h1 course title, the "Description" h2 section, the
 * "Edit Course" action — together with the Batch 4.3 surfaces: the
 * materials region, the role-aware action visibility, and the
 * NO-PLACEHOLDER rule (nothing renders for the future hub slots).
 *
 * Story fixtures are MOCKED data for component-state coverage only;
 * the real material journey is exercised on the owner's environment.
 */

const courseId = "550e8400-e29b-41d4-a716-446655440100";

const course: Course = {
    id: courseId,
    owner_id: "00000000-0000-4000-8000-000000000001",
    title: "Introduction to Machine Learning",
    description:
        "A gentle first pass through regression, classification, and evaluation.",
    created_at: "2026-10-21T09:00:00.000Z",
};

const ownerMe: Me = {
    id: "00000000-0000-4000-8000-000000000001",
    email: "instructor@example.com",
    settings: {},
    roles: ["instructor"],
    keycloak: {
        issuer: "http://localhost:8080/realms/openlearn",
        subject: "storybook-user",
    },
};

/** A different authenticated identity (not the owner). */
const viewerMe: Me = {
    ...ownerMe,
    id: "00000000-0000-4000-8000-000000000002",
};

const materials: Material[] = [
    {
        id: "660e8400-e29b-41d4-a716-446655440210",
        course_id: courseId,
        s3_key: `${courseId}/materials/lecture-1-handout.pdf`,
        title: "Lecture 1 — handout",
        status: "ready",
        uploaded_by: "00000000-0000-4000-8000-000000000001",
        created_at: "2026-10-20T09:15:00.000Z",
    },
    {
        id: "660e8400-e29b-41d4-a716-446655440211",
        course_id: courseId,
        s3_key: `${courseId}/materials/lecture-2-slides.pdf`,
        title: "Lecture 2 — slides",
        status: "processing",
        uploaded_by: "00000000-0000-4000-8000-000000000001",
        created_at: "2026-10-21T10:00:00.000Z",
    },
];

/** The stub's setter — present only where the alias resolves
 * (tsc sees the REAL next/navigation types, which lack it). */
const setStorybookParams = (
    storybookNavigation as unknown as {
        setStorybookParams?: (params: Record<string, string>) => void;
    }
).setStorybookParams;

/** The static-build mechanism: the nextjs framework's RouterDecorator
 * feeds `navigation.segments` into the REAL AppRouter/PathParams
 * contexts, so the real useParams() resolves the fixture id. */
const parameters = {
    nextjs: {
        appDirectory: true,
        navigation: {
            pathname: `/courses/${courseId}`,
            segments: [["id", courseId]] as [string, string][],
        },
    },
};

function withSeededCache(
    meData: Me,
    courseData: Course | null,
    materialsData: Material[] | null,
    ui: React.ReactNode,
) {
    const queryClient = new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: Infinity } },
    });
    queryClient.setQueryData(authKeys.me(), meData);
    // Seed whichever mechanism this pipeline resolves.
    if (typeof setStorybookParams === "function") {
        setStorybookParams({ id: courseData?.id ?? courseId });
    }
    if (courseData) {
        queryClient.setQueryData(
            courseKeys.detail(courseData.id),
            courseData,
        );
    }
    if (materialsData) {
        queryClient.setQueryData(
            materialKeys.list(courseData?.id ?? courseId),
            materialsData,
        );
        // Seed the per-material status polls as well (hermeticity —
        // see the CourseMaterials stories' note): a mounted
        // non-terminal row never starts a real request here.
        for (const material of materialsData) {
            queryClient.setQueryData(
                materialKeys.status(material.id),
                {
                    material_id: material.id,
                    status: material.status,
                },
            );
        }
    }
    return (
        <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    );
}

const meta = {
    title: "Pages/CourseDetail",
    component: CourseDetailPage,
    tags: ["autodocs"],
    parameters,
    render: () =>
        withSeededCache(
            ownerMe,
            course,
            materials,
            <CourseDetailPage />,
        ),
} satisfies Meta<typeof CourseDetailPage>;

export default meta;

type Story = StoryObj<typeof meta>;

/** The owning instructor's hub — the full management view. */
export const OwnerHub: Story = {
    name: "Owner — hub with materials",
    render: () =>
        withSeededCache(ownerMe, course, materials, <CourseDetailPage />),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // The pinned hub identity: the course title is the h1.
        await expect(
            canvas.getByRole("heading", {
                level: 1,
                name: "Introduction to Machine Learning",
            }),
        ).toBeVisible();

        // The back-to-index link.
        const back = canvas.getByRole("link", { name: "All courses" });
        await expect(back).toHaveAttribute("href", "/courses");

        // The "Description" h2 section renders the real description
        // (the courses-crud E2E pin).
        await expect(
            canvas.getByRole("heading", { level: 2, name: "Description" }),
        ).toBeVisible();
        await expect(
            canvas.getByText(
                "A gentle first pass through regression, classification, and evaluation.",
            ),
        ).toBeVisible();

        // The Materials region renders the seeded list, with the
        // upload affordance for the owning instructor.
        await expect(
            canvas.getByRole("heading", { level: 2, name: "Materials" }),
        ).toBeVisible();
        await expect(
            canvas.getByRole("heading", { level: 3, name: "Lecture 1 — handout" }),
        ).toBeVisible();
        await expect(canvas.getByText("Ready")).toBeVisible();
        await expect(canvas.getByText("Processing")).toBeVisible();
        await expect(
            canvas.getByLabelText("Material title"),
        ).toBeVisible();

        // The role-aware management actions (E2E pins).
        const edit = canvas.getByRole("link", { name: "Edit Course" });
        await expect(edit).toHaveAttribute(
            "href",
            `/courses/${courseId}/edit`,
        );
        await expect(
            canvas.getByRole("button", { name: "Delete Course" }),
        ).toBeVisible();

        // The NO-PLACEHOLDER rule (roadmap Section 9): the future
        // hub slots render NOTHING.
        for (const forbidden of [
            /coming soon/i,
            /extracted text/i,
            /knowledge base/i,
            /chat/i,
            /enroll/i,
            /citation/i,
        ]) {
            await expect(canvas.queryByText(forbidden)).toBeNull();
        }
        await expect(
            canvas.queryByRole("button", { name: /disabled|placeholder/i }),
        ).toBeNull();
    },
};

/**
 * A non-owning viewer's hub — presentation only (the backend's
 * owner-scoped course read keeps real students off this page; this
 * story pins the role-aware presentation): no management actions, no
 * upload affordance, the content regions read the same.
 */
export const ViewerHub: Story = {
    name: "Viewer — read-only hub",
    render: () =>
        withSeededCache(viewerMe, course, materials, <CourseDetailPage />),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            canvas.getByRole("heading", {
                level: 1,
                name: "Introduction to Machine Learning",
            }),
        ).toBeVisible();

        // No management actions for the non-owner.
        await expect(
            canvas.queryByRole("link", { name: "Edit Course" }),
        ).toBeNull();
        await expect(
            canvas.queryByRole("button", { name: "Delete Course" }),
        ).toBeNull();
        await expect(
            canvas.queryByLabelText("Material title"),
        ).toBeNull();

        // The materials list still reads.
        await expect(
            canvas.getByRole("heading", { level: 3, name: "Lecture 1 — handout" }),
        ).toBeVisible();
    },
};

/** A course without a description — the honest absence. */
export const NoDescription: Story = {
    name: "Owner — course without a description",
    render: () =>
        withSeededCache(
            ownerMe,
            { ...course, description: null },
            [],
            <CourseDetailPage />,
        ),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            canvas.getByText("No description."),
        ).toBeVisible();
        await expect(
            canvas.getByText("No materials in this course yet."),
        ).toBeVisible();
    },
};
