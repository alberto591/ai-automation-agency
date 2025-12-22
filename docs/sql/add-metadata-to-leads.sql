-- 🗄️ Add metadata column to leads table for enriched agent state
-- This column will store structured data like property preferences and sentiment analysis.

ALTER TABLE leads ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- Comment for clarity
COMMENT ON COLUMN leads.metadata IS 'Stores enriched AI state such as PropertyPreferences and SentimentAnalysis results.';
