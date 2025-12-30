-- Fix migration: Drop and Recreate to ensure correct schema
DROP TABLE IF EXISTS appraisal_validations CASCADE;

CREATE TABLE appraisal_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appraisal_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    lead_id UUID REFERENCES leads(id), -- Optional linkage
    model_version TEXT NOT NULL,
    predicted_value_eur INTEGER NOT NULL,
    confidence_low_eur INTEGER,
    confidence_high_eur INTEGER,
    uncertainty_score DECIMAL(5,4),

    -- Validation Data
    actual_listing_price_eur INTEGER, -- Known at time of scrape
    actual_sale_price_eur INTEGER,    -- Known later
    error_pct DECIMAL(5,2),           -- (Predicted - Actual) / Actual

    -- Metadata
    zone TEXT NOT NULL,
    city TEXT NOT NULL,
    fifi_status TEXT, -- 'AUTO_APPROVED', 'HUMAN_REVIEW'
    alert_triggered BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_validation_zone ON appraisal_validations(zone);
CREATE INDEX idx_validation_date ON appraisal_validations(appraisal_date DESC);
