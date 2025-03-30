from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

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

class RefinementHistoryItem(BaseModel):
    id: int
    itinerary_id: int
    content: str
    refinement_request: str
    created_at: datetime

class RefinementHistoryResponse(BaseModel):
    history: List[RefinementHistoryItem]
