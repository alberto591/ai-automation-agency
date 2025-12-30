# ADR 046: AVM Audit Trail and Shadow Mode Validation

## Status
Accepted

## Context
High-reliability AI systems require continuous monitoring (Mishaps prevention) and a clear audit trail for accountability. We need a way to track what the AI predicted, for whom, and what features were used, while also measuring model drift (MAPE) against actual market outcomes.

## Decision
1.  **Unified Audit Table**: All appraisal requests are logged to `appraisal_validations`. This table serves both as a legal log (Audit Trail) and a training dataset (Shadow Mode).
2.  **Validation Interface**: A `ValidationPort` is defined to decouple the logging logic from specific database implementations. The `PostgresValidationAdapter` handles the Supabase integration.
3.  **Shadow Mode Execution**: A dedicated script (`run_shadow_mode.py`) is used to compare predictions against historical or actual transaction data without affecting the user experience.
4.  **Automatic Alerts**: The validation logic will trigger warnings if MAPE exceeds 15% in a specific zone, allowing for proactive model retraining.

## Consequences
-   **Security**: Minimal sensitive data (Addresses/Phones) is stored in the audit trail, mapped back to the primary `leads` table.
-   **Performance**: Slight overhead on the `finalize_node` in the LangGraph to perform the async audit insert.
-   **Observability**: Provides the agency owner with a dashboard of "AI Accuracy" vs "Humans," facilitating trust.
-   **Governance**: Directly supports the EU AI Act requirement for "Technical Robustness and Accuracy."
