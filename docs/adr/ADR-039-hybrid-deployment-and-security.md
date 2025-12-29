# ADR [039]: Hybrid Deployment & Security Architecture

**Status:** Accepted
**Date:** 2025-12-30
**Author:** Antigravity

## 1. Context (The "Why")
As the project transitions from a local prototype to a production-ready system, we needed a robust deployment strategy that:
*   Supports a monorepo structure (Vite + FastAPI).
*   Ensures secure access to lead data.
*   Automates quality checks (CI) to prevent regressions.
*   Handles regional latency (Italy-based users).

## 2. Decision
We have adopted a **Hybrid Cloud Strategy** leveraging Vercel and Supabase:

### 2.1. Vercel for Compute (Edge + Serverless)
*   **Frontend**: Hosted as a static Vite application on Vercel's Edge network.
*   **Backend**: FastAPI routes exposed via Vercel Serverless Functions using the `api/index.py` bridge.
*   **Routing**: Defined in `vercel.json` to unify the domain (e.g., `/api/*` routes to backend, others to frontend).

### 2.2. Supabase for Data & Identity
*   **Auth**: Primary identity provider via Supabase Auth (JWT).
*   **Storage/DB**: Managed PostgreSQL with Realtime enabled for the dashboard.
*   **Security (RLS)**: Enforced Row Level Security on `leads` and `messages`.
    *   *Anonymous*: Blocked.
    *   *Authenticated Users (Agents)*: Full access to the dashboard.
    *   *Internal Services (AI Agent)*: Bypass RLS using the `service_role` key in the adapter.

### 2.3. CI/CD Workflow (GitHub Actions)
*   **Validation**: Every push to `master` triggers a GitHub Action (`deploy.yml`).
*   **Test Suite**:
    *   Runs `pytest tests/unit` to ensure core logic and API contracts are intact.
    *   *Note*: Integration tests are currently skipped in CI to avoid dependency on live Twilio/Mistral credentials, requiring manual verification before merge.

### 2.4. Lightweight Migrations
*   Instead of an ORM (Alembic), we use idempotent SQL scripts in `scripts/migrations/`.
*   This reduces the runtime footprint on serverless functions and allows for quick manual application via the Supabase SQL Editor.

## 3. Rationale (The "Proof")
*   **Zero-Downtime**: Vercel handles blue-green deployments out of the box.
*   **Cost Efficiency**: Serverless functions scale to zero, minimizing idle costs during non-business hours.
*   **Security First**: RLS ensures that even if a frontend exploit occurs, the database remains protected at the storage level.

## 4. Consequences
*   **Positive:** Simplified deployment, high global availability, and strong security defaults.
*   **Trade-offs:** Serverless cold starts may occasionally impact API responsiveness. Background tasks (like IMAP polling) require external triggers (Vercel Cron or GitHub Action schedules).

## 5. Wiring Check (No Dead Code)
- [x] `vercel.json` configured and verified.
- [x] RLS Policies active on Supabase.
- [x] `.github/workflows/deploy.yml` passing unit tests.
- [x] Environment variables standardized across `.env` and Vercel Dashboard.
