import { CourseTable } from "@/components/courses/CourseTable";

export default function CoursesPage() {
    return (
        <main className="min-h-screen bg-background px-4 py-8">
            <div className="mx-auto max-w-6xl space-y-6">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        Courses
                    </h1>

                    <p className="mt-2 text-muted-foreground">
                        Browse the available OpenLearn AI courses.
                    </p>
                </div>

                <CourseTable />
            </div>
        </main>
    );
}