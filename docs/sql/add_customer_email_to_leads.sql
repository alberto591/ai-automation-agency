-- Add customer_email column to leads table
ALTER TABLE leads ADD COLUMN IF NOT EXISTS customer_email TEXT;

-- Index for searching by email
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(customer_email);
