/**
 * Material query-key factory (Batch 4.3, D5 convention).
 *
 * Stable, hierarchical keys for the material domain. Follows the same
 * convention as `courseKeys` and `authKeys`: an `all` root, then
 * per-scope branches. The registration step invalidates the owning
 * course's list; the per-material status polls live under
 * `status(materialId)`.
 */

export const materialKeys = {
    all: ["materials"] as const,
    lists: () => [...materialKeys.all, "list"] as const,
    list: (courseId: string) => [...materialKeys.lists(), courseId] as const,
    statuses: () => [...materialKeys.all, "status"] as const,
    status: (materialId: string) =>
        [...materialKeys.statuses(), materialId] as const,
};
