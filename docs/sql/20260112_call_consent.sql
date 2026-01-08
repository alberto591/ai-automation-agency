-- Migration: Call Recording Consent (GDPR Compliance)
-- Date: 2026-01-12
-- Purpose: Track user consent for call recordings per Italian GDPR requirements

CREATE TABLE IF NOT EXISTS call_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id TEXT NOT NULL,
    phone TEXT NOT NULL,
    consent_given BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMPTZ,
    consent_method TEXT CHECK (consent_method IN ('ivr', 'verbal', 'written')),
    recording_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_call_consents_phone ON call_consents(phone);
CREATE INDEX IF NOT EXISTS idx_call_consents_timestamp ON call_consents(consent_timestamp DESC);

-- Add RLS policies
ALTER TABLE call_consents ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "Service role has full access to call_consents"
    ON call_consents
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Allow authenticated users to view their own consents
CREATE POLICY "Users can view their own call consents"
    ON call_consents
    FOR SELECT
    TO authenticated
    USING (phone = current_setting('request.jwt.claims', true)::json->>'phone');

COMMENT ON TABLE call_consents IS 'GDPR-compliant call recording consent tracking';
COMMENT ON COLUMN call_consents.consent_method IS 'How consent was obtained: ivr (automated), verbal (during call), written (email/sms)';
COMMENT ON COLUMN call_consents.consent_timestamp IS 'When user provided consent (NULL if consent_given = FALSE)';
