from supabase import Client
from fastapi import HTTPException, status
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Handle authentication operations with Supabase Auth."""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    async def signup(self, email: str, password: str) -> Dict[str, Any]:
        """
        Register new user.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            dict: Keys: user, session, email_confirmation_required
            
        Raises:
            HTTPException: If signup fails
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if not response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account"
                )
            
            logger.info("User signup successful")
            
            # session might be None if email confirmation is required
            return {
                "user": response.user,
                "session": response.session,
                "email_confirmation_required": response.session is None
            }
            
        except Exception as e:
            logger.error("Signup failed")
            
            # Handle specific Supabase errors
            error_message = str(e)
            if "already registered" in error_message.lower() or "already exists" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            elif "invalid email" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )
            elif "password" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password does not meet requirements"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create account. Please try again."
                )
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            dict: Keys: user, session
            
        Raises:
            HTTPException: If login fails
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not response.user or not response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            logger.info("User login successful")
            
            return {
                "user": response.user,
                "session": response.session
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Login failed")
            
            error_message = str(e)
            if "invalid" in error_message.lower() or "credentials" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Login failed. Please try again."
                )
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            dict: Keys: user
            
        Raises:
            HTTPException: If token invalid or expired
        """
        try:
            response = self.client.auth.get_user(token)
            
            if not response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            
            return {"user": response.user}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Token verification failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            dict: Keys: session
            
        Raises:
            HTTPException: If refresh fails
        """
        try:
            response = self.client.auth.refresh_session(refresh_token)
            
            if not response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            logger.info("Token refresh successful")
            
            return {"session": response.session}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Token refresh failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh token. Please login again."
            )
    
    async def logout(self, token: str) -> None:
        """
        Logout user and invalidate session.
        
        Args:
            token: JWT access token
        """
        try:
            self.client.auth.sign_out()
            logger.info("User logout successful")
            
        except Exception as e:
            logger.error("Logout failed")
            pass
