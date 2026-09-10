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
    <main className="min-h-screen bg-background p-8">
      <div className="mx-auto max-w-4xl">

        {/* Header */}
        <div className="mb-8">
          <Badge className="mb-3">
            OpenLearn AI
          </Badge>

          <h1 className="text-3xl font-bold tracking-tight">
            Design System
          </h1>

          <p className="mt-2 text-muted-foreground">
            Testing our colors, typography, spacing, and UI components.
          </p>
        </div>

        {/* Components */}
        <div className="grid gap-6 md:grid-cols-2">

          {/* Learning Card */}
          <Card>
            <CardHeader>
              <CardTitle>Start Learning</CardTitle>

              <CardDescription>
                Continue your learning journey with AI.
              </CardDescription>
            </CardHeader>

            <CardContent>
              <div className="space-y-4">

                <Input
                  placeholder="Enter your course name..."
                />

                <div className="flex gap-3">
                  <Button>
                    Start Learning
                  </Button>

                  <Button variant="outline">
                    Explore
                  </Button>
                </div>

              </div>
            </CardContent>
          </Card>

          {/* UI Preview Card */}
          <Card>
            <CardHeader>
              <CardTitle>UI Preview</CardTitle>

              <CardDescription>
                Core components of our design system.
              </CardDescription>
            </CardHeader>

            <CardContent>
              <div className="flex flex-wrap gap-3">

                <Badge>
                  Primary
                </Badge>

                <Badge variant="secondary">
                  Secondary
                </Badge>

                <Badge variant="outline">
                  Outline
                </Badge>

                <Button variant="ghost">
                  Ghost Button
                </Button>

              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </main>
  );
}

/*
cd frontend
npm run dev  
Local: http://localhost:3000
document.documentElement.classList.add("dark")
*/ 