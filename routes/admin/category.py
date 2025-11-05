from app import app, db
from model import Category
from flask import request, jsonify

@app.get('/category/list')
def category_list():
    categories = Category.query.all()
    result = [{"id": c.id, "name": c.name} for c in categories]
    return jsonify(result), 200

@app.get('/category/<int:category_id>')
def category_get(category_id):
    c = Category.query.get(category_id)
    if not c:
        return jsonify({"error": "Category not found"}), 404
    return jsonify({"id": c.id, "name": c.name}), 200

@app.post('/category/create')
def category_create():
    data = request.get_json()
    name = data.get('name')

    existing = Category.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": "Category already exists"}), 409

    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({
        "message": "Category created successfully",
        "category": {"id": new_category.id, "name": new_category.name}
    }), 201

@app.put('/category/update/<int:category_id>')
def category_update(category_id):
    c = Category.query.get(category_id)
    if not c:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json()
    c.name = data.get('name', c.name)

    db.session.commit()

    return jsonify({
        "message": "Category updated successfully",
        "category": {"id": c.id, "name": c.name}
    }), 200

@app.delete('/category/delete/<int:category_id>')
def category_delete(category_id):
    c = Category.query.get(category_id)
    if not c:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(c)
    db.session.commit()

    return jsonify({
        "message": "Category deleted successfully",
        "category": {"id": c.id, "name": c.name}
    }), 200
