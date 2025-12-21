# 4. Supabase for Database & Vector Store

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-01-15 (Retroactive)

## Context and Problem Statement

The application requires a robust relational database to store leads, conversations, and property data. Additionally, it needs a vector store to enable RAG (Retrieval-Augmented Generation) for property matching. Managing separate systems for the database and vector search (e.g., PostgreSQL + Pinecone) introduces complexity and synchronization overhead.

## Considered Options

*   **Separate SQL + Vector DB**: PostgreSQL (managed) + Pinecone/Weaviate.
*   **Supabase (PostgreSQL + pgvector)**: All-in-one platform.
*   **NoSQL**: MongoDB (less suitable for structured property data).

## Decision Outcome

Chosen option: **Supabase**.

### Reasoning
1.  **Unified Stack**: Supabase provides a production-grade PostgreSQL database with the `pgvector` extension natively supported. This allows us to perform relational queries and vector similarity searches in a single SQL query.
2.  **Real-time Capabilities**: Supabase Realtime enables instant UI updates in the dashboard when database changes occur (e.g., new messages).
3.  **Developer Experience**: strong ecosystem, easy Python client (`supabase-py`), and built-in authentication/RLS (if needed later).
4.  **Open Source**: Prevents vendor lock-in compared to proprietary vector solutions.

### Positive Consequences
*   Simplified infrastructure (one service to manage).
*   Atomic transactions across business data and embeddings.
*   Cost-effective (free tier covers initial dev/test usage).

### Negative Consequences
*   Tight coupling to PostgreSQL specifics (though standard SQL).
