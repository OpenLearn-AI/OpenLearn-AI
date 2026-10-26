import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { LoadingBlock } from "../components/state/LoadingBlock";

const meta = {
  title: "State/LoadingBlock",
  component: LoadingBlock,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof LoadingBlock>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    message: "Loading...",
  },
};

export const CustomMessage: Story = {
  args: {
    message: "Loading your courses...",
  },
};
