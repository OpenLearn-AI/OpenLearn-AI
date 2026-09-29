"use client";

import Link from "next/link";

import { ProfileForm } from "@/components/profile/ProfileForm";
import { useProfile } from "@/features/profile/api/useProfile";
import { useMe } from "@/features/auth/api/useMe";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { ErrorState } from "@/components/state/ErrorState";
import { Button } from "@/components/ui/button";

export default function ProfilePage() {
    const { data: me, isLoading: meLoading } = useMe();
    const {
        data: profile,
        isLoading: profileLoading,
        isError,
        error,
    } = useProfile();

    const isLoading = meLoading || profileLoading;

    if (isLoading) {
        return (
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
                <div className="max-w-md mx-auto">
                    <LoadingBlock message="Loading your profile data..." />
                </div>
            </main>
        );
    }

    if (isError) {
        return (
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="max-w-lg mx-auto">
                    <ErrorState
                        message={
                            error instanceof Error
                                ? error.message
                                : "Failed to load your profile. Please check your connection or session."
                        }
                    />
                </div>
            </main>
        );
    }

    const profileName = me?.email || "User";
    const profileInitial =
        typeof profileName === "string"
            ? profileName.charAt(0).toUpperCase()
            : "U";

    return (
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8 bg-background min-h-screen">
            {/* Header Banner */}
            <div className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground p-6 sm:p-8 rounded-2xl shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
                <div className="flex items-center gap-4">
                    <div className="w-16 h-16 rounded-2xl bg-primary-foreground/10 border border-primary-foreground/20 text-primary-foreground flex items-center justify-center font-bold text-2xl shadow-inner backdrop-blur-xs">
                        {profileInitial}
                    </div>
                    <div className="space-y-1">
                        <span className="bg-primary-foreground/10 text-primary-foreground/90 text-xs px-3 py-1 rounded-full font-medium">
                            Account Settings
                        </span>
                        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight pt-1">
                            {profileName}
                        </h1>
                        <p className="text-primary-foreground/80 text-xs sm:text-sm">
                            {me?.email ||
                                "Manage your account credentials and personal preferences"}
                        </p>
                    </div>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    render={<Link href="/dashboard" />}
                    className="bg-primary-foreground/10 border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/20"
                >
                    Back to Dashboard
                </Button>
            </div>

            {/* Content Layout Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left 2 Columns: Main Profile Form */}
                <div className="lg:col-span-2 bg-card rounded-2xl border border-border p-6 sm:p-8 shadow-xs space-y-6">
                    <div>
                        <h3 className="text-lg font-bold text-card-foreground">
                            {profile
                                ? "Personal Information"
                                : "Create Your Profile"}
                        </h3>
                        <p className="text-xs text-muted-foreground mt-0.5">
                            {profile
                                ? "Update your account details and profile configurations."
                                : "Complete your profile information to get started."}
                        </p>
                    </div>

                    {!profile && (
                        <div className="rounded-xl border border-border bg-muted/50 p-4">
                            <p className="text-xs text-muted-foreground">
                                Your account does not have a profile yet.
                                Complete the form below to create one.
                            </p>
                        </div>
                    )}

                    <div className="border-t border-border pt-6">
                        <ProfileForm profile={profile ?? null} />
                    </div>
                </div>

                {/* Right Column: Help Card (subscription/plan deferred) */}
                <div className="space-y-6">
                    <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-2">
                        <h3 className="font-bold text-card-foreground text-sm">
                            Need Assistance?
                        </h3>
                        <p className="text-xs text-muted-foreground leading-relaxed">
                            If you encounter any issues updating your profile
                            credentials, check your connection or reach out to
                            platform support.
                        </p>
                    </div>
                </div>
            </div>
        </main>
    );
}
