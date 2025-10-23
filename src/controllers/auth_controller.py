from fastapi import HTTPException, status
from typing import Dict, Any
import logging

from services.auth_service import AuthService
from models.schemas import SignupRequest, LoginRequest, AuthResponse, UserInfo

logger = logging.getLogger(__name__)


class AuthController:
    """Controller for handling authentication business logic."""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    async def handle_signup(self, signup_data: SignupRequest) -> AuthResponse:
        """
        Handle user signup request.
        
        Args:
            signup_data: Signup request data
            
        Returns:
            AuthResponse with tokens and user info
            
        Raises:
            HTTPException: If signup fails
        """
        try:
            # Call auth service to create user
            result = await self.auth_service.signup(
                email=signup_data.email,
                password=signup_data.password
            )
            
            user = result["user"]
            session = result["session"]
            email_confirmation_required = result.get("email_confirmation_required", False)
            
            if email_confirmation_required or session is None:
                raise HTTPException(
                    status_code=status.HTTP_201_CREATED,
                    detail="Account created successfully. Please check your email to confirm your account before logging in."
                )
            
            # Format response with session tokens
            return AuthResponse(
                access_token=session.access_token,
                token_type="bearer",
                expires_in=session.expires_in if hasattr(session, 'expires_in') else 3600,
                refresh_token=session.refresh_token,
                user=UserInfo(
                    id=user.id,
                    email=user.email,
                    created_at=user.created_at if hasattr(user, 'created_at') else None
                )
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Signup handler error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create account"
            )
    
    async def handle_login(self, login_data: LoginRequest) -> AuthResponse:
        """
        Handle user login request.
        
        Args:
            login_data: Login request data
            
        Returns:
            AuthResponse with tokens and user info
            
        Raises:
            HTTPException: If login fails
        """
        try:
            # Call auth service to authenticate user
            result = await self.auth_service.login(
                email=login_data.email,
                password=login_data.password
            )
            
            user = result["user"]
            session = result["session"]
            
            # Format response
            return AuthResponse(
                access_token=session.access_token,
                token_type="bearer",
                expires_in=session.expires_in if hasattr(session, 'expires_in') else 3600,
                refresh_token=session.refresh_token,
                user=UserInfo(
                    id=user.id,
                    email=user.email,
                    created_at=user.created_at if hasattr(user, 'created_at') else None
                )
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login handler error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )
    
    async def handle_refresh(self, refresh_token: str) -> AuthResponse:
        """
        Handle token refresh request.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            AuthResponse with new tokens
            
        Raises:
            HTTPException: If refresh fails
        """
        try:
            result = await self.auth_service.refresh_token(refresh_token)
            session = result["session"]
            
            # Get user info from new token
            user_result = await self.auth_service.verify_token(session.access_token)
            user = user_result["user"]
            
            return AuthResponse(
                access_token=session.access_token,
                token_type="bearer",
                expires_in=session.expires_in if hasattr(session, 'expires_in') else 3600,
                refresh_token=session.refresh_token,
                user=UserInfo(
                    id=user.id,
                    email=user.email,
                    created_at=user.created_at if hasattr(user, 'created_at') else None
                )
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh handler error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh token"
            )
    
    async def handle_logout(self, token: str) -> Dict[str, str]:
        """
        Handle user logout request.
        
        Args:
            token: Access token
            
        Returns:
            Success message
        """
        try:
            await self.auth_service.logout(token)
            return {"message": "Logged out successfully"}
            
        except Exception as e:
            logger.error(f"Logout handler error: {str(e)}")

            return {"message": "Logged out successfully"}
