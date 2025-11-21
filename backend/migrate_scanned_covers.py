"""
Migration script to add cover_image column to scanned_games table.
Run this before starting the server if you have an existing database.
"""

import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), 'gamemanager.db')

if not os.path.exists(db_path):
    print("Database not found. A new one will be created when the server starts.")
    exit(0)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(scanned_games)")
columns = [column[1] for column in cursor.fetchall()]

if 'cover_image' not in columns:
    print("Adding cover_image column to scanned_games table...")
    try:
        cursor.execute("ALTER TABLE scanned_games ADD COLUMN cover_image VARCHAR(255)")
        conn.commit()
        print("✓ Column added successfully!")
    except Exception as e:
        print(f"Error adding column: {e}")
        conn.rollback()
else:
    print("✓ Column already exists. No migration needed.")

conn.close()
print("\nMigration complete!")
