"""Service for Password Reset business logic."""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from typing import Optional
from app.models.user import User
from app.repositories.user import get_user_by_email
from app.services.auth import get_password_hash
from app.core.logging import setup_logging

logger = setup_logging()


class PasswordResetService:
    """Service for Password Reset operations."""
    
    def __init__(self, db: Session):
        self.db = db
        # In production, this would be stored in Redis or a database table
        # For demo purposes, we'll use an in-memory dictionary
        self.reset_tokens = {}
    
    def forgot_password(self, email: str) -> str:
        """Initiate password reset by generating a reset token."""
        user = get_user_by_email(self.db, email=email)
        if not user:
            # For security, we still return success even if user doesn't exist
            # This prevents email enumeration attacks
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return ""
        
        # Generate a secure random token
        token = secrets.token_urlsafe(32)
        
        # Store token with expiration (1 hour from now)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        self.reset_tokens[token] = {
            "user_id": user.id,
            "email": user.email,
            "expires_at": expires_at
        }
        
        # In production, this would send an email with the reset link
        # For demo purposes, we'll log it and return it
        logger.info(f"Password reset token generated for {email}: {token}")
        logger.info(f"Mock email sent to {email} with reset link")
        
        return token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using a valid token."""
        # Validate token
        token_data = self.reset_tokens.get(token)
        if not token_data:
            raise ValueError("Invalid or expired reset token")
        
        # Check expiration
        if datetime.utcnow() > token_data["expires_at"]:
            del self.reset_tokens[token]
            raise ValueError("Reset token has expired")
        
        # Get user
        user = self.db.query(User).filter(User.id == token_data["user_id"]).first()
        if not user:
            raise ValueError("User not found")
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        
        # Remove used token
        del self.reset_tokens[token]
        
        logger.info(f"Password reset successful for user {user.email}")
        
        return True
    
    def validate_token(self, token: str) -> dict:
        """Validate a password reset token."""
        token_data = self.reset_tokens.get(token)
        if not token_data:
            return {
                "valid": False,
                "email": None,
                "expires_at": None
            }
        
        # Check expiration
        if datetime.utcnow() > token_data["expires_at"]:
            del self.reset_tokens[token]
            return {
                "valid": False,
                "email": None,
                "expires_at": None
            }
        
        return {
            "valid": True,
            "email": token_data["email"],
            "expires_at": token_data["expires_at"].isoformat()
        }
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens (should be run periodically)."""
        current_time = datetime.utcnow()
        expired_tokens = [
            token for token, data in self.reset_tokens.items()
            if current_time > data["expires_at"]
        ]
        
        for token in expired_tokens:
            del self.reset_tokens[token]
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired reset tokens")
