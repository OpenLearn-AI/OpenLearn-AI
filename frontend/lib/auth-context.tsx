"use client";

import {
    createContext,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from "react";
import { getKeycloak } from "./keycloak";

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

        async function initializeAuth() {
            try {
                const keycloak = await getKeycloak();

                if (cancelled) {
                    return;
                }

                setIsAuthenticated(
                    Boolean(keycloak?.authenticated),
                );
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