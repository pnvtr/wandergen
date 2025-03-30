from openai import OpenAI
import os
from dotenv import load_dotenv
from database import supabase
from logger import setup_logger

# Setup logger
logger = setup_logger("model")

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    error_msg = "OPENAI_API_KEY not found in environment variables"
    logger.error(error_msg)
    raise ValueError(error_msg)

try:
    client = OpenAI(api_key=api_key)
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    raise

def generate_itinerary(mood: str, preferences: str = None) -> str:
    """
    Generate a travel itinerary based on the given mood and preferences.
    Saves the itinerary to Supabase database.
    """
    try:
        logger.info(f"Generating itinerary for mood: {mood}, preferences: {preferences}")
        
        prompt = (
            f"Generate a detailed 3-day travel itinerary for a person feeling '{mood}'. "
            f"Consider these preferences: {preferences if preferences else 'none'}.\n\n"
            "The itinerary should include suggestions for destinations, activities, and local cuisine."
        )
        
        response = client.responses.create(
            model = "gpt-4o",
            input = prompt
        )
        
        # Extract the content from the response structure
        itinerary = response.output[0].content[0].text
        logger.info("Successfully generated itinerary")

        # Save to Supabase
        try:
            data = {
                "mood": mood,
                "preferences": preferences,
                "content": itinerary
            }
            supabase.table("itineraries").insert(data).execute()
            logger.info("Successfully saved itinerary to database")
        except Exception as e:
            logger.error(f"Failed to save itinerary to database: {str(e)}")
            # Continue execution even if database save fails

        return itinerary
    except Exception as e:
        logger.error(f"Failed to generate itinerary: {str(e)}")
        raise

# Example usage
if __name__ == "__main__":
    try:
        result = generate_itinerary("happy", "sports and adventurous")
        print(result)
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")