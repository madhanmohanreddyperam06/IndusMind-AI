"""API routes for Password Reset."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.password_reset import PasswordResetService
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    ValidateTokenRequest,
    ValidateTokenResponse
)
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


def get_password_reset_service(db: Session = Depends(get_db)) -> PasswordResetService:
    """Dependency to get password reset service."""
    return PasswordResetService(db)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(
    request: ForgotPasswordRequest,
    service: PasswordResetService = Depends(get_password_reset_service)
):
    """Initiate password reset (no authentication required)."""
    try:
        token = service.forgot_password(request.email)
        
        # In production, we would not include the token in the response
        # For demo purposes, we'll include it so the user can test the flow
        message = "If an account exists with this email, a password reset link has been sent."
        return ForgotPasswordResponse(
            message=message,
            reset_token=token if token else None
        )
    except Exception as e:
        logger.error(f"Error in forgot password: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process password reset request")


@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password(
    request: ResetPasswordRequest,
    service: PasswordResetService = Depends(get_password_reset_service)
):
    """Reset password using a valid token (no authentication required)."""
    try:
        # Verify passwords match
        if request.new_password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords do not match"
            )
        
        service.reset_password(request.token, request.new_password)
        return ResetPasswordResponse(message="Password reset successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error in reset password: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password")


@router.post("/validate-token", response_model=ValidateTokenResponse)
def validate_token(
    request: ValidateTokenRequest,
    service: PasswordResetService = Depends(get_password_reset_service)
):
    """Validate a password reset token (no authentication required)."""
    try:
        result = service.validate_token(request.token)
        return ValidateTokenResponse(**result)
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to validate token")
