import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function Home() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">

        {/* Sidebar */}
        <aside className="hidden w-64 shrink-0 border-r bg-card lg:flex lg:flex-col">
          <div className="flex h-16 items-center border-b px-6">
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground font-bold">
                O
              </div>
              <span className="text-lg font-bold">
                OpenLearn
              </span>
            </div>
          </div>

          <nav className="flex-1 space-y-1 p-4">
            <Button variant="secondary" className="w-full justify-start">
              Dashboard
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              My Courses
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              AI Assistant
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              Progress
            </Button>
            <div className="my-4 border-t" />
            <Button variant="ghost" className="w-full justify-start">
              Settings
            </Button>
          </nav>

          <div className="border-t p-4">
            <div className="rounded-xl bg-muted p-4">
              <p className="text-sm font-medium">Need help?</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Ask the AI assistant about your courses.
              </p>
              <Button size="sm" className="mt-3 w-full">
                Ask AI
              </Button>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex min-w-0 flex-1 flex-col">

          {/* Top Navigation */}
          <header className="flex h-16 items-center justify-between border-b bg-background px-6">
            <div>
              <p className="text-sm text-muted-foreground">
                Admin workspace / Dashboard
              </p>
            </div>

            <div className="flex items-center gap-3">
              <Button variant="ghost" size="icon">
                🔔
              </Button>
              <div className="hidden text-right sm:block">
                <p className="text-sm font-medium">Ibrahim</p>
                <p className="text-xs text-muted-foreground">AI Student</p>
              </div>
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">
                IM
              </div>
            </div>
          </header>

          {/* Dashboard */}
          <div className="flex-1 bg-background p-4 sm:p-6 lg:p-8">
            <div className="mx-auto max-w-7xl space-y-6">

              {/* Hero */}
              <section className="relative overflow-hidden rounded-2xl border bg-card p-6 shadow-sm sm:p-8">
                <div className="relative z-10 max-w-2xl">
                  <Badge className="mb-4">OpenLearn AI</Badge>
                  <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
                    Keep learning.
                    <br />
                    Let AI guide you.
                  </h1>
                  <p className="mt-4 max-w-xl text-sm leading-6 text-muted-foreground sm:text-base">
                    Continue your courses, track your progress, and use AI to understand difficult concepts faster.
                  </p>
                  <div className="mt-6 flex flex-wrap gap-3">
                    <Button>Continue Learning</Button>
                    <Button variant="outline">Explore Courses</Button>
                  </div>
                </div>
              </section>

              {/* Stats */}
              <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <StatCard label="Active Courses" value="4" description="Currently learning" />
                <StatCard label="Overall Progress" value="68%" description="Across your courses" />
                <StatCard label="Learning Hours" value="24h" description="This month" />
                <StatCard label="Completed" value="12" description="Lessons completed" />
              </section>

              {/* Main Grid */}
              <section className="grid gap-6 lg:grid-cols-3">
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>Continue Learning</CardTitle>
                        <CardDescription>Pick up where you left off.</CardDescription>
                      </div>
                      <Badge variant="secondary">72% Complete</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="rounded-xl border bg-card p-5">
                      <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                          <Badge variant="outline">Machine Learning</Badge>
                          <h3 className="mt-3 text-xl font-semibold">Machine Learning Fundamentals</h3>
                          <p className="mt-1 text-sm text-muted-foreground">Chapter 7 · Neural Networks</p>
                        </div>
                        <Button>Continue</Button>
                      </div>
                      <div className="mt-5">
                        <div className="mb-2 flex justify-between text-xs">
                          <span className="text-muted-foreground">Course progress</span>
                          <span className="font-medium">72%</span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-muted">
                          <div className="h-full rounded-full bg-primary" style={{ width: "72%" }} />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Weekly Goal</CardTitle>
                    <CardDescription>Your learning activity</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-center py-6">
                      <div className="flex h-36 w-36 items-center justify-center rounded-full border-8 border-primary/20">
                        <div className="text-center">
                          <p className="text-3xl font-bold">76%</p>
                          <p className="text-xs text-muted-foreground">completed</p>
                        </div>
                      </div>
                    </div>
                    <p className="text-center text-sm text-muted-foreground">3.8 / 5 hours this week</p>
                  </CardContent>
                </Card>
              </section>

              {/* AI Assistant */}
              <section>
                <Card className="overflow-hidden border-primary/20 bg-card">
                  <CardContent className="p-6 sm:p-8">
                    <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-center">
                      <div>
                        <Badge className="mb-3">AI Learning Assistant</Badge>
                        <h2 className="text-2xl font-bold">Stuck on something?</h2>
                        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
                          Ask questions about your current course, get explanations, examples, or help understanding difficult concepts.
                        </p>
                        <div className="mt-5 flex flex-col gap-3 sm:flex-row">
                          <Input placeholder="Ask something about Machine Learning..." className="sm:max-w-xl bg-background" />
                          <Button>Ask AI</Button>
                        </div>
                      </div>
                      <div className="hidden h-24 w-24 items-center justify-center rounded-2xl bg-primary/10 text-4xl lg:flex">
                        ✦
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </section>

              {/* Recommended Courses */}
              <section>
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold">Recommended for You</h2>
                    <p className="text-sm text-muted-foreground">Courses based on your learning journey.</p>
                  </div>
                  <Button variant="ghost">View all</Button>
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <CourseCard category="Artificial Intelligence" title="Deep Learning with PyTorch" description="Build neural networks and practical AI models." progress="32%" />
                  <CourseCard category="Data Science" title="Data Analysis with Python" description="Learn data processing, visualization, and analysis." progress="18%" />
                  <CourseCard category="AI Engineering" title="Building AI Applications" description="Turn AI models into production-ready applications." progress="0%" />
                </div>
              </section>

            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

function StatCard({ label, value, description }: { label: string; value: string; description: string }) {
  return (
    <Card>
      <CardContent className="p-5">
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="mt-2 text-3xl font-bold tracking-tight">{value}</p>
        <p className="mt-1 text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}

function CourseCard({ category, title, description, progress }: { category: string; title: string; description: string; progress: string }) {
  return (
    <Card className="transition-all hover:-translate-y-1 hover:shadow-md">
      <CardHeader>
        <Badge variant="secondary" className="w-fit">{category}</Badge>
        <CardTitle className="mt-2">{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-2 flex justify-between text-xs">
          <span className="text-muted-foreground">Progress</span>
          <span className="font-medium">{progress}</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-muted">
          <div className="h-full rounded-full bg-primary" style={{ width: progress }} />
        </div>
        <Button variant="outline" className="mt-4 w-full">View Course</Button>
      </CardContent>
    </Card>
  );
}
/*
cd frontend
npm run dev  
Local: http://localhost:3000
document.documentElement.classList.add("dark")
Username: week5test@example.com
Password: Test1234!
registerPassword: Ibrahim8
*/ 