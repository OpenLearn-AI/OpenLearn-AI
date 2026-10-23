import { BookOpen, LayoutDashboard, UserRound } from "lucide-react";

/**
 * Primary navigation configuration (Batch 3.3 shell).
 *
 * The single shared source of truth for the shell's primary
 * navigation — the desktop sidebar and the mobile drawer both render
 * from this list, so their destinations, order, and labels cannot
 * drift apart.
 *
 * Final navigation inventory (Batch 3.3 follow-up, owner IA decision
 * 2026-10-23): the legacy `Home` entry (href `/`) was removed. `/` is
 * the public landing page for visitors and exits the authenticated
 * application shell, so it is not a protected-navigation destination;
 * `/dashboard` is the authenticated users' primary destination and is
 * already the post-login default (LoginForm's D7 redirect policy).
 * The remaining destinations and their relative order are unchanged
 * from the legacy NAV_LINKS. The product identity (brand link) in the
 * shell's upper region still targets `/`, as the legacy Navbar's
 * brand link always did — it is the identity mark, not a navigation
 * entry. Icons are presentation only; they are decorative
 * reinforcement next to a text label and carry no information the
 * label does not.
 *
 * Role-awareness (roadmap Sections 4 and 8): navigation stays
 * role-simple — the same links are shown to every signed-in user.
 * The backend authorizes; the shell does not gate, and no admin or
 * role-specific destination exists to present (the admin role has no
 * enforced backend capability; Section 4 of the roadmap).
 */
export const NAV_LINKS = [
    { href: "/courses", label: "Courses", icon: BookOpen },
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/profile", label: "Profile & Settings", icon: UserRound },
] as const;

/**
 * Active-route matcher for the shell.
 *
 * Deliberate nested-route handling: an item is current when the
 * pathname equals its href or lives beneath it (`href/...`), so the
 * Courses item stays current on `/courses/new`, `/courses/[id]`, and
 * `/courses/[id]/edit`. Every configured href is a distinct top-level
 * protected segment, so exactly one item is current on any protected
 * route (and none is current while the matcher's inputs are outside
 * the configured set).
 */
export function isActiveRoute(pathname: string, href: string): boolean {
    return pathname === href || pathname.startsWith(`${href}/`);
}
