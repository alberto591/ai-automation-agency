-- Migration Phase 10: Advanced WhatsApp & Dashboard Integration
-- Run this in the Supabase SQL Editor

-- 1. Add new columns to 'messages' table
ALTER TABLE public.messages
ADD COLUMN IF NOT EXISTS sid TEXT,
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'sent',
ADD COLUMN IF NOT EXISTS media_url TEXT,
ADD COLUMN IF NOT EXISTS channel TEXT DEFAULT 'whatsapp';

-- 2. Add index on sid for faster status updates
CREATE INDEX IF NOT EXISTS idx_messages_sid ON public.messages(sid);

-- 3. (Optional) Update existing messages to have a default channel
UPDATE public.messages SET channel = 'whatsapp' WHERE channel IS NULL;
UPDATE public.messages SET status = 'sent' WHERE status IS NULL;
