"""Script to reset the users table with new schema (without username)."""
from app.config.database import reset_users_table

if __name__ == "__main__":
    print("Dropping and recreating users table...")
    reset_users_table()
    print("Users table has been reset successfully!")
