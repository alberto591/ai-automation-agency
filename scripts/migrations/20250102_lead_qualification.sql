-- Migration: Lead Qualification Headers
-- Date: 2025-01-02
-- Description: Adds columns for lead qualification scoring and data tracking

-- 1. Add qualification columns to leads table
ALTER TABLE public.leads
ADD COLUMN IF NOT EXISTS qualification_score INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS qualification_status TEXT DEFAULT 'COLD', -- HOT, WARM, COLD, NEW
ADD COLUMN IF NOT EXISTS qualification_data JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS last_qualified_at TIMESTAMPTZ;

-- 2. Add index for finding High Value leads quickly
CREATE INDEX IF NOT EXISTS idx_leads_qualification_score ON public.leads(qualification_score DESC);

-- 3. Add index for filtering by status (e.g. "Get all HOT leads")
CREATE INDEX IF NOT EXISTS idx_leads_qualification_status ON public.leads(qualification_status);
