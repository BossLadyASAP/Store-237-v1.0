from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User, Store
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/landing')
def landing():
    """Landing page with language and theme options."""
    return render_template('landing.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember'))
            return redirect(url_for('dashboard.dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        store_name = request.form.get('store_name')
        proprietor_name = request.form.get('proprietor_name')
        seller_name = request.form.get('seller_name')
        
        # Validation
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already exists')
        
        # Create user
        user = User(
            username=username,
            email=email,
            full_name=full_name
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        # Create store
        store = Store(
            store_name=store_name,
            proprietor_name=proprietor_name,
            seller_name=seller_name,
            owner_id=user.id,
            currency='USD'
        )
        db.session.add(store)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('register.html')

@auth_bp.route('/demo_login', methods=['POST'])
def demo_login():
    """Demo account login."""
    demo_user = User.query.filter_by(username='demo').first()
    
    if demo_user:
        login_user(demo_user)
        return redirect(url_for('dashboard.dashboard'))
    
    return redirect(url_for('auth.landing'))

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    return redirect(url_for('auth.landing'))
