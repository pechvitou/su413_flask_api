import requests
from app import app
from flask import render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
import json
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

EXCHANGE_RATE = int(os.getenv("EXCHANGE_RATE", 4000))

# Flask-Mail config
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

mail = Mail(app)


def send_order_notification(name, email, phone, address, cart, total_usd, total_riel):
    """Send order details via Telegram and email."""

    # Prepare Telegram message
    telegram_message = f"""📦 *New Order Received!*

👤 *Customer:* {name}
📧 *Email:* {email}
📞 *Phone:* {phone}
🏠 *Address:* {address}

🛒 *Order Details:*
"""
    for item in cart:
        subtotal = item['price'] * item['quantity']
        telegram_message += f"    • {item['name']} x{item['quantity']} - ${subtotal:.2f}\n"

    telegram_message += f"""
💰 *Total USD:* ${total_usd:.2f}
💵 *Total Riel:* KHR{total_riel:,.0f}
    """

    # Send Telegram
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": telegram_message,
                "parse_mode": "Markdown"
            }
        )
    except Exception as e:
        print("Telegram error:", e)

    # Prepare HTML invoice
    rows = ""
    for item in cart:
        subtotal = item['price'] * item['quantity']
        rows += f"<tr><td>{item['name']}</td><td align='center'>{item['quantity']}</td><td align='right'>${item['price']:.2f}</td><td align='right'>${subtotal:.2f}</td></tr>"

    invoice_html = f"""
    <div style="font-family: 'Segoe UI', sans-serif; max-width:700px; margin:auto; padding:20px; border:1px solid #e0e0e0; border-radius:10px; background:#fafafa;">
        <h2 style="color:#007bff;">Invoice</h2>
        <p><strong>Customer:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Phone:</strong> {phone}</p>
        <p><strong>Address:</strong> {address}</p>
        <table style="width:100%; border-collapse: collapse;">
            <thead>
                <tr style="background:#007bff; color:#fff;">
                    <th style="padding:8px; border:1px solid #ddd;">Product</th>
                    <th style="padding:8px; border:1px solid #ddd;">Qty</th>
                    <th style="padding:8px; border:1px solid #ddd;">Unit Price</th>
                    <th style="padding:8px; border:1px solid #ddd;">Subtotal</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="3" style="text-align:right; font-weight:bold; padding:8px;">Total USD:</td>
                    <td style="padding:8px; font-weight:bold;">${total_usd:.2f}</td>
                </tr>
                <tr>
                    <td colspan="3" style="text-align:right; font-weight:bold; padding:8px;">Total Riel:</td>
                    <td style="padding:8px; font-weight:bold;">KHR{total_riel:,.0f}</td>
                </tr>
            </tfoot>
        </table>
    </div>
    """

    # Send Email
    try:
        msg = Message(
            subject="New Order Received",
            recipients=[email],
            html=invoice_html
        )
        mail.send(msg)
    except Exception as e:
        print("Email error:", e)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Handle form submission
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')

        cart_json = request.form.get('cart')
        cart = json.loads(cart_json) if cart_json else []

        total_usd = sum(item['price'] * item['quantity'] for item in cart)
        total_riel = total_usd * EXCHANGE_RATE

        # Store invoice in session
        session['invoice'] = {
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "cart": cart,
            "total_usd": total_usd,
            "total_riel": total_riel
        }

        # Send notifications
        send_order_notification(name, email, phone, address, cart, total_usd, total_riel)

        return redirect(url_for('invoice'))

    return render_template('checkout.html')
