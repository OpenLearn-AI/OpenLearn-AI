"use client";

import { useMe } from "@/features/auth/api/useMe";

export function UserInfo() {
    const { data, isLoading, isError } = useMe();

    if (isLoading) {
        return (
            <p className="text-sm text-muted-foreground">Loading your profile...</p>
        );
    }

    if (isError || !data) {
        return (
            <p className="text-sm text-destructive">
                Unable to load your account information.
            </p>
        );
    }

    return (
        <div className="space-y-2">
            <p className="text-sm">
                <span className="font-medium">Email:</span> {data.email}
            </p>

            {data.roles.length === 1 ? (
                <p className="text-sm">
                    <span className="font-medium">Role:</span> {data.roles[0]}
                </p>
            ) : (
                <div className="text-sm">
                    <span className="font-medium">Roles:</span>
                    <ul className="ml-4 list-disc">
                        {data.roles.map((role) => (
                            <li key={role}>{role}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}