-- Migration: Fifi AVM Foundation
-- Date: 2025-12-30
-- Description: Creates tables for historical transactions and property features to support ML model training.

-- 0. Required Extensions for Geospatial Search
CREATE EXTENSION IF NOT EXISTS cube;
CREATE EXTENSION IF NOT EXISTS earthdistance;

-- 1. Historical Transactions Table (Ground Truth)
CREATE TABLE IF NOT EXISTS historical_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    zone TEXT NOT NULL,
    postcode TEXT,
    lat DECIMAL(10,8),
    lon DECIMAL(11,8),
    sale_price_eur INTEGER NOT NULL,
    price_per_sqm_eur INTEGER,
    sqm INTEGER,
    bedrooms INTEGER,
    bathrooms INTEGER,
    floor INTEGER,
    has_elevator BOOLEAN,
    has_balcony BOOLEAN,
    condition TEXT, -- 'excellent', 'good', 'fair', 'poor', 'luxury'
    property_age_years INTEGER,
    cadastral_category TEXT, -- 'A/2', 'A/3', etc.
    sale_date DATE NOT NULL,
    source TEXT, -- 'OMI', 'Notary', 'Scrape'
    metadata JSONB, -- Additional data (e.g., energy class)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_transactions_zone_date ON historical_transactions(zone, sale_date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_location ON historical_transactions USING GIST (ll_to_earth(lat::double precision, lon::double precision));

-- 2. Property Features Table (Enriched Data)
CREATE TABLE IF NOT EXISTS property_features_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_slug TEXT UNIQUE NOT NULL, -- e.g. 'milano-brera'
    avg_price_index DECIMAL(5,2), -- Relative to city average
    distance_to_metro_avg_m INTEGER,
    walkability_score_avg INTEGER,
    crime_rate_index DECIMAL(5,2),
    tourism_impact_score INTEGER,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Appraisal Validations Table (Performance Monitoring)
CREATE TABLE IF NOT EXISTS appraisal_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appraisal_date TIMESTAMPTZ DEFAULT NOW(),
    lead_id UUID REFERENCES leads(id),
    model_version TEXT NOT NULL,
    predicted_value_eur INTEGER NOT NULL,
    confidence_low_eur INTEGER,
    confidence_high_eur INTEGER,
    uncertainty_score DECIMAL(5,4),
    actual_sale_value_eur INTEGER, -- To be filled upon sale
    error_pct DECIMAL(5,2),
    metadata JSONB
);

COMMENT ON TABLE historical_transactions IS 'Ground truth data from Notarial Deeds and OMI for ML training.';
COMMENT ON TABLE property_features_stats IS 'Aggregated geospatial and socio-economic features per zone.';
