from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import supabase
from logger import setup_logger
from .models import UserResponse

logger = setup_logger("auth")
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get the current authenticated user."""
    try:
        # Verify the JWT token with Supabase
        auth_response = supabase.auth.get_user(credentials.credentials)
        if not auth_response or not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user data",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserResponse(
            id=auth_response.user.id,
            email=auth_response.user.email,
            access_token=credentials.credentials
        )
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 