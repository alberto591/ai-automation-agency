-- 🗄️ Database Upgrade: Split Mock & Production Data
-- Run this in your Supabase SQL Editor

-- 1. Create separate table for Mock Data (Cloning structure of properties)
CREATE TABLE IF NOT EXISTS mock_properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT,
    description TEXT,
    price FLOAT,
    sqm INTEGER,
    rooms INTEGER,
    bathrooms INTEGER,
    floor INTEGER,
    energy_class TEXT,
    has_elevator BOOLEAN DEFAULT FALSE,
    image_url TEXT,
    status TEXT DEFAULT 'available',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Clean up 'properties' table
-- First, drop the policy that depends on is_mock
DROP POLICY IF EXISTS "Public View Properties" ON properties;

-- Recreate policies for production properties (strict)
CREATE POLICY "Public View Properties" 
ON properties FOR SELECT 
USING (status = 'available');

-- Now safe to drop the column
ALTER TABLE properties DROP COLUMN IF EXISTS is_mock;

-- 3. Security: Enable RLS on new table
ALTER TABLE mock_properties ENABLE ROW LEVEL SECURITY;

-- 4. Policies for Mock Table (Permissive for testing)
CREATE POLICY "Public Read Mock" ON mock_properties FOR SELECT USING (true);
CREATE POLICY "Public Write Mock" ON mock_properties FOR INSERT WITH CHECK (true);
CREATE POLICY "Public Update Mock" ON mock_properties FOR UPDATE USING (true);
CREATE POLICY "Public Delete Mock" ON mock_properties FOR DELETE USING (true);

-- 5. Add Indexing to match production
CREATE INDEX IF NOT EXISTS idx_mock_price ON mock_properties(price);
CREATE INDEX IF NOT EXISTS idx_mock_sqm ON mock_properties(sqm);
