"use client";

import { ProfileForm } from "@/components/profile/ProfileForm";
import { useProfile } from "@/features/profile/api/useProfile";

export default function ProfilePage() {
    const {
        data: profile,
        isLoading,
        isError,
        error,
    } = useProfile();

    if (isLoading) {
        return (
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-2xl">
                    <div className="rounded-lg border p-6 text-center">
                        Loading profile...
                    </div>
                </div>
            </main>
        );
    }

    if (isError) {
        return (
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-2xl">
                    <div
                        role="alert"
                        className="rounded-lg border p-6 text-center text-destructive"
                    >
                        {error instanceof Error
                            ? error.message
                            : "Failed to load profile."}
                    </div>
                </div>
            </main>
        );
    }

    if (!profile) {
        return (
            <main className="min-h-screen bg-background px-4 py-8">
                <div className="mx-auto max-w-2xl">
                    <div className="rounded-lg border p-6 text-center text-muted-foreground">
                        Profile not found.
                    </div>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-background px-4 py-8">
            <div className="mx-auto max-w-2xl space-y-6">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        Profile
                    </h1>

                    <p className="mt-2 text-muted-foreground">
                        Manage your learning profile information.
                    </p>
                </div>

                <div className="rounded-lg border bg-card p-6">
                    <ProfileForm profile={profile} />
                </div>
            </div>
        </main>
    );
}