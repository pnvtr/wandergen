-- First, clear the refinement history table due to foreign key constraint
DELETE FROM refinement_history;

-- Then clear the itineraries table
DELETE FROM itineraries;

-- Reset the sequence if it exists
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_sequences 
        WHERE sequencename = 'itineraries_id_seq'
    ) THEN
        ALTER SEQUENCE itineraries_id_seq RESTART WITH 1;
    END IF;
END $$; 