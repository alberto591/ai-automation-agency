# ADR 045: Regulatory Hardening and Preliminary Positioning

## Status
Accepted

## Context
As the "Fifi AI" system moves toward production, it faces regulatory scrutiny under the EU AI Act (Regulation 2024/1689). Automated valuation models (AVMs) that impact financial decisions can be perceived as "High-Risk" if not properly governed. To minimize legal risk and professional liability, we must move away from "Definitive Valuation" and toward "Preliminary Decision Support."

## Decision
1.  **Rebranding**: The tool is renamed to **"Supporto Valutativo Preliminare"** (Preliminary Valuation Support) in all user-facing interfaces. This explicitly communicates that the tool is an aid, not a professional appraisal.
2.  **Mandatory Disclaimer**: A "Click-to-accept" checkbox is implemented on the appraisal form. The form cannot be submitted without the user acknowledging that:
    -   The result is a preliminary estimate.
    -   It does not replace a professional appraisal (*perizia*).
3.  **Visual Mitigation**: The UI will use "Confidence Ranges" rather than single point estimates to reflect the statistical nature of the prediction.

## Consequences
-   **Legal**: Lower risk of professional liability under Italian Consumer Law (*Codice del Consumo*).
-   **Compliance**: Aligns with EU AI Act requirements for transparency and technical documentation.
-   **UX**: Minor friction introduced by the checkbox, balanced by increased trust and professional appearance.
-   **Technical**: Requires i18n support for the disclaimer and state management for form validation.
