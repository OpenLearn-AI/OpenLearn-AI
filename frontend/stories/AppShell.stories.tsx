import { useState } from "react";

import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, userEvent, waitFor, within } from "storybook/test";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { AppSidebar } from "../components/shell/AppSidebar";
import { MobileNav } from "../components/shell/MobileNav";
import { AppShell } from "../components/shell/AppShell";
import { authKeys } from "../features/auth/keys";

/**
 * Application-shell stories (Batch 3.3 + follow-up).
 *
 * The sidebar and mobile navigation are presentational and receive
 * their data via props, so the stories exercise the real component
 * markup: expanded/collapsed desktop states, the current-route
 * treatment (aria-current + indicator + tint), icon-only accessible
 * naming, the tooltip behavior, and the mobile modal drawer's
 * open/close/navigation contract. The expanded and drawer stories
 * also pin the final navigation inventory (Batch 3.3 follow-up owner
 * IA decision: the public landing `/` is not a protected-navigation
 * destination; the brand identity link remains, outside the nav list).
 *
 * Hermeticity: every story tree is wrapped in a QueryClientProvider
 * (LogoutButton reads the query client context). The full-shell story
 * pre-seeds the `authKeys.me()` cache with a schema-valid user and
 * sets `staleTime: Infinity`, so `useMe` resolves from cache and NO
 * network request — and therefore no Keycloak initialization — ever
 * runs inside Storybook (a live init would attempt an OIDC redirect).
 */

const user = {
    name: "instructor@example.com",
    initial: "I",
    me: {
        id: "00000000-0000-4000-8000-000000000001",
        email: "instructor@example.com",
        settings: {},
        roles: ["instructor"],
        keycloak: {
            issuer: "http://localhost:8080/realms/openlearn",
            subject: "storybook-user",
        },
    },
} as const;

function withQueryClient(ui: React.ReactNode, client?: QueryClient) {
    const queryClient =
        client ??
        new QueryClient({
            defaultOptions: { queries: { retry: false } },
        });
    return (
        <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    );
}

/**
 * Stateful demo wrapper (the AlertDialogDemo pattern): the collapse
 * toggle is a controlled prop on the real component, so the
 * interaction story owns the state here exactly like AppShell does.
 */
function SidebarDemo({
    initialCollapsed = false,
    pathname = "/dashboard",
}: {
    initialCollapsed?: boolean;
    pathname?: string;
}) {
    const [collapsed, setCollapsed] = useState(initialCollapsed);
    return withQueryClient(
        <AppSidebar
            collapsed={collapsed}
            pathname={pathname}
            userName={user.name}
            userInitial={user.initial}
            onToggleCollapsed={() => setCollapsed((v) => !v)}
        />,
    );
}

function MobileDemo({ pathname = "/dashboard" }: { pathname?: string }) {
    return withQueryClient(
        <div className="min-h-svh bg-background">
            <MobileNav
                pathname={pathname}
                userName={user.name}
                userInitial={user.initial}
            />
            <main className="p-6 text-sm text-muted-foreground">
                Page content renders beneath the mobile top bar.
            </main>
        </div>,
    );
}

const meta = {
    title: "Shell/AppShell",
    component: SidebarDemo,
    tags: ["autodocs"],
} satisfies Meta<typeof SidebarDemo>;

export default meta;

type Story = StoryObj<typeof meta>;

export const SidebarExpanded: Story = {
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Final navigation inventory (Batch 3.3 follow-up): exactly the
        // three protected destinations, in order — the public landing
        // (`/`) is not a sidebar entry.
        const nav = await canvas.findByRole(
            "navigation",
            { name: "Primary navigation" },
            { timeout: 5000 },
        );
        const navLinks = within(nav).getAllByRole("link");
        await expect(
            navLinks.map((link) => link.textContent),
        ).toEqual(["Courses", "Dashboard", "Profile & Settings"]);
        await expect(
            within(nav).queryByRole("link", { name: "Home" }),
        ).not.toBeInTheDocument();

        // The brand identity link remains — outside the nav list, still
        // targeting the public landing as the legacy Navbar's did.
        const brand = canvas.getByRole("link", { name: /OpenLearn AI/ });
        await expect(brand).toHaveAttribute("href", "/");

        // Expanded: visible text label + aria-current on the active item.
        const dashboardLink = within(nav).getByRole("link", {
            name: "Dashboard",
        });
        await expect(dashboardLink).toHaveAttribute("aria-current", "page");
    },
};

export const SidebarCollapsed: Story = {
    args: { initialCollapsed: true },
};

export const SidebarNestedRouteActive: Story = {
    // On /courses/<id> the Courses item stays the single current item.
    args: { pathname: "/courses/course-123" },
};

export const SidebarCollapseInteraction: Story = {
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Expanded: visible text label + aria-current on the active item.
        const dashboardLink = await canvas.findByRole(
            "link",
            { name: "Dashboard" },
            { timeout: 5000 },
        );
        await expect(dashboardLink).toHaveAttribute("aria-current", "page");

        // Collapse: the toggle exposes its state via aria-expanded and
        // flips to the expand action.
        const collapse = canvas.getByRole("button", {
            name: "Collapse sidebar",
        });
        await expect(collapse).toHaveAttribute("aria-expanded", "true");
        await userEvent.click(collapse);

        // Collapsed: labels become visually hidden but keep their
        // accessible names; the toggle now reads "Expand sidebar".
        await waitFor(() => {
            expect(
                canvas.queryByRole("button", { name: "Collapse sidebar" }),
            ).not.toBeInTheDocument();
        });
        const stillNamed = canvas.getByRole("link", { name: "Dashboard" });
        await expect(stillNamed.querySelector(".sr-only")).not.toBeNull();
        await expect(stillNamed).toHaveAttribute("aria-current", "page");

        const expand = canvas.getByRole("button", {
            name: "Expand sidebar",
        });
        await expect(expand).toHaveAttribute("aria-expanded", "false");

        // Icon-only account controls keep their accessible names.
        await expect(
            canvas.getByRole("button", { name: "Logout" }),
        ).toBeInTheDocument();
        await expect(
            canvas.getByRole("button", { name: "Toggle theme" }),
        ).toBeInTheDocument();

        // Expand again restores the visible labels.
        await userEvent.click(expand);
        await waitFor(() => {
            expect(
                canvas.getByRole("button", { name: "Collapse sidebar" }),
            ).toBeInTheDocument();
        });
        await canvas.findByRole("link", { name: "Dashboard" });
    },
};

/**
 * Mobile navigation stories, rendered at the smallest supported
 * viewport class (375px) where the mobile top bar is visible. The
 * component owns its Dialog state, so the open/close flows are
 * exercised in the interaction story.
 */
export const MobileBar: Story = {
    render: () => <MobileDemo />,
    parameters: {
        // `default` drives the Storybook UI; `defaultViewport` is the
        // key the addon-vitest test runner reads for CDP emulation.
        viewport: { default: "mobile1", defaultViewport: "mobile1" },
    },
};

export const MobileNavInteraction: Story = {
    render: () => <MobileDemo pathname="/courses" />,
    parameters: {
        // `default` drives the Storybook UI; `defaultViewport` is the
        // key the addon-vitest test runner reads for CDP emulation.
        viewport: { default: "mobile1", defaultViewport: "mobile1" },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        // The drawer portals into the story iframe's document — all
        // drawer queries go through the canvas element's ownerDocument.
        const body = within(canvasElement.ownerDocument.body);

        // Open via the visible, accessible trigger.
        const trigger = await canvas.findByRole(
            "button",
            { name: "Open menu" },
            { timeout: 5000 },
        );
        await userEvent.click(trigger);

        // The modal drawer is open with text-labeled navigation. The
        // pathname is /courses, so Courses carries aria-current.
        const dialog = (await body.findAllByRole("dialog"))[0];
        await expect(dialog).toBeInTheDocument();
        await expect(
            within(dialog).getByRole("heading", { name: "Menu" }),
        ).toBeInTheDocument();

        // Same final inventory as the desktop sidebar — one shared
        // source of truth; no Home entry in the drawer either.
        const drawerLinks = within(dialog).getAllByRole("link");
        await expect(
            drawerLinks.map((link) => link.textContent),
        ).toEqual(["Courses", "Dashboard", "Profile & Settings"]);
        await expect(
            within(dialog).queryByRole("link", { name: "Home" }),
        ).not.toBeInTheDocument();

        const coursesLink = within(dialog).getByRole("link", {
            name: "Courses",
        });
        await expect(coursesLink).toHaveAttribute("aria-current", "page");

        // Account actions are present in the drawer.
        await expect(
            within(dialog).getByRole("button", { name: "Logout" }),
        ).toBeInTheDocument();

        // Explicit close affordance closes the drawer.
        await userEvent.click(
            within(dialog).getByRole("button", { name: "Close menu" }),
        );
        await waitFor(
            () => expect(body.queryAllByRole("dialog")).toHaveLength(0),
            { timeout: 5000 },
        );

        // Reopen and navigate: selecting a link navigates AND closes.
        const reopenTrigger = await canvas.findByRole(
            "button",
            { name: "Open menu" },
            { timeout: 5000 },
        );
        await userEvent.click(reopenTrigger);
        const reopened = (await body.findAllByRole("dialog"))[0];
        await userEvent.click(
            within(reopened).getByRole("link", { name: "Courses" }),
        );
        await waitFor(
            () => expect(body.queryAllByRole("dialog")).toHaveLength(0),
            { timeout: 5000 },
        );

        // Reopen and press Escape: keyboard dismissal closes the drawer
        // (Base UI's documented modal behavior).
        const escapeTrigger = await canvas.findByRole(
            "button",
            { name: "Open menu" },
            { timeout: 5000 },
        );
        await userEvent.click(escapeTrigger);
        const escapeDialog = (await body.findAllByRole("dialog"))[0];
        await expect(escapeDialog).toBeInTheDocument();
        await userEvent.keyboard("{Escape}");
        await waitFor(
            () => expect(body.queryAllByRole("dialog")).toHaveLength(0),
            { timeout: 5000 },
        );
    },
};

/**
 * Full-shell smoke story: AppShell as the (app) layout renders it —
 * QueryClient provider, the me-query cache pre-seeded with a valid
 * user (staleTime: Infinity — nothing is fetched at test time), and
 * the framework's next/navigation mock for the pathname.
 */
export const ShellDesktop: Story = {
    render: () => {
        const queryClient = new QueryClient({
            defaultOptions: { queries: { retry: false, staleTime: Infinity } },
        });
        queryClient.setQueryData(authKeys.me(), user.me);
        return withQueryClient(
            <AppShell>
                <main className="mx-auto w-full max-w-7xl px-4 py-8 text-sm text-muted-foreground sm:px-6 lg:px-8">
                    Page content renders in the shell&apos;s content column.
                </main>
            </AppShell>,
            queryClient,
        );
    },
    parameters: {
        nextjs: {
            appDirectory: true,
            navigation: { pathname: "/dashboard" },
        },
    },
};
