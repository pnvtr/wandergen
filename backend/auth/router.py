from fastapi import APIRouter, HTTPException, Depends
from .models import UserCreate, UserLogin, UserResponse, UserProfileResponse, UserProfileUpdate
from .service import AuthService, UserProfileService
from .dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    try:
        auth_response = await AuthService.sign_up(user.email, user.password)
        # Create user profile after successful signup
        if auth_response.user:
            await UserProfileService.create_profile(auth_response.user.id, user.email)
        # Handle the case where session might not be present
        return UserResponse(
            id=auth_response.user.id if auth_response.user else None,
            email=user.email,
            access_token=auth_response.session.access_token if auth_response.session else None
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin):
    try:
        auth_response = await AuthService.sign_in(user.email, user.password)
        return UserResponse(
            id=auth_response.user.id,
            email=auth_response.user.email,
            access_token=auth_response.session.access_token
        )
    except ValueError as e:
        # Handle email verification error specifically
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(user = Depends(get_current_user)):
    try:
        profile = await UserProfileService.get_profile(user.id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=404, detail="Profile not found")

@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile: UserProfileUpdate,
    user = Depends(get_current_user)
):
    try:
        updated_profile = await UserProfileService.update_profile(user.id, profile.dict())
        return updated_profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 