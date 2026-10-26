import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { expect, within } from "storybook/test";

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

/**
 * Batch 4.2 (Swiss Editorial Grid): the card is a ruled index entry.
 * The play pins the presentation contract the courses-crud E2E and
 * the design depend on — the title as an h2 (pinned only on
 * /courses, and this is the /courses entry), the two quiet actions
 * with their pinned accessible names and real routes, the mono ISO
 * date, and the RETIRED chrome: no "Course" pill and no
 * "No description" filler (a null description renders nothing).
 *
 * Batch 4.2 correction A8: the entry's TITLE is now the primary
 * link to the course hub (the largest natural target in the quiet
 * title-link grammar) — pinned here with its real route, with the
 * heading level and accessible name unchanged.
 */
export const Default: Story = {
  args: {
    course: sampleCourse,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // The title is the entry's h2 (the /courses heading-level pin)...
    await expect(
      canvas.getByRole("heading", {
        level: 2,
        name: "Advanced Software Architecture",
      }),
    ).toBeVisible();
    // ...and (A8) the title itself is the primary link to the hub.
    const titleLink = canvas.getByRole("link", {
      name: "Advanced Software Architecture",
    });
    await expect(titleLink).toHaveAttribute(
      "href",
      "/courses/550e8400-e29b-41d4-a716-446655440000",
    );

    // Both actions are real links with their pinned names and routes.
    const edit = canvas.getByRole("link", { name: "Edit" });
    await expect(edit).toHaveAttribute(
      "href",
      "/courses/550e8400-e29b-41d4-a716-446655440000/edit",
    );
    const hub = canvas.getByRole("link", { name: "Open Hub →" });
    await expect(hub).toHaveAttribute(
      "href",
      "/courses/550e8400-e29b-41d4-a716-446655440000",
    );

    // The created date renders as a machine-readable <time> with the
    // ISO calendar date as its visible mono text.
    const time = canvas.getByText("2026-09-29");
    await expect(time.closest("time")).toHaveAttribute(
      "dateTime",
      "2026-09-29T12:00:00.000Z",
    );

    // Retired chrome stays retired: no "Course" pill on the entry.
    await expect(canvas.queryByText("Course")).toBeNull();
  },
};

export const NoDescription: Story = {
  args: {
    course: noDescriptionCourse,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await expect(
      canvas.getByRole("heading", { level: 2, name: "Machine Learning Basics" }),
    ).toBeVisible();

    // D9: a null description renders NOTHING — the "No description"
    // filler is retired (absence is the truth).
    await expect(canvas.queryByText(/No description/i)).toBeNull();
  },
};

export const LongTitle: Story = {
  args: {
    course: longTitleCourse,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Long titles wrap naturally at the entry's width; the
    // description clamps at three lines so entries cannot grow
    // unbounded (the clamp itself is a rendered-verification check —
    // here we pin that the full title and the clamped description
    // both render).
    const heading = canvas.getByRole("heading", { level: 2 });
    await expect(heading).toHaveTextContent(longTitleCourse.title);
    await expect(
      canvas.getByText(/quantum computing principles/i),
    ).toBeVisible();
  },
};
