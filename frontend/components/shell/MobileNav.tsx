"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import { Menu, X } from "lucide-react";

import { cn } from "@/lib/utils";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { DirectionToggle } from "@/components/ui/direction-toggle";
import { LogoutButton } from "@/components/auth/LogoutButton";
import { NAV_LINKS, isActiveRoute } from "./nav-config";

/**
 * Mobile navigation (Batch 3.3 shell) — the sub-`md` pattern.
 *
 * A compact top bar plus a modal off-canvas navigation drawer. The
 * drawer is composed on Base UI's regular Dialog parts — the
 * repository's only component library, no new dependency — NOT on
 * the Batch 3.2 alert-dialog primitive, whose `role="alertdialog"`
 * semantics and pointer-dismissal disablement are wrong for
 * navigation. Base UI owns the documented modal behavior (focus
 * enters the popup on open, is trapped while open, returns to the
 * trigger on close; Escape closes; background scroll is locked):
 * no second focus-management system here.
 *
 * The drawer shows text labels for every destination (never
 * icon-only by default), an explicit close button, and the account
 * actions adapted to the pattern (identity + theme toggle +
 * logout).
 *
 * Batch 4.2 correction A9 (2026-10-25): the always-visible mobile
 * header is reduced to EXACTLY the identity mark and the menu
 * trigger — the obsolete `/logo.png` reference (a 404 since the
 * asset's removal) and the "OpenLearn AI / Adaptive Learning
 * Platform" wordmark-and-tagline block are REMOVED from the top
 * bar, and the header's height drops from 64px to 56px (the same
 * comfortable step as the collapsed desktop rail: the 36px brand
 * mark and the 36px trigger keep full legibility and tap room with
 * tighter vertical padding). The theme toggle moves INTO the
 * expanded drawer's account region — the same `ThemeToggle`
 * component the desktop sidebar uses, in the same account-actions
 * position, so its behavior is identical and it stays reachable by
 * keyboard and screen readers inside Base UI's focus trap while the
 * menu is open; there is never a second visible toggle (the
 * sidebar's copy is hidden below `md`, where only this bar exists).
 * The identity mark is the owner-supplied `public/logo.svg`
 * (unoptimized SVG as-is, `object-contain` — no crop, no painted
 * tile, matching the sidebar and BrandMark), still linked to `/`
 * as the identity mark with a visually-hidden accessible name.
 *
 * Open/close state is transient and controlled here: each navigation
 * item is a real Next.js `Link` (pure link semantics — a
 * `Dialog.Close` rendered as an anchor would be forced into
 * `role="button"`, breaking the semantic navigation contract) whose
 * click handler closes the drawer before the navigation proceeds;
 * Escape, the explicit close button, and Base UI's dismissal paths
 * close it in place. Focus management stays entirely Base UI's
 * documented behavior.
 */
export function MobileNav({
    pathname,
    userName,
    userInitial,
}: {
    pathname: string;
    userName: string;
    userInitial: string;
}) {
    const [open, setOpen] = useState(false);

    return (
        <DialogPrimitive.Root open={open} onOpenChange={setOpen}>
            {/* Top bar — mobile only (the desktop sidebar is hidden
                here). Correction A9: the identity mark and the menu
                trigger, nothing else. */}
            <header className="sticky top-0 z-40 flex h-14 w-full items-center justify-between border-b border-border bg-card px-4 md:hidden">
                <Link
                    href="/"
                    className="flex items-center rounded-lg outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                    <span className="sr-only">OpenLearn</span>
                    <span className="flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-xl">
                        <Image
                            src="/logo.svg"
                            alt=""
                            width={36}
                            height={36}
                            className="size-full object-contain"
                            unoptimized
                        />
                    </span>
                </Link>

                <DialogPrimitive.Trigger
                    aria-label="Open menu"
                    className="flex size-9 items-center justify-center rounded-xl border border-border bg-background text-foreground outline-none transition-colors hover:bg-muted focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                >
                    <Menu className="size-5" aria-hidden="true" />
                </DialogPrimitive.Trigger>
            </header>

            {/* Off-canvas navigation drawer (portaled, modal) */}
            <DialogPrimitive.Portal>
                <DialogPrimitive.Backdrop
                    className="fixed inset-0 isolate z-50 bg-black/10 duration-100 supports-backdrop-filter:backdrop-blur-xs data-open:animate-in data-open:fade-in-0 data-closed:animate-out data-closed:fade-out-0"
                />
                <DialogPrimitive.Popup
                    className="fixed inset-y-0 start-0 z-50 flex w-72 max-w-[85vw] flex-col bg-sidebar text-sidebar-foreground shadow-xl ring-1 ring-foreground/10 duration-100 outline-none data-open:animate-in data-open:slide-in-from-start data-closed:animate-out data-closed:slide-out-to-start"
                >
                    {/* Drawer header: identity + explicit close affordance */}
                    <div className="flex h-14 shrink-0 items-center justify-between border-b border-sidebar-border px-4">
                        <div className="flex items-center gap-3">
                            <span className="flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-xl">
                                <Image
                                    src="/logo.svg"
                                    alt=""
                                    width={36}
                                    height={36}
                                    className="size-full object-contain"
                                    unoptimized
                                />
                            </span>
                            <DialogPrimitive.Title className="text-base font-bold">
                                Menu
                            </DialogPrimitive.Title>
                        </div>
                        <DialogPrimitive.Close
                            aria-label="Close menu"
                            className="flex size-9 items-center justify-center rounded-xl text-sidebar-foreground/75 outline-none transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                        >
                            <X className="size-5" aria-hidden="true" />
                        </DialogPrimitive.Close>
                    </div>

                    {/* Primary navigation — text labels, same source of
                        truth and order as the desktop sidebar */}
                    <nav
                        aria-label="Primary navigation"
                        className="flex-1 overflow-y-auto px-3 py-4"
                    >
                        <ul className="flex flex-col gap-1">
                            {NAV_LINKS.map((link) => {
                                const isCurrent = isActiveRoute(
                                    pathname,
                                    link.href,
                                );

                                return (
                                    <li key={link.href}>
                                        <Link
                                            href={link.href}
                                            aria-current={
                                                isCurrent ? "page" : undefined
                                            }
                                            onClick={() => setOpen(false)}
                                            className={cn(
                                                "relative flex min-h-10 items-center gap-3 rounded-lg px-2.5 text-sm outline-none transition-colors focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
                                                isCurrent
                                                    ? "bg-sidebar-primary/10 font-medium text-sidebar-primary before:absolute before:inset-y-1.5 before:start-0 before:w-0.5 before:rounded-full before:bg-sidebar-primary hover:bg-sidebar-primary/10 hover:text-sidebar-primary"
                                                    : "text-sidebar-foreground/75 hover:bg-sidebar-accent hover:text-sidebar-foreground",
                                            )}
                                        >
                                            <link.icon
                                                className="size-4 shrink-0"
                                                aria-hidden="true"
                                            />
                                            {link.label}
                                        </Link>
                                    </li>
                                );
                            })}
                        </ul>
                    </nav>

                    {/* Account region — identity + actions, adapted to
                        the drawer pattern. Correction A9: the theme
                        toggle lives HERE (inside the expanded menu),
                        in the same account-actions position and the
                        same component as the desktop sidebar. Batch
                        4.4: the direction control joins it — the
                        same pairing, order, and components as the
                        desktop account region. */}
                    <div className="shrink-0 border-t border-sidebar-border p-4">
                        <div className="flex items-center gap-2.5 pb-3">
                            <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                                {userInitial}
                            </span>
                            <span className="min-w-0 truncate text-sm font-semibold text-sidebar-foreground">
                                {userName}
                            </span>
                        </div>
                        <div className="flex items-center gap-2">
                            <ThemeToggle />
                            <DirectionToggle />
                            <LogoutButton className="flex-1 justify-center" />
                        </div>
                    </div>
                </DialogPrimitive.Popup>
            </DialogPrimitive.Portal>
        </DialogPrimitive.Root>
    );
}
