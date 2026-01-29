from flask import make_response, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request, get_jwt_identity
from app import app, jwt_blocklist


@app.post("/logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_blocklist.add(jti)

    # Clear access token cookie
    resp = make_response(redirect("/"))  # redirect to homepage or login page
    resp.set_cookie(
        "access_token",
        "",
        expires=0,  # immediately expire
        httponly=True,  # same as when setting it
        secure=False,  # True if using HTTPS in production
        samesite="Lax"
    )
    return resp
