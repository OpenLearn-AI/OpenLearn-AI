import { AuthGuard } from "@/components/AuthGuard";
import { OnboardingJourneyVisual } from "@/components/onboarding/OnboardingJourneyVisual";

/**
 * Onboarding layout (Batch 4.2 public-direction redesign).
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
 * Redesign changes vs. Batch 4.1:
 *   - Fixed dark, like every other public surface. The layout is
 *     wrapped in a `dark` root (no system-preference switching on
 *     first-login or public surfaces; the `(app)` Light/Dark toggle
 *     is unaffected), with the documented dark-ambient token mixes
 *     painting the panel's depth instead of hardcoded colors.
 *   - Two-column composition on desktop: a quiet identity visual on
 *     the inline-start side (the product's arcs/dots composition,
 *     drawn on once), the form on the inline-end side. Under RTL the
 *     grid mirrors automatically (logical side placement).
 *   - Redundant branding removed: no extra war-mark above the form
 *     (the wizard's own step headings are the content), and no
 *     theme toggle on a fixed-dark surface.
 */
export default function OnboardingLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <main className="dark relative min-h-svh bg-background text-foreground">
            <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-x-0 top-0 h-72 bg-[radial-gradient(60%_100%_at_18%_0%,var(--ambient-brass-subtle),transparent_70%)]"
            />
            <div className="relative grid min-h-svh lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1fr)]">
                <aside
                    aria-hidden="true"
                    className="relative hidden items-center justify-center overflow-hidden border-border/60 p-12 lg:flex lg:border-e"
                >
                    <div className="w-full max-w-md">
                        <OnboardingJourneyVisual />
                        <p className="ol-enter ol-enter-delay-2 mt-10 text-sm leading-relaxed text-muted-foreground">
                            Three short steps tell us where you study and how
                            you like to learn, so the space can fit you. Nothing
                            is shared or published to other users.
                        </p>
                    </div>
                </aside>
                <section className="flex items-center justify-center px-4 py-10 sm:px-10">
                    <div className="w-full max-w-lg">
                        <AuthGuard>{children}</AuthGuard>
                    </div>
                </section>
            </div>
        </main>
    );
}
