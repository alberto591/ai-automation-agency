# ADR-064: Automated Payment Reminders Architecture

**Status:** Accepted
**Date:** 2026-01-08
**Author:** Antigravity

## 1. Context (The "Why")

FiFi AI aims to provide utility value beyond just lead acquisition. Managing payment schedules (rent, EMI, commissions) is a significant pain point for agencies. Automating these reminders via WhatsApp increases "stickiness" and provides a tangible ROI for the user.

## 2. Decision

We have implemented a dedicated `PaymentService` and background task logic to handle automated reminders.

### 2.1 Technical Components
- **Database**: `payment_schedules` table specifically for tracking due dates and reminder preferences.
- **Service**: `PaymentService` encapsulates the logic for determining which leads are due for a reminder (defaulting to 7, 3, and 0 days before the due date).
- **Execution**: A standalone script `scripts/process_payments.py` designed to be triggered by a daily cron job.

### 2.2 Integration
- Uses `DatabasePort` to fetch leads with payment schedules.
- Uses `MessagingPort` (WhatsApp) to deliver the notifications.

## 3. Rationale (The "Proof")

*   **Asynchronous Processing**: Reminders are processed out-of-band, ensuring no impact on real-time bot responses.
*   **Fail-Fast/Observability**: Success/Error stats are logged per run, allowing for easy monitoring.
*   **Clean Separation**: Payment logic is decoupled from lead qualification logic.

## 4. Consequences

*   **Positive**: Reduced manual effort for agents, improved collection rates.
*   **Negative**: Requires a cron job configuration in the hosting environment.

## 5. Wiring Check (No Dead Code)
- [x] Service implemented in `application/services/payment_service.py`
- [x] Registered in `config/container.py`
- [x] Cron script in `scripts/process_payments.py`
- [x] SQL migration in `docs/sql/20260108_payment_schedules.sql`
