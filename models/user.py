from extensions import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="Staff"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    documents = db.relationship(
        "Document",
        backref="user",
        lazy=True
    )

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f"<User {self.username}>"