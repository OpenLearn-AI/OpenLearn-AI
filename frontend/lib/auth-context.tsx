"use client";

import {
    createContext,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from "react";
import { getKeycloak, onKeycloakRefreshError } from "./keycloak";

interface AuthContextValue {
    isAuthenticated: boolean;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextValue>({
    isAuthenticated: false,
    isLoading: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;
        let unsubscribeRefreshError: (() => void) | null = null;

        async function initializeAuth() {
            try {
                const keycloak = await getKeycloak();

                if (cancelled) {
                    return;
                }

                setIsAuthenticated(
                    Boolean(keycloak?.authenticated),
                );

                // W1: when the Keycloak token refresh fails, reflect
                // the expired session in React state so the existing
                // AuthGuard redirect (unchanged) also reacts. The
                // cache-clearing half of the recovery lives in
                // lib/query-provider.tsx.
                if (keycloak) {
                    unsubscribeRefreshError = onKeycloakRefreshError(() => {
                        if (!cancelled) {
                            setIsAuthenticated(false);
                        }
                    });
                }
            } catch (error) {
                console.error(
                    "Failed to initialize authentication:",
                    error,
                );

                if (!cancelled) {
                    setIsAuthenticated(false);
                }
            } finally {
                if (!cancelled) {
                    setIsLoading(false);
                }
            }
        }

        initializeAuth();

        return () => {
            cancelled = true;
            unsubscribeRefreshError?.();
        };
    }, []);

    return (
        <AuthContext.Provider
            value={{
                isAuthenticated,
                isLoading,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}