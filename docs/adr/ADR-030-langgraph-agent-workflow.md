# ADR-030: LangGraph-based Agentic Workflow for Lead Processing

* Status: Proposed
* Deciders: Engineering Team, Antigravity Agent
* Date: 2025-12-22

## Context and Problem Statement

The previous `LeadProcessor` logic was monolithic and difficult to extend. As we add more complex AI behaviors (structured extraction, multi-step reasoning, grounding), a procedural approach becomes brittle and hard to test. We need a modular framework that allows for distinct nodes of execution, clear state management, and easier debugging.

## Decision Outcome

Chosen option: **LangGraph-based State Machine**.

### Architecture
We refactored the `LeadProcessor` to utilize a LangGraph `StateGraph`. This decomposes the logic into specific nodes:
1.  **Ingest**: Data loading and normalization.
2.  **Intent**: Structured extraction of user intent and budget.
3.  **Sophisticated Analyzers**: New nodes for `PropertyPreferenceExtraction` and `SentimentAnalysis`.
4.  **Semantic Cache**: Performance optimization.
5.  **Retrieval**: Grounded property search.
6.  **Generation**: Templated, grounded response crafting.
7.  **Finalize/Persistence**: Messaging and state preservation.

### Structured Data
We utilize Pydantic models for nodes to ensure high-fidelity data extraction from the LLM, moving away from regex-based parsing.

### Consequence
*   **Positive**: Improved modularity, better observability, easier testing of individual graph nodes, and support for complex multi-turn reasoning.
*   **Positive**: Using `LangChainAdapter` as the primary interface enables advanced features like Output Parsers and ChatPromptTemplates.
*   **Neutral**: Increased initial complexity due to graph wiring and state management.
*   **Negative**: Requires more sophisticated mocking in unit tests.

## Implementation Details
- Workflow defined in `application/workflows/agents.py`.
- `LeadProcessor` updated to act as a lightweight wrapper for the graph.
- New `LangChainAdapter` implemented as the primary `AIPort`.
