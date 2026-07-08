"""Script to drop the users table using pymysql."""
import pymysql
from urllib.parse import quote_plus

# Database credentials
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "Madhanreddy@123"
MYSQL_DATABASE = "indusmind"

try:
    # Connect to MySQL
    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    
    cursor = connection.cursor()
    
    # Drop the users table
    cursor.execute("DROP TABLE IF EXISTS users")
    connection.commit()
    
    print("Users table dropped successfully!")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
