from flask_jwt_extended import jwt_required

from app import app, db
from datetime import datetime, timedelta
from sqlalchemy import extract
from flask import jsonify
from model import Order, User

@app.get('/report/daily')
@jwt_required()
def report_daily():
    today = datetime.now().date()
    orders = Order.query.filter(db.func.date(Order.date_time) == today).all()
    return generate_sales_report(orders, title="Daily Sales")


@app.get('/report/weekly')
@jwt_required()
def report_weekly():
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)          # Sunday
    orders = Order.query.filter(db.func.date(Order.date_time).between(start_of_week, end_of_week)).all()
    return generate_sales_report(orders, title="Weekly Sales")


@app.get('/report/monthly')
@jwt_required()
def report_monthly():
    now = datetime.now()
    orders = Order.query.filter(
        extract('year', Order.date_time) == now.year,
        extract('month', Order.date_time) == now.month
    ).all()
    return generate_sales_report(orders, title="Monthly Sales")


@app.get('/report/by/<int:user_id>')
@jwt_required()
def report_by_user_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": f"User {user_id} not found"}), 404

    # Get all orders belonging to this user
    orders = Order.query.filter_by(user_id=user.id).all()
    report = generate_sales_summary(orders)

    return jsonify({
        "title": f"Sales Report for {user.username}",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        },
        "sales_summary": report
    }), 200



def generate_sales_report(orders, title):
    report_data = []
    total_sales = 0

    for o in orders:
        user = User.query.get(o.user_id)
        items = [
            {
                "product_name": i.product.name,
                "qty": i.qty,
                "price": float(i.price),
                "total": float(i.total)
            } for i in o.items
        ]
        invoice_total = sum(i["total"] for i in items)
        total_sales += invoice_total

        report_data.append({
            "invoice_id": o.id,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "customer_id": o.customer_id,
            "status": o.status,
            "date_time": o.date_time.strftime("%Y-%m-%d %H:%M:%S"),
            "items": items,
            "invoice_total": float(invoice_total)
        })

    return jsonify({
        "title": title,
        "total_sales": float(total_sales),
        "total_invoices": len(orders),
        "report": report_data
    }), 200


def generate_sales_summary(orders):
    total_sales = 0
    invoices = []
    for o in orders:
        items = [
            {
                "product_name": i.product.name,
                "qty": i.qty,
                "price": float(i.price),
                "total": float(i.total)
            } for i in o.items
        ]
        invoice_total = sum(i["total"] for i in items)
        total_sales += invoice_total
        invoices.append({
            "invoice_id": o.id,
            "date_time": o.date_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": o.status,
            "items": items,
            "invoice_total": float(invoice_total)
        })
    return {
        "total_invoices": len(invoices),
        "total_sales": float(total_sales),
        "invoices": invoices
    }
