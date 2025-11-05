from app import app
from flask import session, render_template, url_for, redirect
@app.route('/invoice')
def invoice():
    data = session.get('invoice')
    if not data:
        return redirect(url_for('invoice'))
    return render_template('invoice.html', **data)