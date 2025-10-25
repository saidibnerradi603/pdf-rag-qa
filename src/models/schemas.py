from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, Any
import re


# Auth schemas
class SignupRequest(BaseModel):
    """Request model for user signup."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserInfo(BaseModel):
    """User information model."""
    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User email address")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Response model for authentication endpoints."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: str = Field(..., description="JWT refresh token")
    user: UserInfo = Field(..., description="User information")




class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str = Field(..., description="Refresh token")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for client handling")


# Document schemas
class DocumentMetadata(BaseModel):
    """Optional metadata for documents."""
    title: Optional[str] = None
    tags: Optional[list[str]] = None
    description: Optional[str] = None


class DocumentResponse(BaseModel):
    """Response model for document operations."""
    id: str
    user_id: str
    file_name: str
    bucket_path: str
    status: str
    metadata: dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    """Response for listing documents."""
    documents: list[DocumentResponse]
    total: int


class DocumentUploadResponse(BaseModel):
    """Response after successful upload."""
    document_id: str
    file_name: str
    status: str
    bucket_path: str
    created_at: datetime
    message: str = "Upload successful"


class DocumentDeleteResponse(BaseModel):
    """Response after deletion."""
    message: str
    document_id: str
