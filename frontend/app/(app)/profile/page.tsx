"use client";

import { ProfileForm } from "@/components/profile/ProfileForm";
import { useProfile } from "@/features/profile/api/useProfile";
import { useMe } from "@/features/auth/api/useMe";
import Link from "next/link";

export default function ProfilePage() {
    const { data: me } = useMe();
    const {
        data: profile,
        isLoading,
        isError,
        error,
    } = useProfile();

    if (isLoading) {
        return (
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
                <div className="bg-white rounded-2xl border border-slate-200 p-8 text-slate-500 shadow-xs max-w-md mx-auto flex items-center justify-center gap-3">
                    <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                    <span>Loading your profile data...</span>
                </div>
            </main>
        );
    }

    if (isError) {
        return (
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="bg-red-50 rounded-2xl border border-red-200 p-8 text-center text-red-600 shadow-xs max-w-lg mx-auto space-y-2" role="alert">
                    <h3 className="font-bold text-lg">Failed to Load Profile</h3>
                    <p className="text-sm">{error instanceof Error ? error.message : "Please check your network connection or session."}</p>
                </div>
            </main>
        );
    }

    const profileName = me?.email || "User";
    const profileInitial = typeof profileName === "string" ? profileName.charAt(0).toUpperCase() : "U";

    return (
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8 bg-slate-50/50 min-h-screen">

            {/* Header Banner */}
            <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-indigo-700 text-white p-6 sm:p-8 rounded-2xl shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
                <div className="flex items-center gap-4">
                    <div className="w-16 h-16 rounded-2xl bg-white/10 border border-white/20 text-white flex items-center justify-center font-bold text-2xl shadow-inner backdrop-blur-xs">
                        {profileInitial}
                    </div>
                    <div className="space-y-1">
                        <span className="bg-white/10 text-indigo-100 text-xs px-3 py-1 rounded-full font-medium">
                            Account Settings
                        </span>
                        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight pt-1">
                            {profileName}
                        </h1>
                        <p className="text-indigo-100 text-xs sm:text-sm">
                            {me?.email || "Manage your account credentials and personal preferences"}
                        </p>
                    </div>
                </div>
                <Link href="/dashboard" className="bg-white/10 hover:bg-white/20 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition border border-white/10">
                    - Back to Dashboard
                </Link>
            </div>

            {/* Content Layout Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left 2 Columns: Main Profile Form */}
                <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
                    <div>
                        <h3 className="text-lg font-bold text-slate-900">
                            {profile ? "Personal Information" : "Create Your Profile"}
                        </h3>
                        <p className="text-xs text-slate-500 mt-0.5">
                            {profile
                                ? "Update your account details and profile configurations."
                                : "Complete your profile information to get started."}
                        </p>
                    </div>

                    {!profile && (
                        <div className="rounded-xl border border-indigo-100 bg-indigo-50 p-4">
                            <p className="text-xs text-indigo-900">
                                Your account does not have a profile yet. Complete the form below to create one.
                            </p>
                        </div>
                    )}

                    <div className="border-t border-slate-100 pt-6">
                        <ProfileForm profile={profile ?? null} />
                    </div>
                </div>

                {/* Right Column: Account Status & Info Cards */}
                <div className="space-y-6">

                    {/* Cloud Platform Status Card */}
                    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
                        <h3 className="font-bold text-slate-900 text-base border-b border-slate-100 pb-3">Subscription & Plan</h3>
                        <div className="space-y-3 text-xs">
                            <div className="flex justify-between items-center py-1.5 border-b border-slate-50">
                                <span className="text-slate-500">Edition</span>
                                <span className="font-semibold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-lg">Cloud Adaptive</span>
                            </div>
                            <div className="flex justify-between items-center py-1.5 border-b border-slate-50">
                                <span className="text-slate-500">AI Engine RAG</span>
                                <span className="font-semibold text-emerald-600">Active</span>
                            </div>
                            <div className="flex justify-between items-center py-1.5">
                                <span className="text-slate-500">Knowledge Graph</span>
                                <span className="font-semibold text-slate-800">Enabled</span>
                            </div>
                        </div>
                    </div>

                    {/* Quick Support / Help Box */}
                    <div className="bg-gradient-to-br from-indigo-50 to-slate-50 rounded-2xl border border-indigo-100 p-6 shadow-xs space-y-2">
                        <h3 className="font-bold text-indigo-900 text-sm">Need Assistance?</h3>
                        <p className="text-xs text-slate-600 leading-relaxed">
                            If you encounter any issues updating your profile credentials, check your connection or reach out to platform support.
                        </p>
                    </div>
                </div>
            </div>
        </main>
    );
}