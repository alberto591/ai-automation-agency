# RAG & Matching Study (Priority 1)

## Context
As part of Phase 1 (MVP Completion & Core Optimization), this study explores how Retrieval Augmented Generation (RAG) and advanced matching patterns can be leveraged to improve property discovery and lead qualification in the Italian real estate market.

## Key Findings

### 1. Retrieval Augmented Generation (RAG) Patterns
RAG is no longer just "search + LLM". For real estate, the following patterns are critical:
- **Property Graph RAG**: Combining vector search with Knowledge Graphs to capture relationships between properties, locations, and amenities. This prevents hallucinations about property proximity or feature availability.
- **Multi-modal RAG**: Using both text and image embeddings (CLIP) to allow users to search via visual concepts (e.g., "modern kitchen with island") which are then retrieved from the database.
- **Contextual Retrieval**: Re-ranking retrieved properties based on real-time availability and user session intent.

### 2. Matching Algorithms
- **Semantic Matching**: Moving beyond exact filtros (e.g., 3 bedrooms) to semantic similarity (e.g., "spacious enough for a family of 5").
- **Agentic Matching**: Autonomous AI agents that evaluate a lead's "Heat" (from qualification) against available property features, performing a cross-referencing task rather than a simple database query.
- **ROI-Driven Matching**: For investors, matching properties based on predicted yield and cap rate (integrated with the Fifi appraisal tool).

### 3. Implementation Recommendations for 2026
- **Transition to Hybrid Search**: Combine Supabase pgvector with full-text search for the best of both worlds.
- **Small Model Reranking**: Use a lightweight model (like BGE-Reranker) to refine the top 10 results from vector search before presenting to the LLM.
- **Privacy-First Retrieval**: Ensure RAG pipelines do not leak sensitive lead data into the global vector space.

## Decision / Rationale
We should prioritize **Hybrid Search** and **Semantic Property Discovery** in the next implementation phase to differentiate the agency from standard listing portals.

## Strategic Roadmap Alignment
- **Phase 2**: Implement Google Sheets/Supabase sync for automated vector index updates.
- **Phase 3**: Launch Dynamic PDF Property Cards generated from RAG insights.
