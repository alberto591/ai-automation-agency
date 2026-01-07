-- ==========================================
-- User Authentication & Authorization Schema
-- Migration: 20260107_user_authentication.sql
-- ==========================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 1. User Profiles Table
-- ==========================================
-- This table extends Supabase Auth's auth.users table
-- with application-specific profile data

CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    agency_name TEXT NOT NULL,
    phone TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_phone CHECK (phone IS NULL OR phone ~* '^\+?[0-9]{9,15}$')
);

-- Create index for faster email lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON public.user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- 2. Row Level Security (RLS) Policies
-- ==========================================

ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Users can view their own profile
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
CREATE POLICY "Users can view own profile"
    ON public.user_profiles FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
CREATE POLICY "Users can update own profile"
    ON public.user_profiles FOR UPDATE
    USING (auth.uid() = id);

-- Users can insert their own profile (during registration)
DROP POLICY IF EXISTS "Users can insert own profile" ON public.user_profiles;
CREATE POLICY "Users can insert own profile"
    ON public.user_profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ==========================================
-- 3. Link Leads to Agencies (Users)
-- ==========================================

-- Add agency_id to leads table
ALTER TABLE public.leads
ADD COLUMN IF NOT EXISTS agency_id UUID REFERENCES public.user_profiles(id) ON DELETE SET NULL;

-- Create index for faster agency-based queries
CREATE INDEX IF NOT EXISTS idx_leads_agency_id ON public.leads(agency_id);

-- Enable RLS on leads table
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;

-- Users can view only their own agency's leads
DROP POLICY IF EXISTS "Users can view own agency leads" ON public.leads;
CREATE POLICY "Users can view own agency leads"
    ON public.leads FOR SELECT
    USING (auth.uid() = agency_id);

-- Users can insert leads for their own agency
DROP POLICY IF EXISTS "Users can insert own agency leads" ON public.leads;
CREATE POLICY "Users can insert own agency leads"
    ON public.leads FOR INSERT
    WITH CHECK (auth.uid() = agency_id);

-- Users can update their own agency's leads
DROP POLICY IF EXISTS "Users can update own agency leads" ON public.leads;
CREATE POLICY "Users can update own agency leads"
    ON public.leads FOR UPDATE
    USING (auth.uid() = agency_id);

-- ==========================================
-- 4. Migration for Existing Data
-- ==========================================

-- Create a default "demo" agency for orphaned leads
-- This can be manually assigned later
DO $$
DECLARE
    demo_user_id UUID;
BEGIN
    -- Check if there are any orphaned leads (leads without agency_id)
    -- If so, we can either leave them null or create a demo user
    -- For now, we'll just log the count
    RAISE NOTICE 'Orphaned leads count: %', (SELECT COUNT(*) FROM public.leads WHERE agency_id IS NULL);
END $$;

-- ==========================================
-- 5. Function: Auto-create profile on signup
-- ==========================================

-- This function automatically creates a user_profile when a new user signs up via Supabase Auth
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, email, agency_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'agency_name', 'Unnamed Agency')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to call the function
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ==========================================
-- 6. Comments for Documentation
-- ==========================================

COMMENT ON TABLE public.user_profiles IS 'Extended user profile data for agency accounts';
COMMENT ON COLUMN public.user_profiles.agency_name IS 'Real estate agency name';
COMMENT ON COLUMN public.user_profiles.phone IS 'Agency contact phone number';
COMMENT ON COLUMN public.leads.agency_id IS 'Reference to the agency that owns this lead';

-- ==========================================
-- 7. Grant Permissions
-- ==========================================

-- Grant necessary permissions to authenticated users
GRANT SELECT, INSERT, UPDATE ON public.user_profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.leads TO authenticated;

-- Service role has full access (for backend operations)
GRANT ALL ON public.user_profiles TO service_role;
GRANT ALL ON public.leads TO service_role;
