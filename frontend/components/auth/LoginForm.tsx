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
import { createUserManager } from "@/lib/oidc";

export function LoginForm() {
    const [isLoading, setIsLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

    const handleLogin = async () => {
        try {
            setIsLoading(true);
            setError(null);

            const userManager = createUserManager();

            await userManager.signinRedirect();
        } catch (error) {
            console.error("Failed to start login:", error);

            const message =
                error instanceof Error ? error.message : String(error);

            setError(message);
            setIsLoading(false);
        }
    };

    return (
        <Card className="w-full max-w-md">
            <CardHeader className="space-y-1">
                <CardTitle className="text-2xl">Welcome back</CardTitle>

                <CardDescription>
                    Sign in to your OpenLearn AI account
                </CardDescription>
            </CardHeader>

            <CardContent>
                <div className="space-y-5">
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
                        className="w-full"
                        onClick={handleLogin}
                        disabled={isLoading}
                    >
                        {isLoading ? "Redirecting..." : "Sign in"}
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}