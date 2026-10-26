import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { Input } from "../components/ui/input";

const meta = {
  title: "UI/Input",
  component: Input,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof Input>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    placeholder: "Enter course title...",
    "aria-label": "Course title",
  },
};

export const WithValue: Story = {
  args: {
    value: "Advanced Software Architecture",
    readOnly: true,
    "aria-label": "Course title",
  },
};

export const Disabled: Story = {
  args: {
    placeholder: "Disabled input",
    disabled: true,
    "aria-label": "Course title",
  },
};

export const Invalid: Story = {
  args: {
    placeholder: "Invalid input",
    "aria-invalid": true,
    "aria-label": "Course title",
  },
};

export const WithType: Story = {
  args: {
    type: "number",
    placeholder: "0",
    min: 1,
    max: 1440,
    "aria-label": "Daily available minutes",
  },
};
