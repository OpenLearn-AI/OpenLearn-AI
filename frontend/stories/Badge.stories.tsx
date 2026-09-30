import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { Badge } from "../components/ui/badge";

const meta = {
  title: "UI/Badge",
  component: Badge,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof Badge>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: "Course",
  },
};

export const Secondary: Story = {
  args: {
    variant: "secondary",
    children: "Active",
  },
};

export const Destructive: Story = {
  args: {
    variant: "destructive",
    children: "Failed",
  },
};

export const Outline: Story = {
  args: {
    variant: "outline",
    children: "Draft",
  },
};
