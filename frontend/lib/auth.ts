import type { User } from "oidc-client-ts";

import { createUserManager } from "@/lib/oidc";

export async function getCurrentUser(): Promise<User | null> {
  const userManager = createUserManager();
  return userManager.getUser();
}

export async function isAuthenticated(): Promise<boolean> {
  const user = await getCurrentUser();

  return Boolean(user && !user.expired);
}

export async function logout(): Promise<void> {
  const userManager = createUserManager();

  await userManager.signoutRedirect();
}