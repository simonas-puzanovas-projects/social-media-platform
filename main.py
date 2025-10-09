from app import app_init, db
from app.models import User
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate

app = app_init()
migrate = Migrate(app, db)

def init_db():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('password123')
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Created admin user: admin/password123")

# Socket event handlers

if __name__ == "__main__":

    init_db()

    from app import socketio
    socketio.run(app, debug=True, host='0.0.0.0')


