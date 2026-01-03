-- Phase 3 Database Optimization: Indexes for Properties Table
-- Purpose: Speed up local property search queries from ~0.7s to <0.3s
-- Expected Impact: 60% faster database queries

-- ============================================================================
-- PROPERTIES TABLE INDEXES
-- ============================================================================

-- 1. Full-Text Search Index on Description
-- Enables faster zone/city matching with Italian language support
CREATE INDEX IF NOT EXISTS idx_properties_description_fts 
ON properties 
USING gin(to_tsvector('italian', description));

COMMENT ON INDEX idx_properties_description_fts IS 
'Full-text search index for zone/city matching in Italian';

-- 2. Price Index
-- Speeds up price range filtering (>10000, etc.)
CREATE INDEX IF NOT EXISTS idx_properties_price 
ON properties(price) 
WHERE price IS NOT NULL AND price > 0;

COMMENT ON INDEX idx_properties_price IS 
'Speeds up price range queries for valid properties';

-- 3. Square Meters Index
-- Speeds up size range filtering (±30% target size)
CREATE INDEX IF NOT EXISTS idx_properties_sqm 
ON properties(sqm) 
WHERE sqm IS NOT NULL AND sqm > 0;

COMMENT ON INDEX idx_properties_sqm IS 
'Speeds up size range queries for valid properties';

-- 4. Composite Index: Price + SQM
-- Optimizes the most common filter combination
CREATE INDEX IF NOT EXISTS idx_properties_price_sqm 
ON properties(price, sqm) 
WHERE price IS NOT NULL AND sqm IS NOT NULL AND price > 0 AND sqm > 0;

COMMENT ON INDEX idx_properties_price_sqm IS 
'Composite index for price/sqm validation queries';

-- 5. Image URL Index (for deduplication)
-- Already exists in production, but ensuring it's optimal
CREATE UNIQUE INDEX IF NOT EXISTS idx_properties_image_url 
ON properties(image_url);

COMMENT ON INDEX idx_properties_image_url IS 
'Unique constraint for deduplication by image URL';

-- ============================================================================
-- PERFORMANCE MONITORING TABLE
-- ============================================================================

-- Create table to track appraisal performance metrics
CREATE TABLE IF NOT EXISTS appraisal_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Request context
    city TEXT NOT NULL,
    zone TEXT NOT NULL,
    property_type TEXT,
    surface_sqm INTEGER,
    
    -- Performance metrics
    response_time_ms INTEGER NOT NULL,
    used_local_search BOOLEAN NOT NULL,
    used_perplexity_fallback BOOLEAN DEFAULT FALSE,
    comparables_found INTEGER NOT NULL,
    confidence_level INTEGER NOT NULL,
    reliability_stars INTEGER NOT NULL,
    
    -- Result data
    estimated_value NUMERIC,
    
    -- User context
    user_phone TEXT,
    user_email TEXT,
    
    -- Metadata
    api_version TEXT DEFAULT '1.0',
    optimization_phase TEXT DEFAULT 'phase_2'
);

COMMENT ON TABLE appraisal_performance_metrics IS 
'Tracks appraisal API performance for monitoring and optimization';

-- Index for time-series queries
CREATE INDEX IF NOT EXISTS idx_performance_metrics_created_at 
ON appraisal_performance_metrics(created_at DESC);

-- Index for geographic analysis
CREATE INDEX IF NOT EXISTS idx_performance_metrics_location 
ON appraisal_performance_metrics(city, zone);

-- Index for performance analysis
CREATE INDEX IF NOT EXISTS idx_performance_metrics_response_time 
ON appraisal_performance_metrics(response_time_ms);

-- ============================================================================
-- USER FEEDBACK TABLE
-- ============================================================================

-- Create table for user feedback on appraisals
CREATE TABLE IF NOT EXISTS appraisal_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Link to appraisal
    appraisal_phone TEXT,
    appraisal_email TEXT,
    estimated_value NUMERIC,
    
    -- Feedback data
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    speed_rating INTEGER CHECK (speed_rating BETWEEN 1 AND 5),
    accuracy_rating INTEGER CHECK (accuracy_rating BETWEEN 1 AND 5),
    
    -- User comments
    feedback_text TEXT,
    
    -- Metadata
    source TEXT DEFAULT 'web_form',
    responded_at TIMESTAMPTZ
);

COMMENT ON TABLE appraisal_feedback IS 
'Collects user feedback on appraisal quality and performance';

-- Index for feedback analysis
CREATE INDEX IF NOT EXISTS idx_feedback_created_at 
ON appraisal_feedback(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_feedback_rating 
ON appraisal_feedback(rating) 
WHERE rating IS NOT NULL;

-- ============================================================================
-- MATERIALIZED VIEWS FOR ANALYTICS
-- ============================================================================

-- Daily performance summary
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_performance_summary AS
SELECT 
    DATE(created_at) as date,
    city,
    zone,
    COUNT(*) as total_appraisals,
    AVG(response_time_ms) as avg_response_ms,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_ms) as p50_response_ms,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY response_time_ms) as p90_response_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms) as p99_response_ms,
    SUM(CASE WHEN used_local_search THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as local_hit_rate,
    AVG(confidence_level) as avg_confidence,
    AVG(comparables_found) as avg_comparables
FROM appraisal_performance_metrics
GROUP BY DATE(created_at), city, zone;

COMMENT ON MATERIALIZED VIEW mv_daily_performance_summary IS 
'Daily aggregated performance metrics for dashboard';

-- Create refresh function
CREATE OR REPLACE FUNCTION refresh_performance_views()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_performance_summary;
END;
$$;

COMMENT ON FUNCTION refresh_performance_views IS 
'Refreshes materialized views for performance dashboard';

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

-- Enable RLS on new tables
ALTER TABLE appraisal_performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE appraisal_feedback ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY service_role_all_performance_metrics 
ON appraisal_performance_metrics 
FOR ALL 
TO service_role
USING (true)
WITH CHECK (true);

CREATE POLICY service_role_all_feedback 
ON appraisal_feedback 
FOR ALL 
TO service_role
USING (true)
WITH CHECK (true);

-- Allow public read access to aggregated metrics only (via RPC)
CREATE POLICY public_read_performance_stats 
ON appraisal_performance_metrics 
FOR SELECT 
TO anon, authenticated
USING (false);  -- No direct access, only via RPC functions

CREATE POLICY public_read_feedback_stats 
ON appraisal_feedback 
FOR SELECT 
TO anon, authenticated
USING (false);  -- No direct access, only via RPC functions

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to log appraisal performance
CREATE OR REPLACE FUNCTION log_appraisal_performance(
    p_city TEXT,
    p_zone TEXT,
    p_property_type TEXT,
    p_surface_sqm INTEGER,
    p_response_time_ms INTEGER,
    p_used_local_search BOOLEAN,
    p_used_perplexity BOOLEAN,
    p_comparables_found INTEGER,
    p_confidence_level INTEGER,
    p_reliability_stars INTEGER,
    p_estimated_value NUMERIC,
    p_user_phone TEXT DEFAULT NULL,
    p_user_email TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_metric_id UUID;
BEGIN
    INSERT INTO appraisal_performance_metrics (
        city, zone, property_type, surface_sqm,
        response_time_ms, used_local_search, used_perplexity_fallback,
        comparables_found, confidence_level, reliability_stars,
        estimated_value, user_phone, user_email
    ) VALUES (
        p_city, p_zone, p_property_type, p_surface_sqm,
        p_response_time_ms, p_used_local_search, p_used_perplexity,
        p_comparables_found, p_confidence_level, p_reliability_stars,
        p_estimated_value, p_user_phone, p_user_email
    )
    RETURNING id INTO v_metric_id;
    
    RETURN v_metric_id;
END;
$$;

COMMENT ON FUNCTION log_appraisal_performance IS 
'Logs performance metrics for each appraisal request';

-- Function to get performance stats
CREATE OR REPLACE FUNCTION get_performance_stats(
    p_hours INTEGER DEFAULT 24
)
RETURNS TABLE (
    total_appraisals BIGINT,
    avg_response_ms NUMERIC,
    p50_response_ms NUMERIC,
    p90_response_ms NUMERIC,
    local_hit_rate NUMERIC,
    avg_confidence NUMERIC,
    avg_comparables NUMERIC
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_appraisals,
        ROUND(AVG(response_time_ms), 2) as avg_response_ms,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_ms) as p50_response_ms,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY response_time_ms) as p90_response_ms,
        ROUND(
            SUM(CASE WHEN used_local_search THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100,
            2
        ) as local_hit_rate,
        ROUND(AVG(confidence_level), 2) as avg_confidence,
        ROUND(AVG(comparables_found), 2) as avg_comparables
    FROM appraisal_performance_metrics
    WHERE created_at >= NOW() - (p_hours || ' hours')::INTERVAL;
END;
$$;

COMMENT ON FUNCTION get_performance_stats IS 
'Returns aggregated performance statistics for the last N hours';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check index creation
-- SELECT 
--     tablename, 
--     indexname, 
--     indexdef 
-- FROM pg_indexes 
-- WHERE tablename IN ('properties', 'appraisal_performance_metrics', 'appraisal_feedback')
-- ORDER BY tablename, indexname;

-- Test performance improvement
-- EXPLAIN ANALYZE
-- SELECT * FROM properties
-- WHERE to_tsvector('italian', description) @@ to_tsquery('italian', 'Milano & Centro')
--   AND sqm BETWEEN 66 AND 123
--   AND price > 10000
-- LIMIT 10;
