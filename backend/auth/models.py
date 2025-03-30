from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: Optional[str]
    email: EmailStr
    access_token: Optional[str] = None

class UserProfile(BaseModel):
    preferred_mood: Optional[str] = None
    travel_preferences: Optional[str] = None

class UserProfileResponse(UserProfile):
    email: EmailStr
    created_at: datetime
    updated_at: datetime

class UserProfileUpdate(BaseModel):
    preferred_mood: Optional[str] = None
    travel_preferences: Optional[str] = None 