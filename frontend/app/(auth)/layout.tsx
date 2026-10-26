import { BrandMark } from "@/components/brand/BrandMark";

/**
 * Shared minimal layout for the `(auth)` route group (D1, Batch 4.1;
 * fixed dark per the Batch 4.2 redesign).
 *
 * `/login` and `/register` share this centered, full-screen shell:
 * the product identity (BrandMark) above the entry card. No Navbar,
 * no application navigation, no authenticated UI — those belong to
 * `app/(app)/layout.tsx`.
 *
 * Batch 4.1: the identity block moved here from the individual pages
 * (they previously each hand-rolled an "OPENLEARN" wordmark) so both
 * entries present the same branded surface as the landing and the
 * onboarding wizard. The pages keep their own headings and states —
 * the E2E-pinned strings ("Sign in to your account", "Create an
 * account", "Sign in with OpenLearn AI") are unchanged.
 *
 * Batch 4.2 redesign: the public experience is FIXED dark — system /
 * preference-driven theming is deliberately OFF on public surfaces
 * (the previous ThemeToggle is removed), so the shell is wrapped in a
 * `dark` root regardless of any stored `(app)` theme preference. The
 * documented dark ambient token mix paints the shell's depth; no
 * hardcoded colors.
 */
export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <main className="dark relative min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-4">
            <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-x-0 top-0 h-72 bg-[radial-gradient(60%_100%_at_50%_0%,var(--ambient-brass-subtle),transparent_70%)]"
            />
            <div className="relative">
                <div className="mb-8">
                    <BrandMark />
                </div>

                {children}
            </div>
        </main>
    );
}
