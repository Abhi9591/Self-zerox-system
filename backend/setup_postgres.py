

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def setup_database():
    # Support both DATABASE_URL and individual variables
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Parse DATABASE_URL (for Render.com)
        parsed = urlparse(database_url)
        user = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 5432
        target_db = parsed.path[1:]  # Remove leading '/'
        default_db = "postgres"
        
        print(f"Using DATABASE_URL: {parsed.hostname}/{target_db}")
    else:
        # Use individual variables (for local development)
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "password")
        host = os.getenv("POSTGRES_SERVER", "localhost")
        port = 5432
        target_db = os.getenv("POSTGRES_DB", "self_xerox")
        default_db = "postgres"
        
        print(f"Connecting to '{default_db}' on {host} as {user}...")

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=default_db,
            user=user,
            password=password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Check if DB exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{target_db}'")
        exists = cur.fetchone()

        if not exists:
            print(f"Creating database '{target_db}'...")
            cur.execute(f"CREATE DATABASE {target_db}")
            print("Database created successfully!")
        else:
            print(f"Database '{target_db}' already exists.")

        cur.close()
        conn.close()
        
        print("\nSetup Complete. Now run: python seed_db.py")

    except Exception as e:
        print(f"\nERROR: Could not connect to PostgreSQL.")
        print(f"Details: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is installed and running.")
        print("2. Check the password in your .env file.")
        print("3. Ensure the 'postgres' user exists (Default for Windows installer).")

if __name__ == "__main__":
    setup_database()
