"""Seed script for RBAC system - creates initial roles and permissions."""
from sqlalchemy.orm import Session
from app.config.database import SessionLocal, engine
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission
from app.models.user import User


def seed_roles(db: Session):
    """Create initial roles."""
    roles_data = [
        {
            "name": "superuser",
            "description": "Full system access with all permissions",
            "is_active": True,
            "is_system": True
        },
        {
            "name": "admin",
            "description": "Administrative access for user and system management",
            "is_active": True,
            "is_system": True
        },
        {
            "name": "user",
            "description": "Standard user access for document processing and queries",
            "is_active": True,
            "is_system": True
        },
        {
            "name": "viewer",
            "description": "Read-only access to documents and queries",
            "is_active": True,
            "is_system": True
        }
    ]
    
    for role_data in roles_data:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
            db.commit()
            print(f"Created role: {role_data['name']}")
        else:
            print(f"Role already exists: {role_data['name']}")


def seed_permissions(db: Session):
    """Create initial permissions."""
    permissions_data = [
        # User management permissions
        {"name": "users:create", "description": "Create new users", "resource": "users", "action": "create"},
        {"name": "users:read", "description": "View user information", "resource": "users", "action": "read"},
        {"name": "users:update", "description": "Update user information", "resource": "users", "action": "update"},
        {"name": "users:delete", "description": "Delete users", "resource": "users", "action": "delete"},
        
        # Role management permissions
        {"name": "roles:create", "description": "Create new roles", "resource": "roles", "action": "create"},
        {"name": "roles:read", "description": "View role information", "resource": "roles", "action": "read"},
        {"name": "roles:update", "description": "Update role information", "resource": "roles", "action": "update"},
        {"name": "roles:delete", "description": "Delete roles", "resource": "roles", "action": "delete"},
        
        # Permission management permissions
        {"name": "permissions:create", "description": "Create new permissions", "resource": "permissions", "action": "create"},
        {"name": "permissions:read", "description": "View permission information", "resource": "permissions", "action": "read"},
        {"name": "permissions:update", "description": "Update permission information", "resource": "permissions", "action": "update"},
        {"name": "permissions:delete", "description": "Delete permissions", "resource": "permissions", "action": "delete"},
        
        # Document management permissions
        {"name": "documents:create", "description": "Upload and create documents", "resource": "documents", "action": "create"},
        {"name": "documents:read", "description": "View and download documents", "resource": "documents", "action": "read"},
        {"name": "documents:update", "description": "Update document metadata", "resource": "documents", "action": "update"},
        {"name": "documents:delete", "description": "Delete documents", "resource": "documents", "action": "delete"},
        
        # Knowledge extraction permissions
        {"name": "extraction:run", "description": "Run knowledge extraction", "resource": "extraction", "action": "run"},
        {"name": "extraction:read", "description": "View extraction results", "resource": "extraction", "action": "read"},
        
        # Knowledge graph permissions
        {"name": "graph:read", "description": "Query and view knowledge graph", "resource": "graph", "action": "read"},
        {"name": "graph:update", "description": "Update knowledge graph", "resource": "graph", "action": "update"},
        {"name": "graph:delete", "description": "Delete graph data", "resource": "graph", "action": "delete"},
        
        # RAG engine permissions
        {"name": "rag:query", "description": "Query RAG engine", "resource": "rag", "action": "query"},
        {"name": "rag:read", "description": "View RAG conversations", "resource": "rag", "action": "read"},
        {"name": "rag:delete", "description": "Delete RAG conversations", "resource": "rag", "action": "delete"},
        
        # System configuration permissions
        {"name": "config:read", "description": "View system configuration", "resource": "config", "action": "read"},
        {"name": "config:update", "description": "Update system configuration", "resource": "config", "action": "update"},
        
        # System monitoring permissions
        {"name": "monitoring:read", "description": "View system monitoring data", "resource": "monitoring", "action": "read"},
        
        # Audit log permissions
        {"name": "audit:read", "description": "View audit logs", "resource": "audit", "action": "read"},
    ]
    
    for perm_data in permissions_data:
        existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            db.commit()
            print(f"Created permission: {perm_data['name']}")
        else:
            print(f"Permission already exists: {perm_data['name']}")


def seed_role_permissions(db: Session):
    """Assign permissions to roles."""
    # Get all roles and permissions
    superuser_role = db.query(Role).filter(Role.name == "superuser").first()
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    user_role = db.query(Role).filter(Role.name == "user").first()
    viewer_role = db.query(Role).filter(Role.name == "viewer").first()
    
    all_permissions = db.query(Permission).all()
    
    # Superuser gets all permissions
    if superuser_role:
        for permission in all_permissions:
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == superuser_role.id,
                RolePermission.permission_id == permission.id
            ).first()
            if not existing:
                role_permission = RolePermission(role_id=superuser_role.id, permission_id=permission.id)
                db.add(role_permission)
                db.commit()
        print(f"Assigned all permissions to superuser role")
    
    # Admin gets user, role, permission, config, monitoring, audit permissions
    if admin_role:
        admin_permissions = [p for p in all_permissions if p.resource in ["users", "roles", "permissions", "config", "monitoring", "audit"]]
        for permission in admin_permissions:
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == admin_role.id,
                RolePermission.permission_id == permission.id
            ).first()
            if not existing:
                role_permission = RolePermission(role_id=admin_role.id, permission_id=permission.id)
                db.add(role_permission)
                db.commit()
        print(f"Assigned admin permissions to admin role")
    
    # User gets document, extraction, graph (read), rag (query, read) permissions
    if user_role:
        user_permissions = [p for p in all_permissions if p.resource in ["documents", "extraction", "graph", "rag"] and p.action in ["create", "read", "update", "query"]]
        for permission in user_permissions:
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == user_role.id,
                RolePermission.permission_id == permission.id
            ).first()
            if not existing:
                role_permission = RolePermission(role_id=user_role.id, permission_id=permission.id)
                db.add(role_permission)
                db.commit()
        print(f"Assigned user permissions to user role")
    
    # Viewer gets read-only permissions for documents, extraction, graph, rag
    if viewer_role:
        viewer_permissions = [p for p in all_permissions if p.resource in ["documents", "extraction", "graph", "rag"] and p.action == "read"]
        for permission in viewer_permissions:
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == viewer_role.id,
                RolePermission.permission_id == permission.id
            ).first()
            if not existing:
                role_permission = RolePermission(role_id=viewer_role.id, permission_id=permission.id)
                db.add(role_permission)
                db.commit()
        print(f"Assigned viewer permissions to viewer role")


def main():
    """Main seed function."""
    db = SessionLocal()
    try:
        print("Seeding RBAC data...")
        seed_roles(db)
        seed_permissions(db)
        seed_role_permissions(db)
        print("RBAC seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding RBAC data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
