-- 🗄️ Database Upgrade: Add Postcode to Lead Conversations
-- Run this in your Supabase SQL Editor

ALTER TABLE lead_conversations
ADD COLUMN IF NOT EXISTS postcode TEXT;

-- Optional: Add a comment to the column
COMMENT ON COLUMN lead_conversations.postcode IS 'Postal code (CAP) provided by the lead during appraisal or inquiry';
