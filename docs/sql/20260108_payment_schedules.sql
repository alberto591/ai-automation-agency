-- Migration: Create payment_schedules table
-- Date: 2026-01-08
-- Purpose: Support automated payment reminders (Waliner feature parity)

CREATE TABLE IF NOT EXISTS payment_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    description TEXT,
    due_date DATE NOT NULL,
    recurrence VARCHAR(20) CHECK (recurrence IN ('monthly', 'one_time', 'weekly', 'yearly')),
    reminder_days INT[] DEFAULT '{7, 3, 0}', -- Days before due date to send reminder
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'calcelled')),
    stripe_link TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for finding due payments efficiently
CREATE INDEX idx_payment_schedules_due_date ON payment_schedules(due_date);
CREATE INDEX idx_payment_schedules_status ON payment_schedules(status);
