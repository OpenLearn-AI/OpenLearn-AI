"use client";

import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Field } from "@/components/ui/field";
import {
    profileSchema,
    type Profile,
    type ProfileFormValues,
} from "@/features/profile/schemas";
import { profileKeys } from "@/features/profile/keys";
import { useUpdateProfile } from "@/features/profile/api/useProfileMutation";

/**
 * First-login profile setup wizard (Batch 4.1 — owner decisions Q2/Q3).
 *
 * Contract rules (verified against `docs/openapi.json` and the existing
 * schema layer — nothing invented):
 *   - `PUT /v1/users/me` is a FULL-REPLACEMENT upsert: every call must
 *     carry all four required fields; omitted optional fields
 *     (`university`, `learning_style_vark`) are cleared. The wizard
 *     therefore accumulates all answers client-side and issues exactly
 *     ONE `PUT` at the final step — per-step partial PUTs would erase
 *     earlier answers.
 *   - Completion semantics (Q2): a missing profile is the API's 404,
 *     which `useProfile` surfaces as `null`; an existing profile (200)
 *     prefills the wizard (a user who revisits `/onboarding` edits
 *     rather than erases). No client-only completion flag exists or is
 *     created.
 *
 * UX rules (Q3): three manageable steps, explicit progress, backward
 * navigation that never loses entered values, per-step Zod validation
 * from the shared `profileSchema` (single source of truth with
 * `ProfileForm`), explicit saving/success/failure states, no success
 * claim before the API confirms, and a retry path that preserves every
 * entered value.
 *
 * Redirect safety: the CALLER owns navigation — the wizard reports the
 * confirmed save through its `onSaved` callback, and the onboarding
 * page navigates to the `safeRedirectTarget`-validated destination
 * (defaulting to `/dashboard`). Before reporting, the wizard writes the
 * server's response into the profile cache (`setQueryData`), so the
 * `(app)` gate immediately sees the existing profile instead of
 * bouncing back to the wizard (the invalidation's refetch then confirms
 * against the API). Keeping `next/navigation` out of the wizard also
 * makes the component renderable in any provider context (stories
 * include it without an App Router mock).
 */

const STEPS = [
    { title: "About your studies" },
    { title: "Your study rhythm" },
    { title: "Optional details & review" },
] as const;

/**
 * Per-step validation slices of the shared profile schema. Each step
 * validates only its own fields (at the step boundary, before moving
 * on); the final save re-validates the full payload with the complete
 * `profileSchema`.
 */
const STEP_SCHEMAS = [
    profileSchema.pick({ education_level: true, major: true }),
    profileSchema.pick({
        daily_available_minutes: true,
        preferred_language: true,
    }),
    profileSchema.pick({ university: true, learning_style_vark: true }),
] as const;

type FieldErrors = Partial<Record<keyof ProfileFormValues, string>>;

function issuesToFieldErrors(
    issues: { path: (string | number | symbol)[]; message: string }[],
): FieldErrors {
    const fieldErrors: FieldErrors = {};
    for (const issue of issues) {
        const field = issue.path[0] as keyof ProfileFormValues | undefined;
        if (field && !fieldErrors[field]) {
            fieldErrors[field] = issue.message;
        }
    }
    return fieldErrors;
}

export function ProfileSetupWizard({
    profile,
    onSaved,
}: {
    profile: Profile | null;
    /** Called exactly once, after the API has confirmed the save and
     * the profile cache holds the server's response. The caller owns
     * the navigation (and the validated destination). */
    onSaved: () => void;
}) {
    const queryClient = useQueryClient();
    const updateProfile = useUpdateProfile();

    // Accumulated answers — kept as raw strings in state and converted
    // once, when the payload is assembled. Values survive back/forward
    // navigation and a failed save by construction (single state owner).
    const [educationLevel, setEducationLevel] = useState(
        profile?.education_level ?? "",
    );
    const [major, setMajor] = useState(profile?.major ?? "");
    const [dailyAvailableMinutes, setDailyAvailableMinutes] = useState(
        profile ? String(profile.daily_available_minutes) : "60",
    );
    const [preferredLanguage, setPreferredLanguage] = useState<"en" | "ar">(
        profile?.preferred_language === "ar" ? "ar" : "en",
    );
    const [university, setUniversity] = useState(profile?.university ?? "");
    const [learningStyle, setLearningStyle] = useState(
        profile?.learning_style_vark ?? "",
    );

    const [step, setStep] = useState(0);
    const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
    const [saved, setSaved] = useState(false);

    /**
     * The full-replacement payload, assembled exactly as `ProfileForm`
     * assembles it: the two optional fields convert empty strings to
     * `null` (the API clears omitted/null optionals — sending an empty
     * string would violate the 1-char minimum), and the minutes field
     * becomes a real number.
     */
    const buildPayload = (): ProfileFormValues => ({
        education_level: educationLevel,
        major,
        preferred_language: preferredLanguage,
        daily_available_minutes: Number(dailyAvailableMinutes),
        university: university || null,
        learning_style_vark: learningStyle || null,
    });

    const goToStep = (next: number) => {
        setStep(next);
        setFieldErrors({});
    };

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        if (saved || updateProfile.isPending) {
            return;
        }

        const payload = buildPayload();

        // Steps 0 and 1: validate only this step's fields, then advance.
        if (step < STEPS.length - 1) {
            const result = STEP_SCHEMAS[step].safeParse(payload);
            if (!result.success) {
                setFieldErrors(issuesToFieldErrors(result.error.issues));
                return;
            }
            goToStep(step + 1);
            return;
        }

        // Final step: validate the COMPLETE payload, then submit once.
        const result = profileSchema.safeParse(payload);
        if (!result.success) {
            setFieldErrors(issuesToFieldErrors(result.error.issues));
            return;
        }

        setFieldErrors({});

        updateProfile.mutate(result.data, {
            onSuccess: (savedProfile) => {
                // Server-confirmed: seed the profile cache with the API's
                // own response before reporting, so the `(app)` gate
                // resolves immediately. The mutation's invalidation then
                // refetches and confirms the same state.
                queryClient.setQueryData(profileKeys.current(), savedProfile);
                setSaved(true);
                onSaved();
            },
        });
    };

    const mutationError = updateProfile.error;
    const mutationErrorMessage = mutationError
        ? mutationError instanceof ApiError
            ? mutationError.status === 401
                ? "Your session has expired. Redirecting to sign in..."
                : mutationError.status === 422
                    ? "Please check your answers — one or more fields were not accepted."
                    : "We couldn't save your profile. Your answers are preserved — try again."
            : "We couldn't save your profile. Your answers are preserved — try again."
        : null;

    const minutesValue = dailyAvailableMinutes;
    const review = {
        education_level: educationLevel,
        major,
        daily_available_minutes: minutesValue
            ? `${minutesValue} minutes / day`
            : "—",
        preferred_language: preferredLanguage === "ar" ? "Arabic" : "English",
        university: university || "Not provided",
        learning_style_vark: learningStyle || "Not provided",
    };

    return (
        <form onSubmit={handleSubmit} noValidate className="space-y-6">
            {/* Explicit progress — real step position, no fake bar. The
                live region announces step changes to screen readers. */}
            <div className="space-y-2">
                <p
                    aria-live="polite"
                    className="text-xs font-semibold uppercase tracking-wider text-primary"
                >
                    Step {step + 1} of {STEPS.length} — {STEPS[step].title}
                </p>
                <div
                    aria-hidden="true"
                    className="flex gap-1.5"
                >
                    {STEPS.map((s, index) => (
                        <span
                            key={s.title}
                            className={`h-1 flex-1 rounded-full ${
                                index <= step
                                    ? "bg-primary"
                                    : "bg-muted"
                            }`}
                        />
                    ))}
                </div>
                <h2 className="text-xl font-bold tracking-tight text-card-foreground">
                    {STEPS[step].title}
                </h2>
            </div>

            {step === 0 && (
                <div className="space-y-4">
                    <Field
                        label="Education Level"
                        htmlFor="onboarding-education-level"
                        error={fieldErrors.education_level}
                    >
                        <Input
                            id="onboarding-education-level"
                            value={educationLevel}
                            onChange={(event) =>
                                setEducationLevel(event.target.value)
                            }
                            disabled={updateProfile.isPending || saved}
                            aria-invalid={Boolean(
                                fieldErrors.education_level,
                            )}
                        />
                    </Field>

                    <Field
                        label="Major"
                        htmlFor="onboarding-major"
                        error={fieldErrors.major}
                    >
                        <Input
                            id="onboarding-major"
                            value={major}
                            onChange={(event) => setMajor(event.target.value)}
                            disabled={updateProfile.isPending || saved}
                            aria-invalid={Boolean(fieldErrors.major)}
                        />
                    </Field>
                </div>
            )}

            {step === 1 && (
                <div className="space-y-4">
                    <Field
                        label="Daily Available Minutes"
                        htmlFor="onboarding-daily-available-minutes"
                        hint="How many minutes you can realistically study per day (1–1440)."
                        error={fieldErrors.daily_available_minutes}
                    >
                        <Input
                            id="onboarding-daily-available-minutes"
                            type="number"
                            min={1}
                            max={1440}
                            value={dailyAvailableMinutes}
                            onChange={(event) =>
                                setDailyAvailableMinutes(event.target.value)
                            }
                            disabled={updateProfile.isPending || saved}
                            aria-invalid={Boolean(
                                fieldErrors.daily_available_minutes,
                            )}
                        />
                    </Field>

                    <Field
                        label="Preferred Language"
                        htmlFor="onboarding-preferred-language"
                        error={fieldErrors.preferred_language}
                    >
                        <Select
                            id="onboarding-preferred-language"
                            value={preferredLanguage}
                            onChange={(event) =>
                                setPreferredLanguage(
                                    event.target.value as "en" | "ar",
                                )
                            }
                            disabled={updateProfile.isPending || saved}
                            aria-invalid={Boolean(
                                fieldErrors.preferred_language,
                            )}
                        >
                            <option value="en">English</option>
                            <option value="ar">Arabic</option>
                        </Select>
                    </Field>
                </div>
            )}

            {step === 2 && (
                <div className="space-y-5">
                    <div className="space-y-4">
                        <Field
                            label="University (optional)"
                            htmlFor="onboarding-university"
                            error={fieldErrors.university}
                        >
                            <Input
                                id="onboarding-university"
                                value={university}
                                onChange={(event) =>
                                    setUniversity(event.target.value)
                                }
                                disabled={updateProfile.isPending || saved}
                                aria-invalid={Boolean(
                                    fieldErrors.university,
                                )}
                            />
                        </Field>

                        <Field
                            label="Learning Style (VARK) (optional)"
                            htmlFor="onboarding-learning-style"
                            hint="Up to 20 characters — for example Visual, Aural, Read/Write, or Kinesthetic."
                            error={fieldErrors.learning_style_vark}
                        >
                            <Input
                                id="onboarding-learning-style"
                                value={learningStyle}
                                onChange={(event) =>
                                    setLearningStyle(event.target.value)
                                }
                                disabled={updateProfile.isPending || saved}
                                aria-invalid={Boolean(
                                    fieldErrors.learning_style_vark,
                                )}
                            />
                        </Field>
                    </div>

                    {/* Review of the complete payload that will be sent —
                        the same values the single PUT carries. */}
                    <div
                        aria-labelledby="onboarding-review-heading"
                        className="rounded-xl border border-border bg-secondary/50 p-4"
                    >
                        <h3
                            id="onboarding-review-heading"
                            className="text-sm font-semibold text-card-foreground"
                        >
                            Review your answers
                        </h3>
                        <dl className="mt-3 space-y-1.5 text-sm">
                            {(
                                [
                                    ["Education Level", review.education_level],
                                    ["Major", review.major],
                                    [
                                        "Daily Available Minutes",
                                        review.daily_available_minutes,
                                    ],
                                    [
                                        "Preferred Language",
                                        review.preferred_language,
                                    ],
                                    ["University", review.university],
                                    [
                                        "Learning Style (VARK)",
                                        review.learning_style_vark,
                                    ],
                                ] as const
                            ).map(([label, value]) => (
                                <div
                                    key={label}
                                    className="flex justify-between gap-3"
                                >
                                    <dt className="text-muted-foreground">
                                        {label}
                                    </dt>
                                    <dd className="text-end font-medium text-card-foreground">
                                        {value}
                                    </dd>
                                </div>
                            ))}
                        </dl>
                    </div>
                </div>
            )}

            {mutationErrorMessage && (
                <p role="alert" className="text-sm text-destructive">
                    {mutationErrorMessage}
                </p>
            )}

            {saved && (
                <p role="status" className="text-sm text-success">
                    Profile saved. Taking you to your dashboard...
                </p>
            )}

            <div className="flex items-center justify-between gap-3">
                {step > 0 ? (
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => goToStep(step - 1)}
                        disabled={updateProfile.isPending || saved}
                    >
                        Back
                    </Button>
                ) : (
                    <span aria-hidden="true" />
                )}

                <Button
                    type="submit"
                    disabled={updateProfile.isPending || saved}
                >
                    {step < STEPS.length - 1
                        ? "Continue"
                        : updateProfile.isPending
                            ? "Saving..."
                            : "Save profile"}
                </Button>
            </div>
        </form>
    );
}
