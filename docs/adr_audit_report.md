# ADR Implementation Audit Report

I have reviewed all 22 documents in `docs/adr/` and cross-referenced them with the current implementation in `backend/` and `dashboard/`.

## Critical Gaps (Unimplemented)

| ADR # | Decision Topic | Status | Finding |
| :--- | :--- | :--- | :--- |
| **ADR-002** | **Hybrid Search (Vector + SQL)** | ⚠️ Partial | `SupabaseAdapter.get_properties` uses `ilike` on descriptions. Hybrid vector search with `pgvector` is missing. |
| **ADR-004** | **Credulity Testing** | ❌ Missing | No similarity threshold check (0.78) or grounded verification exists in `LeadProcessor`. |
| **ADR-019** | **Semantic Answer Cache** | ❌ Missing | No vector-based lookup for similar queries is implemented. |
| **ADR-023** | **Max Tokens Centralization** | ❌ Missing | `MAX_CONTEXT_MESSAGES` is not in `settings.py`. History growth is currently unmanaged. |
| **ADR-027** | **Law Firm v2 (Scheduling)** | ❌ Missing | Appointment scheduling (Google Calendar) and legal doc templates are not yet built. |

## Partially Implemented / Verification Needed

- **ADR-017 (BPR)**: The `best_practices/` folder exists but only contains the `retriever.py` script. The actual pattern library definitions are sparse.
- **ADR-003 (Parallel Safety)**: With the recent move to `BackgroundTasks` (ADR context), we may need to ensure serial processing per-lead to prevent race conditions if a user sends multiple rapid messages.

## Fully Implemented (Success)

- **ADR-001**: Hexagonal Architecture (Ports and Adapters).
- **ADR-007**: Twilio for WhatsApp Messaging.
- **ADR-008**: Real-Time Dashboard Sync (Supabase Realtime).
- **ADR-009**: Modular React Components & Hooks.
- **ADR-013**: Client-Side Search/Filtering.
- **ADR-015**: Mobile Strategy (Expo/React Native).
- **ADR-016**: Debug Everything Protocol (`scripts/debug_everything.py`).
- **ADR-018**: Lead Scoring (Heuristics).
- **ADR-022**: Mistral AI Integration.
- **ADR-025**: Human-AI Handover (Dashboard Toggles).
- **ADR-029**: Mobile Direct-to-Storage Uploads.

## Recommendations

1. **Implement ADR-023**: Add a sliding window for conversation history to prevent LLM prompt overflow.
2. **Upgrade ADR-002**: Transition from keyword search (`ilike`) to `pgvector` similarity search to match the ADR's decision.
3. **Add ADR-004 Grounding**: Implement the similarity threshold check to avoid hallucinations.
