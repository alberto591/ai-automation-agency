-- ADR-019: Semantic Answer Cache
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS semantic_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT UNIQUE,
    query_embedding vector(1024),
    response_text TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Function to match cached answers
DROP FUNCTION IF EXISTS match_cache(vector, double precision, integer);

CREATE OR REPLACE FUNCTION match_cache (
  p_query_embedding vector(1024),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  query_text TEXT,
  response_text TEXT,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    c.query_text,
    c.response_text,
    (1 - (c.query_embedding <=> p_query_embedding))::float AS similarity
  FROM semantic_cache c
  WHERE (1 - (c.query_embedding <=> p_query_embedding)) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
