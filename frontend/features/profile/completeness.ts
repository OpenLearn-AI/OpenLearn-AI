import type { Profile } from "./schemas";

/**
 * Profile-completeness derivation (Batch 1.4's real-metric inventory,
 * shared since Batch 4.4 by the dashboard facts band and the profile
 * page's aside — ONE definition so the measure can never drift
 * between the two surfaces).
 *
 * The six user-facing content fields of `ProfileResponse` (the
 * identity fields `id`/`user_id` are excluded). A field counts as
 * carried when it is non-null AND non-empty. Four fields are
 * non-nullable in the contract (guaranteed present once a profile
 * exists); `university` and `learning_style_vark` are the only
 * variable ones.
 */
export const PROFILE_FIELD_COUNT = 6;

export function countMissingProfileFields(profile: Profile): number {
    const values = [
        profile.education_level,
        profile.major,
        profile.preferred_language,
        profile.university,
        profile.learning_style_vark,
        profile.daily_available_minutes,
    ];
    const carried = values.filter(
        (value) => value !== null && String(value).trim() !== "",
    ).length;
    return PROFILE_FIELD_COUNT - carried;
}
