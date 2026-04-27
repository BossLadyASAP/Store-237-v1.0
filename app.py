from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_babel import Babel, gettext
from config import config
from models import db, User, Store, Product, Sale, Expense, TeamMember, Receipt, RecurringReport
from datetime import datetime, timedelta
import os
import json

def get_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(['en', 'fr', 'es', 'de', 'pt', 'zh']) or 'en'

def create_app(config_name='production'):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    babel = Babel(app, locale_selector=get_locale)
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.products import products_bp
    from routes.sales import sales_bp
    from routes.expenses import expenses_bp
    from routes.team import team_bp
    from routes.settings import settings_bp
    from routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(api_bp)
    
    # Home route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.dashboard'))
        return redirect(url_for('auth.landing'))
    
    # Language switcher
    @app.route('/set_language/<language>')
    def set_language(language):
        if language in app.config['LANGUAGES']:
            session['language'] = language
        return redirect(request.referrer or url_for('auth.landing'))
    
    # Theme toggle
    @app.route('/toggle_theme')
    def toggle_theme():
        current_theme = session.get('theme', 'light')
        session['theme'] = 'dark' if current_theme == 'light' else 'light'
        return jsonify({'theme': session['theme']})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return render_template('500.html'), 500
    
    # Create database tables
    with app.app_context():
        db.create_all(checkfirst=True)
        create_demo_account()
    
    return app

def create_demo_account():
    """Create demo account with sample data."""
    demo_user = User.query.filter_by(username='demo').first()
    
    if not demo_user:
        # Create demo user
        demo_user = User(
            username='demo',
            email='demo@store237.com',
            full_name='Demo User',
            is_demo=True
        )
        demo_user.set_password('demo123')
        db.session.add(demo_user)
        db.session.flush()
        
        # Create demo store
        demo_store = Store(
            store_name='Store 237 Demo',
            proprietor_name='John Doe',
            seller_name='Jane Smith',
            owner_id=demo_user.id,
            currency='USD',
            description='Demo store for testing Store 237 features'
        )
        db.session.add(demo_store)
        db.session.flush()
        
        # Create sample products
        products_data = [
            {'name': 'Laptop', 'cost_price': 400, 'selling_price': 800, 'quantity': 5, 'category': 'Electronics'},
            {'name': 'Mouse', 'cost_price': 5, 'selling_price': 15, 'quantity': 50, 'category': 'Accessories'},
            {'name': 'Keyboard', 'cost_price': 20, 'selling_price': 60, 'quantity': 30, 'category': 'Accessories'},
            {'name': 'Monitor', 'cost_price': 150, 'selling_price': 350, 'quantity': 8, 'category': 'Electronics'},
            {'name': 'USB Cable', 'cost_price': 1, 'selling_price': 5, 'quantity': 100, 'category': 'Accessories'},
            {'name': 'Headphones', 'cost_price': 30, 'selling_price': 100, 'quantity': 20, 'category': 'Audio'},
            {'name': 'Webcam', 'cost_price': 25, 'selling_price': 75, 'quantity': 15, 'category': 'Electronics'},
            {'name': 'Desk Lamp', 'cost_price': 15, 'selling_price': 45, 'quantity': 25, 'category': 'Accessories'},
        ]
        
        products = []
        for p_data in products_data:
            product = Product(
                store_id=demo_store.id,
                name=p_data['name'],
                cost_price=p_data['cost_price'],
                selling_price=p_data['selling_price'],
                quantity_in_stock=p_data['quantity'],
                category=p_data['category']
            )
            products.append(product)
            db.session.add(product)
        
        db.session.flush()
        
        # Create sample sales
        sales_data = [
            {'product_idx': 0, 'quantity': 2},
            {'product_idx': 1, 'quantity': 10},
            {'product_idx': 2, 'quantity': 5},
            {'product_idx': 3, 'quantity': 1},
            {'product_idx': 4, 'quantity': 20},
            {'product_idx': 5, 'quantity': 3},
            {'product_idx': 6, 'quantity': 2},
            {'product_idx': 7, 'quantity': 8},
            {'product_idx': 1, 'quantity': 15},
            {'product_idx': 2, 'quantity': 7},
        ]
        
        for i, s_data in enumerate(sales_data):
            product = products[s_data['product_idx']]
            quantity = s_data['quantity']
            unit_price = product.selling_price
            total_amount = quantity * unit_price
            cost_total = quantity * product.cost_price
            profit = total_amount - cost_total
            profit_margin = (profit / total_amount * 100) if total_amount > 0 else 0
            
            sale = Sale(
                store_id=demo_store.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                total_amount=total_amount,
                cost_total=cost_total,
                profit=profit,
                profit_margin_percent=profit_margin,
                seller_name='Jane Smith',
                created_at=datetime.utcnow() - timedelta(days=10-i)
            )
            db.session.add(sale)
        
        # Create sample expenses
        expenses_data = [
            {'category': 'Rent', 'amount': 500},
            {'category': 'Utilities', 'amount': 150},
            {'category': 'Salaries', 'amount': 2000},
            {'category': 'Marketing', 'amount': 300},
            {'category': 'Maintenance', 'amount': 200},
            {'category': 'Supplies', 'amount': 100},
        ]
        
        for e_data in expenses_data:
            expense = Expense(
                store_id=demo_store.id,
                category=e_data['category'],
                amount=e_data['amount'],
                created_at=datetime.utcnow() - timedelta(days=5)
            )
            db.session.add(expense)
        
        db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
