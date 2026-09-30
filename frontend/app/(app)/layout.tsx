import type { ReactNode } from "react";

import { Navbar } from "@/components/Navbar";
import { AuthGuard } from "@/components/AuthGuard";

/**
 * Authenticated application shell (D1).
 *
 * All routes under `(app)` share this layout. The Navbar and footer
 * render here — they no longer render on public routes (`/`, `/login`,
 * `/register`) which are handled by the root layout.
 *
 * `AuthGuard` wraps the children so every `(app)` route is protected
 * by exactly one guard, replacing the previous per-page `useEffect`
 * redirect on the dashboard.
 */
export default function AppLayout({ children }: { children: ReactNode }) {
    return (
        <AuthGuard>
            <Navbar />
            <div className="flex-grow flex flex-col">{children}</div>
            <footer className="border-t border-border bg-card py-6 text-center text-xs text-muted-foreground">
                <p>OpenLearn AI Adaptive Learning Platform</p>
            </footer>
        </AuthGuard>
    );
}
