"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { LandingPage } from "@/components/landing/LandingPage";
import { useAuth } from "@/lib/auth-context";

/**
 * The public landing page (Batch 4.1).
 *
 * Auth rules (both owner-approved):
 *   - The landing is genuinely public: this page calls only `useAuth()`
 *     (Keycloak state) and never `useMe()` or any authenticated API.
 *     The previous landing's unconditional `useMe()` threw `ApiError`
 *     (401) for signed-out visitors, and the global session recovery
 *     then bounced them to `/login?redirectedFrom=%2F` — the landing
 *     was not actually public at runtime. That defect is fixed here by
 *     construction: no API call exists on this route.
 *   - Authenticated users visiting `/` are redirected to `/dashboard`
 *     (Decision Lock §4.1, assigned to this batch), but only after
 *     authentication initialization has completed — while Keycloak's
 *     `check-sso` is in flight the landing renders normally, so there
 *     is no splash and no flash-of-nothing for either audience.
 *
 * The redirect runs in an effect (never during render) and uses
 * `replace` so the landing does not remain in the history stack between
 * `/` and the dashboard. Redirect loops are structurally impossible:
 * `/dashboard` never redirects back to `/`.
 */
export default function Home() {
    const { isAuthenticated, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && isAuthenticated) {
            router.replace("/dashboard");
        }
    }, [isLoading, isAuthenticated, router]);

    return <LandingPage />;
}
