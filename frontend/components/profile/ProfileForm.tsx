"use client";

import { useState } from "react";

import {
    profileSchema,
    type ProfileFormValues,
} from "@/features/profile/schemas";
import { useUpdateProfile } from "@/features/profile/api/useProfileMutation";
import type { Profile } from "@/features/profile/schemas";
import { ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Field } from "@/components/ui/field";

interface ProfileFormProps {
    profile: Profile | null;
}

type FieldErrors = Partial<
    Record<keyof ProfileFormValues, string>
>;

export function ProfileForm({ profile }: ProfileFormProps) {
    const updateProfile = useUpdateProfile();

    const [educationLevel, setEducationLevel] = useState(
        profile?.education_level ?? "",
    );
    const [major, setMajor] = useState(profile?.major ?? "");
    const [preferredLanguage, setPreferredLanguage] = useState<"en" | "ar">(
        profile?.preferred_language === "ar" ? "ar" : "en",
    );
    const [university, setUniversity] = useState(
        profile?.university ?? "",
    );
    const [learningStyle, setLearningStyle] = useState(
        profile?.learning_style_vark ?? "",
    );
    const [dailyAvailableMinutes, setDailyAvailableMinutes] = useState(
        String(profile?.daily_available_minutes ?? 60),
    );

    const [errors, setErrors] = useState<FieldErrors>({});
    const [successMessage, setSuccessMessage] = useState("");

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        setSuccessMessage("");

        const values: ProfileFormValues = {
            education_level: educationLevel,
            major,
            preferred_language: preferredLanguage,
            university: university || null,
            learning_style_vark: learningStyle || null,
            daily_available_minutes: Number(dailyAvailableMinutes),
        };

        const result = profileSchema.safeParse(values);

        if (!result.success) {
            const fieldErrors: FieldErrors = {};

            for (const issue of result.error.issues) {
                const field = issue.path[0] as keyof ProfileFormValues;
                fieldErrors[field] = issue.message;
            }

            setErrors(fieldErrors);
            return;
        }

        setErrors({});

        updateProfile.mutate(result.data, {
            onSuccess: () => {
                setSuccessMessage(
                    profile
                        ? "Profile updated successfully."
                        : "Profile created successfully.",
                );
            },
        });
    };

    const mutationError = updateProfile.error;

    const mutationErrorMessage =
        mutationError instanceof ApiError
            ? mutationError.status === 401
                ? "Your session has expired. Please log in again."
                : mutationError.status === 404
                  ? "Unable to save the profile for this user."
                  : mutationError.status === 422
                      ? "Please check your profile information."
                      : mutationError.message
            : mutationError instanceof Error
                ? mutationError.message
                : null;

    return (
        <form onSubmit={handleSubmit} className="space-y-6" noValidate>
            <Field
                label="Education Level"
                htmlFor="education-level"
                error={errors.education_level}
            >
                <Input
                    id="education-level"
                    value={educationLevel}
                    onChange={(event) =>
                        setEducationLevel(event.target.value)
                    }
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(errors.education_level)}
                />
            </Field>

            <Field label="Major" htmlFor="major" error={errors.major}>
                <Input
                    id="major"
                    value={major}
                    onChange={(event) => setMajor(event.target.value)}
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(errors.major)}
                />
            </Field>

            <Field
                label="Preferred Language"
                htmlFor="preferred-language"
                error={errors.preferred_language}
            >
                <Select
                    id="preferred-language"
                    value={preferredLanguage}
                    onChange={(event) =>
                        setPreferredLanguage(
                            event.target.value as "en" | "ar",
                        )
                    }
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(errors.preferred_language)}
                >
                    <option value="en">English</option>
                    <option value="ar">Arabic</option>
                </Select>
            </Field>

            <Field
                label="University"
                htmlFor="university"
                error={errors.university}
            >
                <Input
                    id="university"
                    value={university}
                    onChange={(event) =>
                        setUniversity(event.target.value)
                    }
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(errors.university)}
                />
            </Field>

            <Field
                label="Learning Style (VARK)"
                htmlFor="learning-style"
                error={errors.learning_style_vark}
            >
                <Input
                    id="learning-style"
                    value={learningStyle}
                    onChange={(event) =>
                        setLearningStyle(event.target.value)
                    }
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(errors.learning_style_vark)}
                />
            </Field>

            <Field
                label="Daily Available Minutes"
                htmlFor="daily-available-minutes"
                error={errors.daily_available_minutes}
            >
                <Input
                    id="daily-available-minutes"
                    type="number"
                    min={1}
                    max={1440}
                    value={dailyAvailableMinutes}
                    onChange={(event) =>
                        setDailyAvailableMinutes(event.target.value)
                    }
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(
                        errors.daily_available_minutes,
                    )}
                />
            </Field>

            {mutationErrorMessage && (
                <p role="alert" className="text-sm text-destructive">
                    {mutationErrorMessage}
                </p>
            )}

            {successMessage && (
                <p role="status" className="text-sm text-success-foreground">
                    {successMessage}
                </p>
            )}

            <Button
                type="submit"
                disabled={updateProfile.isPending}
            >
                {updateProfile.isPending
                    ? "Saving..."
                    : profile
                        ? "Save Changes"
                        : "Create Profile"}
            </Button>
        </form>
    );
}
