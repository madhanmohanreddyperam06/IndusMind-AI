"""API routes for User Profile."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.services.profile import ProfileService
from app.schemas.profile import ProfileResponse, ProfileUpdate, PasswordChange, UserPreferences, PreferencesUpdate, PreferencesResponse
from app.core.logging import setup_logging
from datetime import datetime

logger = setup_logging()
router = APIRouter()


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    """Dependency to get profile service."""
    return ProfileService(db)


@router.get("", response_model=ProfileResponse)
def get_profile(
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile."""
    try:
        return service.get_profile(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get profile")


@router.patch("", response_model=ProfileResponse)
def update_profile(
    update_data: ProfileUpdate,
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user profile."""
    try:
        return service.update_profile(current_user.id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update profile")


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_active_user)
):
    """Change current user password."""
    try:
        service.change_password(current_user.id, password_data)
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to change password")


@router.get("/preferences", response_model=UserPreferences)
def get_preferences(
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user preferences."""
    try:
        preferences = service.get_preferences(current_user.id)
        return UserPreferences(**preferences)
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get preferences")


@router.patch("/preferences", response_model=PreferencesResponse)
def update_preferences(
    update_data: PreferencesUpdate,
    service: ProfileService = Depends(get_profile_service),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user preferences."""
    try:
        preferences = service.update_preferences(current_user.id, update_data.preferences)
        return PreferencesResponse(
            user_id=current_user.id,
            preferences=preferences,
            updated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update preferences")
