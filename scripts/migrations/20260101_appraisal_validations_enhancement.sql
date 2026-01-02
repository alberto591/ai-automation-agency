-- Migration: Update Appraisal Validations Schema
-- Date: 2026-01-01
-- Description: Adds missing columns to appraisal_validations table for enhanced monitoring

-- Add missing columns to appraisal_validations table
ALTER TABLE appraisal_validations
ADD COLUMN IF NOT EXISTS zone TEXT,
ADD COLUMN IF NOT EXISTS city TEXT,
ADD COLUMN IF NOT EXISTS fifi_status TEXT DEFAULT 'AUTO_APPROVED',
ADD COLUMN IF NOT EXISTS alert_triggered BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS actual_listing_price_eur INTEGER,
ADD COLUMN IF NOT EXISTS actual_sale_price_eur INTEGER;

-- Add index for zone-based queries (used in drift detection)
CREATE INDEX IF NOT EXISTS idx_appraisal_validations_zone_date
ON appraisal_validations(zone, appraisal_date DESC);

-- Add index for alert monitoring
CREATE INDEX IF NOT EXISTS idx_appraisal_validations_alerts
ON appraisal_validations(alert_triggered, appraisal_date DESC)
WHERE alert_triggered = TRUE;

-- Comment updates
COMMENT ON COLUMN appraisal_validations.zone IS 'Property zone/neighborhood for geographic analysis';
COMMENT ON COLUMN appraisal_validations.city IS 'City where property is located';
COMMENT ON COLUMN appraisal_validations.fifi_status IS 'Auto-approval status: AUTO_APPROVED or HUMAN_REVIEW_REQUIRED';
COMMENT ON COLUMN appraisal_validations.alert_triggered IS 'TRUE if prediction error exceeds 20% threshold';
COMMENT ON COLUMN appraisal_validations.actual_listing_price_eur IS 'Actual listing price when validating against market listings';
COMMENT ON COLUMN appraisal_validations.actual_sale_price_eur IS 'Actual sale price when validating against completed transactions';
