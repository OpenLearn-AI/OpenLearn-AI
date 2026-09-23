"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { getKeycloak } from "@/lib/keycloak";

export function LoginForm() {
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

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

            await keycloak.login({
                redirectUri: window.location.origin,
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

