-- 1. Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Add embedding columns
ALTER TABLE properties DROP COLUMN IF EXISTS embedding;
ALTER TABLE properties ADD COLUMN embedding vector(1024);

ALTER TABLE mock_properties DROP COLUMN IF EXISTS embedding;
ALTER TABLE mock_properties ADD COLUMN embedding vector(1024);

-- 3. Search Function for Properties
DROP FUNCTION IF EXISTS match_properties(vector, double precision, integer, integer, integer);

CREATE OR REPLACE FUNCTION match_properties (
  p_query_embedding vector(1024),
  match_threshold float,
  match_count int,
  min_price int DEFAULT 0,
  max_price int DEFAULT 2147483647
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  description TEXT,
  price NUMERIC,
  sqm INT,
  rooms INT,
  bathrooms INT,
  floor INT,
  energy_class TEXT,
  has_elevator BOOLEAN,
  status TEXT,
  image_url TEXT,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    p.id,
    p.title,
    p.description,
    p.price,
    p.sqm,
    p.rooms,
    p.bathrooms,
    p.floor,
    p.energy_class,
    p.has_elevator,
    p.status,
    p.image_url,
    (1 - (p.embedding <=> p_query_embedding))::float AS similarity
  FROM properties p
  WHERE p.price >= min_price
    AND p.price <= max_price
    AND (1 - (p.embedding <=> p_query_embedding)) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;

-- 4. Search Function for Mock Properties
CREATE OR REPLACE FUNCTION match_mock_properties (
  p_query_embedding vector(1024),
  match_threshold float,
  match_count int,
  min_price int DEFAULT 0,
  max_price int DEFAULT 2147483647
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  description TEXT,
  price NUMERIC,
  sqm INT,
  rooms INT,
  bathrooms INT,
  floor INT,
  energy_class TEXT,
  has_elevator BOOLEAN,
  status TEXT,
  image_url TEXT,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    p.id,
    p.title,
    p.description,
    p.price,
    p.sqm,
    p.rooms,
    p.bathrooms,
    p.floor,
    p.energy_class,
    p.has_elevator,
    p.status,
    p.image_url,
    (1 - (p.embedding <=> p_query_embedding))::float AS similarity
  FROM mock_properties p
  WHERE p.price >= min_price
    AND p.price <= max_price
    AND (1 - (p.embedding <=> p_query_embedding)) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
