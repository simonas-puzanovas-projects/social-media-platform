"""
Migration script to add description column to post table
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
            # Check if description column already exists
            cursor.execute("PRAGMA table_info(post)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'description' not in columns:
                print("Adding description column to post table...")

                # Add the description column
                cursor.execute("""
                    ALTER TABLE post
                    ADD COLUMN description TEXT
                """)

                conn.commit()
                print("Migration successful! description column added to post table")
            else:
                print("Column 'description' already exists. No migration needed.")

        except Exception as e:
            conn.rollback()
            print(f"Migration failed: {e}")
            raise
        finally:
            conn.close()

if __name__ == "__main__":
    migrate()
