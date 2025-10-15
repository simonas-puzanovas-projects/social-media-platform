"""
Migration script to add is_read column to message table
Run this once to update your database schema
"""
from app import app_init, db
import sqlite3

def migrate():
    app = app_init()

    with app.app_context():
        # Get the database path
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            # If it's a relative path, prefix with 'instance/'
            if not db_path.startswith('/') and not ':' in db_path:
                db_path = f'instance/{db_path}'
        else:
            db_path = db_uri

        print(f"Migrating database: {db_path}")

        # Connect directly to SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # Check if is_read column already exists
            cursor.execute("PRAGMA table_info(message)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'is_read' not in columns:
                print("Adding is_read column to message table...")

                # Add the is_read column with a default value
                cursor.execute("""
                    ALTER TABLE message
                    ADD COLUMN is_read BOOLEAN DEFAULT 0
                """)

                # Update existing rows to have the default value
                cursor.execute("""
                    UPDATE message
                    SET is_read = 0
                    WHERE is_read IS NULL
                """)

                conn.commit()
                print("Migration successful! is_read column added to message table")
            else:
                print("Column 'is_read' already exists. No migration needed.")

        except Exception as e:
            conn.rollback()
            print(f"Migration failed: {e}")
            raise
        finally:
            conn.close()

if __name__ == "__main__":
    migrate()
