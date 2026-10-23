import { BookOpen, House, LayoutDashboard, UserRound } from "lucide-react";

/**
 * Primary navigation configuration (Batch 3.3 shell).
 *
 * The single shared source of truth for the shell's primary
 * navigation — the desktop sidebar and the mobile drawer both render
 * from this list, so their destinations, order, and labels cannot
 * drift apart.
 *
 * Labels and destinations are preserved verbatim from the legacy
 * `components/Navbar.tsx` NAV_LINKS (Batch 3.3 contract: nav link
 * targets do not change). Icons are presentation only; they are
 * decorative reinforcement next to a text label and carry no
 * information the label does not.
 *
 * Role-awareness (roadmap Sections 4 and 8): navigation stays
 * role-simple — the same links are shown to every signed-in user.
 * The backend authorizes; the shell does not gate, and no admin or
 * role-specific destination exists to present (the admin role has no
 * enforced backend capability; Section 4 of the roadmap).
 */
export const NAV_LINKS = [
    { href: "/", label: "Home", icon: House },
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
 * `/courses/[id]/edit`. With this rule exactly one configured item
 * can be current on any protected route — `/` (the public landing,
 * outside the protected shell) is the only href that matches by
 * equality alone and can never be current inside `(app)`.
 */
export function isActiveRoute(pathname: string, href: string): boolean {
    if (href === "/") {
        return pathname === "/";
    }
    return pathname === href || pathname.startsWith(`${href}/`);
}
