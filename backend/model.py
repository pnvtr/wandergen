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

def generate_itinerary(mood: str, preferences: str = None, user_id: str = None) -> dict:
    """
    Generate a travel itinerary based on the given mood and preferences.
    Saves the itinerary to Supabase database.
    """
    try:
        logger.info(f"Generating itinerary for user {user_id}, mood: {mood}")
        
        prompt = (
            f"Generate a detailed 3-day travel itinerary for a person feeling '{mood}'. "
            f"Consider these preferences: {preferences if preferences else 'none'}.\n\n"
            "The itinerary should include suggestions for destinations, activities, and local cuisine."
        )
        
        response = client.responses.create(
            model = "gpt-4o",
            input = prompt,
            temperature = 0.8,  # Higher temperature for more randomness
            max_tokens = 1000,  # Limit response length
            top_p = 0.9,  # Nucleus sampling for more diverse outputs
            frequency_penalty = 0.5,  # Reduce repetition
            presence_penalty = 0.5,  # Encourage new topics
            stop = None  # No specific stop sequence
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
                "user_id": user_id,
                "original_content": itinerary,
                "is_favorite": False
            }
            result = supabase.table("itineraries").insert(data).execute()
            logger.info("Successfully saved itinerary to database")
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to save itinerary to database: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Failed to generate itinerary: {str(e)}")
        raise

def refine_itinerary(itinerary_id: int, refinement_request: str) -> str:
    """
    Refine an existing itinerary based on the refinement request.
    """
    try:
        # Get the current itinerary
        result = supabase.table("itineraries").select("*").eq("id", itinerary_id).execute()
        if not result.data:
            raise ValueError("Itinerary not found")
        
        current_itinerary = result.data[0]
        logger.info(f"Refining itinerary {itinerary_id}")

        # Create the prompt for refinement
        prompt = (
            f"Here's the current itinerary:\n\n{current_itinerary['content']}\n\n"
            f"Please refine it according to this request: {refinement_request}\n\n"
            "Provide a complete refined version of the itinerary."
        )
        
        # Generate refined version
        response = client.responses.create(
            model = "gpt-4o",
            input = prompt,
            temperature = 0.7,  # Slightly lower temperature for refinements
            max_tokens = 1000,
            top_p = 0.9,
            frequency_penalty = 0.3,
            presence_penalty = 0.3,
            stop = None
        )
        
        refined_itinerary = response.output[0].content[0].text
        logger.info("Successfully generated refined itinerary")

        # Save the refinement to history
        try:
            history_data = {
                "itinerary_id": itinerary_id,
                "content": refined_itinerary,
                "refinement_request": refinement_request
            }
            supabase.table("refinement_history").insert(history_data).execute()
            logger.info("Successfully saved refinement to history")

            # Update the main itinerary
            supabase.table("itineraries")\
                .update({"content": refined_itinerary})\
                .eq("id", itinerary_id)\
                .execute()
            logger.info("Successfully updated main itinerary")
        except Exception as e:
            logger.error(f"Failed to save refinement: {str(e)}")
            raise

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

def toggle_favorite_itinerary(itinerary_id: int, user_id: str, is_favorite: bool) -> dict:
    """
    Toggle favorite status of an itinerary.
    Returns the updated itinerary.
    """
    try:
        # Verify ownership
        result = supabase.table("itineraries")\
            .select("*")\
            .eq("id", itinerary_id)\
            .eq("user_id", user_id)\
            .execute()
            
        if not result.data:
            raise ValueError("Itinerary not found")
            
        # Update favorite status
        updated = supabase.table("itineraries")\
            .update({"is_favorite": is_favorite})\
            .eq("id", itinerary_id)\
            .execute()
            
        return updated.data[0]
    except Exception as e:
        logger.error(f"Failed to toggle favorite status: {str(e)}")
        raise

async def get_favorite_itineraries(user_id: str) -> list:
    """
    Get all favorite itineraries for a user.
    """
    try:
        result = supabase.table("itineraries")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("is_favorite", True)\
            .execute()
        return result.data
    except Exception as e:
        logger.error(f"Failed to get favorite itineraries: {str(e)}")
        raise

def get_user_itineraries(user_id: str) -> list:
    """
    Get all itineraries for a specific user.
    """
    try:
        result = supabase.table("itineraries")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        return result.data
    except Exception as e:
        logger.error(f"Failed to get user itineraries: {str(e)}")
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