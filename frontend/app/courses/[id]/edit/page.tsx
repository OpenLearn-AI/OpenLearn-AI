import { CourseTable } from "@/components/courses/CourseTable";

export default function CoursesPage() {
    return (
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Courses</h1>
                    <p className="text-sm text-slate-500 mt-1">Browse the available OpenLearn AI courses.</p>
                </div>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
                <CourseTable />
            </div>
        </main>
    );
}