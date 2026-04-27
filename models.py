from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stores = db.relationship('Store', backref='owner', lazy=True, foreign_keys='Store.owner_id')
    team_memberships = db.relationship('TeamMember', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Store(db.Model):
    """Store model."""
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    store_name = db.Column(db.String(120), nullable=False)
    proprietor_name = db.Column(db.String(120), nullable=False)
    seller_name = db.Column(db.String(120), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    currency = db.Column(db.String(10), default='USD')
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='store', lazy=True, cascade='all, delete-orphan')
    sales = db.relationship('Sale', backref='store', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='store', lazy=True, cascade='all, delete-orphan')
    team_members = db.relationship('TeamMember', backref='store', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Store {self.store_name}>'

class Product(db.Model):
    """Product model."""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    cost_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    quantity_in_stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sales = db.relationship('Sale', backref='product', lazy=True)
    
    def profit_per_unit(self):
        return self.selling_price - self.cost_price
    
    def profit_margin_percent(self):
        if self.selling_price == 0:
            return 0
        return ((self.selling_price - self.cost_price) / self.selling_price) * 100
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Sale(db.Model):
    """Sale/Transaction model."""
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    cost_total = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)
    profit_margin_percent = db.Column(db.Float, default=0)
    seller_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Sale {self.sale_id}>'

class Expense(db.Model):
    """Expense model."""
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Expense {self.category}>'

class TeamMember(db.Model):
    """Team member model."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    role = db.Column(db.String(20), default='viewer')  # admin, manager, viewer
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TeamMember {self.user_id} - {self.role}>'

class Receipt(db.Model):
    """Receipt model for transaction history."""
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    items = db.Column(db.JSON)  # List of items in receipt
    total_amount = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    total_profit = db.Column(db.Float, nullable=False)
    profit_margin_percent = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Receipt {self.receipt_id}>'

class RecurringReport(db.Model):
    """Recurring report configuration."""
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    frequency = db.Column(db.String(20))  # daily, weekly, monthly
    email = db.Column(db.String(120), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    last_sent = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RecurringReport {self.frequency}>'
