/**
 * Profile query-key factory (D5).
 *
 * Stable, hierarchical keys for the profile domain. Follows the same
 * convention as `courseKeys` and `authKeys`.
 */

export const profileKeys = {
    all: ["profile"] as const,
    current: () => [...profileKeys.all, "current"] as const,
};
