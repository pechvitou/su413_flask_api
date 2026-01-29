from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt_identity
from app import app
from flask import render_template, redirect, url_for

from model import User


@app.route('/admin')
@jwt_required()
def admin():
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        return redirect(url_for("login_page"))

    # Optional: check user role if needed
    user = User.query.get(user_id)
    if user.role != "admin":
        return render_template("error_page/403.html"), 403

    return render_template('admin.html')
