from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the Supabase URL and key from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) 

def test_connection():
    try:
        # Try to fetch a single row from itineraries table
        result = supabase.table("itineraries").select("*").limit(1).execute()
        print("Successfully connected to Supabase!")
        return True
    except Exception as e:
        print(f"Failed to connect to Supabase: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 