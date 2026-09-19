"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useRegister } from "@/features/auth/api/useRegister";
import { registerSchema } from "@/features/auth/schemas";

export default function RegisterForm() {
  const router = useRouter();
  const registerMutation = useRegister();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [errors, setErrors] = useState<{
    email?: string;
    password?: string;
    confirmPassword?: string;
    general?: string;
  }>({});

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setErrors({});

    const result = registerSchema.safeParse({
      email,
      password,
      confirmPassword,
    });

    if (!result.success) {
      const fieldErrors = result.error.flatten().fieldErrors;

      setErrors({
        email: fieldErrors.email?.[0],
        password: fieldErrors.password?.[0],
        confirmPassword: fieldErrors.confirmPassword?.[0],
      });

      return;
    }

    try {
      await registerMutation.mutateAsync(result.data);
      router.push("/login");
    } catch (error) {
      const apiError = error as {
        status?: number;
        message?: string;
      };

      if (apiError.status === 409) {
        setErrors({
          email: "An account with this email already exists.",
        });
        return;
      }

      if (apiError.status === 422) {
        setErrors({
          general:
            apiError.message ?? "Please check your information.",
        });
        return;
      }

      setErrors({
        general:
          apiError.message ??
          "Registration failed. Please try again.",
      });
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto flex w-full max-w-md flex-col gap-5"
      noValidate
    >
      <div>
        <label
          htmlFor="register-email"
          className="mb-2 block text-sm font-medium"
        >
          Email
        </label>

        <input
          id="register-email"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="w-full rounded-md border px-3 py-2"
          aria-invalid={Boolean(errors.email)}
          aria-describedby={
            errors.email ? "register-email-error" : undefined
          }
        />

        {errors.email && (
          <p
            id="register-email-error"
            className="mt-1 text-sm text-red-600"
          >
            {errors.email}
          </p>
        )}
      </div>

      <div>
        <label
          htmlFor="register-password"
          className="mb-2 block text-sm font-medium"
        >
          Password
        </label>

        <input
          id="register-password"
          name="password"
          type="password"
          autoComplete="new-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="w-full rounded-md border px-3 py-2"
          aria-invalid={Boolean(errors.password)}
          aria-describedby={
            errors.password ? "register-password-error" : undefined
          }
        />

        {errors.password && (
          <p
            id="register-password-error"
            className="mt-1 text-sm text-red-600"
          >
            {errors.password}
          </p>
        )}
      </div>

      <div>
        <label
          htmlFor="register-confirm-password"
          className="mb-2 block text-sm font-medium"
        >
          Confirm Password
        </label>

        <input
          id="register-confirm-password"
          name="confirmPassword"
          type="password"
          autoComplete="new-password"
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          className="w-full rounded-md border px-3 py-2"
          aria-invalid={Boolean(errors.confirmPassword)}
          aria-describedby={
            errors.confirmPassword
              ? "register-confirm-password-error"
              : undefined
          }
        />

        {errors.confirmPassword && (
          <p
            id="register-confirm-password-error"
            className="mt-1 text-sm text-red-600"
          >
            {errors.confirmPassword}
          </p>
        )}
      </div>

      {errors.general && (
        <p
          role="alert"
          className="rounded-md border border-red-300 px-3 py-2 text-sm text-red-600"
        >
          {errors.general}
        </p>
      )}

      <button
        type="submit"
        disabled={registerMutation.isPending}
        className="rounded-md bg-primary px-4 py-2 text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50"
      >
        {registerMutation.isPending
          ? "Creating account..."
          : "Create account"}
      </button>
    </form>
  );
}
