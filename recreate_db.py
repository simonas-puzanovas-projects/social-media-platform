"""
Script to recreate the database with cascade delete constraints
WARNING: This will delete all existing data!
"""
import os
from main import app, db

def recreate_database():
    with app.app_context():
        print("WARNING: This will delete all existing data!")
        response = input("Are you sure you want to continue? (yes/no): ")

        if response.lower() != 'yes':
            print("Operation cancelled.")
            return

        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()

        # Create all tables with new schema
        print("Creating tables with cascade delete constraints...")
        db.create_all()

        print("Database recreated successfully!")
        print("All foreign keys now have CASCADE DELETE configured.")

if __name__ == '__main__':
    recreate_database()
