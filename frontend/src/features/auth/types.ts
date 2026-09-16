export interface MeResponse {
  id: string;
  email: string;
  preferred_lang: string;
  settings: Record<string, unknown>;
  roles: string[];
  keycloak_issuer: string;
  keycloak_subject: string;
}