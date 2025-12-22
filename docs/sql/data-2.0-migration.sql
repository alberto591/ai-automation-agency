-- 🗄️ Database Upgrade: Data 2.0 Strategy

-- 1. Upgrade 'properties' table with modular attributes
ALTER TABLE properties
ADD COLUMN IF NOT EXISTS sqm INTEGER,
ADD COLUMN IF NOT EXISTS rooms INTEGER,
ADD COLUMN IF NOT EXISTS bathrooms INTEGER,
ADD COLUMN IF NOT EXISTS energy_class TEXT,
ADD COLUMN IF NOT EXISTS floor INTEGER,
ADD COLUMN IF NOT EXISTS has_elevator BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'available', -- available, reserved, sold
ADD COLUMN IF NOT EXISTS image_url TEXT;

-- 2. Upgrade 'lead_conversations' with lead profiling
ALTER TABLE lead_conversations
ADD COLUMN IF NOT EXISTS budget_max INTEGER,
ADD COLUMN IF NOT EXISTS preferred_zones TEXT[],
ADD COLUMN IF NOT EXISTS lead_type TEXT DEFAULT 'buyer'; -- buyer, seller, renter

-- 3. Add index for performance on price and sqm searches
CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_sqm ON properties(sqm);

-- 4. Enable RLS (Row Level Security) if not already enabled (Safe mode)
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;

-- 5. Create basic public read policy if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'properties' AND policyname = 'Public read access'
    ) THEN
        CREATE POLICY "Public read access" ON properties FOR SELECT USING (true);
    END IF;
END $$;
