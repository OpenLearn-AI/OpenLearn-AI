"use client";

import { useState, type ReactNode } from "react";
import { usePathname } from "next/navigation";

import { useUserName } from "@/features/auth/useUserName";
import { AppSidebar } from "./AppSidebar";
import { MobileNav } from "./MobileNav";

/**
 * Shared protected application shell (Batch 3.3).
 *
 * Replaces the legacy top Navbar as the primary navigation for the
 * `(app)` route group. One shared composition — rendered once in
 * `app/(app)/layout.tsx` — provides:
 *
 * - Desktop (md+): a collapsible sidebar (expanded ⇄ collapsed) with
 *   primary navigation, the current-route treatment, and an account
 *   region (identity, ThemeToggle, Logout, collapse control).
 * - Mobile (<md): a compact top bar (brand, ThemeToggle, menu
 *   trigger) and a modal off-canvas navigation drawer.
 * - A content column whose width reflows with the sidebar state.
 *
 * Batch 4.2 correction C: the shared bottom footer ("OpenLearn AI
 * Adaptive Learning Platform") is REMOVED — the owner does not
 * want a persistent branding bar anywhere. The content column now
 * ends with the page content; no replacement branding element was
 * added, and nothing else in the shell (skip link, sidebar, mobile
 * nav, main-content focus behavior) changed.
 *
 * Responsibility boundaries: the shell owns navigation and account
 * placement only — page content keeps its own layout and containers.
 * Auth remains owned by `AuthGuard` (which wraps this shell in the
 * `(app)` layout, position and behavior unchanged), so the shell
 * renders only where a protected, authenticated context already
 * exists and never leaks to public routes.
 *
 * Sidebar state persistence (the batch's recorded decision): the
 * expanded/collapsed preference lives in this component's React
 * state. The `(app)` layout is persistent across client-side
 * navigations, so the state survives route changes without resets.
 * Reload persistence was deliberately left out of scope: the
 * repository has no existing storage-persistence convention to
 * reuse, a post-hydration `localStorage` sync would flash a visibly
 * incorrect shell between the server-rendered and restored states,
 * and the batch rules forbid adding a storage framework or a
 * hydration-risky mechanism for a low-stakes preference.
 */
export function AppShell({ children }: { children: ReactNode }) {
    const [collapsed, setCollapsed] = useState(false);
    const pathname = usePathname();
    const { name, initial } = useUserName();

    return (
        <div className="flex min-h-svh w-full">
            <AppSidebar
                collapsed={collapsed}
                pathname={pathname}
                userName={name}
                userInitial={initial}
                onToggleCollapsed={() => setCollapsed((v) => !v)}
            />

            <div className="flex min-w-0 flex-1 flex-col">
                <MobileNav
                    pathname={pathname}
                    userName={name}
                    userInitial={initial}
                />

                <a
                    href="#app-content"
                    className="sr-only focus:not-sr-only focus:fixed focus:start-2 focus:top-2 focus:z-[60] focus:rounded-lg focus:bg-primary focus:px-3 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-foreground focus:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                    Skip to content
                </a>

                {/* Content column: reflows with the sidebar's inline size.
                    `tabIndex={-1}` makes the skip-link target focusable
                    programmatically without joining the tab order. */}
                <div
                    id="app-content"
                    tabIndex={-1}
                    className="flex min-w-0 flex-1 flex-col focus:outline-none"
                >
                    {children}
                </div>
            </div>
        </div>
    );
}
