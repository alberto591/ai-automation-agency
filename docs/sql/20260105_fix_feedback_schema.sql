-- Fix appraisal_feedback schema for Demo Scenario 4
-- Previous error indicated missing 'overall_rating' and 'appraisal_id' columns

-- 1. Create table if it doesn't exist (base structure)
CREATE TABLE IF NOT EXISTS public.appraisal_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Add missing columns safely
DO $$
BEGIN
    -- overall_rating
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'appraisal_feedback' AND column_name = 'overall_rating') THEN
        ALTER TABLE public.appraisal_feedback ADD COLUMN overall_rating INTEGER;
    END IF;

    -- speed_rating
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'appraisal_feedback' AND column_name = 'speed_rating') THEN
        ALTER TABLE public.appraisal_feedback ADD COLUMN speed_rating INTEGER;
    END IF;

    -- accuracy_rating
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'appraisal_feedback' AND column_name = 'accuracy_rating') THEN
        ALTER TABLE public.appraisal_feedback ADD COLUMN accuracy_rating INTEGER;
    END IF;

    -- feedback_text
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'appraisal_feedback' AND column_name = 'feedback_text') THEN
        ALTER TABLE public.appraisal_feedback ADD COLUMN feedback_text TEXT;
    END IF;

    -- appraisal_id (nullable for backward compatibility/direct feedback)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'appraisal_feedback' AND column_name = 'appraisal_id') THEN
        ALTER TABLE public.appraisal_feedback ADD COLUMN appraisal_id TEXT;
    END IF;

    -- appraisal_phone
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'appraisal_feedback' AND column_name = 'appraisal_phone') THEN
        ALTER TABLE public.appraisal_feedback ADD COLUMN appraisal_phone TEXT;
    END IF;

    -- appraisal_email
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'appraisal_feedback' AND column_name = 'appraisal_email') THEN
        ALTER TABLE public.appraisal_feedback ADD COLUMN appraisal_email TEXT;
    END IF;
END $$;

-- 3. Enable RLS (just in case) and allow public inserts for demo
ALTER TABLE public.appraisal_feedback ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'appraisal_feedback' AND policyname = 'Allow public inserts'
    ) THEN
        CREATE POLICY "Allow public inserts" ON public.appraisal_feedback
            FOR INSERT 
            WITH CHECK (true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'appraisal_feedback' AND policyname = 'Allow public read'
    ) THEN
        CREATE POLICY "Allow public read" ON public.appraisal_feedback
            FOR SELECT 
            USING (true);
    END IF;
END $$;
