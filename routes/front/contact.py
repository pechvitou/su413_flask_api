from app import app
from flask import render_template, request

@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.post("/contact-success")
def contact_success():
    first_name = request.form.get("first_name", "")
    last_name = request.form.get("last_name", "")
    email = request.form.get("email", "")
    phone = request.form.get("phone", "")
    message = request.form.get("message", "")

    full_name = f"{first_name} {last_name}".strip()

    return render_template(
        "result.html",
        full_name=full_name,
        email=email,
        phone=phone,
        message=message
    )
