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
    const handleLogin = async () => {
        const keycloak = await getKeycloak();

        if (!keycloak) return;

        await keycloak.login({
            redirectUri: window.location.origin,
        });
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
                <Button
                    type="button"
                    onClick={handleLogin}
                    className="w-full"
                >
                    Sign in with OpenLearn AI
                </Button>
            </CardContent>
        </Card>
    );
}