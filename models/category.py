from extensions import db

class Category(db.Model):
    __tablename__ = "categories"

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    documents = db.relationship("Document", backref="category", lazy=True)