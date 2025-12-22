-- 🏆 Database Optimization: Gold Standard Architecture
-- Run this in your Supabase SQL Editor.

-- =============================================
-- 1. PROPERTIES & MOCK_PROPERTIES (Inventory)
-- =============================================

-- A. Enforce Status Constraints
ALTER TABLE properties DROP CONSTRAINT IF EXISTS check_prop_status;
ALTER TABLE properties ADD CONSTRAINT check_prop_status 
CHECK (status IN ('available', 'reserved', 'sold', 'hidden'));

ALTER TABLE mock_properties DROP CONSTRAINT IF EXISTS check_mock_status;
ALTER TABLE mock_properties ADD CONSTRAINT check_mock_status 
CHECK (status IN ('available', 'reserved', 'sold', 'hidden'));

-- B. Performance Indexes
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_specs ON properties(rooms, sqm);
CREATE INDEX IF NOT EXISTS idx_mock_status ON mock_properties(status);

-- C. RLS Policies (Public Read, Agent Write)
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE mock_properties ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Public Read Properties" ON properties;
DROP POLICY IF EXISTS "Public Read Mock" ON mock_properties;

-- Create Clean Policies
CREATE POLICY "Public Read Properties" ON properties FOR SELECT USING (true);
CREATE POLICY "Public Read Mock" ON mock_properties FOR SELECT USING (true);
-- Note: Write policies usually require Auth, assuming Service Key for now for Backend

-- =============================================
-- 2. LEAD_CONVERSATIONS (CRM)
-- =============================================

-- A. Data Integrity
ALTER TABLE lead_conversations 
ALTER COLUMN is_ai_active SET DEFAULT TRUE,
ALTER COLUMN is_ai_active TYPE BOOLEAN USING is_ai_active::boolean;

-- B. Performance Indexes (Critical for Webhooks)
CREATE INDEX IF NOT EXISTS idx_leads_phone ON lead_conversations(customer_phone);
CREATE INDEX IF NOT EXISTS idx_leads_updated ON lead_conversations(updated_at DESC);

-- C. RLS Policies
ALTER TABLE lead_conversations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public Insert Leads" ON lead_conversations;
CREATE POLICY "Public Insert Leads" ON lead_conversations FOR INSERT WITH CHECK (true);

-- =============================================
-- 3. MARKET_DATA (Intelligence)
-- =============================================

-- A. Constraints
ALTER TABLE market_data ADD CONSTRAINT market_data_url_key UNIQUE (portal_url);

-- =============================================
-- 4. DOCUMENTS (Knowledge Base)
-- =============================================

-- A. Schema Definition
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    content TEXT, -- Extracted text content
    metadata JSONB DEFAULT '{}'::jsonb, -- Page numbers, author, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- B. Search Index (Gin for Metadata)
CREATE INDEX IF NOT EXISTS idx_docs_metadata ON documents USING GIN (metadata);

-- C. RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
