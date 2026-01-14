-- ==========================================
-- Multi-Tenancy Phase 2: Complete Data Isolation
-- Migration: 20260114_multi_tenancy_phase2.sql
-- ==========================================

-- 1. Helper for RLS (ensure it exists)
CREATE OR REPLACE FUNCTION public.get_current_tenant_id()
RETURNS UUID AS $$
BEGIN
    RETURN (auth.jwt() -> 'app_metadata' ->> 'active_org_id')::uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ==========================================
-- 2. PROPERTIES (Real & Mock)
-- ==========================================

-- A. Add tenant_id
ALTER TABLE properties
ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES organizations(id) ON DELETE SET NULL;

ALTER TABLE mock_properties
ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES organizations(id) ON DELETE SET NULL;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_props_tenant ON properties(tenant_id);
CREATE INDEX IF NOT EXISTS idx_mock_props_tenant ON mock_properties(tenant_id);

-- B. Strict RLS
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE mock_properties ENABLE ROW LEVEL SECURITY;

-- Drop Public Policies
DROP POLICY IF EXISTS "Public Read Properties" ON properties;
DROP POLICY IF EXISTS "Public Read Mock" ON mock_properties;

-- Create Tenant Policies
CREATE POLICY "Tenant isolation SELECT properties" ON properties FOR SELECT
USING (tenant_id = public.get_current_tenant_id());

CREATE POLICY "Tenant isolation INSERT properties" ON properties FOR INSERT
WITH CHECK (tenant_id = public.get_current_tenant_id());

CREATE POLICY "Tenant isolation UPDATE properties" ON properties FOR UPDATE
USING (tenant_id = public.get_current_tenant_id());

CREATE POLICY "Tenant isolation DELETE properties" ON properties FOR DELETE
USING (tenant_id = public.get_current_tenant_id());

-- Mock Properties Policies
CREATE POLICY "Tenant isolation SELECT mock" ON mock_properties FOR SELECT
USING (tenant_id = public.get_current_tenant_id());

CREATE POLICY "Tenant isolation INSERT mock" ON mock_properties FOR INSERT
WITH CHECK (tenant_id = public.get_current_tenant_id());


-- ==========================================
-- 3. DOCUMENTS (Knowledge Base)
-- ==========================================

-- A. Add tenant_id
ALTER TABLE documents
ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_docs_tenant ON documents(tenant_id);

-- B. Strict RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public Read Documents" ON documents; -- If it exists

CREATE POLICY "Tenant isolation SELECT documents" ON documents FOR SELECT
USING (tenant_id = public.get_current_tenant_id());

CREATE POLICY "Tenant isolation INSERT documents" ON documents FOR INSERT
WITH CHECK (tenant_id = public.get_current_tenant_id());

CREATE POLICY "Tenant isolation UPDATE documents" ON documents FOR UPDATE
USING (tenant_id = public.get_current_tenant_id());

CREATE POLICY "Tenant isolation DELETE documents" ON documents FOR DELETE
USING (tenant_id = public.get_current_tenant_id());


-- ==========================================
-- 4. SEMANTIC CACHE (AI Memory)
-- ==========================================

-- A. Add tenant_id
ALTER TABLE semantic_cache
ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_cache_tenant ON semantic_cache(tenant_id);

-- B. Strict RLS
ALTER TABLE semantic_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tenant isolation SELECT cache" ON semantic_cache FOR SELECT
USING (tenant_id = public.get_current_tenant_id());

CREATE POLICY "Tenant isolation INSERT cache" ON semantic_cache FOR INSERT
WITH CHECK (tenant_id = public.get_current_tenant_id());

-- C. Update RPC Function (Critical for Search)
-- We must update the match function to filter by tenant_id!
DROP FUNCTION IF EXISTS match_cache(vector, double precision, integer);

CREATE OR REPLACE FUNCTION match_cache (
  p_query_embedding vector(1024),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  query_text TEXT,
  response_text TEXT,
  similarity float
)
LANGUAGE plpgsql
AS $$
DECLARE
  current_tenant_id UUID;
BEGIN
  -- Get current tenant context
  current_tenant_id := (auth.jwt() -> 'app_metadata' ->> 'active_org_id')::uuid;

  RETURN QUERY
  SELECT
    c.query_text,
    c.response_text,
    (1 - (c.query_embedding <=> p_query_embedding))::float AS similarity
  FROM semantic_cache c
  WHERE
    c.tenant_id = current_tenant_id -- Strict Filter
    AND (1 - (c.query_embedding <=> p_query_embedding)) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;


-- ==========================================
-- 5. Grant Permissions
-- ==========================================
GRANT SELECT, INSERT, UPDATE, DELETE ON properties TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON mock_properties TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON documents TO authenticated;
GRANT SELECT, INSERT ON semantic_cache TO authenticated;

GRANT ALL ON properties TO service_role;
GRANT ALL ON mock_properties TO service_role;
GRANT ALL ON documents TO service_role;
GRANT ALL ON semantic_cache TO service_role;


-- ==========================================
-- MANUAL STEP: Backfill
-- ==========================================
-- Run manually after migration for your MAIN ADMIN tenant:
-- UPDATE properties SET tenant_id = 'YOUR-ORG-UUID' WHERE tenant_id IS NULL;
-- UPDATE mock_properties SET tenant_id = 'YOUR-ORG-UUID' WHERE tenant_id IS NULL;
-- UPDATE documents SET tenant_id = 'YOUR-ORG-UUID' WHERE tenant_id IS NULL;
-- UPDATE semantic_cache SET tenant_id = 'YOUR-ORG-UUID' WHERE tenant_id IS NULL;
