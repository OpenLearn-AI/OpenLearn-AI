import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { Field } from "../components/ui/field";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Select } from "../components/ui/select";

const meta = {
  title: "UI/Field",
  component: Field,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof Field>;

export default meta;

type Story = StoryObj<typeof meta>;

export const WithInput: Story = {
  args: {
    label: "Title",
    htmlFor: "course-title",
    children: <Input id="course-title" placeholder="Course title" />,
  },
};

export const WithError: Story = {
  args: {
    label: "Title",
    htmlFor: "course-title-error",
    error: "Title is required",
    children: <Input id="course-title-error" placeholder="Course title" aria-invalid />,
  },
};

export const WithHint: Story = {
  args: {
    label: "Description",
    htmlFor: "course-description",
    hint: "Max 255 characters",
    children: <Textarea id="course-description" placeholder="Course description" />,
  },
};

export const WithSelect: Story = {
  args: {
    label: "Preferred Language",
    htmlFor: "preferred-language",
    children: (
      <Select id="preferred-language">
        <option value="en">English</option>
        <option value="ar">Arabic</option>
      </Select>
    ),
  },
};
