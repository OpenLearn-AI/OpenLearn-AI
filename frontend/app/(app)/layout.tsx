import type { ReactNode } from "react";

import { AppShell } from "@/components/shell/AppShell";
import { AuthGuard } from "@/components/AuthGuard";

/**
 * Authenticated application shell (D1, Batch 3.3).
 *
 * All routes under `(app)` share this layout. The shared sidebar
 * shell (desktop navigation, mobile navigation, account region, and
 * footer) renders here — it no longer renders on public routes (`/`,
 * `/login`, `/register`) which are handled by the root layout.
 *
 * `AuthGuard` wraps the shell so every `(app)` route is protected by
 * exactly one guard, at the same position as before this batch: the
 * shell (and everything it renders) exists only inside the
 * authenticated context the guard provides.
 */
export default function AppLayout({ children }: { children: ReactNode }) {
    return (
        <AuthGuard>
            <AppShell>{children}</AppShell>
        </AuthGuard>
    );
}
