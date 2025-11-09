from app import app, db
from model import User, Customer, Product, Category, Order, OrderItem
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

with app.app_context():
    db.drop_all()
    db.create_all()

    # --- Seed Users ---
    users = [
        User(username="admin", email="admin@gmail.com", password=generate_password_hash("admin123")),
        User(username="staff", email="staff@gmail.com", password=generate_password_hash("staff123"))
    ]
    db.session.add_all(users)
    db.session.flush()

    # --- Seed Customers ---
    customers = [
        Customer(username="Pen Pichvitou", email="penpichvitou@gmail.com", password=generate_password_hash("pass123")),
        Customer(username="Sok Dara", email="sokdara@gmail.com", password=generate_password_hash("pass123")),
        Customer(username="Chan Sreyleak", email="chansreyleak@gmail.com", password=generate_password_hash("pass123"))
    ]
    db.session.add_all(customers)
    db.session.flush()

    # --- Seed Categories ---
    categories = [
        Category(name="Clothing"),
        Category(name="Electronics"),
        Category(name="Groceries"),
        Category(name="Accessories"),
        Category(name="Home & Living")
    ]
    db.session.add_all(categories)
    db.session.flush()

    # --- Seed Products ---
    products = [
        # Clothing
        Product(name="Blue Shirt", category_id=categories[0].id, cost=10.0, price=20.0, stock=100),
        Product(name="Black Jeans", category_id=categories[0].id, cost=15.0, price=35.0, stock=80),
        Product(name="Sneakers", category_id=categories[0].id, cost=30.0, price=60.0, stock=50),
        Product(name="Jacket", category_id=categories[0].id, cost=25.0, price=55.0, stock=60),

        # Electronics
        Product(name="Laptop", category_id=categories[1].id, cost=500.0, price=800.0, stock=30),
        Product(name="Smartphone", category_id=categories[1].id, cost=300.0, price=600.0, stock=40),
        Product(name="Headphones", category_id=categories[1].id, cost=50.0, price=100.0, stock=70),
        Product(name="Smartwatch", category_id=categories[1].id, cost=80.0, price=150.0, stock=50),

        # Groceries
        Product(name="Rice 5kg", category_id=categories[2].id, cost=3.0, price=6.0, stock=200),
        Product(name="Cooking Oil 1L", category_id=categories[2].id, cost=2.0, price=4.5, stock=180),
        Product(name="Instant Noodles (Pack)", category_id=categories[2].id, cost=1.0, price=2.0, stock=300),
        Product(name="Fresh Milk 1L", category_id=categories[2].id, cost=1.5, price=3.0, stock=150),

        # Accessories
        Product(name="Leather Belt", category_id=categories[3].id, cost=5.0, price=12.0, stock=90),
        Product(name="Wrist Watch", category_id=categories[3].id, cost=40.0, price=90.0, stock=40),
        Product(name="Sunglasses", category_id=categories[3].id, cost=10.0, price=25.0, stock=100),
        Product(name="Wallet", category_id=categories[3].id, cost=8.0, price=18.0, stock=110),

        # Home & Living
        Product(name="Pillow", category_id=categories[4].id, cost=6.0, price=15.0, stock=100),
        Product(name="Bed Sheet Set", category_id=categories[4].id, cost=20.0, price=40.0, stock=60),
        Product(name="LED Lamp", category_id=categories[4].id, cost=10.0, price=25.0, stock=80),
        Product(name="Electric Kettle", category_id=categories[4].id, cost=15.0, price=35.0, stock=70)
    ]
    db.session.add_all(products)
    db.session.flush()

    # --- Seed Orders (for the whole month) ---
    start_date = datetime(2025, 11, 1)
    end_date = datetime(2025, 11, 30)
    total_days = (end_date - start_date).days + 1

    for i in range(total_days):
        date = start_date + timedelta(days=i)
        daily_orders = random.randint(2, 6)  # 2–6 orders per day

        for _ in range(daily_orders):
            user = users[0] if random.random() < 0.6 else users[1]
            customer = random.choice(customers)
            order = Order(
                user_id=user.id,
                customer_id=customer.id,
                date_time=date,
                status=random.choice(["completed", "pending"])
            )
            db.session.add(order)
            db.session.flush()

            # Each order has 1–4 items
            for _ in range(random.randint(1, 4)):
                product = random.choice(products)
                qty = random.randint(1, 5)
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    qty=qty,
                    price=product.price,
                    total = product.price * qty
                )
                db.session.add(order_item)

    db.session.commit()
    print("Seeding complete with users, customers, categories, products, orders & order_items!")
