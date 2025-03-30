from fastapi import APIRouter, HTTPException
from .models import UserCreate, UserLogin, UserResponse
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    try:
        auth_response = await AuthService.sign_up(user.email, user.password)
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