"""Pydantic schemas for Password Reset."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Schema for forgot password response."""
    message: str
    # In production, we would not include the token in the response
    # For demo purposes, we'll include it so the user can test the flow
    reset_token: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    """Schema for reset password request."""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=10, max_length=100)
    confirm_password: str = Field(..., min_length=10, max_length=100)


class ResetPasswordResponse(BaseModel):
    """Schema for reset password response."""
    message: str


class ValidateTokenRequest(BaseModel):
    """Schema for validate token request."""
    token: str = Field(..., min_length=1)


class ValidateTokenResponse(BaseModel):
    """Schema for validate token response."""
    valid: bool
    email: Optional[str] = None
    expires_at: Optional[str] = None
