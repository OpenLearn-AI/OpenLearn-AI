import {
  UserManager,
  WebStorageStateStore,
} from "oidc-client-ts";

export const oidcConfig = {
  authority: "http://localhost:8080/realms/openlearn",
  client_id: "openlearn-frontend",
  redirect_uri: "http://localhost:3000/login/callback",
  post_logout_redirect_uri: "http://localhost:3000/login",
  response_type: "code",
  scope: "openid profile email",

  // Renew the access token before it expires.
  automaticSilentRenew: true,
};

let userManager: UserManager | null = null;

export function createUserManager(): UserManager {
  if (typeof window === "undefined") {
    throw new Error(
      "OIDC UserManager can only be created in the browser.",
    );
  }

  if (userManager) {
    return userManager;
  }

  userManager = new UserManager({
    ...oidcConfig,

    userStore: new WebStorageStateStore({
      store: window.sessionStorage,
    }),
  });

  return userManager;
}