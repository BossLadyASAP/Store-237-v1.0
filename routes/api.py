from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import Store, Sale, Expense, Product

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/stores')
@login_required
def get_user_stores():
    """Get all stores for current user."""
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    
    data = [
        {
            'id': s.id,
            'storeName': s.store_name,
            'currency': s.currency,
            'proprietorName': s.proprietor_name,
            'sellerName': s.seller_name
        }
        for s in stores
    ]
    
    return jsonify(data)

@api_bp.route('/store/<int:store_id>/summary')
@login_required
def get_store_summary(store_id):
    """Get store summary."""
    store = Store.query.get(store_id)
    
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    sales = Sale.query.filter_by(store_id=store_id).all()
    expenses = Expense.query.filter_by(store_id=store_id).all()
    products = Product.query.filter_by(store_id=store_id).all()
    
    total_revenue = sum(s.total_amount for s in sales)
    total_expenses = sum(e.amount for e in expenses)
    total_profit = total_revenue - total_expenses
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return jsonify({
        'storeName': store.store_name,
        'totalRevenue': total_revenue,
        'totalExpenses': total_expenses,
        'totalProfit': total_profit,
        'profitMarginPercent': profit_margin,
        'totalSales': len(sales),
        'totalProducts': len(products),
        'currency': store.currency
    })
