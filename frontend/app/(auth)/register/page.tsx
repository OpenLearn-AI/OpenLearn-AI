"use client";

import { Button } from "@/components/ui/button";
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
        <>
            {/* Brand Header */}
            <div className="text-center mb-8">
                <h1 className="text-2xl sm:text-3xl font-bold tracking-wider text-foreground">OPENLEARN</h1>
            </div>

            <div className="w-full max-w-md bg-card text-card-foreground p-8 rounded-2xl shadow-xl border border-border">
                <div className="mb-6 space-y-1">
                    <h2 className="text-2xl font-bold text-card-foreground">Create an account</h2>
                    <p className="text-sm text-muted-foreground">Create your OpenLearn AI account</p>
                </div>

                <Button
                    type="button"
                    onClick={handleRegister}
                    className="w-full font-medium py-2.5 rounded-xl transition"
                >
                    Create account
                </Button>
            </div>
        </>
    );
}
