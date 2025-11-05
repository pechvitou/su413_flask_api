from app import app, db
from model import Product
from flask import request, jsonify
import uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/product_images'

@app.get('/product/list')
def product_list():
    products = Product.query.all()
    result = [
        {
            "id": p.id,
            "name": p.name,
            "category_id": p.category_id,
            "cost": float(p.cost),
            "price": float(p.price),
            "image": p.image,
            "stock": float(p.stock),
            "description": p.description
        }
        for p in products
    ]
    return jsonify(result), 200

@app.get('/api/product/<int:product_id>/', strict_slashes=False)
def product_get(product_id):
    p = Product.query.get(product_id)
    if not p:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({
        "id": p.id,
        "name": p.name,
        "category_id": p.category_id,
        "cost": float(p.cost),
        "price": float(p.price),
        "image": p.image,
        "stock": float(p.stock),
        "description": p.description
    }), 200

@app.post('/product/create')
def product_create():
    data = request.form
    files = request.files

    # Get fields
    name = data.get('name')
    category_id = data.get('category_id')
    cost = data.get('cost')
    price = data.get('price')
    stock = data.get('stock', 0)
    description = data.get('description')

    # Validate required fields
    if not name or not category_id or not cost or not price:
        return jsonify({"error": "Name, category_id, cost, and price are required"}), 400

    # Convert types
    try:
        category_id = int(category_id)
        cost = float(cost)
        price = float(price)
        stock = float(stock)
    except (ValueError, TypeError):
        return jsonify({"error": "category_id must be int, cost/price/stock must be numbers"}), 400

    # Handle image file
    image_file = files.get('image')
    if image_file:
        filename = secure_filename(image_file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        image_file.save(f"{UPLOAD_FOLDER}/{unique_filename}")
        image_filename = unique_filename
    else:
        image_filename = None

    # Check if product exists
    existing = Product.query.filter_by(name=name, category_id=category_id).first()
    if existing:
        return jsonify({"error": "Product already exists in this category"}), 409

    # Create product
    new_product = Product(
        name=name,
        category_id=category_id,
        cost=cost,
        price=price,
        stock=stock,
        description=description,
        image=image_filename
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "message": "Product created successfully",
        "product": {
            "id": new_product.id,
            "name": new_product.name,
            "category_id": new_product.category_id,
            "cost": float(new_product.cost),
            "price": float(new_product.price),
            "stock": float(new_product.stock),
            "description": new_product.description,
            "image": new_product.image
        }
    }), 201

# --------------------- UPDATE ---------------------
@app.put('/product/update/<int:product_id>')
def product_update(product_id):
    p = Product.query.get(product_id)
    if not p:
        return jsonify({"error": "Product not found"}), 404

    data = request.form
    files = request.files

    # Get fields from form-data
    name = data.get('name', p.name)
    category_id = data.get('category_id', p.category_id)
    cost = data.get('cost', p.cost)
    price = data.get('price', p.price)
    stock = data.get('stock', p.stock)
    description = data.get('description', p.description)

    # Convert types
    try:
        category_id = int(category_id)
        cost = float(cost)
        price = float(price)
        stock = float(stock)
    except (ValueError, TypeError):
        return jsonify({"error": "category_id must be int, cost/price/stock must be numbers"}), 400

    # Handle image file if uploaded
    image_file = files.get('image')
    if image_file:
        filename = secure_filename(image_file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        image_file.save(f"{UPLOAD_FOLDER}/{unique_filename}")
        p.image = unique_filename  # update image only if new file is uploaded

    # Update other fields
    p.name = name
    p.category_id = category_id
    p.cost = cost
    p.price = price
    p.stock = stock
    p.description = description

    db.session.commit()

    return jsonify({
        "message": "Product updated successfully",
        "product": {
            "id": p.id,
            "name": p.name,
            "category_id": p.category_id,
            "cost": float(p.cost),
            "price": float(p.price),
            "stock": float(p.stock),
            "description": p.description,
            "image": p.image
        }
    }), 200


@app.delete('/product/delete/<int:product_id>')
def product_delete(product_id):
    p = Product.query.get(product_id)
    if not p:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(p)
    db.session.commit()

    return jsonify({
        "message": "Product deleted successfully",
        "product": {
            "id": p.id,
            "name": p.name,
            "category_id": p.category_id,
            "cost": float(p.cost),
            "price": float(p.price),
            "image": p.image,
            "stock": float(p.stock),
            "description": p.description
        }
    }), 200
