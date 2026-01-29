from app import app
from flask import render_template
from products import product_list

# Product page
@app.route('/products/<int:product_id>')
def product(product_id):
    product = next((p for p in product_list if p['id'] == product_id), None)
    if not product:
        return "Product not found", 404
    return render_template('product.html', product=product)