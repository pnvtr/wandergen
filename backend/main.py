from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model import generate_itinerary

app = FastAPI()

# Define a request model for mood input
class MoodInput(BaseModel):
    mood: str
    preferences: str = None  # Optional for additional details

@app.post("/generate-trip")
async def generate_trip(input: MoodInput):
    """
    Endpoint to generate a trip itinerary based on the user's mood and preferences.
    """
    try:
        itinerary = generate_itinerary(input.mood, input.preferences)
        return {"itinerary": itinerary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "Welcome to WanderGen API!"}
