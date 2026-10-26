"use client";

import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/ui/field";
import { ChoiceTileGroup } from "@/components/ui/choice-tile-group";
import {
    profileSchema,
    type Profile,
    type ProfileFormValues,
} from "@/features/profile/schemas";
import { profileKeys } from "@/features/profile/keys";
import { useUpdateProfile } from "@/features/profile/api/useProfileMutation";

/**
 * First-login profile setup wizard (Batch 4.1 — owner decisions Q2/Q3;
 * presentation refined by the corrective follow-up and the Batch 4.2
 * public-direction redesign).
 *
 * Contract rules (verified against `docs/openapi.json` — nothing
 * invented):
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
 *   - `preferred_language` and the daily-minutes integer presets stay
 *     single-select tiles (finite, contract-backed choices). Education
 *     level has no trusted catalog, so the four education-stage tiles
 *     are product-side entry aids, not contract enums: "Other" keeps
 *     the honest free-text input. `learning_style_vark` is FREE TEXT
 *     in the contract (owner-approved max length raise to 100 chars),
 *     which is why it gets a genuine multi-select toggle group — joined
 *     with commas, exactly what the product's own VARK hint documents.
 *     Major and university remain text inputs (no trusted catalog
 *     exists; none is invented).
 *
 * Batch 4.2 redesign decisions (owner task §6):
 *   - The interim review step was REMOVED: the final save shows a clear
 *     pending/failure state instead, and every step is small enough to
 *     see in one glance. Backward navigation never loses entered
 *     values.
 *   - Selecting a named education stage commits that value immediately;
 *     "Other" reveals a free-text input. Switching away from "Other"
 *     clears any stale custom value (a half-typed custom level is never
 *     silently kept behind a named tile).
 *   - Each step carries ONE concise sentence under its title (no
 *     AI-summary flavor, no redundant restatements of the heading).
 *   - No em dashes in any visible copy.
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
    {
        title: "About your studies",
        instruction: "Tell us where you are in your education and what you study.",
    },
    {
        title: "Your study rhythm",
        instruction: "Tell us when you study and in which language.",
    },
    {
        title: "Optional details",
        instruction: "These fields are optional. Skip any of them and save directly.",
    },
] as const;

const EDUCATION_STAGE_OPTIONS = [
    { value: "High school", label: "High school" },
    { value: "Undergraduate", label: "Undergraduate" },
    { value: "Postgraduate", label: "Postgraduate" },
    { value: "Other", label: "Other" },
] as const;

const MINUTES_PRESETS = [
    { value: "15", label: "15 min" },
    { value: "30", label: "30 min" },
    { value: "60", label: "1 hour" },
    { value: "120", label: "2 hours" },
] as const;

const LANGUAGE_OPTIONS = [
    { value: "en", label: "English" },
    { value: "ar", label: "العربية" },
] as const;

const VARK_OPTIONS = [
    { value: "Visual", label: "Visual" },
    { value: "Aural", label: "Aural" },
    { value: "Read/Write", label: "Read/Write" },
    { value: "Kinesthetic", label: "Kinesthetic" },
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

    // Learning style: the contract field is free text, so an existing
    // profile may hold tokens that are NOT one of the four VARK
    // options. Known tokens back the toggle group; unknown tokens ride
    // along and are submitted back unchanged, without inventing a tile
    // for them.
    const initialStyleTokens = (
        profile?.learning_style_vark ?? ""
    ).split(",");
    const initialKnownStyles = initialStyleTokens.filter((token) =>
        VARK_OPTIONS.some((option) => option.value === token),
    );
    const [preservedStyleTokens] = useState(
        initialStyleTokens
            .filter(
                (token) =>
                    !VARK_OPTIONS.some((option) => option.value === token),
            )
            .join(","),
    );
    const [learningStyles, setLearningStyles] = useState(initialKnownStyles);

    // Which education-stage tile matches the prefilled value: a known
    // stage maps to that tile; anything else (including the empty
    // first-time value) starts unselected, and "Other" re-reveals the
    // prefilled text.
    const prefilledEducation = profile?.education_level ?? "";
    const initialEducationStage = prefilledEducation
        ? EDUCATION_STAGE_OPTIONS.some(
              (option) => option.value === prefilledEducation,
          )
            ? prefilledEducation
            : "Other"
        : "";
    const [educationStage, setEducationStage] = useState(
        initialEducationStage,
    );

    const [step, setStep] = useState(0);
    const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
    const [saved, setSaved] = useState(false);

    const busy = updateProfile.isPending || saved;

    /**
     * The full-replacement payload, assembled exactly as `ProfileForm`
     * assembles it: the two optional fields convert empty strings to
     * `null` (the API clears omitted/null optionals — sending an empty
     * string would violate the 1-char minimum), the minutes field
     * becomes a real number, and the multi-selected learning styles
     * join into the comma format the field documents (unknown
     * prefilled tokens ride along first, unchanged).
     */
    const buildPayload = (): ProfileFormValues => ({
        education_level: educationLevel,
        major,
        preferred_language: preferredLanguage,
        daily_available_minutes: Number(dailyAvailableMinutes),
        university: university || null,
        learning_style_vark:
            [preservedStyleTokens, ...learningStyles]
                .filter(Boolean)
                .join(",") || null,
    });

    const selectEducationStage = (stage: string) => {
        setEducationStage(stage);
        setFieldErrors((errors) => ({ ...errors, education_level: undefined }));
        if (stage === "Other") {
            // Reveal the free-text input empty: no stale custom value is
            // kept behind the tiles.
            setEducationLevel("");
        } else {
            // A named stage commits its value immediately.
            setEducationLevel(stage);
        }
    };

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
                    ? "Please check your answers. One or more fields were not accepted."
                    : "We couldn't save your profile. Your answers are preserved, so you can safely try again."
            : "We couldn't save your profile. Your answers are preserved, so you can safely try again."
        : null;

    const learningStyleJoined =
        [preservedStyleTokens, ...learningStyles].filter(Boolean).join(",") ||
        "";

    return (
        <form onSubmit={handleSubmit} noValidate className="space-y-6">
            {/* Step header: position + title + one-line instruction.
                The live region announces step changes to screen readers;
                the segments are decorative progress markers. */}
            <div className="space-y-3">
                <div className="flex items-center justify-between gap-3">
                    <p
                        aria-live="polite"
                        className="text-xs font-semibold uppercase tracking-wider text-primary"
                    >
                        Step {step + 1} of {STEPS.length}
                    </p>
                    <div aria-hidden="true" className="flex w-24 gap-1.5">
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
                </div>
                <div className="space-y-1">
                    <h2 className="text-xl font-bold tracking-tight text-foreground">
                        {STEPS[step].title}
                    </h2>
                    <p className="text-sm text-muted-foreground">
                        {STEPS[step].instruction}
                    </p>
                </div>
            </div>

            {step === 0 && (
                <div className="space-y-4">
                    {/* Education stage tiles: a product-side entry aid over
                        the contract's free-text field. "Other" reveals the
                        honest free-text input. */}
                    <ChoiceTileGroup
                        id="onboarding-education-stage"
                        label="Education Level"
                        options={EDUCATION_STAGE_OPTIONS}
                        value={educationStage}
                        onValueChange={selectEducationStage}
                        error={fieldErrors.education_level}
                        disabled={busy}
                        groupClassName="[&>button]:min-w-[calc(50%-0.5rem)] sm:[&>button]:flex-1"
                    />
                    {educationStage === "Other" && (
                        <Field
                            label="Your education level"
                            htmlFor="onboarding-education-level"
                            hint="Any level that fits, e.g. vocational training."
                            error={fieldErrors.education_level}
                        >
                            <Input
                                id="onboarding-education-level"
                                placeholder="e.g. Vocational training"
                                value={educationLevel}
                                onChange={(event) =>
                                    setEducationLevel(event.target.value)
                                }
                                disabled={busy}
                                aria-invalid={Boolean(
                                    fieldErrors.education_level,
                                )}
                            />
                        </Field>
                    )}

                    <Field
                        label="Major"
                        htmlFor="onboarding-major"
                        error={fieldErrors.major}
                    >
                        <Input
                            id="onboarding-major"
                            placeholder="e.g. Computer Science"
                            value={major}
                            onChange={(event) => setMajor(event.target.value)}
                            disabled={busy}
                            aria-invalid={Boolean(fieldErrors.major)}
                        />
                    </Field>
                </div>
            )}

            {step === 1 && (
                <div className="space-y-4">
                    <div className="space-y-2">
                        <ChoiceTileGroup
                            id="onboarding-daily-minutes"
                            label="Daily study time"
                            options={MINUTES_PRESETS}
                            value={
                                MINUTES_PRESETS.some(
                                    (preset) =>
                                        preset.value === dailyAvailableMinutes,
                                )
                                    ? dailyAvailableMinutes
                                    : ""
                            }
                            onValueChange={setDailyAvailableMinutes}
                            disabled={busy}
                        />
                        {/* Contract: any integer 1–1440 — the presets are
                            shortcuts, the input stays the honest control
                            for every other value. */}
                        <Input
                            id="onboarding-daily-available-minutes"
                            aria-label="Custom minutes per day"
                            type="number"
                            inputMode="numeric"
                            min={1}
                            max={1440}
                            placeholder="Custom value, 1 to 1440"
                            value={dailyAvailableMinutes}
                            onChange={(event) =>
                                setDailyAvailableMinutes(event.target.value)
                            }
                            disabled={busy}
                            aria-invalid={Boolean(
                                fieldErrors.daily_available_minutes,
                            )}
                            className="max-w-44"
                        />
                        {fieldErrors.daily_available_minutes ? (
                            <p
                                id="onboarding-daily-minutes-error"
                                role="alert"
                                className="text-sm text-destructive"
                            >
                                {fieldErrors.daily_available_minutes}
                            </p>
                        ) : null}
                    </div>

                    <ChoiceTileGroup
                        id="onboarding-preferred-language"
                        label="Preferred language"
                        options={LANGUAGE_OPTIONS}
                        value={preferredLanguage}
                        onValueChange={(next) =>
                            setPreferredLanguage(next as "en" | "ar")
                        }
                        error={fieldErrors.preferred_language}
                        disabled={busy}
                        groupClassName="[&>button]:flex-1 [&>button]:basis-40"
                    />
                </div>
            )}

            {step === 2 && (
                <div className="space-y-5">
                    <Field
                        label="University (optional)"
                        htmlFor="onboarding-university"
                        error={fieldErrors.university}
                    >
                        <Input
                            id="onboarding-university"
                            placeholder="e.g. Cairo University"
                            value={university}
                            onChange={(event) =>
                                setUniversity(event.target.value)
                            }
                            disabled={busy}
                            aria-invalid={Boolean(
                                fieldErrors.university,
                            )}
                        />
                    </Field>

                    {/* Learning style: the contract field is free text, so
                        a genuine multi-select (toggle-group semantics) is
                        the honest control; selections join with commas. */}
                    <ChoiceTileGroup
                        id="onboarding-learning-style"
                        label="Learning style (optional)"
                        options={VARK_OPTIONS}
                        multiple
                        value={learningStyles}
                        onValueChange={setLearningStyles}
                        disabled={busy}
                        error={fieldErrors.learning_style_vark}
                        hint="Pick every style that applies to you."
                        groupClassName="[&>button]:min-w-[calc(50%-0.5rem)] sm:[&>button]:flex-1"
                        action={
                            learningStyleJoined && !busy ? (
                                <button
                                    type="button"
                                    onClick={() => setLearningStyles([])}
                                    className="rounded text-xs font-medium text-muted-foreground outline-none hover:text-foreground focus-visible:ring-3 focus-visible:ring-ring/50"
                                >
                                    Clear
                                </button>
                            ) : undefined
                        }
                    />
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
                        disabled={busy}
                    >
                        Back
                    </Button>
                ) : (
                    <span aria-hidden="true" />
                )}

                <Button type="submit" disabled={busy}>
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
