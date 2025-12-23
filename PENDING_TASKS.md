# 📋 Agenzia AI: Consolidated Pending Tasks

This file tracks uncompleted tasks identified from historical agent logs, documentation, and the strategic roadmap.

## 🏗️ Structural & Architectural
- [x] **Root Reorganization**: ~20 scripts moved from the root into `scripts/` and `test_scripts/`.
- [x] **Code Hygiene**: All type errors in `application/workflows/agents.py` and `application/services/journey_manager.py` resolved.
- [x] **Infrastructure Decoupling**: Direct infrastructure imports removed from the application layer (Logging moved to Domain).
- [x] **ADR Completion**: Create/Finalize ADRs for recent structural changes (e.g., Appraisal Tool isolation, Database Normalization).

## 📱 Dashboard & CRM
- [x] **Lead Actions**: Implement "Modify Profile" in the dashboard frontend.
- [x] **Data Management**: Implement "Archive Conversation" to filter the lead list.
- [x] **Real-time Sync**: Verify and polish Supabase real-time updates for the inbox.
- [x] **Seed Data**: Successfully run the rich property/lead seed scripts (resolved RLS blockers).

## 🚀 Feature Roadmap
- [x] **English Support**: Improved language detection and dedicated "Tourist" persona implemented. **Live integration active**.
- [x] **Setmore Integration**: Infrastructure and Webhooks implemented. **Awaiting Pro Account** for API activation.
- [x] **Market Analysis**: Dynamic area insights and negotiation reasoning implemented. **Live integration active**.
- [x] **PDF Property Cards**: Professional generator integrated into the bot flow (JourneyManager/LeadProcessor). **Live integration active**.

## 🧪 Testing & DevOps
- [x] **CI/CD Compliance**: Resolve all `ruff` and `mypy` errors so `make check-all` passes reliably.
- [x] **E2E Simulation**: Run a full lifecycle test against the `sales-journey-blueprint.md`.
- [x] **Monitoring**: Set up basic error monitoring for the production API (Structured Logging integrated).

---
*Created on 2025-12-23. Mark items as [x] once completed.*
