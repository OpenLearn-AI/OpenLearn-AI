import { CourseForm } from "@/components/courses/CourseForm";

export default function NewCoursePage() {
    return (
        <main className="min-h-screen bg-background px-4 py-8">
            <div className="mx-auto max-w-2xl space-y-6">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        Create Course
                    </h1>

                    <p className="mt-2 text-muted-foreground">
                        Create a new course for OpenLearn AI.
                    </p>
                </div>

                <CourseForm mode="create" />
            </div>
        </main>
    );
}