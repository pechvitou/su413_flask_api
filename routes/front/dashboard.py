from flask_jwt_extended.exceptions import NoAuthorizationError
from app import app
from flask import render_template, make_response, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, create_access_token
from model import User

@app.route("/dashboard")
def dashboard():
    user_id = None

    # Try access token first (optional, from header)
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except:
        pass

    # If access token missing/invalid, try refresh token (from cookie)
    if not user_id:
        try:
            verify_jwt_in_request(refresh=True)
            user_id = get_jwt_identity()
        except NoAuthorizationError:
            return redirect(url_for("login_page"))

    # Render template; access token will be fetched via /refresh in JS
    return render_template("dashboard.html", user=User.query.get(user_id))