-- Create market_data table for competitive analysis
CREATE TABLE IF NOT EXISTS market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portal_url TEXT UNIQUE NOT NULL,
    title TEXT,
    price FLOAT,
    sqm FLOAT,
    price_per_mq FLOAT,
    zone TEXT,
    city TEXT DEFAULT 'Milano',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;

-- Simple policy for public read (optional, following existing pattern)
CREATE POLICY "Allow public read on market_data" ON market_data FOR SELECT USING (true);
