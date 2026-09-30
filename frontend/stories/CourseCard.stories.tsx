import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { CourseCard } from "../components/CourseCard";
import type { Course } from "../features/courses/schemas";

const meta = {
  title: "Shared/CourseCard",
  component: CourseCard,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof CourseCard>;

export default meta;

type Story = StoryObj<typeof meta>;

// Story-only fixture data — isolated, not imported into production code.
const sampleCourse: Course = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  owner_id: "550e8400-e29b-41d4-a716-446655440001",
  title: "Advanced Software Architecture",
  description:
    "Learn system design, distributed patterns, and scalable architecture principles through real-world case studies.",
  created_at: "2026-09-29T12:00:00.000Z",
};

const noDescriptionCourse: Course = {
  id: "550e8400-e29b-41d4-a716-446655440002",
  owner_id: "550e8400-e29b-41d4-a716-446655440001",
  title: "Machine Learning Basics",
  description: null,
  created_at: "2026-09-28T08:30:00.000Z",
};

const longTitleCourse: Course = {
  id: "550e8400-e29b-41d4-a716-446655440003",
  owner_id: "550e8400-e29b-41d4-a716-446655440001",
  title: "Introduction to Quantum Computing and Its Applications in Modern Cryptography and Information Theory",
  description:
    "An in-depth exploration of quantum computing principles, qubits, entanglement, and their implications for cryptography, search algorithms, and the future of computing.",
  created_at: "2026-09-27T16:45:00.000Z",
};

export const Default: Story = {
  args: {
    course: sampleCourse,
  },
};

export const NoDescription: Story = {
  args: {
    course: noDescriptionCourse,
  },
};

export const LongTitle: Story = {
  args: {
    course: longTitleCourse,
  },
};
