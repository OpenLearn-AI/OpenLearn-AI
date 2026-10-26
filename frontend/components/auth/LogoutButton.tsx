"use client";

import { useQueryClient } from "@tanstack/react-query";

import { cn } from "@/lib/utils";
import { getKeycloak } from "@/lib/keycloak";
import { markOidcAttempt } from "@/features/auth/oidc-attempt";

/**
 * The shared logout control.
 *
 * Batch 3.3 relocated logout from its Dashboard-only "Session
 * Control" card into the shell's account region (desktop sidebar and
 * mobile navigation both render it). The logout sequence itself is
 * unchanged and must stay unchanged: resolve Keycloak, clear the
 * React Query cache, then perform the existing Keycloak logout
 * redirect to `/login` (cache clear THEN redirect — the ordering is
 * a batch must-not-change).
 *
 * `compact` renders the icon-only form used by the collapsed sidebar;
 * the accessible name ("Logout") is identical in both forms, so the
 * control keeps a clear name in every mode. When `compact` is false
 * the visible "Logout" text is the accessible name and no
 * `aria-label` is applied.
 */
export function LogoutButton({
    compact = false,
    className,
}: {
    compact?: boolean;
    className?: string;
}) {
    const queryClient = useQueryClient();

    async function handleLogout() {
        const keycloak = await getKeycloak();

        if (!keycloak) {
            return;
        }

        queryClient.clear();

        // The logout redirect lands on `/login` (unchanged target). Mark
        // the OIDC attempt BEFORE leaving so the arrival renders the
        // explicit sign-in form instead of auto-redirecting straight
        // back into Keycloak — logout must never become an instant
        // re-login loop (corrective follow-up §C.4 loop audit).
        markOidcAttempt("login");

        await keycloak.logout({
            redirectUri: `${window.location.origin}/login`,
        });
    }

    return (
        <button
            type="button"
            onClick={handleLogout}
            aria-label={compact ? "Logout" : undefined}
            className={cn(
                "group inline-flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 text-sm font-medium text-destructive transition-all duration-200 hover:bg-destructive hover:text-destructive-foreground active:scale-[0.98] focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none",
                compact
                    ? "size-9 justify-center rounded-xl"
                    : "px-4 py-2",
                className,
            )}
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="transition-transform duration-200 group-hover:translate-x-0.5 rtl:rotate-180"
                aria-hidden="true"
            >
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            {!compact && "Logout"}
        </button>
    );
}
