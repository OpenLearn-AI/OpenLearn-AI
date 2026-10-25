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
 * - Expanded (224px): the "OpenLearn" brand identity with the
 *   adjacent collapse control, icon + text label per item, a visible
 *   current-route treatment, and an account region (identity, theme
 *   toggle, logout).
 * - Collapsed (56px, SIDE-01 — reduced from 64px; the smallest
 *   standard step that keeps every icon, the 36px brand mark, the
 *   avatar, and the toggle at their original sizes with usable hit
 *   targets): icons only, with the brand mark at the top. Text labels
 *   become `sr-only` so every icon-only control keeps its accessible
 *   name without relying on the tooltip; tooltips reinforce the name
 *   visually on hover AND keyboard focus (Base UI behavior) at an
 *   inline-end placement that flips automatically in RTL.
 *
 * Collapsed toggle interaction (SIDE-02, refining SIDE-01): the
 * expand control REPLACES the logo in the logo's own 36px cell while
 * the pointer stays near the brand region — at idle the logo is
 * visible and the control is hidden; on hover the two swap in place
 * through a choreographed opacity cross-fade (the mark fades out
 * immediately, the control fades in after a short delay, and the
 * order reverses on leave, so the two never visibly compete for the
 * cell). The swap is pure CSS over a stable shared region (the top
 * region is the `group`; no JavaScript position tracking), so moving
 * the pointer from the mark onto the revealed control cannot trigger
 * a pointer-leave, and nothing in the surrounding layout ever
 * shifts. The control is also revealed by receiving keyboard focus
 * (it stays in the accessibility tree at all times, so keyboard
 * users can always reach and see it with a visible focus indicator),
 * and on hover-less (touch) pointer devices it stays permanently
 * visible in its own row beneath the mark — the exact SIDE-01
 * hover-less behavior, unchanged.
 *
 * Batch 4.2 correction B: the collapsed top region no longer
 * reserves SIDE-01's empty second row on hover-capable pointer
 * devices — the logo row is the region's only row there, removing
 * the dead band that used to sit beneath the mark (the owner's
 * "useless gap below the logo"). The slot still exists for
 * hover-less (touch) devices, where it is the toggle's permanent
 * visible row and carries real content; the rule is a structural
 * media query on the slot itself (the same [@media(hover:…)]
 * vocabulary the toggle already uses), not a negative margin or a
 * one-off override. The expanded sidebar is untouched.
 *
 * The current route is marked by `aria-current="page"` plus a brass
 * tint + text treatment (`bg-sidebar-primary/10` +
 * `text-sidebar-primary`, AA-verified in both themes) AND an
 * inline-start indicator bar in `sidebar-primary` — never color alone
 * (WCAG 1.4.1). All spacing/edges use logical utilities (`ps-`,
 * `pe-`, `start-`, `border-e`) per the RTL discipline; colors are the
 * `sidebar-*` token group only.
 *
 * The collapse/expand control lives in the upper region: at the
 * inline end of the identity row when expanded (visually separate
 * from the logo — unchanged), and in the collapsed rail it overlays
 * the logo's own cell while the pointer or keyboard focus is there,
 * dropping to its dedicated row beneath the mark on hover-less
 * devices (SIDE-02 replacement interaction).
 *
 * Brand tile (SIDE-02): the tile behind the mark no longer paints a
 * surface. Its `bg-primary/10` rendered a warm/yellow plate behind
 * the mark in the dark theme (the dark `--primary` IS the brass of
 * the mark itself), which the owner flagged as an unwanted yellow
 * background; the supplied `public/logo.svg` is transparent by
 * design, so the mark now sits directly on the sidebar surface in
 * both themes.
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
                collapsed ? "w-14" : "w-56",
            )}
        >
            {/* Top region — product identity (brand mark + "OpenLearn")
                with the collapse/expand control adjacent to it. The
                expanded width keeps the control at the title row's
                inline end; the collapsed rail stacks the mark and the
                hover-revealed control. The collapsed branch is the
                hover/focus group that reveals that control. */}
            <div
                className={cn(
                    "relative shrink-0 border-b border-sidebar-border",
                    collapsed
                        ? "group flex flex-col items-center gap-1 px-2 py-2"
                        : "px-3 py-2.5",
                )}
            >
                <Link
                    href="/"
                    className={cn(
                        "block rounded-lg outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
                        collapsed &&
                            // SIDE-02 swap, logo side: the mark yields its
                            // cell to the toggle while the pointer hovers
                            // the brand region or the toggle holds focus.
                            // Leaving the region reverses the order (the
                            // toggle fades out at once, the mark returns
                            // after a short delay) so the two never
                            // overlap mid-transition.
                            "transition-opacity duration-150 delay-100 group-hover:opacity-0 group-hover:delay-0 group-has-[button:focus]:opacity-0 group-has-[button:focus]:delay-0",
                    )}
                >
                    <span
                        className={cn(
                            "flex h-9 items-center gap-3",
                            !collapsed && "pe-11",
                        )}
                    >
                        <span className="flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-xl">
                            {/* The supplied `public/logo.svg` brand asset
                                (vector — crisp at any size; `unoptimized`
                                serves the SVG as-is, no optimizer
                                involvement) at its natural aspect ratio
                                (`object-contain`, no crop/distortion).
                                SIDE-02: no painted tile behind it — see
                                the header note. The link's accessible
                                name comes from the visible (or
                                visually-hidden) product name. */}
                            <Image
                                src="/logo.svg"
                                alt=""
                                width={36}
                                height={36}
                                className="size-full object-contain"
                                unoptimized
                            />
                        </span>
                        {!collapsed && (
                            <span className="block min-w-0 truncate text-base font-bold text-sidebar-foreground">
                                OpenLearn
                            </span>
                        )}
                        {collapsed && (
                            <span className="sr-only">OpenLearn</span>
                        )}
                    </span>
                </Link>

                {collapsed && (
                    // The toggle's dedicated row, needed ONLY where the
                    // SIDE-02 in-cell replacement cannot work: on
                    // hover-less (touch) devices the control lives here,
                    // permanently visible (the SIDE-01 behavior). On
                    // hover-capable pointer devices the slot collapses
                    // entirely (Batch 4.2 correction B) — the control
                    // overlays the logo's own cell and the region ends
                    // at the logo row, so no empty band sits beneath
                    // the mark and the nav starts immediately below.
                    <div
                        aria-hidden="true"
                        className="size-9 [@media(hover:hover)]:hidden"
                    />
                )}

                {collapsed ? (
                    // SIDE-02 replacement position: the control overlays
                    // the logo's own cell (`inset-x-0` + `mx-auto` center
                    // it inside the 56px rail; direction-neutral, no
                    // transform). Idle it is invisible AND
                    // pointer-transparent, so clicks pass through to the
                    // logo link beneath; hover/focus reveals it as the
                    // logo yields — the choreography lives in the two
                    // `transition-*` pairs (mark: instant out / delayed
                    // return; control: delayed in / instant out). On
                    // hover-less devices the control moves down to its
                    // dedicated row and is permanently visible — the
                    // SIDE-01 touch behavior, unchanged.
                    <SidebarCollapseToggle
                        collapsed={collapsed}
                        onToggleCollapsed={onToggleCollapsed}
                        className="pointer-events-none absolute inset-x-0 top-2 mx-auto opacity-0 transition-opacity duration-100 focus:pointer-events-auto focus:opacity-100 group-hover:pointer-events-auto group-hover:delay-100 group-hover:duration-150 group-hover:opacity-100 [@media(hover:none)]:pointer-events-auto [@media(hover:none)]:bottom-2 [@media(hover:none)]:opacity-100 [@media(hover:none)]:top-auto"
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
                the primary navigation area. Collapsed, the horizontal
                padding tightens by one step (px-2) so the 36px avatar
                keeps its exact size and centering inside the 56px rail. */}
            <div
                className={cn(
                    "shrink-0 border-t border-sidebar-border p-3",
                    collapsed && "px-2",
                )}
            >
                {/* User identity (SIDE-01): the expanded label is the
                    person's first and last name; the collapsed avatar
                    shows the first-name initial. Both are derived by
                    the shared `useUserName` hook from the session's
                    real name claims, with the established
                    email → "User" fallback. Collapsed, the name is
                    carried by visually-hidden text (never the tooltip
                    alone); the tooltip is a sighted-user reinforcement
                    on hover. */}
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
 * "Expand sidebar"). In the collapsed sidebar it is icon-only, gets a
 * reinforcing tooltip like every other icon-only control, and is
 * hidden at idle behind an opacity transition owned by the caller —
 * it stays in the accessibility tree and operable at all times
 * (keyboard activation does not depend on pointer reachability; the
 * caller also releases `pointer-events` back to it whenever it is
 * revealed). Its positioning is owned by the caller; the reveal and
 * the surrounding geometry never shift the layout.
 */
function SidebarCollapseToggle({
    collapsed,
    onToggleCollapsed,
    className,
}: {
    collapsed: boolean;
    onToggleCollapsed: () => void;
    className?: string;
}) {
    const button = (
        <button
            type="button"
            onClick={onToggleCollapsed}
            aria-expanded={!collapsed}
            aria-controls="app-sidebar"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            className={cn(
                "flex size-9 shrink-0 items-center justify-center rounded-xl text-sidebar-foreground/75 outline-none transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
                className,
            )}
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
