from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Store, User

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
@login_required
def settings():
    """Settings page."""
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    
    if not stores:
        return render_template('no_stores.html')
    
    store = stores[0]
    return render_template('settings.html', store=store, stores=stores)

@settings_bp.route('/store/<int:store_id>', methods=['POST'])
@login_required
def update_store(store_id):
    """Update store settings."""
    store = Store.query.get(store_id)
    
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    store.store_name = request.form.get('store_name', store.store_name)
    store.proprietor_name = request.form.get('proprietor_name', store.proprietor_name)
    store.seller_name = request.form.get('seller_name', store.seller_name)
    store.currency = request.form.get('currency', store.currency)
    store.description = request.form.get('description', store.description)
    
    db.session.commit()
    
    return redirect(url_for('settings.settings'))

@settings_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile."""
    current_user.full_name = request.form.get('full_name', current_user.full_name)
    current_user.email = request.form.get('email', current_user.email)
    
    password = request.form.get('password')
    if password:
        current_user.set_password(password)
    
    db.session.commit()
    
    return redirect(url_for('settings.settings'))

@settings_bp.route('/api/store/<int:store_id>')
@login_required
def api_get_store(store_id):
    """API endpoint to get store settings."""
    store = Store.query.get(store_id)
    
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': store.id,
        'storeName': store.store_name,
        'proprietorName': store.proprietor_name,
        'sellerName': store.seller_name,
        'currency': store.currency,
        'description': store.description
    })
