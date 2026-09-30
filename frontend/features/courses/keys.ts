/**
 * Course query-key factory (D5).
 *
 * Stable, hierarchical keys for the course domain. Every course query
 * and mutation references keys from this module so that mutations can
 * invalidate the right cache entries by calling `queryClient` with
 * `courseKeys.all`, `courseKeys.lists()`, or `courseKeys.detail(id)`.
 *
 * Convention for new domains: copy this file, rename the prefix,
 * keep the `all` / `lists()` / `detail(id)` shape.
 */

export const courseKeys = {
    all: ["courses"] as const,
    lists: () => [...courseKeys.all, "list"] as const,
    list: (filters?: { search?: string }) =>
        [...courseKeys.lists(), filters ?? {}] as const,
    details: () => [...courseKeys.all, "detail"] as const,
    detail: (id: string) => [...courseKeys.details(), id] as const,
};
