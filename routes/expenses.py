from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Store, Expense

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@expenses_bp.route('/')
@login_required
def list_expenses():
    """List all expenses."""
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    
    if not stores:
        return render_template('no_stores.html')
    
    store = stores[0]
    expenses = Expense.query.filter_by(store_id=store.id).order_by(Expense.created_at.desc()).all()
    
    return render_template('expenses.html', store=store, stores=stores, expenses=expenses)

@expenses_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_expense():
    """Create a new expense."""
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    
    if not stores:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        store_id = request.form.get('store_id', type=int)
        store = Store.query.get(store_id)
        
        if not store or store.owner_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        category = request.form.get('category')
        amount = request.form.get('amount', type=float)
        description = request.form.get('description')
        
        expense = Expense(
            store_id=store_id,
            category=category,
            amount=amount,
            description=description
        )
        
        db.session.add(expense)
        db.session.commit()
        
        return redirect(url_for('expenses.list_expenses'))
    
    store = stores[0]
    return render_template('create_expense.html', store=store, stores=stores)

@expenses_bp.route('/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(expense_id):
    """Delete an expense."""
    expense = Expense.query.get(expense_id)
    
    if not expense:
        return jsonify({'error': 'Not found'}), 404
    
    store = Store.query.get(expense.store_id)
    if store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(expense)
    db.session.commit()
    
    return redirect(url_for('expenses.list_expenses'))

@expenses_bp.route('/api/list/<int:store_id>')
@login_required
def api_list_expenses(store_id):
    """API endpoint to list expenses."""
    store = Store.query.get(store_id)
    
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    expenses = Expense.query.filter_by(store_id=store_id).order_by(Expense.created_at.desc()).all()
    
    data = [
        {
            'id': e.id,
            'category': e.category,
            'amount': e.amount,
            'description': e.description,
            'date': e.created_at.strftime('%Y-%m-%d')
        }
        for e in expenses
    ]
    
    return jsonify(data)
