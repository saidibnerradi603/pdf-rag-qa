from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict

from models.schemas import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
    RefreshTokenRequest,
    ErrorResponse
)
from controllers.auth_controller import AuthController
from services.auth_service import AuthService
from utils.dependencies import get_auth_service, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_controller(
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthController:
    """Dependency to get AuthController instance."""
    return AuthController(auth_service)


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password.",
    responses={
        201: {"description": "User created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid input or email already exists"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def signup(
    request: SignupRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """
    Register a new user account.
    
    Requirements:
    - Valid email address
    - Password minimum 8 characters with uppercase, lowercase, number, and special character
    
    Note: If email confirmation is enabled, check your email before logging in.
    """
    return await controller.handle_signup(request)


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user with email and password to receive JWT tokens.",
    responses={
        200: {"description": "Login successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def login(
    request: LoginRequest,
    controller: AuthController = Depends(get_auth_controller)
) -> AuthResponse:
    """
    Authenticate user and receive JWT tokens.
    
    Returns JWT access token and refresh token.
    Include access token in Authorization header for protected routes.
    """
    return await controller.handle_login(request)


@router.post(
    "/refresh",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using a refresh token.",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def refresh_token(
    request: RefreshTokenRequest,
    controller: AuthController = Depends(get_auth_controller)
) -> AuthResponse:
    """
    Refresh access token using refresh token.
    
    Use this when your access token expires to get a new one without logging in again.
    """
    return await controller.handle_refresh(request.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout current user and invalidate session.",
    responses={
        200: {"description": "Logout successful"},
        401: {"model": ErrorResponse, "description": "Invalid or missing token"}
    }
)
async def logout(
    current_user: Dict = Depends(get_current_user),
    controller: AuthController = Depends(get_auth_controller)
) -> Dict[str, str]:
    """
    Logout current user and invalidate session.
    
    Requires valid JWT token in Authorization header.
    """
    return await controller.handle_logout(token=None)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get information about the currently authenticated user.",
    responses={
        200: {"description": "User information retrieved"},
        401: {"model": ErrorResponse, "description": "Invalid or missing token"}
    }
)
async def get_me(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    Returns user ID, email, and account creation date.
    """
    return {
        "user": current_user,
        "message": "User authenticated successfully"
    }
