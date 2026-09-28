import { useMutation } from "@tanstack/react-query";
import { getAccessToken } from "@/lib/keycloak";
import type { CourseFormValues } from "../schemas";

export class CourseApiError extends Error {
    status: number;

    constructor(message: string, status: number) {
        super(message);
        this.name = "CourseApiError";
        this.status = status;
    }
}


async function createCourse(payload: CourseFormValues) {
    const token = await getAccessToken();

    if (!token) {
        throw new CourseApiError("Not authenticated", 401);
    }
    const baseUrl = process.env.NEXT_PUBLIC_API_URL;

    const response = await fetch(`${baseUrl}/v1/courses`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new CourseApiError(
            `Failed to create course: ${response.status}`,
            response.status,
        );
    }

    return response.json();
}

async function updateCourse(
    courseId: string,
    payload: CourseFormValues,
) {
    const token = await getAccessToken();

    if (!token) {
        throw new CourseApiError("Not authenticated", 401);
    }

    const baseUrl = process.env.NEXT_PUBLIC_API_URL;

    const response = await fetch(
        `${baseUrl}/v1/courses/${courseId}`,
        {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
        },
    );

    if (!response.ok) {
        throw new CourseApiError(
            `Failed to update course: ${response.status}`,
            response.status,
        );
    }

    return response.json();
}

export function useCreateCourse() {
    return useMutation({
        mutationFn: createCourse,
    });
}

export function useUpdateCourse() {
    return useMutation({
        mutationFn: ({
            courseId,
            payload,
        }: {
            courseId: string;
            payload: CourseFormValues;
        }) => updateCourse(courseId, payload),
    });
}