from app import app
from flask import render_template
# Cart page
@app.route('/cart')
def cart():
    return render_template('cart.html')