import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { ThemeToggle } from "../components/ui/theme-toggle";

const meta = {
  title: "UI/ThemeToggle",
  component: ThemeToggle,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof ThemeToggle>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
