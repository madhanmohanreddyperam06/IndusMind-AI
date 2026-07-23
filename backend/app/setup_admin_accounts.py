"""Script to set up admin and superuser accounts with specific credentials."""
import sys
sys.path.insert(0, 'E:\\AI-powered Industrial Knowledge Intelligence Platform\\backend')

from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.services.auth import get_password_hash
from datetime import datetime

# Import all models to ensure relationships are registered
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.audit_log import AuditLog
from app.models.notification import Notification

def setup_admin_accounts():
    """Create admin and superuser accounts with specific credentials."""
    db = SessionLocal()
    
    try:
        # Get role IDs
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        superuser_role = db.query(Role).filter(Role.name == "superuser").first()
        user_role = db.query(Role).filter(Role.name == "user").first()
        
        if not admin_role or not superuser_role or not user_role:
            print("Error: Required roles not found. Please run seed_rbac.py first.")
            return
        
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "madhanmohanreddyperam06@gmail.com").first()
        if existing_admin:
            print("Admin account already exists. Updating password...")
            existing_admin.hashed_password = get_password_hash("Madhan@123")
            existing_admin.is_active = True
            existing_admin.is_superuser = False
            db.commit()
            admin_user = existing_admin
        else:
            # Create admin account
            admin_user = User(
                email="madhanmohanreddyperam06@gmail.com",
                full_name="Madhan Mohan Reddy Peram",
                hashed_password=get_password_hash("Madhan@123"),
                is_active=True,
                is_superuser=False  # Admin is not superuser
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Admin account created successfully")
        
        # Assign admin role
        existing_admin_role = db.query(UserRole).filter(
            UserRole.user_id == admin_user.id,
            UserRole.role_id == admin_role.id
        ).first()
        
        if not existing_admin_role:
            admin_assignment = UserRole(
                user_id=admin_user.id,
                role_id=admin_role.id,
                assigned_at=datetime.utcnow(),
                assigned_by=admin_user.id
            )
            db.add(admin_assignment)
            db.commit()
            print("Admin role assigned")
        
        # Check if superuser already exists
        existing_superuser = db.query(User).filter(User.email == "mohanreddymadhan580@gmail.com").first()
        if existing_superuser:
            print("Superuser account already exists. Updating password...")
            existing_superuser.hashed_password = get_password_hash("Mohan@123")
            existing_superuser.is_active = True
            existing_superuser.is_superuser = True
            db.commit()
            superuser_user = existing_superuser
        else:
            # Create superuser account
            superuser_user = User(
                email="mohanreddymadhan580@gmail.com",
                full_name="Mohan Reddy Madhan",
                hashed_password=get_password_hash("Mohan@123"),
                is_active=True,
                is_superuser=True  # Superuser flag
            )
            db.add(superuser_user)
            db.commit()
            db.refresh(superuser_user)
            print("Superuser account created successfully")
        
        # Assign superuser role
        existing_superuser_role = db.query(UserRole).filter(
            UserRole.user_id == superuser_user.id,
            UserRole.role_id == superuser_role.id
        ).first()
        
        if not existing_superuser_role:
            superuser_assignment = UserRole(
                user_id=superuser_user.id,
                role_id=superuser_role.id,
                assigned_at=datetime.utcnow(),
                assigned_by=superuser_user.id
            )
            db.add(superuser_assignment)
            db.commit()
            print("Superuser role assigned")
        
        print("\n=== Account Setup Complete ===")
        print("\nAdmin Credentials:")
        print("Email: madhanmohanreddyperam06@gmail.com")
        print("Password: Madhan@123")
        print("Role: admin")
        
        print("\nSuperuser Credentials:")
        print("Email: mohanreddymadhan580@gmail.com")
        print("Password: Mohan@123")
        print("Role: superuser")
        
        print("\nNote: Regular users can register and will be assigned 'user' role by default.")
        
    except Exception as e:
        print(f"Error setting up accounts: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_admin_accounts()
