/**
 * Auth query-key factory (D5).
 *
 * Stable, hierarchical keys for the auth domain. Follows the same
 * convention as `courseKeys`: `all` root, then per-scope branches.
 */

export const authKeys = {
    all: ["auth"] as const,
    me: () => [...authKeys.all, "me"] as const,
};
