import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { CourseMaterials } from "../components/courses/CourseMaterials";
import { authKeys } from "../features/auth/keys";
import { materialKeys } from "../features/materials/keys";
import type { Material } from "../features/materials/schemas";
import { MATERIAL_FAILED_COPY } from "../features/materials/flow";

/**
 * CourseMaterials stories (Batch 4.3) — the course-detail materials
 * surface in every state the REAL contract supports, rendered
 * hermetically: the real hooks with seeded query caches (`staleTime:
 * Infinity`), no network, no Keycloak initialization (the same
 * pattern as the Dashboard/CoursesIndex stories — a stateful demo
 * wrapper, because the component takes required props).
 *
 * The per-material status poll never becomes live here (Storybook is
 * Keycloak-free, so the token check ends any poll attempt
 * immediately — the poll's documented unrecoverable-stop path), which
 * keeps these stories deterministic. The live polling behavior is
 * exercised on the owner's environment through the real walkthrough.
 *
 * Story fixtures are MOCKED data for component-state coverage only —
 * clearly labeled as such; no claim of integration coverage is made
 * here.
 */

const courseId = "550e8400-e29b-41d4-a716-446655440100";

/** One material per contract status — the four-value literal set. */
const materials: Material[] = [
    {
        id: "660e8400-e29b-41d4-a716-446655440200",
        course_id: courseId,
        s3_key: `${courseId}/materials/lecture-1-handout.pdf`,
        title: "Lecture 1 — Course Overview",
        status: "ready",
        uploaded_by: "00000000-0000-4000-8000-000000000001",
        created_at: "2026-10-20T09:15:00.000Z",
    },
    {
        id: "660e8400-e29b-41d4-a716-446655440201",
        course_id: courseId,
        s3_key: `${courseId}/materials/lecture-2-slides.pdf`,
        title: "Lecture 2 — Slides",
        status: "processing",
        uploaded_by: "00000000-0000-4000-8000-000000000001",
        created_at: "2026-10-21T10:00:00.000Z",
    },
    {
        id: "660e8400-e29b-41d4-a716-446655440202",
        course_id: courseId,
        s3_key: `${courseId}/materials/lecture-3-readings.pdf`,
        title: "Lecture 3 — Readings",
        status: "pending",
        uploaded_by: "00000000-0000-4000-8000-000000000001",
        created_at: "2026-10-22T11:30:00.000Z",
    },
    {
        id: "660e8400-e29b-41d4-a716-446655440203",
        course_id: courseId,
        s3_key: `${courseId}/materials/scanned-archive.pdf`,
        title: "Scanned archive (quota-blocked OCR)",
        status: "failed",
        uploaded_by: "00000000-0000-4000-8000-000000000001",
        created_at: "2026-10-23T08:45:00.000Z",
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

/** The stateful demo wrapper (all props optional, so explicit-render
 * stories need no args — the AppShell SidebarDemo convention). */
function MaterialsDemo({
    materials: seeded = materials,
    canUpload = true,
}: {
    materials?: Material[];
    canUpload?: boolean;
}) {
    const queryClient = new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: Infinity } },
    });
    queryClient.setQueryData(authKeys.me(), me);
    queryClient.setQueryData(materialKeys.list(courseId), seeded);
    // Seed the per-material status polls too, so mounting a
    // non-terminal row never starts a REAL request inside Storybook
    // (hermeticity): the seeded status equals the list snapshot, so
    // the poll has fresh data on mount and nothing fetches. The
    // interval only exists while the story stays mounted — each test
    // run completes well inside one 5s cadence, and unmounting the
    // story clears the interval with it.
    for (const material of seeded) {
        queryClient.setQueryData(materialKeys.status(material.id), {
            material_id: material.id,
            status: material.status,
        });
    }

    return (
        <QueryClientProvider client={queryClient}>
            {/* The page-level frame the component renders inside on
                the hub. */}
            <div className="@container mx-auto w-full max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
                <h2 className="mb-5 text-[0.8125rem] font-medium text-muted-foreground">
                    Materials
                </h2>
                <CourseMaterials courseId={courseId} canUpload={canUpload} />
            </div>
        </QueryClientProvider>
    );
}

const meta = {
    title: "Courses/CourseMaterials",
    component: MaterialsDemo,
    tags: ["autodocs"],
    render: () => <MaterialsDemo />,
} satisfies Meta<typeof MaterialsDemo>;

export default meta;

type Story = StoryObj<typeof meta>;

/**
 * The owner's view — the upload affordance renders, and the list
 * shows one entry per contract status with the honest presentation
 * vocabulary (Queued / Processing / Ready / Failed — no fabricated
 * progress, phases, or ETAs).
 */
export const OwnerAllStatuses: Story = {
    name: "Owner — all four statuses",
    render: () => <MaterialsDemo />,
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // The upload affordance (title + file + submit).
        await expect(
            canvas.getByLabelText("Material title"),
        ).toBeVisible();
        await expect(canvas.getByLabelText("File")).toBeVisible();
        await expect(
            canvas.getByRole("button", { name: /upload material/i }),
        ).toBeVisible();

        // Every status label renders from the contract vocabulary.
        for (const label of ["Ready", "Processing", "Queued", "Failed"]) {
            await expect(canvas.getByText(label)).toBeVisible();
        }

        // The failed row carries the honest failure copy naming the
        // plausible cause class — never the exact cause.
        await expect(
            canvas.getByText(MATERIAL_FAILED_COPY, { exact: false }),
        ).toBeVisible();

        // No fabricated progress, retry, or reprocess affordances.
        await expect(
            canvas.queryByRole("button", { name: /retry|reprocess/i }),
        ).toBeNull();
        await expect(canvas.queryByText(/%/)).toBeNull();
    },
};

/**
 * The read-only view (a viewer who is not the owning instructor —
 * presentation only; the backend remains the authorization): NO
 * upload affordance renders, the list reads the same.
 */
export const ViewerReadOnly: Story = {
    name: "Viewer — read-only (no upload affordance)",
    render: () => <MaterialsDemo canUpload={false} />,
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            canvas.queryByLabelText("Material title"),
        ).toBeNull();
        await expect(canvas.queryByLabelText("File")).toBeNull();
        await expect(
            canvas.queryByRole("button", { name: /upload material/i }),
        ).toBeNull();

        // The list itself still renders.
        await expect(
            canvas.getByText("Lecture 1 — Course Overview"),
        ).toBeVisible();
    },
};

/** An empty course — the honest "no materials yet" state. */
export const Empty: Story = {
    name: "Owner — no materials yet",
    render: () => <MaterialsDemo materials={[]} />,
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            canvas.getByText("No materials in this course yet."),
        ).toBeVisible();
        // The upload affordance stays available in the empty state.
        await expect(
            canvas.getByRole("button", { name: /upload material/i }),
        ).toBeVisible();
    },
};

/**
 * The remaining async states — loading and the recoverable list
 * error — render through the shared state kit (LoadingBlock
 * `role=status` / ErrorState `role=alert` + retry) exactly as the
 * other async surfaces do; their grammar is pinned by the kit's own
 * stories, and they cannot be seeded hermetically here (Storybook is
 * Keycloak-free by design, so no authenticated request can be made
 * to fail). The real loading/error/permission paths exercise on the
 * owner's environment through the documented walkthrough.
 */
