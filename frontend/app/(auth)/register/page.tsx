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
        <main className="relative min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center justify-center p-4">
            <div className="text-center mb-8">
                <h1 className="text-2xl sm:text-3xl font-bold tracking-wider text-white">OPENLEARN</h1>
            </div>

            <div className="w-full max-w-md bg-white text-slate-800 p-8 rounded-2xl shadow-xl border border-slate-200">
                <div className="mb-6 space-y-1">
                    <h2 className="text-2xl font-bold text-slate-900">Create an account</h2>
                    <p className="text-sm text-slate-500">Create your OpenLearn AI account</p>
                </div>

                <Button
                    type="button"
                    onClick={handleRegister}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-xl transition"
                >
                    Create account
                </Button>
            </div>
        </main>
    );
}