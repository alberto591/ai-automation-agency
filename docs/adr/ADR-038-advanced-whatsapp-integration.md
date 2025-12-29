# ADR [038]: Advanced WhatsApp & Dashboard Integration

**Status:** Accepted
**Date:** 2025-12-30
**Author:** Antigravity

## 1. Context (The "Why")
The initial WhatsApp integration only supported plain text and lacked transparency regarding message delivery. To provide a premium agentic experience, the dashboard needed:
*   **Media Support**: Capability to handle images and documents sent by leads (e.g., floor plans, property photos).
*   **Read Receipts**: Visual confirmation of "Delivered" and "Read" statuses to prevent "ghosting" anxiety.
*   **Unified Inbox**: A clear indication of which channel (WhatsApp, Voice, Email) a message originated from.
*   **Real-time Sync**: Instant dashboard updates without requiring manual refreshes.

## 2. Decision
We have implemented the following architectural changes:
1.  **Schema Expansion**: Added `sid` (Twilio Message SID), `status`, `media_url`, and `channel` to the `messages` table.
2.  **Status Callbacks**: Configured `TwilioAdapter` to pass a `status_callback` URL to Twilio for every outbound message.
3.  **Webhook De-coupling**: Added a dedicated `/api/webhooks/twilio/status` endpoint to handle POST requests from Twilio asynchronously.
4.  **Reactive UI**: Enhanced the `useMessages` hook to listen specifically for `UPDATE` events on the `messages` table via Supabase Realtime.
5.  **Channel Metadata**: Standardized a `channel` field across all messaging ports to facilitate the "Unified Inbox" view.

## 3. Rationale (The "Proof")
*   **Hexagonal Integrity**: We maintained the Port/Adapter pattern. `MessagingPort` now returns a unique ID (`sid`) which is used as the correlation key for status updates.
*   **Performance**: Indexed the `sid` column in Supabase to ensure that Twilio callbacks (which can be numerous) result in sub-millisecond database updates.
*   **UX Excellence**: Used `lucide-react` icons (Check, CheckCheck) to mirror the familiar WhatsApp user experience, reducing the learning curve for agents.

## 4. Consequences
*   **Positive:** Highly responsive dashboard, full visibility into message lifecycle, and support for rich media.
*   **Trade-offs:** Requires a valid `WEBHOOK_BASE_URL` in environment variables. If missing, callbacks will fail silently or be skipped.

## 5. Wiring Check (No Dead Code)
- [x] Logic implemented in `infrastructure/adapters/twilio_adapter.py`
- [x] Status handler in `presentation/api/api.py`
- [x] `WEBHOOK_BASE_URL` added to `config/settings.py` and `.env`
- [x] UI logic in `ChatWindow.jsx` and `useMessages.js`
