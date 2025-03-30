from typing import Optional
from database import supabase
from logger import setup_logger

logger = setup_logger("auth")

class AuthService:
    @staticmethod
    async def sign_up(email: str, password: str) -> dict:
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            logger.info(f"User signed up successfully: {email}")
            if response.user and not response.user.email_confirmed_at:
                logger.info(f"Verification email sent to: {email}")
            return response
        except Exception as e:
            logger.error(f"Failed to sign up user: {str(e)}")
            raise

    @staticmethod
    async def sign_in(email: str, password: str) -> dict:
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            logger.info(f"User signed in successfully: {email}")
            return response
        except Exception as e:
            if "Email not confirmed" in str(e):
                logger.error(f"Login attempted with unconfirmed email: {email}")
                raise ValueError("Please verify your email before logging in. Check your inbox for the verification link.")
            logger.error(f"Failed to sign in user: {str(e)}")
            raise

class UserProfileService:
    @staticmethod
    async def get_profile(user_id: str) -> dict:
        try:
            result = supabase.table("user_profiles").select("*").eq("id", user_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            raise

    @staticmethod
    async def update_profile(user_id: str, profile_data: dict) -> dict:
        try:
            result = supabase.table("user_profiles").update(profile_data).eq("id", user_id).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to update user profile: {str(e)}")
            raise

    @staticmethod
    async def create_profile(user_id: str, email: str) -> dict:
        try:
            profile_data = {
                "id": user_id,
                "email": email
            }
            result = supabase.table("user_profiles").insert(profile_data).execute()
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to create user profile: {str(e)}")
            raise 