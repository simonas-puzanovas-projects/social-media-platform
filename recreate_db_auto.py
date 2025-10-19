"""
Script to recreate the database with cascade delete constraints
This version runs automatically without user confirmation
"""
import os
from main import app, db

def recreate_database():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()

        print("Creating tables with cascade delete constraints...")
        db.create_all()

        print("Database recreated successfully!")
        print("All foreign keys now have CASCADE DELETE configured.")

        # Optionally create admin user
        from app.models import User
        from werkzeug.security import generate_password_hash

        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('password123')
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Created admin user: admin/password123")

if __name__ == '__main__':
    recreate_database()
