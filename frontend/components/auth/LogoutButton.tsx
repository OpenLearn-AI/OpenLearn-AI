"use client";

import { useQueryClient } from "@tanstack/react-query";
import { getKeycloak } from "@/lib/keycloak";

export function LogoutButton() {
    const queryClient = useQueryClient();

    async function handleLogout() {
        const keycloak = await getKeycloak();

        if (!keycloak) {
            return;
        }

        queryClient.clear();

        await keycloak.logout({
            redirectUri: `${window.location.origin}/login`,
        });
    }

    return (
        <button
            onClick={handleLogout}
            className="group inline-flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-2 text-sm font-medium text-destructive transition-all duration-200 hover:bg-destructive hover:text-destructive-foreground active:scale-[0.98]"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="transition-transform duration-200 group-hover:translate-x-0.5"
            >
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Logout
        </button>
    );
}
