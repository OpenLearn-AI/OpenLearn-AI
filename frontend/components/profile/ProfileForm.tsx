"use client";

import { useState } from "react";
import {
    profileSchema,
    type ProfileFormValues,
} from "@/features/profile/schemas";
import {
    ProfileApiError,
    useUpdateProfile,
} from "@/features/profile/api/useProfileMutation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { Profile } from "@/features/profile/api/useProfile";

interface ProfileFormProps {
    profile: Profile;
}

export function ProfileForm({ profile }: ProfileFormProps) {
    const updateProfile = useUpdateProfile();

    const [educationLevel, setEducationLevel] = useState(
        profile.education_level,
    );
    const [major, setMajor] = useState(profile.major);
    const [preferredLanguage, setPreferredLanguage] = useState<
        "en" | "ar"
    >(
        profile.preferred_language === "ar"
            ? "ar"
            : "en",
    );
    const [university, setUniversity] = useState(
        profile.university ?? "",
    );
    const [learningStyle, setLearningStyle] = useState(
        profile.learning_style_vark ?? "",
    );
    const [dailyAvailableMinutes, setDailyAvailableMinutes] =
        useState(String(profile.daily_available_minutes));

    const [errors, setErrors] = useState<{
        education_level?: string;
        major?: string;
        preferred_language?: string;
        university?: string;
        learning_style_vark?: string;
        daily_available_minutes?: string;
    }>({});

    const [successMessage, setSuccessMessage] = useState("");

    const handleSubmit = (
        event: React.FormEvent<HTMLFormElement>,
    ) => {
        event.preventDefault();

        setSuccessMessage("");

        const values: ProfileFormValues = {
            education_level: educationLevel,
            major,
            preferred_language: preferredLanguage,
            university: university || null,
            learning_style_vark: learningStyle || null,
            daily_available_minutes: Number(
                dailyAvailableMinutes,
            ),
        };

        const result = profileSchema.safeParse(values);

        if (!result.success) {
            const fieldErrors: typeof errors = {};

            for (const issue of result.error.issues) {
                const field = issue.path[0];

                if (
                    field === "education_level" ||
                    field === "major" ||
                    field === "preferred_language" ||
                    field === "university" ||
                    field === "learning_style_vark" ||
                    field === "daily_available_minutes"
                ) {
                    fieldErrors[field] = issue.message;
                }
            }

            setErrors(fieldErrors);
            return;
        }

        setErrors({});

        updateProfile.mutate(result.data, {
            onSuccess: () => {
                setSuccessMessage(
                    "Profile updated successfully.",
                );
            },
        });
    };

    const mutationError = updateProfile.error;

    const mutationErrorMessage =
        mutationError instanceof ProfileApiError
            ? mutationError.status === 401
                ? "Your session has expired. Please log in again."
                : mutationError.status === 404
                  ? "Profile not found."
                  : mutationError.status === 422
                    ? "Please check your profile information."
                    : mutationError.message
            : mutationError instanceof Error
              ? mutationError.message
              : null;

    return (
        <form
            onSubmit={handleSubmit}
            className="space-y-6"
            noValidate
        >
            <div className="space-y-2">
                <Label htmlFor="education-level">
                    Education Level
                </Label>

                <Input
                    id="education-level"
                    value={educationLevel}
                    onChange={(event) =>
                        setEducationLevel(event.target.value)
                    }
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(
                        errors.education_level,
                    )}
                />

                {errors.education_level && (
                    <p className="text-sm text-destructive">
                        {errors.education_level}
                    </p>
                )}
            </div>

            <div className="space-y-2">
                <Label htmlFor="major">Major</Label>

                <Input
                    id="major"
                    value={major}
                    onChange={(event) =>
                        setMajor(event.target.value)
                    }
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(errors.major)}
                />

                {errors.major && (
                    <p className="text-sm text-destructive">
                        {errors.major}
                    </p>
                )}
            </div>

            <div className="space-y-2">
                <Label htmlFor="preferred-language">
                    Preferred Language
                </Label>

                <select
                    id="preferred-language"
                    value={preferredLanguage}
                    onChange={(event) =>
                        setPreferredLanguage(
                            event.target.value as "en" | "ar",
                        )
                    }
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(
                        errors.preferred_language,
                    )}
                    className="h-10 w-full rounded-md border bg-background px-3 text-sm"
                >
                    <option value="en">English</option>
                    <option value="ar">Arabic</option>
                </select>

                {errors.preferred_language && (
                    <p className="text-sm text-destructive">
                        {errors.preferred_language}
                    </p>
                )}
            </div>

            <div className="space-y-2">
                <Label htmlFor="university">
                    University
                </Label>

                <Input
                    id="university"
                    value={university}
                    onChange={(event) =>
                        setUniversity(event.target.value)
                    }
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(errors.university)}
                />

                {errors.university && (
                    <p className="text-sm text-destructive">
                        {errors.university}
                    </p>
                )}
            </div>

            <div className="space-y-2">
                <Label htmlFor="learning-style">
                    Learning Style (VARK)
                </Label>

                <Input
                    id="learning-style"
                    value={learningStyle}
                    onChange={(event) =>
                        setLearningStyle(event.target.value)
                    }
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(
                        errors.learning_style_vark,
                    )}
                />

                {errors.learning_style_vark && (
                    <p className="text-sm text-destructive">
                        {errors.learning_style_vark}
                    </p>
                )}
            </div>

            <div className="space-y-2">
                <Label htmlFor="daily-available-minutes">
                    Daily Available Minutes
                </Label>

                <Input
                    id="daily-available-minutes"
                    type="number"
                    min={1}
                    max={1440}
                    value={dailyAvailableMinutes}
                    onChange={(event) =>
                        setDailyAvailableMinutes(
                            event.target.value,
                        )
                    }
                    disabled={updateProfile.isPending}
                    aria-invalid={Boolean(
                        errors.daily_available_minutes,
                    )}
                />

                {errors.daily_available_minutes && (
                    <p className="text-sm text-destructive">
                        {errors.daily_available_minutes}
                    </p>
                )}
            </div>

            {mutationErrorMessage && (
                <p
                    role="alert"
                    className="text-sm text-destructive"
                >
                    {mutationErrorMessage}
                </p>
            )}

            {successMessage && (
                <p
                    role="status"
                    className="text-sm text-green-600"
                >
                    {successMessage}
                </p>
            )}

            <Button
                type="submit"
                disabled={updateProfile.isPending}
            >
                {updateProfile.isPending
                    ? "Saving..."
                    : "Save Changes"}
            </Button>
        </form>
    );
}