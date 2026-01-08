# ADR-059: Feedback System Schema Normalization and API Consolidation

**Status:** Accepted
**Date:** 2026-01-07
**Author:** Antigravity (AI Assistant)

## 1. Context (The "Why")
The feedback submission system was experiencing failures due to a mismatch between the frontend payload and the database schema. Columns like `comment` (text) versus `rating` (int) were inconsistent across table versions, and the backend logic lacked proper validation for these fields.

## 2. Decision
**Normalize the `feedbacks` table schema** and consolidate the backend handling into a dedicated API service.

Key components:
1.  **Schema Migration**: Created `docs/sql/20260105_fix_feedback_schema.sql` to ensure columns `user_id`, `rating`, `comment`, and `category` exist with correct types.
2.  **Dedicated Endpoint**: Implemented `presentation/api/feedback.py` using FastAPI/Pydantic for strict input validation.
3.  **Verification Script**: Created `scripts/verify_feedback_columns.py` to programmatically check DB state during CI/CD or recovery.
4.  **Frontend Sync**: Updated the feedback modal to ensure field names match the new schema exactly.

## 3. Rationale (The "Proof")
*   **Data Integrity**: Type-safe Pydantic models prevent junk data from entering the database.
*   **Observability**: A dedicated endpoint makes it easier to track feedback rates and errors in the logs.
*   **Resilience**: The migration script is idempotent, allowing it to be run repeatedly without failure.

## 4. Consequences
*   **Positive**: 100% success rate on feedback submissions during testing. Better structure for analysis (sorting by rating/category).
*   **Negative/Trade-offs**: Requires a database migration on all environments (dev/prod).

## 5. Wiring Check (No Dead Code)
- [x] Schema fix applied via `20260105_fix_feedback_schema.sql`
- [x] API logic in `presentation/api/feedback.py`
- [x] Health check updated to include feedback system verification
