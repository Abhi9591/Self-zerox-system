
import psycopg2
import os
from dotenv import load_dotenv
from app.core.security import get_password_hash

load_dotenv()

def seed_data():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_SERVER", "localhost"),
            database=os.getenv("POSTGRES_DB", "self_xerox"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password")
        )
        cur = conn.cursor()

        # 1. Admin
        username = "admin"
        password = "password"
        hashed_pw = get_password_hash(password)
        
        cur.execute("SELECT id FROM admins WHERE username = %s", (username,))
        existing = cur.fetchone()
        
        if existing:
            print(f"Admin '{username}' already exists.")
            admin_id = existing[0]
        else:
            cur.execute("INSERT INTO admins (username, hashed_password, is_active) VALUES (%s, %s, TRUE) RETURNING id", 
                           (username, hashed_pw))
            admin_id = cur.fetchone()[0]
            print(f"Created Admin: '{username}'")

        # 2. Machine
        machine_code = "KIOSK-001"
        cur.execute("SELECT id FROM machines WHERE machine_code = %s", (machine_code,))
        existing_machine = cur.fetchone()
        
        if existing_machine:
             machine_id = existing_machine[0]
             print(f"Machine '{machine_code}' already exists.")
        else:
            # Using 5.0 explicitly
            cur.execute("INSERT INTO machines (machine_code, name, price_per_page, is_active) VALUES (%s, %s, 5.0, TRUE) RETURNING id", 
                           (machine_code, f"Kiosk {machine_code}"))
            machine_id = cur.fetchone()[0]
            print(f"Created Machine: '{machine_code}'")

        # 3. Binding
        cur.execute("SELECT id FROM admin_machine_map WHERE machine_id = %s", (machine_id,))
        existing_map = cur.fetchone()
        
        if existing_map:
            print("Binding already exists.")
        else:
            cur.execute("INSERT INTO admin_machine_map (admin_id, machine_id) VALUES (%s, %s)", 
                           (admin_id, machine_id))
            print("Machine bound to Admin.")

        conn.commit()
        cur.close()
        conn.close()
        print("\nSUCCESS: Database seeded (PostgreSQL).")
        print(f"Login with: {username} / {password}")

    except Exception as e:
        print(f"Error seeding: {e}")

if __name__ == "__main__":
    seed_data()
