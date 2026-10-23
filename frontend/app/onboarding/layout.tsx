import { AuthGuard } from "@/components/AuthGuard";
import { BrandMark } from "@/components/brand/BrandMark";
import { ThemeToggle } from "@/components/ui/theme-toggle";

/**
 * Onboarding layout (Batch 4.1 — owner decision Q3).
 *
 * The wizard lives OUTSIDE the `(app)` group by design: it must not
 * mount the application shell (there is nothing to navigate away to
 * mid-setup), and it must not mount the `(app)` OnboardingGate — the
 * gate redirects profile-less users to `/onboarding`, so a gate inside
 * the wizard's own route would loop. Loop safety is therefore
 * structural: the wizard's route is never in the gate's scope.
 *
 * Protection is still required — `/onboarding` is an authenticated
 * surface (its API calls need a session), so `AuthGuard` (unchanged)
 * wraps the content and redirects unauthenticated visitors to
 * `/login?redirectedFrom=/onboarding`.
 *
 * The visual identity matches the `(auth)` entries (BrandMark + theme
 * toggle on the same centered surface), keeping one product identity
 * across the public and first-login journeys.
 */
export default function OnboardingLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <main className="relative min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-4">
            <div className="absolute end-6 top-6">
                <ThemeToggle />
            </div>

            <div className="mb-8">
                <BrandMark />
            </div>

            <AuthGuard>{children}</AuthGuard>
        </main>
    );
}
