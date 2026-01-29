import base64
import re
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity
from werkzeug.utils import secure_filename
from app import app, db
from model import User
from flask import request, jsonify
from werkzeug.security import generate_password_hash


@app.get('/user/list')
@jwt_required()
def user_list():
    users = User.query.all()
    result = [{"id": u.id, "username": u.username, "email": u.email} for u in users]
    return jsonify(result), 200


@app.get('/user/<int:user_id>')
@jwt_required()
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
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }), 201

@app.put('/user/update/<int:user_id>')
@jwt_required()
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
@jwt_required()
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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post('/update-profile')
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    if 'profile' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400

    file = request.files['profile']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # Convert to base64
        file_bytes = file.read()
        encoded_str = f"data:{file.content_type};base64," + base64.b64encode(file_bytes).decode('utf-8')

        # Save to correct database field
        current_user.profile_image = encoded_str
        db.session.commit()

        return jsonify({'success': True, 'profile': current_user.profile_image})

    return jsonify({'success': False, 'message': 'Invalid file type'}), 400
