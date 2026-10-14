"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { getKeycloak } from "@/lib/keycloak";

/**
 * Registration entry (S3 — real register flow).
 *
 * Registration is hosted by Keycloak: this page starts the OIDC
 * register redirect and gives feedback in every state it can observe —
 * idle, loading (the redirect is in flight), the null-client state
 * (no Keycloak instance could be created), and error (the redirect
 * failed). Before Batch 1.2 the page failed silently in all of these.
 * The `keycloak.register` call site and its redirect target are
 * protected logic (roadmap Batches 1.2 / 4.1) and are unchanged. The
 * theme toggle mirrors the login page (theme parity).
 */
export default function RegisterPage() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleRegister = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const keycloak = await getKeycloak();

            if (!keycloak) {
                // Null-client state: the Keycloak adapter could not be
                // created or initialized (e.g. the auth service is
                // unreachable). Surfaced below instead of a silent return.
                throw new Error(
                    "Unable to connect to the authentication service.",
                );
            }

            await keycloak.register({
                redirectUri: `${window.location.origin}/dashboard`,
            });
        } catch (cause) {
            console.error("Registration failed:", cause);

            setError(
                cause instanceof Error
                    ? cause.message
                    : "Unable to start registration. Please try again.",
            );

            setIsLoading(false);
        }
    };

    return (
        <>
            <div className="absolute end-6 top-6">
                <ThemeToggle />
            </div>

            {/* Brand Header */}
            <div className="text-center mb-8">
                <h1 className="text-2xl sm:text-3xl font-bold tracking-wider text-foreground">OPENLEARN</h1>
            </div>

            <div className="w-full max-w-md bg-card text-card-foreground p-8 rounded-2xl shadow-xl border border-border">
                <div className="mb-6 space-y-1">
                    <h2 className="text-2xl font-bold text-card-foreground">Create an account</h2>
                    <p className="text-sm text-muted-foreground">Create your OpenLearn AI account</p>
                </div>

                {error && (
                    <p
                        role="alert"
                        className="mb-4 text-sm text-destructive"
                    >
                        {error}
                    </p>
                )}

                <Button
                    type="button"
                    onClick={handleRegister}
                    disabled={isLoading}
                    className="w-full font-medium py-2.5 rounded-xl transition"
                >
                    {isLoading
                        ? "Connecting..."
                        : "Create account"}
                </Button>
            </div>
        </>
    );
}
