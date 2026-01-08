-- Migration: Multi-Agent Routing Support
-- Date: 2026-01-08

-- 1. Extend public.users with routing fields
-- Assumes public.users exists (from 20260107_user_authentication.sql)
-- If not, create it minimalistically first

CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    role TEXT DEFAULT 'agent'
);

ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS zones TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- 2. Add assignment to leads
ALTER TABLE public.leads
ADD COLUMN IF NOT EXISTS assigned_agent_id UUID REFERENCES public.users(id);

-- 3. RLS Policies for Leads (Agents see only their leads or all if admin)
-- Note: Assuming existing policies allow "service_role" unrestricted.
-- We add policy for "Agents view assigned leads"

CREATE POLICY "Agents view assigned leads" ON public.leads
FOR SELECT
USING (
    auth.uid() = assigned_agent_id
    OR
    EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND role = 'admin')
);

-- 4. Index for performance
CREATE INDEX IF NOT EXISTS idx_leads_assigned_agent ON public.leads(assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_users_zones ON public.users USING GIN(zones);
