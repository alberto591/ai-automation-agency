-- 🗄️ Database Setup Script
-- Based on database_standards.md
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. PROPERTIES
CREATE TABLE IF NOT EXISTS properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT,
    description TEXT,
    price NUMERIC,
    status TEXT DEFAULT 'available', -- 'available', 'reserved', 'sold'
    sqm INTEGER,
    rooms INTEGER,
    bathrooms INTEGER,
    floor INTEGER,
    energy_class TEXT,
    has_elevator BOOLEAN DEFAULT FALSE,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. LEAD CONVERSATIONS
CREATE TABLE IF NOT EXISTS lead_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_phone TEXT UNIQUE NOT NULL,
    messages JSONB DEFAULT '[]'::jsonb,
    status TEXT DEFAULT 'active', -- 'active', 'hot', 'human_mode'
    is_ai_active BOOLEAN DEFAULT TRUE,
    budget_max INTEGER,
    preferred_zones TEXT[],
    lead_type TEXT DEFAULT 'buyer',
    postcode TEXT, 
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. MARKET DATA
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portal_url TEXT UNIQUE NOT NULL,
    title TEXT,
    price NUMERIC,
    sqm NUMERIC,
    price_per_mq NUMERIC,
    zone TEXT,
    city TEXT DEFAULT 'Milano',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. INDEXES
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_sqm ON properties(sqm);
CREATE INDEX IF NOT EXISTS idx_lead_conversations_phone ON lead_conversations(customer_phone);

-- 5. STORAGE BUCKETS
-- Safely insert bucket if it doesn't exist
INSERT INTO storage.buckets (id, name, public)
VALUES ('chat-attachments', 'chat-attachments', true)
ON CONFLICT (id) DO NOTHING;

-- 6. RLS & POLICIES
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;

-- Basic Public Read Policies (Idempotent creation)
DO $$ 
BEGIN
    -- Properties
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'properties' AND policyname = 'Public read properties') THEN
        CREATE POLICY "Public read properties" ON properties FOR SELECT USING (true);
    END IF;

    -- Market Data
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'market_data' AND policyname = 'Public read market_data') THEN
        CREATE POLICY "Public read market_data" ON market_data FOR SELECT USING (true);
    END IF;

    -- Storage: Public Uploads
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'objects' AND policyname = 'Allow public uploads') THEN
        CREATE POLICY "Allow public uploads" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'chat-attachments');
    END IF;

    -- Storage: Public Viewing
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'objects' AND policyname = 'Allow public viewing') THEN
        CREATE POLICY "Allow public viewing" ON storage.objects FOR SELECT USING (bucket_id = 'chat-attachments');
    END IF;
END $$;
