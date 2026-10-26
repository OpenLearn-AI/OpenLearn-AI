import { OidcEntryBridge } from "@/components/auth/OidcEntryBridge";

/**
 * Registration entry — minimal redirect bridge (Batch 4.1 corrective
 * follow-up §C.4).
 *
 * Registration is hosted by Keycloak (registration is enabled in the
 * active realm): this page hands the visit straight to the shared
 * `OidcEntryBridge`, which initiates the existing `keycloak.register`
 * flow directly — no local form, no extra click. The redirect target
 * stays `/dashboard` (protected logic, unchanged), whose onboarding
 * gate routes fresh users into `/onboarding`. The bridge's manual state
 * keeps the pinned "Create account" button for the
 * return-after-attempt and error paths; the brand identity and theme
 * toggle come from the shared `(auth)` layout.
 */
export default function RegisterPage() {
    return <OidcEntryBridge mode="register" />;
}
