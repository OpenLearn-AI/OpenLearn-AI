import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";

import { LoginForm } from "@/components/auth/LoginForm";

const mockSigninRedirect = vi.fn();

vi.mock("@/lib/oidc", () => ({
  createUserManager: () => ({
    signinRedirect: mockSigninRedirect,
  }),
}));

describe("LoginForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it("renders the sign in button", () => {
    render(<LoginForm />);

    const button = screen.getByRole("button", {
      name: "Sign in",
    });

    expect(button).toBeTruthy();
    expect(button).toBeEnabled();
  });

  it("starts the OIDC login flow when sign in is clicked", async () => {
    mockSigninRedirect.mockResolvedValue(undefined);

    render(<LoginForm />);

    fireEvent.click(
      screen.getByRole("button", {
        name: "Sign in",
      }),
    );

    await waitFor(() => {
      expect(mockSigninRedirect).toHaveBeenCalledTimes(1);
    });
  });

  it("shows a loading state while redirecting", async () => {
    mockSigninRedirect.mockImplementation(
      () => new Promise<void>(() => {}),
    );

    render(<LoginForm />);

    fireEvent.click(
      screen.getByRole("button", {
        name: "Sign in",
      }),
    );

    await waitFor(() => {
      const button = screen.getByRole("button", {
        name: "Redirecting...",
      });

      expect(button).toBeTruthy();
      expect(button).toBeDisabled();
    });
  });

  it("shows an error when starting the login flow fails", async () => {
    mockSigninRedirect.mockRejectedValue(
      new Error("Unable to connect to Keycloak"),
    );

    render(<LoginForm />);

    fireEvent.click(
      screen.getByRole("button", {
        name: "Sign in",
      }),
    );

    await waitFor(() => {
      expect(
        screen.getByRole("alert"),
      ).toBeTruthy();
    });

    expect(
      screen.getByRole("alert").textContent,
    ).toContain("Unable to connect to Keycloak");

    expect(
      screen.getByRole("button", {
        name: "Sign in",
      }),
    ).toBeEnabled();
  });
});
