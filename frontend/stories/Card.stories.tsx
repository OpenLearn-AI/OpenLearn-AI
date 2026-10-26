import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  CardAction,
} from "../components/ui/card";
import { Button } from "../components/ui/button";

const meta = {
  title: "UI/Card",
  component: Card,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof Card>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Course Details</CardTitle>
        <CardDescription>
          View and manage your course information.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          This course covers distributed systems design and scalable architecture.
        </p>
      </CardContent>
    </Card>
  ),
};

export const WithAction: Story = {
  render: () => (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Course Details</CardTitle>
        <CardDescription>
          Manage your active learning modules.
        </CardDescription>
        <CardAction>
          <Button size="sm" variant="outline">Edit</Button>
        </CardAction>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          Advanced Software Architecture
        </p>
      </CardContent>
      <CardFooter>
        <span className="text-xs text-muted-foreground">
          Created 2026-09-29
        </span>
      </CardFooter>
    </Card>
  ),
};

export const SmallSize: Story = {
  render: () => (
    <Card size="sm" className="w-full max-w-sm">
      <CardHeader>
        <CardTitle>Compact Card</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground">
          Uses the small spacing variant.
        </p>
      </CardContent>
    </Card>
  ),
};
