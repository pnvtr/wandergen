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

def refine_itinerary(itinerary_id: int, refinement_request: str) -> str:
    """
    Refine an existing itinerary based on user feedback or specific requests.
    """
    try:
        logger.info(f"Refining itinerary with ID: {itinerary_id}")
        
        # Fetch the original itinerary from Supabase
        try:
            result = supabase.table("itineraries").select("*").eq("id", itinerary_id).execute()
            if not result.data:
                raise ValueError(f"Itinerary with ID {itinerary_id} not found")
            original_itinerary = result.data[0]
        except Exception as e:
            logger.error(f"Failed to fetch itinerary from database: {str(e)}")
            raise

        # Create refinement prompt
        prompt = (
            f"Here is the original itinerary:\n\n{original_itinerary['content']}\n\n"
            f"Please refine this itinerary according to the following request: {refinement_request}\n\n"
            "Provide a complete refined version of the itinerary."
        )
        
        # Get refined version from GPT
        response = client.responses.create(
            model = "gpt-4o",
            input = prompt
        )
        
        refined_itinerary = response.output[0].content[0].text
        logger.info("Successfully generated refined itinerary")

        # Update the itinerary in Supabase
        try:
            update_data = {
                "content": refined_itinerary,
                "refined": True,
                "refinement_request": refinement_request
            }
            
            # Only store original content if this is the first refinement
            if not original_itinerary.get('original_content'):
                update_data["original_content"] = original_itinerary['content']
            
            supabase.table("itineraries").update(update_data).eq("id", itinerary_id).execute()
            logger.info("Successfully updated refined itinerary in database")
        except Exception as e:
            logger.error(f"Failed to update refined itinerary in database: {str(e)}")
            # Continue execution even if database update fails

        return refined_itinerary
    except Exception as e:
        logger.error(f"Failed to refine itinerary: {str(e)}")
        raise

# Example usage
if __name__ == "__main__":
    try:
        # Generate a new itinerary
        result = generate_itinerary("happy", "sports and adventurous")
        print("Generated Itinerary:", result)
        
        # Example of refining an itinerary (assuming ID 1 exists)
        refined = refine_itinerary(1, "Add more budget-friendly options")
        print("\nRefined Itinerary:", refined)
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")