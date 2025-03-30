from pydantic import BaseModel
from typing import Optional

class MoodInput(BaseModel):
    mood: str
    preferences: str = None  # Optional for additional details

class ItineraryRequest(BaseModel):
    mood: str
    preferences: Optional[str] = None

class RefinementRequest(BaseModel):
    itinerary_id: int
    refinement_request: str

class ItineraryResponse(BaseModel):
    itinerary: str

class RefinedItineraryResponse(BaseModel):
    refined_itinerary: str

class HealthResponse(BaseModel):
    status: str
