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
import { safeRedirectTarget } from "@/features/auth/redirect";

export function LoginForm() {
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const searchParams = useSearchParams();

    // Keycloak is initialized with a non-silent `check-sso` (lib/keycloak.ts):
    // while unauthenticated, `init()` performs a full OIDC redirect to
    // Keycloak and back before the adapter settles, so the very first
    // document that renders this page is torn down mid-initialization.
    // A click processed before that round trip completes is silently
    // destroyed with the document (the adapter's login() never even
    // resolves). Gate the button on `getKeycloak()` settling instead.
    // This is purely observational — AuthProvider already starts init on
    // mount and both callers share the same init promise — so the OIDC
    // flow itself is unchanged. The button also re-enables when init
    // fails (null instance): clicking then surfaces the existing error
    // message rather than dead-ending.
    const [isReady, setIsReady] = React.useState(false);

    React.useEffect(() => {
        let cancelled = false;

        // getKeycloak() always settles (instance or null) — it catches
        // init errors internally and never rejects.
        getKeycloak().then(() => {
            if (!cancelled) {
                setIsReady(true);
            }
        });

        return () => {
            cancelled = true;
        };
    }, []);

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
                    disabled={isLoading || !isReady}
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

