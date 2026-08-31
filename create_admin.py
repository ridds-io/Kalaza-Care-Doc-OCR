from werkzeug.security import generate_password_hash

from app import app
from extensions import db
from models.user import User


with app.app_context():

    existing = User.query.filter_by(
        username="admin"
    ).first()

    if existing:
        print("Admin already exists.")

    else:

        admin = User(
            username="admin",
            email="admin@doctrack.com",
            password_hash=generate_password_hash("admin123"),
            role="Admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin Created Successfully")