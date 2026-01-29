import re

from flask import request, jsonify
from werkzeug.security import generate_password_hash

from app import app, db
from model import User


@app.post('/register')
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Validate required fields
    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400

    tag_re = re.compile(r'<[^>]+>')
    username = tag_re.sub('', username)
    email = tag_re.sub('', email)
    password = tag_re.sub('', password)

    # Check if user exists
    existing = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing:
        return jsonify({"error": "User already exists"}), 409

    if len(username) < 3 or len(username) > 20:
        return jsonify({"error": "Username must be 3–20 characters"}), 400

    if not re.match(r"^[A-Za-z0-9_.-]+$", username):
        return jsonify({"error": "Username can only contain letters, numbers, ., _, -"}), 400

    # ========== VALIDATE GMAIL ==========
    if not email.lower().endswith("@gmail.com"):
        return jsonify({"error": "Email must be a valid Gmail address"}), 400

    if not re.match(r"^[A-Za-z0-9._%+-]+@gmail\.com$", email):
        return jsonify({"error": "Invalid Gmail format"}), 400

    # ========== VALIDATE PASSWORD ==========
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

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
        "message": "success",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }), 201