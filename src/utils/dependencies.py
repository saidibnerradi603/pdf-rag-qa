from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from typing import Dict, Any, Optional
import logging

from db.supabase_client import db
from services.auth_service import AuthService

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


def get_supabase_client() -> Client:
    """
    Get Supabase client instance.
    
    Returns:
        Client: Supabase client for database operations
    """
    return db


def get_auth_service(supabase: Client = Depends(get_supabase_client)) -> AuthService:
    """
    Get AuthService instance.
    
    Args:
        supabase: Supabase client
        
    Returns:
        AuthService: Service for authentication operations
    """
    return AuthService(supabase)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Validate JWT token and return authenticated user information.
    
    Args:
        credentials: Bearer token from Authorization header
        supabase: Supabase client instance
        
    Returns:
        dict: User data with keys: id, email, created_at
        
    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        token = credentials.credentials
        response = supabase.auth.get_user(token)
        
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user = response.user
        
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at if hasattr(user, 'created_at') else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token validation failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: Client = Depends(get_supabase_client)
) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns user if authenticated, None otherwise.
    
    Args:
        credentials: Bearer token from Authorization header
        supabase: Supabase client instance
        
    Returns:
        dict: User data if authenticated, None if not
    """
    try:
        return await get_current_user(credentials, supabase)
    except HTTPException:
        return None
