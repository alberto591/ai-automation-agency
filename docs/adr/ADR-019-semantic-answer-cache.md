# ADR-019: semantic-answer-cache

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-12-21

## Context and Problem Statement

Repeated customer questions on WhatsApp (e.g., "Do you have 2-bedroom apartments in Navigli?") cause redundant LLM processing and latency. We need a way to cache semantically similar queries to reduce costs and improve response times.

## Decision Outcome

Chosen option: **Vector-Based Answer Cache (Future Consideration)**.

### Reasoning
1. **Efficiency**: By storing the embedding of previous queries and their AI-generated answers in `market_data`, we can perform a cosine similarity lookup before calling Mistral.
2. **Consistency**: Ensures the AI gives the same answer to the same question within a short time window.

### Positive Consequences
- Reduced LLM API bill.
- Near-instant responses for common inquiries.
