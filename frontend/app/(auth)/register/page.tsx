"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getKeycloak } from "@/lib/keycloak";

export default function RegisterPage() {
    const handleRegister = async () => {
        const keycloak = await getKeycloak();

        if (!keycloak) return;

        await keycloak.register({
            redirectUri: `${window.location.origin}/dashboard`,
        });
    };

    return (
        <main className="relative flex min-h-screen items-center justify-center bg-background px-4 py-8">
            <Card className="w-full max-w-md">
                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl">
                        Create an account
                    </CardTitle>

                    <CardDescription>
                        Create your OpenLearn AI account
                    </CardDescription>
                </CardHeader>

                <CardContent>
                    <Button
                        type="button"
                        onClick={handleRegister}
                        className="w-full"
                    >
                        Create account
                    </Button>
                </CardContent>
            </Card>
        </main>
    );
}