-- Lead Qualification Analytics Enhancement
-- Migration Date: 2025-01-02

-- Create qualification events tracking table
CREATE TABLE IF NOT EXISTS qualification_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL, -- 'started', 'question_answered', 'completed', 'abandoned'
    question_number INTEGER,
    answer_value TEXT,
    score_at_event INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_qual_events_lead ON qualification_events(lead_id);
CREATE INDEX IF NOT EXISTS idx_qual_events_type ON qualification_events(event_type);
CREATE INDEX IF NOT EXISTS idx_qual_events_created ON qualification_events(created_at DESC);

-- Add routing and analytics fields to leads table
ALTER TABLE leads
ADD COLUMN IF NOT EXISTS assigned_agent_id UUID,
ADD COLUMN IF NOT EXISTS routing_reason TEXT,
ADD COLUMN IF NOT EXISTS qualification_completed_at TIMESTAMPTZ;

-- Create index for agent routing queries
CREATE INDEX IF NOT EXISTS idx_leads_assigned_agent ON leads(assigned_agent_id) WHERE assigned_agent_id IS NOT NULL;

-- Create view for analytics (optional, for easier querying)
CREATE OR REPLACE VIEW qualification_analytics AS
SELECT
    DATE(created_at) as date,
    COUNT(*) FILTER (WHERE event_type = 'started') as started_count,
    COUNT(*) FILTER (WHERE event_type = 'completed') as completed_count,
    COUNT(*) FILTER (WHERE event_type = 'abandoned') as abandoned_count,
    ROUND(
        COUNT(*) FILTER (WHERE event_type = 'completed')::DECIMAL /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'started'), 0) * 100,
        2
    ) as completion_rate_pct
FROM qualification_events
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

COMMENT ON TABLE qualification_events IS 'Tracks each step of the lead qualification flow for analytics';
COMMENT ON COLUMN leads.assigned_agent_id IS 'Agent automatically assigned based on lead score';
COMMENT ON COLUMN leads.routing_reason IS 'Explanation of why lead was routed to this agent (e.g., "Score 8/10 - HOT lead")';
COMMENT ON COLUMN leads.qualification_completed_at IS 'Timestamp when qualification flow was completed';
