from app import app
from flask import render_template, redirect, url_for
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


@app.route('/signup')
def signup():
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
    return render_template('signup.html')
