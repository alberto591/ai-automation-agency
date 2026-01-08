-- Migration to support B2B Outreach and Market Discovery
-- Created: 2026-01-08

CREATE TABLE IF NOT EXISTS outreach_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    address TEXT,
    city TEXT,
    outreach_message TEXT,
    status TEXT DEFAULT 'PENDING', -- PENDING, CONTACTED, FAILED, INTERESTED
    last_contacted_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for phone lookups
CREATE INDEX IF NOT EXISTS idx_outreach_targets_phone ON outreach_targets(phone);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_outreach_targets_status ON outreach_targets(status);

-- Enable RLS
ALTER TABLE outreach_targets ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to manage targets
CREATE POLICY "Allow authenticated users to manage outreach targets"
    ON outreach_targets
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Market Data table (already exists but ensuring structure/index if needed)
-- Assuming market_data exists from market-data-migration.sql
-- Let's check it in the next step or just trust the previous analyzed scripts.
