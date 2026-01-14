-- 🔒 Enforce Strict Tenant Isolation (Multi-Tenancy)
-- Migration: enforce_tenant_isolation.sql

-- 1. Ensure RLS is enabled
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- 2. Drop "Public" or Permissive Policies
DROP POLICY IF EXISTS "Public Read Leads" ON leads;
DROP POLICY IF EXISTS "Public Insert Leads" ON leads;
DROP POLICY IF EXISTS "Public Update Leads" ON leads;

DROP POLICY IF EXISTS "Public Read Messages" ON messages;
DROP POLICY IF EXISTS "Public Insert Messages" ON messages;

-- 3. Strict LEADS Policies (Agency/User Scope)

-- View: strict ownership
CREATE POLICY "Users can only view own agency leads"
ON leads FOR SELECT
USING (agency_id = auth.uid());

-- Insert: must assign to self
CREATE POLICY "Users can insert leads for own agency"
ON leads FOR INSERT
WITH CHECK (agency_id = auth.uid());

-- Update: strict ownership
CREATE POLICY "Users can update own agency leads"
ON leads FOR UPDATE
USING (agency_id = auth.uid());

-- Delete: strict ownership
CREATE POLICY "Users can delete own agency leads"
ON leads FOR DELETE
USING (agency_id = auth.uid());


-- 4. Strict MESSAGES Policies (Via Lead Association)
-- Checking association via JOIN (exists)

-- View
CREATE POLICY "Users can view messages for own leads"
ON messages FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM leads
        WHERE leads.id = messages.lead_id
        AND leads.agency_id = auth.uid()
    )
);

-- Insert
CREATE POLICY "Users can insert messages for own leads"
ON messages FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM leads
        WHERE leads.id = messages.lead_id
        AND leads.agency_id = auth.uid()
    )
);

-- Note: Service Role (Backend) bypasses RLS by default, so Webhooks will still work
-- provided the backend uses the Service Key / Client.

-- 5. Helper: Assign Orphans (Optional run manually)
-- UPDATE leads SET agency_id = 'USER_UUID_HERE' WHERE agency_id IS NULL;
