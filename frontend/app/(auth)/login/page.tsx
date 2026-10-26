import { Suspense } from "react";

import { OidcEntryBridge } from "@/components/auth/OidcEntryBridge";
import { LoadingBlock } from "@/components/state/LoadingBlock";

/**
 * Login entry — minimal redirect bridge (Batch 4.1 corrective follow-up
 * §C.4).
 *
 * The previous local card ("Sign in to your account" + a separate OIDC
 * button) added an extra click between the landing page and Keycloak;
 * this page now hands the visit straight to the shared
 * `OidcEntryBridge`, which initiates the EXISTING Keycloak flow
 * directly (carrying the validated `redirectedFrom` deep link exactly
 * as before). The bridge's manual state keeps the E2E-pinned
 * "Sign in with OpenLearn AI" button for the return-after-attempt and
 * error paths.
 *
 * The Suspense boundary is required by Next.js because the bridge reads
 * `useSearchParams()` (the `redirectedFrom` query param carried over by
 * AuthGuard).
 */
export default function LoginPage() {
    return (
        <Suspense
            fallback={
                <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 text-card-foreground shadow-xs">
                    <LoadingBlock message="Preparing sign-in…" />
                </div>
            }
        >
            <OidcEntryBridge mode="login" />
        </Suspense>
    );
}
