from datetime import datetime
from flask import request, redirect, url_for, make_response, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, verify_jwt_in_request, get_jwt_identity
from werkzeug.security import check_password_hash
from app import app, db
from model.user import User


@app.post("/login")
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # username = request.form.get("username")
    # password = request.form.get("password")

    if not username or not password:
        # return redirect(url_for("login_page"))
        return jsonify({"message": "Invalid username or password."})

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        # return redirect(url_for("login_page"))
        return jsonify({"message": "Invalid username or password."})

    user.last_login = datetime.utcnow()
    db.session.commit()

    # Create tokens
    access_token = create_access_token(identity=str(user.id))
    # refresh_token = create_refresh_token(identity=str(user.id))

    # Store access/refresh token in HttpOnly cookie
    # resp = make_response(redirect(url_for("dashboard")))
    resp = jsonify({"message": "success", "access_token": access_token})
    resp.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=False,
        samesite="Lax"
    )

    return resp
