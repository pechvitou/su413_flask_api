from flask import jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app import app


@app.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": new_access_token})
