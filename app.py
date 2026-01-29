from datetime import timedelta

from flask import Flask, request, jsonify, redirect, url_for, render_template, flash, make_response
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

load_dotenv()
import os

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine, text
from werkzeug.exceptions import HTTPException

from flask_jwt_extended import create_access_token, get_jwt, verify_jwt_in_request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

# Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key")

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"

# app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
# app.config["JWT_REFRESH_COOKIE_NAME"] = "refresh_token"

app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
jwt_blocklist = set()
jwt = JWTManager(app)

# MySQL config
DB_USER = 'root'
DB_PASSWORD = '123'
DB_HOST = 'localhost'
DB_NAME = 'flask_db'

engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}')
with engine.connect() as conn:
    # conn.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME}"))
    # conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))

# SQLAlchemy config
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models/routes after db initialization
from model import User
import model
import routes

@app.context_processor
def inject_user():
    user = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            user = User.query.get(user_id)
    except:
        pass
    return dict(user=user)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in jwt_blocklist

@jwt.unauthorized_loader
@jwt.invalid_token_loader
@jwt.expired_token_loader
def handle_bad_token(*args, **kwargs):
    return "", 401

# @app.after_request
# def add_no_cache_headers(response):
#     response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
#     response.headers["Pragma"] = "no-cache"
#     response.headers["Expires"] = "0"
#     return response

if __name__ == "__main__":
    app.run(debug=True)
