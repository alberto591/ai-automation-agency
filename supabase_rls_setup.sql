-- Enable RLS on core tables
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE schedule ENABLE ROW LEVEL SECURITY; -- If exists

-- Policy for LEADS: Authenticated users can do everything
DROP POLICY IF EXISTS "Enable access for authenticated users only" ON leads;
CREATE POLICY "Enable access for authenticated users only" ON leads
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Policy for MESSAGES: Authenticated users can do everything
DROP POLICY IF EXISTS "Enable access for authenticated users only" ON messages;
CREATE POLICY "Enable access for authenticated users only" ON messages
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Optional: Allow Anon Insert (e.g., from Webhooks)?
-- Ideally, webhooks should use a Service Role Key which bypasses RLS,
-- but if we use Anon key for public forms, we need this:
-- CREATE POLICY "Allow public inserts" ON leads FOR INSERT TO anon WITH CHECK (true);
