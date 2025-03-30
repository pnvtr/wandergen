from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=api_key)

def generate_itinerary(mood: str, preferences: str = None) -> str:
    """
    Generate a travel itinerary based on the given mood and preferences.
    """
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
    return itinerary

# print(generate_itinerary("happy", "sports and adventurous"))