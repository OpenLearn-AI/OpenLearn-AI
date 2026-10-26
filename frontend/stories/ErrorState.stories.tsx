import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { ErrorState } from "../components/state/ErrorState";

const meta = {
  title: "State/ErrorState",
  component: ErrorState,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof ErrorState>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    message: "Something went wrong.",
  },
};

export const WithRetry: Story = {
  args: {
    message: "Failed to load courses.",
    onRetry: () => console.log("retry clicked"),
    retryLabel: "Try again",
  },
};

export const CustomMessage: Story = {
  args: {
    message: "Your session has expired. Please log in again.",
  },
};
