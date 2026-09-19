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

        getKeycloak().then((keycloak) => {
            if (cancelled || !keycloak) return;

            setIsAuthenticated(!!keycloak.authenticated);
            setIsLoading(false);
        });

        return () => {
            cancelled = true;
        };
    }, []);

    return (
        <AuthContext.Provider value={{ isAuthenticated, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}