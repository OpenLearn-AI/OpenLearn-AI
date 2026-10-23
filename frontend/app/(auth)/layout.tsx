import { ThemeToggle } from "@/components/ui/theme-toggle";
import { BrandMark } from "@/components/brand/BrandMark";

/**
 * Shared minimal layout for the `(auth)` route group (D1, Batch 4.1).
 *
 * `/login` and `/register` share this centered, full-screen shell:
 * the product identity (BrandMark) above the entry card and the theme
 * toggle at the inline end. No Navbar, no application navigation, no
 * authenticated UI — those belong to `app/(app)/layout.tsx`.
 *
 * Batch 4.1: the identity block moved here from the individual pages
 * (they previously each hand-rolled an "OPENLEARN" wordmark) so both
 * entries present the same branded surface as the landing and the
 * onboarding wizard. The pages keep their own headings and states —
 * the E2E-pinned strings ("Sign in to your account", "Create an
 * account", "Sign in with OpenLearn AI") are unchanged.
 */
export default function AuthLayout({
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

            {children}
        </main>
    );
}
