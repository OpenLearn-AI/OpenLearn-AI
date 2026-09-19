import { useMutation } from "@tanstack/react-query";

import { apiRequest } from "@/lib/api";
import type { RegisterFormValues } from "../schemas";

type RegisterResponse = {
  message: string;
  email: string;
};

async function registerUser(
  values: RegisterFormValues,
): Promise<RegisterResponse> {
  return apiRequest<RegisterResponse>("/auth/register", {
    method: "POST",
    auth: false,
    body: JSON.stringify({
      email: values.email,
      password: values.password,
      confirm_password: values.confirmPassword,
    }),
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: registerUser,
  });
}
