from flask import Flask
from dotenv import load_dotenv
load_dotenv()
import os

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine, text
from werkzeug.exceptions import HTTPException

# Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key")

# MySQL config
DB_USER = 'root'
DB_PASSWORD = '123'
DB_HOST = 'localhost'
DB_NAME = 'flask_db'

# Create database if not exists
engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}')
with engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))

# SQLAlchemy config
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models/routes after db initialization
import model
import routes

if __name__ == "__main__":
    app.run(debug=True)
