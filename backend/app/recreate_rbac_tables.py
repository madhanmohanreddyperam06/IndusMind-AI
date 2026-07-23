"""Script to recreate RBAC tables with correct schema."""
from sqlalchemy import text
from app.config.database import engine

def recreate_rbac_tables():
    """Drop and recreate RBAC tables."""
    tables_to_drop = [
        'role_permissions',
        'user_roles', 
        'permissions',
        'roles',
        'audit_logs',
        'notifications'
    ]
    
    with engine.connect() as conn:
        for table in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                print(f"Dropped table: {table}")
            except Exception as e:
                print(f"Error dropping {table}: {e}")
        
        conn.commit()
    
    print("RBAC tables dropped successfully")
    
    # Recreate tables
    from app.config.database import init_db
    init_db()
    print("RBAC tables recreated with correct schema")

if __name__ == "__main__":
    recreate_rbac_tables()
