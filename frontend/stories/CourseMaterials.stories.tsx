import { useEffect } from "react";
import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent, within } from "storybook/test";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import {
    CourseMaterials,
    MaterialProcessControl,
} from "../components/courses/CourseMaterials";
import { authKeys } from "../features/auth/keys";
import { materialKeys } from "../features/materials/keys";
import type {
    Material,
    MaterialPagesResponse,
} from "../features/materials/schemas";
import {
    MATERIAL_EMPTY_PAGE_COPY,
    MATERIAL_FAILED_COPY,
    MATERIAL_NO_PAGES_COPY,
    MATERIAL_PROCESS_REQUESTING_LABEL,
} from "../features/materials/flow";

/**
 * CourseMaterials stories (Batch 4.3; the extracted-text viewer and
 * reprocess states added in Batch 4.5) — the course-detail materials
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
 * Batch 4.5 adds two hermeticity tools for the states a seeded cache
 * cannot express (an in-flight read, a failed read, a pending
 * reprocess request):
 *
 * - **A scoped `crypto.subtle.digest` guard** (the loading/error/
 *   pending stories): the keycloak-js adapter (v26) performs no
 *   network I/O during `init({ onLoad: "check-sso" })` with an object
 *   config — it goes straight to the PKCE code-challenge digest and
 *   then the login redirect. The guard intercepts exactly that
 *   digest: "hang" keeps the request pending forever; "fail" rejects
 *   the init (the token resolves to null and `apiFetch` fails with
 *   its honest 401 BEFORE issuing any request). No navigation, no
 *   network, and NO dependence on what is running on the Keycloak or
 *   API ports — the stories stay deterministic in CI and on the
 *   owner's machine alike. The guard restores itself on unmount (and
 *   releases a hung init so the next story starts clean).
 * - **The presentational `MaterialProcessControl`** (the
 *   retry-budget-exhausted 409 story): the control renders every
 *   state from props — the exact backend detail string the contract
 *   documents for the exhausted budget is presented as the row's
 *   alert, without firing any request.
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

/** The ready material's stored pages — English, Arabic, and a page
 * with no extractable text (all honest contract states). */
const readyMaterialPages: MaterialPagesResponse = {
    material_id: "660e8400-e29b-41d4-a716-446655440200",
    pages: [
        {
            page_number: 1,
            text: "Introduction to Machine Learning. This handout covers the course scope, the assessment plan, and the reading list for the first three weeks.",
        },
        {
            page_number: 2,
            text: "التعلم الآلي هو فرع من الذكاء الاصطناعي يهتم ببناء أنظمة تتعلم من البيانات. يستخدم هذا المساق أمثلة تطبيقية من مجالات متعددة.",
        },
        {
            page_number: 3,
            text: "",
        },
    ],
};

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

/** The scoped keycloak-init guard (see the module doc): intercepts
 * the PKCE code-challenge digest that sits on the adapter's
 * check-sso login path — BEFORE any navigation or request — so the
 * guarded story's request is held pending ("hang") or failed at the
 * token boundary ("fail"). Returns a restore function that also
 * releases a hung init, leaving the module state clean for the next
 * story. */
function installStoryKeycloakGuard(mode: "hang" | "fail"): () => void {
    const originalDigest = crypto.subtle.digest.bind(crypto.subtle);
    let release: (() => void) | null = null;

    crypto.subtle.digest = () =>
        new Promise<ArrayBuffer>((_, reject) => {
            if (mode === "fail") {
                reject(
                    new Error("story guard: keycloak init blocked (fail)"),
                );
                return;
            }
            release = () =>
                reject(
                    new Error("story guard: keycloak init released (hang)"),
                );
        });

    return () => {
        release?.();
        crypto.subtle.digest = originalDigest;
    };
}

/** The stateful demo wrapper (all props optional, so explicit-render
 * stories need no args — the AppShell SidebarDemo convention). */
function MaterialsDemo({
    materials: seeded = materials,
    canUpload = true,
    pagesData,
    keycloakGuard,
    seedMe = true,
}: {
    materials?: Material[];
    canUpload?: boolean;
    /** Seeded page-list window 0 for the ready fixture (hermetic viewer
     * data — no request fires). */
    pagesData?: MaterialPagesResponse;
    /** The scoped keycloak-init guard for the request-level states
     * ("hang" holds the token path pending — usable exactly once per
     * file, the first keycloak touch; "fail" fails the init at the
     * token boundary with the honest 401, and also protects any
     * first touch from the adapter's login redirect). */
    keycloakGuard?: "hang" | "fail";
    /** Seeding the session makes every gated query enabled; leaving it
     * unseeded (the me query then fails fast at the token boundary)
     * keeps the page-list query DISABLED — its honest pending state. */
    seedMe?: boolean;
}) {
    useEffect(() => {
        if (!keycloakGuard) {
            return;
        }
        return installStoryKeycloakGuard(keycloakGuard);
    }, [keycloakGuard]);

    const queryClient = new QueryClient({
        defaultOptions: { queries: { retry: false, staleTime: Infinity } },
    });
    if (seedMe) {
        queryClient.setQueryData(authKeys.me(), me);
    }
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
    if (pagesData) {
        queryClient.setQueryData(
            [
                ...materialKeys.pages(pagesData.material_id),
                0,
            ],
            pagesData,
        );
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

/** Locate a material row by its h3 title (one row per fixture). */
function rowByTitle(canvas: ReturnType<typeof within>, title: string) {
    return canvas
        .getByRole("heading", { level: 3, name: title })
        .closest("li")!;
}

/**
 * The owner's view — the upload affordance renders, and the list
 * shows one entry per contract status with the honest presentation
 * vocabulary (Queued / Processing / Ready / Failed — no fabricated
 * progress, phases, or ETAs).
 *
 * Batch 4.5: the terminal-row action area renders — the reprocess
 * control on BOTH terminal states (failed AND ready) for the owning
 * instructor, the extracted-text viewer disclosure on the ready row
 * only, and neither control on queued/processing rows.
 */
export const OwnerAllStatuses: Story = {
    name: "Owner — all four statuses (terminal-row actions)",
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

        // Batch 4.5 — the viewer disclosure renders ONLY on the
        // ready row.
        const readyRow = rowByTitle(canvas, "Lecture 1 — Course Overview");
        await expect(
            within(readyRow).getByRole("button", { name: "Extracted text" }),
        ).toBeVisible();
        await expect(
            within(readyRow).getByRole("button", { name: "Reprocess" }),
        ).toBeVisible();

        // The reprocess control renders on the FAILED row too (the
        // owner approved both terminal states).
        const failedRow = rowByTitle(
            canvas,
            "Scanned archive (quota-blocked OCR)",
        );
        await expect(
            within(failedRow).getByRole("button", { name: "Reprocess" }),
        ).toBeVisible();
        await expect(
            within(failedRow).queryByRole("button", {
                name: "Extracted text",
            }),
        ).toBeNull();

        // Neither control renders on non-terminal rows.
        const queuedRow = rowByTitle(canvas, "Lecture 3 — Readings");
        await expect(
            within(queuedRow).queryByRole("button", { name: "Reprocess" }),
        ).toBeNull();
        await expect(
            within(queuedRow).queryByRole("button", {
                name: "Extracted text",
            }),
        ).toBeNull();

        const processingRow = rowByTitle(canvas, "Lecture 2 — Slides");
        await expect(
            within(processingRow).queryByRole("button", {
                name: "Reprocess",
            }),
        ).toBeNull();
        await expect(
            within(processingRow).queryByRole("button", {
                name: "Extracted text",
            }),
        ).toBeNull();

        // No fabricated progress anywhere.
        await expect(canvas.queryByText(/%/)).toBeNull();
    },
};

/**
 * The read-only view (a viewer who is not the owning instructor —
 * presentation only; the backend remains the authorization): NO
 * upload or reprocess affordance renders (both are the owner's
 * management actions), while the extracted-text disclosure stays —
 * the viewer reads a ready material's stored pages through the same
 * owner-scoped read the hub itself uses.
 */
export const ViewerReadOnly: Story = {
    name: "Viewer — read-only (no management affordances)",
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

        // No reprocess control for the non-owner (the backend's
        // instructor + ownership rule; presentation mirrors it).
        await expect(
            canvas.queryByRole("button", { name: "Reprocess" }),
        ).toBeNull();

        // The viewer disclosure remains on the ready row.
        const readyRow = rowByTitle(canvas, "Lecture 1 — Course Overview");
        await expect(
            within(readyRow).getByRole("button", { name: "Extracted text" }),
        ).toBeVisible();

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

/* -------------------------------------------------------------------------
 * Batch 4.5 — the extracted-text viewer states.
 * ---------------------------------------------------------------------- */

/**
 * The viewer open on a ready material with multiple stored pages:
 * English and Arabic pages render as labeled blocks with
 * `dir="auto"`, and the page with no extractable text says exactly
 * that. No "Load more pages" appears — the window (3 of a possible
 * 100) came back short, which the contract defines as the last page.
 */
export const TextViewerOpenPages: Story = {
    name: "Viewer — open on a ready material (multi-page, Arabic, empty page)",
    render: () => <MaterialsDemo pagesData={readyMaterialPages} />,
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        const disclosure = canvas.getByRole("button", {
            name: "Extracted text",
        });
        await expect(disclosure).toHaveAttribute("aria-expanded", "false");

        // Lazy disclosure: opening mounts the viewer (and only then
        // would its queries exist — here they read the seeded cache).
        await userEvent.click(disclosure);
        await expect(disclosure).toHaveAttribute("aria-expanded", "true");

        // Pages render as clearly labeled blocks.
        await expect(canvas.getByText("Page 1")).toBeVisible();
        await expect(canvas.getByText("Page 2")).toBeVisible();
        await expect(canvas.getByText("Page 3")).toBeVisible();

        // The Arabic page's text carries dir="auto" so it reads in
        // its own direction under either layout.
        const arabicPage = canvas.getByText(/التعلم الآلي/);
        await expect(arabicPage).toHaveAttribute("dir", "auto");

        // The English page too — every page block applies dir="auto".
        const englishPage = canvas.getByText(/Introduction to Machine Learning/);
        await expect(englishPage).toHaveAttribute("dir", "auto");

        // The page with no extractable text is stated honestly.
        await expect(
            canvas.getByText(MATERIAL_EMPTY_PAGE_COPY),
        ).toBeVisible();

        // Honest pagination: a short window is the last page — no
        // "Load more pages" is offered, and no total is invented.
        await expect(
            canvas.queryByRole("button", { name: /load more pages/i }),
        ).toBeNull();
        await expect(canvas.queryByText(/page 1 of/i)).toBeNull();
    },
};

/**
 * A ready material whose stored page list is empty (the endpoint's
 * honest "empty until processed" answer) — the viewer says exactly
 * that, without inventing content or a cause.
 */
export const TextViewerEmptyList: Story = {
    name: "Viewer — no extracted text stored",
    render: () => (
        <MaterialsDemo
            materials={[materials[0]!]}
            pagesData={{
                material_id: materials[0]!.id,
                pages: [],
            }}
        />
    ),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await userEvent.click(
            canvas.getByRole("button", { name: "Extracted text" }),
        );

        await expect(
            canvas.getByText(MATERIAL_NO_PAGES_COPY),
        ).toBeVisible();
        await expect(canvas.queryByText("Page 1")).toBeNull();
    },
};

/* -------------------------------------------------------------------------
 * Batch 4.5 — the request-level states (reprocess pending, viewer
 * read failed, viewer loading). The keycloak-js module state is shared
 * by every story in this file (one iframe per file), and its singleton
 * initializes exactly once — so these three stories are ORDERED:
 *
 * 1. ReprocessPending — this file's FIRST keycloak touch. The guard's
 *    "hang" mode holds the token path pending, and the REAL clicked
 *    mutation stays in flight ("Requesting…").
 * 2. TextViewerError — after any completed init, the token path
 *    fast-fails with the honest 401 (the guard only protects a first
 *    touch from the login redirect) — the read fails, the shared
 *    ErrorState with retry renders.
 * 3. TextViewerLoading — the session gate holds the page-list query
 *    DISABLED (its honest pending state): the unseeded me query fails
 *    fast at the token boundary, so `me.isSuccess` stays false and
 *    the viewer renders the shared LoadingBlock.
 *
 * Each story is also correct in isolation (a `-t` run makes it the
 * first touch, where the guard supplies the same behavior).
 * ---------------------------------------------------------------------- */

/**
 * The pending reprocess request — the REAL control, clicked in the
 * story: the scoped keycloak guard holds the request open (the
 * adapter's check-sso path never reaches its login redirect), so
 * the disabled "Requesting…" presentation — the duplicate-submit
 * protection itself — is deterministic in every environment.
 */
export const ReprocessPending: Story = {
    name: "Reprocess — request in flight (disabled, Requesting…)",
    render: () => <MaterialsDemo keycloakGuard="hang" />,
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // The READY row's control (the failed row has one too — the
        // story scopes every assertion to its row).
        const readyRow = rowByTitle(canvas, "Lecture 1 — Course Overview");
        await userEvent.click(
            within(readyRow).getByRole("button", { name: "Reprocess" }),
        );

        // Duplicate-submit protection: the control is disabled and
        // its label states exactly what is happening — nothing more.
        const requesting = within(readyRow).getByRole("button", {
            name: MATERIAL_PROCESS_REQUESTING_LABEL,
        });
        await expect(requesting).toBeDisabled();
        await expect(
            within(readyRow).queryByRole("button", { name: "Reprocess" }),
        ).toBeNull();
        await expect(canvas.queryByText(/%/)).toBeNull();

        // The other terminal row's control is untouched by this
        // request (each row owns its own mutation).
        const failedRow = rowByTitle(
            canvas,
            "Scanned archive (quota-blocked OCR)",
        );
        await expect(
            within(failedRow).getByRole("button", { name: "Reprocess" }),
        ).toBeEnabled();
    },
};

/**
 * The viewer's error state — the page-list read failed at the token
 * boundary (the honest 401 of an unauthenticated session; the guarded
 * init never navigates and never issues a request). The shared
 * ErrorState with its retry action renders deterministically in every
 * environment.
 */
export const TextViewerError: Story = {
    name: "Viewer — read failed (retry offered)",
    render: () => <MaterialsDemo keycloakGuard="fail" />,
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await userEvent.click(
            canvas.getByRole("button", { name: "Extracted text" }),
        );

        await expect(await canvas.findByRole("alert")).toBeVisible();
        await expect(
            canvas.getByRole("button", { name: "Try again" }),
        ).toBeVisible();
        // No page content is fabricated for a failed read.
        await expect(canvas.queryByText("Page 1")).toBeNull();
    },
};

/**
 * The viewer's loading state — the page-list read is pending. The
 * session gate holds the query disabled (the unseeded me query fails
 * fast at the token boundary, so the page-list query never enables):
 * the shared LoadingBlock presentation renders — deterministically in
 * every environment, with no navigation and no request.
 */
export const TextViewerLoading: Story = {
    name: "Viewer — loading the extracted text",
    render: () => (
        <MaterialsDemo keycloakGuard="fail" seedMe={false} />
    ),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await userEvent.click(
            canvas.getByRole("button", { name: "Extracted text" }),
        );

        // The shared async-state kit's polite live region, inside the
        // viewer region (the GlobalStates loading-boundary pattern).
        const viewerRegion = canvas
            .getByRole("heading", { level: 4, name: "Extracted text" })
            .closest("section")!;
        await expect(
            within(viewerRegion).getByRole("status"),
        ).toBeVisible();
        await expect(
            canvas.getByText("Loading extracted text..."),
        ).toBeVisible();
    },
};

/**
 * The documented retry-budget-exhausted 409 — the control's error
 * presentation, rendered from the exact backend detail string the
 * contract documents for the exhausted budget ("N of 3 manual
 * retries consumed"). This is the ONLY honest source of
 * retry-budget information: `MaterialResponse` exposes no
 * `retry_count`, so nothing is pre-computed or predicted anywhere.
 */
export const ReprocessBudgetExhausted: Story = {
    name: "Reprocess — retry budget exhausted (documented 409)",
    render: () => (
        <div className="@container mx-auto w-full max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
            <h2 className="mb-5 text-[0.8125rem] font-medium text-muted-foreground">
                Materials
            </h2>
            <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
                <MaterialProcessControl
                    visible
                    pending={false}
                    feedback={{
                        kind: "error",
                        message:
                            "Manual retry budget exhausted (3 of 3 manual retries consumed)",
                    }}
                    onRequest={() => {}}
                />
            </div>
        </div>
    ),
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        await expect(
            canvas.getByRole("button", { name: "Reprocess" }),
        ).toBeEnabled();

        const alert = canvas.getByRole("alert");
        await expect(alert).toHaveTextContent(
            "Manual retry budget exhausted (3 of 3 manual retries consumed)",
        );

        // No invented retry accounting beyond the backend's own
        // message — no counter, no "retries remaining" widget.
        await expect(
            canvas.queryByText(/retries remaining/i),
        ).toBeNull();
    },
};

/**
 * The remaining async states — the materials list's own loading and
 * recoverable error — render through the shared state kit
 * (LoadingBlock `role=status` / ErrorState `role=alert` + retry)
 * exactly as the other async surfaces do; their grammar is pinned by
 * the kit's own stories, and the list-level states cannot be seeded
 * hermetically here (the list mounts before the demo wrapper's cache
 * can express them). The real loading/error/permission paths
 * exercise on the owner's environment through the documented
 * walkthrough.
 */
