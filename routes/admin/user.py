from app import app, db
from model import User
from flask import request, jsonify
from werkzeug.security import generate_password_hash

@app.get('/user/list')
def user_list():
    users = User.query.all()
    result = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
    return jsonify(result), 200

@app.get('/user/<int:user_id>')
def user_get(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"id": u.id, "username": u.username, "email": u.email}), 200

@app.post('/user/create')
def user_create():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Validate required fields
    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400

    # Check if user exists
    existing = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing:
        return jsonify({"error": "User already exists"}), 409

    # Hash password
    hashed_password = generate_password_hash(password)

    # Create user
    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }), 201

@app.put('/user/update/<int:user_id>')
def user_update(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    # Update fields if provided
    u.username = data.get('username', u.username)
    u.email = data.get('email', u.email)
    new_password = data.get('password')
    if new_password:
        u.password = generate_password_hash(new_password)

    db.session.commit()

    return jsonify({
        "message": "User updated successfully",
        "user": {
            "id": u.id,
            "username": u.username,
            "email": u.email
        }
    }), 200

@app.delete('/user/delete/<int:user_id>')
def user_delete(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(u)
    db.session.commit()

    return jsonify({
        "message": "User deleted successfully",
        "user": {
            "id": u.id,
            "username": u.username,
            "email": u.email
        }
    }), 200
