"use client";

import Image from "next/image";
import Link from "next/link";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";

import { cn } from "@/lib/utils";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { LogoutButton } from "@/components/auth/LogoutButton";
import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import { NAV_LINKS, isActiveRoute } from "./nav-config";

/**
 * Desktop sidebar (Batch 3.3 shell) — presentational.
 *
 * Two explicit states driven by the `collapsed` prop (state lives in
 * `AppShell` so it survives client-side navigation):
 *
 * - Expanded: brand identity with the adjacent collapse control, icon
 *   + text label per item, a visible current-route treatment, and an
 *   account region (identity, theme toggle, logout).
 * - Collapsed: icons only (identity mark + collapse control stacked at
 *   the top). Text labels become `sr-only` so every icon-only control
 *   keeps its accessible name without relying on the tooltip; tooltips
 *   reinforce the name visually on hover AND keyboard focus (Base UI
 *   behavior) at an inline-end placement that flips automatically in
 *   RTL.
 *
 * The current route is marked by `aria-current="page"` plus a Steel
 * Blue tint + text treatment (`bg-sidebar-primary/10` +
 * `text-sidebar-primary`, AA-verified in both themes) AND an
 * inline-start indicator bar in `sidebar-primary` — never color alone
 * (WCAG 1.4.1). All spacing/edges use logical utilities (`ps-`,
 * `pe-`, `start-`, `border-e`) per the RTL discipline; colors are the
 * `sidebar-*` token group only.
 *
 * The collapse/expand control lives in the upper region, adjacent to
 * the product identity: at the inline end of the identity's title row
 * when expanded (the 224px width cannot hold the two-line identity and
 * the control on one row without wrapping the identity), stacked
 * directly beneath the mark when collapsed.
 */
export function AppSidebar({
    collapsed,
    pathname,
    userName,
    userInitial,
    onToggleCollapsed,
}: {
    collapsed: boolean;
    pathname: string;
    userName: string;
    userInitial: string;
    onToggleCollapsed: () => void;
}) {
    return (
        <aside
            id="app-sidebar"
            data-collapsed={collapsed || undefined}
            className={cn(
                "sticky top-0 hidden h-svh shrink-0 flex-col overflow-hidden border-e border-sidebar-border bg-sidebar text-sidebar-foreground transition-[width] md:flex",
                collapsed ? "w-16" : "w-56",
            )}
        >
            {/* Top region — product identity (existing brand assets/name)
                with the collapse/expand control adjacent to it. At the
                224px expanded width a single row cannot hold the
                two-line identity AND the control without wrapping the
                identity, so the identity keeps its own rows (title row
                carries the control at its inline end; the tagline spans
                the full width below) and the collapsed rail stacks the
                mark and the control. Truncation guards exist only as a
                safety net for extreme font metrics — with Geist Sans
                nothing is truncated at either width. */}
            <div
                className={cn(
                    "relative shrink-0 border-b border-sidebar-border",
                    collapsed
                        ? "flex flex-col items-center gap-1 px-2 py-2"
                        : "px-3 py-2.5",
                )}
            >
                <Link
                    href="/"
                    className="block rounded-lg outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                    <span
                        className={cn(
                            "flex h-9 items-center gap-3",
                            !collapsed && "pe-11",
                        )}
                    >
                        <span className="flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-primary/10">
                            <Image
                                src="/logo.png"
                                alt="OpenLearn AI Logo"
                                width={36}
                                height={36}
                                className="size-full object-cover"
                            />
                        </span>
                        {!collapsed && (
                            <span className="block min-w-0 truncate text-base font-bold text-sidebar-foreground">
                                OpenLearn AI
                            </span>
                        )}
                        {collapsed && (
                            <span className="sr-only">
                                OpenLearn AI - Adaptive Learning Platform
                            </span>
                        )}
                    </span>
                    {!collapsed && (
                        <span className="block truncate text-xs text-muted-foreground">
                            Adaptive Learning Platform
                        </span>
                    )}
                </Link>

                {collapsed ? (
                    <SidebarCollapseToggle
                        collapsed={collapsed}
                        onToggleCollapsed={onToggleCollapsed}
                    />
                ) : (
                    <div className="absolute end-1.5 top-2.5">
                        <SidebarCollapseToggle
                            collapsed={collapsed}
                            onToggleCollapsed={onToggleCollapsed}
                        />
                    </div>
                )}
            </div>

            {/* Main region — primary navigation */}
            <nav
                aria-label="Primary navigation"
                className="flex-1 overflow-y-auto overflow-x-hidden px-3 py-4"
            >
                <ul className="flex flex-col gap-1">
                    {NAV_LINKS.map((link) => {
                        const isCurrent = isActiveRoute(pathname, link.href);

                        const linkClassName = cn(
                            "relative flex min-h-9 items-center gap-3 rounded-lg text-sm outline-none transition-colors focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
                            collapsed ? "justify-center px-0" : "px-2.5",
                            isCurrent
                                ? "bg-sidebar-primary/10 font-medium text-sidebar-primary before:absolute before:inset-y-1.5 before:start-0 before:w-0.5 before:rounded-full before:bg-sidebar-primary hover:bg-sidebar-primary/10 hover:text-sidebar-primary"
                                : "text-sidebar-foreground/75 hover:bg-sidebar-accent hover:text-sidebar-foreground",
                        );

                        const linkContent = (
                            <>
                                <link.icon
                                    className="size-4 shrink-0"
                                    aria-hidden="true"
                                />
                                <span
                                    className={cn(
                                        "whitespace-nowrap",
                                        collapsed && "sr-only",
                                    )}
                                >
                                    {link.label}
                                </span>
                            </>
                        );

                        return (
                            <li key={link.href}>
                                {collapsed ? (
                                    <Tooltip>
                                        <TooltipTrigger
                                            render={
                                                <Link
                                                    href={link.href}
                                                    aria-current={
                                                        isCurrent
                                                            ? "page"
                                                            : undefined
                                                    }
                                                    className={linkClassName}
                                                />
                                            }
                                        >
                                            {linkContent}
                                        </TooltipTrigger>
                                        <TooltipContent side="inline-end">
                                            {link.label}
                                        </TooltipContent>
                                    </Tooltip>
                                ) : (
                                    <Link
                                        href={link.href}
                                        aria-current={
                                            isCurrent ? "page" : undefined
                                        }
                                        className={linkClassName}
                                    >
                                        {linkContent}
                                    </Link>
                                )}
                            </li>
                        );
                    })}
                </ul>
            </nav>

            {/* Bottom account region — visually/semantically distinct from
                the primary navigation area */}
            <div className="shrink-0 border-t border-sidebar-border p-3">
                {/* User identity. Collapsed, the name is carried by
                    visually-hidden text (never the tooltip alone); the
                    tooltip is a sighted-user reinforcement on hover. */}
                {collapsed ? (
                    <Tooltip>
                        <TooltipTrigger
                            render={
                                <span className="flex w-full justify-center pb-2 outline-none" />
                            }
                        >
                            <span className="sr-only">{userName}</span>
                            <span
                                aria-hidden="true"
                                className="flex size-9 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary"
                            >
                                {userInitial}
                            </span>
                        </TooltipTrigger>
                        <TooltipContent side="inline-end">
                            {userName}
                        </TooltipContent>
                    </Tooltip>
                ) : (
                    <div className="flex items-center gap-2.5 pb-3">
                        <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                            {userInitial}
                        </span>
                        <span className="min-w-0 truncate text-sm font-semibold text-sidebar-foreground">
                            {userName}
                        </span>
                    </div>
                )}

                {/* Account actions: theme, logout — same order in both
                    states; icon-only controls keep sr-only names plus
                    reinforcing tooltips when collapsed. The collapse
                    control lives in the upper region, next to the
                    product identity. */}
                <div
                    className={cn(
                        "flex items-center",
                        collapsed
                            ? "flex-col justify-center gap-1"
                            : "justify-between gap-2",
                    )}
                >
                    {collapsed ? (
                        <Tooltip>
                            <TooltipTrigger render={<ThemeToggle />} />
                            <TooltipContent side="inline-end">
                                Toggle theme
                            </TooltipContent>
                        </Tooltip>
                    ) : (
                        <ThemeToggle />
                    )}

                    {collapsed ? (
                        <Tooltip>
                            <TooltipTrigger render={<LogoutButton compact />} />
                            <TooltipContent side="inline-end">
                                Logout
                            </TooltipContent>
                        </Tooltip>
                    ) : (
                        <LogoutButton />
                    )}
                </div>
            </div>
        </aside>
    );
}

/**
 * The dedicated collapse/expand control.
 *
 * Its current state is exposed twice: `aria-expanded` reflects the
 * sidebar's expansion (true = expanded), and the accessible name
 * states the action the next press performs ("Collapse sidebar" /
 * "Expand sidebar"). In the collapsed sidebar it is icon-only and
 * gets a reinforcing tooltip like every other icon-only control.
 */
function SidebarCollapseToggle({
    collapsed,
    onToggleCollapsed,
}: {
    collapsed: boolean;
    onToggleCollapsed: () => void;
}) {
    const button = (
        <button
            type="button"
            onClick={onToggleCollapsed}
            aria-expanded={!collapsed}
            aria-controls="app-sidebar"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="flex size-9 shrink-0 items-center justify-center rounded-xl text-sidebar-foreground/75 outline-none transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        >
            {collapsed ? (
                <PanelLeftOpen
                    className="size-4 rtl:rotate-180"
                    aria-hidden="true"
                />
            ) : (
                <PanelLeftClose
                    className="size-4 rtl:rotate-180"
                    aria-hidden="true"
                />
            )}
        </button>
    );

    if (!collapsed) {
        return button;
    }

    return (
        <Tooltip>
            <TooltipTrigger render={button} />
            <TooltipContent side="inline-end">
                Expand sidebar
            </TooltipContent>
        </Tooltip>
    );
}
