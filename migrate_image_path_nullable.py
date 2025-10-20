"""
Migration script to make image_path column nullable in post table.
This allows text-only posts without images.
"""
import sqlite3
import os

def migrate_database():
    db_path = os.path.join('instance', 'users.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
        print("Starting migration to make image_path nullable...")

        # Create new table with nullable image_path
        cursor.execute("""
            CREATE TABLE post_new (
                id INTEGER PRIMARY KEY,
                owner INTEGER NOT NULL,
                image_path VARCHAR(100),
                description TEXT,
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY (owner) REFERENCES user(id) ON DELETE CASCADE
            )
        """)

        # Copy data from old table to new table
        cursor.execute("""
            INSERT INTO post_new (id, owner, image_path, description, created_at, updated_at)
            SELECT id, owner, image_path, description, created_at, updated_at
            FROM post
        """)

        # Drop old table
        cursor.execute("DROP TABLE post")

        # Rename new table to original name
        cursor.execute("ALTER TABLE post_new RENAME TO post")

        conn.commit()
        print("Migration completed successfully!")
        print("image_path column is now nullable")

    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise

    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
