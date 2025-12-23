-- 🏗️ Phase 2: Database Normalization
-- Run this in Supabase SQL Editor

-- 1. Create AGENTS table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id), -- Link to Supabase Auth
    full_name TEXT,
    role TEXT DEFAULT 'agent', -- 'admin', 'agent'
    email TEXT UNIQUE,
    phone TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create LEADS table (Profile info only)
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_phone TEXT UNIQUE NOT NULL,
    customer_name TEXT,
    status TEXT DEFAULT 'new', -- 'new', 'contacted', 'qualified', 'lost'
    is_ai_active BOOLEAN DEFAULT TRUE,

    -- Preferences
    budget_max INTEGER,
    postcode TEXT,
    preferred_zones TEXT[], -- Array of strings
    lead_type TEXT DEFAULT 'buyer',

    -- Metadata
    score INTEGER DEFAULT 0,
    ai_summary TEXT,
    assigned_agent_id UUID REFERENCES agents(id),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create MESSAGES table (Atomic chat history)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    role TEXT NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT,
    metadata JSONB DEFAULT '{}'::jsonb, -- token_count, latency, etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Create EVENTS table (Audit log)
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL, -- 'STATUS_CHANGE', 'LEAD_CREATED'
    payload JSONB,
    actor_id UUID, -- Could be agent_id or NULL (system)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_leads_agent ON leads(assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_messages_lead ON messages(lead_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);

-- 6. Enable RLS
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- 7. Basic Policies (Adjust as needed)
CREATE POLICY "Public Insert Leads" ON leads FOR INSERT WITH CHECK (true);
CREATE POLICY "Public Read Leads" ON leads FOR SELECT USING (true);
CREATE POLICY "Public Insert Messages" ON messages FOR INSERT WITH CHECK (true);
CREATE POLICY "Public Read Messages" ON messages FOR SELECT USING (true);
