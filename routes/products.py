from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Store, Product
from werkzeug.utils import secure_filename
import os

products_bp = Blueprint('products', __name__, url_prefix='/products')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@products_bp.route('/')
@login_required
def list_products():
    """List all products for user's stores."""
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    
    if not stores:
        return render_template('no_stores.html')
    
    store = stores[0]
    products = Product.query.filter_by(store_id=store.id).all()
    
    return render_template('products.html', store=store, stores=stores, products=products)

@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_product():
    """Create a new product."""
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    
    if not stores:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        store_id = request.form.get('store_id', type=int)
        store = Store.query.get(store_id)
        
        if not store or store.owner_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        name = request.form.get('name')
        description = request.form.get('description')
        cost_price = request.form.get('cost_price', type=float)
        selling_price = request.form.get('selling_price', type=float)
        quantity = request.form.get('quantity_in_stock', type=int, default=0)
        category = request.form.get('category')
        
        # Handle image upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join('uploads', filename)
                file.save(filepath)
                image_url = f'/uploads/{filename}'
        
        product = Product(
            store_id=store_id,
            name=name,
            description=description,
            cost_price=cost_price,
            selling_price=selling_price,
            quantity_in_stock=quantity,
            category=category,
            image_url=image_url
        )
        
        db.session.add(product)
        db.session.commit()
        
        return redirect(url_for('products.list_products'))
    
    store = stores[0]
    return render_template('create_product.html', store=store, stores=stores)

@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit a product."""
    product = Product.query.get(product_id)
    
    if not product:
        return redirect(url_for('products.list_products'))
    
    store = Store.query.get(product.store_id)
    if store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.cost_price = request.form.get('cost_price', type=float)
        product.selling_price = request.form.get('selling_price', type=float)
        product.quantity_in_stock = request.form.get('quantity_in_stock', type=int)
        product.category = request.form.get('category')
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join('uploads', filename)
                file.save(filepath)
                product.image_url = f'/uploads/{filename}'
        
        db.session.commit()
        return redirect(url_for('products.list_products'))
    
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    return render_template('edit_product.html', product=product, store=store, stores=stores)

@products_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete a product."""
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'error': 'Not found'}), 404
    
    store = Store.query.get(product.store_id)
    if store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(product)
    db.session.commit()
    
    return redirect(url_for('products.list_products'))

@products_bp.route('/api/list/<int:store_id>')
@login_required
def api_list_products(store_id):
    """API endpoint to list products."""
    store = Store.query.get(store_id)
    
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    products = Product.query.filter_by(store_id=store_id).all()
    
    data = [
        {
            'id': p.id,
            'name': p.name,
            'costPrice': p.cost_price,
            'sellingPrice': p.selling_price,
            'quantity': p.quantity_in_stock,
            'category': p.category,
            'imageUrl': p.image_url,
            'profitMargin': p.profit_margin_percent()
        }
        for p in products
    ]
    
    return jsonify(data)
