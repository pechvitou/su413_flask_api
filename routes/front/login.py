from flask import render_template, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import app


@app.route("/login-page")
def login_page():
    user_id = None
    # Check access token in header (memory) first
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            # Already logged in → redirect to dashboard
            return redirect(url_for("dashboard"))
    except:
        pass
    return render_template("/auth/login.html")
