from app import app, db
from model import Order, OrderItem, Customer, Product, User
from flask import request, jsonify
from datetime import datetime

@app.get('/invoice/list')
def invoice_list():
    try:
        orders = Order.query.all()
        result = []
        for o in orders:
            items = [
                {
                    "id": i.id,
                    "product_id": i.product_id,
                    "price": float(i.price),
                    "qty": i.qty,
                    "total": float(i.total)
                } for i in o.items
            ]
            total = sum(i['total'] for i in items)
            result.append({
                "id": o.id,
                "user_id": o.user_id,
                "customer_id": o.customer_id,
                "date_time": o.date_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": o.status,
                "items": items,
                "total": total
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500



@app.get('/invoice/<int:invoice_id>')
def invoice_get(invoice_id):
    o = Order.query.get(invoice_id)
    if not o:
        return jsonify({"error": "Invoice not found"}), 404

    items = [
        {
            "id": i.id,
            "product_id": i.product_id,
            "price": float(i.price),
            "qty": i.qty,
            "total": float(i.total)
        } for i in o.items
    ]
    total = sum(i['total'] for i in items)

    return jsonify({
        "id": o.id,
        "user_id": o.user_id,
        "customer_id": o.customer_id,
        "date_time": o.date_time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": o.status,
        "items": items,
        "total": total
    }), 200


@app.post('/invoice/create')
def invoice_create():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        user_id = data.get('user_id')
        customer_id = data.get('customer_id')
        status = data.get('status', 'pending')
        items = data.get('items', [])

        if not user_id or not customer_id or not items:
            return jsonify({"error": "user_id, customer_id and items are required"}), 400

        # Fetch user and customer for later return
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User {user_id} not found"}), 400

        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": f"Customer {customer_id} not found"}), 400

        # Create Order
        order = Order(
            user_id=user_id,
            customer_id=customer_id,
            date_time=datetime.now(),
            status=status
        )
        db.session.add(order)
        db.session.commit()  # commit first to get order.id

        # Add order items
        detailed_items = []
        for item in items:
            product_id = item.get('product_id')
            qty = item.get('qty', 1)
            product = Product.query.get(product_id)
            if not product:
                return jsonify({"error": f"Product {product_id} not found"}), 400

            sub_total = product.price * qty
            order_item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                price=product.price,
                qty=qty,
                total=sub_total
            )
            db.session.add(order_item)

            # Prepare detailed item for response
            detailed_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "qty": qty,
                "price": float(product.price),
                "sub_total": float(sub_total)
            })

        db.session.commit()

        # Calculate total
        total = sum(i['sub_total'] for i in detailed_items)

        return jsonify({
            "message": "Invoice created successfully",
            "invoice_id": order.id,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "customer": {
                "id": customer.id,
                "username": customer.username,
                "email": customer.email
            },
            "items": detailed_items,
            "total": float(total)
        }), 201

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500


@app.put('/invoice/update/<int:invoice_id>')
def invoice_update(invoice_id):
    try:
        o = Order.query.get(invoice_id)
        if not o:
            return jsonify({"error": "Invoice not found"}), 404

        data = request.get_json()

        # Update status, user, customer
        o.status = data.get('status', o.status)
        o.customer_id = data.get('customer_id', o.customer_id)
        o.user_id = data.get('user_id', o.user_id)

        # Fetch updated user and customer info
        user = User.query.get(o.user_id)
        customer = Customer.query.get(o.customer_id)

        # Update items if provided
        new_items = data.get('items')
        detailed_items = []
        if new_items is not None:
            # Delete existing items
            OrderItem.query.filter_by(order_id=o.id).delete()
            # Add new items
            for item in new_items:
                product_id = item.get('product_id')
                qty = item.get('qty', 1)
                product = Product.query.get(product_id)
                if not product:
                    continue
                sub_total = product.price * qty
                order_item = OrderItem(
                    order_id=o.id,
                    product_id=product_id,
                    price=product.price,
                    qty=qty,
                    total=sub_total
                )
                db.session.add(order_item)
                detailed_items.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "qty": qty,
                    "price": float(product.price),
                    "sub_total": float(sub_total)
                })

        db.session.commit()

        # If items were not updated, get current ones
        if not detailed_items:
            order_items = OrderItem.query.filter_by(order_id=o.id).all()
            for i in order_items:
                detailed_items.append({
                    "product_id": i.product.id,
                    "product_name": i.product.name,
                    "qty": i.qty,
                    "price": float(i.price),
                    "sub_total": float(i.total)
                })

        total = sum(i['sub_total'] for i in detailed_items)

        return jsonify({
            "message": "Invoice updated successfully",
            "invoice_id": o.id,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "customer": {
                "id": customer.id,
                "username": customer.username,
                "email": customer.email
            },
            "items": detailed_items,
            "total": float(total)
        }), 200

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500


@app.delete('/invoice/delete/<int:invoice_id>')
def invoice_delete(invoice_id):
    o = Order.query.get(invoice_id)
    if not o:
        return jsonify({"error": "Invoice not found"}), 404

    # Prepare details before deleting
    items = [
        {
            "product_id": i.product_id,
            "product_name": i.product.name,
            "qty": i.qty,
            "price": float(i.price),
            "sub_total": float(i.total)
        } for i in o.items
    ]
    total = sum(i['sub_total'] for i in items)

    user = User.query.get(o.user_id)
    customer = Customer.query.get(o.customer_id)

    response_data = {
        "invoice_id": o.id,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        },
        "customer": {
            "id": customer.id,
            "username": customer.username,
            "email": customer.email
        },
        "items": items,
        "total": float(total)
    }

    # Delete related items and order
    OrderItem.query.filter_by(order_id=o.id).delete()
    db.session.delete(o)
    db.session.commit()

    return jsonify({
        "message": "Invoice deleted successfully",
        "deleted_invoice": response_data
    }), 200

