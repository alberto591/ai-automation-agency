-- ADR-027: Sales Journey v2 (Infrastructure Extension)
-- Run this in Supabase SQL Editor

-- 1. Add journey tracking columns to leads table
ALTER TABLE leads ADD COLUMN IF NOT EXISTS journey_state TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMPTZ;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS contract_url TEXT;

-- 2. (Optional) Add an index for journey state for faster filtering in the dashboard
CREATE INDEX IF NOT EXISTS idx_leads_journey_state ON leads(journey_state);
