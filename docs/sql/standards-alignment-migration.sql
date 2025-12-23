-- 🗄️ Database Standards Alignment & Hardening
-- Run this in your Supabase SQL Editor to enforce project standards.

-- 1. PROPERTIES table alignment
-- Ensure all standard columns exist with correct types
ALTER TABLE properties
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'available',
ADD COLUMN IF NOT EXISTS image_url TEXT,
ADD COLUMN IF NOT EXISTS has_elevator BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS energy_class TEXT;

-- Add constraints for data integrity
ALTER TABLE properties
DROP CONSTRAINT IF EXISTS check_status_valid;

ALTER TABLE properties
ADD CONSTRAINT check_status_valid
CHECK (status IN ('available', 'reserved', 'sold', 'hidden'));

-- Indexing for performance (Mobile App filters)
CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_specs ON properties(rooms, sqm);


-- 2. LEADS table alignment (lead_conversations)
-- Ensure explicit columns for AI logic
ALTER TABLE lead_conversations
ADD COLUMN IF NOT EXISTS is_ai_active BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS lead_type TEXT DEFAULT 'buyer';

-- Indexes for realtime subscriptions and webhooks
CREATE INDEX IF NOT EXISTS idx_lead_phone ON lead_conversations(customer_phone);
CREATE INDEX IF NOT EXISTS idx_lead_updated_at ON lead_conversations(updated_at DESC);


-- 3. RLS (Row Level Security) - "Security by Default"
-- Enable RLS on all tables
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;

-- 4. POLICIES (Simple examples for prototype)
-- Allow public read of available properties
DROP POLICY IF EXISTS "Public View Properties" ON properties;
CREATE POLICY "Public View Properties"
ON properties FOR SELECT
USING (status = 'available' OR is_mock = TRUE);

-- Allow anyone to insert leads (Webhooks/App usage)
DROP POLICY IF EXISTS "Public Insert Leads" ON lead_conversations;
CREATE POLICY "Public Insert Leads"
ON lead_conversations FOR INSERT
WITH CHECK (true);

-- Allow public read of own leads (demo mode - usually strict user check)
DROP POLICY IF EXISTS "Public View Leads" ON lead_conversations;
CREATE POLICY "Public View Leads"
ON lead_conversations FOR SELECT
USING (true);
