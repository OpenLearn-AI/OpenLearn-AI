import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { Label } from "../components/ui/label";

const meta = {
  title: "UI/Label",
  component: Label,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof Label>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    htmlFor: "example-input",
    children: "Course Title",
  },
};
