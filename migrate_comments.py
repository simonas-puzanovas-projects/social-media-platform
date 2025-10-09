"""
Migration script to add created_at column to post_comment table
Run this once to update your database schema
"""
from app import app_init, db
from datetime import datetime
import sqlite3

def migrate():
    app = app_init()

    with app.app_context():
        # Get the database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

        print(f"Migrating database: {db_path}")

        # Connect directly to SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Check if created_at column already exists
            cursor.execute("PRAGMA table_info(post_comment)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'created_at' not in columns:
                print("Adding created_at column to post_comment table...")

                # Add the created_at column with a default value
                cursor.execute("""
                    ALTER TABLE post_comment
                    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)

                # Update existing rows to have the current timestamp
                cursor.execute("""
                    UPDATE post_comment
                    SET created_at = CURRENT_TIMESTAMP
                    WHERE created_at IS NULL
                """)

                conn.commit()
                print("✅ Migration successful! created_at column added to post_comment table")
            else:
                print("✅ Column 'created_at' already exists. No migration needed.")

        except Exception as e:
            conn.rollback()
            print(f"❌ Migration failed: {e}")
            raise
        finally:
            conn.close()

if __name__ == "__main__":
    migrate()
