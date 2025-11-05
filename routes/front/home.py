from app import app
from flask import render_template
from products import product_list
# Home page
@app.route('/')
def home():
    return render_template('home.html', products=product_list)