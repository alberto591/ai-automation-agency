-- 🗄️ Database Upgrade: Mock Data Support
-- Run this in your Supabase SQL Editor

ALTER TABLE properties
ADD COLUMN IF NOT EXISTS is_mock BOOLEAN DEFAULT FALSE;

-- Optional: Index for faster filtering
CREATE INDEX IF NOT EXISTS idx_properties_is_mock ON properties(is_mock);

-- Comment
COMMENT ON COLUMN properties.is_mock IS 'Flag to identify test/demo data vs real production listings';
