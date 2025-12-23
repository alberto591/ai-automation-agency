# ADR-036: Database Normalization (Leads & Messages)

## Status
Accepted

## Context
Initially, the project used a flat table `lead_conversations` which stored both lead profile data and an array of message objects. While simple for an MVP, this structure faced several limitations:
1.  **Scalability**: Appending messages to a single JSONB array becomes inefficient as conversations grow.
2.  **Searchability**: Querying individual messages (e.g., for RAG or analytics) within a nested array is complex and slow.
3.  **Data Integrity**: Hard to enforce constraints on individual messages.
4.  **Real-time Efficiency**: Supabase real-time updates triggered on the entire conversation object, even for minor message additions.

## Decision
We decided to normalize the schema into two distinct tables:
-   `leads`: Stores profile information (phone, name, budget, preferences, status, ai_summary).
-   `messages`: Stores atomic messages linked to a lead via `lead_id`.

## Consequences
-   **Performance**: Improved query speed for both profiles and chat history.
-   **RAG Integration**: Messages are now easier to vectorize and search individually.
-   **Dashboard**: Updated `useLeads` and `useMessages` hooks to perform a join and granular subscriptions.
-   **Maintainability**: Clear separation between Lead CRM state and Chat history state.

## Alternatives Considered
-   **Partitioning lead_conversations**: Considered but rejected as it doesn't solve the atomic search issue.
-   **External Vector DB only**: Rejected as we need a relational source of truth for the dashboard.
