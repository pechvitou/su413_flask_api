from app import app
from flask import render_template
# Home page
@app.route('/about')
def about():
    return render_template('about.html')