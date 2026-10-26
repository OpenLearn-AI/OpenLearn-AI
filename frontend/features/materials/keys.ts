/**
 * Material query-key factory (Batch 4.3, D5 convention; the pages
 * branch added in Batch 4.5).
 *
 * Stable, hierarchical keys for the material domain. Follows the same
 * convention as `courseKeys` and `authKeys`: an `all` root, then
 * per-scope branches. The registration step invalidates the owning
 * course's list; the per-material status polls live under
 * `status(materialId)`; the extracted-text viewer's paginated
 * page-list windows live under `pages(materialId)` — a reprocess
 * invalidates that whole branch (a re-run may change the stored text
 * under the Week 9 keep-more-pages rule).
 */

export const materialKeys = {
    all: ["materials"] as const,
    lists: () => [...materialKeys.all, "list"] as const,
    list: (courseId: string) => [...materialKeys.lists(), courseId] as const,
    pages: (materialId: string) =>
        [...materialKeys.all, "pages", materialId] as const,
    statuses: () => [...materialKeys.all, "status"] as const,
    status: (materialId: string) =>
        [...materialKeys.statuses(), materialId] as const,
};
