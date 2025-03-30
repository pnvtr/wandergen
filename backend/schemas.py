from pydantic import BaseModel

class MoodInput(BaseModel):
    mood: str
    preferences: str = None  # Optional for additional details
