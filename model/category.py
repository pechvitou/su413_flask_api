from app import db
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Relationship: one category → many products
    products = db.relationship('Product', backref='category', lazy=True)
