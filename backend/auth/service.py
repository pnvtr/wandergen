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