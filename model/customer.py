from app import db
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    remark = db.Column(db.String(128))

    # Relationships
    cart_items = db.relationship('CustomerCart', backref='customer', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)