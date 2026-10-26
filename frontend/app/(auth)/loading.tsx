import { LoadingBlock } from "@/components/state/LoadingBlock";

/**
 * Route-level loading boundary for the `(auth)` route group (S8).
 *
 * Mirrors the `(app)` boundary using the shared async-state kit (the
 * only sanctioned loading presentation). The auth layout already
 * centers and sizes its children, so — unlike the `(app)` boundary —
 * no full-screen wrapper is added here.
 */
export default function AuthLoading() {
    return <LoadingBlock message="Loading..." />;
}
