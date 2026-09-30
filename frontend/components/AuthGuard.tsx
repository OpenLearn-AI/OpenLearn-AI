"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth-context";
import { LoadingBlock } from "@/components/state/LoadingBlock";

/**
 * Single application-level authentication guard (D7).
 *
 * Wraps the `(app)` route group's children. While the Keycloak
 * initialization is in flight, a loading state is rendered (no
 * redirect). Once resolved:
 *   - authenticated → children render normally
 *   - unauthenticated → redirect to `/login` carrying `redirectedFrom`
 *     so the login flow can return the user to the page they originally
 *     requested
 *
 * Side effects live in a `useEffect` to avoid redirecting during render
 * and to prevent redirect loops.
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, isLoading } = useAuth();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (isLoading || isAuthenticated) {
            return;
        }

        // Unauthenticated — redirect to login with the originally
        // requested path so the user can return after authenticating.
        const params = new URLSearchParams({ redirectedFrom: pathname });
        router.replace(`/login?${params.toString()}`);
    }, [isLoading, isAuthenticated, router, pathname]);

    if (isLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-background px-4 py-8">
                <LoadingBlock message="Preparing your session..." />
            </div>
        );
    }

    if (!isAuthenticated) {
        // The effect above is redirecting; render nothing to avoid
        // flashing protected content.
        return null;
    }

    return <>{children}</>;
}
