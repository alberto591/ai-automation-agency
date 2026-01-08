# ADR-065: Multi-Agent Routing (Zone Affinity)

**Status:** Accepted
**Date:** 2026-01-08
**Author:** Antigravity

## 1. Context (The "Why")

As agencies scale, leads need to be distributed among multiple agents. Real estate leads are geography-centric; an agent specialized in "Centro Milano" shouldn't receive leads for "Baggio".

## 2. Decision

We have implemented a `RoutingService` that uses **Zone Affinity** as the primary assignment mechanism, with **Round Robin** as a fallback.

### 2.1 Assignment Logic
1.  **Zone Match**: Compares Lead's `postcode` or query-extracted zone against Agent's allowed `zones` (stored as an array in `public.users`).
2.  **Fallback**: If no match (or no postcode), the system picks a random active agent from the pool to ensure even distribution.

### 2.2 Domain Changes
- Added `assigned_agent_id` to `Lead` model.
- Created `Agent` model in domain layer.

## 3. Rationale (The "Proof")

*   **Scalability**: Allows adding agents via the database without code changes.
*   **Efficiency**: Connects leads with the most relevant agent immediately.
*   **Hexagonal Integrity**: Routing logic is an application service, decoupled from specific I/O adapters.

## 4. Consequences

*   **Positive**: Enterprise-ready lead distribution.
*   **Negative**: Initial extraction of "Zone" from natural language is heuristic-based (improved in future with NLU).

## 5. Wiring Check (No Dead Code)
- [x] Service in `application/services/routing_service.py`
- [x] Integration in `LeadProcessor.process_lead`
- [x] DB Schema updated in `docs/sql/20260108_multi_agent_routing.sql`
