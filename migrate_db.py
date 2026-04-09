"""
DB Migration: Add new columns to existing portfolio database.
Run once: python migrate_db.py

Safe to run multiple times — uses ALTER TABLE only if column doesn't exist.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "portfolio.db")

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("   Run create_db.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    migrations = [
        ("project", "is_featured", "INTEGER DEFAULT 0"),
        ("post",    "tags",        "TEXT DEFAULT ''"),
        ("message", "subject",     "TEXT DEFAULT ''"),
    ]

    for table, column, col_def in migrations:
        if not column_exists(cur, table, column):
            print(f"  Adding column '{column}' to '{table}'...")
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
            print(f"  ✔ Done.")
        else:
            print(f"  ✓ Column '{column}' in '{table}' already exists — skipping.")

    conn.commit()
    conn.close()
    print("\n✅ Migration complete.")

if __name__ == "__main__":
    migrate()
