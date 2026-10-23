"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { initiateOidcAction } from "@/features/auth/oidc-actions";

/**
 * Direct authentication action button (Batch 4.1 corrective follow-up
 * §C.1/§C.3) — the landing navbar's "Log in" and "Create account".
 *
 * Clicking initiates the EXISTING Keycloak flow immediately
 * (`keycloak.login` / `keycloak.register` — no local form, no extra
 * click), which is the intended journey:
 *
 *   landing → Keycloak → OIDC callback → onboarding (when required)
 *           → dashboard or intended destination
 *
 * The Keycloak adapter is imported dynamically so the landing page
 * never initializes Keycloak (or evaluates its config) until a visitor
 * actually chooses an auth action — the landing stays a public,
 * hermetic surface at rest. If the auth service cannot be reached, the
 * button falls back to the matching entry bridge (`/login`,
 * `/register`), which renders the explicit error state — the button
 * never dead-ends.
 */
export function OidcEntryButton({
    mode,
    children,
    variant,
    size,
    className,
}: {
    mode: "login" | "register";
    children: React.ReactNode;
    variant?: React.ComponentProps<typeof Button>["variant"];
    size?: React.ComponentProps<typeof Button>["size"];
    className?: string;
}) {
    const router = useRouter();
    const [isPending, setIsPending] = React.useState(false);

    const handleClick = async () => {
        setIsPending(true);

        try {
            await initiateOidcAction(
                mode,
                // Same destinations the previous links produced via the
                // entry pages: login defaults to /dashboard, register
                // lands on /dashboard (and the onboarding gate takes it
                // from there for fresh users).
                "/dashboard",
            );
        } catch {
            // Keycloak unreachable / adapter failed: hand over to the
            // entry bridge, which owns the explicit error UI.
            router.push(mode === "login" ? "/login" : "/register");
        }
    };

    return (
        <Button
            type="button"
            variant={variant}
            size={size}
            className={className}
            onClick={handleClick}
            disabled={isPending}
            aria-busy={isPending}
        >
            {children}
        </Button>
    );
}
