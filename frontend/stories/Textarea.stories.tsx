import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { Textarea } from "../components/ui/textarea";

const meta = {
  title: "UI/Textarea",
  component: Textarea,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof Textarea>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    placeholder: "Enter course description...",
    "aria-label": "Course description",
  },
};

export const WithValue: Story = {
  args: {
    value: "This course covers the fundamentals of distributed systems design.",
    readOnly: true,
    "aria-label": "Course description",
  },
};

export const Disabled: Story = {
  args: {
    placeholder: "Disabled textarea",
    disabled: true,
    "aria-label": "Course description",
  },
};

export const Invalid: Story = {
  args: {
    placeholder: "Invalid textarea",
    "aria-invalid": true,
    "aria-label": "Course description",
  },
};
