import type { ReactNode } from "react";

import { AppShell } from "@/components/shell/AppShell";
import { AuthGuard } from "@/components/AuthGuard";
import { OnboardingGate } from "@/components/onboarding/OnboardingGate";

/**
 * Authenticated application shell (D1, Batch 3.3; gate added Batch 4.1).
 *
 * All routes under `(app)` share this layout. The shared sidebar
 * shell (desktop navigation, mobile navigation, account region, and
 * footer) renders here — it no longer renders on public routes (`/`,
 * `/login`, `/register`, `/onboarding`).
 *
 * Guard order (each layer has exactly one responsibility):
 *   1. `AuthGuard` — authentication only (unchanged): redirects
 *      unauthenticated users to `/login?redirectedFrom=...`.
 *   2. `OnboardingGate` — profile existence only (Batch 4.1): routes
 *      users without a profile (the API's confirmed 404) to the
 *      `/onboarding` wizard; `/profile` is exempt; request failures
 *      render an error, never a redirect. The gate never mounts on
 *      `/onboarding` itself (outside this group), so no loop is
 *      possible.
 *   3. `AppShell` — navigation chrome only.
 */
export default function AppLayout({ children }: { children: ReactNode }) {
    return (
        <AuthGuard>
            <OnboardingGate>
                <AppShell>{children}</AppShell>
            </OnboardingGate>
        </AuthGuard>
    );
}
