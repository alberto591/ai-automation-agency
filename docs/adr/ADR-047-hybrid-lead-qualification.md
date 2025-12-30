# ADR 047: Hybrid Lead Qualification Flow

## Status
Accepted

## Context
Qualifying real estate leads requires extracting specific structured data (Budget, Timeline, Intent, Financing). Purely open-ended LLM conversations often miss these fields or take too many turns. Conversely, rigid forms have low conversion on WhatsApp.

## Decision
1.  **Hybrid Flow**: Use a scripted 7-question sequence in Italian to ensure "Professional Tone" and "Data Completeness."
2.  **LLM-Assisted Extraction**: After each user response, use a specialized LLM node (`lead_qualification_node`) to map the text to structured fields in `QualificationData`.
3.  **Stateful Memory**: Persist partially completed qualification data in the lead's metadata, allowing the conversation to resume across different sessions or after agent handoff.
4.  **Scoring Integration**: Resulting data is passed to `LeadScoringService` to compute a 1-10 priority score (HOT/WARM/COLD).

## Consequences
-   **Reliability**: Guarantees that all 7 critical data points are collected.
-   **Scalability**: Allows the agency to handle hundreds of leads simultaneously without human triage.
-   **Flexibility**: The LLM can still handle "Detours" (e.g., questions about the area) between qualification steps.
