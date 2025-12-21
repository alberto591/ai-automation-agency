# 8. RAG Property Matching Strategy

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-02-15 (Retroactive)

## Context and Problem Statement

Users express property needs in natural language (e.g., "trilocale luminoso vicino alla metro, max 300k"). A standard SQL query cannot easily handle "vicino alla metro" (near subway) or "luminoso" (bright). Conversely, a pure vector search might recommend a "bright" apartment that is 500k, violating the hard budget constraint.

## Considered Options

*   **Pure Vector Search**: Convert query to embedding, find nearest neighbors.
*   **Pure SQL Search**: Extract entities (price, rooms) and run `SELECT *`.
*   **Hybrid Search**: Combine Vector Similarity with SQL Metadata Filtering.

## Decision Outcome

Chosen option: **Hybrid Search**.

### Reasoning
1.  **Precision & Recall**: Real estate has hard constraints (Price, Location, Rooms) that must be respected using Metadata Filtering. It also has soft constraints (Style, Vibe, Proximity) that are best handled by Vector Search.
2.  **Supabase Capabilities**: `pgvector` allows query chaining: `embedding <=> query_embedding` AND `price <= 300000`.

### Implementation Process
1.  **Ingestion**: Property descriptions are embedded (Mistral Embeddings) and stored in `property_listings`.
2.  **Querying**:
    *   LLM extracts structured filters (price max, rooms min).
    *   LLM summarizes the "vibe" into a search string.
    *   System executes a Vector Search *within* the pre-filtered SQL dataset.

### Positive Consequences
*   Avoids "hallucinating" matches that are over budget.
*   Finds properties that match the description semantically even if they don't share exact keywords.

### Negative Consequences
*   Complex query construction.
*   Dependency on the quality of the LLM's entity extraction.
