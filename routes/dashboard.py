from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, Store, Sale, Expense, Product
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard():
    """Main dashboard page."""
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    
    if not stores:
        return render_template('no_stores.html')
    
    store = stores[0]
    return render_template('dashboard.html', store=store, stores=stores)

@dashboard_bp.route('/api/kpis/<int:store_id>')
@login_required
def get_kpis(store_id):
    """Get KPI data for dashboard."""
    store = Store.query.get(store_id)
    
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Calculate KPIs
    sales = Sale.query.filter_by(store_id=store_id).all()
    expenses = Expense.query.filter_by(store_id=store_id).all()
    
    total_revenue = sum(s.total_amount for s in sales)
    total_expenses = sum(e.amount for e in expenses)
    total_profit = total_revenue - total_expenses
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return jsonify({
        'totalRevenue': total_revenue,
        'totalExpenses': total_expenses,
        'totalProfit': total_profit,
        'profitMarginPercent': profit_margin,
        'totalSales': len(sales),
        'currency': store.currency
    })

@dashboard_bp.route('/api/expenses-breakdown/<int:store_id>')
@login_required
def get_expenses_breakdown(store_id):
    """Get expenses breakdown by category."""
    store = Store.query.get(store_id)
    
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    expenses = Expense.query.filter_by(store_id=store_id).all()
    breakdown = {}
    
    for expense in expenses:
        if expense.category not in breakdown:
            breakdown[expense.category] = 0
        breakdown[expense.category] += expense.amount
    
    data = [{'category': k, 'amount': v} for k, v in breakdown.items()]
    return jsonify(data)

@dashboard_bp.route('/api/best-selling-products/<int:store_id>')
@login_required
def get_best_selling_products(store_id):
    """Get best-selling products."""
    store = Store.query.get(store_id)
    
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    sales = Sale.query.filter_by(store_id=store_id).all()
    product_sales = {}
    
    for sale in sales:
        product = Product.query.get(sale.product_id)
        if product:
            if product.id not in product_sales:
                product_sales[product.id] = {
                    'name': product.name,
                    'quantity': 0,
                    'revenue': 0
                }
            product_sales[product.id]['quantity'] += sale.quantity
            product_sales[product.id]['revenue'] += sale.total_amount
    
    # Sort by quantity sold
    sorted_products = sorted(
        product_sales.values(),
        key=lambda x: x['quantity'],
        reverse=True
    )[:10]
    
    return jsonify(sorted_products)

@dashboard_bp.route('/api/sales-trend/<int:store_id>')
@login_required
def get_sales_trend(store_id):
    """Get sales trend over time."""
    store = Store.query.get(store_id)
    
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get sales for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    sales = Sale.query.filter(
        Sale.store_id == store_id,
        Sale.created_at >= thirty_days_ago
    ).all()
    
    # Group by date
    daily_sales = {}
    for sale in sales:
        date_key = sale.created_at.strftime('%Y-%m-%d')
        if date_key not in daily_sales:
            daily_sales[date_key] = {'revenue': 0, 'profit': 0, 'count': 0}
        daily_sales[date_key]['revenue'] += sale.total_amount
        daily_sales[date_key]['profit'] += sale.profit
        daily_sales[date_key]['count'] += 1
    
    data = [
        {
            'date': k,
            'revenue': v['revenue'],
            'profit': v['profit'],
            'transactions': v['count']
        }
        for k, v in sorted(daily_sales.items())
    ]
    
    return jsonify(data)
