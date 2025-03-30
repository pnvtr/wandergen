-- Add refinement-related columns to itineraries table
ALTER TABLE itineraries
ADD COLUMN refined BOOLEAN DEFAULT FALSE,
ADD COLUMN refinement_request TEXT,
ADD COLUMN original_content TEXT,
ADD COLUMN refinement_count INTEGER DEFAULT 0;

-- Create a table for refinement history
CREATE TABLE refinement_history (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    itinerary_id BIGINT REFERENCES itineraries(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    refinement_request TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create indexes for faster queries
CREATE INDEX itineraries_refined_idx ON itineraries(refined);
CREATE INDEX refinement_history_itinerary_id_idx ON refinement_history(itinerary_id);
CREATE INDEX refinement_history_created_at_idx ON refinement_history(created_at); 