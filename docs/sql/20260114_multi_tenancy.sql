-- ==========================================
-- Multi-Tenancy: Enterprise Data Isolation
-- Migration: 20260114_multi_tenancy.sql
-- ==========================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 1. Organizations (Tenants) Table
-- ==========================================
CREATE TABLE IF NOT EXISTS public.organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_organizations_slug ON public.organizations(slug);

-- ==========================================
-- 2. Organization Members (User <-> Org)
-- ==========================================
CREATE TABLE IF NOT EXISTS public.organization_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, organization_id)
);

CREATE INDEX IF NOT EXISTS idx_org_members_user ON public.organization_members(user_id);
CREATE INDEX IF NOT EXISTS idx_org_members_org ON public.organization_members(organization_id);

-- ==========================================
-- 3. Helper Function: Get Current Tenant ID
-- ==========================================
-- Extracts active_org_id from JWT app_metadata
CREATE OR REPLACE FUNCTION public.get_current_tenant_id()
RETURNS UUID AS $$
BEGIN
    RETURN (auth.jwt() -> 'app_metadata' ->> 'active_org_id')::uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ==========================================
-- 4. Add tenant_id to Data Tables
-- ==========================================

-- 4a. Leads Table
ALTER TABLE public.leads
ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_leads_tenant ON public.leads(tenant_id);

-- 4b. Properties Table (if exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'properties') THEN
        ALTER TABLE public.properties
        ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL;
        CREATE INDEX IF NOT EXISTS idx_properties_tenant ON public.properties(tenant_id);
    END IF;
END $$;

-- ==========================================
-- 5. RLS Policies for Organizations
-- ==========================================
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own organizations" ON public.organizations;
CREATE POLICY "Users can view own organizations"
ON public.organizations FOR SELECT
USING (
    id IN (
        SELECT organization_id FROM public.organization_members
        WHERE user_id = auth.uid()
    )
);

-- ==========================================
-- 6. RLS Policies for Organization Members
-- ==========================================
ALTER TABLE public.organization_members ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own memberships" ON public.organization_members;
CREATE POLICY "Users can view own memberships"
ON public.organization_members FOR SELECT
USING (user_id = auth.uid());

-- ==========================================
-- 7. Strict RLS Policies for Leads
-- ==========================================
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;

-- Drop old permissive policies
DROP POLICY IF EXISTS "Public Read Leads" ON public.leads;
DROP POLICY IF EXISTS "Public Insert Leads" ON public.leads;
DROP POLICY IF EXISTS "Users can view own agency leads" ON public.leads;
DROP POLICY IF EXISTS "Users can insert own agency leads" ON public.leads;
DROP POLICY IF EXISTS "Users can update own agency leads" ON public.leads;

-- Strict tenant-based policies
DROP POLICY IF EXISTS "Tenant isolation SELECT leads" ON public.leads;
CREATE POLICY "Tenant isolation SELECT leads"
ON public.leads FOR SELECT
USING (tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "Tenant isolation INSERT leads" ON public.leads;
CREATE POLICY "Tenant isolation INSERT leads"
ON public.leads FOR INSERT
WITH CHECK (tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "Tenant isolation UPDATE leads" ON public.leads;
CREATE POLICY "Tenant isolation UPDATE leads"
ON public.leads FOR UPDATE
USING (tenant_id = public.get_current_tenant_id());

DROP POLICY IF EXISTS "Tenant isolation DELETE leads" ON public.leads;
CREATE POLICY "Tenant isolation DELETE leads"
ON public.leads FOR DELETE
USING (tenant_id = public.get_current_tenant_id());

-- ==========================================
-- 8. RLS Policies for Messages (via Lead)
-- ==========================================
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public Read Messages" ON public.messages;
DROP POLICY IF EXISTS "Public Insert Messages" ON public.messages;

DROP POLICY IF EXISTS "Tenant isolation SELECT messages" ON public.messages;
CREATE POLICY "Tenant isolation SELECT messages"
ON public.messages FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.leads
        WHERE leads.id = messages.lead_id
        AND leads.tenant_id = public.get_current_tenant_id()
    )
);

DROP POLICY IF EXISTS "Tenant isolation INSERT messages" ON public.messages;
CREATE POLICY "Tenant isolation INSERT messages"
ON public.messages FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.leads
        WHERE leads.id = messages.lead_id
        AND leads.tenant_id = public.get_current_tenant_id()
    )
);

-- ==========================================
-- 9. Organization Invitations (Invite-Only Model)
-- ==========================================
CREATE TABLE IF NOT EXISTS public.organization_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role TEXT DEFAULT 'member' CHECK (role IN ('admin', 'member')),
    invited_by UUID REFERENCES auth.users(id),
    token TEXT UNIQUE NOT NULL DEFAULT encode(gen_random_bytes(32), 'hex'),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '7 days',
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, email)
);

CREATE INDEX IF NOT EXISTS idx_invitations_email ON public.organization_invitations(email);
CREATE INDEX IF NOT EXISTS idx_invitations_token ON public.organization_invitations(token);

-- RLS for invitations
ALTER TABLE public.organization_invitations ENABLE ROW LEVEL SECURITY;

-- Org owners/admins can view their org's invitations
DROP POLICY IF EXISTS "Org admins can view invitations" ON public.organization_invitations;
CREATE POLICY "Org admins can view invitations"
ON public.organization_invitations FOR SELECT
USING (
    organization_id IN (
        SELECT organization_id FROM public.organization_members
        WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
);

-- Org owners/admins can create invitations
DROP POLICY IF EXISTS "Org admins can create invitations" ON public.organization_invitations;
CREATE POLICY "Org admins can create invitations"
ON public.organization_invitations FOR INSERT
WITH CHECK (
    organization_id IN (
        SELECT organization_id FROM public.organization_members
        WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
);

-- ==========================================
-- 10. Accept Invitation on Signup
-- ==========================================
-- When a new user signs up, check if they have a pending invitation
CREATE OR REPLACE FUNCTION public.handle_new_user_invitation()
RETURNS TRIGGER AS $$
DECLARE
    invite RECORD;
BEGIN
    -- Check for pending invitation
    SELECT * INTO invite
    FROM public.organization_invitations
    WHERE email = NEW.email
    AND accepted_at IS NULL
    AND expires_at > NOW()
    ORDER BY created_at DESC
    LIMIT 1;

    IF invite IS NOT NULL THEN
        -- Add user to organization
        INSERT INTO public.organization_members (user_id, organization_id, role)
        VALUES (NEW.id, invite.organization_id, invite.role);

        -- Mark invitation as accepted
        UPDATE public.organization_invitations
        SET accepted_at = NOW()
        WHERE id = invite.id;

        -- Set active_org_id in app_metadata
        UPDATE auth.users
        SET raw_app_meta_data = COALESCE(raw_app_meta_data, '{}'::jsonb) ||
            jsonb_build_object('active_org_id', invite.organization_id::text)
        WHERE id = NEW.id;
    END IF;
    -- If no invitation, user has no org access until invited

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop old trigger if exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Create new trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user_invitation();

-- ==========================================
-- 11. Grant Permissions
-- ==========================================
GRANT SELECT ON public.organizations TO authenticated;
GRANT SELECT ON public.organization_members TO authenticated;
GRANT SELECT, INSERT ON public.organization_invitations TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.leads TO authenticated;
GRANT SELECT, INSERT ON public.messages TO authenticated;

-- Service role has full access (for backend/webhooks)
GRANT ALL ON public.organizations TO service_role;
GRANT ALL ON public.organization_members TO service_role;
GRANT ALL ON public.organization_invitations TO service_role;
GRANT ALL ON public.leads TO service_role;
GRANT ALL ON public.messages TO service_role;

-- ==========================================
-- MANUAL STEP: Backfill Existing Data
-- ==========================================
-- After running this migration, run these manually:
--
-- 1. Create org for existing admin:
-- INSERT INTO organizations (id, name, slug)
-- VALUES ('YOUR-ORG-UUID', 'Anzevino Realty', 'anzevino-realty');
--
-- 2. Link admin to org:
-- INSERT INTO organization_members (user_id, organization_id, role)
-- VALUES ('YOUR-ADMIN-USER-UUID', 'YOUR-ORG-UUID', 'owner');
--
-- 3. Backfill leads:
-- UPDATE leads SET tenant_id = 'YOUR-ORG-UUID' WHERE tenant_id IS NULL;
--
-- 4. Update admin JWT metadata:
-- UPDATE auth.users
-- SET raw_app_meta_data = raw_app_meta_data || '{"active_org_id": "YOUR-ORG-UUID"}'
-- WHERE id = 'YOUR-ADMIN-USER-UUID';
