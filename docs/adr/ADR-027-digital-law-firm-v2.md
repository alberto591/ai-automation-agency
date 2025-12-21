# ADR-027: digital-law-firm-v2 (Real Estate Evolution)

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-12-21

## Context and Problem Statement

The current Anzevino AI (v1) focuses on lead qualification and basic property lookup. The next phase (v2) must handle end-to-end appointment scheduling and legal document assistance for real estate contracts.

## Decision Outcome

Chosen option: **Goal-Oriented Multi-Step Framework**.

### Reasoning
1. **Scalability**: Moving from single-turn replies to stateful "Sales Journeys".
2. **Integration**: Deep integration with Google Calendar and local Italian real estate contract templates.

### Positive Consequences
- Full automation of the agency's top-of-funnel operations.
- Higher conversion from "lead" to "signed viewing agreement".
