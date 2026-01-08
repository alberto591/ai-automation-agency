# ADR-060: Lead Property Interest Tracking

**Status:** Accepted
**Date:** 2026-01-08
**Author:** Antigravity

## 1. Context (The "Why")
To generate accurate sales reports for property owners, we need to know which leads have expressed interest in a specific property. While a many-to-many join table (`lead_property_interests`) is the standard relational approach, we needed a solution that was:
1. Fast to implement without extensive DDL migrations in a fast-paced development cycle.
2. Flexible enough to store "soft" interest (e.g., just viewing a brochure) without strict relational constraints.

## 2. Decision
We are utilizing the existing `metadata` JSONB field in the `leads` table to store an array of `interested_property_ids`.
When a lead is sent a brochure or interacts with a property search, the `JourneyManager` updates this list.

## 3. Rationale (The "Proof")
* **Performance:** Single-table lookup for lead details and interests.
* **Flexibility:** Easy to add other "interest" types (e.g., `viewing_scheduled_property_ids`) without new tables.
* **Implementation Speed:** Leverages existing `update_lead` patterns in the `SupabaseAdapter`.

## 4. Consequences
* **Positive:** Reduced database schema complexity. Accurate real-time aggregation for sales reports.
* **Negative/Trade-offs:** Searching for "all leads interested in property X" requires a JSONB containment query (`@>`) or a Python-side filter (which we implemented in `api.py` for simplicity in the first iteration).

## 5. Wiring Check (No Dead Code)
- [x] Logic implemented in `application/services/journey_manager.py` (send_property_brochure)
- [x] Query logic used in `presentation/api/api.py` (generate_sales_report_endpoint)
