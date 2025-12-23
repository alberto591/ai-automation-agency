# ADR-017: component-discovery-registry-first

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-12-21

## Context and Problem Statement

Engineering standards like structured logging or circuit breakers are often forgotten or inconsistently applied. We need a "Source of Truth" for patterns that tools and agents can discover programmatically.

## Decision Outcome

Chosen option: **Best Practices Registry (BPR)**.

### Reasoning
1. **Discoverability**: By placing patterns in `best_practices/`, they become part of the codebase, not just external documentation.
2. **Tooling**: The `retriever.py` script allows CLI-based discovery of patterns, making it easier to audit compliance.

### Positive Consequences
- Standardized implementation of cross-cutting concerns (logging, resilience).
- Self-documenting codebase.
