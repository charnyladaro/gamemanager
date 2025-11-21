"""
Migration script to add admin functionality to the GameManager database.
This script:
1. Adds is_admin column to users table
2. Creates a default admin user (admin/admin123)
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'gamemanager.db')

def migrate_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if is_admin column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'is_admin' not in columns:
            print("Adding is_admin column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            conn.commit()
            print("[OK] is_admin column added successfully")
        else:
            print("[OK] is_admin column already exists")

        # Check if admin user exists
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()

        if not admin_user:
            print("\nCreating default admin user...")
            password_hash = generate_password_hash('admin123')
            now = datetime.utcnow().isoformat()

            cursor.execute("""
                INSERT INTO users (username, email, password_hash, display_name, is_admin, is_online, last_seen, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ('admin', 'admin@gamemanager.local', password_hash, 'Administrator', 1, 0, now, now))

            conn.commit()
            print("[OK] Admin user created successfully")
            print("\n" + "="*60)
            print("DEFAULT ADMIN CREDENTIALS:")
            print("Username: admin")
            print("Password: admin123")
            print("="*60)
            print("\n[WARNING] IMPORTANT: Please change the admin password after first login!")
        else:
            print("[OK] Admin user already exists")
            # Update existing admin user to have admin privileges if not set
            cursor.execute("UPDATE users SET is_admin = 1 WHERE username = 'admin'")
            conn.commit()

        print("\n[OK] Migration completed successfully!")

    except Exception as e:
        print(f"[ERROR] Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    print("GameManager Admin Migration")
    print("="*60)
    migrate_database()
