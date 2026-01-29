from flask_jwt_extended import jwt_required

from app import app, db
from model import Branch
from flask import request, jsonify

@app.get('/branch/list')
@jwt_required()
def branch_list():
    branches = Branch.query.all()
    result = [
        {"id": b.id, "name": b.name, "phone": b.phone, "address": b.address, "description": b.description}
        for b in branches
    ]
    return jsonify(result), 200

@app.get('/branch/<int:branch_id>')
@jwt_required()
def branch_get(branch_id):
    b = Branch.query.get(branch_id)
    if not b:
        return jsonify({"error": "Branch not found"}), 404
    return jsonify({
        "id": b.id,
        "name": b.name,
        "phone": b.phone,
        "address": b.address,
        "description": b.description
    }), 200

@app.post('/branch/create')
@jwt_required()
def branch_create():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    address = data.get('address')
    description = data.get('description')

    existing = Branch.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": "Branch already exists"}), 409

    new_branch = Branch(
        name=name,
        phone=phone,
        address=address,
        description=description
    )
    db.session.add(new_branch)
    db.session.commit()

    return jsonify({
        "message": "Branch created successfully",
        "branch": {
            "id": new_branch.id,
            "name": new_branch.name,
            "phone": new_branch.phone,
            "address": new_branch.address,
            "description": new_branch.description
        }
    }), 201

@app.put('/branch/update/<int:branch_id>')
@jwt_required()
def branch_update(branch_id):
    b = Branch.query.get(branch_id)
    if not b:
        return jsonify({"error": "Branch not found"}), 404

    data = request.get_json()
    b.name = data.get('name', b.name)
    b.phone = data.get('phone', b.phone)
    b.address = data.get('address', b.address)
    b.description = data.get('description', b.description)

    db.session.commit()

    return jsonify({
        "message": "Branch updated successfully",
        "branch": {
            "id": b.id,
            "name": b.name,
            "phone": b.phone,
            "address": b.address,
            "description": b.description
        }
    }), 200

@app.delete('/branch/delete/<int:branch_id>')
@jwt_required()
def branch_delete(branch_id):
    b = Branch.query.get(branch_id)
    if not b:
        return jsonify({"error": "Branch not found"}), 404

    db.session.delete(b)
    db.session.commit()

    return jsonify({
        "message": "Branch deleted successfully",
        "branch": {
            "id": b.id,
            "name": b.name,
            "phone": b.phone,
            "address": b.address,
            "description": b.description
        }
    }), 200
