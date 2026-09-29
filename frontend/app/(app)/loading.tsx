import { LoadingBlock } from "@/components/state/LoadingBlock";

/**
 * Route-level loading boundary for the `(app)` route group (D11).
 * Renders while any `(app)` route segment is streaming its content.
 */
export default function AppLoading() {
    return (
        <div className="flex min-h-screen items-center justify-center bg-background px-4 py-8">
            <LoadingBlock message="Loading..." />
        </div>
    );
}
