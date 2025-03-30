from supabase import create_client
import os
from dotenv import load_dotenv
from logger import setup_logger

# Setup logger
logger = setup_logger("database")

# Load environment variables
load_dotenv()

# Get the Supabase URL and key from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    error_msg = "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
    logger.error(error_msg)
    raise ValueError(error_msg)

try:
    # Create Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    raise

def test_connection():
    try:
        # Try to fetch a single row from itineraries table
        result = supabase.table("itineraries").select("*").limit(1).execute()
        logger.info("Successfully connected to Supabase!")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 