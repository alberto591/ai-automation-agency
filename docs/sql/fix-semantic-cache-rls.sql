-- Enable Row Level Security (RLS) for semantic_cache
-- This fixes the security warning in Supabase and restricts public access.

ALTER TABLE public.semantic_cache ENABLE ROW LEVEL SECURITY;

-- 1. Policy for Authenticated Users (Dashboard/App)
-- Allows reading and writing to the cache for authenticated users.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'semantic_cache' AND policyname = 'Allow authenticated access to semantic_cache') THEN
        CREATE POLICY "Allow authenticated access to semantic_cache"
        ON public.semantic_cache
        FOR ALL
        TO authenticated
        USING (true)
        WITH CHECK (true);
    END IF;
END $$;

-- 2. Policy for Service Role
-- The service_role (backend) always bypasses RLS in standard Supabase configurations,
-- but we can be explicit if needed. By default, no policy is needed for service_role.

-- 3. Policy for Anonymous Users
-- No policy is added for 'anon', which means all access from anonymous users will be DENIED.
