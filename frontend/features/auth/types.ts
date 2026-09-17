export interface MeResponse {
    id: string;
    email: string;
    preferred_lang: string;
    settings: Record<string, unknown>;
    roles: string[];
    keycloak: {
        issuer: string;
        subject: string;
    };
}