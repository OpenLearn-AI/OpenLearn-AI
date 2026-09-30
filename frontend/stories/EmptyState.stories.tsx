import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { EmptyState } from "../components/state/EmptyState";

const meta = {
  title: "State/EmptyState",
  component: EmptyState,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof EmptyState>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    message: "Nothing here yet.",
  },
};

export const WithAction: Story = {
  args: {
    message: "You don't have any courses yet.",
    actionHref: "/courses/new",
    actionLabel: "Create your first course",
  },
};

export const SearchEmpty: Story = {
  args: {
    message: "No courses found matching your search.",
  },
};
