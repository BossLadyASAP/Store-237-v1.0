from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from models import db, Store, Product, Sale, Receipt
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.route('/pos')
@login_required
def pos():
    """Point of Sale interface."""
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    
    if not stores:
        return render_template('no_stores.html')
    
    store = stores[0]
    return render_template('pos.html', store=store, stores=stores)

@sales_bp.route('/api/checkout', methods=['POST'])
@login_required
def checkout():
    """Process checkout and create sale."""
    data = request.get_json()
    store_id = data.get('storeId')
    items = data.get('items', [])
    
    store = Store.query.get(store_id)
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not items:
        return jsonify({'error': 'No items in cart'}), 400
    
    total_amount = 0
    total_cost = 0
    receipt_items = []
    sales_list = []
    
    try:
        for item in items:
            product = Product.query.get(item['productId'])
            if not product or product.store_id != store_id:
                return jsonify({'error': f'Product {item["productId"]} not found'}), 404
            
            quantity = item['quantity']
            if quantity > product.quantity_in_stock:
                return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
            
            unit_price = product.selling_price
            item_total = quantity * unit_price
            item_cost = quantity * product.cost_price
            item_profit = item_total - item_cost
            profit_margin = (item_profit / item_total * 100) if item_total > 0 else 0
            
            # Create sale record
            sale = Sale(
                store_id=store_id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                total_amount=item_total,
                cost_total=item_cost,
                profit=item_profit,
                profit_margin_percent=profit_margin,
                seller_name=store.seller_name
            )
            sales_list.append(sale)
            db.session.add(sale)
            
            # Update product stock
            product.quantity_in_stock -= quantity
            
            total_amount += item_total
            total_cost += item_cost
            
            receipt_items.append({
                'name': product.name,
                'quantity': quantity,
                'unitPrice': unit_price,
                'total': item_total,
                'profit': item_profit,
                'profitMargin': profit_margin
            })
        
        total_profit = total_amount - total_cost
        total_profit_margin = (total_profit / total_amount * 100) if total_amount > 0 else 0
        
        # Create receipt
        receipt = Receipt(
            store_id=store_id,
            items=receipt_items,
            total_amount=total_amount,
            total_cost=total_cost,
            total_profit=total_profit,
            profit_margin_percent=total_profit_margin
        )
        db.session.add(receipt)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'receiptId': receipt.receipt_id,
            'totalAmount': total_amount,
            'totalCost': total_cost,
            'totalProfit': total_profit,
            'profitMarginPercent': total_profit_margin,
            'items': receipt_items
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_bp.route('/receipt/<receipt_id>/pdf')
@login_required
def generate_receipt_pdf(receipt_id):
    """Generate PDF receipt."""
    receipt = Receipt.query.filter_by(receipt_id=receipt_id).first()
    
    if not receipt:
        return jsonify({'error': 'Receipt not found'}), 404
    
    store = Store.query.get(receipt.store_id)
    if store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#22c55e'),
        spaceAfter=30,
        alignment=1
    )
    
    # Title
    elements.append(Paragraph(store.store_name, title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Store info
    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=10)
    elements.append(Paragraph(f"<b>Proprietor:</b> {store.proprietor_name}", info_style))
    elements.append(Paragraph(f"<b>Seller:</b> {store.seller_name}", info_style))
    elements.append(Paragraph(f"<b>Receipt ID:</b> {receipt.receipt_id}", info_style))
    elements.append(Paragraph(f"<b>Date:</b> {receipt.created_at.strftime('%Y-%m-%d %H:%M:%S')}", info_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Items table
    table_data = [['Item', 'Qty', 'Unit Price', 'Total', 'Profit', 'Margin %']]
    for item in receipt.items:
        table_data.append([
            item['name'],
            str(item['quantity']),
            f"{store.currency} {item['unitPrice']:.2f}",
            f"{store.currency} {item['total']:.2f}",
            f"{store.currency} {item['profit']:.2f}",
            f"{item['profitMargin']:.2f}%"
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#22c55e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Totals
    totals_style = ParagraphStyle('Totals', parent=styles['Normal'], fontSize=12, alignment=2)
    elements.append(Paragraph(f"<b>Total Revenue:</b> {store.currency} {receipt.total_amount:.2f}", totals_style))
    elements.append(Paragraph(f"<b>Total Cost:</b> {store.currency} {receipt.total_cost:.2f}", totals_style))
    elements.append(Paragraph(f"<b>Total Profit:</b> {store.currency} {receipt.total_profit:.2f}", totals_style))
    elements.append(Paragraph(f"<b>Profit Margin:</b> {receipt.profit_margin_percent:.2f}%", totals_style))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'receipt_{receipt_id}.pdf'
    )

@sales_bp.route('/history')
@login_required
def sales_history():
    """View sales history."""
    stores = Store.query.filter_by(owner_id=current_user.id).all()
    
    if not stores:
        return render_template('no_stores.html')
    
    store = stores[0]
    sales = Sale.query.filter_by(store_id=store.id).order_by(Sale.created_at.desc()).all()
    
    return render_template('sales_history.html', store=store, stores=stores, sales=sales)

@sales_bp.route('/api/history/<int:store_id>')
@login_required
def api_sales_history(store_id):
    """API endpoint for sales history."""
    store = Store.query.get(store_id)
    
    if not store or store.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    sales = Sale.query.filter_by(store_id=store_id).order_by(Sale.created_at.desc()).all()
    
    data = [
        {
            'id': s.id,
            'productName': Product.query.get(s.product_id).name,
            'quantity': s.quantity,
            'unitPrice': s.unit_price,
            'totalAmount': s.total_amount,
            'profit': s.profit,
            'profitMargin': s.profit_margin_percent,
            'date': s.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for s in sales
    ]
    
    return jsonify(data)
