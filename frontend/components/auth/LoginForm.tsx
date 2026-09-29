"use client";

import * as React from "react";
import { useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { getKeycloak } from "@/lib/keycloak";

/**
 * Validate that a `redirectedFrom` value is a same-origin, local, non-
 * API route. This prevents open-redirect attacks via crafted query
 * params while preserving the deep-link return-to flow.
 */
function safeRedirectTarget(value: string | null): string | null {
    if (!value) return null;
    // Must start with a single slash and not target the API or auth routes.
    if (!value.startsWith("/") || value.startsWith("//")) return null;
    if (value.startsWith("/login") || value.startsWith("/register")) {
        return null;
    }
    return value;
}

export function LoginForm() {
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const searchParams = useSearchParams();

    const handleLogin = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const keycloak = await getKeycloak();

            if (!keycloak) {
                throw new Error(
                    "Unable to connect to the authentication service.",
                );
            }

            // Phase 3 redirect policy (D7): login → /dashboard by default,
            // or the originally requested protected route if a valid
            // `redirectedFrom` was carried over by AuthGuard.
            const redirectTarget =
                safeRedirectTarget(searchParams.get("redirectedFrom")) ??
                "/dashboard";

            await keycloak.login({
                redirectUri: `${window.location.origin}${redirectTarget}`,
            });
        } catch (error) {
            console.error("Login failed:", error);

            setError(
                error instanceof Error
                    ? error.message
                    : "Unable to sign in. Please try again.",
            );

            setIsLoading(false);
        }
    };

    return (
        <Card className="w-full max-w-md">
            <CardHeader className="space-y-1">
                <CardTitle className="text-2xl">
                    Welcome back
                </CardTitle>

                <CardDescription>
                    Sign in to your OpenLearn AI account
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
                {error && (
                    <p
                        role="alert"
                        className="text-sm text-destructive"
                    >
                        {error}
                    </p>
                )}

                <Button
                    type="button"
                    onClick={handleLogin}
                    disabled={isLoading}
                    className="w-full"
                >
                    {isLoading
                        ? "Connecting..."
                        : "Sign in with OpenLearn AI"}
                </Button>
            </CardContent>
        </Card>
    );
}

