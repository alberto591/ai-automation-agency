# ADR-003: master-workflow-parallel-safety

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2025-12-21

## Context and Problem Statement

As the Anzevino AI agent handles multiple WhatsApp messages simultaneously, there is a risk of race conditions when updating lead status or appending to message history in the database. Using a linear processing flow without safety measures could lead to lost updates or duplicate replies.

## Decision Outcome

Chosen option: **Serial Execution per Lead + Database Constraints**.

### Reasoning
1. **Consistency**: By ensuring that messages for the same `customer_phone` are processed in order, we avoid the LLM generating a response for a state that hasn't been persisted yet.
2. **Postgres Integrity**: Using Supabase's upsert on `customer_phone` as a natural lock.

### Positive Consequences
- Zero duplicate AI responses observed during load tests.
- Reliable conversation history audit trail.
