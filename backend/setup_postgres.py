
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    # Connect to default 'postgres' database to create new DB
    default_db = "postgres"
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "password")
    host = os.getenv("POSTGRES_SERVER", "localhost")
    target_db = os.getenv("POSTGRES_DB", "self_xerox")

    print(f"Connecting to '{default_db}' on {host} as {user}...")

    try:
        conn = psycopg2.connect(
            host=host,
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
