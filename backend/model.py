from openai import OpenAI
import os
from dotenv import load_dotenv
from database import supabase
from logger import setup_logger
from typing import List, Dict, Any

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
                "content": itinerary,
                "original_content": itinerary  # Store original content
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
            logger.info(f"Original itinerary data: {original_itinerary}")
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
            # Store current content in history before updating
            # Always use 'Initial version' if no refinement request exists
            history_refinement_request = original_itinerary.get('refinement_request') or 'Initial version'
            logger.info(f"Using refinement request for history: {history_refinement_request}")
            
            history_data = {
                "itinerary_id": itinerary_id,
                "content": original_itinerary['content'],
                "refinement_request": history_refinement_request
            }
            logger.info(f"History data to be inserted: {history_data}")
            
            supabase.table("refinement_history").insert(history_data).execute()
            logger.info("Successfully inserted history record")

            # Update the itinerary
            update_data = {
                "content": refined_itinerary,
                "refined": True,
                "refinement_request": refinement_request,
                "refinement_count": original_itinerary.get('refinement_count', 0) + 1
            }
            logger.info(f"Update data for itinerary: {update_data}")
            
            supabase.table("itineraries").update(update_data).eq("id", itinerary_id).execute()
            logger.info("Successfully updated refined itinerary in database")
        except Exception as e:
            logger.error(f"Failed to update refined itinerary in database: {str(e)}")
            # Continue execution even if database update fails

        return refined_itinerary
    except Exception as e:
        logger.error(f"Failed to refine itinerary: {str(e)}")
        raise

def revert_to_original(itinerary_id: int) -> str:
    """
    Revert an itinerary back to its original version.
    """
    try:
        logger.info(f"Reverting itinerary with ID: {itinerary_id} to original version")
        
        # Fetch the original itinerary from Supabase
        try:
            result = supabase.table("itineraries").select("*").eq("id", itinerary_id).execute()
            if not result.data:
                raise ValueError(f"Itinerary with ID {itinerary_id} not found")
            itinerary = result.data[0]
            
            if not itinerary.get('original_content'):
                raise ValueError("No original content found for this itinerary")
        except Exception as e:
            logger.error(f"Failed to fetch itinerary from database: {str(e)}")
            raise

        # Update the itinerary to revert to original content
        try:
            update_data = {
                "content": itinerary['original_content'],
                "refined": False,
                "refinement_request": None,
                "refinement_count": 0
            }
            
            supabase.table("itineraries").update(update_data).eq("id", itinerary_id).execute()
            logger.info("Successfully reverted itinerary to original version")
        except Exception as e:
            logger.error(f"Failed to revert itinerary in database: {str(e)}")
            raise

        return itinerary['original_content']
    except Exception as e:
        logger.error(f"Failed to revert itinerary: {str(e)}")
        raise

def get_refinement_history(itinerary_id: int) -> List[Dict[str, Any]]:
    """
    Get the refinement history for an itinerary.
    """
    try:
        logger.info(f"Fetching refinement history for itinerary ID: {itinerary_id}")
        
        result = supabase.table("refinement_history")\
            .select("*")\
            .eq("itinerary_id", itinerary_id)\
            .order("created_at", desc=True)\
            .execute()
            
        return result.data
    except Exception as e:
        logger.error(f"Failed to fetch refinement history: {str(e)}")
        raise

# Example usage
if __name__ == "__main__":
    try:
        # Generate a new itinerary
        result = generate_itinerary("want to do something fun", "entertaining, yummy food")
        print("Generated Itinerary:", result)
        
        # Example of refining an itinerary (assuming ID 1 exists)
        refined = refine_itinerary(1, "Add more budget-friendly options")
        print("\nRefined Itinerary:", refined)
        
        # Example of getting refinement history
        history = get_refinement_history(1)
        print("\nRefinement History:", history)
        
        # Example of reverting to original
        original = revert_to_original(1)
        print("\nReverted to Original:", original)
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")