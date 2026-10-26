import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { Select } from "../components/ui/select";

const meta = {
  title: "UI/Select",
  component: Select,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof Select>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    defaultValue: "en",
    "aria-label": "Preferred language",
    children: [
      <option key="en" value="en">English</option>,
      <option key="ar" value="ar">Arabic</option>,
    ],
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
    "aria-label": "Preferred language",
    children: [
      <option key="en" value="en">English</option>,
      <option key="ar" value="ar">Arabic</option>,
    ],
  },
};

export const Invalid: Story = {
  args: {
    "aria-invalid": true,
    "aria-label": "Preferred language",
    children: [
      <option key="en" value="en">English</option>,
      <option key="ar" value="ar">Arabic</option>,
    ],
  },
};
