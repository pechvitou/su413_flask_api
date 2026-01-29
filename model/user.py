from sqlalchemy import DateTime

from app import db
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer')
    profile_image = db.Column(db.Text, nullable=True)
    last_login = db.Column(DateTime, nullable=True)  # NEW FIELD
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)