# ADR-004: rag-credulity-testing

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2025-12-21

## Context and Problem Statement

Users often ask "trick" questions or request property features that don't exist in our inventory. A "credulous" RAG system might hallucinate a match just to satisfy the user request. We need to verify that matches are grounded in real `market_data` or `properties` records.

## Decision Outcome

Chosen option: **Double-Check Verification Layer**.

### Reasoning
1. **Truthfulness**: The LLM must explicitly state "I couldn't find a perfect match" if the vector search similarity falls below a certain threshold (0.78).
2. **Schema Validation**: Property IDs returned by the search are re-fetched from the DB before the LLM incorporates them into the message.

### Positive Consequences
- Increased user trust by admitting inventory gaps.
- Eliminated "fake apartment" hallucinations.
