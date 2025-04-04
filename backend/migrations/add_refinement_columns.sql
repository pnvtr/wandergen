-- Function to check if a column exists
CREATE OR REPLACE FUNCTION column_exists(p_table_name text, p_column_name text)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE columns.table_name = p_table_name 
        AND columns.column_name = p_column_name
    );
END;
$$ LANGUAGE plpgsql;

-- Add refinement-related columns to itineraries table if they don't exist
DO $$ 
BEGIN
    IF NOT column_exists('itineraries', 'refined') THEN
        ALTER TABLE itineraries ADD COLUMN refined BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT column_exists('itineraries', 'refinement_request') THEN
        ALTER TABLE itineraries ADD COLUMN refinement_request TEXT;
    END IF;
    
    IF NOT column_exists('itineraries', 'original_content') THEN
        ALTER TABLE itineraries ADD COLUMN original_content TEXT;
    END IF;
    
    IF NOT column_exists('itineraries', 'refinement_count') THEN
        ALTER TABLE itineraries ADD COLUMN refinement_count INTEGER DEFAULT 0;
    END IF;
END $$;

-- Drop the refinement_history table if it exists to recreate it with proper constraints
DROP TABLE IF EXISTS refinement_history;

-- Create refinement history table with proper constraints
CREATE TABLE refinement_history (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    itinerary_id BIGINT REFERENCES itineraries(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    refinement_request TEXT NOT NULL DEFAULT 'Initial version',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create indexes if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'itineraries_refined_idx'
    ) THEN
        CREATE INDEX itineraries_refined_idx ON itineraries(refined);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'refinement_history_itinerary_id_idx'
    ) THEN
        CREATE INDEX refinement_history_itinerary_id_idx ON refinement_history(itinerary_id);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'refinement_history_created_at_idx'
    ) THEN
        CREATE INDEX refinement_history_created_at_idx ON refinement_history(created_at);
    END IF;
END $$; 