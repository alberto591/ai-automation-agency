# 12. Real-Time Dashboard Synchronization

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-03-10 (Retroactive)

## Context and Problem Statement

The dashboard needs to show new incoming WhatsApp messages instantly. If an agent is staring at the screen and a client replies, the message must appear without a page refresh. Latency or "refresh button mashing" leads to missed opportunities.

## Considered Options

*   **Short Polling**: Frontend calls `fetch()` every 5 seconds.
*   **WebSockets (Custom)**: Building a socket.io server in Python/FastAPI.
*   **Supabase Realtime**: Using the native subscription feature of the database.

## Decision Outcome

Chosen option: **Supabase Realtime**.

### Reasoning
1.  **"Push" Architecture**: Supabase listens to the PostgreSQL Replication Log (WAL). When a new row is inserted into `lead_conversations` (by the webhook), Supabase automatically pushes this payload to connected clients.
2.  **No Extra Backend State**: We don't need to manage WebSocket connections or sticky sessions in our Python API.
3.  **Simplicity**: Implemented in `useLeads.js` with just a few lines of code (`.on('postgres_changes'...).subscribe()`).

### Positive Consequences
*   Instant UI updates (< 100ms latency).
*   Reduced server load (no polling).

### Negative Consequences
*   Requires enabling "Realtime" replication on specific tables in Supabase Dashboard.
*   Connection limits on the Supabase free tier.
