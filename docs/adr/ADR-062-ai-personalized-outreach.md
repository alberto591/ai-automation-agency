# ADR-062: AI Personalized Outreach

**Status:** Accepted
**Date:** 2026-01-08
**Author:** Antigravity

## 1. Context (The "Why")
Standard B2B outreach messages like "Hi, check out our AI tool" often yield low conversion rates. Agencies in different cities/zones respond better to localized and personalized context.

## 2. Decision
Incorporate a personalization step in `scripts/agency_outreach.py` where Mistral AI generates a unique opening message for each agency, referencing their name and specific location details extracted from market listings.

## 3. Rationale (The "Proof")
* **Higher ROI:** Personalized outreach is a proven strategy for B2B engagement.
* **Scalability:** Generates hundreds of unique messages in minutes, which would be impossible manually.
* **Tone Control:** Ensures a professional but friendly Italian tone across all messages.

## 4. Consequences
* **Positive:** More "human-like" outreach. Improved dashboard stats for the agency client.
* **Negative/Trade-offs:** Slightly slower CSV generation due to LLM overhead. Dependency on Mistral being up during discovery runs.

## 5. Wiring Check (No Dead Code)
- [x] Meta-generation logic in `scripts/agency_outreach.py`
- [x] Container access for AI port in scripts.
