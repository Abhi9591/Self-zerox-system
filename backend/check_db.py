
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_data():
    try:
        print(f"Connecting to: {os.getenv('POSTGRES_DB')} on {os.getenv('POSTGRES_SERVER')}...")
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_SERVER", "localhost"),
            database=os.getenv("POSTGRES_DB", "self_xerox"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password")
        )
        cur = conn.cursor()

        # Check Admins
        cur.execute("SELECT * FROM admins;")
        admins = cur.fetchall()
        print(f"\n[Admins Table] Count: {len(admins)}")
        for a in admins:
            print(f" - ID: {a[0]}, User: {a[1]}, Active: {a[3]}")

        # Check Machines
        cur.execute("SELECT * FROM machines;")
        machines = cur.fetchall()
        print(f"\n[Machines Table] Count: {len(machines)}")
        for m in machines:
            print(f" - ID: {m[0]}, Code: {m[1]}, Name: {m[2]}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error checking DB: {e}")

if __name__ == "__main__":
    check_data()
